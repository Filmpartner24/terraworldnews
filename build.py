#!/usr/bin/env python3
"""TERRA WORLD NEWS – static site generator.
Usage: python3 build.py   → writes ./out
Content: content/YYYY-MM-DD.json (one file per daily edition)."""
import json, os, glob, shutil, html, datetime
from email.utils import format_datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
SITE = 'https://terraworldnews.com'
TZ = '+02:00'  # editorial times are Berlin time (CEST); adjust for winter time
e = html.escape
CUR_T = ' aria-current="true"'
CUR_P = ' aria-current="page"'

# All planned languages (order = language bar). Only languages with content are built.
LANGS = [('bg', 'Български'), ('de', 'Deutsch'), ('en', 'English'), ('es', 'Español'), ('pt', 'Português'), ('fr', 'Français'),
         ('it', 'Italiano'), ('ro', 'Română'), ('tr', 'Türkçe'), ('ru', 'Русский'), ('uk', 'Українська'), ('ar', 'العربية'),
         ('zh', '中文'), ('hi', 'हिन्दी'), ('ja', '日本語'), ('el', 'Ελληνικά'), ('sr', 'Српски')]
PREFIX = {'bg': '/'}  # Bulgarian is the main edition at the root
def pre(l): return PREFIX.get(l, f'/{l}/')
LOCALE = {'bg': 'bg_BG', 'de': 'de_DE', 'en': 'en_GB'}

