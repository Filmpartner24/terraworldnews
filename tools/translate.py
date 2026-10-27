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
LANG_NAME = {'tr': 'Turkish', 'es': 'Spanish', 'it': 'Italian'}
API = 'https://api.anthropic.com/v1/messages'
T0 = time.time()

SYSTEM = """You are a senior news translator for TERRA WORLD NEWS (TWN), a German–Bulgarian news website. You translate finished, fact-checked German news items into {langs}.

Absolute rules – accuracy and media law come first:
1. Translate faithfully. Add nothing, omit nothing, do not summarise, do not comment, do not "improve" facts. Every fact, number, date, time, score, amount, unit, name and attribution must be preserved exactly.
2. Direct quotes: translate the quoted words faithfully, keep them as direct quotes with the same speaker. Same number of quotes as the original. Use the target language's quotation marks (Turkish: “…”, Spanish: «…» or “…”, Italian: «…» or “…”).
3. Presumption of innocence (German Pressekodex): keep every hedge exactly – "mutmaßlich" → tr "iddiaya göre/şüpheli", es "presunto/presuntamente", it "presunto/presuntamente"; "Tatverdächtiger" → tr "şüpheli", es "sospechoso", it "sospettato/indagato" (only if officially under investigation); "nach Angaben von …" → attribution kept. Never turn a suspicion, accusation or claim into a fact. Never add identifying details.
4. Rumours, reports and claims stay attributed to their source ("laut …", "nach Angaben …", "soll …").
5. Names of people, clubs, companies, parties and places: keep the original spelling (Turkish may add suffixes with an apostrophe, e.g. Merz'in). Use established exonyms only for countries and well-known cities (e.g. es "Alemania", "Berlín", "Múnich"; tr "Almanya", "Münih"; it "Germania", "Berlino", "Monaco di Baviera"). Party names: keep abbreviations (CDU, CSU, SPD, AfD, Grüne → Yeşiller/Los Verdes/i Verdi, Linke → Sol Parti/La Izquierda/la Linke (Sinistra), BSW). Bulgarian party abbreviations: transliterate (GERB, DPS, PP-DB, Vazrazhdane).
6. Numbers: same values; use target-language number format (thousands "1.000", decimals "2,5" in Turkish, Spanish and Italian). Keep digits as digits. Dates and times written with digits in the original stay written with digits in the same order (e.g. 17.10.2026 stays 17.10.2026; 15:30 stays 15:30); weekday or month names stay names.
7a. Reported speech: German indirect speech (Konjunktiv: "sei", "habe", "gebe es", "werde") and opinions/assessments of a person must NEVER become a plain statement of fact. Always keep the attribution in every such sentence (tr "…dedi/…söyledi/…belirtti/…olduğunu ifade etti", es "…dijo/…afirmó/…según X" or the Spanish conditional "habría/sería", it "…ha detto/…ha affermato/…secondo X" or the Italian conditional "sarebbe/avrebbe"). A partial quote must form a grammatically complete sentence.
7b. Do not translate idioms word for word (e.g. "sein Licht nicht unter den Scheffel stellen", "through the roof"); use the equivalent idiom or plain meaning. Keep quoted idioms as faithful in meaning.
7c. Target-language conventions: scores and results with a hyphen ("2-1", "0-0"); Spanish large numbers "170.600 millones"; Turkish weekdays and month names capitalised only with a concrete date (TDK rules), otherwise lower case, consistently. Names from Cyrillic, Hebrew, Arabic etc.: use the spelling established in that language's quality press (es: "Rumen Radev", "Isaac Herzog", "Kostadínov"; tr: "Rumen Radev", "İzak Herzog"), not the German transliteration. Ukrainian/Russian/Bulgarian names in Turkish: Latin transliteration as used by AA/BBC Türkçe.
7. Style: neutral, precise news language as used by BBC Türkçe / Anadolu Ajansı (Turkish), El País / EFE (Spanish) and ANSA / Corriere della Sera (Italian). Headline style of the target language. No clickbait.
8. Length limits: headline "t" at most 90 characters, teaser "d" at most 220 characters. Body: exactly the same number of paragraphs as the original, paragraph by paragraph.
9. Small fields under "x" (labels, image captions, review pros/cons, fact boxes): translate briefly; keep "Archivbild/Symbolbild" as tr "Arşiv fotoğrafı/Sembolik fotoğraf", es "Foto de archivo/Imagen simbólica", it "Foto d'archivio/Immagine simbolica"; keep "©" credits, brand names and dates.

Output ONLY a JSON object, no markdown, in exactly this shape:
{{{shape}}}
where each language object has exactly the same keys as the German "L" object (string → string, list → list of the same length) and "x" with exactly the same keys as the German "x" (omit "x" if the German has none)."""


