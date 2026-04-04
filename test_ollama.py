import urllib.request, json

prompt = "Eres periodista. Responde UNICAMENTE con este JSON sin texto antes ni despues:\n\n{\"titular\":\"titulo aqui\",\"subtitulo\":\"subtitulo\",\"cuerpo\":\"<p>parrafo</p>\",\"tags\":[\"tag1\"],\"resumen_seo\":\"descripcion\"}"

data = json.dumps({"model":"mistral:latest","prompt":prompt,"stream":False}).encode()
req = urllib.request.Request("http://localhost:11434/api/generate",data=data,headers={"Content-Type":"application/json"})
with urllib.request.urlopen(req) as r:
    resp = json.loads(r.read())["response"].strip()
print(repr(resp[:500]))
