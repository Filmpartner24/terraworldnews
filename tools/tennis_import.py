#!/usr/bin/env python3
"""Tennis: ATP-/WTA-Weltrangliste und laufende Turniere (ESPN-Daten) -> content/tennis/rankings.json.
Per Download-Brücke holen (bridge/<aufgabe>/requests.txt):
  https://site.api.espn.com/apis/site/v2/sports/tennis/atp/rankings atp_rank.json
  https://site.api.espn.com/apis/site/v2/sports/tennis/wta/rankings wta_rank.json
  https://site.api.espn.com/apis/site/v2/sports/tennis/atp/scoreboard atp_sb.json
  https://site.api.espn.com/apis/site/v2/sports/tennis/wta/scoreboard wta_sb.json
Usage: python3 tools/tennis_import.py bridge/<aufgabe>/files
Danach Platz 1–5 mit atptour.com/wtatennis.com vergleichen."""
import json, os, sys, datetime
def _d(x):
    if not x: return ''
    try: return (datetime.datetime.fromisoformat(x.replace('Z', '+00:00')) - datetime.timedelta(hours=5)).date().isoformat()   # ESPN liefert Tagesgrenzen in UTC (04:00Z)
    except Exception: return x[:10]
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = sys.argv[1]
out = {'updated': datetime.date.today().isoformat(), 'events': []}
for tour in ('atp', 'wta'):
    rk = json.load(open(os.path.join(d, f'{tour}_rank.json'), encoding='utf-8'))['rankings'][0]
    out[tour] = {'date': (rk.get('update') or rk.get('date') or '')[:10],
                 'ranks': [{'r': x['current'], 'prev': x.get('previous'), 'name': x['athlete']['displayName'], 'cc': x['athlete'].get('citizenshipCountry', ''),
                            'pts': int(x['points'])} for x in rk['ranks'][:150]]}
    sb = os.path.join(d, f'{tour}_sb.json')
    if os.path.exists(sb):
        for ev in json.load(open(sb, encoding='utf-8')).get('events', []):
            out['events'].append({'tour': tour.upper(), 'name': ev.get('name', ''), 'start': _d(ev.get('date')) if False else (ev.get('date') or '')[:10], 'end': _d(ev.get('endDate'))})
out['src'] = [{'n': 'ESPN Tennis', 'u': 'https://www.espn.com/tennis/rankings'}, {'n': 'ATP Tour', 'u': 'https://www.atptour.com/en/rankings/singles'}, {'n': 'WTA', 'u': 'https://www.wtatennis.com/rankings/singles'}]
json.dump(out, open(os.path.join(HERE, 'content', 'tennis', 'rankings.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ATP 1:', out['atp']['ranks'][0]['name'], '| WTA 1:', out['wta']['ranks'][0]['name'], '|', len(out['events']), 'Turniere')
