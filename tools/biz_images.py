#!/usr/bin/env python3
"""TERRA WORLD NEWS – eigene Infografiken für die Rubrik Business.
Usage: python3 tools/biz_images.py [YYYY-MM-DD]   (Standard: neueste Datei in content/business/)
Liest content/business/<datum>.json, zeichnet je Block eine 1200x675-Grafik aus den Daten des Blocks
(static/assets/news/<datum>/biz-<id>.webp) und trägt sie als "img" (own: true) in die Datei ein.
Keine Fremdbilder: Gestaltung und Zeichnung komplett selbst erstellt, Zahlen aus den Quellen des Blocks."""
import json, os, sys, glob
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = os.path.join(HERE, 'static', 'assets', 'fonts')
def F(name, size): return ImageFont.truetype(os.path.join(FD, name), size)
NB = lambda s: F('pt-sans-narrow-latin-700-normal.woff2', s)
NR = lambda s: F('pt-sans-narrow-latin-400-normal.woff2', s)
SB = lambda s: F('pt-sans-latin-700-normal.woff2', s)
W, H = 1200, 675
UP, DN, EQ = (91, 227, 166), (255, 128, 116), (255, 207, 58)
WHITE, SOFT = (255, 255, 255), (200, 220, 212)

THEME = {  # Hintergrund, Akzent, Titel, Untertitel, Art
 'strom-ibex': ((10, 38, 64), (255, 207, 58), 'IBEX DAY-AHEAD', 'BULGARIA · EUR/MWh', 'power'),
 'wallstreet': ((14, 30, 74), (91, 227, 166), 'WALL STREET', 'NEW YORK · NYSE · NASDAQ', 'market'),
 'deutsche-boerse': ((10, 61, 46), (91, 227, 166), 'FRANKFURT · XETRA', 'DAX · MDAX · TecDAX', 'market'),
 'bg-energie-aktien': ((40, 30, 70), (91, 227, 166), 'SOFIA · BSE', 'SOFIX · BGBX40 · BGTR30', 'market'),
 'invest-bulgarien': ((10, 70, 70), (255, 207, 58), 'INVEST · BULGARIA', 'EUR m · REGIONS', 'invest'),
 'invest-deutschland': ((30, 34, 40), (255, 207, 58), 'INVEST · GERMANY', 'EUR m · REGIONS', 'invest'),
}
ALT = {'power': ('Графика: цени на електроенергията на IBEX', 'Grafik: Strompreise an der Börse IBEX', 'Graphic: electricity prices on the IBEX exchange'),
       'market': ('Графика: борсови индекси', 'Grafik: Börsenindizes', 'Graphic: stock market indices'),
       'invest': ('Графика: инвестиционни проекти по региони', 'Grafik: Investitionsprojekte nach Regionen', 'Graphic: investment projects by region')}

def L(x, l='en'):
    return (x.get(l) or x.get('de') or '') if isinstance(x, dict) else ('' if x is None else str(x))
def fnum(v, dec=2):
    t = f'{abs(v):,.{dec}f}'.replace(',', ' ').replace('.', ',')
    return ('−' if v < 0 else '') + t
def tri(d, x, y, s, up, col):
    d.polygon([(x, y + s), (x + s, y + s), (x + s / 2, y)] if up else [(x, y), (x + s, y), (x + s / 2, y + s)], fill=col)
def chg_txt(d, x, y, v, size=30):
    col = UP if v > 0 else DN if v < 0 else EQ
    if v != 0: tri(d, x, y + size * .28, size * .55, v > 0, col)
    else: d.rectangle([x, y + size * .3, x + size * .5, y + size * .75], fill=col)
    d.text((x + size * .75, y), ('+' if v > 0 else '') + fnum(v) + ' %', font=SB(size), fill=col)
def fit(d, text, font_fn, size, maxw):
    while size > 14 and d.textlength(text, font=font_fn(size)) > maxw: size -= 2
    return font_fn(size)

def base(bg, acc, title, sub, date):
    im = Image.new('RGB', (W, H), bg); d = ImageDraw.Draw(im)
    for x in range(0, W, 40): d.line([(x, 0), (x, H)], fill=tuple(min(255, c + 9) for c in bg))
    for y in range(0, H, 40): d.line([(0, y), (W, y)], fill=tuple(min(255, c + 9) for c in bg))
    d.rectangle([0, 0, W, 10], fill=acc)
    d.text((56, 36), 'TERRA WORLD NEWS  ·  BUSINESS', font=NB(26), fill=acc)
    dd = '.'.join(reversed(date.split('-')))
    d.text((W - 56 - d.textlength(dd, font=NB(26)), 36), dd, font=NB(26), fill=SOFT)
    d.text((54, 74), title, font=fit(d, title, NB, 92, W - 110), fill=WHITE)
    d.text((58, 178), sub, font=NR(30), fill=SOFT)
    return im, d

