#!/usr/bin/env python3
"""TERRA WORLD NEWS – Champions League / Europa League / Conference League (seit 15.10.2026, Nedys Vorgabe).
Quelle: offizielle UEFA-Daten (match.uefa.com / standings.uefa.com), aus dem Container nur über die Download-Brücke erreichbar.
Brücke (bridge/ucl/requests.txt), je Wettbewerb c (1 = Champions League, 14 = Europa League, 2019 = Conference League):
  https://match.uefa.com/v5/matches?competitionId=<c>&seasonYear=2027&order=ASC&offset=<0|100|200|300|400>&limit=100 m_<c>_<offset>.json
  https://standings.uefa.com/v1/standings?competitionId=<c>&seasonYear=2027 st_<c>.json
Usage: python3 -I tools/uefa_import.py bridge/ucl/files [--season-year 2027]
Schreibt content/football/champions-league.json und europa-league.json im Format der Liga-Dateien
(matches = Ligaphase mit r = Spieltag, table = offizielle UEFA-Tabelle, cups = Qualifikation und K.-o.-Runden)."""
import json, os, sys, glob, datetime
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPS = [  # key, competitionId, API-Football-ID (Live), Name
    ('champions-league', '1', {'bg': 'Шампионска лига', 'de': 'Champions League', 'en': 'Champions League'}),
    ('europa-league', '14', {'bg': 'Лига Европа', 'de': 'Europa League', 'en': 'Europa League'}),
    ('conference-league', '2019', {'bg': 'Лига на конференциите', 'de': 'Conference League', 'en': 'Conference League'}),   # seit 15.10.2026
]
UEFA_PATH = {'1': 'uefachampionsleague', '14': 'uefaeuropaleague', '2019': 'uefaconferenceleague'}
ROUNDS = {  # UEFA-Rundenname -> Anzeige (Reihenfolge = Reihenfolge auf der Seite)
    'First qualifying round': {'bg': 'Първи квалификационен кръг', 'de': '1. Qualifikationsrunde', 'en': 'First qualifying round'},
    'Second qualifying round': {'bg': 'Втори квалификационен кръг', 'de': '2. Qualifikationsrunde', 'en': 'Second qualifying round'},
    'Third qualifying round': {'bg': 'Трети квалификационен кръг', 'de': '3. Qualifikationsrunde', 'en': 'Third qualifying round'},
    'Play-Offs': {'bg': 'Плейофи (квалификации)', 'de': 'Play-offs (Qualifikation)', 'en': 'Play-offs (qualifying)'},
    'Knockout Round Play-offs': {'bg': 'Плейофи за осминафиналите', 'de': 'K.-o.-Phase: Play-offs', 'en': 'Knockout phase play-offs'},
    'Round of 16': {'bg': 'Осминафинали', 'de': 'Achtelfinale', 'en': 'Round of 16'},
    'Quarter-finals': {'bg': 'Четвъртфинали', 'de': 'Viertelfinale', 'en': 'Quarter-finals'},
    'Semi-finals': {'bg': 'Полуфинали', 'de': 'Halbfinale', 'en': 'Semi-finals'},
    'Final': {'bg': 'Финал', 'de': 'Finale', 'en': 'Final'},
}
BERLIN = ZoneInfo('Europe/Berlin')

def team(t):
    tr = t.get('translations', {})
    return (tr.get('displayOfficialName') or {}).get('DE') or t.get('internationalName') or tr['displayName']['EN']

def when(m):
    k = m['kickOffTime']
    dt = datetime.datetime.fromisoformat(k['dateTime'].replace('Z', '+00:00')).astimezone(BERLIN)
    return dt.date().isoformat(), dt.strftime('%H:%M')

def score(m):
    if m.get('status') != 'FINISHED': return None
    t = (m.get('score') or {}).get('total') or (m.get('score') or {}).get('regular')
    return [t['home'], t['away']] if t else None

def note(m):
    sc = m.get('score') or {}; out = []
    if sc.get('penalty'): out.append(f"i.E. {sc['penalty']['home']}:{sc['penalty']['away']}")
    if (m.get('winner') or {}).get('match', {}).get('reason') == 'WIN_ON_EXTRA_TIME' or sc.get('extraTime'): out.insert(0, 'n.V.')
    agg = (m.get('winner') or {}).get('aggregate')
    if agg and sc.get('aggregate'): out.append(f"Gesamt {sc['aggregate']['home']}:{sc['aggregate']['away']} – weiter: {team(agg['team'])}")
    return ', '.join(out)

