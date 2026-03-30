import urllib.request, json, re, os

URL = 'https://t.me/s/novgorod42'

try:
    req = urllib.request.Request(URL, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'ru-RU,ru;q=0.9',
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode('utf-8')

    # Сохраняем сырой HTML для отладки
    os.makedirs('docs', exist_ok=True)
    with open('docs/debug.html', 'w', encoding='utf-8') as f:
        f.write(html[:5000])

    print(f"HTML length: {len(html)}")
    print(f"Has tgme_widget_message: {'tgme_widget_message' in html}")
    print(f"First 500 chars: {html[:500]}")

    blocks = re.split(r'<div class="tgme_widget_message_wrap', html)
    print(f"Blocks found: {len(blocks)-1}")

    def clean(s): return re.sub(r'<[^>]+>', '', s).strip()
    def get_img(b):
        m = re.search(r'background-image:url\(\'([^\']+)\'', b)
        if m: return m.group(1)
        m = re.search(r'<img[^>]+src="([^"]+)"', b)
        return m.group(1) if m else ''
    def get_link(b):
        m = re.search(r'tgme_widget_message_date.*?href="([^"]+)"', b, re.S)
        return m.group(1) if m else ''
    def get_date(b):
        m = re.search(r'<time[^>]+datetime="([^"]+)"', b)
        return m.group(1)[:10] if m else ''
    def get_text(b):
        m = re.search(r'tgme_widget_message_text[^"]*"[^>]*>([\s\S]*?)</div>', b)
        return clean(m.group(1))[:200] if m else ''

    items = []
    for b in blocks[1:]:
        link = get_link(b)
        text = get_text(b)
        if not link: continue
        title = (text[:60]+'...') if len(text)>60 else text or 'novgorod42'
        items.append({'title':title,'link':link,'date':get_date(b),'description':text,'imageUrl':get_img(b)})
        if len(items)>=10: break

    with open('docs/feed.json','w',encoding='utf-8') as f:
        json.dump({'items':items},f,ensure_ascii=False,indent=2)
    print(f"Items saved: {len(items)}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback; traceback.print_exc()
    os.makedirs('docs', exist_ok=True)
    with open('docs/feed.json','w') as f:
        json.dump({'items':[]},f)
