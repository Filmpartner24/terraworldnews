#!/usr/bin/env python3
"""TERRA WORLD NEWS – Besucherbericht als sauber gestaltetes PDF (Tag oder Woche).

Liest analytics/YYYY-MM-DD.json (von der GitHub Action aus Cloudflare Web Analytics geschrieben)
und content/*.json (für lesbare Artikeltitel und Rubriken) und erzeugt ein PDF.

  python3 tools/visitor_report.py daily  [--date 2026-10-03] [--notes notes.txt] [--out bericht.pdf]
  python3 tools/visitor_report.py weekly [--week-end 2026-10-04] [--notes notes.txt] [--out bericht.pdf]

daily:  Standarddatum = gestern (Europe/Berlin).
weekly: Standard = letzte volle Woche Montag–Sonntag.
--notes: Textdatei mit Einordnung/Beobachtungen (eine Zeile = ein Punkt), wird als eigener Abschnitt eingefügt.
Fehlende Tage werden im PDF ausdrücklich genannt; es werden keine Zahlen erfunden.
"""
import argparse, datetime as dt, glob, io, json, os, re, sys
from collections import Counter, defaultdict
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, KeepTogether)

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BERLIN = ZoneInfo('Europe/Berlin')
NAVY = colors.HexColor('#0f2f7a'); RED = colors.HexColor('#d4161c'); INK = colors.HexColor('#111827')
MUTED = colors.HexColor('#6b7280'); LINE = colors.HexColor('#e5e7eb'); ZEBRA = colors.HexColor('#f5f7fb')
GREEN = colors.HexColor('#0a7d5a')

# ---- Schrift (DejaVu für Umlaute/Kyrillisch, sonst Helvetica)
FONT, FONTB = 'Helvetica', 'Helvetica-Bold'
for reg, bold in [('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')]:
    if os.path.exists(reg) and os.path.exists(bold):
        pdfmetrics.registerFont(TTFont('DV', reg)); pdfmetrics.registerFont(TTFont('DVB', bold)); FONT, FONTB = 'DV', 'DVB'

ST = {
    'h1': ParagraphStyle('h1', fontName=FONTB, fontSize=20, leading=24, textColor=INK, spaceAfter=2),
    'sub': ParagraphStyle('sub', fontName=FONT, fontSize=10, leading=13, textColor=MUTED, spaceAfter=10),
    'h2': ParagraphStyle('h2', fontName=FONTB, fontSize=12.5, leading=16, textColor=NAVY, spaceBefore=12, spaceAfter=6),
    'p': ParagraphStyle('p', fontName=FONT, fontSize=9.5, leading=13, textColor=INK),
    'li': ParagraphStyle('li', fontName=FONT, fontSize=9.5, leading=13, textColor=INK, leftIndent=10, bulletIndent=0, spaceAfter=3),
    'small': ParagraphStyle('small', fontName=FONT, fontSize=8, leading=10.5, textColor=MUTED),
    'cell': ParagraphStyle('cell', fontName=FONT, fontSize=8.8, leading=11, textColor=INK),
    'kv': ParagraphStyle('kv', fontName=FONTB, fontSize=19, leading=22, textColor=NAVY, alignment=TA_CENTER),
    'kl': ParagraphStyle('kl', fontName=FONT, fontSize=8, leading=10, textColor=MUTED, alignment=TA_CENTER),
    'kd': ParagraphStyle('kd', fontName=FONTB, fontSize=9, leading=11, textColor=MUTED, alignment=TA_CENTER),
}
WD = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
MO = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
COUNTRIES = {'DE': 'Deutschland', 'BG': 'Bulgarien', 'US': 'USA', 'AT': 'Österreich', 'CH': 'Schweiz', 'GB': 'Großbritannien', 'FR': 'Frankreich',
             'NL': 'Niederlande', 'IT': 'Italien', 'ES': 'Spanien', 'GR': 'Griechenland', 'RO': 'Rumänien', 'TR': 'Türkei', 'RU': 'Russland',
             'UA': 'Ukraine', 'PL': 'Polen', 'SE': 'Schweden', 'IE': 'Irland', 'BE': 'Belgien', 'CZ': 'Tschechien', 'SG': 'Singapur', 'CN': 'China',
             'IN': 'Indien', 'JP': 'Japan', 'CA': 'Kanada', 'MK': 'Nordmazedonien', 'RS': 'Serbien', 'FI': 'Finnland', 'DK': 'Dänemark', 'NO': 'Norwegen',
             'HU': 'Ungarn', 'PT': 'Portugal', 'BR': 'Brasilien', 'AU': 'Australien', 'HK': 'Hongkong', 'IL': 'Israel', 'AE': 'VAE', 'CY': 'Zypern', 'XX': 'unbekannt'}
