# Fußball heute im TV

Eine Datei pro Tag: `content/tv/YYYY-MM-DD.json` (wird von der Aufgabe „TWN Fußball-Tabellen täglich“ angelegt).

```json
{"date": "2026-10-05",
 "items": [{"time": "20:45",
            "comp": {"de": "Nations League", "bg": "Лига на нациите", "en": "Nations League"},
            "m": {"de": "Frankreich – Belgien", "bg": "Франция – Белгия", "en": "France v Belgium"},
            "de": ["RTL+"], "bg": ["Диема Спорт"]}],
 "src": [{"n": "Quelle", "u": "https://…"}]}
```

- `de`: Sender in Deutschland, `bg`: Sender in Bulgarien (leer lassen, wenn unbekannt – nie raten).
- Die DE-Seite zeigt nur Spiele mit deutschen Sendern, die BG-Seite nur mit bulgarischen, EN zeigt beide.
- Angezeigt wird die Datei des aktuellen Tages (Berliner Zeit) am Ende der Seiten Fußball und Länderspiele (nach Mitternacht die des Vortags mit Ergebnissen); die Startseite verlinkt darauf.
