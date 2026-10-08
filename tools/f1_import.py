#!/usr/bin/env python3
"""Formel 1: WM-Stand, Kalender, Sieger aus Jolpica-F1 (Nachfolger der Ergast-API, frei nutzbar) -> content/f1/<Saison>.json.
Der Container erreicht api.jolpi.ca nicht direkt: per Download-Brücke holen (bridge/<aufgabe>/requests.txt):
  https://api.jolpi.ca/ergast/f1/<Saison>/driverstandings/ f1_drivers.json
  https://api.jolpi.ca/ergast/f1/<Saison>/constructorstandings/ f1_teams.json
  https://api.jolpi.ca/ergast/f1/<Saison>/races/?limit=40 f1_races.json
  https://api.jolpi.ca/ergast/f1/<Saison>/results/1/?limit=40 f1_winners.json
Usage: python3 tools/f1_import.py bridge/<aufgabe>/files"""
import json, os, sys, datetime
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = sys.argv[1]
J = lambda n: json.load(open(os.path.join(d, n), encoding='utf-8'))['MRData']
ds = J('f1_drivers.json')['StandingsTable']; season = ds['season']; sl = ds['StandingsLists'][0]
drivers = [{'pos': int(s['position']), 'name': f"{s['Driver']['givenName']} {s['Driver']['familyName']}", 'nat': s['Driver'].get('nationality', ''),
            'team': s['Constructors'][0]['name'] if s.get('Constructors') else '', 'pts': float(s['points']), 'wins': int(s['wins'])} for s in sl['DriverStandings']]
ts = J('f1_teams.json')['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
teams = [{'pos': int(s['position']), 'name': s['Constructor']['name'], 'pts': float(s['points']), 'wins': int(s['wins'])} for s in ts]
win = {r['round']: r['Results'][0] for r in J('f1_winners.json')['RaceTable']['Races'] if r.get('Results')}
races = []
for r in J('f1_races.json')['RaceTable']['Races']:
    x = {'round': int(r['round']), 'name': r['raceName'], 'circuit': r['Circuit']['circuitName'], 'locality': r['Circuit']['Location']['locality'],
         'country': r['Circuit']['Location']['country'], 'date': r['date'], 'time': (r.get('time') or '')[:5]}
    w = win.get(r['round'])
    if w: x['winner'] = f"{w['Driver']['givenName']} {w['Driver']['familyName']}"; x['winner_team'] = w['Constructor']['name']
    races.append(x)
out = {'season': season, 'round': int(sl['round']), 'updated': datetime.date.today().isoformat(), 'drivers': drivers, 'teams': teams, 'races': races,
       'src': [{'n': 'Jolpica-F1 (Ergast-Nachfolger)', 'u': 'https://github.com/jolpica/jolpica-f1'}, {'n': 'Formula 1 – offizielle Wertung', 'u': 'https://www.formula1.com/en/results'}]}
fp = os.path.join(HERE, 'content', 'f1', f'{season}.json')
json.dump(out, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(fp, 'Runde', out['round'], 'Führender', drivers[0]['name'], drivers[0]['pts'])
