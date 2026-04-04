import urllib.request, json

prompt = "Eres periodista. Noticia: Trump lanza guerra de aranceles. Responde SOLO con este JSON: {\"titular\":\"titulo\",\"subtitulo\":\"subtitulo\",\"cuerpo\":\"<p>texto</p>\",\"tags\":[\"economia\"],\"resumen_seo\":\"descripcion\"}"

data = json.dumps({"model":"mistral:latest","prompt":prompt,"stream":False}).encode()
req = urllib.request.Request("http://localhost:11434/api/generate",data=data,headers={"Content-Type":"application/json"})
with urllib.request.urlopen(req) as r:
    resp = json.loads(r.read())["response"].strip()
print("RESPUESTA:")
print(repr(resp[:800]))
