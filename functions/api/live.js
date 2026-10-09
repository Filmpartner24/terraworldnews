// Schlüssel APISPORTS_KEY in Cloudflare hinterlegt am 09.10.2026 (Pro bis 09.11.2026)
// Live-Spielstände (Fußball) für die Seiten Sport → Fußball und Sport → Länderspiele.
// Datenquelle: API-Football (api-sports.io). Der Schlüssel liegt als Cloudflare-Secret APISPORTS_KEY vor, nie im Repo.
// Abrufe werden serverseitig gecacht (Tagesspielplan 10 Min., Live-Daten 60 s), damit alle Besucher dieselbe Antwort
// bekommen und das Anfrage-Kontingent geschont wird. Live-Daten werden nur abgefragt, wenn heute gerade ein Spiel läuft.
// Ohne Schlüssel antwortet die Funktion mit {ok:false} – der Live-Block bleibt dann einfach ausgeblendet.

const API = 'https://v3.football.api-sports.io';
// Liga-IDs bei API-Football: Vereinsfußball (Fußball-Seite) und Nationalteams (Länderspiele-Seite)
const CLUB = [78, 79, 81, 39, 140, 135, 61, 172, 2, 3];     // BL, 2. BL, DFB-Pokal, PL, La Liga, Serie A, Ligue 1, Parwa Liga, CL, EL
const NAT = [5, 10, 32, 960, 4, 1];                        // Nations League, Freundschaftsspiele, WM-Quali Europa, EM-Quali, EM, WM
const ALL = new Set([...CLUB, ...NAT]);
const LIVE = new Set(['1H', 'HT', '2H', 'ET', 'BT', 'P', 'SUSP', 'INT', 'LIVE']);

function berlinDate() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Berlin', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
}

async function cached(ctx, path, ttl, base = API, ks = '') {
  const key = new Request('https://terraworldnews.com/__live' + (base === API ? '' : '/hb') + ks + path);
  const cache = caches.default;
  const hit = await cache.match(key);
  if (hit) return hit.json();
  // Schlüssel: direkt bei API-Sports (APISPORTS_KEY) oder über RapidAPI (RAPIDAPI_KEY) – gleiche Daten, andere Adresse
  let url = base + path, headers = { 'x-apisports-key': ctx.env.APISPORTS_KEY };
  if (!ctx.env.APISPORTS_KEY && ctx.env.RAPIDAPI_KEY) {
    const host = base === API ? 'api-football-v1.p.rapidapi.com' : 'api-handball.p.rapidapi.com';
    url = 'https://' + host + (base === API ? '/v3' : '') + path;
    headers = { 'x-rapidapi-key': ctx.env.RAPIDAPI_KEY, 'x-rapidapi-host': host };
  }
  const r = await fetch(url, { headers });
  if (!r.ok) throw new Error('api ' + r.status);
  const j = await r.json();
  if (j.errors && Object.keys(j.errors).length) return j;   // Fehler (z. B. rateLimit) nie zwischenspeichern
  ctx.waitUntil(cache.put(key, new Response(JSON.stringify(j), { headers: { 'content-type': 'application/json', 'cache-control': `public, max-age=${ttl}` } })));
  return j;
}

function slim(f, ev) {
  const fx = f.fixture || {}, st = fx.status || {}, lg = f.league || {}, t = f.teams || {}, g = f.goals || {};
  const out = {
    id: fx.id, ts: fx.timestamp, st: st.short, min: st.elapsed, ext: st.extra || null,
    lg: lg.id, ln: lg.name, lc: lg.country, rd: lg.round,
    h: (t.home || {}).name, a: (t.away || {}).name, gh: g.home, ga: g.away,
    ven: ((fx.venue || {}).city) || ''
  };
  const evs = ev || f.events || [];
  out.ev = evs.filter(e => e.type === 'Goal' || e.type === 'Card' || e.type === 'subst')
    .map(e => ({ m: (e.time || {}).elapsed, x: (e.time || {}).extra || null, side: (e.team || {}).id === (t.home || {}).id ? 'h' : 'a',
                 ty: e.type === 'Goal' ? (e.detail === 'Own Goal' ? 'og' : e.detail === 'Penalty' ? 'pen' : e.detail === 'Missed Penalty' ? 'mp' : 'g')
                   : e.type === 'Card' ? (e.detail === 'Red Card' || e.detail === 'Second Yellow card' ? 'rc' : 'yc') : 'sub',
                 p: (e.player || {}).name || '', p2: (e.assist || {}).name || '' }));
  return out;
}