SECTIONS = ['welt', 'europa', 'deutschland', 'bulgarien', 'leben', 'ki', 'wirtschaft', 'klima', 'kultur']
SEC = {
 'bg': {'welt': ('Свят', 'svyat'), 'europa': ('Европа', 'evropa'), 'deutschland': ('Германия', 'germania'), 'bulgarien': ('България', 'balgaria'), 'ki': ('Технологии', 'tehnologii'), 'wirtschaft': ('Икономика', 'ikonomika'), 'klima': ('Климат и енергия', 'klimat'), 'kultur': ('Развлечения', 'razvlechenia'), 'leben': ('Живот и ежедневие', 'zhivot')},
 'de': {'welt': ('Welt', 'welt'), 'europa': ('Europa', 'europa'), 'deutschland': ('Deutschland', 'deutschland'), 'bulgarien': ('Bulgarien', 'bulgarien'), 'ki': ('Technologie', 'technologie'), 'wirtschaft': ('Wirtschaft', 'wirtschaft'), 'klima': ('Klima & Energie', 'klima'), 'kultur': ('Entertainment', 'entertainment'), 'leben': ('Leben & Alltag', 'leben-alltag')},
 'en': {'welt': ('World', 'world'), 'europa': ('Europe', 'europe'), 'deutschland': ('Germany', 'germany'), 'bulgarien': ('Bulgaria', 'bulgaria'), 'ki': ('Technology', 'technology'), 'wirtschaft': ('Business', 'business'), 'klima': ('Climate & Energy', 'climate'), 'kultur': ('Entertainment', 'entertainment'), 'leben': ('Everyday Life', 'everyday-life')},
}
SEC_COLOR = {'welt': 'var(--cobalt)', 'europa': '#5b3fc4', 'deutschland': 'var(--muted)', 'bulgarien': 'var(--teal)', 'usa': '#b23a48', 'ki': '#0f7c9c', 'wirtschaft': 'var(--sand)', 'klima': '#2f8a4a', 'kultur': 'var(--signal)', 'leben': '#c26a00'}
NEWS_DIR = {'bg': 'novini', 'de': 'nachrichten', 'en': 'news'}
WEEKDAYS = {'bg': ['понеделник', 'вторник', 'сряда', 'четвъртък', 'петък', 'събота', 'неделя'], 'de': ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'], 'en': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
MONTHS = {'bg': ['януари', 'февруари', 'март', 'април', 'май', 'юни', 'юли', 'август', 'септември', 'октомври', 'ноември', 'декември'], 'de': ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'], 'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']}

UI = {
 'bg': dict(home='Начало', tagline='Новини от целия свят', ed='Брой {n} · Година I', places='София · Берлин · Светът', clocks=[('Берлин', 'Europe/Berlin'), ('София', 'Europe/Sofia'), ('Лондон', 'Europe/London'), ('Ню Йорк', 'America/New_York'), ('Пекин', 'Asia/Shanghai')],
   brk='Извънредно', brkup='Update', vid='Видео', playv='▶ Пусни видеото', trl='Трейлъри на деня', mvd='Музикални видеа на деня', tours='Турнета и концерти', lead='Водеща новина', most='Последни новини', all='Всички новини →', src='Източници', by='Редакция TERRA', read='Четене {m} мин.', hour='ч.', items='новини', facts='Най-важното', more='Още от рубриката', trailer='Трейлър', play='▶ Пусни трейлъра', ytnote='При пускане видеото се зарежда от YouTube (Google).', empty='В тази рубрика скоро ще излизат материали на редакцията.',
   foot='Terra World News (TWN) – независим новинарски портал с новини от целия свят · Редакция София и Берлин', about='За нас', publisher='Издател: FILMPARTNER 24 EOOD', imprint='Импресум', privacy='Поверителност', principles='Редакционни принципи', rss='RSS', back='Към началото',
   desc_home='TWN – World News (Terra World News): новини от целия свят, от България, Германия и Европа. Всеки ден, проверени и с посочени източници.', title_home='TWN – World News | Terra World News – Новини от целия свят', live='НА ЖИВО', lang='Език'),
 'de': dict(home='Start', tagline='Nachrichten aus aller Welt', ed='Ausgabe {n} · Jahrgang I', places='Sofia · Berlin · Die Welt', clocks=[('Berlin', 'Europe/Berlin'), ('Sofia', 'Europe/Sofia'), ('London', 'Europe/London'), ('New York', 'America/New_York'), ('Peking', 'Asia/Shanghai')],
   brk='Breaking News', brkup='Update', vid='Video', playv='▶ Video abspielen', trl='Trailer des Tages', mvd='Musikvideos des Tages', tours='Tourneen & Konzerte', lead='Aufmacher', most='Neueste Meldungen', all='Alle Meldungen →', src='Quellen', by='TERRA-Redaktion', read='Lesezeit {m} Min.', hour='Uhr', items='Meldungen', facts='Das Wichtigste', more='Mehr aus dem Ressort', trailer='Trailer', play='▶ Trailer abspielen', ytnote='Beim Abspielen wird das Video von YouTube (Google) geladen.', empty='In diesem Ressort erscheinen in Kürze Meldungen der Redaktion.',
   foot='Terra World News (TWN) – unabhängiges Nachrichtenportal mit Nachrichten aus aller Welt · Redaktion Sofia & Berlin', about='Über uns', publisher='Herausgeber: FILMPARTNER 24 EOOD', imprint='Impressum', privacy='Datenschutz', principles='Redaktionsgrundsätze', rss='RSS', back='Zur Startseite',
   desc_home='TWN – World News (Terra World News): Nachrichten aus aller Welt, aus Deutschland, Bulgarien und Europa. Täglich, geprüft und mit Quellenangaben.', title_home='TWN – World News | Terra World News – Nachrichten aus aller Welt', live='LIVE', lang='Sprache'),
 'en': dict(home='Home', tagline='News from around the world', ed='Issue {n}', places='', clocks=[('Berlin', 'Europe/Berlin'), ('Sofia', 'Europe/Sofia'), ('London', 'Europe/London'), ('New York', 'America/New_York'), ('Beijing', 'Asia/Shanghai')],
   brk='Breaking News', brkup='Update', vid='Video', playv='▶ Play video', trl='Trailers of the day', mvd='Music videos of the day', tours='Tours & concerts', lead='Top story', most='Latest news', all='All news →', src='Sources', by='TWN newsroom', read='{m} min read', hour='', items='stories', facts='Key points', more='More from this section', trailer='Trailer', play='▶ Play trailer', ytnote='Playing the video loads it from YouTube (Google).', empty='Stories from our newsroom will appear in this section soon.',
   foot='Terra World News (TWN) – an independent news portal with news from around the world · Newsrooms in Sofia & Berlin', about='About us', publisher='Publisher: FILMPARTNER 24 EOOD', imprint='Imprint', privacy='Privacy', principles='Editorial principles', rss='RSS', back='Back to home',
   desc_home='TWN – World News (Terra World News): news from around the world, from Europe, Germany, Bulgaria and the USA. Daily, fact-checked and with sources.', title_home='TWN – World News | Terra World News – News from around the world', live='LIVE', lang='Language'),
}
LEGAL_SLUG = {'bg': {'about': 'za-nas', 'imprint': 'impresum', 'privacy': 'poveritelnost', 'principles': 'redaktsionni-printsipi'}, 'de': {'about': 'ueber-uns', 'imprint': 'impressum', 'privacy': 'datenschutz', 'principles': 'redaktionsgrundsaetze'}, 'en': {'about': 'about', 'imprint': 'imprint', 'privacy': 'privacy', 'principles': 'editorial-principles'}}

def load():
    eds, brk = [], []
    for f in sorted(glob.glob(os.path.join(HERE, 'content', '*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        for it in d['items']:
            it['date'] = d['date']
            if it.get('s') == 'usa': it['s'] = 'welt'  # USA-Meldungen laufen unter Welt
            if it.get('img') and not it['img']['f'].startswith('/'): it['img']['f'] = '/' + it['img']['f']  # Pfad immer absolut
            if it.get('img') and not os.path.exists(os.path.join(HERE, 'static', it['img']['f'].lstrip('/'))):
                it.pop('img')  # Foto noch nicht geladen (kommt mit dem nächsten Action-Lauf) -> Platzhalter statt grauer Fläche
            for _l in ('bg', 'de', 'en'):
                _b = it.get(_l, {}).get('body') if isinstance(it.get(_l), dict) else None
                if isinstance(_b, str):  # Text als ein Block geliefert -> in Absätze teilen
                    it[_l]['body'] = [p.strip() for p in _b.replace('\r', '').split('\n') if p.strip()]
        if os.path.basename(f)[10:11] == '-':   # YYYY-MM-DD-<zusatz>.json: Breaking News, Leben & Alltag …
            for it in d['items']:
                it.pop('lead', None)
                if f.endswith('-breaking.json'): it['brk'] = True
            brk.append(d)
        else:
            eds.append(d)
    # Breaking-News-Updates (content/YYYY-MM-DD-breaking.json) gehören zur Ausgabe desselben Tages
    for b in brk:
        ed = next((x for x in eds if x['date'] == b['date']), None)
        if ed is None:
            ed = {'date': b['date'], 'issue': (eds[-1].get('issue', 0) + 1) if eds else 1, 'items': []}
            eds.append(ed); eds.sort(key=lambda x: x['date'])
        ids = {it['id'] for it in ed['items']}
        ed['items'] += [it for it in b['items'] if it['id'] not in ids]
    # Nur das jeweils neueste Breaking-News-Update ist "live" (roter Block, Badge, Laufband vorn);
    # frühere Updates rutschen als normale Meldungen in "Neueste Meldungen", Ressorts und Laufband.
    allb = [it for d in eds for it in d['items'] if it.get('brk')]
    if allb:
        top = max((it['date'], it['time']) for it in allb)
        if top[0] == eds[-1]['date']:
            for it in allb:
                if (it['date'], it['time']) == top: it['live'] = True
    return eds

def active_langs(eds):
    have = set()
    for d in eds:
        for it in d['items']:
            have |= {l for l, _ in LANGS if l in it}
    return [l for l, _ in LANGS if l in have and l in UI]

def nice_date(date, l):
    dt = datetime.date.fromisoformat(date)
    if l == 'bg': return f'{WEEKDAYS[l][dt.weekday()].capitalize()}, {dt.day} {MONTHS[l][dt.month - 1]} {dt.year}'
    if l == 'en': return f'{WEEKDAYS[l][dt.weekday()]}, {dt.day} {MONTHS[l][dt.month - 1]} {dt.year}'
    return f'{WEEKDAYS[l][dt.weekday()]}, {dt.day}. {MONTHS[l][dt.month - 1]} {dt.year}'

def short_date(date, l):
    dt = datetime.date.fromisoformat(date)
    return f'{dt.day} {MONTHS[l][dt.month - 1]} {dt.year}' if l in ('bg', 'en') else f'{dt.day}. {MONTHS[l][dt.month - 1]} {dt.year}'

def art_url(it, l):
    y, m, d = it['date'].split('-')
    return f"{pre(l)}{NEWS_DIR[l]}/{y}/{m}/{d}/{it['id']}.html"

def sec_url(s, l): return f"{pre(l)}{SEC[l][s][1]}/"
def legal_url(k, l): return f"{pre(l)}{LEGAL_SLUG[l][k]}.html"
def iso(it): return f"{it['date']}T{it['time']}:00{TZ}"
def read_min(it, l):
    words = sum(len(p.split()) for p in it[l].get('body', [])) + len(it[l]['d'].split())
    return max(1, round(words / 200))

def globe_svg(cls='globe'):
    return (f'<svg class="{cls}" viewBox="0 0 80 80" fill="none" aria-hidden="true"><circle cx="40" cy="40" r="36" stroke="currentColor" stroke-width="5"/>'
            '<ellipse cx="40" cy="40" rx="15" ry="36" stroke="currentColor" stroke-width="3"/><path d="M6 40h68M12 22h56M12 58h56" stroke="currentColor" stroke-width="3"/>'
            '<circle cx="57" cy="23" r="6" fill="#e0342a"/></svg>')

import hashlib as _hl
ASSET_V={n:_hl.md5(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'static','assets',n),'rb').read()).hexdigest()[:8] for n in ('fonts.css','terra.css')}
ASSET_V['search.js']=_hl.md5(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'search.js'),'rb').read()).hexdigest()[:8]
ASSET_V['terra.js']=_hl.md5(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'terra.js'),'rb').read()).hexdigest()[:8]

