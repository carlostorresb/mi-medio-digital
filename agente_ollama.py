import feedparser, json, re, base64, os, urllib.request, urllib.parse
from datetime import datetime
from pathlib import Path

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = "carlostorresb/mi-medio-digital"
GITHUB_BRANCH = "main"

SECCIONES = {
    "ciberseguridad": {
        "nombre": "Ciberseguridad",
        "feeds": ["https://feeds.feedburner.com/TheHackersNews","https://krebsonsecurity.com/feed/"],
        "estilo": "Eres periodista de ciberseguridad para audiencia peruana.",
    },
    "tecnologia": {
        "nombre": "Tecnologia",
        "feeds": ["https://feeds.bbci.co.uk/mundo/ciencia_y_tecnologia/rss.xml"],
        "estilo": "Eres periodista de tecnologia. Escribes en español peruano.",
    },
    "economia": {
        "nombre": "Economia",
        "feeds": ["https://feeds.bbci.co.uk/mundo/economia/rss.xml"],
        "estilo": "Eres periodista economico. Escribes en español peruano.",
    },
    "deportes": {
        "nombre": "Deportes",
        "feeds": [
            "https://www.libero.pe/rss/futbol-peruano.xml",
            "https://feeds.bbci.co.uk/sport/football/rss.xml",
            "https://e00-marca.uecdn.es/rss/futbol/primera-division.xml",
            "https://www.espn.com/espn/rss/soccer/news",
        ],
        "estilo": "Eres un periodista deportivo apasionado especializado en futbol. Cubres la Liga Peruana, Premier League, La Liga española y la MLS. Tienes especial atencion al Inter Miami y Lionel Messi. Escribes en español peruano con emocion y pasion, usando terminos futbolisticos. Articulos de 300-500 palabras con titular atractivo.",
    },
    "politica": {
        "nombre": "Politica",
        "feeds": ["https://feeds.bbci.co.uk/mundo/america_latina/rss.xml"],
        "estilo": "Eres periodista politico neutral.",
    },
}

PROCESADOS = Path("noticias_procesadas.json")

def cargar(): return set(json.loads(PROCESADOS.read_text()).get("urls",[])) if PROCESADOS.exists() else set()
def guardar(urls): PROCESADOS.write_text(json.dumps({"urls":list(urls)},indent=2))

def noticias(feeds, procesados):
    result = []
    for f in feeds:
        try:
            for e in feedparser.parse(f).entries[:5]:
                u = e.get("link","")
                if u and u not in procesados:
                    result.append({"titulo":e.get("title",""),"resumen":e.get("summary","")[:400],"url":u})
                    if len(result)>=2: return result
        except: pass
    return result