// ---- Handball (API-Handball, gleicher API-Sports-Schlüssel; eigenes Kontingent: kostenlos 100 Abrufe/Tag)
// Sparsam: Tagesplan alle 30 Min., während laufender Spiele alle 5 Min. – Abrufe nur, wenn Besucher die Seite öffnen.
const HB = 'https://v1.handball.api-sports.io';
const HB_LIVE = new Set(['1H', '2H', 'HT', 'ET', 'BT', 'PT', 'LIVE']);
async function handball(ctx, hdr) {
  const day = berlinDate();
  let j = await cached(ctx, `/games?date=${day}&timezone=Europe/Berlin`, 1800, HB);
  const now = Date.now() / 1000;
  const want = g => { const c = ((g.country || {}).name || ''), n = ((g.league || {}).name || '');
    return (c === 'Germany' && /Bundesliga|DHB/i.test(n)) || /EHF Champions League|EHF European League|World Championship|European Championship/i.test(n); };
  let list = (j.response || []).filter(want);
  const anyLive = list.some(g => HB_LIVE.has((g.status || {}).short) || ((g.status || {}).short === 'NS' && g.timestamp <= now && g.timestamp > now - 3 * 3600));
  if (anyLive) { j = await cached(ctx, `/games?date=${day}&timezone=Europe/Berlin`, 300, HB, '/live'); list = (j.response || []).filter(want); }
  const m = list.map(g => ({ id: g.id, ts: g.timestamp, st: (g.status || {}).short, min: null, ext: null, lg: (g.league || {}).id, ln: (g.league || {}).name,
    lc: (g.country || {}).name, h: ((g.teams || {}).home || {}).name, a: ((g.teams || {}).away || {}).name,
    gh: (g.scores || {}).home, ga: (g.scores || {}).away, ev: [] })).sort((x, y) => x.ts - y.ts);
  const apierr = j.errors && Object.keys(j.errors).length ? Object.keys(j.errors).join(',') : '';
  return new Response(JSON.stringify({ ok: !apierr, apierr, total: j.results || 0, day, live: anyLive, m }), { headers: hdr });
}

export async function onRequest(ctx) {
  const hdr = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'public, max-age=30', 'x-robots-tag': 'noindex', 'access-control-allow-origin': '*' };
  if (!ctx.env.APISPORTS_KEY && !ctx.env.RAPIDAPI_KEY) return new Response(JSON.stringify({ ok: false, reason: 'nokey', m: [] }), { headers: hdr });
  try {
    if (new URL(ctx.request.url).searchParams.get('sport') === 'handball') return await handball(ctx, hdr);
    const day = berlinDate();
    const today = await cached(ctx, `/fixtures?date=${day}&timezone=Europe/Berlin`, 600);
    let list = (today.response || []).filter(f => ALL.has((f.league || {}).id));
    const now = Date.now() / 1000;
    const anyLive = list.some(f => { const st = ((f.fixture || {}).status || {}).short; return LIVE.has(st) || (st === 'NS' && f.fixture.timestamp <= now && f.fixture.timestamp > now - 3 * 3600); });
    if (anyLive) {
      const live = await cached(ctx, `/fixtures?live=${[...ALL].join('-')}&timezone=Europe/Berlin`, 60);
      const byId = new Map((live.response || []).map(f => [f.fixture.id, f]));
      list = list.map(f => byId.get(f.fixture.id) || f);
    }
    const m = list.map(f => slim(f)).sort((x, y) => (x.ts - y.ts) || (x.lg - y.lg));
    const apierr = today.errors && Object.keys(today.errors).length ? Object.keys(today.errors).join(',') : '';
    return new Response(JSON.stringify({ ok: !apierr, apierr, total: today.results || 0, day, live: anyLive, club: CLUB, nat: NAT, m }), { headers: hdr });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, reason: 'error', m: [] }), { headers: hdr });
  }
}
