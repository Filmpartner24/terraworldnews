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
LANGS = [('de', 'Deutsch'), ('bg', 'Български'), ('en', 'English'), ('es', 'Español'), ('pt', 'Português'), ('fr', 'Français'),
         ('it', 'Italiano'), ('ro', 'Română'), ('tr', 'Türkçe'), ('ru', 'Русский'), ('uk', 'Українська'), ('ar', 'العربية'),
         ('zh', '中文'), ('hi', 'हिन्दी'), ('ja', '日本語'), ('el', 'Ελληνικά'), ('sr', 'Српски')]
PREFIX = {'bg': '/'}  # Bulgarian is the main edition at the root
def pre(l): return PREFIX.get(l, f'/{l}/')
LOCALE = {'bg': 'bg_BG', 'de': 'de_DE', 'en': 'en_GB'}

SECTIONS = ['welt', 'europa', 'deutschland', 'bulgarien', 'usa', 'ki', 'wirtschaft', 'klima', 'kultur']
SEC = {
 'bg': {'welt': ('Свят', 'svyat'), 'europa': ('Европа', 'evropa'), 'deutschland': ('Германия', 'germania'), 'bulgarien': ('България', 'balgaria'), 'usa': ('САЩ', 'sasht'), 'ki': ('Изкуствен интелект', 'izkustven-intelekt'), 'wirtschaft': ('Икономика', 'ikonomika'), 'klima': ('Климат и енергия', 'klimat'), 'kultur': ('Развлечения', 'razvlechenia')},
 'de': {'welt': ('Welt', 'welt'), 'europa': ('Europa', 'europa'), 'deutschland': ('Deutschland', 'deutschland'), 'bulgarien': ('Bulgarien', 'bulgarien'), 'usa': ('USA', 'usa'), 'ki': ('KI', 'ki'), 'wirtschaft': ('Wirtschaft', 'wirtschaft'), 'klima': ('Klima & Energie', 'klima'), 'kultur': ('Entertainment', 'entertainment')},
 'en': {'welt': ('World', 'world'), 'europa': ('Europe', 'europe'), 'deutschland': ('Germany', 'germany'), 'bulgarien': ('Bulgaria', 'bulgaria'), 'usa': ('USA', 'usa'), 'ki': ('AI', 'ai'), 'wirtschaft': ('Business', 'business'), 'klima': ('Climate & Energy', 'climate'), 'kultur': ('Entertainment', 'entertainment')},
}
SEC_COLOR = {'welt': 'var(--cobalt)', 'europa': '#5b3fc4', 'deutschland': 'var(--muted)', 'bulgarien': 'var(--teal)', 'usa': '#b23a48', 'ki': '#0f7c9c', 'wirtschaft': 'var(--sand)', 'klima': '#2f8a4a', 'kultur': 'var(--signal)'}
NEWS_DIR = {'bg': 'novini', 'de': 'nachrichten', 'en': 'news'}
WEEKDAYS = {'bg': ['понеделник', 'вторник', 'сряда', 'четвъртък', 'петък', 'събота', 'неделя'], 'de': ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'], 'en': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
MONTHS = {'bg': ['януари', 'февруари', 'март', 'април', 'май', 'юни', 'юли', 'август', 'септември', 'октомври', 'ноември', 'декември'], 'de': ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'], 'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']}

UI = {
 'bg': dict(home='Начало', tagline='Новини от целия свят', ed='Брой {n} · Година I', places='София · Берлин · Светът', clocks=[('Берлин', 'Europe/Berlin'), ('София', 'Europe/Sofia'), ('Лондон', 'Europe/London'), ('Ню Йорк', 'America/New_York'), ('Пекин', 'Asia/Shanghai')],
   lead='Водеща новина', most='Последни новини', all='Всички новини →', src='Източници', by='Редакция TERRA', read='Четене {m} мин.', hour='ч.', items='новини', facts='Най-важното', more='Още от рубриката', trailer='Трейлър', play='▶ Пусни трейлъра', ytnote='При пускане видеото се зарежда от YouTube (Google).', empty='В тази рубрика скоро ще излизат материали на редакцията.',
   foot='Независими новини от целия свят · Редакция София и Берлин', publisher='Издател: FILMPARTNER 24 EOOD', imprint='Импресум', privacy='Поверителност', principles='Редакционни принципи', rss='RSS', back='Към началото',
   desc_home='TWN – World News (Terra World News): новини от целия свят, от България, Германия и Европа. Всеки ден, проверени и с посочени източници.', title_home='TWN – World News | Terra World News – Новини от целия свят', live='НА ЖИВО', lang='Език'),
 'de': dict(home='Start', tagline='Nachrichten aus aller Welt', ed='Ausgabe {n} · Jahrgang I', places='Sofia · Berlin · Die Welt', clocks=[('Berlin', 'Europe/Berlin'), ('Sofia', 'Europe/Sofia'), ('London', 'Europe/London'), ('New York', 'America/New_York'), ('Peking', 'Asia/Shanghai')],
   lead='Aufmacher', most='Neueste Meldungen', all='Alle Meldungen →', src='Quellen', by='TERRA-Redaktion', read='Lesezeit {m} Min.', hour='Uhr', items='Meldungen', facts='Das Wichtigste', more='Mehr aus dem Ressort', trailer='Trailer', play='▶ Trailer abspielen', ytnote='Beim Abspielen wird das Video von YouTube (Google) geladen.', empty='In diesem Ressort erscheinen in Kürze Meldungen der Redaktion.',
   foot='Unabhängige Nachrichten aus aller Welt · Redaktion Sofia & Berlin', publisher='Herausgeber: FILMPARTNER 24 EOOD', imprint='Impressum', privacy='Datenschutz', principles='Redaktionsgrundsätze', rss='RSS', back='Zur Startseite',
   desc_home='TWN – World News (Terra World News): Nachrichten aus aller Welt, aus Deutschland, Bulgarien und Europa. Täglich, geprüft und mit Quellenangaben.', title_home='TWN – World News | Terra World News – Nachrichten aus aller Welt', live='LIVE', lang='Sprache'),
 'en': dict(home='Home', tagline='News from around the world', ed='Issue {n}', places='', clocks=[('Berlin', 'Europe/Berlin'), ('Sofia', 'Europe/Sofia'), ('London', 'Europe/London'), ('New York', 'America/New_York'), ('Beijing', 'Asia/Shanghai')],
   lead='Top story', most='Latest news', all='All news →', src='Sources', by='TWN newsroom', read='{m} min read', hour='', items='stories', facts='Key points', more='More from this section', trailer='Trailer', play='▶ Play trailer', ytnote='Playing the video loads it from YouTube (Google).', empty='Stories from our newsroom will appear in this section soon.',
   foot='Independent news from around the world · Newsrooms in Sofia & Berlin', publisher='Publisher: FILMPARTNER 24 EOOD', imprint='Imprint', privacy='Privacy', principles='Editorial principles', rss='RSS', back='Back to home',
   desc_home='TWN – World News (Terra World News): news from around the world, from Europe, Germany, Bulgaria and the USA. Daily, fact-checked and with sources.', title_home='TWN – World News | Terra World News – News from around the world', live='LIVE', lang='Language'),
}
LEGAL_SLUG = {'bg': {'imprint': 'impresum', 'privacy': 'poveritelnost', 'principles': 'redaktsionni-printsipi'}, 'de': {'imprint': 'impressum', 'privacy': 'datenschutz', 'principles': 'redaktionsgrundsaetze'}, 'en': {'imprint': 'imprint', 'privacy': 'privacy', 'principles': 'editorial-principles'}}

def load():
    eds = []
    for f in sorted(glob.glob(os.path.join(HERE, 'content', '*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        for it in d['items']:
            it['date'] = d['date']
        eds.append(d)
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
    if ticker:
        tick = f'<div class="ticker"><span class="k">{u["live"]}</span><p id="tick" data-items="{e(json.dumps(ticker, ensure_ascii=False))}"><a href="{ticker[0]["u"]}"><span class="meta">{ticker[0]["time"]}</span> · {e(ticker[0]["t"])}</a></p></div>'
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
    <nav class="langs" aria-label="{e(u['lang'])}">{langbar}</nav>
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
    <nav><a href="{legal_url('imprint', l)}">{e(u['imprint'])}</a><a href="{legal_url('privacy', l)}">{e(u['privacy'])}</a><a href="{legal_url('principles', l)}">{e(u['principles'])}</a><a href="{pre(l)}rss.xml">{e(u['rss'])}</a></nav>
  </footer>
</div>
<script src="/assets/terra.js" defer></script>
</body>
</html>'''

def SN(x): return x['n'] if isinstance(x, dict) else x
def SNAMES(xs): return ', '.join(SN(x) for x in xs)
def LI(xs): return ''.join(('<li><a href="' + e(x['u']) + '" rel="noopener nofollow" target="_blank">' + e(x['n']) + '</a></li>') if isinstance(x, dict) and x.get('u') else ('<li>' + e(SN(x)) + '</li>') for x in xs)
def CIT(xs): return [({"@type": "CreativeWork", "name": x['n'], "url": x['u']} if isinstance(x, dict) and x.get('u') else SN(x)) for x in xs]

def credit(im, l, link=False):
    who = (im['art'] + ' / ') if im.get('art') else ''
    lab = {'bg': 'Снимка', 'de': 'Foto'}.get(l, 'Photo')
    txt = f'{lab}: {who}Wikimedia Commons, {im["lic"]}'
    return f'<a href="{e(im["page"])}" rel="noopener nofollow" target="_blank">{e(txt)}</a>' if link else e(txt)

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

def kick(it, l, prefix=''):
    return f'<div class="kick" style="--c:{SEC_COLOR[it["s"]]}"><i></i>{prefix}{e(SEC[l][it["s"]][0])} · <span class="meta">{it["time"]} {UI[l]["hour"]}</span></div>'

def card(it, l):
    T = it[l]
    return (f'<article class="card"><a href="{art_url(it, l)}">{plate(it, l)}{kick(it, l)}<h3>{e(T["t"])}</h3></a>'
            f'<p>{e(T["d"])}</p><span class="src">{UI[l]["src"]}: {e(SNAMES(it["src"]))}</span></article>')

ORG = {"@type": "NewsMediaOrganization", "@id": SITE + "/#org", "name": "TERRA WORLD NEWS", "alternateName": ["TWN", "TWN World News"], "url": SITE + "/",
       "logo": {"@type": "ImageObject", "url": SITE + "/assets/logo.png", "width": 600, "height": 185},
       "parentOrganization": {"@type": "Organization", "name": "FILMPARTNER 24 EOOD", "legalName": "„ФИЛМПАРТНЕР 24“ ЕООД", "url": "https://filmpartner24.com/", "vatID": "BG208477411"},
       "founder": {"@type": "Person", "name": "Nedy John Cross", "url": "https://nedyjcross.com/"},
       "publishingPrinciples": SITE + "/redaktsionni-printsipi.html", "correctionsPolicy": SITE + "/redaktsionni-printsipi.html#korekcii",
       "email": "media@filmpartner24.com", "areaServed": "Worldwide", "knowsLanguage": ["bg", "de"]}

def build():
    eds = load()
    act = active_langs(eds)
    ORG['knowsLanguage'] = act
    if os.path.exists(OUT): shutil.rmtree(OUT)
    shutil.copytree(os.path.join(HERE, 'static'), OUT)
    shutil.copy(os.path.join(HERE, 'terra.js'), os.path.join(OUT, 'assets', 'terra.js'))
    allitems = [it for d in eds for it in d['items']]
    latest = eds[-1]
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
        ticker = [{"t": it[l]['t'], "u": art_url(it, l), "time": it['time']} for it in sorted(today, key=lambda x: x['time'], reverse=True)]
        # ---- home
        lead = next((it for it in today if it.get('lead')), today[0])
        rest = sorted([it for it in today if it is not lead], key=lambda x: x['time'], reverse=True)
        ranked = ''.join(f'<div class="rank"><span class="n">{i + 1}</span><a href="{art_url(it, l)}"><div class="kick" style="--c:{SEC_COLOR[it["s"]]}"><i></i>{e(SEC[l][it["s"]][0])}</div><h3>{e(it[l]["t"])}</h3></a></div>' for i, it in enumerate(rest[:5]))
        order = ['bulgarien', 'welt', 'europa', 'deutschland', 'usa', 'ki', 'wirtschaft', 'klima', 'kultur'] if l == 'bg' else ['welt', 'europa', 'usa', 'deutschland', 'bulgarien', 'ki', 'wirtschaft', 'klima', 'kultur'] if l == 'en' else ['welt', 'deutschland', 'europa', 'bulgarien', 'usa', 'ki', 'wirtschaft', 'klima', 'kultur']
        rails = ''
        for s in order:
            its = [it for it in rest if it['s'] == s]
            if its:
                rails += f'<section class="rail" style="--c:{SEC_COLOR[s]}"><div class="rail-h"><h2>{e(SEC[l][s][0])}</h2><a href="{sec_url(s, l)}">{e(u["all"])}</a></div><div class="cards">{"".join(card(it, l) for it in its[:4])}</div></section>'
        body = (f'<section class="lead"><div class="lead-main"><a href="{art_url(lead, l)}">{plate(lead, l, eager=True)}</a>{kick(lead, l, e(u["lead"]) + " · ")}'
                f'<a href="{art_url(lead, l)}"><h1>{e(lead[l]["t"])}</h1></a><p class="dek">{e(lead[l]["d"])}</p><span class="src">{u["src"]}: {e(SNAMES(lead["src"]))}</span></div>'
                f'<div class="ranked"><h2 class="rh">{e(u["most"])}</h2>{ranked}</div></section>{rails}')
        alts = {x: pre(x) for x in act}
        ld = {"@context": "https://schema.org", "@graph": [ORG, {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "TWN World News", "alternateName": ["TWN", "Terra World News", "TERRA WORLD NEWS"], "publisher": {"@id": SITE + "/#org"}, "inLanguage": act},
              {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE + art_url(it, l)} for i, it in enumerate([lead] + rest)]}]}
        write(pre(l), page(l, act, u['title_home'], u['desc_home'], pre(l), body, alts, ld, issue=latest.get('issue', 1), date=latest['date'], ticker=ticker))
        urls.append((pre(l), alts, latest['date']))
        # ---- sections
        for s in SECTIONS:
            its = sorted([it for it in items_l if it['s'] == s], key=lambda x: (x['date'], x['time']), reverse=True)
            inner = f'<div class="cards">{"".join(card(it, l) for it in its)}</div>' if its else f'<p class="note">{e(u["empty"])}</p>'
            body = f'<section class="rail" style="--c:{SEC_COLOR[s]}"><div class="rail-h"><h1 class="sec-h">{e(SEC[l][s][0])}</h1><span class="meta">{len(its)} {u["items"]}</span></div>{inner}</section>'
            body = body.replace('<h1 class="sec-h">', '<h2>').replace('</h1>', '</h2>', 1)
            salts = {x: sec_url(s, x) for x in act}
            write(sec_url(s, l), page(l, act, f'{SEC[l][s][0]} | TWN – World News', f'{SEC[l][s][0]}: {u["desc_home"]}', sec_url(s, l), body, salts, {"@context": "https://schema.org", "@graph": [ORG, {"@type": "CollectionPage", "name": SEC[l][s][0], "url": SITE + sec_url(s, l), "inLanguage": l}]}, issue=latest.get('issue', 1), date=latest['date']))
            urls.append((sec_url(s, l), salts, latest['date']))
        # ---- articles
        for it in items_l:
            T = it[l]
            paras = ''.join(f'<p>{e(p)}</p>' for p in T.get('body', [T['d']]))
            trailer = ''
            for v in ([it['yt']] if isinstance(it.get('yt'), dict) else it.get('yt') or []):
                vid = e(v['id']); ttl = e(v.get('t', {}).get(l) or T['t'])
                trailer += (f'<section class="trailer"><h2>{e(u["trailer"])}: {ttl}</h2>'
                            f'<div class="yt" data-yt="{vid}"><button type="button" class="yt-play">{e(u["play"])}</button><span class="yt-note">{e(u["ytnote"])}</span></div>'
                            f'<p class="src">YouTube · {e(v.get("ch", ""))} · <a href="https://www.youtube.com/watch?v={vid}" rel="noopener nofollow" target="_blank">youtube.com</a></p></section>')
            facts = f'<aside class="facts"><h2>{e(u["facts"])}</h2><ul>{LI(T["facts"])}</ul></aside>' if T.get('facts') else ''
            rel = [x for x in items_l if x['s'] == it['s'] and x is not it][:3]
            relh = f'<section class="rail" style="--c:{SEC_COLOR[it["s"]]}"><div class="rail-h"><h2>{e(u["more"])}</h2><a href="{sec_url(it["s"], l)}">{e(SEC[l][it["s"]][0])} →</a></div><div class="cards">{"".join(card(x, l) for x in rel)}</div></section>' if rel else ''
            body = (f'<article class="article"><a class="back" href="{sec_url(it["s"], l)}">← {e(SEC[l][it["s"]][0])}</a>{kick(it, l)}<h1>{e(T["t"])}</h1><p class="dek">{e(T["d"])}</p>'
                    f'<div class="byline meta"><span>{e(u["by"])}</span><time datetime="{iso(it)}">{short_date(it["date"], l)}, {it["time"]} {u["hour"]}</time><span>{u["read"].format(m=read_min(it, l))}</span></div>'
                    f'{plate(it, l, cap=True, eager=True)}<div class="body">{paras}</div>{trailer}{facts}<div class="sources"><h2>{e(u["src"])}</h2><ul>{LI(it["src"])}</ul></div></article>{relh}')
            aalts = {x: art_url(it, x) for x in act if x in it}
            ld = {"@context": "https://schema.org", "@graph": [ORG, {"@type": "NewsArticle", "@id": SITE + art_url(it, l) + "#article", "mainEntityOfPage": SITE + art_url(it, l), "headline": T['t'][:110], "description": T['d'],
                  "datePublished": iso(it), "dateModified": iso(it), "inLanguage": l, "articleSection": SEC[l][it['s']][0], "isAccessibleForFree": True,
                  "image": [SITE + (it["img"]["f"] if it.get("img") else "/assets/og-image.jpg")], "author": {"@type": "Organization", "name": u['by'], "url": SITE + legal_url('principles', l)}, "publisher": {"@id": SITE + "/#org"},
                  "citation": CIT(it['src'])},
                  {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": u['home'], "item": SITE + pre(l)}, {"@type": "ListItem", "position": 2, "name": SEC[l][it['s']][0], "item": SITE + sec_url(it['s'], l)}, {"@type": "ListItem", "position": 3, "name": T['t']}]}]}
            extra = f'<meta property="article:published_time" content="{iso(it)}"><meta property="article:section" content="{e(SEC[l][it["s"]][0])}">'
            write(art_url(it, l), page(l, act, f'{T["t"]} | TWN', T['d'], art_url(it, l), body, aalts, ld, og_type='article', issue=latest.get('issue', 1), date=it['date'], extra_head=extra, og_img=(it['img']['f'] if it.get('img') else None)))
            urls.append((art_url(it, l), aalts, it['date']))
        # ---- legal
        for k in ('imprint', 'privacy', 'principles'):
            txt = open(os.path.join(HERE, 'legal', f'{k}.{l}.html'), encoding='utf-8').read()
            lalts = {x: legal_url(k, x) for x in act}
            write(legal_url(k, l), page(l, act, f'{u[k]} | TWN – World News', f'{u[k]} – TWN – World News (Terra World News)', legal_url(k, l), f'<article class="legal">{txt}</article>', lalts, issue=latest.get('issue', 1), date=latest['date']))
            urls.append((legal_url(k, l), lalts, latest['date']))
        # ---- RSS
        rss_items = ''
        for it in sorted(items_l, key=lambda x: (x['date'], x['time']), reverse=True)[:100]:
            dt = datetime.datetime.fromisoformat(iso(it))
            rss_items += f'<item><title>{e(it[l]["t"])}</title><link>{SITE}{art_url(it, l)}</link><guid>{SITE}{art_url(it, l)}</guid><pubDate>{format_datetime(dt)}</pubDate><category>{e(SEC[l][it["s"]][0])}</category><description>{e(it[l]["d"])}</description></item>'
        write(pre(l) + 'rss.xml', f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>TWN – World News ({l.upper()})</title><link>{SITE}{pre(l)}</link><description>{e(u["desc_home"])}</description><language>{l}</language>{rss_items}</channel></rss>')

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
    open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\nSitemap: {SITE}/news-sitemap.xml\n')
    n = sum(1 for _ in glob.glob(OUT + '/**/*', recursive=True) if os.path.isfile(_))
    print(f'built {len(urls)} pages, {n} files, languages: {act}')

if __name__ == '__main__':
    build()
