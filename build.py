#!/usr/bin/env python3
"""TERRA WORLD NEWS – static site generator.
Usage: python3 build.py   → writes ./out
Content: content/YYYY-MM-DD.json (one file per daily edition)."""
import json, os, glob, shutil, html, datetime, re
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

SECTIONS = ['welt', 'europa', 'deutschland', 'bulgarien', 'leben', 'ki', 'wirtschaft', 'energie', 'business', 'klima', 'ai', 'film', 'musik', 'games', 'sport']
MEDIA = ('games', 'film', 'musik', 'sport', 'ai', 'ki', 'wirtschaft', 'energie', 'leben', 'klima', 'welt', 'europa', 'deutschland', 'bulgarien')   # Rubriken mit eigenem Medien-Layout (Reviews/Trailer + News)
SUBS = {'sport': ['fussball', 'boxen', 'mma']}
SLOGAN = {'bg': ['НОВИНИ', 'ФАКТИ', 'КОНТЕКСТ'], 'de': ['NACHRICHTEN', 'FAKTEN', 'KONTEXT'], 'en': ['NEWS', 'FACTS', 'CONTEXT']}
NAV_GROUPS = [  # Menü-Gruppen (Desktop: Trennstriche, Mobil: Überschriften im aufgeklappten Menü)
    ('news', {'bg': 'Новини', 'de': 'Nachrichten', 'en': 'News'}, ['welt', 'europa', 'deutschland', 'bulgarien']),
    ('life', {'bg': 'Живот', 'de': 'Leben', 'en': 'Life'}, ['leben']),
    ('know', {'bg': 'Икономика и знание', 'de': 'Wirtschaft & Wissen', 'en': 'Economy & Knowledge'}, ['ki', 'wirtschaft', 'energie', 'business', 'klima', 'ai']),
    ('ent', {'bg': 'Развлечения', 'de': 'Unterhaltung', 'en': 'Entertainment'}, ['film', 'musik', 'games']),
    ('sport', {'bg': 'Спорт', 'de': 'Sport', 'en': 'Sport'}, ['sport'])]   # Unterrubriken (Feld "sub" im Item)
SUB = {'bg': {'fussball': ('Футбол', 'futbol'), 'boxen': ('Бокс', 'boks'), 'mma': ('ММА', 'mma')},
       'de': {'fussball': ('Fußball', 'fussball'), 'boxen': ('Boxen', 'boxen'), 'mma': ('MMA', 'mma')},
       'en': {'fussball': ('Football', 'football'), 'boxen': ('Boxing', 'boxing'), 'mma': ('MMA', 'mma')}}
