// Aktuelles Wetter für die Kopfzeile (Berlin, München, Hamburg, Sofia, Burgas, Kjustendil).
// Daten: MET Norway Locationforecast 2.0 (CC BY 4.0), serverseitig abgerufen und 30 Minuten zwischengespeichert –
// die Besucher haben dadurch keinen Kontakt zu Dritten.
const CITIES = [[52.52, 13.405], [48.137, 11.575], [53.551, 9.994], [42.698, 23.322], [42.504, 27.462], [42.284, 22.691]];
const UA = 'terraworldnews.com media@filmpartner24.com';

export async function onRequest(ctx) {
  const cache = caches.default;
  const key = new Request('https://terraworldnews.com/api/weather?v=1');
  const hit = await cache.match(key);
  if (hit) return hit;
  const data = await Promise.all(CITIES.map(async ([lat, lon]) => {
    try {
      const r = await fetch(`https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=${lat}&lon=${lon}`, { headers: { 'User-Agent': UA } });
      if (!r.ok) return null;
      const j = await r.json();
      const d = j.properties.timeseries[0].data;
      const sum = (d.next_1_hours || d.next_6_hours || {}).summary || {};
      return { t: Math.round(d.instant.details.air_temperature), s: sum.symbol_code || '' };
    } catch (e) { return null; }
  }));
  const ok = data.some(Boolean);
  const res = new Response(JSON.stringify(data), { headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': `public, max-age=${ok ? 1800 : 120}` } });
  if (ok) ctx.waitUntil(cache.put(key, res.clone()));
  return res;
}
