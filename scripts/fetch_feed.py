import urllib.request, json, re, os

RSS_URL = 'https://rsshub.app/telegram/channel/novgorod42'

def get(xml, tag):
    m = re.search(r'<' + tag + r'[^>]*>([\s\S]*?)<\/' + tag + r'>', xml)
    return re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else ''

def get_img(xml):
    m = re.search(r'enclosure[^>]+url="([^"]+)"', xml)
    if m: return m.group(1)
    m = re.search(r'<media:thumbnail[^>]+url="([^"]+)"', xml)
    if m: return m.group(1)
    m = re.search(r'<img[^>]+src="([^"]+)"', xml)
    return m.group(1) if m else ''

try:
    req = urllib.request.Request(RSS_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        xml = r.read().decode('utf-8')

    blocks = xml.split('<item>')
    items = []
    for b in blocks[1:11]:
        items.append({
            'title': get(b, 'title') or 'novgorod42',
            'link': get(b, 'link'),
            'date': get(b, 'pubDate'),
            'description': get(b, 'description')[:200],
            'imageUrl': get_img(b)
        })

    os.makedirs('docs', exist_ok=True)
    with open('docs/feed.json', 'w', encoding='utf-8') as f:
        json.dump({'items': items}, f, ensure_ascii=False)

    print(f"OK: {len(items)} items saved")

except Exception as e:
    print(f"ERROR: {e}")
    # Write empty fallback so file always exists
    os.makedirs('docs', exist_ok=True)
    if not os.path.exists('docs/feed.json'):
        with open('docs/feed.json', 'w') as f:
            json.dump({'items': []}, f)
