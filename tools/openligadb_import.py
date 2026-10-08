#!/usr/bin/env python3
"""2. Bundesliga aus OpenLigaDB (api.openligadb.de, frei nutzbar) -> content/football/2-bundesliga.json.
Der Container erreicht OpenLigaDB nicht direkt: Datei per Download-Brücke holen
(bridge/<aufgabe>/requests.txt: "https://api.openligadb.de/getmatchdata/bl2/<Saisonjahr> bl2_matches.json").
Usage: python3 tools/openligadb_import.py bridge/<aufgabe>/files/bl2_matches.json [--season 2026-27]
Vorhandene Ergebnisse bleiben erhalten, wenn die Quelle (noch) keines hat."""
import json, os, sys, argparse
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('--season', default='2026-27'); a = ap.parse_args()
src = json.load(open(a.src, encoding='utf-8'))
fp = os.path.join(HERE, 'content', 'football', '2-bundesliga.json')
old = json.load(open(fp, encoding='utf-8')) if os.path.exists(fp) else {}
oldm = {(m['r'], m['t1'], m['t2']): m for m in old.get('matches', [])}
ms = []
for m in sorted(src, key=lambda x: (x['group']['groupOrderID'], x['matchDateTime'])):
    r = m['group']['groupOrderID']; d, t = m['matchDateTime'].split('T')
    x = {'r': r, 'date': d, 'time': t[:5], 't1': m['team1']['teamName'], 't2': m['team2']['teamName']}
    fin = [z for z in m.get('matchResults') or [] if z.get('resultTypeID') == 2 or z.get('resultName') == 'Endergebnis']
    if m.get('matchIsFinished') and fin: x['ft'] = [fin[0]['pointsTeam1'], fin[0]['pointsTeam2']]
    elif (r, x['t1'], x['t2']) in oldm and oldm[(r, x['t1'], x['t2'])].get('ft') is not None: x['ft'] = oldm[(r, x['t1'], x['t2'])]['ft']
    ms.append(x)
out = {'key': '2-bundesliga', 'code': 'de.2', 'season': a.season,
       'name': {'bg': '2. Бундеслига', 'de': '2. Bundesliga', 'en': '2. Bundesliga'}, 'tz': 'Europe/Berlin',
       'matches': ms, 'cups': old.get('cups', []),
       'src': [{'n': 'OpenLigaDB', 'u': 'https://www.openligadb.de/'}]}
json.dump(out, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(ms), 'Spiele,', sum(1 for m in ms if m.get('ft')), 'mit Ergebnis')
