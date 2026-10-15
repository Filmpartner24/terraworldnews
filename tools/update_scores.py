#!/usr/bin/env python3
"""TERRA WORLD NEWS – Tabellen unmittelbar nach den Spielen aktualisieren (Nedys Vorgabe 15.10.2026).
Läuft als GitHub Action (.github/workflows/scores.yml) zu den typischen Abpfiff-Zeiten und schreibt nur Daten-Dateien:
  1. Champions League / Europa League / Conference League: offizielle UEFA-Daten (match.uefa.com, standings.uefa.com) -> tools/uefa_import.py
  2. 2. Bundesliga: OpenLigaDB -> tools/openligadb_import.py
  3. Bundesliga: Endergebnisse aus OpenLigaDB in content/football/bundesliga.json nachtragen (Spielplan bleibt openfootball)
  4. Premier League, La Liga, Serie A, Ligue 1, Bundesliga: openfootball (CC0) -> tools/football_import.py (vorhandene Ergebnisse bleiben)
Jeder Schritt ist unabhängig: schlägt einer fehl, laufen die anderen weiter. Commit/Push macht der Workflow."""
import json, os, sys, re, subprocess, tempfile, datetime, urllib.request, unicodedata

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {'User-Agent': 'TERRA-WORLD-NEWS-scores/1.0 (https://terraworldnews.com; media@filmpartner24.com)', 'Accept': 'application/json'}

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))

def season_years():
    t = datetime.date.today()
    end = t.year + 1 if t.month >= 7 else t.year          # UEFA-seasonYear = Endjahr (2026/27 -> 2027)
    return end, end - 1                                   # OpenLigaDB = Startjahr

def uefa(sy):
    d = tempfile.mkdtemp(prefix='uefa_')
    for cid in ('1', '14', '2019'):
        off = 0
        while off <= 600:
            j = get(f'https://match.uefa.com/v5/matches?competitionId={cid}&seasonYear={sy}&order=ASC&offset={off}&limit=100')
            if not j: break
            json.dump(j, open(os.path.join(d, f'm_{cid}_{off}.json'), 'w'))
            if len(j) < 100: break
            off += 100
        json.dump(get(f'https://standings.uefa.com/v1/standings?competitionId={cid}&seasonYear={sy}'), open(os.path.join(d, f'st_{cid}.json'), 'w'))
    subprocess.run([sys.executable, '-I', os.path.join(HERE, 'tools', 'uefa_import.py'), d], check=True)

def bl2(oy):
    p = os.path.join(tempfile.mkdtemp(prefix='bl2_'), 'bl2.json')
    json.dump(get(f'https://api.openligadb.de/getmatchdata/bl2/{oy}'), open(p, 'w'))
    subprocess.run([sys.executable, os.path.join(HERE, 'tools', 'openligadb_import.py'), p, '--season', f'{oy}/{str(oy + 1)[2:]}'], check=True)

def nz(x):
    x = unicodedata.normalize('NFD', str(x or '').lower())
    x = ''.join(c for c in x if not unicodedata.combining(c))
    x = re.sub(r'\b(fc|sv|sc|vfb|vfl|tsg|tsv|ssv|1|04|05|07|1899|1846|1909|de|borussia|bayer)\b', ' ', x)
    return set(w for w in re.sub(r'[^a-z0-9 ]', ' ', x).split() if len(w) > 2)

def bl1(oy):
    fp = os.path.join(HERE, 'content', 'football', 'bundesliga.json')
    lg = json.load(open(fp, encoding='utf-8')); n = 0
    src = get(f'https://api.openligadb.de/getmatchdata/bl1/{oy}')
    for m in src:
        fin = [z for z in m.get('matchResults') or [] if z.get('resultTypeID') == 2 or z.get('resultName') == 'Endergebnis']
        if not (m.get('matchIsFinished') and fin): continue
        r = m['group']['groupOrderID']; a, b = nz(m['team1']['teamName']), nz(m['team2']['teamName'])
        for x in lg['matches']:
            if x['r'] == r and x.get('ft') is None and nz(x['t1']) & a and nz(x['t2']) & b:
                x['ft'] = [fin[0]['pointsTeam1'], fin[0]['pointsTeam2']]; x.pop('status', None); n += 1
    if n: json.dump(lg, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('Bundesliga (OpenLigaDB):', n, 'neue Ergebnisse')

def openfootball(oy):
    subprocess.run([sys.executable, os.path.join(HERE, 'tools', 'football_import.py'), '--season', f'{oy}-{str(oy + 1)[2:]}'], check=True)

def main():
    sy, oy = season_years(); ok = True
    for name, fn, arg in (('UEFA', uefa, sy), ('2. Bundesliga', bl2, oy), ('openfootball', openfootball, oy), ('Bundesliga', bl1, oy)):
        try: fn(arg)
        except Exception as e:
            ok = False; print(f'FEHLER {name}: {e}', file=sys.stderr)
    return 0 if ok else 0   # Teilfehler brechen den Lauf nicht ab; der Workflow committet, was geklappt hat

if __name__ == '__main__':
    sys.exit(main())
