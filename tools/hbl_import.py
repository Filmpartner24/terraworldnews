#!/usr/bin/env python3
"""Handball-Bundesliga: Ergebnisse aus den kicktipp-Spielplanseiten in content/handball/handball-bundesliga.json übernehmen.
Der Container erreicht kicktipp nicht direkt: Seiten per Download-Brücke holen
(bridge/<aufgabe>/requests.txt, je Spieltag N eine Zeile:
 "https://www.kicktipp.com/info/service/competitions/handball%20bundesliga/spielplan?saisonId=525787&spieltagIndex=N hbl_N.html").
Usage: python3 tools/hbl_import.py bridge/<aufgabe>/files
- Ergebnisse (a-b) werden bei vorhandenen Spielen (gleiche Paarung) eingetragen.
- Neue Paarungen werden mit Datum ergänzt (Uhrzeit nur, wenn noch keine bekannt ist; die Anwurfzeit bitte mit liquimoly-hbl.de prüfen).
- "Cancelled"/"Abgesagt" -> status "postponed". Danach Tabelle mit einer offiziellen Quelle (liquimoly-hbl.de, sportschau.de) vergleichen."""
import json, os, sys, re, glob, html, datetime
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fp = os.path.join(HERE, 'content', 'handball', 'handball-bundesliga.json')
lg = json.load(open(fp, encoding='utf-8'))
idx = {(m['t1'], m['t2']): m for m in lg['matches']}
new = upd = 0
for f in sorted(glob.glob(os.path.join(sys.argv[1], 'hbl_*.html'))):
    r = int(re.search(r'hbl_(\d+)', f).group(1))
    h = open(f, encoding='utf-8', errors='ignore').read()
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', h, re.S):
        tds = [html.unescape(re.sub(r'<[^>]+>', ' ', x)).strip() for x in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
        tds = [re.sub(r'\s+', ' ', x) for x in tds]
        if len(tds) < 4: continue
        dt, t1, t2, res = tds[0], tds[1], tds[2], tds[3]
        if not t1 or not t2: continue
        m = idx.get((t1, t2))
        if m is None:
            m = {'r': r, 't1': t1, 't2': t2}
            d = re.search(r'(\d{1,2})[./](\d{1,2})[./](\d{2,4})', dt)
            if d:
                a, b, y = d.groups(); y = int(y) + (2000 if len(y) == 2 else 0)
                mo, da = (int(a), int(b)) if '/' in dt else (int(b), int(a))
                m['date'] = datetime.date(y, mo, da).isoformat()
            else: m['date'] = lg['matches'][-1]['date']
            lg['matches'].append(m); idx[(t1, t2)] = m; new += 1
        sc = re.search(r'(\d+)\s*[-:]\s*(\d+)', res)
        if sc and m.get('ft') != [int(sc.group(1)), int(sc.group(2))]:
            m['ft'] = [int(sc.group(1)), int(sc.group(2))]; m.pop('status', None); upd += 1
        if re.search(r'cancel|abgesagt|verlegt', dt + res, re.I) and m.get('ft') is None: m['status'] = 'postponed'
lg['matches'].sort(key=lambda m: (m['r'], m['date'], m.get('time', '')))
json.dump(lg, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'{upd} Ergebnisse aktualisiert, {new} neue Spiele')
