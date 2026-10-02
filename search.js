/* TWN – Suche über einen Wortindex (nach Wortanfang aufgeteilt). Lädt nur die Teile, die für die Suchwörter
   gebraucht werden – bleibt dadurch auch bei einem Archiv über viele Jahre schnell. */
(function () {
  var f = document.querySelector('.sform'); if (!f) return;
  var base = f.dataset.base, hour = f.dataset.hour, q = f.querySelector('[name=q]'), ss = f.querySelector('[name=s]'), sp = f.querySelector('[name=p]');
  var stat = document.querySelector('.sstat'), list = document.querySelector('.sres'), more = document.querySelector('.smore');
  var META = null, SH = {}, DC = {}, hits = [], shown = 0, PAGE = 30, lastTerms = [], STOP = {};
  function norm(t) { return (t || '').toLowerCase().normalize('NFD').replace(/ß/g, 'ss').replace(/[̀-ͯ]/g, ''); }
  function toks(t) { return (norm(t).match(/[\p{L}\p{N}]+/gu) || []).filter(function (w) { return w.length >= 2 && !STOP[w]; }); }
  function esc(t) { return t.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function key(w) { return Array.from(new TextEncoder().encode(w.slice(0, 2))).map(function (b) { return b.toString(16).padStart(2, '0'); }).join(''); }
  function getJ(u) { return fetch(u).then(function (r) { return r.ok ? r.json() : null; }); }
  function meta() { return META ? Promise.resolve(META) : getJ(base + 'meta.json').then(function (m) { META = m; (m.stop || []).forEach(function (w) { STOP[w] = 1; }); return m; }); }
  function shard(k) { if (!SH[k]) SH[k] = getJ(base + 't/' + k + '.json').then(function (j) { return j || {}; }); return SH[k]; }
  function chunk(c) { if (!DC[c]) DC[c] = getJ(base + 'd/' + c + '.json'); return DC[c]; }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  // Datumsangaben in Suchbegriffe übersetzen: 02.10.2026 · 2026-10-02 · 2. Oktober 2026 · Oktober 2026 · 2.10.
  function parse(raw) {
    var t = norm(raw), terms = [], m;
    t = t.replace(/\b(\d{4})-(\d{1,2})-(\d{1,2})\b/g, function (_, y, mo, d) { terms.push({ w: 'd' + y + pad(+mo) + pad(+d), x: 1 }); return ' '; });
    t = t.replace(/\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b/g, function (_, d, mo, y) { terms.push({ w: 'd' + y + pad(+mo) + pad(+d), x: 1 }); return ' '; });
    t = t.replace(/\b(\d{1,2})\.(\d{1,2})\.(?!\d)/g, function (_, d, mo) { terms.push({ w: 'md' + pad(+mo) + pad(+d), x: 1 }); return ' '; });
    var mons = META.months || {};
    Object.keys(mons).forEach(function (mn) {
      var re = new RegExp('(?:\\b(\\d{1,2})\\.?\\s+)?' + mn + '(?:\\s+(\\d{4}))?', 'g');
      t = t.replace(re, function (all, d, y) {
        var mo = pad(mons[mn]);
        if (d && y) terms.push({ w: 'd' + y + mo + pad(+d), x: 1 }); else if (d) terms.push({ w: 'md' + mo + pad(+d), x: 1 }); else if (y) terms.push({ w: 'ym' + y + mo, x: 1 }); else return all;
        return ' ';
      });
    });
    toks(t).forEach(function (w) { terms.push({ w: w, x: 0 }); });
    return terms;
  }
  function lookup(term, years) {
    return Promise.all(years.map(function (y) { return shard(y + '/' + key(term.w)); })).then(function (parts) {
      var res = {};
      parts.forEach(function (sh) {
        Object.keys(sh).forEach(function (w) {
          if (term.x ? w !== term.w : w.indexOf(term.w) !== 0) return;
          var exact = w === term.w;
          sh[w].forEach(function (p) { var id = p >> 1, sc = (p & 1 ? 6 : 1) + (exact ? 1 : 0); if (!res[id] || res[id] < sc) res[id] = sc; });
        });
      });
      return res;
    });
  }
  function fmt(r) { var d = r[4].split('-'); return d[2] + '.' + d[1] + '.' + d[0] + ', ' + r[5] + (hour ? ' ' + hour : ''); }
  function mark(t) {
    var out = esc(t); lastTerms.forEach(function (w) { if (w.length < 2) return; var i = norm(out).indexOf(w); if (i < 0) return; out = out.slice(0, i) + '<mark>' + out.slice(i, i + w.length) + '</mark>' + out.slice(i + w.length); });
    return out;
  }
  function run(push) {
    var raw = q.value.trim(), sec = ss.value, per = parseInt(sp.value || '0', 10);
    if (push !== false) { var u = new URL(location.href); u.searchParams.set('q', raw); sec ? u.searchParams.set('s', sec) : u.searchParams.delete('s'); per ? u.searchParams.set('p', per) : u.searchParams.delete('p'); history.replaceState(null, '', u); }
    if (!raw && !sec && !per) { list.innerHTML = ''; stat.textContent = ''; more.hidden = true; return; }
    stat.textContent = f.dataset.loading;
    meta().then(function (M) {
      var terms = parse(raw); lastTerms = terms.filter(function (t) { return !t.x; }).map(function (t) { return t.w; });
      var minId = 0;
      if (per) { var d = new Date(); d.setDate(d.getDate() - (per - 1)); var min = d.toISOString().slice(0, 10), best = M.n; Object.keys(M.days).forEach(function (k) { if (k >= min && M.days[k] < best) best = M.days[k]; }); minId = best; }
      var codeOf = {}; Object.keys(M.codes).forEach(function (c) { codeOf[M.codes[c]] = c; });
      var want = sec ? codeOf[sec] : null;
      var yrs = (M.years || []).filter(function (y) { return !per || y >= String(new Date(Date.now() - per * 864e5).getFullYear()); });
      var p = terms.length ? Promise.all(terms.map(function (t) { return lookup(t, yrs); })) : Promise.resolve(null);
      return p.then(function (maps) {
        var cand = [];
        if (maps) {
          maps.sort(function (a, b) { return Object.keys(a).length - Object.keys(b).length; });
          Object.keys(maps[0]).forEach(function (id) {
            id = +id; var sc = 0;
            for (var i = 0; i < maps.length; i++) { var v = maps[i][id]; if (!v) return; sc += v; }
            cand.push([id, sc]);
          });
        } else { for (var i = M.n - 1; i >= 0; i--) cand.push([i, 0]); }
        hits = cand.filter(function (c) { return c[0] >= minId && (!want || M.sec[c[0]] === want); }).sort(function (a, b) { return b[1] - a[1] || b[0] - a[0]; });
        list.innerHTML = ''; shown = 0;
        stat.textContent = hits.length ? f.dataset.found.replace('{n}', hits.length) : f.dataset.none;
        return render(M);
      });
    }).catch(function () { stat.textContent = f.dataset.none; });
  }
  function render(M) {
    M = M || META; var page = hits.slice(shown, shown + PAGE);
    var need = {}; page.forEach(function (h) { need[Math.floor(h[0] / M.chunk)] = 1; });
    return Promise.all(Object.keys(need).map(function (c) { return chunk(c).then(function (j) { need[c] = j || []; }); })).then(function () {
      var frag = document.createDocumentFragment();
      page.forEach(function (h) {
        var r = need[Math.floor(h[0] / M.chunk)][h[0] % M.chunk]; if (!r) return;
        var li = document.createElement('li');
        li.innerHTML = '<a href="' + r[0] + '"><div class="kick"><i></i>' + esc(M.names[r[3]] || '') + ' · <time class="meta" datetime="' + r[4] + 'T' + r[5] + '">' + fmt(r) + '</time></div><h3>' + mark(r[1]) + '</h3><p>' + mark(r[2]) + '</p></a>';
        frag.appendChild(li);
      });
      list.appendChild(frag); shown = Math.min(hits.length, shown + PAGE); more.hidden = shown >= hits.length;
    });
  }
  more.addEventListener('click', function () { render(); });
  f.addEventListener('submit', function (e) { e.preventDefault(); run(); });
  ss.addEventListener('change', function () { run(); }); sp.addEventListener('change', function () { run(); });
  var t; q.addEventListener('input', function () { clearTimeout(t); t = setTimeout(function () { if (q.value.trim().length >= 2 || !q.value.trim()) run(); }, 300); });
  q.addEventListener('focus', function () { meta(); }, { once: true });
  var P = new URLSearchParams(location.search);
  q.value = P.get('q') || ''; ss.value = P.get('s') || ''; sp.value = P.get('p') || '';
  if (q.value || ss.value || sp.value) run(false); else q.focus();
})();
