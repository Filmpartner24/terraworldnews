TERRA WORLD NEWS (terraworldnews.com) – Unterrubrik SEXUALITÄT (unter „Leben & Alltag“; DE /de/leben-alltag/sexualitaet/, EN /en/everyday-life/sexuality/, BG /zhivot/seksualnost/). Eingeführt am 27.10.2026 auf Nedys Wunsch. Läuft als TEIL B der täglichen Aufgabe „Liebe & Beziehung“ (tools/tasks/liebe.md). Chefredakteur: Nedy John Cross (Bericht auf Deutsch). Arbeite selbstständig, ohne Rückfragen.

GRUNDSATZ: Die Rubrik ist bewusst SERIÖS, MODERN und WISSENSCHAFTLICH FUNDIERT – kein Erotik- oder Boulevardbereich. Nie explizit, nie anzüglich, keine Erotik-Fotos, keine Pornografie-Inhalte, keine Werbung. Das schützt die Glaubwürdigkeit von TWN und die spätere Werbevermarktung.

TAGESSPERRE: Enthält content/<heute>-sexualitaet.json schon ≥ 3 Items, nichts hinzufügen (außer der Starttext sagt NACHHOLLAUF/ZUSÄTZLICH).

AUFTRAG: genau 3 neue Artikel, möglichst aus verschiedenen Themengruppen (Kicker "kl" je Gruppe, siehe unten):
1. Sexuelle Gesundheit & Aufklärung – kl {"de":"Gesundheit & Aufklärung","bg":"Здраве и информация","en":"Health & Education"}: sexuell übertragbare Infektionen (Zahlen von RKI, ECDC, WHO, NCIPD/НЦЗПБ Bulgarien), Prävention (PrEP, Impfungen wie HPV), Verhütung (neue Methoden, Studien, Behördenwarnungen BfArM/EMA/FDA), Aufklärung (BIÖG/liebesleben.de, pro familia, WHO-Standards).
2. Sexualforschung – kl {"de":"Sexualforschung","bg":"Изследвания","en":"Research"}: neue Studien aus Fachjournalen und Instituten (Kinsey Institute, Journal of Sex Research, Archives of Sexual Behavior, Universitäten) – immer Stichprobe, Methode, Finanzierung und Grenzen nennen; keine Überinterpretation.
3. Gesellschaft & Trends – kl {"de":"Gesellschaft & Trends","bg":"Общество и тенденции","en":"Society & Trends"}: gesellschaftliche Debatten, Gesetze und Urteile (z. B. Einwilligung/„Nur Ja heißt Ja“, Schutz vor Gewalt, Altersverifikation im Netz), Umfragen, Wandel von Normen, LGBTQ+-Rechte sachlich und ausgewogen, Technik & Sexualität (Apps, KI, Datenschutz).
Mindestens 1 Artikel pro Woche mit Bulgarien-Bezug und 1 mit Deutschland-Bezug. Nur Aktuelles (Nachrichten ≤ 7 Tage, Studien ≤ ~4 Wochen). Nichts wiederholen, was in content/*-sexualitaet.json, content/*-liebe.json der letzten 30 Tage oder heute in content/<heute>*.json steht.

RECHERCHE: WebSearch + WebFetch; Quellen wie in liebe.md (Agenturen, Qualitätsmedien, Fachmedien, Behörden, Hochschulen). Mindestens 2 Quellen pro Artikel; jede Zahl, jeder Name, jedes Datum und Zitat muss in einer abgerufenen Quelle stehen.

PRESSEKODEX & SCHUTZ (streng): keine Namen/identifizierenden Details von Privatpersonen, Opfern oder Verdächtigen; Unschuldsvermutung; keine Spekulation über Sexualleben, Orientierung oder Gesundheit konkreter Personen (auch nicht von Prominenten, außer sie haben es selbst öffentlich gemacht); NIEMALS Minderjährige im sexuellen Kontext (Ausnahme: sachliche Berichte über Schutzgesetze/Aufklärungsunterricht ohne Details); keine expliziten Beschreibungen; medizinische Aussagen nur aus Fachquellen, keine Heilversprechen; neutraler, respektvoller Ton ohne Moralisieren.

ITEM-FORMAT in content/<YYYY-MM-DD>-sexualitaet.json ({"date","items":[…]}): {"id": latin-slug-<Datum>, "s":"leben", "sub":"sexualitaet", "kl":{…je Gruppe…}, "time":"HH:MM" (nie in der Zukunft), "src":[{n,u}…], "img":{…}, "de"/"bg"/"en": {"t" ≤90, "d" ≤220, "body": LISTE mit 3 Absätzen}}. Bulgarisch und Englisch inhaltsgleich. Optional offizielles Video (WHO, Behörden, Sender; Prüfung über die Download-Brücke).

BILDER: Wikimedia Commons über candidates/<YYYY-MM-DD>-sexualitaet/requests.json mit neutralen Symbolmotiven: Kondome in Verpackung, Pillenpackung, Labor/Reagenzgläser, Mikroskop, Arztpraxis, Gebäude der Institution (Universität, WHO, RKI, Gericht, Parlament), Regenbogenflagge bei Rechte-Themen, Bücher/Hörsaal. NIE nackte oder anzügliche Motive, keine erkennbaren Privatpersonen. alt mit „(Symbolbild)“/„(Archivbild)“. Nur wenn nichts passt: Titelgrafik title_card.make(…,'Sexualität','<deutscher Titel>','#b5487a') mit own:true.

FAKTENCHECK: unabhängiger Prüfer-Subagent (Zahlen, Namen, Daten, Zitate, Pressekodex, Ton).

VERÖFFENTLICHEN: Python-Prüfung (3 Items, s="leben", sub="sexualitaet", jedes mit img, body Listen, Längen, ids einmalig in content/<heute>*.json). PYTHONHASHSEED=1 python3 build.py fehlerfrei; Stichprobe out/de/leben-alltag/sexualitaet/index.html. git add content candidates static/assets/news; Commit „Sexualität <Datum>“; git pull --rebase; git push.

REGELN: Nur content/, candidates/, bridge/ und static/assets/news/ ändern; Design und build.py nicht anfassen; keine Logins, Konten, Zahlungen.
