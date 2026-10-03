// Ortszeit + Wetter für die Datumsleiste.
// Land und ungefähre Position liefert Cloudflare aus der IP-Adresse (request.cf); es wird nichts gespeichert.
// Uhrzeit: Hauptstadt des Landes, aus dem die Seite aufgerufen wird. Temperatur: am ungefähren Standort des Besuchers.
// Wetterdaten: MET Norway (api.met.no, CC BY 4.0) – Abruf serverseitig, die IP des Besuchers wird nicht weitergegeben.
import { CAP } from '../../fnlib/geo.js';

const UA = 'TerraWorldNews/1.0 (+https://terraworldnews.com)';

async function weather(lat, lon, ctx) {
  const la = (Math.round(lat * 10) / 10).toFixed(1), lo = (Math.round(lon * 10) / 10).toFixed(1);
  const key = new Request(`https://terraworldnews.com/__wx/${la}/${lo}`);
  const cache = caches.default;
  let hit = await cache.match(key);
  if (hit) return hit.json();
  const r = await fetch(`https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=${la}&lon=${lo}`, { headers: { 'User-Agent': UA, Accept: 'application/json' } });
  if (!r.ok) return null;
  const j = await r.json();
  const ts = (j.properties && j.properties.timeseries) || [];
  const now = Date.now();
  const cur = ts.find(x => Date.parse(x.time) + 3600e3 > now) || ts[0];
  if (!cur) return null;
  const out = { t: cur.data.instant.details.air_temperature, sym: ((cur.data.next_1_hours || cur.data.next_6_hours || {}).summary || {}).symbol_code || '' };
  ctx.waitUntil(cache.put(key, new Response(JSON.stringify(out), { headers: { 'content-type': 'application/json', 'cache-control': 'public, max-age=1800' } })));
  return out;
}

export async function onRequest(ctx) {
  const url = new URL(ctx.request.url);
  const l = ['bg', 'de', 'en'].includes(url.searchParams.get('l')) ? url.searchParams.get('l') : 'en';
  const cf = ctx.request.cf || {};
  const cc = String(cf.country || '').toUpperCase();
  const cap = CAP[cc] || CAP.DE;
  const res = { cc, cap: cap[{ en: 0, de: 1, bg: 2 }[l]], tz: cap[3] };
  const lat = parseFloat(cf.latitude), lon = parseFloat(cf.longitude);
  if (Number.isFinite(lat) && Number.isFinite(lon)) {
    try { const w = await weather(lat, lon, ctx); if (w) { res.t = Math.round(w.t); res.sym = w.sym; } } catch (e) {}
  }
  return new Response(JSON.stringify(res), { headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'private, max-age=600', 'x-robots-tag': 'noindex' } });
}
