// Service-Leiste der Startseite: Wetter in festen Städten (Bulgarien + Deutschland) und Euro-Referenzkurse der EZB.
// Wetter: MET Norway (api.met.no, CC BY 4.0). Kurse: Europäische Zentralbank (Euro-Referenzkurse, freie Nutzung mit Quellenangabe).
// Alle Abrufe serverseitig und zwischengespeichert; es werden keine Besucherdaten weitergegeben.
const UA = 'TerraWorldNews/1.0 (+https://terraworldnews.com)';
const CITIES = [
  ['sofia', 42.70, 23.32], ['plovdiv', 42.14, 24.75], ['varna', 43.21, 27.91], ['burgas', 42.50, 27.47],
  ['berlin', 52.52, 13.40], ['muenchen', 48.14, 11.58], ['frankfurt', 50.11, 8.68], ['hamburg', 53.55, 9.99],
];
const FX = ['USD', 'GBP', 'CHF', 'TRY', 'RON', 'PLN', 'JPY'];

async function cached(key, ttl, ctx, fn) {
  const k = new Request(`https://terraworldnews.com/__svc/${key}`);
  const hit = await caches.default.match(k);
  if (hit) return hit.json();
  const v = await fn();
  if (v) ctx.waitUntil(caches.default.put(k, new Response(JSON.stringify(v), { headers: { 'content-type': 'application/json', 'cache-control': `public, max-age=${ttl}` } })));
  return v;
}

async function wx(c, lat, lon) {
  const r = await fetch(`https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=${lat.toFixed(2)}&lon=${lon.toFixed(2)}`, { headers: { 'User-Agent': UA, Accept: 'application/json' } });
  if (!r.ok) return null;
  const j = await r.json();
  const ts = (j.properties && j.properties.timeseries) || [];
  const now = Date.now();
  const cur = ts.find(x => Date.parse(x.time) + 3600e3 > now) || ts[0];
  if (!cur) return null;
  const s = ((cur.data.next_1_hours || cur.data.next_6_hours || {}).summary || {}).symbol_code || '';
  return { c, t: Math.round(cur.data.instant.details.air_temperature), sym: s };
}

async function fx() {
  const r = await fetch('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml', { headers: { 'User-Agent': UA } });
  if (!r.ok) return null;
  const x = await r.text();
  const d = (x.match(/time=['"](\d{4}-\d{2}-\d{2})['"]/) || [])[1];
  const rates = {};
  for (const m of x.matchAll(/currency=['"]([A-Z]{3})['"]\s+rate=['"]([\d.]+)['"]/g)) if (FX.includes(m[1])) rates[m[1]] = parseFloat(m[2]);
  return d && Object.keys(rates).length ? { date: d, rates } : null;
}

export async function onRequest(ctx) {
  const out = { wx: [], fx: null };
  const ws = await Promise.all(CITIES.map(([c, la, lo]) => cached(`wx-${c}`, 1800, ctx, () => wx(c, la, lo)).catch(() => null)));
  out.wx = ws.filter(Boolean);
  try { out.fx = await cached('fx', 21600, ctx, fx); } catch (e) {}
  return new Response(JSON.stringify(out), { headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'public, max-age=900', 'x-robots-tag': 'noindex' } });
}
