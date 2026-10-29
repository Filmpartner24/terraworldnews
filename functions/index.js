// Startseite "/" (Bulgarisch): Besucher in ihre Sprache leiten (Nedy 29.10.2026).
// Reihenfolge: 1. selbst gewählte Sprache (Cookie twn_lang)  2. Gerätesprache (Accept-Language)
//              3. Land (Bulgarien -> bg, DE/AT/CH/LI -> de, Türkei -> tr, spanischsprachige Länder -> es)  4. sonst en.
// Bulgarisch bleibt auf "/". Suchmaschinen-Bots werden nie umgeleitet.
const LANGS = new Set(['bg', 'de', 'en', 'es', 'tr']);
const DE = new Set(['DE', 'AT', 'CH', 'LI']);
const ES = new Set(['ES', 'MX', 'AR', 'CO', 'CL', 'PE', 'VE', 'EC', 'GT', 'CU', 'BO', 'DO', 'HN', 'PY', 'SV', 'NI', 'CR', 'PA', 'UY', 'PR', 'GQ']);
const BOT = /bot|crawl|spider|google|inspectiontool|bing|yandex|duckduck|applebot|baidu|petal|slurp|bingpreview|mediapartners|facebookexternalhit|embedly|whatsapp|telegram|discord|skype|preview|lighthouse|headless|curl|wget|python|feed|rss/i;

function fromAcceptLanguage(h) {
  // "de-DE,de;q=0.9,en;q=0.8" -> beste unterstützte Sprache nach q-Wert
  let best = null, bq = 0;
  for (const part of (h || '').split(',')) {
    const [tag, ...params] = part.trim().toLowerCase().split(';');
    const code = tag.split('-')[0];
    if (!LANGS.has(code)) continue;
    let q = 1;
    for (const p of params) { const m = p.trim().match(/^q=([0-9.]+)$/); if (m) q = parseFloat(m[1]); }
    if (q > bq) { best = code; bq = q; }
  }
  return best;
}

function fromCountry(c) {
  c = (c || '').toUpperCase();
  if (c === 'BG') return 'bg';
  if (DE.has(c)) return 'de';
  if (c === 'TR') return 'tr';
  if (ES.has(c)) return 'es';
  return 'en';
}

export async function onRequest(ctx) {
  const req = ctx.request;
  const url = new URL(req.url);
  if (url.pathname !== '/' || (req.method !== 'GET' && req.method !== 'HEAD')) return ctx.next();
  if (BOT.test(req.headers.get('user-agent') || '')) return ctx.next();
  const m = (req.headers.get('cookie') || '').match(/(?:^|;\s*)twn_lang=(bg|de|en|tr|es|it)\b/);
  const lang = (m && m[1]) || fromAcceptLanguage(req.headers.get('accept-language')) || fromCountry(req.cf && req.cf.country);
  if (lang === 'bg') return ctx.next();
  return new Response(null, { status: 302, headers: { Location: '/' + lang + '/' + url.search, 'Cache-Control': 'private, no-store', Vary: 'Cookie, Accept-Language' } });
}