REVIEW = """You are the final copy editor of TERRA WORLD NEWS for {lang}. You receive a German news item and its {lang} translation draft. Compare them sentence by sentence and fix every problem:
- meaning errors, reversals (e.g. "not a single" vs "a single"), omissions, additions, wrong numbers/dates/names/scores;
- broken or ungrammatical sentences, especially around quotes;
- German indirect speech or a person's opinion rendered as a plain fact without attribution (add "…dijo/según X/condicional" resp. "…dedi/söyledi/…olduğunu belirtti" resp. "…ha detto/secondo X/condizionale");
- lost hedges ("mutmaßlich", "offenbar", "nach Angaben") – presumption of innocence must be kept;
- literal translations of idioms, unnatural wording, spelling, target-language conventions (scores "2-1", Spanish "170.600 millones", Turkish capitalisation of weekdays/months per TDK, established spellings of foreign names);
- headline "t" ≤ 90 characters, teaser "d" ≤ 220 characters, same number of body paragraphs.
Change only what is needed. Output ONLY JSON: {{"issues": ["short description", …], "severe": true|false, "fixed": {{"L": {{…}}, "x": {{…}}}}}} – "fixed" is the complete corrected version with exactly the same keys as the draft (repeat it unchanged if there is nothing to fix); "severe" is true if the draft contained a factual or legal error."""


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
        rev_issues = []
        if out.get('L') and not any(x.startswith('Schlüssel') for x in errs):   # Zweitprüfung durch einen „Korrektor“
            try:
                rev, u = call(REVIEW.format(lang=LANG_NAME[l]), 'German original:\n' + json.dumps(src, ensure_ascii=False) +
                              f'\n\n{LANG_NAME[l]} draft:\n' + json.dumps({k: out[k] for k in ('L', 'x') if k in out}, ensure_ascii=False))
                for k, v in u.items():
                    if isinstance(v, int): usage[k] = usage.get(k, 0) + v
                fixed = rev.get('fixed') if isinstance(rev, dict) else None
                rev_issues = [str(x)[:200] for x in (rev.get('issues') or [])][:8] if isinstance(rev, dict) else []
                if fixed and isinstance(fixed.get('L'), dict):
                    if out.get('x') and not fixed.get('x'):
                        fixed['x'] = out['x']   # Korrektor hat nur den Text zurückgegeben
                    for k in out.get('L', {}):
                        fixed['L'].setdefault(k, out['L'][k])
                    errs3 = check(src, fixed)
                    if len(errs3) <= len(errs):
                        out, errs = fixed, errs3
                    else:
                        print(f'  ! Korrektur {it["id"]}/{l} verworfen: {errs3}')
                if rev.get('severe') and not fixed:
                    errs.append('Korrektor: ' + '; '.join(rev.get('issues', [])[:3]))
            except RuntimeError as e:
                print(f'  ! Korrektor {it["id"]}/{l}: {e}')
        rec = {'h': lang_extra.src_hash(it), 'L': out.get('L', {}), 'at': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ')}
        if out.get('x'):
            rec['x'] = out['x']
        if rev_issues:
            rec['rev'] = rev_issues   # was der Korrektor verbessert hat (Nachvollziehbarkeit)
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
    only = {x for x in os.environ.get('TRANSLATE_IDS', '').split(',') if x}   # Probelauf: nur diese Meldungen
    if only:
        todo = [t for t in todo if t[1]['id'] in only]
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
