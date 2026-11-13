#!/usr/bin/env python3
"""Tagesbericht TERRA WORLD NEWS als PDF (Nedy 13.11.2026).

Aufruf: python3 tools/report_pdf.py YYYY-MM-DD [ausgabe.pdf]
Liest analytics/YYYY-MM-DD.json (+ die 6 Vortage für den Verlauf) und content/*.json für Artikeltitel.
Bot-Verdacht: ein Land mit >= 40 % aller Aufrufe, das nicht zu den Kernmärkten gehört,
fast nur Direktaufrufe ohne Herkunftsseite und gleichmäßig über den Tag verteilt (Rechenzentrum).
"""
import glob, json, os, re, sys, datetime as dt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = '/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('DV', F + 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DVB', F + 'DejaVuSans-Bold.ttf'))
RED = colors.HexColor('#C8102E'); GREY = colors.HexColor('#666666'); LIGHT = colors.HexColor('#F3F3F3')
CORE = {'BG', 'DE', 'AT', 'CH'}
LAND = {'BG': 'Bulgarien', 'DE': 'Deutschland', 'AT': 'Österreich', 'CH': 'Schweiz', 'US': 'USA', 'SG': 'Singapur', 'GB': 'Großbritannien',
        'FR': 'Frankreich', 'NL': 'Niederlande', 'RO': 'Rumänien', 'TR': 'Türkei', 'GR': 'Griechenland', 'IT': 'Italien', 'ES': 'Spanien',
        'PL': 'Polen', 'BR': 'Brasilien', 'CN': 'China', 'IN': 'Indien', 'CO': 'Kolumbien', 'ID': 'Indonesien', 'NG': 'Nigeria', 'MX': 'Mexiko',
        'PK': 'Pakistan', 'VE': 'Venezuela', 'TN': 'Tunesien', 'IE': 'Irland', 'CA': 'Kanada', 'JP': 'Japan', 'RU': 'Russland', 'UA': 'Ukraine',
        'HK': 'Hongkong', 'FI': 'Finnland', 'SE': 'Schweden', 'BE': 'Belgien', 'CZ': 'Tschechien'}

