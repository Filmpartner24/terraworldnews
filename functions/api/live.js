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

async function cached(ctx, path, ttl) {
  const key = new Request('https://terraworldnews.com/__live' + path);
  const cache = caches.default;
  const hit = await cache.match(key);
  if (hit) return hit.json();
  const r = await fetch(API + path, { headers: { 'x-apisports-key': ctx.env.APISPORTS_KEY } });
  if (!r.ok) throw new Error('api ' + r.status);
  const j = await r.json();
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

export async function onRequest(ctx) {
  const hdr = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'public, max-age=30', 'x-robots-tag': 'noindex', 'access-control-allow-origin': '*' };
  if (!ctx.env.APISPORTS_KEY) return new Response(JSON.stringify({ ok: false, reason: 'nokey', m: [] }), { headers: hdr });
  try {
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
    return new Response(JSON.stringify({ ok: true, day, live: anyLive, club: CLUB, nat: NAT, m }), { headers: hdr });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, reason: 'error', m: [] }), { headers: hdr });
  }
}
