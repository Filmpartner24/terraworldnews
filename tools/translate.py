"""Türkisch- und Spanisch-Fassung aller neuen Meldungen (seit 27.10.2026, Nedy).

Läuft in der GitHub Action nach jedem Push. Übersetzt jede Meldung ab dem Startdatum (i18n/config.json)
aus dem DEUTSCHEN Text über die Anthropic-API (Claude Sonnet) und speichert das Ergebnis in
translations/<sprache>/<datum>.json. content/ wird nie verändert.

Sicherheitsnetz (automatischer Abgleich mit dem Original):
- alle Zahlen des deutschen Texts müssen in der Übersetzung vorkommen,
- gleiche Zahl von Absätzen und von wörtlichen Zitaten,
- Titel ≤ 90, Teaser ≤ 220 Zeichen.
Schlägt eine Prüfung fehl, wird einmal mit Hinweis neu übersetzt; schlägt sie wieder fehl, wird die Meldung
markiert ("flag") und NICHT veröffentlicht (Liste in translations/flagged.json).

Ohne ANTHROPIC_API_KEY tut das Skript nichts.
"""
import concurrent.futures as cf
import datetime
import glob
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import lang_extra  # noqa: E402

CFG = json.load(open(os.path.join(HERE, 'i18n', 'config.json'), encoding='utf-8'))
LANG_NAME = {'tr': 'Turkish', 'es': 'Spanish'}
API = 'https://api.anthropic.com/v1/messages'
T0 = time.time()

SYSTEM = """You are a senior news translator for TERRA WORLD NEWS (TWN), a German–Bulgarian news website. You translate finished, fact-checked German news items into {langs}.

Absolute rules – accuracy and media law come first:
1. Translate faithfully. Add nothing, omit nothing, do not summarise, do not comment, do not "improve" facts. Every fact, number, date, time, score, amount, unit, name and attribution must be preserved exactly.
2. Direct quotes: translate the quoted words faithfully, keep them as direct quotes with the same speaker. Same number of quotes as the original. Use the target language's quotation marks (Turkish: “…”, Spanish: «…» or “…”).
3. Presumption of innocence (German Pressekodex): keep every hedge exactly – "mutmaßlich" → tr "iddiaya göre/şüpheli", es "presunto/presuntamente"; "Tatverdächtiger" → tr "şüpheli", es "sospechoso"; "nach Angaben von …" → attribution kept. Never turn a suspicion, accusation or claim into a fact. Never add identifying details.
4. Rumours, reports and claims stay attributed to their source ("laut …", "nach Angaben …", "soll …").
5. Names of people, clubs, companies, parties and places: keep the original spelling (Turkish may add suffixes with an apostrophe, e.g. Merz'in). Use established exonyms only for countries and well-known cities (e.g. es "Alemania", "Berlín", "Múnich"; tr "Almanya", "Münih"). Party names: keep abbreviations (CDU, CSU, SPD, AfD, Grüne → Yeşiller/Los Verdes, Linke → Sol Parti/La Izquierda, BSW). Bulgarian party abbreviations: transliterate (GERB, DPS, PP-DB, Vazrazhdane).
6. Numbers: same values; use target-language number format (thousands "1.000", decimals "2,5" in both Turkish and Spanish). Keep digits as digits. Dates and times written with digits in the original stay written with digits in the same order (e.g. 17.10.2026 stays 17.10.2026; 15:30 stays 15:30); weekday or month names stay names.
7. Style: neutral, precise news language as used by BBC Türkçe / Anadolu Ajansı (Turkish) and El País / EFE (Spanish). Headline style of the target language. No clickbait.
8. Length limits: headline "t" at most 90 characters, teaser "d" at most 220 characters. Body: exactly the same number of paragraphs as the original, paragraph by paragraph.
9. Small fields under "x" (labels, image captions, review pros/cons, fact boxes): translate briefly; keep "Archivbild/Symbolbild" as tr "Arşiv fotoğrafı/Sembolik fotoğraf", es "Foto de archivo/Imagen simbólica"; keep "©" credits, brand names and dates.

Output ONLY a JSON object, no markdown, in exactly this shape:
{{{shape}}}
where each language object has exactly the same keys as the German "L" object (string → string, list → list of the same length) and "x" with exactly the same keys as the German "x" (omit "x" if the German has none)."""


def _shape(langs):
    return ', '.join(f'"{l}": {{"L": {{…}}, "x": {{…}}}}' for l in langs)


def nfold(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))


def flat(v):
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        return '\n'.join(flat(x) for x in v)
    if isinstance(v, dict):
        return '\n'.join(flat(x) for x in v.values())
    return ''


NUM = re.compile(r'\d+(?:[.,:/]\d+)*')


