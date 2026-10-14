"""Neue/geänderte URLs an Suchmaschinen melden.
1) Bing URL Submission API (Bing Webmaster Tools, Secret BING_API_KEY) – Hauptweg für Bing/DuckDuckGo/Yahoo.
   Neueste Artikel zuerst (news-sitemap.xml), danach heute geänderte Rubrikseiten (sitemap.xml);
   bereits gemeldete URLs stehen in ~/.cache/twn/bing-submitted.txt (per actions/cache zwischen Läufen erhalten),
   damit das Tageskontingent nicht mit Wiederholungen verbraucht wird.
2) IndexNow (Yandex, Seznam, Naver …) wie bisher."""
import json, os, sys, urllib.request, urllib.error, urllib.parse, xml.etree.ElementTree as ET, datetime
from zoneinfo import ZoneInfo

KEY = '2049bbf38319833cc271f38180251969'
HOST = 'terraworldnews.com'
SITE = f'https://{HOST}'
NS = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
today = datetime.datetime.now(ZoneInfo('Europe/Berlin')).date()
since = (today - datetime.timedelta(days=2)).isoformat()

root = ET.parse('out/sitemap.xml').getroot()
recent = [(u.find('s:loc', NS).text, (u.find('s:lastmod', NS).text or '')[:10] if u.find('s:lastmod', NS) is not None else '')
          for u in root.findall('s:url', NS)]
urls = [loc for loc, lm in recent if not lm or lm >= since][:10000]


# ---------- 1) Bing URL Submission API ----------
def bing():
    key = os.environ.get('BING_API_KEY', '').strip()
    if not key:
        print('Bing API: kein BING_API_KEY – übersprungen'); return
    api = 'https://ssl.bing.com/webmaster/api.svc/json/'
    q = urllib.parse.urlencode({'siteUrl': SITE, 'apikey': key})
    try:
        with urllib.request.urlopen(api + 'GetUrlSubmissionQuota?' + q, timeout=30) as r:
            d = json.load(r).get('d') or {}
        quota = int(d.get('DailyQuota', 0))
        print('Bing API: Tageskontingent frei', quota, '| Monat', d.get('MonthlyQuota'))
    except urllib.error.HTTPError as e:
        print('Bing API Kontingent-Abfrage fehlgeschlagen:', e.code, e.read()[:300].decode('utf-8', 'replace')); return
    except Exception as e:
        print('Bing API Kontingent-Abfrage fehlgeschlagen:', type(e).__name__); return
    if quota <= 0:
        print('Bing API: Kontingent für heute aufgebraucht'); return

    log = os.path.expanduser('~/.cache/twn/bing-submitted.txt')
    os.makedirs(os.path.dirname(log), exist_ok=True)
    keep_from = (today - datetime.timedelta(days=3)).isoformat()
    done = {}
    if os.path.exists(log):
        for line in open(log, encoding='utf-8'):
            p = line.rstrip('\n').split('\t')
            if len(p) == 2 and p[0] >= keep_from: done[p[1]] = p[0]

    cand = []
    try:   # neueste Artikel zuerst
        nroot = ET.parse('out/news-sitemap.xml').getroot()
        cand += [u.find('s:loc', NS).text for u in nroot.findall('s:url', NS)]
    except Exception as e:
        print('news-sitemap nicht lesbar:', type(e).__name__)
    cand += [loc for loc, lm in recent if lm == today.isoformat()]   # heute geänderte Rubrik-/Übersichtsseiten
    seen, todo = set(), []
    for u in cand:
        if u in seen or u in done: continue
        seen.add(u); todo.append(u)
    todo = todo[:quota]
    if not todo:
        print('Bing API: nichts Neues zu melden'); save(log, done); return

    sent = 0
    for i in range(0, len(todo), 500):
        batch = todo[i:i + 500]
        body = json.dumps({'siteUrl': SITE, 'urlList': batch}).encode()
        req = urllib.request.Request(api + 'SubmitUrlBatch?' + q, data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
        try:
            with urllib.request.urlopen(req, timeout=60) as r: r.read()
            sent += len(batch)
            for u in batch: done[u] = today.isoformat()
        except urllib.error.HTTPError as e:
            print('Bing API SubmitUrlBatch fehlgeschlagen:', e.code, e.read()[:300].decode('utf-8', 'replace')); break
        except Exception as e:
            print('Bing API SubmitUrlBatch fehlgeschlagen:', type(e).__name__); break
    print('Bing API:', sent, 'URLs gemeldet,', len(todo) - sent, 'nicht gesendet')
    save(log, done)


def save(log, done):
    with open(log, 'w', encoding='utf-8') as f:
        for u, d in done.items(): f.write(f'{d}\t{u}\n')


bing()

# ---------- 2) IndexNow ----------
if not urls: sys.exit(0)
body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': f'https://{HOST}/{KEY}.txt', 'urlList': urls}).encode()
for ep in ('https://api.indexnow.org/indexnow', 'https://www.bing.com/indexnow'):   # bei Fehler zusätzlich direkt bei Bing versuchen, Antworttext ausgeben
    req = urllib.request.Request(ep, data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r: print('IndexNow', ep, r.status, len(urls), 'URLs'); break
    except urllib.error.HTTPError as e: print('IndexNow failed:', ep, e.code, e.read()[:500].decode('utf-8', 'replace'))
    except Exception as e: print('IndexNow failed:', ep, e)