DEVICES = {'desktop': 'Desktop', 'mobile': 'Handy', 'tablet': 'Tablet', 'smarttv': 'Smart-TV'}
SEC_NAMES = {'welt': 'Welt', 'europa': 'Europa', 'deutschland': 'Deutschland', 'bulgarien': 'Bulgarien', 'leben': 'Leben & Alltag', 'ki': 'Technologie',
             'ai': 'KI', 'wirtschaft': 'Wirtschaft', 'energie': 'Energie', 'business': 'Business', 'klima': 'Klima', 'film': 'Film', 'musik': 'Musik',
             'games': 'Games', 'sport': 'Sport', 'kultur': 'Entertainment (alt)', 'usa': 'Welt'}
# Rubrik-Slugs aller Sprachen → Rubrik
SLUG2SEC = {'svyat': 'welt', 'welt': 'welt', 'world': 'welt', 'evropa': 'europa', 'europa': 'europa', 'europe': 'europa',
            'germania': 'deutschland', 'deutschland': 'deutschland', 'germany': 'deutschland', 'balgaria': 'bulgarien', 'bulgarien': 'bulgarien',
            'bulgaria': 'bulgarien', 'zhivot': 'leben', 'leben-alltag': 'leben', 'everyday-life': 'leben', 'tehnologii': 'ki', 'technologie': 'ki',
            'technology': 'ki', 'izkustven-intelekt': 'ai', 'ki': 'ai', 'ai': 'ai', 'ikonomika': 'wirtschaft', 'wirtschaft': 'wirtschaft', 'economy': 'wirtschaft',
            'energia': 'energie', 'energie': 'energie', 'energy': 'energie', 'biznes': 'business', 'business': 'business', 'klimat': 'klima', 'klima': 'klima',
            'climate': 'klima', 'filmi': 'film', 'film': 'film', 'muzika': 'musik', 'musik': 'musik', 'music': 'musik', 'igri': 'games', 'games': 'games',
            'sport': 'sport', 'razvlechenia': 'kultur', 'entertainment': 'kultur', 'kultura': 'kultur', 'kultur': 'kultur',
            'priroda': 'leben', 'natur': 'leben', 'nature': 'leben', 'inovatsii': 'ki', 'innovation': 'ki', 'sasht': 'welt', 'usa': 'welt'}


def de_date(d): return f'{WD[d.weekday()]}, {d.day}. {MO[d.month - 1]} {d.year}'
def fmt(n): return f'{n:,}'.replace(',', '.')
def f1(x): return f'{x:.1f}'.replace('.', ',')
def pct(a, b):
    if not b: return None
    return (a - b) / b * 100


def load_day(d):
    f = os.path.join(HERE, 'analytics', f'{d.isoformat()}.json')
    return json.load(open(f, encoding='utf-8')) if os.path.exists(f) else None