def nums(text):
    out = []
    for m in NUM.findall(text):
        out += [g for g in re.split(r'[.,:/]', m)]
    return out


QUOTES = re.compile(r'[„“”«»"]')


def n_quotes(text):
    return len(QUOTES.findall(text)) // 2


def check(src, out):
    """Fehlerliste (leer = in Ordnung)."""
    errs = []
    L, x = src['L'], src.get('x') or {}
    oL, ox = out.get('L'), out.get('x') or {}
    if not isinstance(oL, dict) or set(oL) != set(L):
        return ['Schlüssel im Text stimmen nicht']
    for k, v in L.items():
        if isinstance(v, list) != isinstance(oL[k], list) or (isinstance(v, list) and len(v) != len(oL[k])):
            errs.append(f'Absatzzahl in "{k}" stimmt nicht')
    if len(oL.get('t', '')) > 90:
        errs.append(f'Titel zu lang ({len(oL["t"])} Zeichen)')
    if len(oL.get('d', '')) > 220:
        errs.append(f'Teaser zu lang ({len(oL["d"])} Zeichen)')
    if set(ox) != set(x):
        errs.append('Zusatzfelder stimmen nicht')
    de_txt, tr_txt = flat(L) + '\n' + flat(x), flat(oL) + '\n' + flat(ox)
    a, b = nums(de_txt), nums(tr_txt)
    miss = [n for n in set(a) if b.count(n) < a.count(n) and not (n.isdigit() and len(n) == 1 and int(n) <= 12 and b.count(n) + 1 >= a.count(n))]
    if miss:
        errs.append('Zahlen fehlen oder weichen ab: ' + ', '.join(sorted(miss)[:8]))
    qa, qb = n_quotes(flat(L)), n_quotes(flat(oL))
    if qa and qb < qa:
        errs.append(f'Zitate fehlen ({qb} statt {qa})')
    return errs


