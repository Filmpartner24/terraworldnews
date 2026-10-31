// TWN Live-Abrufdienst (Nedy 31.10.2026): holt die Fußball-Spielstände zentral an EINER Stelle und speichert sie in Workers KV.
// Die Website (/api/live) liest nur noch aus KV – der Datenanbieter bekommt dadurch immer gleich viele Abrufe, egal wie viele Besucher kommen.
// Quellen: 1. API-Football (Schlüssel APISPORTS_KEY), 2. ESPN als Ersatz. Überwachung: Push-Meldung über ntfy, wenn Live-Daten ausfallen.
// Zeitplan: Cron jede Minute; während Spielen zwei Abrufe pro Lauf (alle 30 s), sonst alle 10 Minuten.

const API = 'https://v3.football.api-sports.io';
const CLUB = [78, 79, 81, 39, 140, 135, 61, 172, 2, 3, 848];
const NAT = [5, 10, 32, 960, 4, 1];
const ALL = new Set([...CLUB, ...NAT]);
const LIVE = new Set(['1H', 'HT', '2H', 'ET', 'BT', 'P', 'SUSP', 'INT', 'LIVE']);
const ESPN = { 'ger.1': [78, 'Bundesliga'], 'ger.2': [79, '2. Bundesliga'], 'ger.dfb_pokal': [81, 'DFB Pokal'], 'eng.1': [39, 'Premier League'], 'esp.1': [140, 'La Liga'],
  'ita.1': [135, 'Serie A'], 'fra.1': [61, 'Ligue 1'], 'uefa.champions': [2, 'UEFA Champions League'], 'uefa.europa': [3, 'UEFA Europa League'], 'uefa.europa.conf': [848, 'UEFA Europa Conference League'],
  'uefa.nations': [5, 'UEFA Nations League'], 'fifa.friendly': [10, 'Friendlies'], 'fifa.worldq.uefa': [32, 'World Cup - Qualification Europe'], 'uefa.euroq': [960, 'Euro Championship - Qualification'] };

const berlinDate = () => new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Berlin', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
const sleep = ms => new Promise(r => setTimeout(r, ms));