def load_articles():
    """id → (deutscher Titel, Rubrik) aus allen Content-Dateien."""
    m = {}
    for f in glob.glob(os.path.join(HERE, 'content', '*.json')):
        try: d = json.load(open(f, encoding='utf-8'))
        except Exception: continue
        its = d.get('items', []) if isinstance(d, dict) else d
        for it in its if isinstance(its, list) else []:
            if isinstance(it, dict) and it.get('id'):
                t = (it.get('de') or {}).get('t') or (it.get('bg') or {}).get('t') or it['id']
                m[it['id']] = (t, it.get('s', ''))
    return m


ART = None
def page_label(path):
    """Pfad → (lesbarer Name, Rubrik, Sprache)."""
    global ART
    if ART is None: ART = load_articles()
    p = path.split('?')[0]
    lang = 'DE' if p.startswith('/de/') else 'EN' if p.startswith('/en/') else 'BG'
    if p in ('/', '/de/', '/en/', '/index.html', '/de/index.html', '/en/index.html'):
        return f'Startseite {lang}', '', lang
    m = re.search(r'/(?:novini|nachrichten|news)/\d{4}/\d{2}/\d{2}/([^/]+?)(?:\.html)?$', p)
    if m:
        t, s = ART.get(m.group(1), (m.group(1).replace('-', ' ').capitalize(), ''))
        return t, SEC_NAMES.get(s, s), lang
    parts = [x for x in p.strip('/').split('/') if x and x not in ('de', 'en')]
    if parts and parts[0] in SLUG2SEC:
        name = SEC_NAMES[SLUG2SEC[parts[0]]]
        if len(parts) > 1: name += ' › ' + parts[1].replace('-', ' ').capitalize()
        return f'Rubrikseite {name}', SEC_NAMES[SLUG2SEC[parts[0]]], lang
    return p, '', lang


def merge(days, key):
    c = Counter(); cv = Counter()
    for d in days:
        for r in d.get(key, []) or []:
            k = r['k']
            if key == 'referers':
                kl = k.lower()
                if 'google.' in kl: k = 'Google'
                elif 'bing.' in kl: k = 'Bing'
                elif 'facebook.' in kl or kl.startswith('l.facebook') or kl.startswith('m.facebook'): k = 'Facebook'
                elif kl in ('t.co', 'x.com', 'twitter.com'): k = 'X / Twitter'
                elif 'terraworldnews' in kl: k = '(intern – Klick auf der eigenen Seite)'
                elif kl in ('(direkt)', '', 'direct', '(none)'): k = '(direkt / Lesezeichen)'
            c[k] += r.get('visits', 0); cv[k] += r.get('views', 0)
    return c, cv


# ---- Grafiken
def fig_png(fig):
    b = io.BytesIO(); fig.savefig(b, format='png', dpi=200, bbox_inches='tight'); plt.close(fig); b.seek(0); return b

def style_ax(ax):
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1'); ax.spines['bottom'].set_color('#cbd5e1')
    ax.tick_params(colors='#374151', labelsize=8); ax.grid(axis='y', color='#eef2f7', lw=.8); ax.set_axisbelow(True)

def chart_hours(day):
    hv = {int(r['k']): r.get('visits', 0) for r in day.get('hours', []) or []}
    xs = list(range(24)); ys = [hv.get(h, 0) for h in xs]
    fig, ax = plt.subplots(figsize=(7.2, 2.2)); style_ax(ax)
    best = max(ys) if ys else 0
    ax.bar(xs, ys, color=['#d4161c' if y == best and best else '#0f2f7a' for y in ys], width=.72)
    ax.set_xticks(range(0, 24, 2)); ax.set_xticklabels([f'{h:02d}' for h in range(0, 24, 2)])
    ax.set_ylabel('Besuche', fontsize=8, color='#374151'); ax.set_xlabel('Stunde (Uhrzeit laut Cloudflare)', fontsize=8, color='#374151')
    return fig_png(fig)

