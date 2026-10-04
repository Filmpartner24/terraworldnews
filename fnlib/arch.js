import { SEC } from './sec.js';
// Ältere Artikel (älter als 14 Tage) liegen nicht als einzelne Dateien vor, sondern gebündelt in
// /_arch/<sprache>/<datum>/<bucket>.json. Diese Funktion liefert sie unter ihrer normalen Adresse aus.
const BUCKETS = 8;
function bucket(slug) {
  let h = 2166136261;
  for (const b of new TextEncoder().encode(slug)) { h ^= b; h = Math.imul(h, 16777619) >>> 0; }
  return h % BUCKETS;
}
export async function onRequest(ctx) {
  const res = await ctx.next();
  if (res.status !== 404) return res;
  const url = new URL(ctx.request.url);
  const m = url.pathname.match(/^\/(?:(de|en)\/)?(?:novini|nachrichten|news)\/(\d{4})\/(\d{2})\/(\d{2})\/([a-z0-9-]+)\.html$/);
  if (!m) return res;
  const lang = m[1] || 'bg', day = `${m[2]}-${m[3]}-${m[4]}`, slug = m[5];
  const r = await ctx.env.ASSETS.fetch(new URL(`/_arch/${lang}/${day}/${bucket(slug)}.json`, url.origin));
  if (!r.ok) return res;
  const html = (await r.json())[slug];
  if (!html) return res;
  return new Response(html, { status: 200, headers: { ...SEC, 'content-type': 'text/html; charset=utf-8', 'cache-control': 'public, max-age=3600', 'x-twn-archive': '1' } });
}
