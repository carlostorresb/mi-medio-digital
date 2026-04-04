import urllib.request, json

titulo = "EE. UU. e Iran buscan piloto tras derribo de aviones"
prompt = f"Eres periodista. Noticia: {titulo}. Responde SOLO con este JSON: {{\"titular\":\"titulo\",\"subtitulo\":\"subtitulo\",\"cuerpo\":\"<p>texto</p>\",\"tags\":[\"tag1\"],\"resumen_seo\":\"descripcion\"}}"

data = json.dumps({"model":"mistral:latest","prompt":prompt,"stream":False}).encode()
req = urllib.request.Request("http://localhost:11434/api/generate",data=data,headers={"Content-Type":"application/json"})
with urllib.request.urlopen(req) as r:
    resp = json.loads(r.read())["response"].strip()
print("RESPUESTA:")
print(repr(resp[:600]))