def chart_week(cur_days, prev_days, labels):
    fig, ax = plt.subplots(figsize=(7.2, 2.6)); style_ax(ax)
    cv = [d['visits'] if d else None for d in cur_days]; pv = [d['visits'] if d else None for d in prev_days]
    ax.plot(labels, [v if v is not None else float('nan') for v in pv], color='#94a3b8', lw=2, marker='o', ms=4, label='Vorwoche')
    ax.plot(labels, [v if v is not None else float('nan') for v in cv], color='#0f2f7a', lw=2.6, marker='o', ms=5, label='Diese Woche')
    for x, v in zip(labels, cv):
        if v is not None: ax.annotate(fmt(v), (x, v), textcoords='offset points', xytext=(0, 6), ha='center', fontsize=7.5, color='#0f2f7a')
    ax.set_ylabel('Besuche', fontsize=8, color='#374151'); ax.legend(frameon=False, fontsize=8, loc='upper left')
    return fig_png(fig)

def chart_bars(items, title_color='#0f2f7a'):
    items = items[:8][::-1]
    fig, ax = plt.subplots(figsize=(7.2, .32 * len(items) + .5)); style_ax(ax); ax.grid(axis='x', color='#eef2f7'); ax.grid(axis='y', visible=False)
    ax.barh([k for k, _ in items], [v for _, v in items], color=title_color, height=.6)
    for i, (_, v) in enumerate(items): ax.text(v, i, f'  {fmt(v)}', va='center', fontsize=7.5, color='#374151')
    ax.set_xlabel('Seitenaufrufe', fontsize=8, color='#374151')
    return fig_png(fig)


# ---- PDF-Bausteine
def kpi_row(items):
    data = [[Paragraph(v, ST['kv']) for v, _, _ in items], [Paragraph(l, ST['kl']) for _, l, _ in items], [Paragraph(dd or '&nbsp;', ST['kd']) for _, _, dd in items]]
    w = 180 * mm / len(items)
    t = Table(data, colWidths=[w] * len(items))
    t.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), .6, LINE), ('INNERGRID', (0, 0), (-1, -1), 0, colors.white), ('LINEBEFORE', (1, 0), (-1, -1), .6, LINE),
                           ('LINEABOVE', (0, 0), (-1, 0), 3, NAVY), ('TOPPADDING', (0, 0), (-1, 0), 9), ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
                           ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fbfcfe'))]))
    return t

def delta_txt(p, label):
    if p is None: return f'<font color="#6b7280">{label}: –</font>'
    c = '#0a7d5a' if p >= 0 else '#d4161c'; arrow = '▲' if p >= 0 else '▼'
    return f'<font color="{c}">{arrow} {p:+.0f} %</font> <font color="#6b7280">{label}</font>'

def table(head, rows, widths, num_cols=()):
    data = [[Paragraph(f'<font color="white"><b>{h}</b></font>', ST['cell']) for h in head]] + [[Paragraph(str(c), ST['cell']) for c in r] for r in rows]
    sty = [('BACKGROUND', (0, 0), (-1, 0), NAVY), ('LINEBELOW', (0, 0), (-1, -1), .4, LINE),
           ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]
    sty += [('BACKGROUND', (0, i), (-1, i), ZEBRA) for i in range(2, len(data), 2)]
    t = Table(data, colWidths=widths, repeatRows=1); t.setStyle(TableStyle(sty))
    return t

def share(c, total):
    return f'{(c / total * 100):.0f} %' if total else '–'

def notes_flow(notes_path):
    out = []
    if notes_path and os.path.exists(notes_path):
        lines = [x.strip().lstrip('-•* ').strip() for x in open(notes_path, encoding='utf-8') if x.strip()]
        if lines:
            out.append(Paragraph('Einordnung', ST['h2']))
            out += [Paragraph(x, ST['li'], bulletText='•') for x in lines]
    return out