def load(d):
    p = os.path.join(HERE, 'analytics', f'{d}.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None

def realv(a):
    bk = {c['k'] for c in bots(a)}
    return sum(c['views'] for c in a.get('countries', []) if c['k'] not in bk)

def bots(a):
    tot = max(a.get('views') or 0, sum(c['views'] for c in a.get('countries', [])))
    out = []
    for c in a.get('countries', []):
        if tot and c['views'] >= 0.4 * tot and c['k'] not in CORE:
            out.append(c)
    return out

def titles():
    t = {}
    for f in glob.glob(os.path.join(HERE, 'content', '*.json')):
        try: d = json.load(open(f, encoding='utf-8'))
        except Exception: continue
        for it in (d.get('items') if isinstance(d, dict) else None) or []:
            if isinstance(it, dict) and it.get('id'):
                t[it['id']] = (it.get('de') or {}).get('t') or it['id']
    return t

def page_name(path, T):
    if path in ('/', '/de/', '/en/'): return {'/': 'Startseite (BG)', '/de/': 'Startseite (DE)', '/en/': 'Startseite (EN)'}[path]
    m = re.search(r'/news/\d{4}/\d\d/\d\d/([^/?#.;]+)', path)
    if m:
        slug = m.group(1)
        for k, v in T.items():
            if slug == k or slug.startswith(k) or k.startswith(slug):
                return v
        return slug.replace('-', ' ')
    return 'Rubrik: ' + path.strip('/').replace('/', ' › ')

def main():
    day = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, f'bericht-{day}.pdf')
    a = load(day)
    if not a: sys.exit(f'keine Daten für {day}')
    B = bots(a); bot_v = sum(c['views'] for c in B)
    real = realv(a)
    T = titles()
    d0 = dt.date.fromisoformat(day)
    hist = []
    for i in range(6, -1, -1):
        d = (d0 - dt.timedelta(days=i)).isoformat(); x = load(d)
        if x: hist.append((d[8:10] + '.' + d[5:7], x.get('views') or 0, realv(x)))
    # Diagramm
    fig, ax = plt.subplots(figsize=(7, 2.6), dpi=200)
    xs = [h[0] for h in hist]
    ax.bar(xs, [h[1] for h in hist], color='#DDDDDD', label='alle Aufrufe')
    ax.bar(xs, [h[2] for h in hist], color='#C8102E', label='bereinigt (ohne Bot-Verdacht)')
    for i, h in enumerate(hist): ax.text(i, h[2], str(h[2]), ha='center', va='bottom', fontsize=7)
    ax.spines[['top', 'right']].set_visible(False); ax.legend(fontsize=7, frameon=False); ax.tick_params(labelsize=7)
    fig.tight_layout(); png = out.replace('.pdf', '.png'); fig.savefig(png); plt.close(fig)

    st = lambda n, s=9, c=colors.black, b=False: ParagraphStyle(n, fontName='DVB' if b else 'DV', fontSize=s, leading=s * 1.35, textColor=c)
    H1, H2, P, S = st('h1', 18, RED, True), st('h2', 11.5, colors.black, True), st('p', 9), st('s', 7.5, GREY)
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=14 * mm, bottomMargin=14 * mm,
                            title=f'TWN Tagesbericht {day}', author='TERRA WORLD NEWS')
    el = [Paragraph('TERRA WORLD NEWS – Tagesbericht', H1),
          Paragraph(f'Besucher und Klicks vom {d0.strftime("%d.%m.%Y")} · Quelle: Cloudflare Web Analytics (cookielos)', S), Spacer(1, 6)]
    kpi = [['Seitenaufrufe gesamt', 'davon Bot-Verdacht', 'Bereinigte Aufrufe', 'über Google'],
           [f"{a.get('views', 0):,}".replace(',', '.'), f"{bot_v:,}".replace(',', '.'), f"{real:,}".replace(',', '.'),
            str(next((r['views'] for r in a.get('referers', []) if 'google' in r['k']), 0))]]
    t = Table(kpi, colWidths=[44 * mm] * 4)
    t.setStyle(TableStyle([('FONT', (0, 0), (-1, 0), 'DV', 8), ('TEXTCOLOR', (0, 0), (-1, 0), GREY), ('FONT', (0, 1), (-1, 1), 'DVB', 17),
                           ('TEXTCOLOR', (2, 1), (2, 1), RED), ('BACKGROUND', (0, 0), (-1, -1), LIGHT), ('BOX', (0, 0), (-1, -1), 0.3, colors.white),
                           ('INNERGRID', (0, 0), (-1, -1), 2, colors.white), ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
    el += [t, Spacer(1, 6)]
    if B:
        names = ', '.join(f"{LAND.get(c['k'], c['k'])} ({c['views']})" for c in B)
        el.append(Paragraph(f'<b>Bot-Verdacht:</b> {names} – ein einzelnes Land außerhalb der Kernmärkte mit über 40 % aller Aufrufe, fast nur Direktaufrufe ohne Herkunftsseite. '
                            'Typisch für automatische Abrufe aus einem Rechenzentrum, nicht für echte Leser. Diese Aufrufe sind in der bereinigten Zahl nicht enthalten.', P))
    el += [Spacer(1, 8), Paragraph('Verlauf der letzten 7 Tage', H2), Image(png, width=178 * mm, height=66 * mm), Spacer(1, 6)]

    def table(title, rows, head):
        el.append(Paragraph(title, H2))
        tb = Table([head] + rows, colWidths=[118 * mm, 30 * mm, 30 * mm][:len(head)] if len(head) == 3 else [148 * mm, 30 * mm], repeatRows=1)
        tb.setStyle(TableStyle([('FONT', (0, 0), (-1, 0), 'DVB', 8), ('FONT', (0, 1), (-1, -1), 'DV', 8), ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                                ('LINEBELOW', (0, 0), (-1, 0), 0.6, RED), ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
                                ('TOPPADDING', (0, 0), (-1, -1), 2.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5)]))
        el.extend([tb, Spacer(1, 8)])

    bk = {c['k'] for c in B}
    table('Länder (ohne Bot-Verdacht)', [[LAND.get(c['k'], c['k']), str(c['views'])] for c in sorted(a.get('countries', []), key=lambda c: -c['views']) if c['k'] not in bk][:10], ['Land', 'Aufrufe'])
    lv = a.get('lang_views') or {}
    if lv: table('Aufrufe nach Sprache', [[{'bg': 'Bulgarisch', 'de': 'Deutsch', 'en': 'Englisch'}.get(k, k), str(v)] for k, v in sorted(lv.items(), key=lambda x: -x[1])], ['Sprache', 'Aufrufe'])
    pages = [p for p in a.get('paths', []) if p['views'] > 0][:12]
    table('Meistgelesene Seiten und Artikel', [[Paragraph(page_name(p['k'], T)[:110], st('c', 8)), str(p['views'])] for p in pages], ['Seite / Artikel', 'Aufrufe'])
    table('Woher kommen die Leser?', [[('Direkt / Lesezeichen / Apps' if r['k'] == '(direkt)' else r['k']), str(r['views'])] for r in a.get('referers', []) if r['k'] != 'terraworldnews.com'][:8], ['Herkunft', 'Aufrufe'])
    dev = {d['k']: d['views'] for d in a.get('devices', [])}
    el.append(Paragraph(f"Geräte: Desktop {dev.get('desktop', 0)} · Smartphone {dev.get('mobile', 0)} · Tablet {dev.get('tablet', 0)}", P))
    el += [Spacer(1, 10), Paragraph('Hinweis: Web Analytics zählt Seitenaufrufe in Browsern ohne Cookies. Die „Unique visitors“ in der Cloudflare-Domainübersicht zählen dagegen jede IP-Adresse '
                                    'einschließlich Suchmaschinen und Bots und liegen deshalb um ein Vielfaches höher. „Bereinigt“ ist eine Schätzung.', S)]
    doc.build(el); os.remove(png); print(out, real)

if __name__ == '__main__':
    main()
