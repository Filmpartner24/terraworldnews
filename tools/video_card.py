#!/usr/bin/env python3
"""TWN-Musikvideo-Grafik (Nedy 26.10.2026) – ersetzt bei Musik-Meldungen MIT Video (yt) die dunkle Titelgrafik.
Rechtlich sicher: eigene Grafik (Schallplatte, Equalizer, Künstler + Song), nie YouTube-Vorschaubilder/Cover.

Aufruf:  python3 tools/video_card.py content/<datum>-popfolk.json [weitere content/*.json ...]
Für jedes Item mit s="musik", "yt" und eigener Titelgrafik (img.own, Dateiname mit "-tg"):
  1. Gibt es in content/musik/popfolk-stars.json ein freies Commons-Foto eines beteiligten Künstlers,
     wird dieses als img gesetzt (f=/assets/news/<datum>/<id>.webp + page/art/lic; die Action lädt und schneidet es zu).
  2. Sonst wird static/assets/news/<datum>/<id>-vc.webp erzeugt und als img (own:true) eingetragen.
Die alte -tg-Grafik wird gelöscht. Mehrfaches Ausführen ist unschädlich.
Als Modul: make(path, artist, song, kicker, seed)."""
import sys, os, re, json, math, random, hashlib
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOLD = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
W, H = 1200, 675
PALETTES = [('#ff2d95', '#5b2bd6'), ('#ff7a18', '#c2185b'), ('#00c2a8', '#3a1c71'), ('#f5b700', '#d7263d'),
            ('#2d9cff', '#7b2cbf'), ('#ff4d6d', '#3d1a78'), ('#12c2e9', '#c471ed'), ('#f64f59', '#5f2c82')]
GENRE = {'rock': 'Rock', 'metal': 'Metal', 'indie': 'Indie', 'pop': 'Pop', 'hiphop': 'Hip-Hop', 'rnbsoul': 'R&B · Soul',
         'punk': 'Punk', 'electronic': 'Electronic', 'dance': 'Dance', 'latin': 'Latin', 'reggae': 'Reggae',
         'country': 'Country', 'folk': 'Folk', 'world': 'World', 'schlager': 'Schlager', 'deutschpop': 'Deutschpop',
         'popfolk': 'Pop-Folk', 'jazz': 'Jazz', 'blues': 'Blues', 'klassik': 'Klassik', 'filmmusik': 'Soundtrack'}
LAND_STYLE = {'bg': 'Chalga', 'rs': 'Turbo-Folk', 'ro': 'Manele', 'gr': 'Laïko', 'tr': 'Arabesk', 'al': 'Tallava',
              'xk': 'Tallava', 'ba': 'Sevdah', 'mk': 'Pop-Folk', 'hr': 'Pop-Folk'}


def _f(sz):
    try: return ImageFont.truetype(BOLD, sz)
    except Exception: return ImageFont.load_default()


def _hex(c): return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def _fit(dr, t, maxw, sizes):
    for s in sizes:
        if dr.textlength(t, font=_f(s)) <= maxw: return s
    return sizes[-1]


def _short(dr, t, maxw, sz):
    while t and dr.textlength(t, font=_f(sz)) > maxw: t = t[:-2].rstrip() + '…' if not t.endswith('…') else t[:-2] + '…'
    return t