def page(l, act, title, desc, canon, body, alternates=None, ld=None, og_type='website', issue=1, date=None, ticker=None, extra_head='', og_img=None):
    u = UI[l]
    alts = ''
    if alternates:
        for al, url in alternates.items():
            alts += f'<link rel="alternate" hreflang="{al}" href="{SITE}{url}">'
        if 'bg' in alternates: alts += f'<link rel="alternate" hreflang="x-default" href="{SITE}{alternates["bg"]}">'
    langbar = ''
    for code, name in LANGS:
        if code in act:
            target = (alternates or {}).get(code, pre(code))
            langbar += f'<a href="{target}" hreflang="{code}" lang="{code}" title="{e(name)}"{CUR_T if code == l else ""}>{code.upper()}</a>'

    clocks = ''.join(f'<span>{e(n)} <b data-tz="{tz}">--:--</b></span>' for n, tz in u['clocks'])
    nav = f'<a href="{pre(l)}"{CUR_P if canon == pre(l) else ""}>{e(u["home"])}</a>' + ''.join(
        f'<a href="{sec_url(s, l)}"{CUR_P if canon == sec_url(s, l) else ""}>{e(SEC[l][s][0])}</a>' for s in SECTIONS)
    tick = ''
    ticker = ticker or TICKER.get(l)
    if ticker:
        _ti = ''.join(f'<a href="{x["u"]}">{("<b class=" + chr(34) + "tbk" + chr(34) + ">" + e(u["brk"]) + "</b>") if x.get("b") else ""}<span class="tm">{x["time"]}</span>{e(x["t"])}</a><span class="sep" aria-hidden="true"></span>' for x in ticker[:15])
        _ti2 = _ti.replace('<a ', '<a tabindex="-1" ')
        _pz = {'bg': 'Пауза', 'de': 'Pause', 'en': 'Pause'}.get(l, 'Pause')
        tick = (f'<div class="ticker" role="region" aria-label="{u["live"]}"><span class="k"><i class="dot" aria-hidden="true"></i>{u["live"]}</span>'
                f'<div class="tk-track"><div class="tk-move" id="tick"><div class="tk-set">{_ti}</div><div class="tk-set" aria-hidden="true">{_ti2}</div></div></div>'
                f'<button class="tk-pause" type="button" aria-pressed="false" aria-label="{_pz}" title="{_pz}"><span aria-hidden="true"></span></button></div>')
    ldj = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if ld else ''
    return f'''<!DOCTYPE html>
<html lang="{l}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
<link rel="canonical" href="{SITE}{canon}">
{alts}
<link rel="alternate" type="application/rss+xml" title="TWN – World News ({l.upper()})" href="{SITE}{pre(l)}rss.xml">
<meta name="theme-color" content="#ffffff"><meta name="color-scheme" content="light only">
<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48"><link rel="icon" type="image/png" sizes="96x96" href="/assets/icon-96.png"><link rel="icon" type="image/png" sizes="192x192" href="/assets/icon-192.png"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="TWN – World News"><meta name="application-name" content="TWN"><meta name="apple-mobile-web-app-title" content="TWN"><link rel="manifest" href="/manifest.webmanifest"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{SITE}{canon}"><meta property="og:image" content="{SITE}{og_img or '/assets/og-image.jpg'}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="{675 if og_img else 630}"><meta property="og:locale" content="{LOCALE.get(l, l)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{SITE}{og_img or '/assets/og-image.jpg'}">
{extra_head}{ldj}
<link rel="preload" as="image" href="/assets/terra-masthead2-800.webp" imagesrcset="/assets/terra-masthead2-800.webp 800w, /assets/terra-masthead2-1600.webp 1600w" imagesizes="(max-width: 700px) 86vw, 620px" type="image/webp">
<link rel="stylesheet" href="/assets/fonts.css?v={ASSET_V['fonts.css']}">
<link rel="stylesheet" href="/assets/terra.css?v={ASSET_V['terra.css']}">
</head>
<body>
<div class="wrap">
  <div class="top">
    <div class="clocks" aria-label="{e(u['clocks'][0][0])}">{clocks}</div>
    <div class="top-r"><form class="sbox" action="{search_url(l)}" method="get" role="search"><input type="search" name="q" placeholder="{e(SUI[l]['ph'])}" aria-label="{e(SUI[l]['title'])}"><button type="submit" aria-label="{e(SUI[l]['btn'])}"><svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M15.5 15.5 21 21" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg></button></form>
    <nav class="langs" aria-label="{e(u['lang'])}">{langbar}</nav></div>
  </div>
  <header class="mast">
    <p class="brand"><a href="{pre(l)}"><img class="mast-logo" src="/assets/terra-masthead2-800.webp" srcset="/assets/terra-masthead2-800.webp 800w, /assets/terra-masthead2-1600.webp 1600w" sizes="(max-width: 700px) 86vw, 620px" width="800" height="246" alt="TERRA WORLD NEWS" fetchpriority="high"></a></p>
    <div class="edition"><span class="ed-l" aria-hidden="true"></span><span class="mid">{e(nice_date(date, l)) if date else ''}</span><span class="ed-l" aria-hidden="true"></span></div>
  </header>
  <nav class="sections" aria-label="{e(u['home'])}">{nav}</nav>
  {tick}
  <main id="main">
{body}
  </main>
  <footer>
    <div><a href="{pre(l)}" class="brand-s"><img src="/assets/twn-logo-480.webp" srcset="/assets/twn-logo-480.webp 480w, /assets/twn-logo-960.webp 960w" sizes="240px" width="480" height="148" alt="TWN – TERRA WORLD NEWS" loading="lazy"></a>{e(u['foot'])}<br>{e(u['publisher'])}</div>
    <nav><a href="{legal_url('about', l)}">{e(u['about'])}</a><a href="{legal_url('imprint', l)}">{e(u['imprint'])}</a><a href="{legal_url('privacy', l)}">{e(u['privacy'])}</a><a href="{legal_url('principles', l)}">{e(u['principles'])}</a><a href="{pre(l)}rss.xml">{e(u['rss'])}</a></nav>
  </footer>
</div>
<script src="/assets/terra.js?v={ASSET_V['terra.js']}" defer></script>
</body>
</html>'''

def SN(x): return x['n'] if isinstance(x, dict) else x
def SNAMES(xs): return ', '.join(SN(x) for x in xs)
def LI(xs): return ''.join(('<li><a href="' + e(x['u']) + '" rel="noopener nofollow" target="_blank">' + e(x['n']) + '</a></li>') if isinstance(x, dict) and x.get('u') else ('<li>' + e(SN(x)) + '</li>') for x in xs)
def CIT(xs): return [({"@type": "CreativeWork", "name": x['n'], "url": x['u']} if isinstance(x, dict) and x.get('u') else SN(x)) for x in xs]

def lic_url(lic):
    import re as _r
    t = (lic or '').strip()
    m = _r.match(r'(?i)^CC[ -]?(BY(?:-SA)?)\s*([\d.]+)\s*([a-z]{2})?$', t)
    if m:
        return f'https://creativecommons.org/licenses/{m.group(1).lower()}/{m.group(2)}/' + (f'{m.group(3).lower()}/' if m.group(3) else '')
    if _r.match(r'(?i)^CC0', t): return 'https://creativecommons.org/publicdomain/zero/1.0/'
    m = _r.match(r'(?i)^OGL\s*v?(\d)', t)
    if m: return f'https://www.nationalarchives.gov.uk/doc/open-government-licence/version/{m.group(1)}/'
    return ''

