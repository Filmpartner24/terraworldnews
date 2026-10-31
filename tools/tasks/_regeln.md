# TERRA WORLD NEWS – Gemeinsame Regeln für ALLE geplanten Aufgaben (Stand 06.10.2026)

Diese Regeln gelten für jede Aufgabe und gehen bei Widersprüchen der jeweiligen Aufgabenanweisung UND der Skill „terra-daily-edition“ vor (die Skill ist in Teilen veraltet, z. B. „77 Meldungen“, alte Breaking-Zeiten).

## 1. Aktuelle Eckdaten
- Tagesausgabe: genau 80 Meldungen (Deutschland 12 inkl. 2–3 Berlin und 1 Deutschland–Bulgarien, Bulgarien 11, Welt 15, Europa 8, Technologie [s="ki"] 8, Wirtschaft 6, Energie 3, Klima 3, Leben & Alltag 9, Kultur 5). Alle anderen Aufgaben kommen ZUSÄTZLICH.
- Breaking: 5 Updates täglich (08:00, 11:00, 15:30, 18:30, 21:00), je 8 Meldungen.
- Musik: 8 Meldungen pro Tag (3 Reviews + 5 News) in 21 Genre-Kategorien (Jazz & Blues zusammen = sub "jazz"; Soul & Funk = sub "soulfunk") („sub“/„subs“, siehe musik.md; Nedy 26.10.2026).
- Pop-Folk: 9 Meldungen pro Tag (3 Musikvideos, 3 Alben, 3 News/Konzerte) aus 7 Ländern, eigene Aufgabe tools/tasks/popfolk.md, Datei content/<Datum>-popfolk.json (Nedy 26.10.2026).
- Musik-Genres Rock, Metal, Indie & Alternative, Pop, Hip-Hop: je 9 Meldungen pro Tag (3 Musikvideos, 3 Album-Reviews, 3 Konzerte/News), Aufgabe tools/tasks/genres.md, Datei content/<Datum>-g-<genre>.json (Nedy 26.10.2026).
- Leben & Alltag → Gesundheit: 3 Artikel + 1 Video pro Tag, eigene Aufgabe tools/tasks/gesundheit.md, Datei content/<Datum>-gesundheit.json, s="leben", sub="gesundheit" (Nedy 31.10.2026).
- Musik → Music History: 2 historische Konzerte pro Tag mit Video NUR von offiziellen Kanälen (WDR Rockpalast, Künstler-/Label-Kanäle, Senderarchive), eigene Aufgabe tools/tasks/musikhistory.md, Datei content/<Datum>-musikhistory.json, s="musik", sub="mhistory" (Nedy 31.10.2026).
- Games: 6 Meldungen pro Tag (3 Reviews mit Video „Die neusten Spiele – Reviews“ + 3 Game-News; Nedy 10.10.2026).
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
Videos nur einbetten (yt-Feld), nie herunterladen. In Deutschland abspielbar: Spiel-/Kampf-Highlights nur von deutschen Sender-/Liga-Kanälen (sportstudio fußball/ZDF, Sportschau, DAZN, Sky Sport DE, DFB, RTL Sport). NIE den YouTube-Kanal „Bundesliga“ (Nedy 26.10.2026: dessen Spiel-Highlights zeigen in Deutschland/Bulgarien „Video nicht verfügbar – Der Uploader stellt dieses Video in deinem Land nicht zur Verfügung“; noembed erkennt die Ländersperre nicht) – auch nicht für Interviews; ausländische Liga-/Sender-Kanäle (z. B. Premier League, TNT, beIN, Sky Sports UK) nur für Interviews/Pressekonferenzen. Nachrichten: offizielle Sender-/Agentur-/Institutions-/Firmenkanäle. Nie Fan- oder Re-Upload-Kanäle.
Andere gesperrte Datenquellen (z. B. match.uefa.com, standings.uefa.com) ebenfalls über die Brücke holen (`<URL> <dateiname>.json`).

