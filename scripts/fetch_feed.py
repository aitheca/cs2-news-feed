import urllib.request, json, re, os

# Парсим публичную веб-версию канала напрямую
URL = 'https://t.me/s/novgorod42'

def clean(s):
    return re.sub(r'<[^>]+>', '', s).strip()

def get_img(block):
    # Фото поста
    m = re.search(r'<a[^>]+style="[^"]*background-image:url\(\'([^\']+)\'', block)
    if m: return m.group(1)
    m = re.search(r'<img[^>]+src="([^"]+)"', block)
    return m.group(1) if m else ''

def get_link(block):
    m = re.search(r'tgme_widget_message_date.*?href="([^"]+)"', block, re.S)
    return m.group(1) if m else ''

def get_date(block):
    m = re.search(r'<time[^>]+datetime="([^"]+)"', block)
    return m.group(1)[:10] if m else ''

def get_text(block):
    m = re.search(r'<div class="tgme_widget_message_text[^"]*"[^>]*>([\s\S]*?)</div>', block)
    if m:
        t = clean(m.group(1))
        return t[:200]
    return ''

try:
    req = urllib.request.Request(URL, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode('utf-8')

    # Разбиваем на блоки сообщений
    blocks = re.split(r'<div class="tgme_widget_message_wrap', html)
    items = []
    for b in blocks[1:]:
        text = get_text(b)
        link = get_link(b)
        date = get_date(b)
        img  = get_img(b)
        if not link:
            continue
        # Заголовок = первые 60 символов текста
        title = text[:60].rstrip() + ('...' if len(text) > 60 else '') if text else 'novgorod42'
        items.append({
            'title': title,
            'link': link,
            'date': date,
            'description': text,
            'imageUrl': img
        })
        if len(items) >= 10:
            break

    os.makedirs('docs', exist_ok=True)
    with open('docs/feed.json', 'w', encoding='utf-8') as f:
        json.dump({'items': items}, f, ensure_ascii=False, indent=2)

    print(f"OK: {len(items)} items saved")
    for it in items[:3]:
        print(f"  - {it['title'][:50]} | img={'yes' if it['imageUrl'] else 'no'}")

except Exception as e:
    print(f"ERROR: {e}")
    os.makedirs('docs', exist_ok=True)
    if not os.path.exists('docs/feed.json'):
        with open('docs/feed.json', 'w') as f:
            json.dump({'items': []}, f)
