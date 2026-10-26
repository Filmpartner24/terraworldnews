#!/usr/bin/env python3
"""TWN-Musikvideo-Grafik (Nedy 26.10.2026) – ersetzt bei Musik-Meldungen MIT Video (yt) die dunkle Titelgrafik.
Rechtlich sicher: eigene Grafik (Schallplatte, Equalizer, Künstler + Song), nie YouTube-Vorschaubilder/Cover.

Aufruf:  python3 tools/video_card.py content/<datum>-popfolk.json [weitere content/*.json ...]
Für jedes Item mit s="musik", "yt" und eigener Titelgrafik (img.own, Dateiname mit "-tg") ODER einem Foto, das in den
7 Tagen davor schon bei einer anderen Musik-Meldung verwendet wurde (keine doppelten Fotos – Nedy 26.10.2026):
  1. Gibt es in content/musik/popfolk-stars.json ein freies, noch nicht verwendetes Commons-Foto eines beteiligten Künstlers,
     wird dieses als img gesetzt (f=/assets/news/<datum>/<id>.webp + page/art/lic; die Action lädt und schneidet es zu).
  2. Sonst wird static/assets/news/<datum>/<id>-vc.webp erzeugt und als img (own:true) eingetragen.
Die alte -tg-Grafik wird gelöscht. Mehrfaches Ausführen ist unschädlich.
Läuft zusätzlich automatisch in der GitHub-Action (ohne Argument = alle content/*.json), damit keine Musik-Videokachel dunkel bleibt.
Als Modul: make(path, artist, song, kicker, seed)."""
import sys, os, re, json, math, random, hashlib
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOLD = os.path.join(HERE, 'tools', 'fonts', 'Poppins-Bold.ttf')  # SIL OFL 1.1, siehe tools/fonts/OFL-Poppins.txt
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
    if not song and dr.textlength(artist, font=_f(56)) > 680:  # Schlagzeile statt Künstler/Song: umbrechen (max. 3 Zeilen)
        import textwrap
        for s in (50, 44, 40):
            lines = textwrap.wrap(artist, width=int(680 / (s * 0.55)))
            if len(lines) <= 3: break
        lines = lines[:3]; y = H - 90 - len(lines) * int(s * 1.2)
        for ln in lines:
            dr.text((60, y), _short(dr, ln, 700, s), font=_f(s), fill=(255, 255, 255)); y += int(s * 1.2)
        dr.text((62, H - 48), 'TERRA WORLD NEWS · TWN MUSIC', font=_f(22), fill=(255, 255, 255, 170))
        os.makedirs(os.path.dirname(path), exist_ok=True); im.convert('RGB').save(path, 'WEBP', quality=88); return
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


def _card(it, date):
    artist, song = split_title(it['de']['t'])
    if it['id'].startswith('review') or it.get('rv'): kind = 'Album'
    elif not song: kind = 'News'
    else: kind = 'Live' if it.get('vk') == 'live' else 'Video'
    if not song: artist = it['de']['t']
    style = LAND_STYLE.get(it.get('land')) if it.get('sub') == 'popfolk' else None
    kicker = f'{kind} · {style or GENRE.get(it.get("sub"), "Music")}'
    f = f'/assets/news/{date}/{it["id"]}-vc.webp'
    make(os.path.join(HERE, 'static', f.lstrip('/')), artist, song, kicker, it['id'])
    ta = {L: split_title(it[L]['t']) for L in ('de', 'bg', 'en')}
    it['img'] = {'f': f, 'w': 1200, 'h': 675, 'own': True,
                 'alt': {'de': f'Grafik: {ta["de"][0]} {ta["de"][1]}'.strip(), 'bg': f'Графика: {ta["bg"][0]}'.strip(), 'en': f'Graphic: {ta["en"][0]}'.strip()}}


def _star(it, date, st):
    nm = st['name']; f = f'/assets/news/{date}/{it["id"]}.webp'
    it['img'] = {'f': f, 'w': 1200, 'h': 675, 'art': st['art'], 'lic': st['lic'],
                 'page': st['page'], 'alt': {'de': f'{nm} (Archivbild)', 'bg': f'{nm} (архивна снимка)', 'en': f'{nm} (archive photo)'}}
    src = os.path.join(HERE, 'static', st['f'].lstrip('/')); dest = os.path.join(HERE, 'static', f.lstrip('/'))
    if os.path.exists(src) and not os.path.exists(dest):  # sofort lokal zuschneiden – keine schwarze Kachel bis zum Action-Lauf
        sys.path.insert(0, os.path.join(HERE, 'tools')); from fetch_images import render
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        render(open(src, 'rb').read()).save(dest, 'WEBP', quality=80, method=6)


def run(targets=None):
    """Alle content/*.json chronologisch durchgehen. Ein Foto (Commons-Seite) darf bei Musik-Meldungen innerhalb von
    WINDOW Tagen nur EINMAL vorkommen (Nedy 26.10.2026: „nicht dieselben Fotos, sonst denken die Zuschauer, es sind
    dieselben Videos“). Video-Items mit doppeltem Foto oder alter -tg-Grafik bekommen ein noch freies Starfoto oder
    die Musikvideo-Grafik. Geändert werden nur Dateien in targets (None = alle)."""
    import glob, datetime as dt
    WINDOW = 7
    files = sorted(glob.glob(os.path.join(HERE, 'content', '*.json')))
    tg = None if targets is None else {os.path.abspath(t) for t in targets}
    data, rows = {}, []
    for p in files:
        try: d = json.load(open(p))
        except Exception: continue
        if not isinstance(d, dict) or not isinstance(d.get('items'), list): continue
        date = d.get('date') or os.path.basename(p)[:10]
        try: day = dt.date.fromisoformat(date[:10])
        except Exception: continue
        data[p] = d
        for k, it in enumerate(d['items']):
            if isinstance(it, dict) and it.get('s') == 'musik': rows.append((date, it.get('time') or '', p, k, day, it))
    rows.sort(key=lambda r: r[:4])
    stars = _stars(); used = {}; changed = set()
    dup = lambda page, day: bool(page) and page in used and (day - used[page]).days <= WINDOW
    for date, _, p, _, day, it in rows:
        im = it.get('img') or {}
        if it.get('yt') and (tg is None or os.path.abspath(p) in tg):
            old_tg = im.get('own') and '-tg' in im.get('f', '')
            if old_tg or dup(im.get('page'), day):
                artist, _ = split_title(it['de']['t'])
                st = next((s for s in stars if re.search(r'(?<!\w)' + re.escape(s['name'].lower()) + r'(?!\w)', artist.lower())
                           and not dup(s['page'], day)), None)
                if st: _star(it, date, st)
                else: _card(it, date)
                if old_tg:
                    old = os.path.join(HERE, 'static', im['f'].lstrip('/'))
                    if os.path.exists(old): os.remove(old)
                changed.add(p); print('  ', os.path.basename(p), it['id'], '->', 'Starfoto ' + st['name'] if st else it['img']['f'])
        pg = (it.get('img') or {}).get('page')
        if pg: used[pg] = day
    for p in changed: json.dump(data[p], open(p, 'w'), ensure_ascii=False, indent=1)
    return len(changed)


if __name__ == '__main__':
    run(sys.argv[1:] or None)  # ohne Argument: alle content/*.json (so läuft es in der Action)