## 4. BILDER (rechtssicher)
- JEDE Meldung braucht ein img – auch Meldungen mit Video (das Bild dient als Video-Titelbild). Vor dem Push mit Python prüfen: kein Item ohne img, und jede Datei static<img.f> existiert (Commons-Fotos kommen erst nach dem Action-Lauf – dann nach git pull nachprüfen; fehlt eines, Titelgrafik einsetzen).
- Nur Wikimedia Commons (CC BY / BY-SA / CC0 / PD / OGL) über candidates/<ordner>/requests.json → Kontaktbogen ansehen → img {"f":"/assets/news/<Datum>/<id>.webp","w":1200,"h":675,"art","lic","page","alt":{bg,de,en}} (Pfad IMMER mit führendem „/“; art bei CC BY/BY-SA nie leer), Symbol-/Archivbild im alt kennzeichnen.
- AUSNAHME (Nedy 11.10.2026): Exklusiv-Beiträge der eigenen Reihe „FilmPartner24 – History“ nutzen IMMER die Reihen-Titelgrafik img {"f":"/assets/exklusiv/filmpartner24-history.webp","w":1200,"h":675,"own":true,"cr":{… "© FilmPartner24"},"alt":{…}} (eigenes Bildmaterial von FilmPartner24).
- NIEMALS: YouTube-Vorschaubilder, Video-Standbilder, Film-Stills, Plakate, Album-/Spiel-Cover, Agentur-/Pressefotos, KI-Bilder – auch nicht mit „©“-Vermerk (ein ©-Vermerk ist keine Lizenz).
- MUSIK MIT VIDEO (Nedy 26.10.2026): Musik-Items mit yt und ohne Commons-Foto bekommen statt der dunklen Titelgrafik die farbige TWN-Musikvideo-Grafik: nach dem Setzen der Titelgrafik `python3 tools/video_card.py content/<Datei>.json` ausführen (nutzt automatisch freie Starfotos aus content/musik/popfolk-stars.json). Die GitHub-Action führt das Skript zusätzlich bei jedem Push aus – trotzdem selbst vorher ausführen, damit keine Kachel zwischenzeitlich dunkel ist. Ziel: JEDE Musik-Videokachel zeigt entweder ein Foto des Künstlers oder die farbige Musikvideo-Grafik. KEINE DOPPELTEN FOTOS (Nedy 26.10.2026): Dasselbe Foto (gleiche Commons-Seite) darf bei Musik-Meldungen innerhalb von 7 Tagen nur einmal vorkommen – sonst halten Leser es für dasselbe Video. Vor der Fotowahl die img.page der Musik-Dateien der letzten 7 Tage prüfen und ein anderes Foto wählen; das Skript ersetzt verbliebene Dubletten bei Video-Items automatisch durch die Musikvideo-Grafik.
- Gibt es kein passendes Commons-Bild: eigene Titelgrafik erzeugen – python3 -c "import sys; sys.path.insert(0,'tools'); import title_card; title_card.make('static/assets/news/<Datum>/<id>-tg.webp','<RUBRIK>','<deutscher Titel>','<Farbe>')" und img {"f":"/assets/news/<Datum>/<id>-tg.webp","w":1200,"h":675,"own":true,"alt":{bg,de,en}}. Ergebnisgrafiken (Sport) wie bisher mit own:true.