def credit(im, l, link=False):
    who = (im['art'] + ' / ') if im.get('art') else ''
    lab = {'bg': 'Снимка', 'de': 'Foto'}.get(l, 'Photo')
    txt = f'{lab}: {who}Wikimedia Commons, {im["lic"]}'
    if not link: return e(txt)
    lu = lic_url(im.get('lic'))
    mod = {'bg': 'изрязана и мащабирана', 'de': 'zugeschnitten und skaliert', 'en': 'cropped and resized'}.get(l, 'cropped and resized')
    lic_h = f'<a href="{lu}" rel="noopener nofollow license" target="_blank">{e(im["lic"])}</a>' if lu else e(im['lic'])
    return (f'{lab}: <a href="{e(im["page"])}" rel="noopener nofollow" target="_blank">{e(who + "Wikimedia Commons")}</a>, {lic_h} ({mod})')

def plate(it, l, label=None, cap=False, eager=False):
    im = it.get('img')
    if im:
        alt = im.get('alt', {}).get(l, '')
        lz = '' if eager else ' loading="lazy" decoding="async"'
        tag = f'<img src="{im["f"]}" width="{im["w"]}" height="{im["h"]}" alt="{e(alt)}"{lz}>'
        if cap:
            return f'<figure class="photo-fig"><div class="plate photo">{tag}</div><figcaption>{e(alt)} · {credit(im, l, True)}</figcaption></figure>'
        return f'<div class="plate photo">{tag}<span class="credit">{credit(im, l)}</span></div>'
    return f'<div class="plate" style="--c:{SEC_COLOR[it["s"]]}"><canvas data-seed="{it["id"]}" aria-hidden="true"></canvas><span class="lbl">{e(label or SEC[l][it["s"]][0])}</span></div>'

PUBL = {'bg': 'Публикувано', 'de': 'Veröffentlicht', 'en': 'Published'}

def num_date(d):
    y, m, dd = d.split('-')
    return f'{dd}.{m}.{y}'

def kick(it, l, prefix=''):
    if it.get('live'): prefix = f'<b class="brk">{e(UI[l]["brk"])}</b>' + prefix
    return f'<div class="kick" style="--c:{SEC_COLOR[it["s"]]}"><i></i>{prefix}{e(SEC[l][it["s"]][0])} · <time class="meta" datetime="{iso(it)}">{num_date(it["date"])}, {it["time"]}{(" " + UI[l]["hour"]) if UI[l]["hour"] else ""}</time></div>'

def card(it, l):
    T = it[l]
    pl = plate(it, l)
    if it.get('yt'): pl = pl.replace('<div class="plate', '<div class="has-v"><span class="rt-play" aria-hidden="true">▶</span><div class="plate', 1) + '</div>'
    return (f'<article class="card"><a href="{art_url(it, l)}">{pl}{kick(it, l)}<h3>{e(T["t"])}</h3></a>'
            f'<p>{e(T["d"])}</p><span class="src">{UI[l]["src"]}: {e(SNAMES(it["src"]))}</span></article>')

ORG = {"@type": "NewsMediaOrganization", "@id": SITE + "/#org", "name": "TERRA WORLD NEWS", "alternateName": ["Terra World News", "TWN", "TWN – World News", "TWN World News"], "description": "Terra World News (TWN) is an independent online news portal publishing daily news from around the world in Bulgarian, German and English.", "foundingDate": "2026", "url": SITE + "/",
       "logo": {"@type": "ImageObject", "url": SITE + "/assets/logo.png", "width": 600, "height": 185},
       "parentOrganization": {"@type": "Organization", "name": "FILMPARTNER 24 EOOD", "legalName": "„ФИЛМПАРТНЕР 24“ ЕООД", "url": "https://filmpartner24.com/", "vatID": "BG208477411"},
       "founder": {"@type": "Person", "name": "Nedy John Cross", "url": "https://nedyjcross.com/"},
       "publishingPrinciples": SITE + "/redaktsionni-printsipi.html", "correctionsPolicy": SITE + "/redaktsionni-printsipi.html#korekcii",
       "email": "media@filmpartner24.com", "areaServed": "Worldwide", "knowsLanguage": ["bg", "de", "en"]}

TICKER = {}
ARCH = {}            # Artikel älter als STATIC_DAYS: gebündelt in /_arch/<l>/<datum>/<bucket>.json, ausgeliefert von functions/
STATIC_DAYS = 14     # so viele Tage liegen Artikel als einzelne HTML-Dateien vor
ARCH_BUCKETS = 8
STATIC_FROM = '0000-00-00'
def arch_bucket(slug):
    h = 2166136261
    for b in slug.encode('utf-8'):
        h ^= b; h = (h * 16777619) & 0xffffffff
    return h % ARCH_BUCKETS
SEARCH_SLUG = {'bg': 'tarsene', 'de': 'suche', 'en': 'search'}
SUI = {
 'bg': dict(title='Търсене', ph='Име, държава, събитие или дата …', btn='Търси', all='Всички рубрики', any='По всяко време', d1='Днес', d7='Последните 7 дни', d30='Последните 30 дни',
            hint='Търсете по имена, държави, събития или дата (напр. 2 октомври или 02.10.2026). Всички думи трябва да се срещат в статията.', found='{n} резултата', none='Няма намерени статии. Опитайте с друга дума или по-широк период.', loading='Търсене …', more='Още резултати'),
 'de': dict(title='Suche', ph='Name, Land, Ereignis oder Datum …', btn='Suchen', all='Alle Rubriken', any='Gesamter Zeitraum', d1='Heute', d7='Letzte 7 Tage', d30='Letzte 30 Tage',
            hint='Suchen Sie nach Namen, Ländern, Ereignissen oder einem Datum (z. B. 2. Oktober oder 02.10.2026). Alle Wörter müssen im Artikel vorkommen.', found='{n} Treffer', none='Keine Artikel gefunden. Versuchen Sie ein anderes Wort oder einen größeren Zeitraum.', loading='Suche läuft …', more='Weitere Treffer'),
 'en': dict(title='Search', ph='Name, country, event or date …', btn='Search', all='All sections', any='Any time', d1='Today', d7='Last 7 days', d30='Last 30 days',
            hint='Search for names, countries, events or a date (e.g. 2 October or 02.10.2026). All words must appear in the article.', found='{n} results', none='No articles found. Try another word or a wider time range.', loading='Searching …', more='More results')}
SEC_CODE = {k: chr(97 + i) for i, k in enumerate(['welt', 'europa', 'deutschland', 'bulgarien', 'usa', 'ki', 'wirtschaft', 'klima', 'kultur', 'leben'])}
SEC_DESC = {'leben': {'bg': 'Какво движи живота ти: пари, жилище, работа, пътувания и дигитална сигурност – разбираемо обяснени.',
                      'de': 'Was dein Leben bewegt: Geld, Wohnen, Arbeit, Reisen und digitale Sicherheit – verständlich erklärt.',
                      'en': 'What moves your life: money, housing, work, travel and digital safety – clearly explained.'}}
