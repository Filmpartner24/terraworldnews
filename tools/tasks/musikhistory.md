TERRA WORLD NEWS (terraworldnews.com) – Musik-Kategorie MUSIC HISTORY (BG „Музикална история“ /muzika/muzikalna-istoriya/, DE /de/musik/music-history/, EN /en/music/music-history/). Eingeführt am 31.10.2026 auf Nedys Wunsch: täglich 2 historische Konzerte, ZUSÄTZLICH zu allen anderen Musik-Meldungen. Chefredakteur: Nedy John Cross (Bericht auf Deutsch). Arbeite selbstständig, ohne Rückfragen. Zuerst tools/tasks/_regeln.md lesen – die gemeinsamen Regeln gehen vor.

IDEE: Legendäre, ältere Konzerte (etwa 1960er bis 2000er) als eingebettetes Video mit gut recherchiertem Begleittext – zeitlos, wird lange gesucht und gelesen. Auf der Musik-Seite erscheinen die neuesten 4 im Band „Music History“ und unter dem Genre-Raster als breite Kachel.

TAGESSPERRE: Enthält content/<heute>-musikhistory.json schon ≥ 2 Items, nichts hinzufügen (außer der Starttext sagt NACHHOLLAUF/ZUSÄTZLICH).

AUFTRAG: genau 2 neue Items pro Tag, jedes mit Video (Pflicht). Möglichst 2 verschiedene Genres/Jahrzehnte; über die Woche abwechseln: Rock, Hard Rock & Metal, Pop, Soul & Funk, Jazz & Blues, Punk/New Wave, Singer-Songwriter, Deutschrock, gelegentlich Bulgarien (BNT-Archiv: z. B. Щурците, ФСБ, Сигнал, Лили Иванова, Ахат). Bekannte Jahrestage bevorzugen (Konzert heute vor X Jahren, Geburtstag/Todestag des Künstlers, Albumjubiläum) – nur wenn das Datum belegt ist.
KEINE WIEDERHOLUNG: weder dasselbe Video noch dasselbe Konzert noch derselbe Künstler innerhalb von 30 Tagen (alle content/*-musikhistory.json lesen).

VIDEOS – RECHTLICH ENTSCHEIDEND (Nedy 31.10.2026): NUR offizielle Kanäle, die die Rechte haben:
- WDR Rockpalast (offizieller Kanal, viele komplette Konzerte der 70er/80er) – erste Wahl
- Offizielle Künstler-/Band-Kanäle (z. B. AC/DC, Queen Official, Iron Maiden, Metallica, Deep Purple, Pink Floyd, The Rolling Stones, U2, Scorpions, Black Sabbath) sowie VEVO und Label-Kanäle (Universal, Sony, Warner, Rhino, Eagle Rock/Mercury Studios, Earache, Nuclear Blast)
- Sender- und Festivalarchive: Radio Bremen „Beat-Club“, Montreux Jazz Festival, BBC/BBC Archive, ORF, ZDF/ARD-Kanäle, BNT (БНТ архив), Ina Archive
NIE: Fan-, Sammler- oder Re-Upload-Kanäle (z. B. private Namen, „…Fan“, „Live Archive“, „Rare Concerts“), selbst zusammengeschnittene „Revised/Restored Editions“, Bootlegs, Kanäle ohne erkennbare Rechteinhaberschaft. Im Zweifel weglassen. Hintergrund: Einbetten erkennbar unerlaubter Uploads auf einer werbefinanzierten Seite kann eine Urheberrechtsverletzung sein (EuGH), außerdem werden solche Videos oft gelöscht.
Video-ID nur aus tatsächlich gesehener URL; JEDE ID über die Download-Brücke prüfen (_regeln.md Nr. 3, Ordner bridge/musikhistory/): gültig nur, wenn author_name ein erlaubter offizieller Kanal ist und der Titel zum Konzert passt. yt {"id","ch","kind":"video","t":{bg,de,en}}. In Deutschland abspielbar (Ländersperren beachten; im Zweifel anderes Video).

RECHERCHE (Begleittext): WebSearch + WebFetch. Quellen: Künstler-/Bandseiten, Senderseiten (wdr.de/rockpalast, BNT), setlist.fm (nur für Setlist-Angaben), AllMusic, Rolling Stone, Classic Rock, laut.de, Musikexpress, Wikipedia nur ergänzend (Fakten möglichst zusätzlich belegen). Mindestens 2 Quellen pro Item. Jede Angabe (Datum, Ort, Besetzung, Setlist, Zahlen, Zitate) muss in einer abgerufenen Quelle stehen; Anekdoten nur belegt.
TEXT je Item (bg/de/en, inhaltsgleich): t ≤ 90 (z. B. „AC/DC live im Rockpalast 1979: …“), d ≤ 220, body = LISTE mit 3 Absätzen: (1) Wann, wo, Anlass – was man im Video sieht; (2) Besetzung und Setlist-Höhepunkte; (3) Einordnung – warum das Konzert/die Ära wichtig war, was danach kam. facts = 3–5 kurze Punkte (Datum, Ort, Besetzung, Dauer/Länge des Mitschnitts, Quelle des Videos).

ITEM-FORMAT in content/<YYYY-MM-DD>-musikhistory.json ({"date","items":[…]}; existiert die Datei, anhängen): {"id": latin-slug-<Datum> (einmalig), "s":"musik", "sub":"mhistory", optional "subs":[Genre-Schlüssel aus musik.md, max. 2, z. B. ["rock"]], "kl":{"de":"Music History","bg":"Музикална история","en":"Music History"}, "time":"HH:MM" (nie in der Zukunft), "src":[{n,u}…], "yt":{…}, "img":{…}, "bg"/"de"/"en":{"t","d","body","facts"}}.

BILDER: JEDES Item braucht ein img (Video-Titelbild). Wikimedia Commons über candidates/<YYYY-MM-DD>-musikhistory/requests.json: möglichst ein frei lizenziertes Foto des Künstlers/der Band, idealerweise aus der Zeit des Konzerts (Commons hat viele Konzertfotos der 70er/80er, z. B. aus Nationaal Archief, Bundesarchiv, Fotos von Konzertfotografen unter CC BY-SA); sonst Veranstaltungsort (Westfalenhalle, Grugahalle, Apollo, Wembley …). alt mit „(Archivbild)“ und Jahr. Nur eindeutig identifizierte Personen. Keine Video-Standbilder, Plattencover, Plakate. Gibt es nichts Passendes: Musikvideo-Grafik nach _regeln.md Nr. 4 (python3 tools/video_card.py content/<Datei>.json). Kein Foto doppelt innerhalb von 7 Tagen in Musik-Dateien.

FAKTENCHECK: ein unabhängiger Prüfer-Subagent prüft Datum, Ort, Besetzung, Setlist-Angaben, Zitate und vor allem die Kanal-Berechtigung des Videos; Fehler korrigieren oder Item ersetzen.

VERÖFFENTLICHEN: Python-Prüfung (2 neue Items, s="musik", sub="mhistory", jedes mit yt und img; body Listen; Längen; ids einmalig in content/<heute>*.json). PYTHONHASHSEED=1 python3 build.py fehlerfrei; Stichprobe out/de/musik/music-history/index.html. git add content candidates bridge static/assets/news; Commit „Music History <Datum>“ mit den Attributionszeilen der Sitzung; git pull --rebase; git push. Danach Fotos und Cloudflare-Status nach _regeln.md Nr. 6 prüfen; candidates/ und bridge/musikhistory/ in einem Folge-Commit löschen.

BERICHT kurz auf Deutsch: die 2 Konzerte (Künstler, Jahr, Ort), Video-Kanal, was weggelassen wurde. PushNotification nur bei Problemen (_regeln.md Nr. 7).

REGELN: Nur content/, candidates/, bridge/ und static/assets/news/ ändern; Design und build.py nicht anfassen; keine Logins, Konten, Zahlungen. Videos nur eingebettet, nie heruntergeladen.
