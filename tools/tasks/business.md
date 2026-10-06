TERRA WORLD NEWS (terraworldnews.com) – tägliches Update der Rubrik BUSINESS (BG „Бизнес“ /biznes/, DE /de/business/, EN /en/business/). Chefredakteur: Nedy John Cross (Bericht auf Deutsch). Arbeite selbstständig, ohne Rückfragen.

0. SETUP: Repo Filmpartner24/terraworldnews (privat, main) mit add_repo (access push) anhängen, nach /home/claude/terra klonen bzw. git pull. Lies tools/BUSINESS.md (Datenformat, Regeln, Bilder) und die Datei der Vortage unter content/business/ als Muster. Skill „terra-daily-edition“ laden, falls vorhanden (Stil, Quellen, „АзГ (AfD)“). Bestimme Datum/Uhrzeit Europe/Berlin.

1. RECHERCHE parallel mit 4 Subagenten (WebSearch mode "extended", dann WebFetch; jede Zahl aus einer tatsächlich gesehenen, datierten Quelle; nichts raten; Unbestätigtes weglassen; eigene Rechnungen in notes vermerken):
   a) strom-ibex: Bulgarische Strombörse IBEX (https://ibex.bg/en/), Day-Ahead für den heutigen Liefertag + Vortag: Base, Peak, Off-Peak (EUR/MWh), gehandelte Menge (MWh) – Quelle BTA-Meldungen nach БНЕБ-Daten bzw. ibex.bg. Tabelle „Tagesüberblick“ (Zeilen in dieser Reihenfolge: Base, Peak, Off-Peak, Menge; Spalten: Kennzahl | heute | morgen (falls schon veröffentlicht, sonst null) | Vortag). Optional Vergleich Deutschland Day-Ahead (SMARD/EU-Quelle). KEINE bulgarischen Viertelstunden-/Stundenwerte von energy-charts.info (Lizenz). Sehr verständlich erklären (Was ist die Strombörse? Was heißt der Preis für Firmen/Haushalte?).
   b) wallstreet: Schlusskurse des letzten US-Handelstags (Dow Jones, S&P 500, Nasdaq; Tag %, am Montag/nach Wochenende auch Woche %), wichtigste Einzelwerte, Rendite 10 J., Öl, Gold – AP, Reuters, CNBC, Yahoo Finance, Nasdaq.com. Was hat bewegt?
   c) deutsche-boerse: Xetra/Frankfurt letzter Handelstag – DAX, MDAX, SDAX, TecDAX, Euro Stoxx 50, DAX-Gewinner/-Verlierer; Quellen https://live.deutsche-boerse.com/, boerse-frankfurt.de, tagesschau Marktbericht, dpa-AFX bei seriösen Medien, finanzen.net.
   d) bg-energie-aktien: Börse Sofia (BSE) – SOFIX, BGBX40, BGTR30, BGREIT (BTA-Tagesmeldung), Energiewerte (z. B. via https://de.investing.com/stock-screener/bulgaria/energy, infostock.bg) – nur datierte Kurse, letzter Abschluss mit Datum kennzeichnen; Notierung in EUR.
   e) invest-bulgarien und invest-deutschland (gleicher Subagent wie d oder eigener): aktuelle Investitionsprojekte nach Regionen (BG: Bezirke/Wirtschaftszonen; DE: Bundesländer) der letzten Tage/Wochen – Tabelle Region | Unternehmen/Projekt | Branche | Summe (Mio. EUR, Zahl) | Arbeitsplätze | Datum, plus Strukturdaten mit Datenstand; auch Werksschließungen. Nur Neues seit dem letzten Bericht hervorheben; ältere Projekte nur mit Datum. Erste kpi-Kachel = Gesamtsumme (u „Mio. EUR“ bzw. „Mrd. EUR“).
   An Wochenenden/Feiertagen ohne Börsenhandel: letzte Schlusskurse mit klarem Datenstand (asof) verwenden und das im Text sagen.
   Jeder Block: bg/de/en (t ≤90, d ≤220, body 2–4 Absätze, explain = 1–2 Sätze „Was bedeutet das für mich?“ in einfacher Sprache), kpi (3–4 Kacheln), tables, ticker (für das BÖRSE-Laufband), src, asof. Keine Anlageberatung.

2. FAKTENCHECK: ein unabhängiger Faktenprüfer-Subagent prüft jede Zahl in kpi/tables/ticker/Text in allen drei Sprachen gegen die Quellen; Korrekturen übernehmen, Unbestätigtes streichen.

3. DATEI: content/business/<YYYY-MM-DD>.json = {"date","time":"HH:MM" (Veröffentlichungszeit Berlin),"blocks":[strom-ibex, wallstreet, deutsche-boerse, bg-energie-aktien, invest-bulgarien, invest-deutschland]} (notes-Felder entfernen). Block-ids genau so. Diese Berichte zählen ZUSÄTZLICH zu den 80 Tagesmeldungen. Existiert die Datei schon, Blöcke aktualisieren statt doppeln.

4. BILDER: python3 tools/biz_images.py <YYYY-MM-DD> ausführen (eigene Infografik je Block aus den Daten, setzt "img" mit own:true). Zwei bis drei der erzeugten Bilder mit Read ansehen (Text lesbar, nichts überlappt, Zahlen stimmen mit der Datei). Keine Fremd- oder KI-Bilder.

5. VERÖFFENTLICHEN: PYTHONHASHSEED=1 python3 build.py muss fehlerfrei laufen; out/de/business/index.html stichprobenartig prüfen (Tabellen, Grafiken, BÖRSE-Laufband). git add content/business static/assets/news/<YYYY-MM-DD>/biz-*; commit „Business <Datum>“ (mit den Attributionszeilen der Sitzung); git pull --rebase; push. Nach ~4 Min. prüfen, dass der letzte Action-Lauf erfolgreich war.

6. BERICHT (SendUserMessage via ToolSearch laden, und als finale Antwort), kurz auf Deutsch: Kernzahlen (IBEX Base, DAX, S&P 500, SOFIX), Schlagzeilen der 6 Blöcke, was nicht bestätigt/weggelassen wurde, offene Punkte.

REGELN: Nur content/business/ und static/assets/news/<Datum>/biz-* ändern; Design nicht anfassen. Keine Logins, Konten, Zahlungen. Nur eigene Arbeitsdateien löschen.