class Doc(BaseDocTemplate):
    def __init__(self, path, title):
        super().__init__(path, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=34 * mm, bottomMargin=18 * mm,
                         title=title, author='TERRA WORLD NEWS', subject='Besucherbericht terraworldnews.com')
        self.rtitle = title
        fr = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id='f')
        self.addPageTemplates([PageTemplate(id='p', frames=[fr], onPage=self.deco)])

    def deco(self, c, doc):
        W, H = A4
        c.saveState()
        c.setFillColor(NAVY); c.rect(0, H - 24 * mm, W, 24 * mm, stroke=0, fill=1)
        c.setFillColor(RED); c.rect(0, H - 25.2 * mm, W, 1.2 * mm, stroke=0, fill=1)
        logo = os.path.join(HERE, 'tools', 'report-icon.png')
        if os.path.exists(logo): c.drawImage(logo, 15 * mm, H - 20.5 * mm, 17 * mm, 17 * mm, mask='auto')
        c.setFillColor(colors.white); c.setFont(FONTB, 15); c.drawString(36 * mm, H - 12 * mm, 'TERRA WORLD NEWS')
        c.setFont(FONT, 9); c.drawString(36 * mm, H - 17.5 * mm, 'Besucherbericht · terraworldnews.com')
        c.setFont(FONTB, 8); c.drawRightString(W - 15 * mm, H - 12 * mm, 'NEWS · FACTS · CONTEXT')
        c.setFont(FONT, 8); c.drawRightString(W - 15 * mm, H - 17.5 * mm, self.rtitle)
        c.setStrokeColor(LINE); c.line(15 * mm, 12 * mm, W - 15 * mm, 12 * mm)
        c.setFillColor(MUTED); c.setFont(FONT, 7.5)
        c.drawString(15 * mm, 8 * mm, 'Quelle: Cloudflare Web Analytics (cookielos). Richtwerte – Nutzer mit Werbeblockern werden teils nicht gezählt.')
        c.drawRightString(W - 15 * mm, 8 * mm, f'Seite {doc.page}')
        c.restoreState()


def common_sections(days, total_visits, total_views, top_pages_n):
    out = []
    lc, lv = merge(days, 'countries')
    out.append(Paragraph('Herkunft der Besucher – Top 10 Länder', ST['h2']))
    rows = [[i + 1, COUNTRIES.get(k, k), fmt(v), share(v, total_visits), fmt(lv[k])] for i, (k, v) in enumerate(lc.most_common(10))]
    out.append(table(['#', 'Land', 'Besuche', 'Anteil', 'Aufrufe'], rows or [['–', 'keine Daten', '', '', '']], [10 * mm, 70 * mm, 30 * mm, 30 * mm, 40 * mm], (2, 3, 4)))

    rc, rv = merge(days, 'referers')
    out.append(Paragraph('Woher kommen die Besuche? – Verweisquellen', ST['h2']))
    rows = [[k, fmt(v), fmt(rv[k])] for k, v in rc.most_common(10)]
    out.append(table(['Quelle', 'Besuche', 'Aufrufe'], rows or [['keine Daten', '', '']], [110 * mm, 35 * mm, 35 * mm], (1, 2)))
    out.append(Spacer(1, 2)); out.append(Paragraph('„intern“ = Klicks von einer TWN-Seite auf die nächste (zählt als Seitenaufruf, nicht als neuer Besuch).', ST['small']))

    lang = Counter()
    for d in days:
        for k, v in (d.get('lang_views') or {}).items(): lang[k.upper()] += v
    dc, dv = merge(days, 'devices')
    tl = sum(lang.values()); td = sum(dc.values())
    left = table(['Sprache', 'Aufrufe', 'Anteil'], [[k, fmt(lang[k]), share(lang[k], tl)] for k in ('BG', 'DE', 'EN')], [30 * mm, 28 * mm, 26 * mm], (1, 2))
    right = table(['Gerät', 'Besuche', 'Anteil'], [[DEVICES.get(k, k), fmt(v), share(v, td)] for k, v in dc.most_common()] or [['–', '', '']], [30 * mm, 28 * mm, 26 * mm], (1, 2))
    two = Table([[Paragraph('Sprachen', ST['h2']), Paragraph('Geräte', ST['h2'])], [left, right]], colWidths=[90 * mm, 90 * mm])
    two.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0)]))
    out.append(KeepTogether([two]))

    pc, pv = merge(days, 'paths')
    out.append(Paragraph(f'Meistgelesene Seiten – Top {top_pages_n}', ST['h2']))
    rows = []
    for i, (k, v) in enumerate(sorted(pv.items(), key=lambda x: -x[1])[:top_pages_n]):
        name, sec, lg = page_label(k)
        rows.append([i + 1, name, sec, lg, fmt(v)])
    out.append(table(['#', 'Seite / Artikel', 'Rubrik', 'Spr.', 'Aufrufe'], rows or [['–', 'keine Daten', '', '', '']],
                     [9 * mm, 104 * mm, 30 * mm, 12 * mm, 25 * mm], (4,)))
    # Rubriken
    secv = Counter()
    for k, v in pv.items():
        _, sec, _ = page_label(k)
        if sec: secv[sec] += v
    if secv:
        out.append(KeepTogether([Paragraph('Rubriken nach Seitenaufrufen', ST['h2']),
                                 Image(chart_bars(secv.most_common(), '#0f2f7a'), width=180 * mm, height=(.32 * min(8, len(secv)) + .5) * 180 * mm / 7.2)]))
    return out