SEC = {
 'bg': {'welt': ('Свят', 'svyat'), 'europa': ('Европа', 'evropa'), 'deutschland': ('Германия', 'germania'), 'bulgarien': ('България', 'balgaria'), 'ki': ('Технологии', 'tehnologii'), 'wirtschaft': ('Икономика', 'ikonomika'), 'business': ('Бизнес', 'biznes'), 'klima': ('Климат', 'klimat'), 'ai': ('ИИ', 'izkustven-intelekt'), 'energie': ('Енергия', 'energia'), 'kultur': ('Развлечения', 'razvlechenia'), 'games': ('Игри', 'igri'), 'film': ('Филми', 'filmi'), 'musik': ('Музика', 'muzika'), 'sport': ('Спорт', 'sport'), 'leben': ('Живот и ежедневие', 'zhivot')},
 'de': {'welt': ('Welt', 'welt'), 'europa': ('Europa', 'europa'), 'deutschland': ('Deutschland', 'deutschland'), 'bulgarien': ('Bulgarien', 'bulgarien'), 'ki': ('Technologie', 'technologie'), 'wirtschaft': ('Wirtschaft', 'wirtschaft'), 'business': ('Business', 'business'), 'klima': ('Klima', 'klima'), 'ai': ('KI', 'ki'), 'energie': ('Energie', 'energie'), 'kultur': ('Entertainment', 'entertainment'), 'leben': ('Leben & Alltag', 'leben-alltag'), 'games': ('Games', 'games'), 'sport': ('Sport', 'sport'), 'film': ('Film', 'film'), 'musik': ('Musik', 'musik')},
 'en': {'welt': ('World', 'world'), 'europa': ('Europe', 'europe'), 'deutschland': ('Germany', 'germany'), 'bulgarien': ('Bulgaria', 'bulgaria'), 'ki': ('Technology', 'technology'), 'wirtschaft': ('Economy', 'economy'), 'business': ('Business', 'business'), 'klima': ('Climate', 'climate'), 'ai': ('AI', 'ai'), 'energie': ('Energy', 'energy'), 'kultur': ('Entertainment', 'entertainment'), 'leben': ('Everyday Life', 'everyday-life'), 'games': ('Games', 'games'), 'sport': ('Sport', 'sport'), 'film': ('Film', 'film'), 'musik': ('Music', 'music')},
}
SEC_COLOR = {'welt': 'var(--cobalt)', 'europa': '#5b3fc4', 'deutschland': 'var(--muted)', 'bulgarien': 'var(--teal)', 'usa': '#b23a48', 'ki': '#0f7c9c', 'wirtschaft': 'var(--sand)', 'business': '#0a7d5a', 'klima': '#2f8a4a', 'ai': '#06b6d4', 'energie': '#d97706', 'kultur': 'var(--signal)', 'games': '#7b2cbf', 'film': '#d62839', 'musik': '#0e9f6e', 'sport': '#e85d04', 'leben': '#c26a00'}
NEWS_DIR = {'bg': 'novini', 'de': 'nachrichten', 'en': 'news'}
WEEKDAYS = {'bg': ['понеделник', 'вторник', 'сряда', 'четвъртък', 'петък', 'събота', 'неделя'], 'de': ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'], 'en': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
MONTHS = {'bg': ['януари', 'февруари', 'март', 'април', 'май', 'юни', 'юли', 'август', 'септември', 'октомври', 'ноември', 'декември'], 'de': ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'], 'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']}

UI = {
 'bg': dict(home='Начало', tagline='Новини от целия свят', ed='Брой {n} · Година I', places='София · Берлин · Светът', clocks=[('Берлин', 'Europe/Berlin'), ('София', 'Europe/Sofia'), ('Лондон', 'Europe/London'), ('Ню Йорк', 'America/New_York'), ('Пекин', 'Asia/Shanghai')],
   brk='Извънредно', brkup='Update', vid='Видео', playv='▶ Пусни видеото', trl='Трейлъри на деня', nat='Най-красивата природа на света', mvd='Музикални видеа на деня', tours='Турнета и концерти', lead='Водеща новина', most='Последни новини', all='Всички новини →', src='Източници', by='Редакция TERRA', read='Четене {m} мин.', hour='ч.', items='новини', facts='Най-важното', more='Още от рубриката', trailer='Трейлър', play='▶ Пусни трейлъра', ytnote='При пускане видеото се зарежда от YouTube (Google).', empty='В тази рубрика скоро ще излизат материали на редакцията.',
   foot='Terra World News (TWN) – независим новинарски портал с новини от целия свят · Редакция София и Берлин', about='За нас', publisher='Издател: FILMPARTNER 24 EOOD', imprint='Импресум', privacy='Поверителност', principles='Редакционни принципи', rss='RSS', back='Към началото',
   desc_home='TWN – World News (Terra World News): новини от целия свят, от България, Германия и Европа. Всеки ден, проверени и с посочени източници.', title_home='TWN – World News | Terra World News – Новини от целия свят', live='НА ЖИВО', lang='Език'),
 'de': dict(home='Start', tagline='Nachrichten aus aller Welt', ed='Ausgabe {n} · Jahrgang I', places='Sofia · Berlin · Die Welt', clocks=[('Berlin', 'Europe/Berlin'), ('Sofia', 'Europe/Sofia'), ('London', 'Europe/London'), ('New York', 'America/New_York'), ('Peking', 'Asia/Shanghai')],
   brk='Breaking News', brkup='Update', vid='Video', playv='▶ Video abspielen', trl='Trailer des Tages', nat='Die schönste Natur der Welt', mvd='Musikvideos des Tages', tours='Tourneen & Konzerte', lead='Aufmacher', most='Neueste Meldungen', all='Alle Meldungen →', src='Quellen', by='TERRA-Redaktion', read='Lesezeit {m} Min.', hour='Uhr', items='Meldungen', facts='Das Wichtigste', more='Mehr aus dem Ressort', trailer='Trailer', play='▶ Trailer abspielen', ytnote='Beim Abspielen wird das Video von YouTube (Google) geladen.', empty='In diesem Ressort erscheinen in Kürze Meldungen der Redaktion.',
   foot='Terra World News (TWN) – unabhängiges Nachrichtenportal mit Nachrichten aus aller Welt · Redaktion Sofia & Berlin', about='Über uns', publisher='Herausgeber: FILMPARTNER 24 EOOD', imprint='Impressum', privacy='Datenschutz', principles='Redaktionsgrundsätze', rss='RSS', back='Zur Startseite',
   desc_home='TWN – World News (Terra World News): Nachrichten aus aller Welt, aus Deutschland, Bulgarien und Europa. Täglich, geprüft und mit Quellenangaben.', title_home='TWN – World News | Terra World News – Nachrichten aus aller Welt', live='LIVE', lang='Sprache'),
 'en': dict(home='Home', tagline='News from around the world', ed='Issue {n}', places='', clocks=[('Berlin', 'Europe/Berlin'), ('Sofia', 'Europe/Sofia'), ('London', 'Europe/London'), ('New York', 'America/New_York'), ('Beijing', 'Asia/Shanghai')],
   brk='Breaking News', brkup='Update', vid='Video', playv='▶ Play video', trl='Trailers of the day', nat="The world's most beautiful nature", mvd='Music videos of the day', tours='Tours & concerts', lead='Top story', most='Latest news', all='All news →', src='Sources', by='TWN newsroom', read='{m} min read', hour='', items='stories', facts='Key points', more='More from this section', trailer='Trailer', play='▶ Play trailer', ytnote='Playing the video loads it from YouTube (Google).', empty='Stories from our newsroom will appear in this section soon.',
   foot='Terra World News (TWN) – an independent news portal with news from around the world · Newsrooms in Sofia & Berlin', about='About us', publisher='Publisher: FILMPARTNER 24 EOOD', imprint='Imprint', privacy='Privacy', principles='Editorial principles', rss='RSS', back='Back to home',
   desc_home='TWN – World News (Terra World News): news from around the world, from Europe, Germany, Bulgaria and the USA. Daily, fact-checked and with sources.', title_home='TWN – World News | Terra World News – News from around the world', live='LIVE', lang='Language'),
}
LEGAL_SLUG = {'bg': {'about': 'za-nas', 'imprint': 'impresum', 'privacy': 'poveritelnost', 'principles': 'redaktsionni-printsipi'}, 'de': {'about': 'ueber-uns', 'imprint': 'impressum', 'privacy': 'datenschutz', 'principles': 'redaktionsgrundsaetze'}, 'en': {'about': 'about', 'imprint': 'imprint', 'privacy': 'privacy', 'principles': 'editorial-principles'}}

FILM_W = ('film', 'kino', 'trailer', 'oscar', 'serie', 'netflix', 'regie', 'regisseur', 'schauspiel', 'studio', 'disney', 'marvel', 'berlinale', 'cannes', 'venedig', 'golden globe', 'emmy', 'streaming', 'box office', 'kinostart')
def kultur_to(it):
    if it.get('trl'): return 'film'
    if it.get('mv') or it.get('tour'): return 'musik'
    t = ' '.join([it.get('de', {}).get('t', ''), it.get('de', {}).get('d', '')]).lower()
    return 'film' if any(w in t for w in FILM_W) else 'musik'

def load():
    eds, brk = [], []
    for f in sorted(glob.glob(os.path.join(HERE, 'content', '*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        for it in d['items']:
            it['date'] = d['date']
            if it.get('s') == 'usa': it['s'] = 'welt'
            if it.get('s') == 'klima' and it.get('nat'): it['s'] = 'leben'; it['_kl'] = True  # Naturorte laufen unter Leben & Alltag, Klima hat wieder eigene Rubrik  # Klima/Natur läuft unter Leben & Alltag (seit 03.10.2026)  # USA-Meldungen laufen unter Welt
            if it.get('s') == 'kultur': it['s'] = kultur_to(it)  # Entertainment aufgeteilt in Film und Musik
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
    # Business-Seite (content/business/YYYY-MM-DD.json): jeder Bericht wird zusätzlich eine Meldung (Rubrik business, zusätzlich zu den 77)
    for f in sorted(glob.glob(os.path.join(HERE, 'content', 'business', '*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        its = []
        for b in d.get('blocks', []):
            it = {'id': b['id'], 'date': d['date'], 's': 'business', 'time': b.get('time') or d.get('time', '07:00'), 'src': b.get('src', []), 'biz': b}
            if b.get('img') and os.path.exists(os.path.join(HERE, 'static', b['img']['f'].lstrip('/'))): it['img'] = b['img']
            for _l in ('bg', 'de', 'en'):
                if _l in b: it[_l] = {k: b[_l][k] for k in ('t', 'd', 'body') if k in b[_l]}
            its.append(it)
        BIZ[d['date']] = d
        brk.append({'date': d['date'], 'items': its})
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
def sub_url(s, k, l): return f"{sec_url(s, l)}{SUB[l][k][1]}/"
def sec_home(s, l, sub=None):  # Rubriken mit Unterrubriken (Sport) haben keine eigene Übersichtsseite → erste/zugehörige Unterrubrik
    return sub_url(s, sub if sub in SUBS.get(s, []) else SUBS[s][0], l) if s in SUBS else sec_url(s, l)
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

def page(l, act, title, desc, canon, body, alternates=None, ld=None, og_type='website', issue=1, date=None, ticker=None, extra_head='', og_img=None, ticker2=''):
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
    def _navi(s):
        a = f'<a href="{sec_home(s, l)}"{CUR_P if canon == sec_url(s, l) or (s in SUBS and canon.startswith(sec_url(s, l))) else ""}>{e(SEC[l][s][0])}</a>'
        if s not in SUBS: return a
        dd = ''.join(f'<a href="{sub_url(s, k, l)}"{CUR_P if canon == sub_url(s, k, l) else ""}>{e(SUB[l][k][0])}</a>' for k in SUBS[s])
        return f'<span class="nav-dd">{a}<span class="dd">{dd}</span></span>'
    _home_svg = '<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true"><path d="M3 11.2 12 4l9 7.2" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"/><path d="M5.5 10v9.5h4.6v-5.6h3.8v5.6h4.6V10" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linejoin="round"/></svg>'
    nav = f'<a class="nv-home" href="{pre(l)}"{CUR_P if canon == pre(l) else ""}>{_home_svg}<span>{e(u["home"])}</span></a>'
    for _g, _gl, _gs in NAV_GROUPS:
        _in = ''.join(_navi(s) for s in _gs if s in SECTIONS)
        if _in: nav += f'<div class="ng ng-{_g}"><span class="ng-h">{e(_gl[l])}</span>{_in}</div>'
    _cur = next((s for s in SECTIONS if canon.startswith(sec_url(s, l))), None)
    swipe = ''.join(f'<a href="{sec_home(s, l)}"{CUR_P if s == _cur else ""}>{e(SEC[l][s][0])}</a>' for s in SECTIONS)
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
<link rel="icon" href="/favicon.ico?v=2" sizes="16x16 32x32 48x48"><link rel="icon" type="image/png" sizes="96x96" href="/assets/icon-96.png?v=2"><link rel="icon" type="image/png" sizes="192x192" href="/assets/icon-192.png?v=2"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png?v=2">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="TWN – World News"><meta name="application-name" content="TWN"><meta name="apple-mobile-web-app-title" content="TWN"><link rel="manifest" href="/manifest.webmanifest"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{SITE}{canon}"><meta property="og:image" content="{SITE}{og_img or '/assets/og-image.jpg'}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="{675 if og_img else 630}"><meta property="og:locale" content="{LOCALE.get(l, l)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{SITE}{og_img or '/assets/og-image.jpg'}">
{extra_head}{ldj}
<link rel="preload" as="image" href="/assets/terra-masthead5-800.webp" imagesrcset="/assets/terra-masthead5-800.webp 800w, /assets/terra-masthead5-1600.webp 1600w" imagesizes="(max-width: 700px) 86vw, 620px" type="image/webp">
<link rel="stylesheet" href="/assets/fonts.css?v={ASSET_V['fonts.css']}">
<link rel="stylesheet" href="/assets/terra.css?v={ASSET_V['terra.css']}">
</head>
<body>
<div class="wrap">
  <div class="top">
    <div class="top-r"><form class="sbox" action="{search_url(l)}" method="get" role="search"><input type="search" name="q" placeholder="{e(SUI[l]['ph'])}" aria-label="{e(SUI[l]['title'])}"><button type="submit" aria-label="{e(SUI[l]['btn'])}"><svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M15.5 15.5 21 21" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg></button></form>
    <nav class="langs" aria-label="{e(u['lang'])}">{langbar}</nav></div>
  </div>
  <header class="mast">
    <p class="brand"><a href="{pre(l)}"><img class="mast-logo" src="/assets/terra-masthead5-800.webp" srcset="/assets/terra-masthead5-800.webp 800w, /assets/terra-masthead5-1600.webp 1600w" sizes="(max-width: 700px) 86vw, 620px" width="800" height="209" alt="TERRA WORLD NEWS" fetchpriority="high"></a></p>
    <div class="edition"><span class="ed-clock" id="edclock"><span class="ed-city">{e(u['clocks'][0][0])}</span> <b data-tz="Europe/Berlin">--:--</b></span><span class="mid">{e(nice_date(date, l)) if date else ''}</span><span class="ed-wx" id="edwx" title="{e(WXT[l])}"></span></div>
  </header>
  <div id="nv-sentinel" aria-hidden="true"></div>
  <nav class="sections nv2" id="mainnav" aria-label="{e(u['home'])}"><div class="nv-bar"><a class="nv-logo" href="{pre(l)}" aria-label="TWN – World News"><img src="/assets/icon-96.png?v=2" width="30" height="30" alt=""><b>TWN</b></a><button type="button" class="nav-tg" aria-expanded="false" aria-controls="navitems"><span class="hb" aria-hidden="true"><i></i><i></i><i></i></span><span class="nav-tl">{ {'bg': 'Меню', 'de': 'Menü', 'en': 'Menu'}.get(l, 'Menu') }</span></button><div class="nav-items" id="navitems">{nav}</div><a class="nv-search" href="{search_url(l)}" aria-label="{e(SUI[l]['title'])}"><svg viewBox="0 0 24 24" width="19" height="19" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M15.5 15.5 21 21" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg></a></div><div class="nv-swipe" aria-label="{e(u['home'])}">{swipe}</div></nav>
  {tick}{ticker2}
  <main id="main">
{body}
  </main>
  <footer>
    <div><a href="{pre(l)}" class="brand-s"><img src="/assets/twn-logo2-480.webp" srcset="/assets/twn-logo2-480.webp 480w, /assets/twn-logo2-960.webp 960w" sizes="240px" width="480" height="133" alt="TWN – TERRA WORLD NEWS" loading="lazy"></a>{e(u['foot'])}<br>{e(u['publisher'])}<br><span class="wxcredit">{e(WXT[l])} · <a href="https://api.met.no/" rel="noopener nofollow" target="_blank">api.met.no</a></span></div>
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
    if im.get('cr'):  # z. B. Standbild aus offiziellem Trailer
        t = im['cr'].get(l) or im['cr'].get('de', '')
        return (e(t) + (f' · <a href="{e(im["page"])}" rel="noopener nofollow" target="_blank">YouTube</a>' if link and im.get('page') else '')) if link else e(t)
    if im.get('own'):  # eigene Grafik der Redaktion (Rubrik Business)
        return e({'bg': 'Графика: TERRA WORLD NEWS (собствена графика по данните от източниците)', 'de': 'Grafik: TERRA WORLD NEWS (eigene Darstellung nach den genannten Quellen)'}.get(l, 'Graphic: TERRA WORLD NEWS (own graphic based on the sources listed)'))
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

# ---- Business: Zahlen, Kennzahlen, Tabellen, Börsen-Laufband
BZ = {'bg': dict(boerse='БОРСА', asof='Данни', explain='Какво означава това за мен?', overview='Пазарите накратко', jump='На тази страница', full='Цялата статия →', nodata='–', desc='Борси, ток и инвестиции – всеки ден с цифри и таблици, обяснени разбираемо: Уолстрийт, Франкфурт, София, енергийната борса IBEX и инвестиции по региони.', noadv='Информацията е само с информативна цел и не е инвестиционен съвет. Цените са към посочения момент; борсите в момента не се обновяват на живо.'),
      'de': dict(boerse='BÖRSE', asof='Datenstand', explain='Was bedeutet das für mich?', overview='Märkte auf einen Blick', jump='Auf dieser Seite', full='Ganzer Artikel →', nodata='–', desc='Börse, Strom und Investitionen – täglich mit Zahlen und Tabellen, verständlich erklärt: Wall Street, Frankfurt, Sofia, die Strombörse IBEX und Investitionen in den Regionen.', noadv='Die Angaben dienen nur der Information und sind keine Anlageberatung. Kurse mit dem genannten Datenstand, keine Echtzeitkurse.'),
      'en': dict(boerse='MARKETS', asof='Data as of', explain='What does this mean for me?', overview='Markets at a glance', jump='On this page', full='Full article →', nodata='–', desc='Stock markets, electricity and investment – daily with figures and tables, clearly explained: Wall Street, Frankfurt, Sofia, the IBEX power exchange and regional investment.', noadv='For information only, not investment advice. Prices as of the time stated, not real-time quotes.')}
def L(x, l):
    return x.get(l) or x.get('de') or next(iter(x.values()), '') if isinstance(x, dict) else ('' if x is None else str(x))
UNITS = {'Pkt.': {'bg': 'пункта', 'en': 'pts'}, 'Mio. EUR': {'bg': 'млн. евро', 'en': 'EUR m'}, 'Mrd. EUR': {'bg': 'млрд. евро', 'en': 'EUR bn'},
         'Mio.': {'bg': 'млн.', 'en': 'm'}, 'Mrd.': {'bg': 'млрд.', 'en': 'bn'}}
def LU(x, l):  # Einheit in der Seitensprache (Daten oft mit deutscher Einheit)
    v = L(x, l); return UNITS.get(v, {}).get(l, v)
def fnum(v, dec, l):
    if v is None: return '–'
    t = f'{abs(v):,.{dec}f}'
    if l == 'de': t = t.replace(',', 'X').replace('.', ',').replace('X', '.')
    elif l == 'bg': t = t.replace(',', ' ').replace('.', ',')
    return ('−' if v < 0 else '') + t
def fchg(v, dec, l):
    if v is None: return '<span class="chg">–</span>'
    cls = 'up' if v > 0 else 'dn' if v < 0 else 'eq'
    ar = '▲' if v > 0 else '▼' if v < 0 else '■'
    return f'<span class="chg {cls}"><span aria-hidden="true">{ar}</span> {"+" if v > 0 else ""}{fnum(v, dec, l)} %</span>'
def biz_kpis(b, l):
    out = ''
    for k in b.get('kpi', []):
        ch = fchg(k['chg'], 2, l) if k.get('chg') is not None else ''
        out += f'<div class="kpi"><span class="kl">{e(L(k["l"], l))}</span><b class="kv">{fnum(k["v"], k.get("dec", 2), l)}</b><span class="ku">{e(LU(k.get("u", ""), l))}</span>{ch}</div>'
    return f'<div class="kpis">{out}</div>' if out else ''
def biz_tables(b, l):
    out = ''
    for t in b.get('tables', []):
        cols = t['cols']
        th = ''.join(f'<th scope="col" class="{"n" if c["k"] != "txt" else ""}">{e(L(c["h"], l))}</th>' for c in cols)
        trs = ''
        for r in t['rows']:
            tds = ''
            for i, (c, v) in enumerate(zip(cols, r)):
                if c['k'] == 'txt': cell = e(L(v, l)) if v is not None else '–'
                elif c['k'] == 'chg': cell = fchg(v, c.get('dec', 2), l)
                else: cell = fnum(v, c.get('dec', 2), l)
                tag = 'th scope="row"' if i == 0 else 'td'
                tds += f'<{tag} class="{"n" if c["k"] != "txt" else ""}">{cell}</{tag.split()[0]}>'
            trs += f'<tr>{tds}</tr>'
        out += f'<div class="tbl-wrap"><table class="biz-t"><caption>{e(L(t["cap"], l))}</caption><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'
    return out
def biz_explain(b, l):
    x = b.get(l, {}).get('explain')
    return f'<aside class="explain"><h3>{e(BZ[l]["explain"])}</h3><p>{e(x)}</p></aside>' if x else ''
def biz_asof(b, l):
    return f'<p class="asof meta">{e(BZ[l]["asof"])}: {e(L(b.get("asof", ""), l))}</p>' if b.get('asof') else ''
def biz_src(b, l):
    xs = [f'<a href="{e(x["u"])}" rel="noopener nofollow" target="_blank">{e(x["n"])}</a>' for x in b.get('src', []) if isinstance(x, dict) and x.get('u')]
    return f'<p class="src">{UI[l]["src"]}: {" · ".join(xs)}</p>' if xs else ''
def biz_block(b, l, au, fig=''):
    body = ''.join(f'<p>{e(x)}</p>' for x in b[l].get('body', []))
    return (f'<section class="biz-block" id="{e(b["id"])}"><h2><a href="{au}">{e(b[l]["t"])}</a></h2>{biz_asof(b, l)}<p class="dek">{e(b[l]["d"])}</p>{fig}{biz_kpis(b, l)}'
            f'<div class="body">{body}</div>{biz_explain(b, l)}{biz_tables(b, l)}{biz_src(b, l)}<p class="sec-more"><a href="{au}">{e(BZ[l]["full"])}</a></p></section>')
def boerse_ticker(d, l):
    if not d: return ''
    xs = [t for b in d.get('blocks', []) for t in b.get('ticker', [])]
    if not xs: return ''
    one = ''.join(f'<span class="bq"><b>{e(L(t["n"], l))}</b> {fnum(t["v"], t.get("dec", 2), l)}{(" " + e(LU(t["u"], l))) if t.get("u") else ""} {fchg(t.get("chg"), 2, l)}</span><span class="sep" aria-hidden="true"></span>' for t in xs)
    _pz = {'bg': 'Пауза', 'de': 'Pause', 'en': 'Pause'}.get(l, 'Pause')
    return (f'<div class="ticker boerse" role="region" aria-label="{BZ[l]["boerse"]}"><span class="k">{BZ[l]["boerse"]}</span>'
            f'<div class="tk-track"><div class="tk-move"><div class="tk-set">{one}</div><div class="tk-set" aria-hidden="true">{one}</div></div></div>'
            f'<button class="tk-pause" type="button" aria-pressed="false" aria-label="{_pz}" title="{_pz}"><span aria-hidden="true"></span></button></div>')

MPU = {
       'welt': {'bg': dict(rev='Светът във видео', news='Новини от света', badge='ВИДЕО', more='Към статията →', rel='Дата', vid='Видео', older='Предишни дни', playb='▶ Пусни видеото'),
              'de': dict(rev='Welt im Video', news='Welt-News', badge='VIDEO', more='Zum Artikel →', rel='Datum', vid='Video', older='Vortage', playb='▶ Video abspielen'),
              'en': dict(rev='World on video', news='World news', badge='VIDEO', more='Read more →', rel='Date', vid='Video', older='Previous days', playb='▶ Play video')},
       'europa': {'bg': dict(rev='Европа във видео', news='Новини от Европа', badge='ВИДЕО', more='Към статията →', rel='Дата', vid='Видео', older='Предишни дни', playb='▶ Пусни видеото'),
              'de': dict(rev='Europa im Video', news='Europa-News', badge='VIDEO', more='Zum Artikel →', rel='Datum', vid='Video', older='Vortage', playb='▶ Video abspielen'),
              'en': dict(rev='Europe on video', news='Europe news', badge='VIDEO', more='Read more →', rel='Date', vid='Video', older='Previous days', playb='▶ Play video')},
       'deutschland': {'bg': dict(rev='Германия във видео', news='Новини от Германия', badge='ВИДЕО', more='Към статията →', rel='Дата', vid='Видео', older='Предишни дни', playb='▶ Пусни видеото'),
              'de': dict(rev='Deutschland im Video', news='Deutschland-News', badge='VIDEO', more='Zum Artikel →', rel='Datum', vid='Video', older='Vortage', playb='▶ Video abspielen'),
              'en': dict(rev='Germany on video', news='Germany news', badge='VIDEO', more='Read more →', rel='Date', vid='Video', older='Previous days', playb='▶ Play video')},
       'bulgarien': {'bg': dict(rev='България във видео', news='Новини от България', badge='ВИДЕО', more='Към статията →', rel='Дата', vid='Видео', older='Предишни дни', playb='▶ Пусни видеото'),
              'de': dict(rev='Bulgarien im Video', news='Bulgarien-News', badge='VIDEO', more='Zum Artikel →', rel='Datum', vid='Video', older='Vortage', playb='▶ Video abspielen'),
              'en': dict(rev='Bulgaria on video', news='Bulgaria news', badge='VIDEO', more='Read more →', rel='Date', vid='Video', older='Previous days', playb='▶ Play video')},
       'klima': {'bg': dict(rev='Климат във видео', news='Новини за климата', badge='ВИДЕО', more='Към статията →', rel='Дата', vid='Видео', older='Предишни дни', playb='▶ Пусни видеото'),
                'de': dict(rev='Klima im Video', news='Klima-News', badge='VIDEO', more='Zum Artikel →', rel='Datum', vid='Video', older='Vortage', playb='▶ Video abspielen'),
                'en': dict(rev='Climate on video', news='Climate news', badge='VIDEO', more='Read more →', rel='Date', vid='Video', older='Previous days', playb='▶ Play video')},
       'leben': {'bg': dict(rev='Живот във видео', news='Живот и ежедневие', badge='ВИДЕО', more='Към статията →', rel='Дата', vid='Видео', older='Предишни дни', playb='▶ Пусни видеото'),
                'de': dict(rev='Leben im Video', news='Leben & Alltag', badge='VIDEO', more='Zum Artikel →', rel='Datum', vid='Video', older='Vortage', playb='▶ Video abspielen'),
                'en': dict(rev='Life on video', news='Everyday life', badge='VIDEO', more='Read more →', rel='Date', vid='Video', older='Previous days', playb='▶ Play video')},
       'wirtschaft': {'bg': dict(rev='Икономика във видео', news='Новини от икономиката', badge='ВИДЕО', more='Към статията →', rel='Дата', vid='Видео', older='Предишни дни', playb='▶ Пусни видеото'),
                     'de': dict(rev='Wirtschaft im Video', news='Wirtschafts-News', badge='VIDEO', more='Zum Artikel →', rel='Datum', vid='Video', older='Vortage', playb='▶ Video abspielen'),
                     'en': dict(rev='Economy on video', news='Economy news', badge='VIDEO', more='Read more →', rel='Date', vid='Video', older='Previous days', playb='▶ Play video')},
       'energie': {'bg': dict(rev='Енергетика във видео', news='Новини от енергетиката', badge='ВИДЕО', more='Към статията →', rel='Дата', vid='Видео', older='Предишни дни', playb='▶ Пусни видеото'),
                   'de': dict(rev='Energie im Video', news='Energie-News', badge='VIDEO', more='Zum Artikel →', rel='Datum', vid='Video', older='Vortage', playb='▶ Video abspielen'),
                   'en': dict(rev='Energy on video', news='Energy news', badge='VIDEO', more='Read more →', rel='Date', vid='Video', older='Previous days', playb='▶ Play video')},
       'ki': {'bg': dict(rev='Технологии във видео', news='Новини', badge='TECH', more='Към статията →', rel='Дата', vid='Видео', older='Още новини', playb='▶ Пусни видеото'),
             'de': dict(rev='Tech-Videos des Tages', news='Tech-News', badge='TECH', more='Zum Artikel →', rel='Datum', vid='Video', older='Weitere Meldungen', playb='▶ Video abspielen'),
             'en': dict(rev="Today's tech videos", news='Tech news', badge='TECH', more='Read more →', rel='Date', vid='Video', older='More stories', playb='▶ Play video')},
       'ai': {'bg': dict(rev='Видео на деня', news='Новини за ИИ', badge='ИИ', more='Към статията →', rel='Дата', vid='Видео', older='Предишни', playb='▶ Пусни видеото'),
             'de': dict(rev='KI-Videos des Tages', news='KI-News', badge='KI', more='Zum Artikel →', rel='Datum', vid='Video', older='Frühere Beiträge', playb='▶ Video abspielen'),
             'en': dict(rev="Today's AI videos", news='AI news', badge='AI', more='Read more →', rel='Date', vid='Video', older='Earlier stories', playb='▶ Play video')},
       'sport': {'bg': dict(rev='Акценти на деня', badge='СПОРТ', more='Към статията →', rel='Дата', vid='Видео', older='Предишни', playb='▶ Пусни видеото'),
                'de': dict(rev='Highlights des Tages', badge='SPORT', more='Zum Artikel →', rel='Datum', vid='Video', older='Frühere Beiträge', playb='▶ Video abspielen'),
                'en': dict(rev="Today's highlights", badge='SPORT', more='Read more →', rel='Date', vid='Video', older='Earlier stories', playb='▶ Play video')},
       'film': {'bg': dict(rev='Трейлъри на деня', badge='ТРЕЙЛЪР', more='Към статията →', rel='Премиера', devl='Режисьор:', vid='Трейлър', older='Предишни трейлъри'),
               'de': dict(rev='Trailer des Tages', badge='TRAILER', more='Zum Artikel →', rel='Kinostart', devl='Regie:', vid='Trailer', older='Frühere Trailer'),
               'en': dict(rev="Today's trailers", badge='TRAILER', more='Read more →', rel='Release', devl='Director:', vid='Trailer', older='Earlier trailers')},
       'musik': {'bg': dict(playb='▶ Пусни видеото', rev='Албуми на деня', badge='АЛБУМ', more='Към ревюто →', rel='Излиза', vid='Видео към сингъла', older='Предишни албуми', single='Сингъл'),
                'de': dict(playb='▶ Video abspielen', rev='Album-Reviews des Tages', badge='ALBUM', more='Zum Review →', rel='Release', vid='Video zur Single', older='Frühere Alben', single='Single'),
                'en': dict(playb='▶ Play video', rev="Today's album reviews", badge='ALBUM', more='Read the review →', rel='Release', vid='Single video', older='Earlier albums', single='Single')}}
GPU = {'bg': dict(rev='Ревюта на деня', news='Новини', older='Предишни ревюта', more='Към ревюто →', badge='РЕВЮ', pf='Платформи', rel='Излиза', dev='Студио', vid='Трейлър', single='Сингъл'),
       'de': dict(rev='Reviews des Tages', news='News', older='Frühere Reviews', more='Zum Review →', badge='REVIEW', pf='Plattformen', rel='Release', dev='Studio', vid='Trailer', single='Single'),
       'en': dict(rev="Today's reviews", news='News', older='Earlier reviews', more='Read the review →', badge='REVIEW', pf='Platforms', rel='Release', dev='Studio', vid='Trailer', single='Single')}
def gp_slogan(l):  # Slogan rechts im Rubrik-Kopf (statt Datum)
    return '<span class="gp-slogan" aria-label="' + '. '.join(SLOGAN[l]) + '.">' + '<i aria-hidden="true"></i>'.join(SLOGAN[l]) + '</span>'
def games_page(l, its, day0, others, SX, kind='games', title=None):
    u = UI[l]; g = dict(GPU[l]); g.update(MPU.get(kind, {}).get(l, {}))
    def cover_style(it):
        im = it.get('img')
        return f' style="background-image:url({im["f"]})"' if im else ''
    def review(it):
        v = it['yt'] if isinstance(it['yt'], dict) else it['yt'][0]
        rv = it.get('rv', {})
        meta = ' · '.join(x for x in [rv.get('pf'), (g['rel'] + ' ' + rv['rel']) if rv.get('rel') else '', ((g['devl'] + ' ' + rv['dev']) if g.get('devl') else rv['dev']) if rv.get('dev') else ''] if x)
        sc = rv.get('score', {}).get(l) if isinstance(rv.get('score'), dict) else rv.get('score')
        im = it.get('img')
        cvl = {'bg': 'Обложка', 'de': 'Albumcover', 'en': 'Album cover'}[l]
        cr = (f'<p class="gr-cr">{credit(im, l, True)}' + (f' · {cvl} {e(it["cover"].get("cr", ""))}' if it.get('cover') else '') + '</p>') if im else ''
        cov = f'<img class="gr-cover" src="{e(it["cover"]["f"])}" alt="{e(it["cover"].get("alt", {}).get(l, ""))}" width="600" height="600" loading="lazy">' if it.get('cover') else ''
        return (f'<article class="gr"><div class="gr-media"><div class="yt gr-yt" data-yt="{e(v["id"])}"{cover_style(it)}><span class="gr-badge">{g["badge"]}</span>{cov}'
                f'<button type="button" class="yt-play">{e(g.get("playb") or u["play"])}</button><span class="yt-note">{e(u["ytnote"])}</span></div>{cr}</div>'
                f'<div class="gr-txt">' + (f'<div class="gr-score">{e(sc)}</div>' if sc else '') +
                f'<a href="{art_url(it, l)}"><h3>{e(it[l]["t"])}</h3></a>' + (f'<p class="gr-meta">{e(meta)}</p>' if meta else '') +
                f'<p class="gr-dek">{e(it[l]["d"])}</p>' + (f'<p class="gr-single">{e(g["single"])}: <b>{e(rv["single"])}</b></p>' if rv.get('single') else '') + f'<p class="gr-yt-src">{e(g["vid"])}: YouTube · {e(v.get("ch", ""))}</p><a class="gr-more" href="{art_url(it, l)}">{e(g["more"])}</a></div></article>')
    def small(it):
        return (f'<article class="gs"><a href="{art_url(it, l)}"><div class="gs-img"{cover_style(it)}>' + ('<span class="rt-play" aria-hidden="true">▶</span>' if it.get('yt') else '') +
                f'</div>{kick(it, l)}<h3>{e(it[l]["t"])}</h3></a></article>')
    today = [it for it in its if it['date'] == day0]
    if kind in ('ai', 'ki'):  # KI / Technologie: 3 Video-Artikel oben, 3 News unten (bevorzugt "mn"), Rest unter „Frühere“
        revs = [it for it in today if it.get('yt')][:4]
        news = ([it for it in today if it.get('mn') and it not in revs] + [it for it in today if not it.get('mn') and it not in revs])[:3]
    elif kind in ('wirtschaft', 'energie', 'leben', 'klima', 'welt', 'europa', 'deutschland', 'bulgarien'):  # Artikel aus den 77: mit Video oben, alle übrigen des Tages als News darunter
        revs = [it for it in today if it.get('yt')][:3]
        news = [it for it in today if it not in revs]
    elif kind == 'games':
        revs = [it for it in today if it.get('yt')]
        news = [it for it in today if not it.get('yt')]
    else:  # Film/Musik: Reviews = Items mit rv, News = Items mit "mn"; alte Entertainment-Meldungen laufen unter „Frühere“
        revs = [it for it in today if it.get('rv') and it.get('yt')]
        news = [it for it in today if it.get('mn') and it not in revs]
    older = [it for it in its if it not in revs and it not in news]
    html = f'<div class="gp gp-{kind}"><div class="gp-head"><h1 class="gp-title">{e(title or SEC[l][kind][0])}</h1>{gp_slogan(l)}</div>'
    html += '<div class="gp-main"><div class="gp-panel">'
    if not its: html += f'<p class="gp-empty">{e(u["empty"])}</p>'
    if revs: html += f'<h2 class="gp-h">▶ {e(g["rev"])}</h2>' + ''.join(review(it) for it in revs)
    if news: html += f'<h2 class="gp-h">{e(g["news"])}</h2><div class="gs-grid">' + ''.join(small(it) for it in news) + '</div>'
    if older: html += f'<h2 class="gp-h">{e(g["older"])}</h2><div class="gs-grid">' + ''.join(small(it) for it in older) + '</div>'
    html += f'</div><aside class="sec-side"><h2 class="list-h">{e(SX["other"])}</h2>{others}</aside></div></div>'
    return html

def media_article(it, l, paras, facts, noadv, rel, side, SX):
    """Artikel-/Review-Seite für Games, Film und Musik im Layout der Rubrikseite."""
    u = UI[l]; kind = it['s']; g = dict(GPU[l]); g.update(MPU.get(kind, {}).get(l, {}))
    T = it[l]; rv = it.get('rv', {}); im = it.get('img')
    sc = rv.get('score', {}).get(l) if isinstance(rv.get('score'), dict) else rv.get('score')
    meta = ' · '.join(x for x in [rv.get('pf'), (g['rel'] + ' ' + rv['rel']) if rv.get('rel') else '', ((g['devl'] + ' ' + rv['dev']) if g.get('devl') else rv['dev']) if rv.get('dev') else ''] if x)
    bg = f' style="background-image:url({im["f"]})"' if im else ''
    cvl = {'bg': 'Обложка', 'de': 'Albumcover', 'en': 'Album cover'}[l]
    cr = (f'<p class="gr-cr">{credit(im, l, True)}' + (f' · {cvl} {e(it["cover"].get("cr", ""))}' if it.get('cover') else '') + '</p>') if im else ''
    if it.get('yt'):
        v = it['yt'] if isinstance(it['yt'], dict) else it['yt'][0]
        cov = f'<img class="gr-cover" src="{e(it["cover"]["f"])}" alt="{e(it["cover"].get("alt", {}).get(l, ""))}" width="600" height="600">' if it.get('cover') else ''
        badge = f'<span class="gr-badge">{g["badge"]}</span>' if rv else ''
        media = (f'<div class="ga-media"><div class="yt gr-yt" data-yt="{e(v["id"])}"{bg}>{badge}{cov}<button type="button" class="yt-play">{e(g.get("playb") or u["play"])}</button>'
                 f'<span class="yt-note">{e(u["ytnote"])}</span></div>{cr}<p class="gr-yt-src">{e(g["vid"])}: YouTube · {e(v.get("ch", ""))} · <a href="https://www.youtube.com/watch?v={e(v["id"])}" rel="noopener nofollow" target="_blank">youtube.com</a></p></div>')
    elif im:
        alt = im.get('alt', {}).get(l, '')
        media = f'<div class="ga-media"><img class="ga-img" src="{im["f"]}" width="{im["w"]}" height="{im["h"]}" alt="{e(alt)}">{cr if im.get("cr") else ""}' + ('' if im.get('cr') else f'<p class="gr-cr">{e(alt)} · {credit(im, l, True)}</p>') + '</div>'
    else:
        media = ''
    def small(x):
        st = f' style="background-image:url({x["img"]["f"]})"' if x.get('img') else ''
        return (f'<article class="gs"><a href="{art_url(x, l)}"><div class="gs-img"{st}>' + ('<span class="rt-play" aria-hidden="true">▶</span>' if x.get('yt') else '') +
                f'</div>{kick(x, l)}<h3>{e(x[l]["t"])}</h3></a></article>')
    single = f'<p class="gr-single">{e(g["single"])}: <b>{e(rv["single"])}</b></p>' if rv.get('single') else ''
    html = (f'<div class="gp gp-{kind} ga"><div class="gp-head"><a class="gp-title ga-sec" href="{sec_home(kind, l, it.get('sub'))}">{e(SEC[l][kind][0])}</a>{gp_slogan(l)}</div>'
            f'<div class="gp-main"><article class="gp-panel ga-panel">{kick(it, l)}' + (f'<div class="gr-score">{e(sc)}</div>' if sc else '') +
            f'<h1 class="ga-h1">{e(T["t"])}</h1>' + (f'<p class="gr-meta">{e(meta)}</p>' if meta else '') + f'<p class="ga-dek">{e(T["d"])}</p>'
            f'<div class="byline meta ga-by"><span>{e(u["by"])}</span><time datetime="{iso(it)}">{PUBL[l]}: {short_date(it["date"], l)}, {it["time"]}{(" " + u["hour"]) if u["hour"] else ""}</time><span>{u["read"].format(m=read_min(it, l))}</span></div>'
            f'{media}{single}<div class="body ga-body">{paras}</div>{facts}{noadv}<div class="sources ga-src"><h2>{e(u["src"])}</h2><ul>{LI(it["src"])}</ul></div>'
            + (f'<h2 class="gp-h">{e(u["more"])}</h2><div class="gs-grid">{"".join(small(x) for x in rel)}</div>' if rel else '') +
            f'<p class="ga-back"><a href="{sec_home(kind, l, it.get('sub'))}">← {e(SEC[l][kind][0])}</a></p></article>'
            f'<aside class="sec-side"><h2 class="list-h">{e(SX["other"])}</h2>{side}</aside></div></div>')
    return html

# ---- Fußball: Ligen, Tabellen, Spieltage, Pokale (Daten: content/football/*.json, openfootball CC0 + Redaktion)
FB = {}
FB_ORDER = ['premier-league', 'bundesliga', 'la-liga', 'ligue-1', 'serie-a', 'parva-liga']
def fb_order(l): return (['parva-liga'] + [k for k in FB_ORDER if k != 'parva-liga']) if l == 'bg' else FB_ORDER
FBU = {'bg': dict(season='Сезон', table='Класиране', next='Предстоящ кръг', done='Изиграни кръгове', md='{n}. кръг', cups='Купи', pos='#', team='Отбор', p='М', w='П', d='Р', l='З', g='Голове', gd='ГР', pts='Т',
                  leagues='Лиги', leader='Лидер', lead_pts='т.', ko='Начален час: българско време', noft='–', pp='отложен', src='Данни', open='Към лигата →', upcoming='Предстои', pens='дузпи', aet='след продълж.', tbd='Предстои жребий', nomatch='Все още няма мачове.'),
       'de': dict(season='Saison', table='Tabelle', next='Nächster Spieltag', done='Abgeschlossene Spieltage', md='{n}. Spieltag', cups='Pokale', pos='Pl.', team='Verein', p='Sp', w='S', d='U', l='N', g='Tore', gd='Diff', pts='Pkt',
                  leagues='Ligen', leader='Tabellenführer', lead_pts='Pkt.', ko='Anstoßzeiten: deutsche Zeit', noft='–', pp='verlegt', src='Daten', open='Zur Liga →', upcoming='Anstehend', pens='i.E.', aet='n.V.', tbd='Auslosung steht aus', nomatch='Noch keine Spiele.'),
       'en': dict(season='Season', table='Table', next='Next matchday', done='Completed matchdays', md='Matchday {n}', cups='Cups', pos='#', team='Club', p='P', w='W', d='D', l='L', g='Goals', gd='GD', pts='Pts',
                  leagues='Leagues', leader='Leader', lead_pts='pts', ko='Kick-off times: Central European Time', noft='–', pp='postponed', src='Data', open='Go to league →', upcoming='Upcoming', pens='pens', aet='a.e.t.', tbd='Draw pending', nomatch='No matches yet.')}
FB_IMG = {}   # key -> img dict (Commons), aus content/football/_images.json

def fb_load():
    FB.clear(); FB_IMG.clear()
    d = os.path.join(HERE, 'content', 'football')
    for k in FB_ORDER:
        fp = os.path.join(d, f'{k}.json')
        if os.path.exists(fp): FB[k] = json.load(open(fp, encoding='utf-8'))
    ip = os.path.join(d, '_images.json')
    if os.path.exists(ip):
        for it in json.load(open(ip, encoding='utf-8')).get('items', []):
            im = it['img']
            if os.path.exists(os.path.join(HERE, 'static', im['f'].lstrip('/'))): FB_IMG[it['id']] = im

def fb_url(k, l): return f"{sub_url('sport', 'fussball', l)}{k}/"

def fb_table(lg):
    t = {}
    for m in lg['matches']:
        for x in (m['t1'], m['t2']): t.setdefault(x, [0, 0, 0, 0, 0, 0, 0])  # Sp S U N T GT Pkt
        if m.get('ft') is None: continue
        a, b = m['ft']
        for team, gf, ga in ((m['t1'], a, b), (m['t2'], b, a)):
            r = t[team]; r[0] += 1; r[4] += gf; r[5] += ga
            if gf > ga: r[1] += 1; r[6] += 3
            elif gf == ga: r[2] += 1; r[6] += 1
            else: r[3] += 1
    return sorted(t.items(), key=lambda kv: (-kv[1][6], -(kv[1][4] - kv[1][5]), -kv[1][4], kv[0]))

def fb_dt(m, lg, l):
    import datetime as _d
    from zoneinfo import ZoneInfo
    try:
        h, mi = (m.get('time') or '00:00').split(':')[:2]
        dt = _d.datetime.fromisoformat(m['date']).replace(hour=int(h), minute=int(mi), tzinfo=ZoneInfo(lg.get('tz', 'Europe/Berlin')))
        loc = dt.astimezone(ZoneInfo('Europe/Sofia' if l == 'bg' else 'Europe/Berlin'))
        wd = WEEKDAYS[l][loc.weekday()][:2 if l != 'en' else 3].capitalize()
        return f'{wd} {loc.day:02d}.{loc.month:02d}.' + (f' {loc.hour:02d}:{loc.minute:02d}' if m.get('time') else '')
    except Exception:
        return '.'.join(reversed(m['date'].split('-')))

def fb_rounds(lg):
    rs = {}
    for m in lg['matches']: rs.setdefault(m['r'], []).append(m)
    return dict(sorted(rs.items()))

def fb_state(lg, today):
    rs = fb_rounds(lg)
    done = [r for r, ms in rs.items() if all(m.get('ft') is not None or m.get('status') == 'postponed' for m in ms) and any(m.get('ft') is not None for m in ms)]
    nxt = next((r for r, ms in rs.items() if any(m.get('ft') is None and m.get('status') != 'postponed' for m in ms)), None)
    return rs, done, nxt

def fb_note(n, l):
    if not n: return ''
    return n.replace('n.V.', FBU[l]['aet']).replace('i.E.', FBU[l]['pens'])

def fb_match_row(m, lg, l, cup=False):
    a, b = (m.get('t1') or m.get('team1')), (m.get('t2') or m.get('team2'))
    ft = m.get('ft')
    sc = f'<b class="fb-sc">{ft[0]}:{ft[1]}</b>' if ft is not None else (f'<span class="fb-sc fb-open fb-pp">{e(FBU[l]["pp"])}</span>' if m.get('status') == 'postponed' else f'<span class="fb-sc fb-open">{e(FBU[l]["noft"])}</span>')
    when = fb_dt(m, lg, l) if not cup else ('.'.join(reversed(m['date'].split('-'))) if re.match(r'^\d{4}-\d{2}-\d{2}$', m.get('date', '')) else e(m.get('date', '')))
    note = f' <span class="fb-note">{e(fb_note(m.get("note"), l))}</span>' if m.get('note') else ''
    return f'<tr><td class="fb-when">{when}</td><td class="fb-t1">{e(a)}</td><td class="fb-scc">{sc}</td><td class="fb-t2">{e(b)}{note}</td></tr>'

def fb_league_card(k, l, today):
    lg = FB[k]; f = FBU[l]
    tab = fb_table(lg); rs, done, nxt = fb_state(lg, today)
    lead = tab[0] if tab and tab[0][1][0] else None
    im = FB_IMG.get(k)
    st = f' style="background-image:url({im["f"]})"' if im else ''
    return (f'<article class="fb-card"><a href="{fb_url(k, l)}"><div class="fb-img"{st}><span class="gr-badge">{e(f["season"])} {e(lg["season"])}</span>'
            f'<span class="fb-name">{e(lg["name"][l])}</span></div>'
            f'<div class="fb-card-txt">' + (f'<p class="fb-lead">{e(f["leader"])}: <b>{e(lead[0])}</b> · {lead[1][6]} {e(f["lead_pts"])}</p>' if lead else '') +
            (f'<p class="gr-meta">{e(f["md"].format(n=done[-1]))} ✓' + (f' · {e(f["next"])}: {e(f["md"].format(n=nxt))}' if nxt else '') + '</p>' if done else '') +
            f'<span class="gr-more">{e(f["open"])}</span></div></a></article>')

def fb_overview(l, today, news_html, others):
    f = FBU[l]; title = f'{SEC[l]["sport"][0]} · {SUB[l]["fussball"][0]}'
    seasons = sorted({FB[k]['season'] for k in FB})
    cards = ''.join(fb_league_card(k, l, today) for k in fb_order(l) if k in FB)
    return (f'<div class="gp gp-sport"><div class="gp-head"><h1 class="gp-title">{e(title)}</h1><span class="gp-date">{e(f["season"])} {e(" / ".join(seasons))}</span></div>'
            f'<div class="gp-main"><div class="gp-panel"><h2 class="gp-h">{e(f["leagues"])}</h2><div class="fb-grid">{cards}</div>{news_html}</div>'
            f'<aside class="sec-side"><h2 class="list-h">{e(UI[l]["more"] if False else {"bg": "Други рубрики", "de": "Aus anderen Ressorts", "en": "From other sections"}[l])}</h2>{others}</aside></div></div>')

def fb_league_page(k, l, today, others):
    lg = FB[k]; f = FBU[l]
    tab = fb_table(lg); rs, done, nxt = fb_state(lg, today)
    rows = ''.join(f'<tr{" class=fb-top" if i < 4 else ""}><td class="n">{i + 1}</td><th scope="row">{e(t)}</th><td class="n">{r[0]}</td><td class="n">{r[1]}</td><td class="n">{r[2]}</td><td class="n">{r[3]}</td><td class="n">{r[4]}:{r[5]}</td><td class="n">{"+" if r[4] - r[5] > 0 else ""}{r[4] - r[5]}</td><td class="n fb-pts">{r[6]}</td></tr>'
                   for i, (t, r) in enumerate(tab))
    table = (f'<div class="tbl-wrap"><table class="fb-t"><thead><tr><th class="n">{f["pos"]}</th><th>{f["team"]}</th><th class="n">{f["p"]}</th><th class="n">{f["w"]}</th><th class="n">{f["d"]}</th><th class="n">{f["l"]}</th><th class="n">{f["g"]}</th><th class="n">{f["gd"]}</th><th class="n">{f["pts"]}</th></tr></thead><tbody>{rows}</tbody></table></div>')
    nx = ''
    if nxt:
        nx = (f'<h2 class="gp-h">{e(f["next"])}: {e(f["md"].format(n=nxt))}</h2><div class="tbl-wrap"><table class="fb-m"><tbody>' +
              ''.join(fb_match_row(m, lg, l) for m in sorted(rs[nxt], key=lambda m: (m['date'], m.get('time', '')))) + f'</tbody></table></div><p class="fb-ko">{e(f["ko"])}</p>')
    dn = ''
    for i, r in enumerate(reversed(done)):
        dn += (f'<details class="fb-md"{" open" if i == 0 else ""}><summary>{e(f["md"].format(n=r))}</summary><div class="tbl-wrap"><table class="fb-m"><tbody>' +
               ''.join(fb_match_row(m, lg, l) for m in sorted(rs[r], key=lambda m: (m['date'], m.get('time', '')))) + '</tbody></table></div></details>')
    cups = ''
    for c in lg.get('cups', []):
        body = ''
        for rd in c.get('rounds', []):
            ms = rd.get('matches', [])
            dt = rd.get('date', '')
            body += (f'<h4 class="fb-rd">{e(rd["name"].get(l, rd["name"].get("en", "")))}' + (f' <span class="fb-rdd">{e(dt)}</span>' if dt else '') + '</h4>' +
                     ((f'<div class="tbl-wrap"><table class="fb-m"><tbody>' + ''.join(fb_match_row(m, lg, l, cup=True) for m in ms) + '</tbody></table></div>') if ms else f'<p class="fb-ko">{e(f["nomatch"])}</p>'))
        csrc = ' · '.join(f'<a href="{e(x)}" rel="noopener nofollow" target="_blank">{e(re.sub(r"^https?://(www\\.)?", "", x).split("/")[0])}</a>' for x in c.get('src', [])[:6])
        cups += f'<details class="fb-md fb-cup"><summary>{e(c["name"].get(l, c["name"].get("en", "")))}</summary>{body}' + (f'<p class="fb-ko">{e(f["src"])}: {csrc}</p>' if csrc else '') + '</details>'
    im = FB_IMG.get(k)
    hero = (f'<div class="ga-media"><div class="fb-hero" style="background-image:url({im["f"]})"><span class="gr-badge">{e(f["season"])} {e(lg["season"])}</span></div>'
            f'<p class="gr-cr">{e(im.get("alt", {}).get(l, ""))} · {credit(im, l, True)}</p></div>') if im else ''
    others_l = ''.join(f'<li><a href="{fb_url(x, l)}"{" aria-current=page" if x == k else ""}>{e(FB[x]["name"][l])}</a></li>' for x in fb_order(l) if x in FB)
    return (f'<div class="gp gp-sport fb-page"><div class="gp-head"><h1 class="gp-title">{e(lg["name"][l])}</h1><span class="fb-season">{e(f["season"])} {e(lg["season"])}</span></div>'
            f'<div class="gp-main"><div class="gp-panel">{hero}<h2 class="gp-h">{e(f["table"])}</h2>{table}{nx}'
            + (f'<h2 class="gp-h">{e(f["cups"])}</h2>{cups}' if cups else '') +
            (f'<h2 class="gp-h">{e(f["done"])}</h2>{dn}' if dn else '') +
            f'<p class="fb-ko">{e(f["src"])}: <a href="{e(lg["src"][0]["u"])}" rel="noopener nofollow" target="_blank">{e(lg["src"][0]["n"])}</a></p></div>'
            f'<aside class="sec-side"><h2 class="list-h">{e(f["leagues"])}</h2><ul class="fb-ll">{others_l}</ul>'
            f'<h2 class="list-h">{e({"bg": "Други рубрики", "de": "Aus anderen Ressorts", "en": "From other sections"}[l])}</h2>{others}</aside></div></div>')

# ---- Boxen: Verbände WBC/WBA/IBF/WBO (Daten: content/boxing/*.json, redaktionell recherchiert)
BX = {}; BX_IMG = {}
BX_ORDER = ['wbc', 'wba', 'ibf', 'wbo']
MM_ORDER = ['ufc', 'pfl', 'one', 'oktagon']
BX_SPORT = {'boxen': BX_ORDER, 'mma': MM_ORDER}
MMU = {'bg': dict(orgs='Организации', champs='Шампиони', champ='Шампион', res='Последни главни мачове', open='Към организацията →'),
       'de': dict(orgs='Organisationen', champs='Champions', champ='Champion', res='Letzte Hauptkämpfe', open='Zur Organisation →'),
       'en': dict(orgs='Promotions', champs='Champions', champ='Champion', res='Recent main events', open='Go to promotion →')}
def bxu(l, sp):
    d = dict(BXU[l])
    if sp == 'mma': d.update(MMU[l]); d['side'] = MMU[l]['orgs']
    return d
BXU = {'bg': dict(orgs='Световни боксови организации', champs='Световни шампиони', div='Категория', champ='Шампион', up='Предстоящи мачове', res='Последни мачове за титли', news='Новини', asof='Към', vac='вакантна', open='Към организацията →', next='Следващ мач', side='Организации', src='Източници'),
       'de': dict(orgs='Weltverbände', champs='Weltmeister', div='Gewichtsklasse', champ='Champion', up='Anstehende Kämpfe', res='Letzte Titelkämpfe', news='News', asof='Stand', vac='vakant', open='Zum Verband →', next='Nächster Kampf', side='Verbände', src='Quellen'),
       'en': dict(orgs='World sanctioning bodies', champs='World champions', div='Division', champ='Champion', up='Upcoming fights', res='Recent title fights', news='News', asof='As of', vac='vacant', open='Go to organisation →', next='Next fight', side='Organisations', src='Sources')}

def bx_load():
    BX.clear(); BX_IMG.clear()
    for dn, order in (('boxing', BX_ORDER), ('mma', MM_ORDER)):
      d = os.path.join(HERE, 'content', dn)
      for k in order:
        fp = os.path.join(d, f'{k}.json')
        if os.path.exists(fp):
            BX[k] = json.load(open(fp, encoding='utf-8')); BX[k].setdefault('sp', 'mma' if dn == 'mma' else 'boxen')
      ip = os.path.join(d, '_images.json')
      if os.path.exists(ip):
        for it in json.load(open(ip, encoding='utf-8')).get('items', []):
            if os.path.exists(os.path.join(HERE, 'static', it['img']['f'].lstrip('/'))): BX_IMG[it['id']] = it['img']

def bx_url(k, l): return f"{sub_url('sport', BX[k].get('sp', 'boxen') if k in BX else 'boxen', l)}{k}/"
def bx_d(s): return '.'.join(reversed(s.split('-'))) if re.match(r'^\d{4}-\d{2}-\d{2}$', s or '') else e(s or '')
def bx_t(x, l): return (x.get(l) or x.get('en') or x.get('de') or '') if isinstance(x, dict) else (x or '')

def bx_card(k, l, today):
    o = BX[k]; f = bxu(l, o.get('sp')); im = BX_IMG.get(k)
    st = f' style="background-image:url({im["f"]})"' if im else ''
    up = sorted([x for x in o.get('upcoming', []) if x.get('date', '') >= today], key=lambda x: x['date'])
    nx = f'<p class="gr-meta">{e(f["next"])}: {bx_d(up[0]["date"])} · {e(up[0]["f1"])} – {e(up[0]["f2"])}</p>' if up else ''
    n = sum(1 for c in o.get('champions', []) if c.get('name'))
    return (f'<article class="fb-card"><a href="{bx_url(k, l)}"><div class="fb-img"{st}><span class="gr-badge">{e(f["asof"])} {bx_d(o.get("asof", ""))}</span><span class="fb-name">{e(bx_t(o["name"], l))}</span></div>'
            f'<div class="fb-card-txt"><p class="fb-lead"><b>{e(bx_t(o["full"], l))}</b> · {n} {e(f["champs"])}</p>{nx}<span class="gr-more">{e(f["open"])}</span></div></a></article>')

def bx_news_grid(items, l):
    def small(x):
        st = f' style="background-image:url({x["img"]["f"]})"' if x.get('img') else ''
        pl = '<span class="rt-play" aria-hidden="true">▶</span>' if x.get('yt') else ''
        return f'<article class="gs"><a href="{art_url(x, l)}"><div class="gs-img"{st}>{pl}</div>{kick(x, l)}<h3>{e(x[l]["t"])}</h3></a></article>'
    return f'<div class="gs-grid">{"".join(small(x) for x in items)}</div>' if items else ''

def bx_overview(l, today, news, others, sp='boxen'):
    f = bxu(l, sp); title = f'{SEC[l]["sport"][0]} · {SUB[l][sp][0]}'
    cards = ''.join(bx_card(k, l, today) for k in BX_SPORT[sp] if k in BX)
    fj = [x for x in news if x.get('fj')]
    rest = [x for x in news if not x.get('fj')]
    fjh = ''
    if fj:
        import datetime as _d
        dd = (_d.date(2026, 12, 11) - _d.date.fromisoformat(today)).days
        cd = {'bg': f'още {dd} дни', 'de': f'noch {dd} Tage', 'en': f'{dd} days to go'}[l] if dd > 0 else ''
        fjh = (f'<section class="bx-fj"><h2 class="gp-h">Fury vs. Joshua <span class="fb-rdd">{e({"bg": "11.12.2026 · Кардиф", "de": "11.12.2026 · Cardiff", "en": "11 Dec 2026 · Cardiff"}[l])}</span>'
               + (f' <span class="bx-cd">{e(cd)}</span>' if cd else '') + f'</h2>{bx_news_grid(fj[:6], l)}</section>')
    nh = fjh + (f'<h2 class="gp-h">{e(f["news"])}</h2>{bx_news_grid(rest[:9], l)}' if rest else '')
    return (f'<div class="gp gp-sport"><div class="gp-head"><h1 class="gp-title">{e(title)}</h1>{gp_slogan(l)}</div>'
            f'<div class="gp-main"><div class="gp-panel"><h2 class="gp-h">{e(f["orgs"])}</h2><div class="fb-grid bx-grid">{cards}</div>{nh}</div>'
            f'<aside class="sec-side"><h2 class="list-h">{e({"bg": "Други рубрики", "de": "Aus anderen Ressorts", "en": "From other sections"}[l])}</h2>{others}</aside></div></div>')

def bx_fight_rows(xs, l, res=False):
    out = ''
    for x in xs:
        mid = f'<span class="bx-res">{e(bx_t(x.get("res"), l))}</span>' if res else '<span class="bx-vs">vs.</span>'
        sub = ' · '.join(y for y in [bx_t(x.get('div'), l), bx_t(x.get('title'), l), x.get('place', '')] if y)
        nt = f'<div class="bx-note">{e(x["note"])}</div>' if x.get('note') and l == 'de' else ''
        out += (f'<div class="bx-fight"><div class="bx-date">{bx_d(x.get("date"))}</div><div class="bx-main"><div class="bx-names"><b>{e(x["f1"])}</b> {mid} <b>{e(x["f2"])}</b></div>'
                f'<div class="bx-sub">{e(sub)}</div>{nt}</div></div>')
    return out

def bx_org_page(k, l, today, news, others):
    o = BX[k]; f = bxu(l, o.get('sp')); im = BX_IMG.get(k)
    rows = ''
    for c in o.get('champions', []):
        nm = e(c['name']) if c.get('name') else f'<i class="bx-vac">{e(f["vac"])}</i>'
        extra = ' · '.join(y for y in [c.get('country', '') if l == 'de' else '', bx_t(c.get('note'), l)] if y)
        lim = f'<div class="bx-lim">{e(c.get("limit", ""))}</div>' if l == 'de' and c.get('limit') else ''
        rows += f'<tr><th scope="row">{e(bx_t(c["div"], l))}{lim}</th><td><b class="bx-champ">{nm}</b>' + (f'<div class="bx-lim">{e(extra)}</div>' if extra else '') + '</td></tr>'
    table = f'<div class="tbl-wrap"><table class="fb-t bx-t"><thead><tr><th>{e(f["div"])}</th><th>{e(f["champ"])}</th></tr></thead><tbody>{rows}</tbody></table></div>'
    up = sorted([x for x in o.get('upcoming', []) if x.get('date', '') >= today], key=lambda x: x['date'])
    rs = sorted(o.get('results', []), key=lambda x: x.get('date', ''), reverse=True)
    hero = (f'<div class="ga-media"><div class="fb-hero" style="background-image:url({im["f"]})"><span class="gr-badge">{e(f["asof"])} {bx_d(o.get("asof", ""))}</span></div>'
            f'<p class="gr-cr">{e(im.get("alt", {}).get(l, ""))} · {credit(im, l, True)}</p></div>') if im else ''
    srcs = ''.join(f'<li><a href="{e(s["u"])}" rel="noopener nofollow" target="_blank">{e(s["n"])}</a></li>' for s in o.get('src', []))
    side = ''.join(f'<li><a href="{bx_url(x, l)}"{" aria-current=page" if x == k else ""}>{e(bx_t(BX[x]["name"], l))} <small>{e(bx_t(BX[x]["full"], l))}</small></a></li>' for x in BX_SPORT[o.get('sp', 'boxen')] if x in BX)
    return (f'<div class="gp gp-sport fb-page"><div class="gp-head"><h1 class="gp-title">{e(bx_t(o["name"], l))}</h1><span class="fb-season">{e(bx_t(o["full"], l))}</span></div>'
            f'<div class="gp-main"><div class="gp-panel">{hero}'
            + (f'<h2 class="gp-h">{e(f["up"])}</h2>{bx_fight_rows(up, l)}' if up else '')
            + (f'<h2 class="gp-h">{e(f["news"])}</h2>{bx_news_grid(news, l)}' if news else '')
            + f'<h2 class="gp-h">{e(f["champs"])} <span class="fb-rdd">{e(f["asof"])} {bx_d(o.get("asof", ""))}</span></h2>{table}'
            + (f'<h2 class="gp-h">{e(f["res"])}</h2>{bx_fight_rows(rs, l, True)}' if rs else '')
            + f'<div class="sources ga-src"><h2>{e(f["src"])}</h2><ul>{srcs}</ul></div></div>'
            f'<aside class="sec-side"><h2 class="list-h">{e(f["side"])}</h2><ul class="fb-ll">{side}</ul>'
            f'<h2 class="list-h">{e({"bg": "Други рубрики", "de": "Aus anderen Ressorts", "en": "From other sections"}[l])}</h2>{others}</aside></div></div>')

ORG = {"@type": "NewsMediaOrganization", "@id": SITE + "/#org", "name": "TERRA WORLD NEWS", "alternateName": ["Terra World News", "TWN", "TWN – World News", "TWN World News"], "description": "Terra World News (TWN) is an independent online news portal publishing daily news from around the world in Bulgarian, German and English.", "foundingDate": "2026", "url": SITE + "/",
       "logo": {"@type": "ImageObject", "url": SITE + "/assets/logo.png", "width": 600, "height": 600},
       "parentOrganization": {"@type": "Organization", "name": "FILMPARTNER 24 EOOD", "legalName": "„ФИЛМПАРТНЕР 24“ ЕООД", "url": "https://filmpartner24.com/", "vatID": "BG208477411"},
       "founder": {"@type": "Person", "name": "Nedy John Cross", "url": "https://nedyjcross.com/"},
       "publishingPrinciples": SITE + "/redaktsionni-printsipi.html", "correctionsPolicy": SITE + "/redaktsionni-printsipi.html#korekcii",
       "email": "media@filmpartner24.com", "areaServed": "Worldwide", "knowsLanguage": ["bg", "de", "en"]}

TICKER = {}
GTRL = {'bg': 'Трейлъри към ревютата', 'de': 'Trailer zu den Reviews', 'en': 'Review trailers'}
KEEP_DAYS = {'welt': 3, 'europa': 3, 'deutschland': 3, 'bulgarien': 3, 'klima': 5, 'leben': 5, 'wirtschaft': 5, 'energie': 5, 'ki': 5, 'ai': 5, 'games': 5, 'film': 5, 'musik': 5, 'sport': 5}   # Rubrikseite zeigt nur die letzten N Ausgabetage
ALL_L = {'bg': 'Всички', 'de': 'Alle', 'en': 'All'}
WXT = {'bg': 'Времето: MET Norway (CC BY 4.0)', 'de': 'Wetterdaten: MET Norway (CC BY 4.0)', 'en': 'Weather data: MET Norway (CC BY 4.0)'}
BIZ = {}   # Datum -> Business-Datei
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
SEC_CODE = {k: chr(97 + i) for i, k in enumerate(['welt', 'europa', 'deutschland', 'bulgarien', 'usa', 'ki', 'wirtschaft', 'klima', 'kultur', 'leben', 'business', 'games', 'film', 'musik', 'sport', 'energie', 'ai'])}
SEC_DESC = {'klima': {'bg': 'Климатът на Земята: затопляне, екстремно време и природни бедствия, свързани с климатичните промени – всеки ден, с видео.',
                     'de': 'Das Klima unserer Erde: Erwärmung, Extremwetter und Naturkatastrophen im Klimawandel – täglich, mit Video.',
                     'en': "Our planet's climate: warming, extreme weather and climate-driven disasters – daily, with video."},
            'leben': {'bg': 'Какво движи живота ти: пари, жилище, работа, пътувания, дигитална сигурност и климат – разбираемо обяснени. Плюс всеки ден най-красивата природа на света във видео.',
                      'de': 'Was dein Leben bewegt: Geld, Wohnen, Arbeit, Reisen, digitale Sicherheit und Klima – verständlich erklärt. Dazu täglich die schönste Natur der Welt im Video.',
                      'en': "What moves your life: money, housing, work, travel, digital safety and climate – clearly explained. Plus the world's most beautiful nature on video every day."}}
NOADV = {'bg': 'Тази статия има информационен характер и не представлява правна, данъчна, финансова или медицинска консултация. Данните са към посочената дата.',
         'de': 'Dieser Beitrag dient der Information und ist keine Rechts-, Steuer-, Finanz- oder medizinische Beratung. Angaben mit dem genannten Datenstand.',
         'en': 'This article is for information only and is not legal, tax, financial or medical advice. Figures as of the date stated.'}
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
    fb_load(); bx_load()
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
        lead = next((it for it in today if it.get('lead')), next((it for it in today if it['s'] != 'business'), today[0]))
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
        ranked = ''.join(f'<div class="rank"><span class="n">{i + 1}</span>{rthumb(it)}<a href="{art_url(it, l)}">{kick(it, l)}<h3>{e(it[l]["t"])}</h3></a></div>' for i, it in enumerate([x for x in rest if x['s'] != 'business'][:5]))  # Business-Berichte nie unter „Neueste Meldungen“
        order = ['bulgarien', 'deutschland', 'welt', 'europa', 'wirtschaft', 'business', 'klima', 'ki', 'ai', 'energie', 'film', 'musik', 'sport', 'games'] if l == 'bg' else ['welt', 'europa', 'deutschland', 'bulgarien', 'wirtschaft', 'business', 'klima', 'ki', 'ai', 'energie', 'film', 'musik', 'sport', 'games'] if l == 'en' else ['deutschland', 'bulgarien', 'welt', 'europa', 'wirtschaft', 'business', 'klima', 'ki', 'ai', 'energie', 'film', 'musik', 'sport', 'games']
        lv = sorted([it for it in items_l if it['s'] == 'leben'], key=lambda x: (x['date'], x['time']), reverse=True)[:4]
        def mrail(s2, lst, desc=''):  # Mix: farbiger Rubrik-Kopf wie im Games-Layout, Karten hell darunter
            return (f'<section class="rail mrail" style="--c:{SEC_COLOR[s2]}"><div class="gp gp-{s2} mr-head"><div class="gp-head"><h2 class="gp-title"><a href="{sec_home(s2, l)}">{e(SEC[l][s2][0])}</a></h2>'
                    f'<a class="mr-all" href="{sec_home(s2, l)}">{e(u["all"])}</a></div></div>' + (f'<p class="sec-desc">{e(desc)}</p>' if desc else '') +
                    f'<div class="cards">{"".join(card(it, l) for it in lst)}</div></section>')
        rails = mrail('leben', lv, SEC_DESC['leben'][l]) if lv else ''
        for s in order:
            its = [it for it in rest if it['s'] == s]
            if its:
                rails += mrail(s, its[:4])
        _vids = [it for it in sorted(items_l, key=lambda x: (x['date'], x['time']), reverse=True) if it.get('yt') and it['s'] != 'business' and it['date'] >= (rest[-1]['date'] if rest else latest['date'])][:24]
        _seen, vsel = set(), []
        for it in _vids:  # höchstens 2 Videos pro Rubrik, damit das Band gemischt bleibt
            if sum(1 for x in vsel if x['s'] == it['s']) < 2: vsel.append(it)
            if len(vsel) == 6: break
        def vtile(it):
            st = f' style="background-image:url({it["img"]["f"]})"' if it.get('img') else ''
            return (f'<article class="gs"><a href="{art_url(it, l)}"><div class="gs-img"{st}><span class="rt-play" aria-hidden="true">▶</span></div>'
                    f'{kick(it, l)}<h3>{e(it[l]["t"])}</h3></a></article>')
        VBT = {'bg': 'Видео на деня', 'de': 'Videos des Tages', 'en': 'Videos of the day'}
        vband = (f'<section class="vband gp gp-home"><div class="gp-head"><h2 class="gp-title">▶ {e(VBT[l])}</h2>{gp_slogan(l)}</div>'
                 f'<div class="gp-panel vb-panel"><div class="gs-grid">{"".join(vtile(it) for it in vsel)}</div></div></section>') if len(vsel) >= 3 else ''
        cur = [it for it in today if it.get('live')]
        if l == 'bg': cur = sorted(cur, key=lambda x: x['s'] != 'bulgarien')
        cur = cur[:8]
        bkh = ''
        if cur:
            last = cur[0]['time']
            bkh = (f'<section class="breaking" aria-label="{e(u["brk"])}"><div class="bk-h"><h2><i class="dot" aria-hidden="true"></i>{e(u["brk"])}</h2>'
                   f'<p class="bk-slogan" aria-label="{". ".join(SLOGAN[l])}.">{"<i aria-hidden=\"true\"></i>".join(SLOGAN[l])}</p>'
                   f'<span class="meta">{u["brkup"]} {last}{(" " + u["hour"]) if u["hour"] else ""}</span></div>'
                   f'<div class="cards">{"".join(card(it, l) for it in cur)}</div></section>')
        body = bkh + (f'<section class="lead"><div class="lead-main"><a href="{art_url(lead, l)}">{plate(lead, l, eager=True)}</a>{kick(lead, l, e(u["lead"]) + " · ")}'
                f'<a href="{art_url(lead, l)}"><h1>{e(lead[l]["t"])}</h1></a><p class="dek">{e(lead[l]["d"])}</p><span class="src">{u["src"]}: {e(SNAMES(lead["src"]))}</span></div>'
                f'<div class="ranked"><h2 class="rh">{e(u["most"])}</h2>{ranked}</div></section>{vband}{rails}')
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
            if s in KEEP_DAYS:  # z. B. Games: nur die letzten 5 Ausgabetage auf der Rubrikseite (Artikel bleiben über Suche/Archiv erreichbar)
                _keep = sorted({it['date'] for it in its}, reverse=True)[:KEEP_DAYS[s]]
                its = [it for it in its if it['date'] in _keep]
            salts = {x: sec_url(s, x) for x in act}
            def _others(s):
                o = ''
                for s2 in SECTIONS:
                    if s2 == s: continue
                    ox = sorted([it for it in items_l if it['s'] == s2], key=lambda x: (x['date'], x['time']), reverse=True)[:3]
                    if ox: o += f'<div class="side-sec" style="--c:{SEC_COLOR[s2]}"><h3><a href="{sec_home(s2, l)}">{e(SEC[l][s2][0])}</a></h3><ul>{"".join(mini(it) for it in ox)}</ul></div>'
                return o
            if not its and s in MEDIA:
                body = games_page(l, [], latest['date'], _others(s), SX, s)
            elif not its:
                body = f'<section class="rail" style="--c:{SEC_COLOR[s]}"><div class="rail-h"><h1 class="sec-title">{e(SEC[l][s][0])}</h1></div>' + (f'<p class="sec-desc">{e(SEC_DESC[s][l])}</p>' if s in SEC_DESC else '') + f'<p class="note">{e(u["empty"])}</p></section>'
            else:
                day0 = its[0]['date']
                today_s = [it for it in its if it['date'] == day0]
                if s == 'leben': today_s = [it for it in today_s if not it.get('nat')] or [it for it in its if not it.get('nat')][:5] or today_s  # Natur: Aufmacher = Klima-Thema, Naturvideos im eigenen Block
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
                if s == 'business':
                    bd = BIZ.get(day0) or {}
                    blocks = [b for b in bd.get('blocks', []) if l in b]
                    kp = ''.join(f'<li><a href="#{e(b["id"])}">{e(b[l]["t"])}</a></li>' for b in blocks)
                    bl = ''
                    for b in blocks:
                        bit = next((x for x in its if x['id'] == b['id'] and x['date'] == day0), None)
                        bl += biz_block(b, l, art_url(bit, l) if bit else '#', (f'<a href="{art_url(bit, l)}" class="biz-fig">' + plate(bit, l) + '</a>') if bit and bit.get('img') else '')
                    if blocks:
                        def _tile(b):
                            k = (b.get('kpi') or [None])[0]
                            kv = (f'<span class="bt-l">{e(L(k["l"], l))}</span><b class="bt-v">{fnum(k["v"], k.get("dec", 2), l)} <small>{e(LU(k.get("u", ""), l))}</small></b>'
                                  + (fchg(k["chg"], 2, l) if k.get("chg") is not None else '')) if k else ''
                            return f'<a class="bz-tile" href="#{e(b["id"])}">{kv}<span class="bt-t">{e(b[l]["t"])}</span></a>'
                        head = (f'<div class="gp gp-business bz-top"><div class="gp-head"><h1 class="gp-title">{e(SEC[l][s][0])}</h1>{gp_slogan(l)}</div>'
                                f'<div class="gp-panel bz-panel"><p class="bz-desc">{e(BZ[l]["desc"])} <span class="bz-date">{e(BZ[l]["asof"])}: {e(nice_date(day0, l))}</span></p>'
                                f'<h2 class="gp-h">{e(BZ[l]["overview"])}</h2><nav class="bz-tiles" aria-label="{e(BZ[l]["jump"])}">{"".join(_tile(b) for b in blocks)}</nav></div></div>'
                                f'<div class="biz-blocks">{bl}</div><p class="noadv">{e(BZ[l]["noadv"])}</p>')
                        tops = [x for x in its if x['date'] == day0]
                if s == 'leben':  # Natur: oben "Die schönste Natur der Welt" (mit Video), darunter Klima-Themen
                    nat = sorted([it for it in its if it.get('nat')], key=lambda x: (x['date'], x['time']), reverse=True)[:6]
                    if nat: head = head.replace('<section class="sec-top">', f'<section class="trl-day nat-day"><h2 class="trl-h">▶ {e(u["nat"])}</h2><div class="cards">{"".join(card(it, l) for it in nat)}</div></section><section class="sec-top">', 1)
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
                    if o: others += f'<div class="side-sec" style="--c:{SEC_COLOR[s2]}"><h3><a href="{sec_home(s2, l)}">{e(SEC[l][s2][0])}</a></h3><ul>{"".join(mini(it) for it in o)}</ul></div>'
                pages = [older[i:i + PER] for i in range(0, len(older), PER)]
                def purl(n): return sec_url(s, l) + (f'{"stranitsa" if l == "bg" else "seite" if l == "de" else "page"}-{n}/' if n > 1 else '')
                more = f'<p class="sec-more"><a href="{purl(2)}">{e(SX["older"])} →</a></p>' if pages else ''
                body = (f'<div class="sec-page" style="--c:{SEC_COLOR[s]}">{head}{extra}<div class="sec-main"><div class="sec-list"><h2 class="list-h">{e(SX["latest"])}</h2>{daylist(front)}{more}</div>'
                        f'<aside class="sec-side"><h2 class="list-h">{e(SX["other"])}</h2>{others}</aside></div></div>')
                if s in MEDIA:
                    body = games_page(l, its, day0, others, SX, s)
                    pages = []
                for n, pit in enumerate(pages, start=2):
                    nav = f'<nav class="pager"><a href="{purl(n - 1)}">{e(SX["prev"])}</a><span>{e(SX["page"])} {n} / {len(pages) + 1}</span>' + (f'<a href="{purl(n + 1)}">{e(SX["next"])}</a>' if n <= len(pages) else '<span></span>') + '</nav>'
                    pb = (f'<div class="sec-page" style="--c:{SEC_COLOR[s]}"><div class="rail-h sec-head"><h1 class="sec-title">{e(SEC[l][s][0])} · {e(SX["arch"])}</h1><span class="meta">{e(SX["page"])} {n}</span></div>'
                          f'<div class="sec-list wide">{daylist(pit)}</div>{nav}</div>')
                    write(purl(n), page(l, act, f'{SEC[l][s][0]} – {SX["page"]} {n} | TWN – World News', f'{SEC[l][s][0]}: {u["desc_home"]}', purl(n), pb, None, {"@context": "https://schema.org", "@graph": [ORG, {"@type": "CollectionPage", "name": f'{SEC[l][s][0]} {n}', "url": SITE + purl(n), "inLanguage": l}]}, issue=latest.get('issue', 1), date=latest['date']))
            if s in SUBS:
                tabs = lambda cur: (f'<nav class="subnav" aria-label="{e(SEC[l][s][0])}">'
                                    + ''.join(f'<a href="{sub_url(s, k, l)}"{CUR_P if cur == k else ""}>{e(SUB[l][k][0])}</a>' for k in SUBS[s]) + '</nav>')
                for k in SUBS[s]:
                    sits = [it for it in its if it.get('sub') == k]
                    su = sub_url(s, k, l); title = f'{SEC[l][s][0]} · {SUB[l][k][0]}'
                    if s == 'sport' and k == 'fussball' and FB:
                        nh = games_page(l, sits, sits[0]['date'], '', SX, s) if sits else ''
                        nh = nh.split('<div class="gp-panel">', 1)[1].split('</div><aside', 1)[0] if nh else ''
                        sb = tabs(k) + fb_overview(l, latest['date'], nh, _others(s))
                        for fk in FB_ORDER:
                            if fk not in FB: continue
                            fu = fb_url(fk, l); ft = f'{FB[fk]["name"][l]} {FB[fk]["season"]} | TWN – World News'
                            falts = {x: fb_url(fk, x) for x in act}
                            write(fu, page(l, act, ft, f'{FB[fk]["name"][l]} {FB[fk]["season"]}: {FBU[l]["table"]}, {FBU[l]["next"]}, {FBU[l]["done"]}', fu, tabs(k) + fb_league_page(fk, l, latest['date'], _others(s)), falts,
                                           {"@context": "https://schema.org", "@graph": [ORG, {"@type": "CollectionPage", "name": FB[fk]["name"][l], "url": SITE + fu, "inLanguage": l}]}, issue=latest.get('issue', 1), date=latest['date']))
                            urls.append((fu, falts, latest['date']))
                    elif s == 'sport' and k in BX_SPORT and any(x in BX for x in BX_SPORT[k]):
                        bn = sorted(sits, key=lambda x: (x['date'], x['time']), reverse=True)
                        sb = tabs(k) + bx_overview(l, latest['date'], bn, _others(s), k)
                        for bk in BX_SPORT[k]:
                            if bk not in BX: continue
                            bu = bx_url(bk, l); bt = f'{bx_t(BX[bk]["name"], l)} – {bx_t(BX[bk]["full"], l)} | TWN – World News'
                            balts = {x: bx_url(bk, x) for x in act}
                            bnews = [x for x in bn if bk in (x.get('org') or [])][:6]
                            write(bu, page(l, act, bt, f'{bx_t(BX[bk]["full"], l)}: {bxu(l, k)["champs"]}, {bxu(l, k)["up"]}, {bxu(l, k)["res"]}', bu, tabs(k) + bx_org_page(bk, l, latest['date'], bnews, _others(s)), balts,
                                           {"@context": "https://schema.org", "@graph": [ORG, {"@type": "CollectionPage", "name": bx_t(BX[bk]["full"], l), "url": SITE + bu, "inLanguage": l}]}, issue=latest.get('issue', 1), date=latest['date']))
                            urls.append((bu, balts, latest['date']))
                    elif s in MEDIA:
                        sb = tabs(k) + games_page(l, sits, sits[0]['date'] if sits else latest['date'], _others(s), SX, s, title=title)
                    else:
                        sb = (f'{tabs(k)}<div class="sec-page" style="--c:{SEC_COLOR[s]}"><div class="rail-h sec-head"><h1 class="sec-title">{e(title)}</h1><span class="meta">{len(sits)} {u["items"]}</span></div>'
                              + (f'<div class="sec-list wide">{daylist(sits[:120])}</div>' if sits else f'<p class="note">{e(u["empty"])}</p>') + '</div>')
                    subalts = {x: sub_url(s, k, x) for x in act}
                    write(su, page(l, act, f'{title} | TWN – World News', f'{title}: {u["desc_home"]}', su, sb, subalts, {"@context": "https://schema.org", "@graph": [ORG, {"@type": "CollectionPage", "name": title, "url": SITE + su, "inLanguage": l}]}, issue=latest.get('issue', 1), date=latest['date']))
                    urls.append((su, subalts, latest['date']))
            if s in SUBS:  # keine eigene Übersichtsseite: Weiterleitung auf die erste Unterrubrik (zusätzlich 301 in _redirects)
                _h = sec_home(s, l)
                write(sec_url(s, l), f'<!doctype html><html lang="{l}"><head><meta charset="utf-8"><meta name="robots" content="noindex"><link rel="canonical" href="{SITE}{_h}"><meta http-equiv="refresh" content="0; url={_h}"><title>{e(SEC[l][s][0])}</title></head><body><a href="{_h}">{e(SEC[l][s][0])}</a></body></html>')
                continue
            write(sec_url(s, l), page(l, act, f'{SEC[l][s][0]} | TWN – World News', (BZ[l]['desc'] if s == 'business' else f'{SEC[l][s][0]}: {u["desc_home"]}'), sec_url(s, l), body, salts, {"@context": "https://schema.org", "@graph": [ORG, {"@type": "CollectionPage", "name": SEC[l][s][0], "url": SITE + sec_url(s, l), "inLanguage": l}]}, issue=latest.get('issue', 1), date=latest['date'],
                  ticker2=(boerse_ticker(BIZ[max(BIZ)], l) if s == 'business' and BIZ else '')))
            urls.append((sec_url(s, l), salts, latest['date']))
        # ---- articles
        MSIDE = {}
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
            noadv = f'<p class="noadv">{e(NOADV[l])}</p>' if it['s'] == 'leben' and not it.get('_kl') else f'<p class="noadv">{e(BZ[l]["noadv"])}</p>' if it.get('biz') else ''
            if it.get('biz'):
                _bz = it['biz']
                paras = biz_asof(_bz, l) + biz_kpis(_bz, l) + paras + biz_explain(_bz, l) + biz_tables(_bz, l)
            facts = f'<aside class="facts"><h2>{e(u["facts"])}</h2><ul>{LI(T["facts"])}</ul></aside>' if T.get('facts') else ''
            rel = [x for x in items_l if x['s'] == it['s'] and x is not it][:3]
            relh = f'<section class="rail" style="--c:{SEC_COLOR[it["s"]]}"><div class="rail-h"><h2>{e(u["more"])}</h2><a href="{sec_home(it["s"], l, it.get('sub'))}">{e(SEC[l][it["s"]][0])} →</a></div><div class="cards">{"".join(card(x, l) for x in rel)}</div></section>' if rel else ''
            body = (f'<article class="article"><a class="back" href="{sec_home(it["s"], l, it.get('sub'))}">← {e(SEC[l][it["s"]][0])}</a>{kick(it, l)}<h1>{e(T["t"])}</h1><p class="dek">{e(T["d"])}</p>'
                    f'<div class="byline meta"><span>{e(u["by"])}</span><time datetime="{iso(it)}">{PUBL[l]}: {short_date(it["date"], l)}, {it["time"]}{(" " + u["hour"]) if u["hour"] else ""}</time><span>{u["read"].format(m=read_min(it, l))}</span></div>'
                    f'{plate(it, l, cap=True, eager=True)}<div class="body">{paras}</div>{trailer}{facts}{noadv}<div class="sources"><h2>{e(u["src"])}</h2><ul>{LI(it["src"])}</ul></div></article>{relh}')
            if it['s'] in MEDIA:  # Games/Film/Musik: Artikel im dunklen Medien-Layout mit Seitenleiste
                if it['s'] not in MSIDE:
                    MSIDE[it['s']] = ''.join(f'<div class="side-sec" style="--c:{SEC_COLOR[s2]}"><h3><a href="{sec_home(s2, l)}">{e(SEC[l][s2][0])}</a></h3><ul>{"".join(mini(x) for x in sorted([x for x in items_l if x["s"] == s2], key=lambda x: (x["date"], x["time"]), reverse=True)[:3])}</ul></div>'
                                             for s2 in SECTIONS if s2 != it['s'] and any(x['s'] == s2 for x in items_l))
                body = media_article(it, l, paras, facts, noadv, [x for x in items_l if x['s'] == it['s'] and x is not it and x['date'] >= it['date']][:3] or rel, MSIDE[it['s']], SX)
            aalts = {x: art_url(it, x) for x in act if x in it}
            ld = {"@context": "https://schema.org", "@graph": [ORG, {"@type": "NewsArticle", "@id": SITE + art_url(it, l) + "#article", "mainEntityOfPage": SITE + art_url(it, l), "headline": T['t'][:110], "description": T['d'],
                  "datePublished": iso(it), "dateModified": iso(it), "inLanguage": l, "articleSection": SEC[l][it['s']][0], "isAccessibleForFree": True,
                  "image": [SITE + (it["img"]["f"] if it.get("img") else "/assets/og-image.jpg")], "author": {"@type": "Organization", "name": u['by'], "url": SITE + legal_url('principles', l)}, "publisher": {"@id": SITE + "/#org"},
                  "citation": CIT(it['src'])},
                  {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": u['home'], "item": SITE + pre(l)}, {"@type": "ListItem", "position": 2, "name": SEC[l][it['s']][0], "item": SITE + sec_home(it['s'], l, it.get('sub'))}, {"@type": "ListItem", "position": 3, "name": T['t']}]}]}
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