def call(system, user):
    body = {'model': CFG['model'], 'max_tokens': 8000,
            'system': [{'type': 'text', 'text': system, 'cache_control': {'type': 'ephemeral'}}],
            'messages': [{'role': 'user', 'content': user}]}
    req = urllib.request.Request(API, data=json.dumps(body).encode(), headers={
        'x-api-key': os.environ['ANTHROPIC_API_KEY'], 'anthropic-version': '2023-06-01', 'content-type': 'application/json'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.load(r)
            txt = ''.join(c.get('text', '') for c in d.get('content', []) if c.get('type') == 'text').strip()
            txt = re.sub(r'^```(?:json)?\s*|\s*```$', '', txt)
            return json.loads(txt[txt.index('{'):txt.rindex('}') + 1]), d.get('usage', {})
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors='replace')[:300]
            if e.code in (429, 500, 502, 503, 529) and attempt < 3:
                time.sleep(10 * (attempt + 1)); continue
            if e.code in (400, 401, 403) and ('credit' in msg or 'billing' in msg or 'limit' in msg or e.code in (401, 403)):
                raise SystemExit(f'API nicht nutzbar ({e.code}): {msg}')
            raise RuntimeError(f'HTTP {e.code}: {msg}')
        except (ValueError, KeyError) as e:
            if attempt < 2:
                continue
            raise RuntimeError(f'Antwort nicht lesbar: {e}')
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < 3:
                time.sleep(10); continue
            raise RuntimeError(str(e))


def translate(it, langs):
    src = {'L': {k: v for k, v in it['de'].items() if isinstance(v, (str, list)) and v}, 'x': lang_extra.extras(it)}
    if isinstance(src['L'].get('body'), str):
        src['L']['body'] = [p.strip() for p in src['L']['body'].replace('\r', '').split('\n') if p.strip()]
    if not src['x']:
        src.pop('x')
    system = SYSTEM.format(langs=' and '.join(LANG_NAME[l] for l in langs), shape=_shape(langs))
    ctx = f"Section: {it.get('s', '')}. English reference version (for meaning only; translate from German): " + json.dumps({k: it.get('en', {}).get(k) for k in ('t', 'd')}, ensure_ascii=False)
    user = ctx + '\n\nGerman original:\n' + json.dumps(src, ensure_ascii=False)
    usage = {}
    res, u = call(system, user)
    for k, v in u.items():
        if isinstance(v, int): usage[k] = usage.get(k, 0) + v
    result = {}
    for l in langs:
        out = res.get(l) or {}
        errs = check(src, out)
        if errs:   # einmal gezielt nachbessern
            fix = user + f'\n\nYour previous {LANG_NAME[l]} translation had these problems: ' + '; '.join(errs) + \
                '. Translate again for ' + LANG_NAME[l] + ' only, fixing them. Output {"' + l + '": {...}} only.'
            try:
                res2, u = call(SYSTEM.format(langs=LANG_NAME[l], shape=_shape([l])), fix)
                for k, v in u.items():
                    if isinstance(v, int): usage[k] = usage.get(k, 0) + v
                out2 = res2.get(l) or {}
                errs2 = check(src, out2)
                if not errs2 or len(errs2) < len(errs):
                    out, errs = out2, errs2
            except RuntimeError as e:
                errs.append(str(e))
        rec = {'h': lang_extra.src_hash(it), 'L': out.get('L', {}), 'at': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ')}
        if out.get('x'):
            rec['x'] = out['x']
        if errs:
            rec['flag'] = errs
        result[l] = rec
    return result, usage


def main():
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print('translate: kein ANTHROPIC_API_KEY – übersprungen'); return
    langs, start = CFG['langs'], CFG['start']
    todo = []
    store = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'content', '*.json'))):
        date = os.path.basename(f)[:10]
        if date < start:
            continue
        try:
            d = json.load(open(f, encoding='utf-8'))
        except ValueError:
            continue
        for it in d.get('items', []):
            if not isinstance(it.get('de'), dict) or not it['de'].get('t'):
                continue
            h = lang_extra.src_hash(it)
            need = []
            for l in langs:
                fp = os.path.join(HERE, 'translations', l, f'{d["date"]}.json')
                if fp not in store:
                    store[fp] = json.load(open(fp, encoding='utf-8')) if os.path.exists(fp) else {'date': d['date'], 'items': {}}
                old = store[fp]['items'].get(it['id'])
                if not old or old.get('h') != h:
                    need.append(l)
            if need:
                todo.append((d['date'], it, need))
    todo.sort(key=lambda x: (x[0], x[1].get('time', '')), reverse=True)   # neueste zuerst
    todo = todo[:CFG.get('max_items_per_run', 200)]
    print(f'translate: {len(todo)} Meldungen offen')
    tot, done, flagged, fatal = {}, 0, [], None
    with cf.ThreadPoolExecutor(CFG.get('workers', 6)) as ex:
        futs = {ex.submit(translate, it, need): (date, it) for date, it, need in todo}
        for fu in cf.as_completed(futs):
            date, it = futs[fu]
            try:
                res, u = fu.result()
            except RuntimeError as e:
                print(f'  ! {it["id"]}: {e}'); continue
            except SystemExit as e:   # Guthaben/Limit erreicht oder Schlüssel ungültig: Bisheriges speichern, Rest später
                fatal = str(e); print(f'translate: {e}'); ex.shutdown(cancel_futures=True); break
            for k, v in u.items(): tot[k] = tot.get(k, 0) + v
            for l, rec in res.items():
                fp = os.path.join(HERE, 'translations', l, f'{date}.json')
                store[fp]['items'][it['id']] = rec
                if rec.get('flag'):
                    flagged.append({'id': it['id'], 'date': date, 'lang': l, 'why': rec['flag']})
            done += 1
            if time.time() - T0 > CFG.get('max_seconds', 600):
                print('translate: Zeitlimit erreicht – Rest beim nächsten Lauf'); ex.shutdown(cancel_futures=True); break
    for fp, data in store.items():
        if data['items']:
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            json.dump(data, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
    # Liste aller markierten (nicht veröffentlichten) Übersetzungen
    allf = []
    for fp in glob.glob(os.path.join(HERE, 'translations', '*', '*.json')):
        l = fp.split(os.sep)[-2]
        for k, rec in json.load(open(fp, encoding='utf-8')).get('items', {}).items():
            if rec.get('flag'):
                allf.append({'date': os.path.basename(fp)[:10], 'lang': l, 'id': k, 'why': rec['flag']})
    if allf or os.path.exists(os.path.join(HERE, 'translations', 'flagged.json')):
        os.makedirs(os.path.join(HERE, 'translations'), exist_ok=True)
        json.dump(sorted(allf, key=lambda x: (x['date'], x['id'], x['lang'])), open(os.path.join(HERE, 'translations', 'flagged.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # Zustand für Kontrollaufgaben (nur bei Änderung schreiben, sonst entstünde bei jedem Lauf ein Commit)
    st = {'ok': fatal is None, 'error': re.sub(r',?"request_id":"[^"]*"', '', fatal)[:300] if fatal else None}
    sp = os.path.join(HERE, 'translations', 'status.json')
    old = json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else None
    if old != st and (todo or old is not None):
        os.makedirs(os.path.dirname(sp), exist_ok=True)
        json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'translate: {done} übersetzt, {len(flagged)} markiert, Tokens {tot}')


if __name__ == '__main__':
    main()