def daily(args):
    today = dt.datetime.now(BERLIN).date()
    d = dt.date.fromisoformat(args.date) if args.date else today - dt.timedelta(days=1)
    day = load_day(d); prev = load_day(d - dt.timedelta(days=1)); wk = load_day(d - dt.timedelta(days=7))
    title = f'Tagesbericht {d.strftime("%d.%m.%Y")}'
    out = args.out or os.path.join(HERE, f'TWN-Tagesbericht-{d.isoformat()}.pdf')
    doc = Doc(out, title); s = []
    s.append(Paragraph(f'Tagesbericht Besucher – {de_date(d)}', ST['h1']))
    if not day:
        s.append(Paragraph('Für diesen Tag liegen noch keine Analysedaten vor (Datei analytics/' + d.isoformat() + '.json fehlt). '
                           'Es werden keine Zahlen geschätzt.', ST['p']))
        s += notes_flow(args.notes); doc.build(s); print(out); return
    s.append(Paragraph(f'Datenstand: {day.get("fetched", "–")} · Vergleich mit Vortag und gleichem Wochentag der Vorwoche', ST['sub']))
    s.append(kpi_row([(fmt(day['visits']), 'Besuche', delta_txt(pct(day['visits'], prev and prev['visits']), 'zum Vortag')),
                      (fmt(day['views']), 'Seitenaufrufe', delta_txt(pct(day['views'], prev and prev['views']), 'zum Vortag')),
                      (f1(day["views"] / day["visits"]) if day['visits'] else '–', 'Seiten pro Besuch', ''),
                      (fmt(wk['visits']) if wk else '–', f'Besuche {WD[(d - dt.timedelta(days=7)).weekday()][:2]}. Vorwoche',
                       delta_txt(pct(day['visits'], wk and wk['visits']), 'Veränderung'))]))
    s += notes_flow(args.notes)
    if day.get('hours'):
        hv = sorted(day['hours'], key=lambda r: -r.get('visits', 0))[0]
        s.append(Paragraph(f'Besuche nach Uhrzeit · stärkste Stunde: {hv["k"]}:00 Uhr ({fmt(hv.get("visits", 0))} Besuche)', ST['h2']))
        s.append(Image(chart_hours(day), width=180 * mm, height=55 * mm))
    s += common_sections([day], day['visits'], day['views'], 10)
    doc.build(s); print(out)


