TERRA WORLD NEWS (terraworldnews.com) – Sport → FORMEL 1 (DE /de/sport/formel-1/, EN /en/sport/formula-1/, BG /sport/formula-1/) und Sport → TENNIS (DE /de/sport/tennis/). Aufbau wie die Fußball-Seiten: oben Tabellen/Platzierungen, darunter News und Videos. Chefredakteur: Nedy John Cross (Bericht auf Deutsch). Arbeite selbstständig, ohne Rückfragen. Läuft täglich (Nedys Vorgabe vom 09.10.2026). Zuerst tools/tasks/_regeln.md lesen – die gemeinsamen Regeln gehen vor.

TAGESSPERRE: Enthält content/<heute>-formel1.json schon ≥ 2 Items UND content/<heute>-tennis.json ≥ 2 Items, keine neuen Artikel (Tabellen trotzdem aktualisieren), außer der Starttext sagt NACHHOLLAUF/ZUSÄTZLICH.

1. DATEN (jeden Tag):
   - Download-Brücke: bridge/f1-tennis/requests.txt mit
     https://api.jolpi.ca/ergast/f1/<Saison>/driverstandings/ f1_drivers.json
     https://api.jolpi.ca/ergast/f1/<Saison>/constructorstandings/ f1_teams.json
     https://api.jolpi.ca/ergast/f1/<Saison>/races/?limit=40 f1_races.json
     https://api.jolpi.ca/ergast/f1/<Saison>/results/1/?limit=40 f1_winners.json
     https://site.api.espn.com/apis/site/v2/sports/tennis/atp/rankings atp_rank.json
     https://site.api.espn.com/apis/site/v2/sports/tennis/wta/rankings wta_rank.json
     https://site.api.espn.com/apis/site/v2/sports/tennis/atp/scoreboard atp_sb.json
     https://site.api.espn.com/apis/site/v2/sports/tennis/wta/scoreboard wta_sb.json
     Push mit „[CF-Pages-Skip]“, ~3 Min. warten, git pull, dann python3 tools/f1_import.py bridge/f1-tennis/files und python3 tools/tennis_import.py bridge/f1-tennis/files. bridge/f1-tennis/ danach löschen.
   - Prüfen: F1-WM Platz 1–5 (Punkte) mit formula1.com, motorsport-total.com oder autohebdo.de vergleichen; ATP/WTA Platz 1–5 mit atptour.com/wtatennis.com oder sportschau.de. Hinkt eine Quelle nach (z. B. Rennen gestern noch nicht drin), die Datei korrigieren oder am nächsten Tag erneut laden – nie raten.

2. ARTIKEL (täglich zusätzlich):
   A) FORMEL 1: 2 Meldungen (Rennwochenende: Training/Qualifying/Rennen, WM-Stand, Teams, Fahrerwechsel, Technik, Strafen). An Rennwochenenden 3. Mindestens 1 mit offiziellem Video vom Kanal „FORMULA 1“ (Highlights, Fahrerstimmen) – nur Videos, die in DE und BG abspielbar sind.
   B) TENNIS: 2 Meldungen (laufende ATP-/WTA-Turniere, Grand Slams, Ranglisten-Bewegungen, Verletzungen nur nach offizieller Mitteilung). Fokus auch auf deutsche (z. B. Zverev) und bulgarische Spieler (z. B. Dimitrov). Mindestens 1 mit offiziellem Video von „ATP Tour“, „WTA“ oder „Tennis TV“.
   Quellen: dpa/SID über zdfheute, sportschau, kicker, motorsport-total, motorsport-magazin, Reuters, AP, BTA, Sportal.bg, Gong.bg, offizielle Seiten (formula1.com, atptour.com, wtatennis.com). Mindestens 2 Quellen pro Meldung, jede Zahl belegt. Nichts wiederholen, was in content/*-formel1.json / *-tennis.json der letzten 7 Tage steht.

3. ITEM-FORMAT: content/<YYYY-MM-DD>-formel1.json bzw. -tennis.json ({"date","items":[…]}; anhängen): {"id": latin-slug-<Datum>, "s":"sport", "sub":"formel1"|"tennis", "kl":{"de":"Formel 1","bg":"Формула 1","en":"Formula 1"} bzw. {"de":"Tennis","bg":"Тенис","en":"Tennis"}, "time" (nie Zukunft), "src", "img", optional "yt":{"id","ch","kind":"video","t":{bg,de,en}}, "de"/"bg"/"en":{"t" ≤90,"d" ≤220,"body":[2–3 Absätze]}}. Vorlage: content/2026-10-09-formel1.json und content/2026-10-09-tennis.json. Videos über die Download-Brücke prüfen (_regeln.md Nr. 3).

4. BILDER: Wikimedia Commons (Fahrer/Autos/Spieler nur eindeutig identifiziert, Strecken/Stadien) über candidates/<YYYY-MM-DD>-f1tn/requests.json; „(Archivbild)“/„(Symbolbild)“ im alt. Nie YouTube-Vorschaubilder, Agentur- oder Pressefotos.

5. VERÖFFENTLICHEN: PYTHONHASHSEED=1 python3 build.py fehlerfrei (bei SyntaxError python3.12); Stichprobe out/de/sport/formel-1/index.html und out/de/sport/tennis/index.html. git add content static/assets/news; Commit „Formel 1 + Tennis <Datum>“ mit den Attributionszeilen der Sitzung; git pull --rebase; git push.

6. BERICHT kurz auf Deutsch: WM-Führender F1 + Punkte, ATP/WTA Nr. 1, Titel der neuen Meldungen. PushNotification nur bei Problemen (_regeln.md Nr. 7).

REGELN: Nur content/, candidates/, bridge/ und static/assets/news/ ändern; Design und build.py nicht anfassen; keine Logins, Konten, Zahlungen.