## 5. Inhalt und Recht
- Jede Meldung: bg/de/en (t ≤ 90, d ≤ 220), body = JSON-Liste mit 2–3 Absätzen, Quellen src [{n,u}] nur mit tatsächlich gesehenen, datierten URLs; eigene Worte; Zitate nur wörtlich belegt mit Sprecher; Gerüchte nur gekennzeichnet.
- Pressekodex: Unschuldsvermutung, keine identifizierenden Details von Verdächtigen/Opfern, Verletzungen/Erkrankungen (auch bei Sportlern) nur nach offizieller Mitteilung von Person/Team/Verband, sachlich, ohne medizinische Spekulation.
- time = Veröffentlichungszeit (HH:MM Berlin), NIE in der Zukunft.
- Nichts wiederholen, was in den letzten Tagen schon auf der Seite steht: vor dem Schreiben die relevanten content/*.json lesen (mindestens content/<heute>*.json und content/<gestern>*.json, dazu die eigenen Rubrikdateien der letzten 7 Tage).
- RAUMFAHRT (Nedy 09.10.2026): nie als normale Technologie- oder KI-Meldung. Raumfahrt-Meldungen (Raketen, Satelliten, Sonden, Teleskope, ISS, NASA/ESA/SpaceX) gehören in den Unterpunkt Technologie → Raumfahrt: s="ki", "sub":"raumfahrt", "kl":{"de":"Raumfahrt","bg":"Космос","en":"Space"} (erscheinen nur dort, nicht auf der Technologie-Hauptseite).
- Abgrenzung: Autos (Modelle, Marken, Verkaufszahlen) → Auto-Aufgabe; Tagesausgabe/Technologie nur aus Technik-Sicht (Batterie, autonomes Fahren, Laden). KI-Modelle/KI-Firmen → s="ai" (KI); Technik/Wissenschaft → s="ki" (Technologie). Börsen-/IBEX-Tagesberichte → Business. Trailer/Album-Reviews → Film/Musik-Aufgaben.

- NOVINI.BG (Nedy 26.10.2026): novini.bg ist in Bulgarien sehr beliebt und gehört ab sofort zu den Pflicht-Quellen für Nachrichten und bulgarische Themen (Tagesausgabe, Breaking, Bulgarien, Welt, Pop-Folk/Boulevard). Bei jeder Themenauswahl die Startseite https://novini.bg/ lesen (WebFetch) und prüfen, welche Geschichten dort oben stehen bzw. meistgelesen sind – täglich mehrere Themen von dort aufgreifen. RECHTLICH: novini.bg nur als Themen- und Faktenquelle – immer eigene Formulierung, nie Text, Überschriften, Fotos oder Videos übernehmen; den gelesenen novini.bg-Artikel immer in src verlinken (Name „Novini.bg“); wichtige Fakten möglichst mit einer zweiten Quelle (BTA, BNT, bTV, Nova, Dnevnik) bestätigen; Meinungsbeiträge und Gerüchte von dort nicht als Tatsachen übernehmen.

- RUMÄNIEN (Nedy 26.10.2026): Rumänien-Nachrichten und Skandal-Themen (Korruption, Politik-Affären, Justiz, Polizei-Einsätze, Promi-/Manele-Skandale) sind gewünscht – Leser sollen sehen, „wie es in solchen Ländern zugeht“. Lieblingsquelle ist Libertatea (libertatea.ro), sehr beliebt in Rumänien. ACHTUNG: libertatea.ro ist aus der Cloud für WebFetch gesperrt – NIE per curl/Python/Archiv umgehen; Libertatea-Artikel nur nutzen, wenn sie über WebSearch-Treffer tatsächlich lesbar sind. Sonst gleiche Themen über erreichbare seriöse Quellen: Digi24 (digi24.ro), HotNews (hotnews.ro), G4Media, Adevărul, Știrile ProTV, dazu Reuters/AP/Euronews. Einordnung: Politik/Gesellschaft/Justiz → s="europa" (Tagesausgabe, Teil der 8 Europa-Meldungen, möglichst 1 Rumänien-Thema pro Tag); Manele-/Promi-Skandale → Pop-Folk (land "ro"). Pressekodex streng: Unschuldsvermutung, keine Namen/identifizierenden Details von Verdächtigen und Opfern (außer Amtsträger/Prominente in ihrer öffentlichen Rolle), keine Herkunfts-/Ethnie-Zuschreibung (z. B. Roma) ohne begründetes öffentliches Interesse und amtliche Quelle, keine Häme über das Land – sachlich, eigene Worte, Quelle verlinkt.

- ARCHIV (Nedy 27.10.2026): Alle Rubriken und Unterrubriken löschen nichts mehr – ältere Artikel und Videos stehen auf Seite 2, 3 … (nummerierte Seiten unten, 30 Beiträge pro Seite). Deshalb jede Meldung sorgfältig mit s/sub einordnen; die Seiten wachsen dauerhaft.

## 6. Veröffentlichen
- PYTHONHASHSEED=1 python3 build.py muss fehlerfrei laufen; git pull --rebase vor jedem push.
- FOTOS LIVE PRÜFEN (Nedy 28.10.2026: „Bitte immer darauf achten, dass Fotos drin sind – sonst sehr unprofessionell!“): Commons-Fotos lädt erst die Action nach dem Push und committet sie als „Update edition and photos“. Nach dem eigenen Push ~3 Min. warten, git pull, prüfen, dass JEDE static<img.f> der eigenen Meldungen existiert, UND den Cloudflare-Status des neuesten Commits prüfen: `gh api repos/Filmpartner24/terraworldnews/commits/$(git rev-parse origin/main)/check-runs --jq '.check_runs[]|[.name,.conclusion]|@tsv'`. Ist „Cloudflare Pages“ dort failure, ist die Seite ohne Fotos live (Platzhalter-Kachel) → mit einer kleinen echten Korrektur an den eigenen Meldungen erneut pushen (ohne [CF-Pages-Skip]) und wieder prüfen, bis ein Commit mit den Fotos „success“ hat. Erst dann ist der Lauf fertig.
- GitHub-Action prüfen per Bash: `gh run list -R Filmpartner24/terraworldnews -L 3` (nicht per WebFetch – Repo ist privat). Ist der letzte Lauf rot: 2 Min. warten, erneut prüfen; bleibt er rot, im Problem-Hinweis melden.
- build.py, Design, Workflows nur ändern, wenn Nedy es in einem Gespräch ausdrücklich verlangt – geplante Aufgaben ändern keinen Code (fehlende Teamnamen u. Ä. im Bericht melden).

## 7. Benachrichtigung (Nedys Wunsch: nur Berichte per E-Mail, sonst nur bei Problemen)
- Bei Problemen (Lauf konnte nicht veröffentlichen, Action rot, deutlich weniger als die Soll-Anzahl, Daten-/Videoprüfung unmöglich, Tagessperre unklar): am Ende PushNotification (status "proactive") mit <routine_summary>Problem in einem Satz + was fehlt</routine_summary>.
- Läuft alles normal: KEINE PushNotification (Ausnahmen: Besucher-Tages-/Wochenbericht immer; Leben & Alltag: Hinweis „Entwurf wartet auf Freigabe“).

## 8. Türkisch und Spanisch (seit 27.10.2026, Nedy)
- Die tr/es-Fassungen entstehen AUTOMATISCH in der GitHub Action (tools/translate.py, Anthropic-API) aus dem DEUTSCHEN Text jeder Meldung und liegen in translations/<tr|es>/<Datum>.json. Aufgaben schreiben weiterhin nur bg/de/en – deshalb den deutschen Text besonders sorgfältig formulieren (Zitate, „mutmaßlich“, Zuordnungen).
- translations/ und i18n/ nie von Hand ändern. Wird ein deutscher Text später korrigiert, wird die Übersetzung automatisch erneuert.
- translations/flagged.json = Übersetzungen, die die automatische Prüfung (Zahlen, Zitate, Absätze, Längen) nicht bestanden haben und deshalb NICHT veröffentlicht sind. translations/status.json "ok": false = API nicht nutzbar (Guthaben/Limit/Schlüssel) → im Bericht als Problem melden.
