import feedparser, json
from pathlib import Path

for archivo in Path('C:/mi-medio-digital/agentes').glob('*.json'):
    d = json.loads(archivo.read_text(encoding='utf-8'))
    print(f"\n{d.get('nombre')} ({d.get('seccion')})")
    for f in d.get('feeds_rss', []):
        r = feedparser.parse(f)
        if r.entries:
            print(f"  {r.entries[0].get('title','')[:60]}")
