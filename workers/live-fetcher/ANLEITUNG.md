# TWN Live-Abrufdienst einrichten (ca. 15 Minuten)

**Wozu:** Die Live-Spielstände werden künftig an **einer** Stelle alle 30 Sekunden abgeholt und zentral gespeichert.
Die Website liest nur noch diesen Speicher. Dadurch bekommt der Datenanbieter immer gleich viele Abrufe –
egal ob 100 oder 100.000 Besucher zuschauen. Fällt die Datenquelle aus, kommt eine Warnung aufs Handy.

Solange der Dienst nicht eingerichtet ist, läuft die Website wie bisher weiter (direkter Abruf + ESPN-Ersatz).
Nach der Einrichtung schaltet sie automatisch um – es muss nichts am Code geändert werden.

---

## Schritt 1 – Cloudflare Workers „Paid“ aktivieren (5 $/Monat)
1. https://dash.cloudflare.com öffnen und anmelden.
2. Links **Workers & Pages** → oben **Plans** (bzw. „Workers-Pläne“) → **Workers Paid** wählen → bestätigen.
   *Grund:* An Spieltagen werden mehr als 1.000 Speichervorgänge pro Tag nötig – das kostenlose Paket erlaubt nur 1.000.

## Schritt 2 – Speicher anlegen
1. Links **Storage & Databases** → **KV** → **Create** (Namespace erstellen).
2. Name: `TWN_LIVE` → **Add**.

## Schritt 3 – Den Abrufdienst anlegen
1. Links **Workers & Pages** → **Create** → **Worker** → „Hello World“-Vorlage → Name: `twn-live-fetcher` → **Deploy**.
2. **Edit code** klicken. Den gesamten Inhalt im Editor löschen und durch den Inhalt der Datei
   `workers/live-fetcher/worker.js` aus dem GitHub-Repo ersetzen
   (https://github.com/Filmpartner24/terraworldnews/blob/main/workers/live-fetcher/worker.js → „Raw“ → alles kopieren).
3. Oben rechts **Deploy**.

## Schritt 4 – Einstellungen des Abrufdienstes (Worker `twn-live-fetcher` → **Settings**)
1. **Bindings** → **Add** → **KV namespace** → Variable name: `LIVE_KV` → Namespace: `TWN_LIVE` → **Save**.
2. **Variables and Secrets** → **Add**:
   - Typ **Secret**, Name `APISPORTS_KEY`, Wert: euer API-Football-Schlüssel
     (derselbe wie im Pages-Projekt; zu finden im API-Football-Dashboard unter „My Access“).
   - Typ **Text**, Name `NTFY_TOPIC`, Wert: `twn-live-aa2f050a73ab`
3. **Trigger Events** (bzw. „Triggers“) → **Add** → **Cron Triggers** → Ausdruck `* * * * *` (= jede Minute) → **Add**.

## Schritt 5 – Website mit dem Speicher verbinden
1. **Workers & Pages** → Projekt **terraworldnews** → **Settings** → **Bindings** → **Add** → **KV namespace**.
2. Variable name: `LIVE_KV` → Namespace: `TWN_LIVE` → **Save** (für „Production“).
3. Wirksam ab der nächsten Veröffentlichung (passiert automatisch mehrmals pro Stunde) – oder unter
   **Deployments** beim obersten Eintrag „…“ → **Retry deployment**.

## Schritt 6 – Warnungen aufs Handy
1. App **ntfy** installieren (iPhone: App Store, Android: Google Play – kostenlos, kein Konto nötig).
2. In der App **+** → Topic: `twn-live-aa2f050a73ab` → Server: `ntfy.sh` (Standard) → **Subscribe**.
3. Ab jetzt kommt eine Meldung, wenn bei laufenden Spielen 5 Minuten lang keine Live-Daten ankommen –
   und eine Entwarnung, sobald es wieder läuft.

## Kontrolle
- Im Worker `twn-live-fetcher` oben die Adresse `https://twn-live-fetcher.<euer-name>.workers.dev` öffnen.
  Dort steht z. B. `{"ok":true,"src":"apisports","live":true,"age_s":12}`.
  `age_s` = Alter der Daten in Sekunden (während Spielen unter 60).
- `src` zeigt die Quelle: `apisports` (API-Football) oder `espn` (Ersatz).

Bei Fragen: einfach Claude im TERRA-WORLD-NEWS-Projekt fragen.