def make(path, artist, song, kicker, seed=''):
    h = int(hashlib.md5((seed or artist).encode()).hexdigest(), 16)
    c1, c2 = PALETTES[h % len(PALETTES)]
    a, b = _hex(c1), _hex(c2); rnd = random.Random(h)
    # diagonaler Farbverlauf (klein rechnen, dann hochskalieren)
    sw, sh = 120, 68; g = Image.new('RGB', (sw, sh)); px = g.load()
    for y in range(sh):
        for x in range(sw):
            f = x / sw * 0.6 + y / sh * 0.4
            px[x, y] = tuple(int(a[i] * (1 - f) + b[i] * f * 0.85) for i in range(3))
    im = g.resize((W, H), Image.BICUBIC).convert('RGBA')
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    cx, cy, r = W - 230, H // 2 - 10, 330          # Schallplatte
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(10, 8, 20, 235))
    for k in range(14):
        rr = r - 18 - k * 14; d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(255, 255, 255, 18), width=2)
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 200, 240, fill=(255, 255, 255, 22))
    d.ellipse([cx - 95, cy - 95, cx + 95, cy + 95], fill=a + (255,)); d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(10, 8, 20, 255))
    for i in range(48):                              # Equalizer
        hh = rnd.randint(20, 140) * (0.5 + 0.5 * abs(math.sin(i / 5)))
        x = 60 + i * 14; d.rounded_rectangle([x, H - 60 - hh, x + 8, H - 60], radius=4, fill=(255, 255, 255, 40))
    im = Image.alpha_composite(im, ov)
    mask = Image.new('L', (W, 1)); mask.putdata([int(170 * max(0, 1 - x / 760)) for x in range(W)])  # links dunkel für Lesbarkeit
    mask = mask.resize((W, H))
    im = Image.composite(Image.new('RGBA', (W, H), (8, 6, 18, 255)), im, mask)
    dr = ImageDraw.Draw(im)
    k = kicker.upper(); kw = dr.textlength(k, font=_f(30))
    dr.rounded_rectangle([60, 52, 60 + kw + 36, 104], radius=26, fill=(255, 255, 255, 235)); dr.text((78, 56), k, font=_f(30), fill=b)
    s = _fit(dr, artist, 680, (80, 72, 64, 56, 48, 42)); art = _short(dr, artist, 680, s)
    dr.text((60, H - 228), art, font=_f(s), fill=(255, 255, 255))
    if song:
        s2 = _fit(dr, song, 680, (46, 42, 38, 34, 30)); sg = _short(dr, song, 680, s2)
        dr.text((62, H - 228 + int(s * 1.15)), sg, font=_f(s2), fill=(255, 209, 234))
    dr.text((62, H - 48), 'TERRA WORLD NEWS · TWN MUSIC', font=_f(22), fill=(255, 255, 255, 170))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.convert('RGB').save(path, 'WEBP', quality=88)


def split_title(t):
    """„Künstler – „Song“: Zusatz“ -> (Künstler, „Song“)"""
    artist = t.split(' – ')[0].strip() if ' – ' in t else t.split(':')[0].strip()
    m = re.search(r'„([^“]+)“', t)
    return artist, (f'„{m.group(1)}“' if m else '')


def _stars():
    p = os.path.join(HERE, 'content', 'musik', 'popfolk-stars.json')
    return json.load(open(p))['stars'] if os.path.exists(p) else []


def process(path):
    d = json.load(open(path)); date = d.get('date') or os.path.basename(path)[:10]; stars = _stars(); n = 0
    for it in d.get('items', []):
        im = it.get('img') or {}
        if it.get('s') != 'musik' or not it.get('yt') or not im.get('own') or '-tg' not in im.get('f', ''): continue
        artist, song = split_title(it['de']['t'])
        old = os.path.join(HERE, 'static', im['f'].lstrip('/'))
        st = next((s for s in stars if re.search(r'(?<!\w)' + re.escape(s['name'].lower()) + r'(?!\w)', artist.lower())), None)
        if st:
            nm = st['name']
            it['img'] = {'f': f'/assets/news/{date}/{it["id"]}.webp', 'w': 1200, 'h': 675, 'art': st['art'], 'lic': st['lic'],
                         'page': st['page'], 'alt': {'de': f'{nm} (Archivbild)', 'bg': f'{nm} (архивна снимка)', 'en': f'{nm} (archive photo)'}}
        else:
            if it['id'].startswith('review') or it.get('rv'): kind = 'Album'
            else: kind = 'Live' if it.get('vk') == 'live' else 'Video'
            style = LAND_STYLE.get(it.get('land')) if it.get('sub') == 'popfolk' else None
            kicker = f'{kind} · {style or GENRE.get(it.get("sub"), "Music")}'
            f = f'/assets/news/{date}/{it["id"]}-vc.webp'
            make(os.path.join(HERE, 'static', f.lstrip('/')), artist, song, kicker, it['id'])
            ta = {L: split_title(it[L]['t']) for L in ('de', 'bg', 'en')}
            it['img'] = {'f': f, 'w': 1200, 'h': 675, 'own': True,
                         'alt': {'de': f'Grafik: {ta["de"][0]} {ta["de"][1]}'.strip(), 'bg': f'Графика: {ta["bg"][0]}'.strip(), 'en': f'Graphic: {ta["en"][0]}'.strip()}}
        if os.path.exists(old): os.remove(old)
        n += 1; print('  ', it['id'], '->', 'Starfoto ' + st['name'] if st else it['img']['f'])
    if n: json.dump(d, open(path, 'w'), ensure_ascii=False, indent=1)
    return n


if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(p, process(p))
