// Schlüssel APISPORTS_KEY in Cloudflare hinterlegt am 09.10.2026 (Pro bis 09.11.2026)
// 31.10.2026: Sperrschutz – Fehler werden 75 s zwischengespeichert, letzte gute Daten 6 Std. als Ersatz, Gesamtantwort 30 s je Rechenzentrum.
// Live-Spielstände (Fußball) für die Seiten Sport → Fußball und Sport → Länderspiele.
// Datenquelle: API-Football (api-sports.io). Der Schlüssel liegt als Cloudflare-Secret APISPORTS_KEY vor, nie im Repo.
// Abrufe werden serverseitig gecacht (Tagesspielplan 10 Min., Live-Daten 60 s), damit alle Besucher dieselbe Antwort
// bekommen und das Anfrage-Kontingent geschont wird. Live-Daten werden nur abgefragt, wenn heute gerade ein Spiel läuft.
// Ohne Schlüssel antwortet die Funktion mit {ok:false} – der Live-Block bleibt dann einfach ausgeblendet.

const API = 'https://v3.football.api-sports.io';
// Liga-IDs bei API-Football: Vereinsfußball (Fußball-Seite) und Nationalteams (Länderspiele-Seite)
const CLUB = [78, 79, 81, 39, 140, 135, 61, 172, 2, 3, 848];     // BL, 2. BL, DFB-Pokal, PL, La Liga, Serie A, Ligue 1, Parwa Liga, CL, EL, Conference League
const NAT = [5, 10, 32, 960, 4, 1];                        // Nations League, Freundschaftsspiele, WM-Quali Europa, EM-Quali, EM, WM
const ALL = new Set([...CLUB, ...NAT]);
const LIVE = new Set(['1H', 'HT', '2H', 'ET', 'BT', 'P', 'SUSP', 'INT', 'LIVE']);

function berlinDate() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Berlin', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
}