function slim(f) {
  const fx = f.fixture || {}, st = fx.status || {}, lg = f.league || {}, t = f.teams || {}, g = f.goals || {};
  const ev = (f.events || []).filter(e => e.type === 'Goal' || e.type === 'Card')
    .map(e => ({ m: (e.time || {}).elapsed, x: (e.time || {}).extra || null, side: (e.team || {}).id === (t.home || {}).id ? 'h' : 'a',
      ty: e.type === 'Goal' ? (e.detail === 'Own Goal' ? 'og' : e.detail === 'Penalty' ? 'pen' : e.detail === 'Missed Penalty' ? 'mp' : 'g') : (e.detail === 'Red Card' || e.detail === 'Second Yellow card' ? 'rc' : 'yc'),
      p: (e.player || {}).name || '', p2: (e.assist || {}).name || '' }));
  return { id: fx.id, ts: fx.timestamp, st: st.short, min: st.elapsed, ext: st.extra || null, lg: lg.id, ln: lg.name, lc: lg.country, rd: lg.round,
    h: (t.home || {}).name, a: (t.away || {}).name, gh: g.home, ga: g.away, ven: ((fx.venue || {}).city) || '', ev };
}
async function af(env, path) {
  const r = await fetch(API + path, { headers: { 'x-apisports-key': env.APISPORTS_KEY } });
  if (!r.ok) throw new Error('http ' + r.status);
  const j = await r.json();
  if (j.errors && Object.keys(j.errors).length) throw new Error(Object.keys(j.errors).join(','));
  return j;
}
function espnSlim(ev, lg, ln) {
  const c = (ev.competitions || [])[0] || {}, st = ev.status || {}, ty = st.type || {};
  const home = (c.competitors || []).find(x => x.homeAway === 'home') || {}, away = (c.competitors || []).find(x => x.homeAway === 'away') || {};
  let code = 'NS';
  if (ty.state === 'in') code = ty.name === 'STATUS_HALFTIME' ? 'HT' : ty.name === 'STATUS_SHOOTOUT' ? 'P' : (st.period || 1) >= 3 ? 'ET' : (st.period || 1) === 2 ? '2H' : '1H';
  else if (ty.state === 'post') code = ty.name === 'STATUS_FINAL_AET' ? 'AET' : ty.name === 'STATUS_FINAL_PEN' ? 'PEN' : /POSTPONED/.test(ty.name || '') ? 'PST' : /CANCEL|ABANDON/.test(ty.name || '') ? 'CANC' : 'FT';
  const mm = String(st.displayClock || '').match(/(\d+)'(?:\+(\d+))?/), started = ty.state !== 'pre';
  const ev2 = (c.details || []).filter(d => d.scoringPlay || d.yellowCard || d.redCard).map(d => {
    const m2 = String((d.clock || {}).displayValue || '').match(/(\d+)'(?:\+(\d+))?/);
    return { m: m2 ? +m2[1] : null, x: m2 && m2[2] ? +m2[2] : null, side: ((d.team || {}).id === (home.team || {}).id) ? 'h' : 'a',
      ty: d.scoringPlay ? (d.ownGoal ? 'og' : d.penaltyKick ? 'pen' : 'g') : d.redCard ? 'rc' : 'yc', p: (((d.athletesInvolved || [])[0]) || {}).displayName || '', p2: '' };
  });
  return { id: 'e' + ev.id, ts: Math.floor(Date.parse(ev.date) / 1000), st: code, min: mm ? +mm[1] : null, ext: mm && mm[2] ? +mm[2] : null, lg, ln, lc: '', rd: '',
    h: (home.team || {}).displayName || '', a: (away.team || {}).displayName || '', gh: started ? +(home.score || 0) : null, ga: started ? +(away.score || 0) : null, ven: '', ev: ev2 };
}
async function espnAll(day) {
  const ymd = day.replace(/-/g, '');
  const res = await Promise.all(Object.entries(ESPN).map(([code, [lg, ln]]) =>
    fetch('https://site.api.espn.com/apis/site/v2/sports/soccer/' + code + '/scoreboard?dates=' + ymd, { headers: { 'user-agent': 'TERRA-WORLD-NEWS-live/1.0 (terraworldnews.com)' } })
      .then(r => r.ok ? r.json() : { events: [] }).then(j => (j.events || []).map(ev => espnSlim(ev, lg, ln))).catch(() => null)));
  if (res.every(x => x === null)) throw new Error('espn down');
  return res.filter(Boolean).flat();
}
const isHot = (m, now) => LIVE.has(m.st) || (m.st === 'NS' && m.ts <= now + 120 && m.ts > now - 3 * 3600);

async function once(env, state) {
  const day = berlinDate(), now = Date.now() / 1000;
  const prevRaw = await env.LIVE_KV.get('live:football');
  const prev = prevRaw ? JSON.parse(prevRaw) : null;
  // Tagesspielplan von API-Football höchstens alle 10 Minuten (oder bei Tageswechsel)
  let plan = state.plan;
  if (!plan || plan.day !== day || now - plan.t > 600) {
    try { const j = await af(env, `/fixtures?date=${day}&timezone=Europe/Berlin`); plan = { day, t: now, m: (j.response || []).filter(f => ALL.has((f.league || {}).id)).map(slim) }; state.planErr = null; }
    catch (e) { state.planErr = String(e.message || e); plan = plan && plan.day === day ? plan : null; }
    state.plan = plan;
  }
  let m = plan ? plan.m.slice() : (prev && prev.day === day ? prev.m : []), src = 'apisports', err = state.planErr;
  const hot = m.some(x => isHot(x, now));
  if (plan && hot) {
    try {
      const j = await af(env, `/fixtures?live=${[...ALL].join('-')}&timezone=Europe/Berlin`);
      const byId = new Map((j.response || []).map(f => [f.fixture.id, slim(f)]));
      m = m.map(x => byId.get(x.id) || x); err = null;
    } catch (e) { err = String(e.message || e); }
  }
  if (!plan || err) {   // API-Football gesperrt/ausgefallen → ESPN
    try { const em = await espnAll(day); if (em.length || !plan) { m = em; src = 'espn'; } }
    catch (e) { src = plan ? 'apisports-stale' : 'none'; err = (err ? err + '; ' : '') + 'espn: ' + (e.message || e); }
  }
  m.sort((x, y) => (x.ts - y.ts) || (x.lg - y.lg));
  const live = m.some(x => LIVE.has(x.st));
  const body = { ok: src !== 'none', src, apierr: err || undefined, day, live, total: m.length, club: CLUB, nat: NAT, m, updated: Math.floor(now) };
  const cmp = JSON.stringify({ ...body, updated: 0 }), pcmp = prev ? JSON.stringify({ ...prev, updated: 0 }) : '';
  // Schreiben nur bei Änderung – oder spätestens alle 5 Minuten als Lebenszeichen (spart KV-Schreibvorgänge)
  if (cmp !== pcmp || !prev || now - (prev.updated || 0) > 300) await env.LIVE_KV.put('live:football', JSON.stringify(body));
  return { hot: hot || live, ok: body.ok && !(src === 'apisports-stale'), err };
}

async function alert(env, title, text, force = false) {
  if (!env.NTFY_TOPIC) return;
  const last = +(await env.LIVE_KV.get('health:lastalert') || 0), now = Date.now() / 1000;
  if (!force && now - last < 1800) return;   // höchstens eine Ausfall-Meldung pro 30 Minuten (Entwarnung immer)
  await fetch('https://ntfy.sh/' + env.NTFY_TOPIC, { method: 'POST', body: text, headers: { Title: title, Priority: 'high', Tags: 'warning,soccer' } }).catch(() => {});
  await env.LIVE_KV.put('health:lastalert', String(Math.floor(now)));
}

async function run(env) {
  const state = {};
  const r1 = await once(env, state);
  if (r1.hot) { await sleep(29000); await once(env, state); }   // während Spielen: zweiter Abruf nach 30 s
  // Überwachung: fallen beide Quellen bei laufenden/angesetzten Spielen 5 Minuten lang aus → Push aufs Handy
  const failSince = +(await env.LIVE_KV.get('health:failsince') || 0), now = Math.floor(Date.now() / 1000);
  if (r1.hot && !r1.ok) {
    if (!failSince) await env.LIVE_KV.put('health:failsince', String(now));
    else if (now - failSince >= 300) await alert(env, 'TWN: Live-Ergebnisse ausgefallen', 'Seit ' + Math.round((now - failSince) / 60) + ' Min. keine Live-Daten. Fehler: ' + (r1.err || 'unbekannt'));
  } else if (failSince) {
    await env.LIVE_KV.delete('health:failsince');
    if (now - failSince >= 300) await alert(env, 'TWN: Live-Ergebnisse wieder da', 'Live-Daten laufen wieder (Quelle aktiv).', true);
  }
}

export default {
  async scheduled(event, env, ctx) { ctx.waitUntil(run(env)); },
  async fetch(req, env) {   // Kontrolle im Browser: https://<worker>.workers.dev/ zeigt Zustand (ohne Schlüssel)
    const v = await env.LIVE_KV.get('live:football');
    const d = v ? JSON.parse(v) : null;
    return new Response(JSON.stringify(d ? { ok: d.ok, src: d.src, apierr: d.apierr, day: d.day, live: d.live, total: d.total, age_s: Math.floor(Date.now() / 1000) - d.updated } : { empty: true }), { headers: { 'content-type': 'application/json' } });
  }
};
