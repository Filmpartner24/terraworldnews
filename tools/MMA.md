# MMA – Datenformat (wie tools/BOXING.md)
Datei content/mma/<org>.json (org = ufc | pfl | one | oktagon):
{"key":"ufc","sp":"mma","name":{"bg":"UFC","de":"UFC","en":"UFC"},
 "full":{"bg":"Ultimate Fighting Championship","de":"Ultimate Fighting Championship","en":"Ultimate Fighting Championship"},
 "asof":"YYYY-MM-DD",
 "champions":[ {"div":{"bg":"Тежка категория","de":"Schwergewicht","en":"Heavyweight"},"limit":"bis 120,2 kg (265 lb)" (deutsch),
                "name":"Vorname Nachname","country":"Land (deutsch)","note":{"bg","de","en"} optional (z. B. "Interims-Champion", "vakant", "Frauen")} ],
     // alle aktuellen Titel der Organisation: Männer schwerste zuerst, danach Frauen (div-Namen mit „Frauen“/„жени“/„Women's“)
 "upcoming":[ {"date":"YYYY-MM-DD","place":"Ort, Land","f1":"Name","f2":"Name","div":{bg,de,en},"title":{bg,de,en} (z. B. "UFC 330 – Hauptkampf, Titelkampf"),"note":"optional, deutsch"} ],  // angesetzte Hauptkämpfe/Titelkämpfe der nächsten ~3 Monate
 "results":[ {"date":"YYYY-MM-DD","place":"…","f1":"Sieger","f2":"Verlierer","res":{"bg","de","en"} (z. B. "KO/TKO, 2. Runde", "Submission (Rear-Naked Choke), 1. Runde", "einstimmige Punktentscheidung"),"div":{…},"title":{…}} ],  // Haupt-/Titelkämpfe der letzten ~3 Monate, neueste zuerst
 "src":[{"n":"…","u":"URL"}]}
News-Items: {"id","s":"sport","sub":"mma","org":["ufc"],"mn":true,"src":[{n,u}],"yt":{"id","ch","kind":"video"} optional,"bg":{"t"≤90,"d"≤220,"body":[2–3 Absätze]},"de":{…},"en":{…},"photo_q":["Commons-Suchbegriff (Kämpfer-Name)","Fallback"]}
Regeln: nur belegte Angaben aus tatsächlich gesehenen Quellen (ufc.com, pflmma.com, onefc.com, oktagonmma.com, ESPN, MMA Junkie, MMA Fighting, Sherdog, Tapology-Zitate in Medien, Sky Sport, ran.de, BBC, Reuters, AP). Bei Widersprüchen offizielle Seite bevorzugen bzw. in note vermerken. Namen in lateinischer Schrift. Gültiges JSON. Keine Fakten aus Allgemeinwissen ohne Quelle.
Videos nur von offiziellen Kanälen (UFC, PFL MMA, ONE Championship, OKTAGON MMA, ESPN MMA, TNT Sports, DAZN, Sky Sports), ID nur aus gesehener URL/Einbettung, Kanal + Titel per WebFetch https://noembed.com/embed?url=https://www.youtube.com/watch?v=ID bestätigen.
