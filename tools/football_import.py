#!/usr/bin/env python3
"""TERRA WORLD NEWS – Fußball-Ligadaten (Saison, Spielplan, Ergebnisse).
Quelle Ligen: openfootball/football.json (CC0, Public Domain), ergänzt um redaktionell geprüfte Korrekturen.
Usage: python3 tools/football_import.py [--season 2026-27] [--fixes drafts/fb/fixes.json] [--cups drafts/fb/cups.json] [--offline DIR]
Schreibt content/football/<liga>.json. Vorhandene Ergebnisse (auch manuell eingetragene) bleiben erhalten,
wenn die Quelle (noch) kein Ergebnis hat."""
import json, os, sys, urllib.request, re, argparse

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEAGUES = [  # key, openfootball-Code, Name, Zeitzone der Anstoßzeiten in der Quelle
    ('premier-league', 'en.1', {'bg': 'Висша лига', 'de': 'Premier League', 'en': 'Premier League'}, 'Europe/London'),
    ('bundesliga', 'de.1', {'bg': 'Бундеслига', 'de': 'Bundesliga', 'en': 'Bundesliga'}, 'Europe/Berlin'),
    ('la-liga', 'es.1', {'bg': 'Ла Лига', 'de': 'La Liga', 'en': 'La Liga'}, 'Europe/Madrid'),
    ('ligue-1', 'fr.1', {'bg': 'Лига 1', 'de': 'Ligue 1', 'en': 'Ligue 1'}, 'Europe/Paris'),
    ('serie-a', 'it.1', {'bg': 'Серия А', 'de': 'Serie A', 'en': 'Serie A'}, 'Europe/Rome'),
]
URL = 'https://raw.githubusercontent.com/openfootball/football.json/master/{season}/{code}.json'

def ft_of(m):
    sc = m.get('score')
    if isinstance(sc, list) and len(sc) == 2: return sc            # Kurzform [a, b]
    if isinstance(sc, dict) and sc.get('ft'): return sc['ft']
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--season', default='2026-27')
    ap.add_argument('--fixes'); ap.add_argument('--cups'); ap.add_argument('--offline')
    a = ap.parse_args()
    fixes = json.load(open(a.fixes)) if a.fixes else {}
    cups = json.load(open(a.cups)) if a.cups else {}
    os.makedirs(os.path.join(HERE, 'content', 'football'), exist_ok=True)
    for key, code, name, tz in LEAGUES:
        if a.offline: src = json.load(open(os.path.join(a.offline, f'fb_{code}.json')))
        else: src = json.load(urllib.request.urlopen(URL.format(season=a.season, code=code), timeout=60))
        fp = os.path.join(HERE, 'content', 'football', f'{key}.json')
        old = json.load(open(fp)) if os.path.exists(fp) else {}
        oldm = {(m['date'], m['t1'], m['t2']): m for m in old.get('matches', [])}
        ms = []
        for i, m in enumerate(src['matches']):
            r = int(re.sub(r'\D', '', m.get('round', '0')) or 0)
            x = {'r': r, 'date': m['date'], 'time': m.get('time', ''), 't1': m['team1'], 't2': m['team2'], 'ft': ft_of(m)}
            o = oldm.get((x['date'], x['t1'], x['t2']))
            if x['ft'] is None and o and o.get('ft') is not None: x['ft'] = o['ft']
            if o and o.get('status') and x['ft'] is None: x['status'] = o['status']
            for f in fixes.get(code, []):
                if f.get('i') == i:
                    if f.get('ft'): x['ft'] = f['ft']
                    if f.get('status'): x['status'] = f['status']
            ms.append(x)
        season = (re.search(r'(\d{4}/\d{2})', src.get('name', '')) or [None, a.season.replace('-', '/')])[1]
        out = {'key': key, 'code': code, 'season': season, 'name': name, 'tz': tz, 'matches': ms,
               'cups': cups.get(code, old.get('cups', [])),
               'src': [{'n': 'openfootball (CC0)', 'u': f'https://github.com/openfootball/football.json/tree/master/{a.season}'}]}
        json.dump(out, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(key, season, len(ms), 'Spiele,', sum(1 for m in ms if m['ft'] is not None), 'mit Ergebnis')

if __name__ == '__main__':
    main()
