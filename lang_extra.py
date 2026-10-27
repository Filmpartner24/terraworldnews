"""Zusatzsprachen Türkisch (tr) und Spanisch (es) – seit 27.10.2026 (Nedy).

- apply(g): ergänzt alle sprachabhängigen Tabellen in build.py um tr/es (aus i18n/ui_tr_es.json).
  Tabellen, für die es (noch) keine Übersetzung gibt, bekommen automatisch die englische Fassung,
  damit neue Tabellen in build.py den Bau nie abbrechen lassen.
- merge(it): hängt die maschinellen Übersetzungen aus translations/<lang>/<datum>.json an eine Meldung.
  Eine Übersetzung gilt nur, solange der deutsche Text unverändert ist (Prüfsumme "h").
"""
import ast, copy, glob, hashlib, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
EXTRA = ('tr', 'es', 'it')   # Italienisch seit 27.10.2026 (zuerst nur übersetzt, Veröffentlichung über i18n/config.json → publish_langs)


def _conv(new, ref):
    """Wert in die Form des englischen Originals bringen (Tupel, Sets, verschachtelte Dicts)."""
    if isinstance(ref, set):
        return ast.literal_eval(new) if isinstance(new, str) else set(new)
    if isinstance(ref, tuple):
        return tuple(_conv(n, r) for n, r in zip(new, ref))
    if isinstance(ref, list) and isinstance(new, list):
        return [_conv(n, r) for n, r in zip(new, ref)] + new[len(ref):]
    if isinstance(ref, dict) and isinstance(new, dict):
        return {k: _conv(new[k], ref[k]) if k in ref else new[k] for k in new}
    return new


def _deepfill(new, ref):
    """Schlüssel, die build.py inzwischen neu hat (z. B. eine neue Rubrik), aus Englisch ergänzen."""
    if isinstance(new, dict) and isinstance(ref, dict):
        for k, v in ref.items():
            if k not in new:
                new[k] = copy.deepcopy(v)
            else:
                new[k] = _deepfill(new[k], v)
    return new


def _get(g, path):
    x = g[path[0]]
    for k in path[1:]:
        x = x[k]
    return x


def _fallback(x, depth=0):
    """Jede Tabelle mit bg/de/en-Schlüsseln bekommt fehlende tr/es als Kopie von en."""
    if depth > 5:
        return
    if isinstance(x, dict):
        ks = set(x.keys())
        if 'en' in ks and ('bg' in ks or 'de' in ks):
            for l in EXTRA:
                if l not in x:
                    x[l] = copy.deepcopy(x['en'])
            return
        for v in list(x.values()):
            _fallback(v, depth + 1)
    elif isinstance(x, (list, tuple)):
        for v in x:
            _fallback(v, depth + 1)


def apply(g):
    try:
        data = json.load(open(os.path.join(HERE, 'i18n', 'ui_tr_es.json'), encoding='utf-8'))
    except FileNotFoundError:
        data = []
    for ent in data:
        try:
            box = _get(g, ent['path'])
        except (KeyError, IndexError, TypeError):
            continue   # Tabelle in build.py inzwischen umbenannt/entfernt
        if not isinstance(box, dict):
            continue
        ref = box.get('en', box.get('de'))
        for l in EXTRA:
            if ent.get(l) is not None and l not in box:
                box[l] = _deepfill(_conv(ent[l], ref), ref)
    for n, v in list(g.items()):
        if n.startswith('__') or callable(v) or type(v).__name__ == 'module':
            continue
        if isinstance(v, (dict, list, tuple)):
            _fallback(v)


