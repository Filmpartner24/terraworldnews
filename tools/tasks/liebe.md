TERRA WORLD NEWS (terraworldnews.com) – Unterrubrik LIEBE & BEZIEHUNG (unter „Leben & Alltag“; DE /de/leben-alltag/liebe-beziehung/, EN /en/everyday-life/love-relationships/, BG /zhivot/lyubov-i-vrazki/). Chefredakteur: Nedy John Cross (Bericht auf Deutsch). Arbeite selbstständig, ohne Rückfragen. Läuft täglich (Nedys Vorgabe vom 08.10.2026: täglich 3 Artikel, ZUSÄTZLICH zu allen anderen Meldungen). Zuerst tools/tasks/_regeln.md lesen – die gemeinsamen Regeln gehen vor.

TAGESSPERRE: Enthält content/<heute>-liebe.json schon ≥ 3 Items, nichts hinzufügen (außer der Starttext sagt NACHHOLLAUF/ZUSÄTZLICH).

AUFTRAG: genau 3 neue Artikel. Themen, im Wechsel und möglichst verschieden (pro Tag nicht zweimal dieselbe Themengruppe):
1. Liebe & Beziehung: neue Studien und Umfragen (Paarbeziehung, Treue, Eifersucht, Zusammenleben, Heirat/Scheidung, Statistikämter Destatis/NSI/Eurostat).
2. Sexualität: seriöse Studien und Gesundheitsthemen (Kinsey Institute, BIÖG/liebesleben.de, WHO, Universitäten, Fachjournale), Aufklärung, Verhütung, sexuelle Gesundheit – sachlich, nie explizit oder anzüglich.
3. Bekanntschaften & Dating: Dating-Apps und -Portale (Match Group/Tinder, Bumble, Hinge, Parship, Lovoo, elmaz.com …), Trends (Offline-Dating, Speed-Dating, KI im Dating), staatliche Initiativen, Marktzahlen.
4. Erfahrungen mit Bekanntschaften: nur belegte, veröffentlichte Erfahrungsberichte und Reportagen aus seriösen Medien oder Umfragen (keine erfundenen Stimmen, keine Leserbriefe ohne Quelle), dazu Love-Scamming-Fälle mit Polizeiwarnungen und Schutztipps.
5. Skandale: Beziehungs- und Dating-Skandale von öffentlichem Interesse (Prominente nur, wenn sie selbst öffentlich darüber sprechen oder seriöse Medien berichten; Betrugsfälle, Gerichtsurteile, Plattform-Skandale, Datenlecks bei Dating-Apps).
Mindestens 1 Artikel pro Woche mit Bulgarien-Bezug und 1 mit Deutschland-Bezug. Nur Aktuelles (möglichst ≤ 7 Tage, Studien höchstens ~3 Wochen alt); nichts wiederholen, was in content/*-liebe.json der letzten 30 Tage oder heute in anderen content/<heute>*.json steht.

0. SETUP: Repo Filmpartner24/terraworldnews (Branch main) mit add_repo (access push) anhängen, nach /home/claude/terra klonen (oder git pull).

1. RECHERCHE: WebSearch + WebFetch. Quellen: Nachrichtenagenturen (dpa, AFP, Reuters, AP, BTA), Qualitätsmedien (Spiegel, Zeit, SZ, FAZ, tagesschau, BBC, Guardian, NYT, Dnevnik, Mediapool, Sega, bTV, BNT), Fachmedien (PsyPost, Global Dating Insights, IFLScience), Hochschulen, Statistikämter, Polizei-Pressestellen. Boulevard (Bild, Promiflash u. Ä.) nie als einzige Quelle. Jede Zahl, jeder Name, jedes Datum und Zitat muss in einer abgerufenen Quelle stehen; mindestens 2 Quellen pro Artikel; Studien mit Stichprobe, Finanzierung und Einschränkungen nennen.

2. PRESSEKODEX & SCHUTZ: Keine Namen/identifizierenden Details von Privatpersonen, Opfern oder Verdächtigen; Unschuldsvermutung; keine Spekulation über Sexualleben, Orientierung oder Gesundheit konkreter Personen; nichts über Minderjährige im sexuellen Kontext; keine expliziten Beschreibungen. Ton: sachlich, respektvoll, ohne Moralisieren und ohne Werbesprache; keine Empfehlungen für bestimmte Dating-Anbieter, keine Affiliate-Links.

3. ITEM-FORMAT in content/<YYYY-MM-DD>-liebe.json ({"date":"YYYY-MM-DD","items":[…]}; existiert die Datei, anhängen): {"id": latin-slug-<Datum> (einmalig), "s":"leben", "sub":"liebe", "kl":{"de":"Liebe & Beziehung","bg":"Любов и връзки","en":"Love & Relationships"}, "time":"HH:MM" (nie in der Zukunft), "src":[{n,u}…], "img":{…} (JEDES Item), "de"/"bg"/"en": {"t" ≤90, "d" ≤220, "body": LISTE mit 3 Absätzen}}. Bulgarisch und Englisch inhaltsgleich. Optional ein offizielles Video (yt mit "kind":"video", nur Sender/Agenturen/Institutionen, Prüfung über die Download-Brücke nach _regeln.md Nr. 3). Format-Vorlage: content/2026-10-08-liebe.json.

4. BILDER: Wikimedia Commons nur, wenn ein passendes, unverfängliches Motiv existiert (Orte, Gebäude, Institutionen; keine erkennbaren Privatpersonen, keine Paare in intimen Situationen) über candidates/<YYYY-MM-DD>-liebe/requests.json. Sonst eigene Titelgrafik: python3 -c "import sys; sys.path.insert(0,'tools'); import title_card; title_card.make('static/assets/news/<Datum>/<id>-tg.webp','Liebe & Beziehung','<deutscher Titel>','#c26a00')" und img {"f":"/assets/news/<Datum>/<id>-tg.webp","w":1200,"h":675,"own":true,"alt":{bg,de,en} mit „Eigene Titelgrafik der Redaktion: …“}. Nie Stock-, Agentur-, Instagram- oder KI-Bilder.

5. FAKTENCHECK: ein unabhängiger Prüfer-Subagent vergleicht Daten, Zahlen, Namen und Zitate mit den Quellen; Fehler korrigieren oder streichen.

6. VERÖFFENTLICHEN: Python-Prüfung (genau 3 neue Items mit s="leben", sub="liebe"; jedes mit img und existierender Datei; body Liste; ids einmalig in content/<heute>*.json). PYTHONHASHSEED=1 python3 build.py fehlerfrei (bei SyntaxError python3.12 verwenden); Stichprobe out/de/leben-alltag/liebe-beziehung/index.html. git add content candidates static/assets/news; Commit „Liebe & Beziehung <Datum>“ mit den Attributionszeilen der Sitzung; git pull --rebase; git push.

7. BERICHT kurz auf Deutsch: die 3 Schlagzeilen mit Themengruppe, was weggelassen wurde. PushNotification nur bei Problemen (_regeln.md Nr. 7).

REGELN: Nur content/, candidates/, bridge/ und static/assets/news/ ändern; Design und build.py nicht anfassen; keine Logins, Konten, Zahlungen. Rechtlich unangreifbar: immer Quellen, eigene Formulierungen, Videos nur eingebettet.