def hbars(d, rows, x0, y0, w, h, acc, fmt, sym=True):
    """rows: [(label, value)] -> horizontale Balken (symmetrisch um 0 falls sym)."""
    rows = rows[:6]
    if not rows: return
    n = len(rows); rh = min(64, h / n); lw = 300 if not sym else 230
    mx = max(abs(v) for _, v in rows) or 1
    cx = x0 + lw + ((w - lw) / 2 if sym and any(v < 0 for _, v in rows) else 0)
    span = (w - lw) / 2 - 90 if cx > x0 + lw else (w - lw) - 150
    for i, (lab, v) in enumerate(rows):
        y = y0 + i * rh
        d.text((x0, y + rh * .18), lab, font=fit(d, lab, NB, 30, lw - 14), fill=WHITE)
        bl = max(4, abs(v) / mx * span)
        col = acc if not sym else (UP if v > 0 else DN if v < 0 else EQ)
        a, b = (cx, cx + bl) if v >= 0 else (cx - bl, cx)
        d.rectangle([a, y + rh * .2, b, y + rh * .78], fill=col)
        t = fmt(v)
        tx = b + 10 if v >= 0 else a - 10 - d.textlength(t, font=SB(24))
        d.text((tx, y + rh * .22), t, font=SB(24), fill=WHITE)
    if sym: d.line([(cx, y0 - 6), (cx, y0 + n * rh)], fill=SOFT, width=2)