def main():
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'bridge', 'ucl', 'files')
    os.makedirs(os.path.join(HERE, 'content', 'football'), exist_ok=True)
    for key, cid, name in COMPS:
        ms = []
        for f in sorted(glob.glob(os.path.join(d, f'm_{cid}_*.json')), key=lambda p: int(p.rsplit('_', 1)[1].split('.')[0])):
            ms += json.load(open(f, encoding='utf-8'))
        if not ms: print(key, 'keine Daten'); continue
        seen = set(); ms = [m for m in ms if not (m['id'] in seen or seen.add(m['id']))]
        sy = int(ms[0]['seasonYear']); season = f'{sy - 1}/{str(sy)[2:]}'
        league, ko = [], {}
        for m in sorted(ms, key=lambda m: m['kickOffTime']['dateTime']):
            rn = m['round']['metaData']['name']; dt, tm = when(m)
            if m['homeTeam'].get('isPlaceHolder') or m['awayTeam'].get('isPlaceHolder'):
                if rn == 'League Phase': continue
            x = {'date': dt, 'time': tm, 'ft': score(m)}
            if m.get('status') in ('POSTPONED', 'CANCELLED'): x['status'] = 'postponed'
            if rn == 'League Phase':
                x.update(r=int(''.join(c for c in m['matchday']['name'] if c.isdigit()) or 0), t1=team(m['homeTeam']), t2=team(m['awayTeam']))
                league.append(x)
            else:
                x.update(team1=team(m['homeTeam']), team2=team(m['awayTeam']))
                n = note(m)
                if n: x['note'] = n
                ko.setdefault(rn, []).append(x)
        table = []
        sp = os.path.join(d, f'st_{cid}.json')
        if os.path.exists(sp):
            st = json.load(open(sp, encoding='utf-8'))
            grp = next((g for g in st if g.get('group', {}).get('metaData', {}).get('groupName', '').lower().startswith('league')), st[0] if st else None)
            for it in sorted((grp or {}).get('items', []), key=lambda i: i['rank']):
                table.append({'pos': it['rank'], 'team': team(it['team']), 'p': it['played'], 'w': it['won'], 'd': it['drawn'], 'l': it['lost'],
                              'gf': it['goalsFor'], 'ga': it['goalsAgainst'], 'pts': it['points']})
        # Abgleich: Die UEFA-Tabelle kommt teils verzögert (CDN-Cache). Passt sie nicht zu den Ergebnissen, Tabelle selbst berechnen
        # (Reihenfolge nach UEFA-Regeln der Ligaphase: Punkte, Tordifferenz, Tore, Auswärtstore, Siege, Auswärtssiege).
        calc = {}
        for m in league:
            for x in (m['t1'], m['t2']): calc.setdefault(x, {'team': x, 'p': 0, 'w': 0, 'd': 0, 'l': 0, 'gf': 0, 'ga': 0, 'pts': 0, 'agf': 0, 'aw': 0})
            if m['ft'] is None: continue
            a, b = m['ft']
            for t, gf, ga, away in ((m['t1'], a, b, False), (m['t2'], b, a, True)):
                r = calc[t]; r['p'] += 1; r['gf'] += gf; r['ga'] += ga
                if away: r['agf'] += gf
                if gf > ga: r['w'] += 1; r['pts'] += 3; r['aw'] += 1 if away else 0
                elif gf == ga: r['d'] += 1; r['pts'] += 1
                else: r['l'] += 1
        if table and any((calc.get(x['team']) or {}).get('p') != x['p'] or calc[x['team']]['gf'] != x['gf'] or calc[x['team']]['ga'] != x['ga'] for x in table):
            print(key, 'UEFA-Tabelle noch nicht aktuell – Tabelle aus den Ergebnissen berechnet')
            srt = sorted(calc.values(), key=lambda r: (-r['pts'], -(r['gf'] - r['ga']), -r['gf'], -r['agf'], -r['w'], -r['aw'], r['team']))
            table = [{'pos': i + 1, **{k: r[k] for k in ('team', 'p', 'w', 'd', 'l', 'gf', 'ga', 'pts')}} for i, r in enumerate(srt)]
        rounds = []
        for rn, lab in ROUNDS.items():
            if rn in ko:
                ds = sorted({x['date'] for x in ko[rn]})
                rounds.append({'name': lab, 'date': f'{".".join(reversed(ds[0].split("-")))} – {".".join(reversed(ds[-1].split("-")))}' if len(ds) > 1 else '.'.join(reversed(ds[0].split('-'))), 'matches': ko[rn]})
        quali = [r for r in rounds if 'Qualif' in r['name']['de']]
        knock = [r for r in rounds if r not in quali]
        cups = []
        if knock: cups.append({'key': 'ko', 'name': {'bg': 'Елиминационна фаза', 'de': 'K.-o.-Phase', 'en': 'Knockout phase'}, 'rounds': knock})
        if quali: cups.append({'key': 'quali', 'name': {'bg': 'Квалификации', 'de': 'Qualifikation', 'en': 'Qualifying'}, 'rounds': quali})
        out = {'key': key, 'code': f'uefa.{cid}', 'season': season, 'name': name, 'tz': 'Europe/Berlin', 'uefa': True,
               'matches': league, 'table': table, 'cups': cups,
               'src': [{'n': 'UEFA', 'u': f'https://www.uefa.com/{UEFA_PATH[cid]}/'}],
               'asof': datetime.datetime.now(BERLIN).date().isoformat()}
        fp = os.path.join(HERE, 'content', 'football', f'{key}.json')
        json.dump(out, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(key, season, len(league), 'Ligaphase-Spiele,', sum(1 for m in league if m['ft'] is not None), 'mit Ergebnis,', len(table), 'Tabellenplätze,', sum(len(r['matches']) for r in rounds), 'Quali/K.-o.-Spiele')

if __name__ == '__main__':
    main()