NOADV = {'bg': 'Тази статия има информационен характер и не представлява правна, данъчна или финансова консултация. Данните са към посочената дата.',
         'de': 'Dieser Beitrag dient der Information und ist keine Rechts-, Steuer- oder Finanzberatung. Angaben mit dem genannten Datenstand.',
         'en': 'This article is for information only and is not legal, tax or financial advice. Figures as of the date stated.'}
DOC_CHUNK = 400
STOP = {'de': set('der die das den dem des ein eine einen einem einer eines und oder aber in im ins an am auf aus bei mit nach von vom zu zum zur für über unter vor wie als auch es er sie wir ihr ist sind war wird werden wurde hat haben nicht noch nur so dass sich bis um durch gegen'.split()),
        'en': set('the a an and or but in on at of for to from by with as is are was were be been has have had it its this that these those not no will would can could after over into about than'.split()),
        'bg': set('и в на за с от по до да се е са не че като който която което които при към след без или но той тя те то ще би беше са'.split())}
def snorm(t):
    import unicodedata
    t = unicodedata.normalize('NFD', (t or '').lower()).replace('ß', 'ss')
    return ''.join(c for c in t if not ('\u0300' <= c <= '\u036f'))
def stoks(t, l):
    import re as _r
    return [w for w in _r.findall(r'[^\W_]+', snorm(t)) if len(w) >= 2 and w not in STOP.get(l, ())]
def shard_key(w):
    return w[:2].encode('utf-8').hex()
def search_url(l): return f"{pre(l)}{SEARCH_SLUG[l]}.html"

