# TERRA WORLD NEWS – Gemeinsame Regeln für ALLE geplanten Aufgaben (Stand 06.10.2026)

Diese Regeln gelten für jede Aufgabe und gehen bei Widersprüchen der jeweiligen Aufgabenanweisung UND der Skill „terra-daily-edition“ vor (die Skill ist in Teilen veraltet, z. B. „77 Meldungen“, alte Breaking-Zeiten).

## 1. Aktuelle Eckdaten
- Tagesausgabe: genau 80 Meldungen (Deutschland 12 inkl. 2–3 Berlin und 1 Deutschland–Bulgarien, Bulgarien 11, Welt 15, Europa 8, Technologie [s="ki"] 8, Wirtschaft 6, Energie 3, Klima 3, Leben & Alltag 9, Kultur 5). Alle anderen Aufgaben kommen ZUSÄTZLICH.
- Breaking: 6 Updates täglich (08:00, 11:00, 13:00, 15:30, 18:30, 21:00), je 8 Meldungen.
- Games: 2 Meldungen pro Tag (1 mit Video, 1 News).
- Nur Männerfußball – kein Frauenfußball. Bulgarisch: AfD immer „АзГ (AfD)“.

## 2. TAGESSPERRE (gegen doppelte Läufe)
Vor dem Schreiben: git pull und prüfen, ob für HEUTE (Europe/Berlin) die Zieldatei schon die Soll-Anzahl enthält (z. B. content/<heute>-ki.json ≥ 6 Items). Wenn ja: nichts hinzufügen, nur kurz berichten. Ausnahme: Der Starttext sagt ausdrücklich „NACHHOLLAUF“ oder „ZUSÄTZLICH“.
Jede neue id darf in KEINER content/<heute>*.json schon vorkommen (der Build verwirft doppelte ids stillschweigend). Vor dem Push mit Python prüfen.

## 3. VIDEOPRÜFUNG in der Cloud (noembed.com/youtube.com sind aus dem Container gesperrt)
Nie per WebFetch oder curl versuchen. Stattdessen die Download-Brücke:
1. Für jede Kandidaten-ID eine Zeile in bridge/<aufgabe>/requests.txt (Ordnername = Kurzname der Aufgabe, z. B. bridge/breaking-1100/, bridge/games/):
   `https://noembed.com/embed?url=https://www.youtube.com/watch?v=<ID> noembed_<ID>.json`
2. Zusammen mit den Foto-Kandidaten (candidates/…) in EINEM Commit „… [CF-Pages-Skip]“ pushen, ~3 Min. warten, git pull (wiederholen, bis die Dateien da sind).
3. bridge/<aufgabe>/files/noembed_<ID>.json lesen: gültig nur, wenn kein "error" und author_name = ein erlaubter offizieller Kanal und title passt zu Thema und Datum. Gibt es noembed_<ID>.json.error, gilt das Video als nicht prüfbar → weglassen.
4. Danach bridge/<aufgabe>/ in einem Folge-Commit löschen.
Videos nur einbetten (yt-Feld), nie herunterladen. In Deutschland abspielbar: Spiel-/Kampf-Highlights nur von deutschen Sender-/Liga-Kanälen (sportstudio fußball/ZDF, Sportschau, DAZN, Sky Sport DE, Bundesliga, DFB, RTL Sport); ausländische Liga-/Sender-Kanäle (z. B. Premier League, TNT, beIN, Sky Sports UK) nur für Interviews/Pressekonferenzen. Nachrichten: offizielle Sender-/Agentur-/Institutions-/Firmenkanäle. Nie Fan- oder Re-Upload-Kanäle.
Andere gesperrte Datenquellen (z. B. match.uefa.com, standings.uefa.com) ebenfalls über die Brücke holen (`<URL> <dateiname>.json`).

