#!/usr/bin/env python3
"""Photo candidates from Wikimedia Commons (runs in the GitHub Action, which can reach Commons).

Input:  candidates/<date>/requests.json  — [{"id": "<article id>", "q": ["query 1", "query 2", ...]}, ...]
Output: candidates/<date>/<id>.json      — up to 8 freely licensed candidates with page/author/licence
        candidates/<date>/<id>.jpg       — numbered contact sheet (1..8) to look at before choosing
Items that already have an output JSON are skipped. Only CC BY, CC BY-SA, CC0, public domain
and OGL files are kept; NC/ND, unknown licences and files tagged as AI-generated are dropped."""
import json, glob, os, io, re, html, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {'User-Agent': 'TWN-World-News-photo-search/1.0 (https://terraworldnews.com; media@filmpartner24.com)'}
API = 'https://commons.wikimedia.org/w/api.php?'
MAX = 8
OK_LIC = re.compile(r'^(cc[- ]by(-sa)?[- ]?[0-9.]*( [a-z\-]+)?|cc0|public domain|pd[- ].*|ogl.*|attribution.*)$', re.I)

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()

def clean(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s or '')).strip()

def search(q):
    p = {'action': 'query', 'format': 'json', 'generator': 'search', 'gsrsearch': f'{q} filetype:bitmap',
         'gsrnamespace': '6', 'gsrlimit': '20', 'prop': 'imageinfo|categories', 'cllimit': '50',
         'iiprop': 'url|extmetadata|size', 'iiurlwidth': '360'}
    j = json.loads(get(API + urllib.parse.urlencode(p)))
    pages = sorted((j.get('query') or {}).get('pages', {}).values(), key=lambda x: x.get('index', 99))
    out = []
    for pg in pages:
        ii = (pg.get('imageinfo') or [{}])[0]
        md = ii.get('extmetadata') or {}
        lic = clean((md.get('LicenseShortName') or {}).get('value'))
        cats = ' '.join(c['title'] for c in pg.get('categories', [])).lower()
        if not lic or re.search(r'\b(nc|nd)\b|noncommercial|no deriv', lic, re.I) or not OK_LIC.match(lic):
            continue
        if 'ai-generated' in cats or 'ai generated' in cats or 'midjourney' in cats or 'dall-e' in cats or 'stable diffusion' in cats:
            continue
        if ii.get('width', 0) < 800:
            continue
        out.append({'title': pg['title'], 'page': ii.get('descriptionurl'), 'thumb': ii.get('thumburl'),
                    'art': clean((md.get('Artist') or {}).get('value'))[:120], 'lic': lic,
                    'desc': clean((md.get('ImageDescription') or {}).get('value'))[:300],
                    'w': ii.get('width'), 'h': ii.get('height')})
    return out

def sheet(cands, dest):
    tw, th = 360, 240
    cols = 4; rows = (len(cands) + cols - 1) // cols
    img = Image.new('RGB', (cols * tw, rows * th), 'white')
    d = ImageDraw.Draw(img)
    try: font = ImageFont.truetype('DejaVuSans-Bold.ttf', 28)
    except Exception: font = ImageFont.load_default()
    for i, c in enumerate(cands):
        try:
            t = Image.open(io.BytesIO(get(c['thumb']))).convert('RGB')
            t.thumbnail((tw - 6, th - 6))
            x, y = (i % cols) * tw, (i // cols) * th
            img.paste(t, (x + (tw - t.width) // 2, y + (th - t.height) // 2))
            d.rectangle([x, y, x + 44, y + 38], fill='black'); d.text((x + 10, y + 4), str(i + 1), fill='white', font=font)
        except Exception as ex:
            print('thumb failed', c['title'], ex)
    img.save(dest, quality=82)

def main():
    for req in sorted(glob.glob(os.path.join(HERE, 'candidates', '*', 'requests.json'))):
        folder = os.path.dirname(req)
        for r in json.load(open(req, encoding='utf-8')):
            out = os.path.join(folder, r['id'] + '.json')
            if os.path.exists(out):
                continue
            seen, cands = set(), []
            for q in r.get('q', []):
                try:
                    for c in search(q):
                        if c['title'] not in seen:
                            seen.add(c['title']); cands.append(c)
                except Exception as ex:
                    print('search failed', q, ex)
                if len(cands) >= MAX: break
            cands = cands[:MAX]
            json.dump(cands, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            if cands: sheet(cands, os.path.join(folder, r['id'] + '.jpg'))
            print(r['id'], len(cands), 'candidates')

if __name__ == '__main__':
    main()