def build():
    eds = load()
    act = active_langs(eds)
    ORG['knowsLanguage'] = act
    if os.path.exists(OUT): shutil.rmtree(OUT)
    shutil.copytree(os.path.join(HERE, 'static'), OUT)
    shutil.copy(os.path.join(HERE, 'terra.js'), os.path.join(OUT, 'assets', 'terra.js'))
    shutil.copy(os.path.join(HERE, 'search.js'), os.path.join(OUT, 'assets', 'search.js'))
    allitems = [it for d in eds for it in d['items']]
    latest = eds[-1]
    global STATIC_FROM
    import datetime as _dt
    STATIC_FROM = (_dt.date.fromisoformat(latest['date']) - _dt.timedelta(days=STATIC_DAYS - 1)).isoformat()
    ARCH.clear()
    urls = []  # (url, alternates, lastmod)
    def write(path, content):
        fp = os.path.join(OUT, path.lstrip('/'))
        if fp.endswith('/'): fp += 'index.html'
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, 'w', encoding='utf-8').write(content)

    for l in act:
        u = UI[l]
        items_l = [it for it in allitems if l in it]
        today = [it for it in latest['items'] if l in it]
        ticker = [{"t": it[l]['t'], "u": art_url(it, l), "time": it['time'], "b": it.get('live')} for it in sorted(today, key=lambda x: (bool(x.get('live')), x['time']), reverse=True)]
        TICKER[l] = ticker  # LIVE-Laufband auf allen Seiten
        # ---- home
        lead = next((it for it in today if it.get('lead')), today[0])
        rest = sorted([it for it in today if it is not lead and not it.get("live")], key=lambda x: x['time'], reverse=True)
        def rthumb(it):
            hasv = bool(it.get('yt'))
            play = f'<span class="rt-play" aria-label="{e(u["vid"])}">▶</span>' if hasv else ''
            im = it.get('img')
            if im:
                alt = im.get('alt', {}).get(l, '')
                return f'<a class="rt" href="{art_url(it, l)}" tabindex="-1"><img src="{im["f"]}" width="{im["w"]}" height="{im["h"]}" alt="{e(alt)}" loading="lazy" decoding="async">{play}</a>'
            if hasv:
                return f'<a class="rt rt-v" href="{art_url(it, l)}" tabindex="-1">{play}<span class="rt-l">{e(u["vid"])}</span></a>'
            return f'<a class="rt rt-x" href="{art_url(it, l)}" tabindex="-1" aria-hidden="true" style="--c:{SEC_COLOR[it["s"]]}"></a>'
        ranked = ''.join(f'<div class="rank"><span class="n">{i + 1}</span>{rthumb(it)}<a href="{art_url(it, l)}">{kick(it, l)}<h3>{e(it[l]["t"])}</h3></a></div>' for i, it in enumerate(rest[:5]))
        order = ['bulgarien', 'deutschland', 'welt', 'europa', 'wirtschaft', 'ki', 'klima', 'kultur'] if l == 'bg' else ['welt', 'europa', 'deutschland', 'bulgarien', 'wirtschaft', 'ki', 'klima', 'kultur'] if l == 'en' else ['deutschland', 'bulgarien', 'welt', 'europa', 'wirtschaft', 'ki', 'klima', 'kultur']
        lv = sorted([it for it in items_l if it['s'] == 'leben'], key=lambda x: (x['date'], x['time']), reverse=True)[:4]
        rails = (f'<section class="rail rail-leben" style="--c:{SEC_COLOR["leben"]}"><div class="rail-h"><h2>{e(SEC[l]["leben"][0])}</h2><a href="{sec_url("leben", l)}">{e(u["all"])}</a></div>'
                 f'<p class="sec-desc">{e(SEC_DESC["leben"][l])}</p><div class="cards">{"".join(card(it, l) for it in lv)}</div></section>') if lv else ''
        for s in order:
            its = [it for it in rest if it['s'] == s]
            if its:
                rails += f'<section class="rail" style="--c:{SEC_COLOR[s]}"><div class="rail-h"><h2>{e(SEC[l][s][0])}</h2><a href="{sec_url(s, l)}">{e(u["all"])}</a></div><div class="cards">{"".join(card(it, l) for it in its[:4])}</div></section>'
        cur = [it for it in today if it.get('live')]
        if l == 'bg': cur = sorted(cur, key=lambda x: x['s'] != 'bulgarien')
        cur = cur[:8]
        bkh = ''
        if cur:
            last = cur[0]['time']
            bkh = (f'<section class="breaking" aria-label="{e(u["brk"])}"><div class="bk-h"><h2><i class="dot" aria-hidden="true"></i>{e(u["brk"])}</h2>'
                   f'<span class="meta">{u["brkup"]} {last}{(" " + u["hour"]) if u["hour"] else ""}</span></div>'
                   f'<div class="cards">{"".join(card(it, l) for it in cur)}</div></section>')
        body = bkh + (f'<section class="lead"><div class="lead-main"><a href="{art_url(lead, l)}">{plate(lead, l, eager=True)}</a>{kick(lead, l, e(u["lead"]) + " · ")}'
                f'<a href="{art_url(lead, l)}"><h1>{e(lead[l]["t"])}</h1></a><p class="dek">{e(lead[l]["d"])}</p><span class="src">{u["src"]}: {e(SNAMES(lead["src"]))}</span></div>'
                f'<div class="ranked"><h2 class="rh">{e(u["most"])}</h2>{ranked}</div></section>{rails}')
        alts = {x: pre(x) for x in act}
        ld = {"@context": "https://schema.org", "@graph": [ORG, {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "TWN World News", "alternateName": ["TWN", "Terra World News", "TERRA WORLD NEWS"], "publisher": {"@id": SITE + "/#org"}, "inLanguage": act},
              {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE + art_url(it, l)} for i, it in enumerate([lead] + rest)]}]}
        write(pre(l), page(l, act, u['title_home'], u['desc_home'], pre(l), body, alts, ld, issue=latest.get('issue', 1), date=latest['date'], ticker=ticker))
        urls.append((pre(l), alts, latest['date']))
        # ---- sections (Ressortseite: Aufmacher + Top-Teaser, Tagesblöcke der letzten 7 Tage, Seitenleiste, Archivseiten)
        SX = {'bg': dict(latest='Последни новини', other='Други рубрики', older='По-стари новини', page='Страница', prev='← По-нови', next='По-стари →', arch='Архив'),
              'de': dict(latest='Alle Meldungen', other='Aus anderen Ressorts', older='Ältere Meldungen', page='Seite', prev='← Neuere', next='Ältere →', arch='Archiv'),
              'en': dict(latest='All stories', other='From other sections', older='Older stories', page='Page', prev='← Newer', next='Older →', arch='Archive')}[l]
        def row(it):
            T = it[l]
            return (f'<article class="row"><a class="row-img" href="{art_url(it, l)}" tabindex="-1">{plate(it, l)}</a>'
                    f'<div class="row-txt">{kick(it, l)}<a href="{art_url(it, l)}"><h3>{e(T["t"])}</h3></a><p>{e(T["d"])}</p>'
                    f'<span class="src">{u["src"]}: {e(SNAMES(it["src"]))}</span></div></article>')
        def daylist(lst):
            out, cur = '', None
            for it in lst:
                if it['date'] != cur:
                    if cur is not None: out += '</div>'
                    cur = it['date']
                    out += f'<h3 class="day-h">{e(nice_date(cur, l))}</h3><div class="rows">'
                out += row(it)
            return out + ('</div>' if cur else '')
        def mini(it):
            im = it.get('img')
            th = f'<img src="{im["f"]}" width="{im["w"]}" height="{im["h"]}" alt="" loading="lazy" decoding="async">' if im else ''
            return f'<li><a href="{art_url(it, l)}"><span class="mi">{th}</span><span>{e(it[l]["t"])}</span></a></li>'
        PER = 60
        for s in SECTIONS:
            its = sorted([it for it in items_l if it['s'] == s], key=lambda x: (x['date'], x['time']), reverse=True)
            salts = {x: sec_url(s, x) for x in act}
            if not its:
                body = f'<section class="rail" style="--c:{SEC_COLOR[s]}"><div class="rail-h"><h1 class="sec-title">{e(SEC[l][s][0])}</h1></div>' + (f'<p class="sec-desc">{e(SEC_DESC[s][l])}</p>' if s in SEC_DESC else '') + f'<p class="note">{e(u["empty"])}</p></section>'
            else:
                day0 = its[0]['date']
                today_s = [it for it in its if it['date'] == day0]
                top0 = next((it for it in today_s if it.get('live')), None) or next((it for it in today_s if it.get('lead')), None) or next((it for it in today_s if it.get('img')), today_s[0])
                tops = [top0] + [it for it in today_s if it is not top0 and it.get('img')][:4]
                tops += [it for it in today_s if it not in tops][:5 - len(tops)]
                T0 = top0[l]
                side4 = ''.join(f'<article class="st"><a href="{art_url(it, l)}">{plate(it, l)}{kick(it, l)}<h3>{e(it[l]["t"])}</h3></a></article>' for it in tops[1:5])
                head = (f'<div class="rail-h sec-head"><h1 class="sec-title">{e(SEC[l][s][0])}</h1><span class="meta">{len(its)} {u["items"]}</span></div>'
                        + (f'<p class="sec-desc">{e(SEC_DESC[s][l])}</p>' if s in SEC_DESC else '') +
                        f'<section class="sec-top"><div class="sec-lead"><a href="{art_url(top0, l)}">{plate(top0, l, eager=True)}</a>{kick(top0, l)}'
                        f'<a href="{art_url(top0, l)}"><h2>{e(T0["t"])}</h2></a><p class="dek">{e(T0["d"])}</p><span class="src">{u["src"]}: {e(SNAMES(top0["src"]))}</span></div>'
                        f'<div class="sec-four">{side4}</div></section>')
                extra = ''
                if s == 'kultur':
                    trl = [it for it in its if it['date'] == latest['date'] and it.get('yt') and it.get('trl')][:3] or [it for it in its if it['date'] == latest['date'] and it.get('yt') and not it.get('mv')][:3]
                    mvs = [it for it in its if it['date'] == latest['date'] and it.get('yt') and it.get('mv')][:3]
                    if trl: extra += f'<section class="trl-day"><h2 class="trl-h">▶ {e(u["trl"])}</h2><div class="cards">{"".join(card(it, l) for it in trl)}</div></section>'
                    if mvs: extra += f'<section class="trl-day"><h2 class="trl-h">▶ {e(u["mvd"])}</h2><div class="cards">{"".join(card(it, l) for it in mvs)}</div></section>'
                    tours = [it for it in its if it['date'] == latest['date'] and it.get('tour')][:4]
                    if tours: extra += f'<section class="trl-day"><h2 class="trl-h">♫ {e(u["tours"])}</h2><div class="cards">{"".join(card(it, l) for it in tours)}</div></section>'
                import datetime as _d7
                cut = (_d7.date.fromisoformat(day0) - _d7.timedelta(days=6)).isoformat()
                rest = [it for it in its if it not in tops]
                front = [it for it in rest if it['date'] >= cut][:80]
                older = [it for it in rest if it not in front]
                others = ''
                for s2 in SECTIONS:
                    if s2 == s: continue
                    o = sorted([it for it in items_l if it['s'] == s2], key=lambda x: (x['date'], x['time']), reverse=True)[:3]
                    if o: others += f'<div class="side-sec" style="--c:{SEC_COLOR[s2]}"><h3><a href="{sec_url(s2, l)}">{e(SEC[l][s2][0])}</a></h3><ul>{"".join(mini(it) for it in o)}</ul></div>'
                pages = [older[i:i + PER] for i in range(0, len(older), PER)]
                def purl(n): return sec_url(s, l) + (f'{"stranitsa" if l == "bg" else "seite" if l == "de" else "page"}-{n}/' if n > 1 else '')
                more = f'<p class="sec-more"><a href="{purl(2)}">{e(SX["older"])} →</a></p>' if pages else ''
                body = (f'<div class="sec-page" style="--c:{SEC_COLOR[s]}">{head}{extra}<div class="sec-main"><div class="sec-list"><h2 class="list-h">{e(SX["latest"])}</h2>{daylist(front)}{more}</div>'
                        f'<aside class="sec-side"><h2 class="list-h">{e(SX["other"])}</h2>{others}</aside></div></div>')
                for n, pit in enumerate(pages, start=2):
                    nav = f'<nav class="pager"><a href="{purl(n - 1)}">{e(SX["prev"])}</a><span>{e(SX["page"])} {n} / {len(pages) + 1}</span>' + (f'<a href="{purl(n + 1)}">{e(SX["next"])}</a>' if n <= len(pages) else '<span></span>') + '</nav>'
                    pb = (f'<div class="sec-page" style="--c:{SEC_COLOR[s]}"><div class="rail-h sec-head"><h1 class="sec-title">{e(SEC[l][s][0])} · {e(SX["arch"])}</h1><span class="meta">{e(SX["page"])} {n}</span></div>'
                          f'<div class="sec-list wide">{daylist(pit)}</div>{nav}</div>')
                    write(purl(n), page(l, act, f'{SEC[l][s][0]} – {SX["page"]} {n} | TWN – World News', f'{SEC[l][s][0]}: {u["desc_home"]}', purl(n), pb, None, {"@context": "https://schema.org", "@graph": [ORG, {"@type": "CollectionPage", "name": f'{SEC[l][s][0]} {n}', "url": SITE + purl(n), "inLanguage": l}]}, issue=latest.get('issue', 1), date=latest['date']))
            write(sec_url(s, l), page(l, act, f'{SEC[l][s][0]} | TWN – World News', f'{SEC[l][s][0]}: {u["desc_home"]}', sec_url(s, l), body, salts, {"@context": "https://schema.org", "@graph": [ORG, {"@type": "CollectionPage", "name": SEC[l][s][0], "url": SITE + sec_url(s, l), "inLanguage": l}]}, issue=latest.get('issue', 1), date=latest['date']))
            urls.append((sec_url(s, l), salts, latest['date']))
        # ---- articles
        for it in items_l:
            T = it[l]
            _b = T.get('body') or [T['d']]
            if isinstance(_b, str): _b = [p.strip() for p in _b.replace('\r', '').split('\n') if p.strip()]  # Schutz: Text als ein Block
            paras = ''.join(f'<p>{e(p)}</p>' for p in _b)
            trailer = ''
            for v in ([it['yt']] if isinstance(it.get('yt'), dict) else it.get('yt') or []):
                vid = e(v['id']); ttl = e(v.get('t', {}).get(l) or T['t'])
                isv = v.get('kind') == 'video' or it.get('brk') or it.get('mv')
                trailer += (f'<section class="trailer"><h2>{e(u["vid"] if isv else u["trailer"])}: {ttl}</h2>'
                            f'<div class="yt" data-yt="{vid}"><button type="button" class="yt-play">{e(u["playv"] if isv else u["play"])}</button><span class="yt-note">{e(u["ytnote"])}</span></div>'
                            f'<p class="src">YouTube · {e(v.get("ch", ""))} · <a href="https://www.youtube.com/watch?v={vid}" rel="noopener nofollow" target="_blank">youtube.com</a></p></section>')
            noadv = f'<p class="noadv">{e(NOADV[l])}</p>' if it['s'] == 'leben' else ''
            facts = f'<aside class="facts"><h2>{e(u["facts"])}</h2><ul>{LI(T["facts"])}</ul></aside>' if T.get('facts') else ''
            rel = [x for x in items_l if x['s'] == it['s'] and x is not it][:3]
            relh = f'<section class="rail" style="--c:{SEC_COLOR[it["s"]]}"><div class="rail-h"><h2>{e(u["more"])}</h2><a href="{sec_url(it["s"], l)}">{e(SEC[l][it["s"]][0])} →</a></div><div class="cards">{"".join(card(x, l) for x in rel)}</div></section>' if rel else ''
            body = (f'<article class="article"><a class="back" href="{sec_url(it["s"], l)}">← {e(SEC[l][it["s"]][0])}</a>{kick(it, l)}<h1>{e(T["t"])}</h1><p class="dek">{e(T["d"])}</p>'
                    f'<div class="byline meta"><span>{e(u["by"])}</span><time datetime="{iso(it)}">{PUBL[l]}: {short_date(it["date"], l)}, {it["time"]}{(" " + u["hour"]) if u["hour"] else ""}</time><span>{u["read"].format(m=read_min(it, l))}</span></div>'
                    f'{plate(it, l, cap=True, eager=True)}<div class="body">{paras}</div>{trailer}{facts}{noadv}<div class="sources"><h2>{e(u["src"])}</h2><ul>{LI(it["src"])}</ul></div></article>{relh}')
            aalts = {x: art_url(it, x) for x in act if x in it}
            ld = {"@context": "https://schema.org", "@graph": [ORG, {"@type": "NewsArticle", "@id": SITE + art_url(it, l) + "#article", "mainEntityOfPage": SITE + art_url(it, l), "headline": T['t'][:110], "description": T['d'],
                  "datePublished": iso(it), "dateModified": iso(it), "inLanguage": l, "articleSection": SEC[l][it['s']][0], "isAccessibleForFree": True,
                  "image": [SITE + (it["img"]["f"] if it.get("img") else "/assets/og-image.jpg")], "author": {"@type": "Organization", "name": u['by'], "url": SITE + legal_url('principles', l)}, "publisher": {"@id": SITE + "/#org"},
                  "citation": CIT(it['src'])},
                  {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": u['home'], "item": SITE + pre(l)}, {"@type": "ListItem", "position": 2, "name": SEC[l][it['s']][0], "item": SITE + sec_url(it['s'], l)}, {"@type": "ListItem", "position": 3, "name": T['t']}]}]}
            extra = f'<meta property="article:published_time" content="{iso(it)}"><meta property="article:section" content="{e(SEC[l][it["s"]][0])}">'
            _html = page(l, act, f'{T["t"]} | TWN', T['d'], art_url(it, l), body, aalts, ld, og_type='article', issue=latest.get('issue', 1), date=it['date'], extra_head=extra, og_img=(it['img']['f'] if it.get('img') else None))
            if it['date'] >= STATIC_FROM: write(art_url(it, l), _html)
            else: ARCH.setdefault((l, it['date'], arch_bucket(it['id'])), {})[it['id']] = _html
            urls.append((art_url(it, l), aalts, it['date']))
        # ---- legal
        for k in ('about', 'imprint', 'privacy', 'principles'):
            txt = open(os.path.join(HERE, 'legal', f'{k}.{l}.html'), encoding='utf-8').read()
            lalts = {x: legal_url(k, x) for x in act}
            write(legal_url(k, l), page(l, act, f'{u[k]} | TWN – World News', f'{u[k]} – TWN – World News (Terra World News)', legal_url(k, l), f'<article class="legal">{txt}</article>', lalts, issue=latest.get('issue', 1), date=latest['date']))
            urls.append((legal_url(k, l), lalts, latest['date']))
        # ---- search index: inverted index sharded by token prefix (scales over years) + search page
        docs = sorted(items_l, key=lambda x: (x['date'], x['time'], x['id']))
        post = {}
        days = {}
        secs = ''
        for n, it in enumerate(docs):
            T = it[l]
            body = T.get('body', '')
            body = ' '.join(body) if isinstance(body, list) else body
            y, m, d = it['date'].split('-')
            days.setdefault(it['date'], n)
            secs += SEC_CODE[it['s']]
            tt = set(stoks(T['t'], l))
            other = set(stoks(' '.join([T['d'], body, ' '.join(T.get('facts') or []), ' '.join(x.get('n', '') for x in it.get('src', [])), SEC[l][it['s']][0]]), l))
            other |= {f'd{y}{m}{d}', f'md{m}{d}', f'ym{y}{m}'}
            for w in tt | other:
                post.setdefault(w, []).append(n * 2 + (1 if w in tt else 0))
        shards = {}
        years = sorted({it['date'][:4] for it in docs}, reverse=True)
        for w, ps in post.items():
            for pp in ps:
                shards.setdefault((docs[pp >> 1]['date'][:4], shard_key(w)), {}).setdefault(w, []).append(pp)
        for (yr, k), v in shards.items():
            write(f'{pre(l)}search/t/{yr}/{k}.json', json.dumps(v, ensure_ascii=False, separators=(',', ':')))
        for c in range(0, len(docs), DOC_CHUNK):
            write(f'{pre(l)}search/d/{c // DOC_CHUNK}.json', json.dumps([[art_url(it, l), it[l]['t'], it[l]['d'], it['s'], it['date'], it['time']] for it in docs[c:c + DOC_CHUNK]], ensure_ascii=False, separators=(',', ':')))
        write(f'{pre(l)}search/meta.json', json.dumps({'n': len(docs), 'chunk': DOC_CHUNK, 'sec': secs, 'codes': {SEC_CODE[k]: k for k in SEC[l]}, 'names': {k: SEC[l][k][0] for k in SEC[l]}, 'days': days,
                                                       'months': {snorm(mn): i + 1 for i, mn in enumerate(MONTHS[l])}, 'stop': sorted(STOP.get(l, ())), 'years': years}, ensure_ascii=False, separators=(',', ':')))
        su = SUI[l]
        opts = ''.join(f'<option value="{k}">{e(SEC[l][k][0])}</option>' for k in SECTIONS if k in SEC[l])
        sbody = (f'<section class="search-page"><h1 class="sec-h">{e(su["title"])}</h1>'
                 f'<form class="sform" role="search" data-base="{pre(l)}search/" data-lang="{l}" data-found="{e(su["found"])}" data-none="{e(su["none"])}" data-loading="{e(su["loading"])}" data-more="{e(su["more"])}" data-hour="{u["hour"]}">'
                 f'<div class="srow"><input type="search" name="q" id="sq" placeholder="{e(su["ph"])}" aria-label="{e(su["title"])}" autocomplete="off"><button type="submit">{e(su["btn"])}</button></div>'
                 f'<div class="sfil"><select name="s" aria-label="{e(su["all"])}"><option value="">{e(su["all"])}</option>{opts}</select>'
                 f'<select name="p" aria-label="{e(su["any"])}"><option value="">{e(su["any"])}</option><option value="1">{e(su["d1"])}</option><option value="7">{e(su["d7"])}</option><option value="30">{e(su["d30"])}</option></select></div>'
                 f'<p class="shint">{e(su["hint"])}</p></form><p class="sstat" aria-live="polite"></p><ol class="sres"></ol><button class="smore" type="button" hidden>{e(su["more"])}</button></section>'
                 f'<script src="/assets/search.js?v={ASSET_V["search.js"]}" defer></script>')
        salts2 = {x: search_url(x) for x in act}
        write(search_url(l), page(l, act, f'{su["title"]} | TWN – World News', f'{su["title"]} – TWN – World News (Terra World News)', search_url(l), sbody, salts2, issue=latest.get('issue', 1), date=latest['date'],
              extra_head='<meta name="robots" content="noindex,follow">'))
        # ---- RSS
        rss_items = ''
        for it in sorted(items_l, key=lambda x: (x['date'], x['time']), reverse=True)[:100]:
            dt = datetime.datetime.fromisoformat(iso(it))
            rss_items += f'<item><title>{e(it[l]["t"])}</title><link>{SITE}{art_url(it, l)}</link><guid>{SITE}{art_url(it, l)}</guid><pubDate>{format_datetime(dt)}</pubDate><category>{e(SEC[l][it["s"]][0])}</category><description>{e(it[l]["d"])}</description></item>'
        write(pre(l) + 'rss.xml', f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>TWN – World News ({l.upper()})</title><link>{SITE}{pre(l)}</link><description>{e(u["desc_home"])}</description><language>{l}</language>{rss_items}</channel></rss>')

    # ---- 404 page (needed so that missing files return 404 and the archive function can step in)
    l0 = 'bg' if 'bg' in act else act[0]
    nf = ('<section class="search-page"><h1 class="sec-h">404</h1>'
          '<p>Страницата не е намерена. · Seite nicht gefunden. · Page not found.</p>'
          f'<p><a href="/">TWN – Начало</a> · <a href="/de/">TWN – Start</a> · <a href="/en/">TWN – Home</a></p></section>')
    open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8').write(page(l0, act, '404 | TWN – World News', 'Page not found', '/404.html', nf, extra_head='<meta name="robots" content="noindex">'))
    # ---- archive bundles for older articles
    for (al, ad, ab), pages in ARCH.items():
        fp = os.path.join(OUT, '_arch', al, ad, f'{ab}.json')
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, 'w', encoding='utf-8').write(json.dumps(pages, ensure_ascii=False, separators=(',', ':')))
    # ---- sitemaps
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    for url, alts, lm in urls:
        sm += f'  <url><loc>{SITE}{url}</loc><lastmod>{lm}</lastmod>' + ''.join(f'<xhtml:link rel="alternate" hreflang="{a}" href="{SITE}{h}"/>' for a, h in alts.items()) + '</url>\n'
    sm += '</urlset>\n'
    open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8').write(sm)
    newest = max(d['date'] for d in eds)
    recent = [it for it in allitems if (datetime.date.fromisoformat(newest) - datetime.date.fromisoformat(it['date'])).days <= 1]
    ns = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">\n'
    for it in recent:
        for l in act:
            if l in it:
                ns += f'  <url><loc>{SITE}{art_url(it, l)}</loc><news:news><news:publication><news:name>TWN World News</news:name><news:language>{l}</news:language></news:publication><news:publication_date>{iso(it)}</news:publication_date><news:title>{e(it[l]["t"])}</news:title></news:news></url>\n'
    ns += '</urlset>\n'
    open(os.path.join(OUT, 'news-sitemap.xml'), 'w', encoding='utf-8').write(ns)
    open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nDisallow: /_arch/\nDisallow: /search/\nDisallow: /de/search/\nDisallow: /en/search/\n\nSitemap: {SITE}/sitemap.xml\nSitemap: {SITE}/news-sitemap.xml\n')
    n = sum(1 for _ in glob.glob(OUT + '/**/*', recursive=True) if os.path.isfile(_))
    print(f'built {len(urls)} pages, {n} files, languages: {act}')

if __name__ == '__main__':
    build()
