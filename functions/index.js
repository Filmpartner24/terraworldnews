// Startseite "/" (Bulgarisch): Besucher je nach Land in ihre Sprache leiten.
// Bulgarien -> bleibt auf "/", DE/AT/CH/LI -> /de/, alle anderen -> /en/.
// Suchmaschinen-Bots werden nie umgeleitet; eine selbst gewählte Sprache (Cookie twn_lang) hat Vorrang.
const DE = new Set(['DE', 'AT', 'CH', 'LI']);
const BOT = /bot|crawl|spider|google|inspectiontool|bing|yandex|duckduck|applebot|baidu|petal|slurp|bingpreview|mediapartners|facebookexternalhit|embedly|whatsapp|telegram|discord|skype|preview|lighthouse|headless|curl|wget|python|feed|rss/i;

export async function onRequest(ctx) {
  const req = ctx.request;
  const url = new URL(req.url);
  if (url.pathname !== '/' || (req.method !== 'GET' && req.method !== 'HEAD')) return ctx.next();
  if (BOT.test(req.headers.get('user-agent') || '')) return ctx.next();
  const m = (req.headers.get('cookie') || '').match(/(?:^|;\s*)twn_lang=(bg|de|en)\b/);
  let lang = m ? m[1] : null;
  if (!lang) {
    const c = ((req.cf && req.cf.country) || '').toUpperCase();
    lang = c === 'BG' ? 'bg' : DE.has(c) ? 'de' : 'en';
  }
  if (lang === 'bg') return ctx.next();
  return new Response(null, { status: 302, headers: { Location: '/' + lang + '/' + url.search, 'Cache-Control': 'private, no-store', Vary: 'Cookie' } });
}