## 4. BILDER (rechtssicher)
- JEDE Meldung braucht ein img – auch Meldungen mit Video (das Bild dient als Video-Titelbild). Vor dem Push mit Python prüfen: kein Item ohne img, und jede Datei static<img.f> existiert (Commons-Fotos kommen erst nach dem Action-Lauf – dann nach git pull nachprüfen; fehlt eines, Titelgrafik einsetzen).
- Nur Wikimedia Commons (CC BY / BY-SA / CC0 / PD / OGL) über candidates/<ordner>/requests.json → Kontaktbogen ansehen → img {"f":"/assets/news/<Datum>/<id>.webp","w":1200,"h":675,"art","lic","page","alt":{bg,de,en}} (Pfad IMMER mit führendem „/“; art bei CC BY/BY-SA nie leer), Symbol-/Archivbild im alt kennzeichnen.
- NIEMALS: YouTube-Vorschaubilder, Video-Standbilder, Film-Stills, Plakate, Album-/Spiel-Cover, Agentur-/Pressefotos, KI-Bilder – auch nicht mit „©“-Vermerk (ein ©-Vermerk ist keine Lizenz).
- Gibt es kein passendes Commons-Bild: eigene Titelgrafik erzeugen – python3 -c "import sys; sys.path.insert(0,'tools'); import title_card; title_card.make('static/assets/news/<Datum>/<id>-tg.webp','<RUBRIK>','<deutscher Titel>','<Farbe>')" und img {"f":"/assets/news/<Datum>/<id>-tg.webp","w":1200,"h":675,"own":true,"alt":{bg,de,en}}. Ergebnisgrafiken (Sport) wie bisher mit own:true.

## 5. Inhalt und Recht
- Jede Meldung: bg/de/en (t ≤ 90, d ≤ 220), body = JSON-Liste mit 2–3 Absätzen, Quellen src [{n,u}] nur mit tatsächlich gesehenen, datierten URLs; eigene Worte; Zitate nur wörtlich belegt mit Sprecher; Gerüchte nur gekennzeichnet.
- Pressekodex: Unschuldsvermutung, keine identifizierenden Details von Verdächtigen/Opfern, Verletzungen/Erkrankungen (auch bei Sportlern) nur nach offizieller Mitteilung von Person/Team/Verband, sachlich, ohne medizinische Spekulation.
- time = Veröffentlichungszeit (HH:MM Berlin), NIE in der Zukunft.
- Nichts wiederholen, was in den letzten Tagen schon auf der Seite steht: vor dem Schreiben die relevanten content/*.json lesen (mindestens content/<heute>*.json und content/<gestern>*.json, dazu die eigenen Rubrikdateien der letzten 7 Tage).
- RAUMFAHRT (Nedy 09.10.2026): nie unter Technologie (s="ki") oder KI (s="ai"). Raumfahrt-Meldungen (Raketen, Satelliten, Sonden, Teleskope, ISS, NASA/ESA/SpaceX) laufen unter Welt: s="welt" mit "kl":{"de":"Raumfahrt","bg":"Космос","en":"Space"}.
- Abgrenzung: Autos (Modelle, Marken, Verkaufszahlen) → Auto-Aufgabe; Tagesausgabe/Technologie nur aus Technik-Sicht (Batterie, autonomes Fahren, Laden). KI-Modelle/KI-Firmen → s="ai" (KI); Technik/Wissenschaft → s="ki" (Technologie). Börsen-/IBEX-Tagesberichte → Business. Trailer/Album-Reviews → Film/Musik-Aufgaben.

## 6. Veröffentlichen
- PYTHONHASHSEED=1 python3 build.py muss fehlerfrei laufen; git pull --rebase vor jedem push.
- GitHub-Action prüfen per Bash: `gh run list -R Filmpartner24/terraworldnews -L 3` (nicht per WebFetch – Repo ist privat). Ist der letzte Lauf rot: 2 Min. warten, erneut prüfen; bleibt er rot, im Problem-Hinweis melden.
- build.py, Design, Workflows nur ändern, wenn Nedy es in einem Gespräch ausdrücklich verlangt – geplante Aufgaben ändern keinen Code (fehlende Teamnamen u. Ä. im Bericht melden).

## 7. Benachrichtigung (Nedys Wunsch: nur Berichte per E-Mail, sonst nur bei Problemen)
- Bei Problemen (Lauf konnte nicht veröffentlichen, Action rot, deutlich weniger als die Soll-Anzahl, Daten-/Videoprüfung unmöglich, Tagessperre unklar): am Ende PushNotification (status "proactive") mit <routine_summary>Problem in einem Satz + was fehlt</routine_summary>.
- Läuft alles normal: KEINE PushNotification (Ausnahmen: Besucher-Tages-/Wochenbericht immer; Leben & Alltag: Hinweis „Entwurf wartet auf Freigabe“).
