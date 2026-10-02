/* TWN – Suche: lädt den Suchindex der Sprache (Monatsdateien) und durchsucht Titel, Vorspann, Text, Quellen und Datum. */
(function () {
  var f = document.querySelector('.sform'); if (!f) return;
  var base = f.dataset.base, hour = f.dataset.hour, q = f.querySelector('[name=q]'), ss = f.querySelector('[name=s]'), sp = f.querySelector('[name=p]');
  var stat = document.querySelector('.sstat'), list = document.querySelector('.sres'), more = document.querySelector('.smore');
  var DATA = [], loaded = false, loading = null, shown = 0, hits = [], PAGE = 30;
  function norm(t) { return (t || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/ё/g, 'е').replace(/ß/g, 'ss').replace(/[„“”"«»‚‘’]/g, ' '); }
  function esc(t) { return t.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function mark(t, terms) {
    var out = esc(t); terms.forEach(function (w) {
      if (w.length < 2) return; var nt = norm(out), i = nt.indexOf(w); if (i < 0) return;
      out = out.slice(0, i) + '<mark>' + out.slice(i, i + w.length) + '</mark>' + out.slice(i + w.length);
    }); return out;
  }
  function load() {
    if (loading) return loading;
    loading = fetch(base + 'index.json').then(function (r) { return r.json(); }).then(function (ix) {
      return Promise.all(ix.months.map(function (m) { return fetch(base + m + '.json').then(function (r) { return r.json(); }); }));
    }).then(function (parts) {
      parts.forEach(function (p) { p.forEach(function (it) { it._t = norm(it.t); it._d = norm(it.d); it._x = norm(it.x + ' ' + it.sn); DATA.push(it); }); });
      DATA.sort(function (a, b) { return (b.dt + b.tm).localeCompare(a.dt + a.tm); }); loaded = true;
    });
    return loading;
  }
  function fmt(it) { var d = it.dt.split('-'); return d[2] + '.' + d[1] + '.' + d[0] + ', ' + it.tm + (hour ? ' ' + hour : ''); }
  function run(push) {
    var raw = q.value.trim(), sec = ss.value, per = parseInt(sp.value || '0', 10);
    if (push !== false) { var u = new URL(location.href); u.searchParams.set('q', raw); sec ? u.searchParams.set('s', sec) : u.searchParams.delete('s'); per ? u.searchParams.set('p', per) : u.searchParams.delete('p'); history.replaceState(null, '', u); }
    if (!raw && !sec && !per) { list.innerHTML = ''; stat.textContent = ''; more.hidden = true; return; }
    stat.textContent = f.dataset.loading;
    load().then(function () {
      var terms = norm(raw).split(/\s+/).filter(Boolean), min = '';
      if (per) { var t = new Date(); t.setDate(t.getDate() - (per - 1)); min = t.toISOString().slice(0, 10); }
      hits = [];
      DATA.forEach(function (it) {
        if (sec && it.s !== sec) return; if (min && it.dt < min) return;
        var sc = 0;
        for (var i = 0; i < terms.length; i++) {
          var w = terms[i], a = it._t.indexOf(w) >= 0, b = it._d.indexOf(w) >= 0, c = it._x.indexOf(w) >= 0;
          if (!a && !b && !c) return; sc += (a ? 6 : 0) + (b ? 3 : 0) + (c ? 1 : 0);
        }
        hits.push({ it: it, sc: sc });
      });
      hits.sort(function (a, b) { return b.sc - a.sc || (b.it.dt + b.it.tm).localeCompare(a.it.dt + a.it.tm); });
      list.innerHTML = ''; shown = 0; render(terms);
      stat.textContent = hits.length ? f.dataset.found.replace('{n}', hits.length) : f.dataset.none;
    }).catch(function () { stat.textContent = f.dataset.none; });
  }
  var lastTerms = [];
  function render(terms) {
    if (terms) lastTerms = terms;
    var frag = document.createDocumentFragment();
    hits.slice(shown, shown + PAGE).forEach(function (h) {
      var it = h.it, li = document.createElement('li');
      li.innerHTML = '<a href="' + it.u + '"><div class="kick"><i></i>' + esc(it.sn) + ' · <time class="meta" datetime="' + it.dt + 'T' + it.tm + '">' + fmt(it) + '</time></div><h3>' + mark(it.t, lastTerms) + '</h3><p>' + mark(it.d, lastTerms) + '</p></a>';
      frag.appendChild(li);
    });
    list.appendChild(frag); shown = Math.min(hits.length, shown + PAGE); more.hidden = shown >= hits.length;
  }
  more.addEventListener('click', function () { render(); });
  f.addEventListener('submit', function (e) { e.preventDefault(); run(); });
  ss.addEventListener('change', function () { run(); }); sp.addEventListener('change', function () { run(); });
  var t; q.addEventListener('input', function () { clearTimeout(t); t = setTimeout(function () { if (q.value.trim().length >= 2 || !q.value.trim()) run(); }, 250); });
  q.addEventListener('focus', load, { once: true });
  var P = new URLSearchParams(location.search);
  q.value = P.get('q') || ''; ss.value = P.get('s') || ''; sp.value = P.get('p') || '';
  if (q.value || ss.value || sp.value) run(false); else q.focus();
})();
