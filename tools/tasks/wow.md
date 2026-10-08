TERRA WORLD NEWS (terraworldnews.com) – Rubrik WOW (ganz hinten im Menü; DE /de/wow/, EN /en/wow/, BG /wow/) und Unterrubrik SPORT → EXTREMSPORT (DE /de/sport/extremsport/). Beides reine Video-Seiten (Video-Wand, kurzer Titel). Chefredakteur: Nedy John Cross (Bericht auf Deutsch). Arbeite selbstständig, ohne Rückfragen. Läuft täglich (Nedys Vorgabe vom 08.10.2026). Zuerst tools/tasks/_regeln.md lesen – die gemeinsamen Regeln gehen vor.

TAGESSPERRE: Enthält content/<heute>-wow.json schon ≥ 6 Items UND content/<heute>-extremsport.json ≥ 3 Items, nichts hinzufügen (außer der Starttext sagt NACHHOLLAUF/ZUSÄTZLICH).

AUFTRAG:
A) WOW: genau 6 neue Videos, je 2 pro Kategorie (Feld "wc"):
   - "rec" Rekorde & Kunststücke: Guinness World Records (offizieller Kanal).
   - "nat" Natur & Tiere: BBC Earth, National Geographic, Smithsonian Channel (nur offizielle Kanäle; keine „Full Episode“-Videos).
   - "space" Raumfahrt: NASA, ESA (European Space Agency, ESA), ggf. DLR.
B) EXTREMSPORT: genau 3 neue Videos: Red Bull, GoPro, extreme Weltrekorde (z. B. Guinness World Records, Red Bull Media House, offizielle Kanäle von Weltverbänden wie UCI, World Surf League, IFSC).
Nur Videos der letzten ~30 Tage bevorzugen (ältere nur, wenn besonders spektakulär); nichts wiederholen, was in content/*-wow.json bzw. content/*-extremsport.json der letzten 60 Tage steht (yt.id vergleichen).

0. SETUP: Repo Filmpartner24/terraworldnews (Branch main) mit add_repo (access push) anhängen, nach /home/claude/terra klonen bzw. git pull.

1. VIDEOS FINDEN: Video-ID nur aus tatsächlich gesehener URL (WebSearch/WebFetch der Kanalseiten, offizielle Websites, Presseseiten), nie raten. Jede ID über die Download-Brücke prüfen (_regeln.md Nr. 3): author_name muss exakt der offizielle Kanal sein (z. B. „Guinness World Records“, „BBC Earth“, „National Geographic“, „Smithsonian Channel“, „NASA“, „European Space Agency, ESA“, „Red Bull“, „GoPro“), Titel passt. Fehler/401/403 = weglassen. Videos nur einbetten, nie herunterladen. Keine Reddit-, TikTok-, Fan- oder Re-Upload-Quellen (Urheberrecht).

2. ITEM-FORMAT:
   - WOW in content/<YYYY-MM-DD>-wow.json ({"date","items":[…]}; existiert die Datei, anhängen): {"id": "wow-<slug>-<Datum>", "s":"wow", "wc":"rec|nat|space", "time":"HH:MM" (nie in der Zukunft), "src":[{"n":"YouTube · <Kanal>","u":"https://www.youtube.com/watch?v=<ID>"},{"n":"<Kanal>","u":"<Kanalseite>"}], "yt":{"id","ch","kind":"video","t":{bg,de,en: Original-Videotitel}}, "img":{eigene Titelgrafik, s. u.}, "de"/"bg"/"en": {"t": kurzer Titel ≤ 60 Zeichen, "d": ein Satz ≤ 160 Zeichen, "body":[derselbe Satz]}}.
   - EXTREMSPORT in content/<YYYY-MM-DD>-extremsport.json: wie oben, aber "s":"sport", "sub":"extremsport", "kl":{"de":"Extremsport","bg":"Екстремни спортове","en":"Extreme sports"}, id "ext-<slug>-<Datum>", kein "wc".
   - Texte nur beschreiben, was Titel/Videobeschreibung/offizielle Quelle belegen (Namen nur, wenn eindeutig belegt). Format-Vorlage: content/2026-10-08-wow.json und content/2026-10-08-extremsport.json.

3. BILD (Pflichtfeld, wird auf der Video-Wand nicht angezeigt, aber auf der Artikelseite): eigene Titelgrafik – python3 -c "import sys; sys.path.insert(0,'tools'); import title_card; title_card.make('static/assets/news/<Datum>/<id>-tg.webp','WOW','<deutscher Titel>','#ff2d55')" (Extremsport: Rubrik 'Extremsport', Farbe '#e85d04'); img {"f":"/assets/news/<Datum>/<id>-tg.webp","w":1200,"h":675,"own":true,"alt":{… „Eigene Titelgrafik der Redaktion: …“}}. Nie YouTube-Vorschaubilder.

4. VERÖFFENTLICHEN: Python-Prüfung (Anzahl, jedes Item mit yt und img, Datei vorhanden, ids einmalig in content/<heute>*.json, keine yt.id doppelt in den letzten 60 Tagen). PYTHONHASHSEED=1 python3 build.py fehlerfrei (bei SyntaxError python3.12); Stichprobe out/de/wow/index.html und out/de/sport/extremsport/index.html. git add content static/assets/news; Commit „WOW + Extremsport <Datum>“ mit den Attributionszeilen der Sitzung; git pull --rebase; git push; bridge/wow/ danach in einem Folge-Commit löschen.

5. BERICHT kurz auf Deutsch: die 9 Titel mit Kanal. PushNotification nur bei Problemen (_regeln.md Nr. 7).

REGELN: Nur content/, bridge/ und static/assets/news/ ändern; Design und build.py nicht anfassen; keine Logins, Konten, Zahlungen.
