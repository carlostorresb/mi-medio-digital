import feedparser
feeds = [
    'https://www.who.int/rss-feeds/news-spanish.xml',
    'https://www.paho.org/es/rss.xml'
]
for f in feeds:
    r = feedparser.parse(f)
    print(f'{len(r.entries)} -> {f}')
    for e in r.entries[:3]:
        print('  ' + e.get('title','')[:60])