def src_hash(it):
    """Prüfsumme des deutschen Ausgangstexts (Titel, Teaser, Absätze, weitere Textfelder)."""
    de = it.get('de') or {}
    body = de.get('body', '')
    if isinstance(body, str):   # wie build.py: Text als ein Block -> Absätze
        body = [p.strip() for p in body.replace('\r', '').split('\n') if p.strip()]
    rest = {k: v for k, v in de.items() if k not in ('t', 'd', 'body')}
    s = json.dumps([de.get('t', ''), de.get('d', ''), body, rest], ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(s.encode('utf-8')).hexdigest()[:12]


def static_days(default):
    """Wie viele Tage tr/es-Artikel als Einzeldateien vorliegen (ältere: Archiv-Bündel, wie bei bg/de/en)."""
    if STATIC_OVERRIDE is not None:
        return STATIC_OVERRIDE
    try:
        return int(json.load(open(os.path.join(HERE, 'i18n', 'config.json'), encoding='utf-8')).get('static_days', default))
    except (FileNotFoundError, ValueError):
        return default


_CACHE = {}


def _load(l, date):
    k = (l, date)
    if k not in _CACHE:
        fp = os.path.join(HERE, 'translations', l, f'{date}.json')
        try:
            _CACHE[k] = json.load(open(fp, encoding='utf-8')).get('items', {})
        except (FileNotFoundError, ValueError):
            _CACHE[k] = {}
    return _CACHE[k]


def extras(it):
    """Kleine sprachabhängige Felder einer Meldung (z. B. kl, img.alt, rv.pro, facts): Pfad -> deutscher Wert."""
    out = {}
    for k, v in it.items():
        if k in ('bg', 'de', 'en') + EXTRA or k == 'yt':   # Videotitel bleiben im Original
            continue
        if isinstance(v, dict) and 'de' in v:
            out[k] = v['de']
        elif isinstance(v, dict):
            for kk, vv in v.items():
                if isinstance(vv, dict) and 'de' in vv:
                    out[f'{k}.{kk}'] = vv['de']
    return out


def _fill(it, l):
    """Fehlende Sprachfassung kleiner Felder: englischer Wert (verhindert Abbrüche im Bau)."""
    for v in list(it.values()):
        boxes = [v] + (list(v.values()) if isinstance(v, dict) else [])
        for b in boxes:
            if isinstance(b, dict) and 'en' in b and 'de' in b and l not in b:
                b[l] = copy.deepcopy(b['en'])


def _publish():
    try:
        return bool(json.load(open(os.path.join(HERE, 'i18n', 'config.json'), encoding='utf-8')).get('publish', True))
    except (FileNotFoundError, ValueError):
        return True


PUBLISH = _publish()   # false = tr/es werden weiter übersetzt, aber nicht auf der Seite gebaut


def _publish_langs():
    try:
        v = json.load(open(os.path.join(HERE, 'i18n', 'config.json'), encoding='utf-8')).get('publish_langs')
    except (FileNotFoundError, ValueError):
        v = None
    return set(v) if v is not None else set(EXTRA)


PUBLISH_LANGS = _publish_langs()   # welche Zusatzsprachen auf der Seite erscheinen (übersetzt werden alle aus config "langs")
STATIC_OVERRIDE = None   # vom Dateigrenzen-Schutz in build.py gesetzt


def merge(it, date):
    if not PUBLISH or not isinstance(it.get('de'), dict):
        return
    h = None
    for l in EXTRA:
        if l not in PUBLISH_LANGS:
            continue
        tr = _load(l, date).get(it['id'])
        if not tr or tr.get('flag'):
            continue   # keine oder markierte (nicht freigegebene) Übersetzung
        h = h or src_hash(it)
        if tr.get('h') != h:
            continue   # deutscher Text wurde nach der Übersetzung geändert → neue Übersetzung abwarten
        it[l] = dict(tr['L'])
        for k in ('t', 'd'):
            it[l].setdefault(k, (it.get('en') or {}).get(k, ''))
        for path, val in (tr.get('x') or {}).items():
            box = it
            for k in path.split('.'):
                box = box.get(k) if isinstance(box, dict) else None
            if isinstance(box, dict):
                box[l] = val
        _fill(it, l)


try:
    _INLINE = json.load(open(os.path.join(HERE, 'i18n', 'inline_tr_es.json'), encoding='utf-8'))
except FileNotFoundError:
    _INLINE = {}


def _tx(v, l):
    if isinstance(v, str):
        return (_INLINE.get(v) or {}).get(l, v)
    if isinstance(v, tuple):
        return tuple(_tx(x, l) for x in v)
    if isinstance(v, list):
        return [_tx(x, l) for x in v]
    if isinstance(v, dict):
        return {k: _tx(x, l) for k, x in v.items()}
    return v


def lx(d):
    """Inline-Tabelle {'bg':…, 'de':…, 'en':…} in build.py: tr/es aus i18n/inline_tr_es.json, sonst Englisch."""
    if 'en' in d:
        for l in EXTRA:
            if l not in d:
                d[l] = _tx(d['en'], l)
    return d


def _hook(d):
    """Beim Laden aller Daten-JSONs (Fußball, Boxen, Bilder …): kleine bg/de/en-Felder bekommen tr/es (Englisch bzw. Tabelle).
    Sprachblöcke ganzer Meldungen ({'t','d','body'}) werden NICHT kopiert – die kommen nur aus echten Übersetzungen."""
    if 'en' in d and ('bg' in d or 'de' in d):
        en = d['en']
        if isinstance(en, dict):
            return d
        for l in EXTRA:
            if l not in d:
                d[l] = _tx(en, l)
    return d


class _JSON:
    """Ersatz für das json-Modul in build.py (gleiche Funktionen, aber load/loads mit _hook)."""
    def __getattr__(self, n):
        return getattr(json, n)

    def load(self, fp, **kw):
        kw.setdefault('object_hook', _hook)
        return json.load(fp, **kw)

    def loads(self, s, **kw):
        kw.setdefault('object_hook', _hook)
        return json.loads(s, **kw)


JSON = _JSON()
