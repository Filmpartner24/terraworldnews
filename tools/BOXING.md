# Boxen – Datenformat (Stand 3.10.2026)
Datei content/boxing/<org>.json (org = wbc | wba | ibf | wbo):
{"key":"wbc","name":{"bg":"WBC","de":"WBC","en":"WBC"},
 "full":{"bg":"Световен боксов съвет","de":"World Boxing Council","en":"World Boxing Council"},
 "asof":"2026-10-03",
 "champions":[ {"div":{"bg":"Тежка категория","de":"Schwergewicht","en":"Heavyweight"},"limit":"über 90,7 kg (200 lb)",
                "name":"Vorname Nachname","country":"Land (deutsch)","note":{"bg","de","en"} optional (z. B. "Super-Champion", "Interims-Champion", "vakant")} ],  // alle 17 Gewichtsklassen der Männer, schwerste zuerst; vakante Titel name:"" + note vakant
 "upcoming":[ {"date":"YYYY-MM-DD","place":"Ort, Land","f1":"Name","f2":"Name","div":{bg,de,en},"title":{bg,de,en} (z. B. "WBC-WM"),"note":"optional"} ],   // angesetzte Titelkämpfe/Hauptkämpfe mit Titel dieses Verbands, nächste ~3 Monate
 "results":[ {"date":"YYYY-MM-DD","place":"…","f1":"Sieger","f2":"Verlierer","res":{"bg","de","en"} (z. B. "KO 5. Runde", "einstimmig nach Punkten", "Remis"),"div":{…},"title":{…}} ],  // Titelkämpfe der letzten ~3 Monate, neueste zuerst
 "src":[{"n":"…","u":"URL"}]}
News-Items (je Verband 1 aktuelle Meldung von heute/gestern bzw. wenigen Tagen, falls nichts Neueres): Liste in drafts/box/news-<org>.json:
[{"id":"latin-slug","s":"sport","sub":"boxen","org":["wbc"],"mn":true,"src":[{n,u}],"bg":{"t"≤90,"d"≤220,"body":[2–3 Absätze]},"de":{…},"en":{…},"photo_q":["Wikimedia-Commons-Suchbegriff (Boxer-Name)","Fallback"]}]
Regeln: nur belegte Angaben aus tatsächlich gesehenen Quellen (offizielle Verbandsseiten wbcboxing.com, wbaboxing.com, ibf-usba-boxing.com, wboboxing.com, ESPN, BoxRec-Zitate in Medien, The Ring, BoxingScene, Sky Sports, DAZN, BBC, Reuters, AP). Bei widersprüchlichen Angaben die offizielle Verbandsseite vorziehen und in notes vermerken. Namen in lateinischer Schrift. Gültiges JSON.