def render(b, date):
    bg, acc, title, sub, kind = THEME.get(b['id'], ((20, 40, 50), (255, 207, 58), b['id'].upper(), '', 'market'))
    im, d = base(bg, acc, title, sub, date)
    if kind == 'power':
        t = b['tables'][0]; rows = t['rows'][:3]
        labs = ['BASE', 'PEAK', 'OFF-PEAK']
        cur = [r[1] for r in rows]; prev = [r[3] if len(r) > 3 else None for r in rows]
        mx = max([v for v in cur + prev if v] or [1])
        x0, yb, gh = 70, 560, 300
        for i, (lab, c, p) in enumerate(zip(labs, cur, prev)):
            gx = x0 + i * 205
            if p:
                hp = p / mx * gh; d.rectangle([gx + 92, yb - hp, gx + 152, yb], fill=(90, 110, 130))
            if c:
                hc = c / mx * gh; d.rectangle([gx, yb - hc, gx + 84, yb], fill=acc)
                d.text((gx, yb - hc - 40), fnum(c), font=SB(30), fill=WHITE)
            d.text((gx, yb + 10), lab, font=NB(28), fill=SOFT)
        d.line([(60, yb), (680, yb)], fill=SOFT, width=2)
        # Legende
        import datetime as _dt
        _d = _dt.date.fromisoformat(date); _p = _d - _dt.timedelta(days=1)
        d.rectangle([720, 250, 744, 274], fill=acc); d.text((756, 246), f'{_d.day:02d}.{_d.month:02d}.', font=NB(26), fill=WHITE)
        if any(prev):
            d.rectangle([840, 250, 864, 274], fill=(90, 110, 130)); d.text((876, 246), f'{_p.day:02d}.{_p.month:02d}.', font=NB(26), fill=SOFT)
        k = b['kpi'][0]
        d.text((720, 350), 'BASE  EUR/MWh', font=NB(30), fill=SOFT)
        d.text((716, 384), fnum(k['v']), font=NB(120), fill=WHITE)
        if k.get('chg') is not None: chg_txt(d, 724, 520, k['chg'], 34)
        vol = next((x for x in b['kpi'] if L(x.get('u')) == 'MWh'), None)
        if vol: d.text((724, 578), f'{fnum(vol["v"], 0)} MWh', font=NB(36), fill=SOFT)
        # Blitz
        d.polygon([(1100, 230), (1050, 330), (1085, 330), (1060, 420), (1130, 300), (1092, 300), (1120, 230)], fill=acc)
    elif kind == 'market':
        t = next((t for t in b['tables'] if any(c['k'] == 'chg' for c in t['cols'])), None)
        rows = []
        if t:
            ci = next(i for i, c in enumerate(t['cols']) if c['k'] == 'chg')
            rows = [(L(r[0]), r[ci]) for r in t['rows'] if r[ci] is not None]
        d.text((58, 238), 'DAY %', font=NB(24), fill=SOFT)
        hbars(d, rows, 58, 280, 640, 360, acc, lambda v: ('+' if v > 0 else '') + fnum(v) + ' %')
        ks = [k for k in b['kpi'] if k.get('chg') is not None][:3]
        for i, k in enumerate(ks):
            y = 240 + i * 140
            d.rectangle([740, y, 1144, y + 124], outline=(255, 255, 255), width=1)
            d.rectangle([740, y, 1144, y + 6], fill=acc)
            lab = L(k['l']).upper()
            d.text((760, y + 14), lab, font=fit(d, lab, NB, 26, 370), fill=SOFT)
            d.text((758, y + 40), fnum(k['v'], k.get('dec', 2)), font=NB(56), fill=WHITE)
            chg_txt(d, 1000, y + 58, k['chg'], 24)
    else:
        t = b['tables'][0]
        ai = next((i for i, c in enumerate(t['cols']) if c['k'] == 'num'), None)
        rows = []
        if ai is not None:
            for r in t['rows']:
                if r[ai] is None: continue
                reg = L(r[0]).split(' (')[0].replace('Mecklenburg-W. Pomerania', 'Meckl.-Vorpommern')
                co = L(r[1]).split(' – ')[0].split(' (')[0].strip('„“"')
                rows.append((f'{reg} · {co}' if co else reg, r[ai]))
        rows.sort(key=lambda x: -x[1])
        d.text((58, 238), 'EUR m', font=NB(24), fill=SOFT)
        hbars(d, rows, 58, 280, 700, 360, acc, lambda v: fnum(v, 0 if v >= 10 else 1), sym=False)
        k0 = b['kpi'][0] if b.get('kpi') else None
        if k0:
            u = L(k0.get('u'))
            unit = 'EUR bn' if 'Mrd' in u else 'EUR m' if 'Mio' in u else u
            d.text((800, 236), 'TOTAL  ' + unit, font=NB(28), fill=SOFT)
            d.text((796, 262), fnum(k0['v'], 1), font=NB(100), fill=WHITE)
        # Kran-Piktogramm
        cx, cy = 1030, 652
        d.rectangle([cx, cy - 190, cx + 14, cy], fill=acc)
        d.rectangle([cx - 60, cy - 190, cx + 130, cy - 178], fill=acc)
        d.line([(cx + 7, cy - 240), (cx - 55, cy - 184)], fill=acc, width=5)
        d.line([(cx + 7, cy - 240), (cx + 125, cy - 184)], fill=acc, width=5)
        d.line([(cx + 110, cy - 178), (cx + 110, cy - 120)], fill=acc, width=3)
        d.rectangle([cx + 96, cy - 120, cx + 124, cy - 100], fill=acc)
        for j in range(3):
            d.rectangle([cx + 40 + j * 36, cy - 60, cx + 70 + j * 36, cy], outline=acc, width=4)
    d.text((56, H - 40), 'Grafik / Graphic: TERRA WORLD NEWS', font=NR(20), fill=SOFT)
    return im, kind

def main():
    files = sorted(glob.glob(os.path.join(HERE, 'content', 'business', '*.json')))
    f = os.path.join(HERE, 'content', 'business', sys.argv[1] + '.json') if len(sys.argv) > 1 else files[-1]
    data = json.load(open(f, encoding='utf-8'))
    date = data['date']
    out = os.path.join(HERE, 'static', 'assets', 'news', date); os.makedirs(out, exist_ok=True)
    for b in data['blocks']:
        im, kind = render(b, date)
        fn = f'biz-{b["id"]}.webp'
        im.save(os.path.join(out, fn), 'WEBP', quality=86)
        dd = '.'.join(reversed(date.split('-')))
        a = ALT[kind]
        b['img'] = {'f': f'/assets/news/{date}/{fn}', 'w': W, 'h': H, 'own': True,
                    'alt': {'bg': f'{a[0]}, {dd} (собствена графика)', 'de': f'{a[1]}, {dd} (eigene Darstellung)', 'en': f'{a[2]}, {dd} (own graphic)'}}
        print('ok', fn)
    json.dump(data, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
