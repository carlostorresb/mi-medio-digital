import feedparser, json, re, base64, os, urllib.request, urllib.parse
from datetime import datetime
from pathlib import Path

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = "carlostorresb/mi-medio-digital"
GITHUB_BRANCH = "main"
AGENTES_DIR = Path("C:/mi-medio-digital/agentes")
PROCESADOS = Path("noticias_procesadas.json")

def cargar_periodistas():
    periodistas = {}
    if not AGENTES_DIR.exists():
        print(f"ERROR: No existe {AGENTES_DIR}")
        return periodistas
    for archivo in AGENTES_DIR.glob("*.json"):
        try:
            data = json.loads(archivo.read_text(encoding="utf-8"))
            if not data.get("activo", True):
                continue
            seccion = data.get("seccion", archivo.stem).lower().replace(" ", "_")
            periodistas[seccion] = {
                "nombre": data.get("nombre", "Periodista"),
                "seccion": data.get("seccion", seccion),
                "feeds": data.get("feeds_rss", data.get("feeds", [])),
                "estilo": data.get("instrucciones", data.get("systemPrompt", data.get("descripcion", ""))),
                "puntuacion_minima": data.get("puntuacion_minima", 6),
                "articulos_max": data.get("max_articulos", 3),
            }
            print(f"  Cargado: {data.get('nombre')} ({data.get('seccion')})")
        except Exception as e:
            print(f"  Error {archivo.name}: {e}")
    return periodistas

def cargar():
    return set(json.loads(PROCESADOS.read_text()).get("urls", [])) if PROCESADOS.exists() else set()

def guardar(urls):
    PROCESADOS.write_text(json.dumps({"urls": list(urls)}, indent=2))

def noticias(feeds, procesados, max_arts=2):
    result = []
    for f in feeds:
        try:
            for e in feedparser.parse(f).entries[:5]:
                u = e.get("link", "")
                if u and u not in procesados:
                    result.append({"titulo": e.get("title", ""), "resumen": e.get("summary", "")[:400], "url": u})
                    if len(result) >= max_arts:
                        return result
        except:
            pass
    return result

def ollama(prompt):
    data = json.dumps({"model": "mistral:latest", "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request("http://localhost:11434/api/generate", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["response"].strip()


def leer_contexto_periodista(nombre):
    """Lee la nota del periodista en Obsidian si existe."""
    ruta = Path(f"C:/mi-medio-digital/obsidian/01-periodistas/{nombre}.md")
    if ruta.exists():
        return "\n".join(ruta.read_text(encoding="utf-8").split("\n")[:5])
    return ""
def periodista(noticia, cfg):
    titulo = noticia["titulo"].replace('"', "'")
    resumen = noticia["resumen"].replace('"', "'")
    contexto = leer_contexto_periodista(cfg["nombre"])
    prompt = f"""{cfg["estilo"]}

CONTEXTO DEL PERIODISTA:
{contexto}

Noticia: {titulo}
Resumen: {resumen}

Escribe un articulo LARGO y DETALLADO con minimo 5 parrafos extensos. Responde SOLO con este JSON en espanol, sin texto adicional:
{{"titular":"titular atractivo","subtitulo":"una oracion","cuerpo":"<p>Primer parrafo con contexto e introduccion detallada</p><p>Segundo parrafo con antecedentes y datos relevantes</p><p>Tercer parrafo con desarrollo y analisis profundo</p><p>Cuarto parrafo con impacto y consecuencias</p><p>Quinto parrafo con conclusion y perspectiva</p>","tags":["tag1","tag2"],"resumen_seo":"descripcion breve"}}"""
    try:
        t = ollama(prompt)
        start = t.find("{")
        end = t.rfind("}") + 1
        if start == -1:
            raise ValueError("No JSON")
        t_json = t[start:end].replace("\n", " ").replace("\r", " ").replace("\t", " ")
        t_json = re.sub(r",\s*}", "}", t_json)
        t_json = re.sub(r",\s*]", "]", t_json)
        a = json.loads(t_json)
        a.update({"seccion": cfg["seccion"], "periodista": cfg["nombre"], "url_fuente": noticia["url"], "fecha_generacion": datetime.now().isoformat()})
        return a
    except Exception as e:
        print(f"  Error periodista: {e}")
        return None

def publicar(art):
    slug = re.sub(r"\s+", "-", re.sub(r"[^a-z0-9\s]", "", art.get("titular", "articulo").lower())[:50])
    slug += "-" + datetime.now().strftime("%Y%m%d%H%M")
    art["slug"] = slug
    Path("contenido").mkdir(exist_ok=True)
    Path(f"contenido/{slug}.json").write_text(json.dumps(art, ensure_ascii=False, indent=2))
    print(f"  Guardado: contenido/{slug}.json")

def main(secciones_filtro=None):
    print(f"\n{'='*40}\n  SALA DE REDACCION {datetime.now().strftime('%d/%m/%Y %H:%M')}\n{'='*40}\n")
    print("Cargando periodistas...")
    periodistas = cargar_periodistas()
    if not periodistas:
        print("ERROR: No hay periodistas")
        return
    print(f"Total: {len(periodistas)} periodistas activos\n")
    procesados = cargar()
    nuevas = set()
    if secciones_filtro:
        periodistas = {k: v for k, v in periodistas.items() if any(s.lower() in k.lower() for s in secciones_filtro)}
    for clave, cfg in periodistas.items():
        print(f"{'─'*40}\nSeccion: {cfg['seccion'].upper()} | Periodista: {cfg['nombre']}")
        arts = noticias(cfg["feeds"], procesados, cfg["articulos_max"])
        if not arts:
            print("  Sin noticias nuevas\n")
            continue
        for n in arts:
            print(f"  Noticia: {n['titulo'][:60]}...")
            nuevas.add(n["url"])
            print("  Redactando...")
            a = periodista(n, cfg)
            if not a:
                continue
            publicar(a)
        print()
    procesados.update(nuevas)
    guardar(procesados)
    print(f"\n{'='*40}\n  PUBLICACION COMPLETADA\n{'='*40}\n")

if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)

