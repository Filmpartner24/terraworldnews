#!/usr/bin/env python3
"""Download missing article photos from Wikimedia Commons and store them as 1200x675 WebP.
Reads content/*.json; for every item with img.page (a Commons file page) whose file
static/<img.f> does not exist yet, fetches a 1600px thumbnail and crops it:
portraits (aspect < 1.25) are letterboxed on the photo's corner colour, others cover-cropped."""
import json, glob, os, sys, io, urllib.parse, urllib.request
from PIL import Image

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {'User-Agent': 'TERRA-WORLD-NEWS-image-fetcher/1.0 (https://terraworldnews.com; media@filmpartner24.com)'}
W, H = 1200, 675

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()

def thumb_url(title):
    q = urllib.parse.urlencode({'action': 'query', 'titles': title, 'prop': 'imageinfo', 'iiprop': 'url',
                                'iiurlwidth': '1600', 'format': 'json'})
    j = json.loads(get('https://commons.wikimedia.org/w/api.php?' + q))
    page = next(iter(j['query']['pages'].values()))
    ii = page['imageinfo'][0]
    return ii.get('thumburl') or ii['url']

def render(data):
    im = Image.open(io.BytesIO(data)).convert('RGB')
    ar = im.width / im.height
    if ar < 1.25:
        bg = im.getpixel((3, 3))
        canvas = Image.new('RGB', (W, H), bg)
        sh = min(im.height, int(im.width * 1.05))
        crop = im.crop((0, 0, im.width, sh))
        dw = round(crop.width * H / crop.height)
        canvas.paste(crop.resize((dw, H), Image.LANCZOS), ((W - dw) // 2, 0))
        return canvas
    if ar > W / H:
        sw = im.height * W / H; sx = (im.width - sw) / 2
        box = (sx, 0, sx + sw, im.height)
    else:
        sh = im.width * H / W; sy = (im.height - sh) * 0.4
        box = (0, sy, im.width, sy + sh)
    return im.crop(tuple(round(v) for v in box)).resize((W, H), Image.LANCZOS)

def main():
    done = fail = 0
    for f in sorted(glob.glob(os.path.join(HERE, 'content', '*.json'))) + glob.glob(os.path.join(HERE, 'content', 'football', '_images.json')) + glob.glob(os.path.join(HERE, 'content', 'boxing', '_images.json')) + glob.glob(os.path.join(HERE, 'content', 'mma', '_images.json')) + glob.glob(os.path.join(HERE, 'content', 'sport', '_images.json')) + glob.glob(os.path.join(HERE, 'content', 'nations-league', '_images.json')) + glob.glob(os.path.join(HERE, 'content', 'dating', '_images.json')) + glob.glob(os.path.join(HERE, 'content', 'mode', '_images.json')):
        for it in json.load(open(f, encoding='utf-8')).get('items', []):
            img = it.get('img') or {}
            page, rel = img.get('page', ''), img.get('f', '')
            if 'commons.wikimedia.org/wiki/' not in page or not rel:
                continue
            dest = os.path.join(HERE, 'static', rel.lstrip('/'))
            if os.path.exists(dest):
                continue
            title = urllib.parse.unquote(page.split('/wiki/', 1)[1]).replace('_', ' ')
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                render(get(thumb_url(title))).save(dest, 'WEBP', quality=80, method=6)
                done += 1; print('ok', rel)
            except Exception as ex:
                fail += 1; print('FAIL', rel, ex, file=sys.stderr)
    print(f'{done} new images, {fail} failed')

if __name__ == '__main__':
    main()