def ollama(prompt):
    data = json.dumps({"model":"llama3.2:1b","prompt":prompt,"stream":False}).encode()
    req = urllib.request.Request("http://localhost:11434/api/generate",data=data,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["response"].strip()

def periodista(noticia, estilo, seccion):
    prompt = f"""{estilo}

Redacta un articulo periodistico en español sobre esta noticia.
IMPORTANTE: Responde UNICAMENTE con este JSON, sin texto antes ni despues, sin markdown:

TITULO ORIGINAL: {noticia['titulo']}
RESUMEN: {noticia['resumen']}

{{"titular":"titulo atractivo en español","subtitulo":"una oracion de contexto","cuerpo":"<p>parrafo 1</p><p>parrafo 2</p><p>parrafo 3</p>","tags":["tag1","tag2"],"resumen_seo":"descripcion de 160 caracteres"}}"""
    try:
        t = ollama(prompt)
        t = t.replace("\\n", " ").replace("\\t", " ").replace("\\'", "'")
        start = t.find("{")
        end = t.rfind("}") + 1
        if start == -1:
            # Intenta extraer cualquier texto util
            raise ValueError("No JSON")
        t_json = t[start:end]
        t_json = re.sub(r',\s*}', '}', t_json)
        t_json = re.sub(r',\s*]', ']', t_json)
        t_json = re.sub(r'[\x00-\x1f]', ' ', t_json)
        a = json.loads(t_json)
        a.update({"seccion":seccion,"url_fuente":noticia["url"],"fecha_generacion":datetime.now().isoformat()})
        return a
    except Exception as e:
        print(f"  Error periodista: {e}"); return None

def editor(art):
    prompt = f"""Eres editor jefe de un medio digital peruano.
Revisa este articulo y devuelve SOLO JSON valido sin markdown:

TITULAR: {art.get("titular","sin titulo")}
CUERPO: {art.get("cuerpo","sin cuerpo")}

Si es buen articulo: {{"aprobado":true,"titular":"titular mejorado","subtitulo":"subtitulo","cuerpo":"<p>cuerpo</p>","puntuacion":8}}
Si es malo: {{"aprobado":false}}"""
    try:
        t = ollama(prompt)
        t = t.replace("\\n", " ").replace("\\t", " ").replace("\\'", "'")
        start = t.find("{")
        end = t.rfind("}") + 1
        if start == -1:
            # Intenta extraer cualquier texto util
            raise ValueError("No JSON")
        t_json = t[start:end]
        t_json = re.sub(r',\s*}', '}', t_json)
        t_json = re.sub(r',\s*]', ']', t_json)
        t_json = re.sub(r'[\x00-\x1f]', ' ', t_json)
        r = json.loads(t_json)
        if not r.get("aprobado"): return None
        art.update(r); return art
    except Exception as e:
        print(f"  Error editor: {e}"); return None

def publicar(art):
    slug = re.sub(r"\s+","-",re.sub(r"[^a-z0-9\s]","",art.get("titular","articulo").lower())[:50])
    slug += "-" + datetime.now().strftime("%Y%m%d%H%M")
    art["slug"] = slug
    Path("contenido").mkdir(exist_ok=True)
    Path(f"contenido/{slug}.json").write_text(json.dumps(art,ensure_ascii=False,indent=2))
    print(f"  Guardado local: contenido/{slug}.json")
    if not GITHUB_TOKEN: return
    ruta = f"contenido/{slug}.json"
    payload = json.dumps({
        "message":f"[IA] {art['seccion']}: {art.get('titular', art.get('titulo','articulo'))[:60]}",
        "content":base64.b64encode(json.dumps(art,ensure_ascii=False,indent=2).encode()).decode(),
        "branch":GITHUB_BRANCH
    }).encode()
    req = urllib.request.Request(
        f"https://api.github.com/repos/{GITHUB_REPO}/contents/{ruta}",
        data=payload,
        headers={"Authorization":f"Bearer {GITHUB_TOKEN}","Content-Type":"application/json","Accept":"application/vnd.github+json"},
        method="PUT")
    try:
        with urllib.request.urlopen(req) as r:
            if r.status in (200,201): print(f"  Publicado en GitHub!")
    except Exception as e: print(f"  Error GitHub: {e}")

def main(secciones=None):
    print(f"\n{'='*40}\n  SALA DE REDACCION {datetime.now().strftime('%d/%m/%Y %H:%M')}\n{'='*40}\n")
    procesados = cargar()
    nuevas = set()
    for clave in (secciones or list(SECCIONES.keys())):
        cfg = SECCIONES[clave]
        print(f"Seccion: {cfg['nombre'].upper()}")
        arts = noticias(cfg["feeds"], procesados)
        if not arts: print("  Sin noticias\n"); continue
        for n in arts:
            print(f"  -> {n['titulo'][:60]}...")
            nuevas.add(n["url"])
            print("  Periodista redactando...")
            a = periodista(n, cfg["estilo"], clave)
            if not a: continue
            print("  Editor revisando...")
            af = a
            
            publicar(af)
        print()
    procesados.update(nuevas); guardar(procesados)
    print("Listo!")

if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
