# TERRA WORLD NEWS – Rubrik BUSINESS: Datenformat und Regeln
Ziel: verständliche Börsen-/Wirtschaftsseite für normale Leser (BG/DE/EN), Zahlen + Tabellen, jede Zahl aus einer tatsächlich gesehenen, datierten Quelle.
Datei: content/business/YYYY-MM-DD.json = {"date":"YYYY-MM-DD","time":"HH:MM","blocks":[Block, …]} – Reihenfolge der Blöcke: strom-ibex, wallstreet, deutsche-boerse, bg-energie-aktien, invest-bulgarien, invest-deutschland.
Jeder Block wird automatisch eine eigene Meldung der Rubrik "business" (zusätzlich zu den 77 Tagesmeldungen) und erscheint komplett auf /biznes/, /de/business/, /en/business/; die "ticker"-Werte aller Blöcke bilden das grüne BÖRSE-Laufband auf der Business-Seite (das rote LIVE-Laufband bleibt).
Aktienbörsen: Schlusskurse des letzten Handelstags (am Wochenende Freitag + Wochenbilanz). Strombörse IBEX: Day-Ahead für den heutigen Liefertag (am Vortag ca. 14:30 Sofioter Zeit veröffentlicht, BTA meldet täglich „цената на тока за бизнеса утре …“ nach Daten der БНЕБ) plus Vortag zum Vergleich.
RECHTLICH: Keine bulgarischen Viertelstunden-/Stundenpreise von energy-charts.info verwenden (nur private/interne Nutzung lizenziert) – nur IBEX/БНЕБ-Tageswerte (Base, Peak, Off-Peak, Menge) aus BTA oder ibex.bg. Deutsche Day-Ahead-Werte nur mit Quelle (SMARD = CC BY 4.0).
Tools: ToolSearch "select:WebSearch,WebFetch"; WebSearch mode "extended", dann WebFetch. NIE Zahlen raten oder runden ohne Hinweis; nur URLs nutzen, die du gesehen hast. Was nicht bestätigbar ist: weglassen.
Stil: neutral, eigene Worte, kurze Sätze, Fachbegriffe kurz erklären (z. B. „Leitindex DAX = die 40 größten deutschen Börsenkonzerne“). Keine Anlageempfehlung. Bulgarisch: AfD = „АзГ (AfD)“.

## Ausgabe: EIN JSON-Objekt (Block) pro Datei, Schema:
{
 "id": "slug",
 "asof": {"bg": "…", "de": "Schlusskurse Freitag, 2. Oktober 2026", "en": "…"},
 "bg": {"t": "Titel ≤90", "d": "Teaser ≤220", "body": ["Absatz", "Absatz", "(Absatz)"], "explain": "1–2 Sätze 'Was bedeutet das für mich?' in einfacher Sprache"},
 "de": {...}, "en": {...},
 "kpi": [ {"l": {"bg":"…","de":"…","en":"…"}, "v": 24123.45, "dec": 2, "u": "Pkt.|EUR/MWh|%|USD", "chg": 0.42} ],   // 3–4 Kennzahlen-Kacheln; chg = Veränderung in % (Zahl, optional)
 "tables": [ {"cap": {"bg","de","en"},
              "cols": [ {"h": {"bg","de","en"}, "k": "txt"}, {"h": {...}, "k": "num", "dec": 2}, {"h": {...}, "k": "chg", "dec": 2} ],
              "rows": [ ["S&P 500", 6650.12, 0.45], [{"bg":"…","de":"…","en":"…"}, 1.0, -0.3] ] } ],
      // k: txt = Text (String oder {bg,de,en}); num = Zahl (JSON-Zahl, dec Nachkommastellen); chg = Veränderung in % (Zahl, wird grün/rot); null = „–“
 "chart": {"cap": {"bg","de","en"}, "unit": "EUR/MWh", "labels": ["00","01",…], "values": [ … ]},   // optional (nur Strom: Stundenpreise)
 "ticker": [ {"n": "DAX", "v": 24123.45, "dec": 2, "chg": 0.42} ],   // 2–6 Werte für das Börsen-Laufband
 "src": [ {"n": "Quelle", "u": "URL"} ],
 "notes": "für die Redaktion: was wo gefunden, was nicht bestätigt"
}
Zahlen immer als JSON-Zahlen mit Punkt als Dezimaltrenner (Formatierung macht die Seite).

## Bilder (eigene Infografiken)
Nach dem Schreiben der Datei: `python3 tools/biz_images.py <YYYY-MM-DD>` – zeichnet je Block eine eigene 1200x675-Grafik aus den Daten (static/assets/news/<datum>/biz-<id>.webp) und setzt "img" (own: true) in die Datei. Die Seite zeigt dazu „Grafik: TERRA WORLD NEWS (eigene Darstellung)“. Keine Fremd- oder KI-Bilder. Bilddateien mit committen (git add static/assets/news/<datum>/biz-*).
