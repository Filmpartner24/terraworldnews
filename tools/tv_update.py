#!/usr/bin/env python3
"""TWN TV (Nedy 05.11.2026): aktuelle Livestream-Video-IDs der offiziellen YouTube-Kanäle ermitteln → static/tv/channels.json.
Läuft in der GitHub Action (.github/workflows/tv.yml), die YouTube erreichen kann. Nur offizielle Kanäle (Kanal-ID wird geprüft);
findet sich kein Livestream, bleibt die letzte bekannte ID stehen. Eingebettet wird über youtube-nocookie.com (offizieller Player)."""
import json, os, re, urllib.request, datetime as dt

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, 'static', 'tv', 'channels.json')
CH = [  # Reihenfolge = Anzeige (Nedy 05.11.2026: WELT oben, dann DW; Al Jazeera Arabic entfernt)  # id, Name, Sprache, Handle, offizielle Kanal-ID, Farben
    ('welt', 'WELT', 'de', 'WELTVideoTV', 'UCZMsvbAhhRblVGXmEXW8TSA', '#2f6bff', '#0b1430'),
    ('dw', 'DW News', 'en', 'dwnews', 'UCknLrEdhRCp1aegoMqRaCZg', '#05b2fc', '#002d5a'),
    ('f24en', 'France 24 English', 'en', 'France24_en', 'UCQfwfsi5VrQ8yKZ-UWmAEFg', '#00a4e4', '#1a1f5a'),
    ('f24fr', 'France 24 Français', 'fr', 'FRANCE24', 'UCCCPCZNChQdGa9EkATeye4g', '#00a4e4', '#1a1f5a'),
    ('f24es', 'France 24 Español', 'es', 'France24_es', 'UCUdOoVWuWmgo1wByzcsyKDQ', '#00a4e4', '#1a1f5a'),
    ('eun', 'Euronews English', 'en', 'euronews', 'UCSrZ3UV4jOidv8ppoVuvW9Q', '#3b8bff', '#0a1f4a'),
    ('eude', 'Euronews Deutsch', 'de', 'euronewsde', 'UCACdxU3VrJIJc7ujxtHWs1w', '#3b8bff', '#0a1f4a'),
    ('aje', 'Al Jazeera English', 'en', 'aljazeeraenglish', 'UCNye-wNBqNL5ZzHSJj3l8Bg', '#fa9000', '#3a2400'),
]

def live_id(handle, cid):
    req = urllib.request.Request(f'https://www.youtube.com/@{handle}/live', headers={'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'en'})
    s = urllib.request.urlopen(req, timeout=40).read().decode('utf-8', 'replace')
    owner = re.search(r'"browseEndpoint":\{"browseId":"(UC[\w-]{22})","canonicalBaseUrl":"/@', s)
    vid = re.search(r'"updatedMetadataEndpoint":\{"videoId":"([\w-]{11})"', s)
    title = re.search(r'"videoPrimaryInfoRenderer":\{"title":\{"runs":\[\{"text":"([^"]*)"', s)
    if not (owner and vid) or owner.group(1) != cid: return None, None
    if 'watching now' not in s and '"isLive":true' not in s: return None, None
    return vid.group(1), json.loads('"' + title.group(1) + '"') if title else ''

def main():
    try: old = {c['id']: c for c in json.load(open(OUT, encoding='utf-8'))['channels']}
    except (FileNotFoundError, ValueError, KeyError): old = {}
    out = []
    for k, name, lang, h, cid, c1, c2 in CH:
        v, t = None, None
        try: v, t = live_id(h, cid)
        except Exception as e: print(k, 'Fehler', e)
        o = old.get(k, {})
        out.append({'id': k, 'name': name, 'lang': lang, 'channel': cid, 'handle': h, 'c1': c1, 'c2': c2,
                    'v': v or o.get('v', ''), 'title': t or o.get('title', ''), 'checked': dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ') if v else o.get('checked', '')})
        print(k, v, (t or '')[:60])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    new = {'note': 'Offizielle YouTube-Livestreams (Kanal-ID geprüft), eingebettet über youtube-nocookie.com.', 'channels': out}
    if [ (c['id'], c['v']) for c in out ] != [ (c['id'], c.get('v')) for c in old.values() ] or not os.path.exists(OUT):
        json.dump(new, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
