TERRA WORLD NEWS (terraworldnews.com) – Sport-Unterrubrik BASKETBALL (DE /de/sport/basketball/, EN /en/sport/basketball/, BG /sport/basketbol/). Eingeführt am 31.10.2026 auf Nedys Wunsch: NBA, EuroLeague, easyCredit BBL (Deutschland), FIBA/Nationalteams (Deutschland ist Weltmeister 2023), Bulgarien (НБЛ, Nationalteam) gelegentlich. Chefredakteur: Nedy John Cross (Bericht auf Deutsch). Arbeite selbstständig, ohne Rückfragen. Zuerst tools/tasks/_regeln.md lesen – die gemeinsamen Regeln gehen vor.

TAGESSPERRE: Enthält content/<heute>-basketball.json schon ≥ 4 Items, nichts hinzufügen (außer der Starttext sagt NACHHOLLAUF/ZUSÄTZLICH).

AUFTRAG: genau 4 neue Items pro Tag:
 A) 3 NEWS – möglichst verteilt: 1× NBA (Ergebnisse der Nacht, Top-Leistungen, Transfers/Verletzungen nur nach offizieller Mitteilung, deutsche NBA-Spieler wie Franz und Moritz Wagner, Dennis Schröder, Daniel Theis …), 1× EuroLeague/EuroCup (u. a. FC Bayern München, ALBA Berlin), 1× easyCredit BBL oder FIBA/Nationalteams (Deutschland, Bulgarien). Ergebnisse, Tabellen-Einordnung, Spielerporträts, Transfers.
 B) 1 VIDEO-ITEM (Pflicht): Highlights/Analysen NUR von offiziellen Rechteinhaber-Kanälen, die ihre eigenen Videos hochladen: NBA, EuroLeague Basketball, easyCredit BBL, FIBA, Basketball Bundesliga/MagentaSport (nur offizielle Kanäle), Vereinskanäle (ALBA BERLIN, FC Bayern Basketball), DBB (Deutscher Basketball Bund). NIE Re-Upload-, Fan- oder Compilation-Kanäle. Video-ID nur aus tatsächlich gesehener URL; Prüfung über die Download-Brücke (_regeln.md Nr. 3, Ordner bridge/basketball/). yt {"id","ch","kind":"video","t":{bg,de,en}}. In Deutschland abspielbar. Wenn kein Video sicher prüfbar: Video-Item weglassen und im Bericht nennen.
 Feld "hk" je Item: "nba" | "euroleague" | "bbl" | "fiba" | "bulgarien".

AKTUALITÄT: Nachrichten ≤ 2 Tage (Spielergebnisse vom letzten Spieltag/der letzten Nacht). Nichts wiederholen, was in content/*-basketball.json der letzten 7 Tage oder heute in content/<heute>*.json steht.

RECHERCHE: WebSearch (mode "extended" bei Ergebnissen) + WebFetch. Quellen: nba.com, euroleaguebasketball.net, easycredit-bbl.de, fiba.basketball, basketball-bund.de, Vereinsseiten, ESPN, AP, Reuters, kicker, Sport1, sportschau, BTA/Gong.bg/Sportal.bg für Bulgarien. Mindestens 2 Quellen pro Item. Jede Zahl (Punkte, Rebounds, Ergebnisse, Tabellenplätze), jeder Name, jedes Datum und Zitat muss in einer abgerufenen Quelle stehen.

ITEM-FORMAT in content/<YYYY-MM-DD>-basketball.json ({"date","items":[…]}; existiert die Datei, anhängen): {"id": latin-slug-<Datum> (einmalig), "s":"sport", "sub":"basketball", "hk":"…", "time":"HH:MM" (nie in der Zukunft), "src":[{n,u}…], "img":{…} (JEDES Item), optional "yt", "bg"/"de"/"en": {"t" ≤90, "d" ≤220, "body": LISTE mit 3 Absätzen, optional "facts"}}. Bulgarisch und Englisch inhaltsgleich mit Deutsch.

BILDER: Wikimedia Commons über candidates/<YYYY-MM-DD>-basketball/requests.json (Spielszenen, Arenen wie Uber Arena Berlin, SAP Garden München, Spieler nur eindeutig identifiziert und frei lizenziert). Keine Video-Standbilder, keine Agenturfotos, keine Vereinslogos. Kein Foto doppelt innerhalb von 7 Tagen. Video-Items brauchen ebenfalls ein Foto (daraus entsteht automatisch das TWN-Thumbnail).

FAKTENCHECK: ein unabhängiger Prüfer-Subagent prüft Ergebnisse, Statistiken, Namen, Daten und die Kanal-Berechtigung des Videos; Fehler korrigieren oder Item ersetzen.

VERÖFFENTLICHEN: Python-Prüfung (4 neue Items, s="sport", sub="basketball", jedes mit img; genau 1 mit yt; body Listen; Längen; ids einmalig). PYTHONHASHSEED=1 python3 build.py fehlerfrei; Stichprobe out/de/sport/basketball/index.html. git add content candidates bridge static/assets/news; Commit „Basketball <Datum>“ mit den Attributionszeilen der Sitzung; git pull --rebase; git push. Danach Fotos und Cloudflare-Status nach _regeln.md Nr. 6 prüfen; candidates/ und bridge/basketball/ in einem Folge-Commit löschen.

BERICHT kurz auf Deutsch: die 3 Schlagzeilen, das Video (Kanal), was weggelassen wurde. PushNotification nur bei Problemen (_regeln.md Nr. 7).

REGELN: Nur content/, candidates/, bridge/ und static/assets/news/ ändern; Design und build.py nicht anfassen; keine Logins, Konten, Zahlungen. Videos nur eingebettet, nie heruntergeladen.
