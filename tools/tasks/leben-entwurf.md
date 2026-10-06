TERRA WORLD NEWS (terraworldnews.com) – Rubrik „Leben & Alltag“ (BG „Живот и ежедневие“, EN „Everyday Life“), Schlüssel s = "leben". Chefredakteur: Nedy John Cross. Kommunikation auf Deutsch. Ein Beitrag pro Werktag (Mo–Fr), zuerst als ENTWURF zur Freigabe durch Nedy.

0. SETUP: Repo Filmpartner24/terraworldnews (privat, main) mit add_repo (access push) anhängen, nach /home/claude/terra klonen bzw. git pull. Skill „terra-daily-edition“ laden, falls vorhanden (Regeln zu Fotos, Stil, Quellen, АзГ (AfD)). Lies entwuerfe/leben/THEMEN.md (Themenplan + erledigte Beiträge).

1. THEMA: das nächste offene feste Startthema aus THEMEN.md; danach rotierend Geld – Wohnen – Arbeit – Reisen – digitale Sicherheit, mit aktuellem Anlass bevorzugt (neue Gesetze, Fristen, Preise, Saison) und immer mit Bezug zu Deutschland UND Bulgarien. Keine Wiederholung erledigter Themen.

2. RECHERCHE zuerst (WebSearch extended + WebFetch): amtliche und seriöse Quellen (Destatis, Eurostat, НСИ/NSI, Bundesnetzagentur, КЕВР, BSI, Verbraucherzentrale, КЗП, ГДБОП, БНБ, Ministerien, große Medien). Jede Zahl mit Quelle und Datenstand. Nichts erfinden – keine Zahlen, keine Anlässe; fehlen belastbare Angaben, die Lücke offen benennen. Länderspezifische Angaben eindeutig kennzeichnen („In Deutschland …“ / „В България …“) und Gültigkeit fürs jeweilige Land prüfen. Rechenbeispiele ausdrücklich als Beispiel kennzeichnen und die Annahmen nennen. Danach ein unabhängiger Faktenprüfer-Subagent über alle Zahlen, Namen und Daten.

3. SCHREIBEN: ein Beitrag als Item {id (latin slug), s:"leben", time:"HH:MM" (Veröffentlichungszeit, beim Veröffentlichen setzen), src:[{n,u}] (nur tatsächlich gesehene URLs), facts (3–6 Kernpunkte/Zahlen mit Datenstand), img, und bg/de/en mit t (≤90 Zeichen, konkret und sachlich), d (≤220), body (5–8 kurze, verständliche Absätze; Servicecharakter, Du-Ansprache im Deutschen ok)}. Deutsch zuerst, dann sinngemäß und natürlich ins Bulgarische und Englische (nicht wörtlich). Bulgarisch: AfD immer „АзГ (AfD)“. Die Seite fügt automatisch den Hinweis „keine Rechts-, Steuer- oder Finanzberatung“ an.
   FOTO: nur Wikimedia Commons (CC BY/BY-SA/CC0/PD), Ablauf wie in der Skill: candidates/<YYYY-MM-DD>-leben/requests.json pushen, ~3 Min. warten, git pull, Kontaktbogen ansehen, wählen; img {f:"assets/news/<YYYY-MM-DD>/<id>.webp", w:1200, h:675, art, lic, page, alt:{bg,de,en}}, Symbolbilder kennzeichnen. Danach candidates/<…>-leben/ löschen.

4. ENTWURF ABLEGEN (noch NICHT veröffentlichen): entwuerfe/leben/<YYYY-MM-DD>.json im Format {"date":"YYYY-MM-DD","items":[item]}. In THEMEN.md unter „Erledigt“ eintragen: „<Datum> – <Titel DE> – Entwurf“. Commit mit „[CF-Pages-Skip]“ in der Nachricht (+ Attributionszeilen), git pull --rebase, push.

5. NACHRICHT AN NEDY (SendUserMessage via ToolSearch laden, und als finale Antwort): Überschrift + Kurztext DE, der vollständige deutsche Text, Kernpunkte, Quellenliste mit Datenstand, gewähltes Foto (Autor/Lizenz), offene Lücken. Schluss: „Zum Veröffentlichen antworte hier mit ‚ok‘ – oder schreib mir, was ich ändern soll.“

6. WENN NEDY IN DIESER SITZUNG ANTWORTET:
   - „ok“/Freigabe: (Repo ggf. neu klonen/pull) Item aus entwuerfe/leben/<Datum>.json übernehmen, time = aktuelle Berliner Uhrzeit HH:MM, date = heutiges Datum; in content/<heutiges Datum>-leben.json schreiben (anhängen, falls vorhanden); Entwurfsdatei entfernen; THEMEN.md-Status auf „veröffentlicht <Datum>“; PYTHONHASHSEED=1 python3 build.py muss laufen; commit (ohne Skip), git pull --rebase, push; nach ~4 Min. prüfen, dass der Action-Lauf erfolgreich war und das Foto unter static/assets/news/ liegt. Kurz bestätigen mit Link (DE: https://terraworldnews.com/de/leben-alltag/).
   - Änderungswünsche: umsetzen (in allen drei Sprachen), Entwurf aktualisieren, erneut vorlegen.
   Ohne Freigabe wird nichts veröffentlicht.

REGELN: Nur content/, entwuerfe/, candidates/ ändern; Design nicht anfassen. Keine Logins, Konten, Zahlungen. Nur eigene Arbeitsdateien löschen.

ZUSATZ (06.10.2026): Das Thema darf sich nicht mit Leben-&-Alltag-Artikeln (s="leben") der Tagesausgabe der letzten 14 Tage überschneiden (content/*.json lesen). Am Ende IMMER PushNotification (status "proactive") mit <routine_summary>Leben & Alltag: Entwurf „<Titel>“ wartet auf deine Freigabe – in der Claude-App bei der Aufgabe mit „ok“ antworten.</routine_summary>.
