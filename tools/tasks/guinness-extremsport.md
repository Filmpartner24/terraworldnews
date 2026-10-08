TERRA WORLD NEWS (terraworldnews.com) – Unterpunkt LEBEN & ALLTAG → GUINNESS RECORDS (DE /de/leben-alltag/guinness-records/, EN /en/everyday-life/guinness-world-records/, BG /zhivot/rekordi-gines/) und SPORT → EXTREMSPORT (DE /de/sport/extremsport/). Beides reine Video-Seiten (Video-Wand, kurzer Titel). Die Rubrik WOW wurde am 09.10.2026 auf Nedys Wunsch entfernt – keine WOW-Inhalte mehr anlegen. Chefredakteur: Nedy John Cross (Bericht auf Deutsch). Arbeite selbstständig, ohne Rückfragen. Läuft täglich. Zuerst tools/tasks/_regeln.md lesen – die gemeinsamen Regeln gehen vor.

TAGESSPERRE: Enthält content/<heute>-guinness.json schon ≥ 1 Item UND content/<heute>-extremsport.json ≥ 3 Items, nichts hinzufügen (außer der Starttext sagt NACHHOLLAUF/ZUSÄTZLICH).

AUFTRAG:
A) GUINNESS RECORDS: genau 1 neues Video pro Tag vom offiziellen YouTube-Kanal „Guinness World Records“ (möglichst aus den letzten Tagen).
B) EXTREMSPORT: genau 3 neue Videos: Red Bull, GoPro, extreme Weltrekorde (z. B. Guinness World Records, offizielle Kanäle von Weltverbänden wie UCI, World Surf League, IFSC).
Nichts wiederholen, was in content/*-guinness.json bzw. content/*-extremsport.json der letzten 60 Tage steht (yt.id vergleichen).

0. SETUP: Repo Filmpartner24/terraworldnews (Branch main) mit add_repo (access push) anhängen, nach /home/claude/terra klonen bzw. git pull.

1. VIDEOS FINDEN: Video-ID nur aus tatsächlich gesehener URL (WebSearch/WebFetch der Kanalseiten, offizielle Websites, Presseseiten), nie raten. Jede ID über die Download-Brücke prüfen (_regeln.md Nr. 3): author_name muss exakt der offizielle Kanal sein (z. B. „Guinness World Records“, „BBC Earth“, „National Geographic“, „Smithsonian Channel“, „NASA“, „European Space Agency, ESA“, „Red Bull“, „GoPro“), Titel passt. Fehler/401/403 = weglassen. Videos nur einbetten, nie herunterladen. Keine Reddit-, TikTok-, Fan- oder Re-Upload-Quellen (Urheberrecht).

2. ITEM-FORMAT:
   - GUINNESS in content/<YYYY-MM-DD>-guinness.json ({"date","items":[…]}; existiert die Datei, anhängen): {"id": "gwr-<slug>-<Datum>", "s":"leben", "sub":"guinness", "kl":{"de":"Guinness Records","bg":"Рекорди на Гинес","en":"Guinness World Records"}, "time":"HH:MM" (nie in der Zukunft), "src":[{"n":"YouTube · <Kanal>","u":"https://www.youtube.com/watch?v=<ID>"},{"n":"<Kanal>","u":"<Kanalseite>"}], "yt":{"id","ch","kind":"video","t":{bg,de,en: Original-Videotitel}}, "img":{eigene Titelgrafik, s. u.}, "de"/"bg"/"en": {"t": kurzer Titel ≤ 60 Zeichen, "d": ein Satz ≤ 160 Zeichen, "body":[derselbe Satz]}}.
   - EXTREMSPORT in content/<YYYY-MM-DD>-extremsport.json: wie oben, aber "s":"sport", "sub":"extremsport", "kl":{"de":"Extremsport","bg":"Екстремни спортове","en":"Extreme sports"}, id "ext-<slug>-<Datum>".
   - Texte nur beschreiben, was Titel/Videobeschreibung/offizielle Quelle belegen (Namen nur, wenn eindeutig belegt). Format-Vorlage: content/2026-10-08-guinness.json und content/2026-10-08-extremsport.json.

3. BILD (Pflicht; wird auf der Video-Wand als Vorschaubild gezeigt – Nedys Wunsch 09.10.2026): passendes Wikimedia-Commons-Foto (CC BY/BY-SA/CC0/PD) zum Thema des Videos über candidates/<YYYY-MM-DD>-vid/requests.json → push → ~3 Min. → git pull → Kontaktbogen ansehen → img {"f":"/assets/news/<Datum>/<id>.webp","w":1200,"h":675,"art","lic","page","alt":{bg,de,en} mit „(Symbolbild)“/„(Archivbild)“}; keine Logos/Marken als Motiv, keine erkennbaren Privatpersonen in heiklen Situationen. NIE YouTube-Vorschaubilder oder Video-Standbilder (Urheberrecht + Datenschutz). Nur wenn wirklich nichts passt: eigene Titelgrafik (tools/title_card.py, own:true) – dann zeigt die Kachel eine Farbfläche.

4. VERÖFFENTLICHEN: Python-Prüfung (Anzahl, jedes Item mit yt und img, Datei vorhanden, ids einmalig in content/<heute>*.json, keine yt.id doppelt in den letzten 60 Tagen). PYTHONHASHSEED=1 python3 build.py fehlerfrei (bei SyntaxError python3.12); Stichprobe out/de/leben-alltag/guinness-records/index.html und out/de/sport/extremsport/index.html. git add content static/assets/news; Commit „Guinness + Extremsport <Datum>“ mit den Attributionszeilen der Sitzung; git pull --rebase; git push; bridge/guinness/ danach in einem Folge-Commit löschen.

5. BERICHT kurz auf Deutsch: die 4 Titel mit Kanal. PushNotification nur bei Problemen (_regeln.md Nr. 7).

REGELN: Nur content/, bridge/ und static/assets/news/ ändern; Design und build.py nicht anfassen; keine Logins, Konten, Zahlungen.