async function cached(ctx, path, ttl, base = API, ks = '') {
  // Schutz gegen Sperren (Nedy 31.10.2026: Live-Ergebnisse fehlten wegen „rateLimit“):
  // 1) gute Antworten ttl Sekunden zwischenspeichern, 2) zusätzlich eine „letzte gute“ Kopie 6 Std. aufheben,
  // 3) Fehler/Sperren 75 s zwischenspeichern, damit nicht jeder Besucher sofort erneut anfragt – solange die letzte gute Kopie ausliefern.
  const k = 'https://terraworldnews.com/__live' + (base === API ? '' : '/hb') + ks + path;
  const key = new Request(k), keyGood = new Request(k + '#good'), keyErr = new Request(k + '#err');
  const cache = caches.default;
  const hit = await cache.match(key);
  if (hit) return hit.json();
  const stale = async (why) => { const g = await cache.match(keyGood); if (g) { const j = await g.json(); j.__stale = why; return j; } return null; };
  if (await cache.match(keyErr)) { const s = await stale('cooldown'); if (s) return s; return { errors: { rateLimit: 'cooldown' }, response: [] }; }
  // Schlüssel: direkt bei API-Sports (APISPORTS_KEY) oder über RapidAPI (RAPIDAPI_KEY) – gleiche Daten, andere Adresse
  let url = base + path, headers = { 'x-apisports-key': ctx.env.APISPORTS_KEY };
  if (!ctx.env.APISPORTS_KEY && ctx.env.RAPIDAPI_KEY) {
    const host = base === API ? 'api-football-v1.p.rapidapi.com' : 'api-handball.p.rapidapi.com';
    url = 'https://' + host + (base === API ? '/v3' : '') + path;
    headers = { 'x-rapidapi-key': ctx.env.RAPIDAPI_KEY, 'x-rapidapi-host': host };
  }
  const markErr = () => ctx.waitUntil(cache.put(keyErr, new Response('1', { headers: { 'cache-control': 'public, max-age=75' } })));
  let r;
  try { r = await fetch(url, { headers }); } catch (e) { markErr(); const s = await stale('neterr'); if (s) return s; throw e; }
  if (!r.ok) { markErr(); const s = await stale('http' + r.status); if (s) return s; throw new Error('api ' + r.status); }
  const j = await r.json();
  if (j.errors && Object.keys(j.errors).length) { markErr(); const s = await stale(Object.keys(j.errors).join(',')); return s || j; }
  const body = JSON.stringify(j);
  ctx.waitUntil(cache.put(key, new Response(body, { headers: { 'content-type': 'application/json', 'cache-control': `public, max-age=${ttl}` } })));
  ctx.waitUntil(cache.put(keyGood, new Response(body, { headers: { 'content-type': 'application/json', 'cache-control': 'public, max-age=21600' } })));
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


// ---- Ersatzquelle ESPN (Nedy 31.10.2026: Live-Ergebnisse in Echtzeit): springt ein, wenn API-Football sperrt (rateLimit) oder ausfällt.
// Öffentliche Spielstand-Schnittstelle ohne Schlüssel; Daten werden in dasselbe Format wie API-Football übersetzt (gleiche Liga-IDs).
const ESPN = { 'ger.1': [78, 'Bundesliga'], 'ger.2': [79, '2. Bundesliga'], 'ger.dfb_pokal': [81, 'DFB Pokal'], 'eng.1': [39, 'Premier League'], 'esp.1': [140, 'La Liga'],
  'ita.1': [135, 'Serie A'], 'fra.1': [61, 'Ligue 1'], 'uefa.champions': [2, 'UEFA Champions League'], 'uefa.europa': [3, 'UEFA Europa League'], 'uefa.europa.conf': [848, 'UEFA Europa Conference League'],
  'uefa.nations': [5, 'UEFA Nations League'], 'fifa.friendly': [10, 'Friendlies'], 'fifa.worldq.uefa': [32, 'World Cup - Qualification Europe'], 'uefa.euroq': [960, 'Euro Championship - Qualification'] };
async function espnGet(ctx, code, ymd, ttl) {
  const key = new Request('https://terraworldnews.com/__espn/' + code + '/' + ymd);
  const hit = await caches.default.match(key);
  if (hit) return hit.json();
  const r = await fetch('https://site.api.espn.com/apis/site/v2/sports/soccer/' + code + '/scoreboard?dates=' + ymd, { headers: { 'user-agent': 'TERRA-WORLD-NEWS-live/1.0 (terraworldnews.com)' } });
  if (!r.ok) return { events: [] };
  const j = await r.json();
  ctx.waitUntil(caches.default.put(key, new Response(JSON.stringify(j), { headers: { 'content-type': 'application/json', 'cache-control': `public, max-age=${ttl}` } })));
  return j;
}
function espnSlim(ev, lg, ln) {
  const c = (ev.competitions || [])[0] || {}, st = ev.status || {}, ty = st.type || {};
  const home = (c.competitors || []).find(x => x.homeAway === 'home') || {}, away = (c.competitors || []).find(x => x.homeAway === 'away') || {};
  let code = 'NS';
  if (ty.state === 'in') code = ty.name === 'STATUS_HALFTIME' ? 'HT' : ty.name === 'STATUS_SHOOTOUT' ? 'P' : (st.period || 1) >= 3 ? 'ET' : (st.period || 1) === 2 ? '2H' : '1H';
  else if (ty.state === 'post') code = ty.name === 'STATUS_FINAL_AET' ? 'AET' : ty.name === 'STATUS_FINAL_PEN' ? 'PEN' : /POSTPONED/.test(ty.name || '') ? 'PST' : /CANCEL|ABANDON/.test(ty.name || '') ? 'CANC' : 'FT';
  const mm = String(st.displayClock || '').match(/(\d+)'(?:\+(\d+))?/);
  const started = ty.state !== 'pre';
  const ev2 = (c.details || []).filter(d => d.scoringPlay || d.yellowCard || d.redCard).map(d => {
    const m2 = String((d.clock || {}).displayValue || '').match(/(\d+)'(?:\+(\d+))?/);
    return { m: m2 ? +m2[1] : null, x: m2 && m2[2] ? +m2[2] : null, side: ((d.team || {}).id === (home.team || {}).id) ? 'h' : 'a',
      ty: d.scoringPlay ? (d.ownGoal ? 'og' : d.penaltyKick ? 'pen' : 'g') : d.redCard ? 'rc' : 'yc', p: (((d.athletesInvolved || [])[0]) || {}).displayName || '', p2: '' };
  });
  return { id: 'e' + ev.id, ts: Math.floor(Date.parse(ev.date) / 1000), st: code, min: mm ? +mm[1] : null, ext: mm && mm[2] ? +mm[2] : null, lg, ln, lc: '', rd: '',
    h: (home.team || {}).displayName || '', a: (away.team || {}).displayName || '', gh: started ? +(home.score || 0) : null, ga: started ? +(away.score || 0) : null, ven: ((c.venue || {}).address || {}).city || '', ev: ev2 };
}
async function espnAll(ctx, day) {
  const ymd = day.replace(/-/g, '');
  const res = await Promise.all(Object.entries(ESPN).map(([code, [lg, ln]]) => espnGet(ctx, code, ymd, 60).then(j => (j.events || []).map(ev => espnSlim(ev, lg, ln))).catch(() => [])));
  return res.flat().sort((x, y) => (x.ts - y.ts) || (x.lg - y.lg));
}
const LIVE_ST = new Set(['1H', 'HT', '2H', 'ET', 'BT', 'P', 'SUSP', 'INT', 'LIVE']);

export async function onRequest(ctx) {
  const hdr = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'public, max-age=30', 'x-robots-tag': 'noindex', 'access-control-allow-origin': '*' };
  if (!ctx.env.APISPORTS_KEY && !ctx.env.RAPIDAPI_KEY) return new Response(JSON.stringify({ ok: false, reason: 'nokey', m: [] }), { headers: hdr });
  if (new URL(ctx.request.url).searchParams.get('diag') === '1') {   // Diagnose ohne Schlüsselinhalt
    try {
      const r = await fetch(API + '/status', { headers: { 'x-apisports-key': ctx.env.APISPORTS_KEY || '' } });
      const t = await r.text(); let j = {}; try { j = JSON.parse(t); } catch (e) {}
      const h = {}; for (const [k, v] of r.headers) if (/ratelimit|requests|server|cf-ray|content-type/i.test(k)) h[k] = v;
      const sub = ((j.response || {}).subscription) || {}, req = ((j.response || {}).requests) || {};
      return new Response(JSON.stringify({ http: r.status, errors: j.errors, plan: sub.plan, active: sub.active, end: sub.end, req, keylen: (ctx.env.APISPORTS_KEY || '').length, headers: h, body: j.response ? undefined : t.slice(0, 300) }), { headers: hdr });
    } catch (e) { return new Response(JSON.stringify({ diagerr: String(e) }), { headers: hdr }); }
  }
  // Zentraler Abrufdienst (workers/live-fetcher, Nedy 31.10.2026): ist der KV-Speicher LIVE_KV verbunden und aktuell (< 3 Min.), nur daraus lesen
  if (ctx.env.LIVE_KV && new URL(ctx.request.url).searchParams.get('sport') !== 'handball') {
    try {
      const v = await ctx.env.LIVE_KV.get('live:football', { cacheTtl: 30 });
      if (v) { const d = JSON.parse(v); if (d.ok && Date.now() / 1000 - (d.updated || 0) < 180) return new Response(v, { headers: hdr }); }
    } catch (e) {}
  }
  const outKey = new Request('https://terraworldnews.com/__live/out' + (new URL(ctx.request.url).searchParams.get('sport') === 'handball' ? '/hb' : ''));
  const outHit = await caches.default.match(outKey);
  if (outHit) return new Response(await outHit.text(), { headers: hdr });   // eine gemeinsame Antwort je Rechenzentrum für 30 s
  const keep = (res) => { const c = res.clone(); ctx.waitUntil(c.text().then(t => caches.default.put(outKey, new Response(t, { headers: { 'content-type': 'application/json', 'cache-control': 'public, max-age=30' } })))); return res; };
  try {
    if (new URL(ctx.request.url).searchParams.get('sport') === 'handball') return keep(await handball(ctx, hdr));
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
    const apimsg = apierr ? JSON.stringify(today.errors).slice(0, 300) : undefined;   // Fehlertext der API (ohne Schlüssel) zur Diagnose
    const stale = today.__stale || undefined;
    if (apierr || stale || !m.length) {   // API-Football gesperrt/alt/leer → ESPN (frische Spielstände)
      const em = await espnAll(ctx, day).catch(() => []);
      if (em.length) return keep(new Response(JSON.stringify({ ok: true, src: 'espn', apierr: apierr || undefined, total: em.length, day, live: em.some(x => LIVE_ST.has(x.st)), club: CLUB, nat: NAT, m: em }), { headers: hdr }));
    }
    return keep(new Response(JSON.stringify({ ok: !apierr, apierr, apimsg, stale, total: today.results || 0, day, live: anyLive, club: CLUB, nat: NAT, m }), { headers: hdr }));
  } catch (e) {
    try {   // Ausfall von API-Football → ESPN
      const day = berlinDate(); const em = await espnAll(ctx, day);
      if (em.length) return keep(new Response(JSON.stringify({ ok: true, src: 'espn', total: em.length, day, live: em.some(x => LIVE_ST.has(x.st)), club: CLUB, nat: NAT, m: em }), { headers: hdr }));
    } catch (e2) {}
    return new Response(JSON.stringify({ ok: false, reason: 'error', m: [] }), { headers: hdr });
  }
}