def weekly(args):
    today = dt.datetime.now(BERLIN).date()
    end = dt.date.fromisoformat(args.week_end) if args.week_end else today - dt.timedelta(days=today.weekday() + 1)  # letzter Sonntag
    start = end - dt.timedelta(days=6)
    cur = [load_day(start + dt.timedelta(days=i)) for i in range(7)]
    prev = [load_day(start - dt.timedelta(days=7 - i)) for i in range(7)]
    have = [x for x in cur if x]; haveP = [x for x in prev if x]
    title = f'Wochenbericht {start.strftime("%d.%m.")}–{end.strftime("%d.%m.%Y")}'
    out = args.out or os.path.join(HERE, f'TWN-Wochenbericht-{start.isoformat()}_{end.isoformat()}.pdf')
    doc = Doc(out, title); s = []
    s.append(Paragraph(f'Wochenbericht Besucher – {start.day}. {MO[start.month - 1]} bis {de_date(end)}', ST['h1']))
    missing = [(start + dt.timedelta(days=i)).strftime('%d.%m.') for i, x in enumerate(cur) if not x]
    s.append(Paragraph('Vergleich mit der Vorwoche' + (f' · <font color="#d4161c">Fehlende Tage: {", ".join(missing)}</font>' if missing else ' · alle 7 Tage vorhanden'), ST['sub']))
    tv = sum(x['visits'] for x in have); tw = sum(x['views'] for x in have)
    pv = sum(x['visits'] for x in haveP); pw = sum(x['views'] for x in haveP)
    s.append(kpi_row([(fmt(tv), 'Besuche (Woche)', delta_txt(pct(tv, pv), 'zur Vorwoche')),
                      (fmt(tw), 'Seitenaufrufe (Woche)', delta_txt(pct(tw, pw), 'zur Vorwoche')),
                      (fmt(round(tv / len(have))) if have else '–', 'Ø Besuche pro Tag', ''),
                      (f1(tw / tv) if tv else '–', 'Seiten pro Besuch', '')]))
    s += notes_flow(args.notes)
    labels = [f'{WD[(start + dt.timedelta(days=i)).weekday()][:2]} {(start + dt.timedelta(days=i)).strftime("%d.%m.")}' for i in range(7)]
    s.append(Paragraph('Besuche pro Tag – diese Woche und Vorwoche', ST['h2']))
    s.append(Image(chart_week(cur, prev, labels), width=180 * mm, height=65 * mm))
    rows = []
    vals = [(x['visits'] if x else None) for x in cur]
    best = max([v for v in vals if v is not None], default=None); worst = min([v for v in vals if v is not None], default=None)
    for i, x in enumerate(cur):
        dd = start + dt.timedelta(days=i); p = prev[i]
        mark = ' <font color="#0a7d5a">(bester Tag)</font>' if x and x['visits'] == best and best else (' <font color="#d4161c">(schwächster Tag)</font>' if x and x['visits'] == worst and best != worst and vals.count(worst) == 1 else '')
        rows.append([f'{WD[dd.weekday()]}, {dd.strftime("%d.%m.")}{mark}', fmt(x['visits']) if x else 'fehlt', fmt(x['views']) if x else 'fehlt',
                     fmt(p['visits']) if p else '–'])
    rows.append(['<b>Summe</b>', f'<b>{fmt(tv)}</b>', f'<b>{fmt(tw)}</b>', f'<b>{fmt(pv)}</b>'])
    s.append(Paragraph('Tag für Tag', ST['h2']))
    s.append(table(['Tag', 'Besuche', 'Aufrufe', 'Besuche Vorwoche'], rows, [80 * mm, 30 * mm, 30 * mm, 40 * mm], (1, 2, 3)))
    s += common_sections(have, tv, tw, 15)
    doc.build(s); print(out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['daily', 'weekly'])
    ap.add_argument('--date'); ap.add_argument('--week-end'); ap.add_argument('--notes'); ap.add_argument('--out')
    a = ap.parse_args()
    (daily if a.mode == 'daily' else weekly)(a)
