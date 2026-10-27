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
import hashlib
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
OUTD = os.environ.get('TRANSLATE_OUT', 'translations')   # Probeläufe schreiben in einen eigenen Ordner

SYSTEM = """You are a senior news translator for TERRA WORLD NEWS (TWN), a German–Bulgarian news website. You translate finished, fact-checked German news items into {langs}.

Absolute rules – accuracy and media law come first:
1. Translate faithfully. Add nothing, omit nothing, do not summarise, do not comment, do not "improve" facts. Every fact, number, date, time, score, amount, unit, name and attribution must be preserved exactly.
2. Direct quotes: translate the quoted words faithfully, keep them as direct quotes with the same speaker. Same number of quotes as the original. Use the target language's quotation marks (Turkish: “…”, Spanish: «…» or “…”, Italian: «…» or “…”).
3. Presumption of innocence (German Pressekodex): keep every hedge exactly – "mutmaßlich" → tr "iddiaya göre/şüpheli", es "presunto/presuntamente", it "presunto/presuntamente"; "Tatverdächtiger" → tr "şüpheli", es "sospechoso", it "sospettato/indagato" (only if officially under investigation); "nach Angaben von …" → attribution kept. Never turn a suspicion, accusation or claim into a fact. Never add identifying details.
4. Rumours, reports and claims stay attributed to their source ("laut …", "nach Angaben …", "soll …").
5. Names of people, clubs, companies, parties and places: keep the original spelling (Turkish may add suffixes with an apostrophe, e.g. Merz'in). Use established exonyms only for countries and well-known cities (e.g. es "Alemania", "Berlín", "Múnich"; tr "Almanya", "Münih"; it "Germania", "Berlino", "Monaco di Baviera"). Party names: keep abbreviations (CDU, CSU, SPD, AfD, Grüne → Yeşiller/Los Verdes/i Verdi, Linke → Sol Parti/La Izquierda/la Linke (Sinistra), BSW). Bulgarian party abbreviations: transliterate (GERB, DPS, PP-DB, Vazrazhdane). Names from Bulgarian/Russian/Ukrainian (Cyrillic): NEVER copy the German transliteration (-ow, -ew, -jew, j for й/я/ю, sch, tsch, sh for ж). Use the English-style Latin transliteration used by BTA/Reuters: ж→zh, ш→sh, щ→sht, ч→ch, ц→ts, ъ→a, й→y, ю→yu, я→ya, -ов→-ov, -ев→-ev; e.g. Kostadinow→Kostadinov, Gjurow→Gyurov, Jotowa→Yotova, Radew→Radev, Scheljaskow→Zhelyazkov, Peewski→Peevski, Wasraschdane→Vazrazhdane, Selenskyj→Zelenskyy (es "Zelenski", it "Zelensky"), Wolodymyr→Volodymyr.
6. Numbers: same values; use target-language number format (thousands "1.000", decimals "2,5" in Turkish, Spanish and Italian). Keep digits as digits. Dates and times written with digits in the original stay written with digits in the same order (e.g. 17.10.2026 stays 17.10.2026; 15:30 stays 15:30); weekday or month names stay names.
7d. Headline "t" and teaser "d": keep every hedge and attribution of the German headline/teaser in the same field ("offenbar", "mutmaßlich", "soll", "laut", "nach Angaben"); never drop or move a qualifier (e.g. "fährt offenbar gezielt in Gruppe" → the car apparently targeted the group, not "apparently drove into a group").
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
Change only what is needed: leave correct sentences exactly as they are. Every change must keep the meaning identical to the German – never change logical relations (time vs. cause: "als" = when/while, not because; "und" vs. "aber"), tense, modality or who said what. If unsure, do not change. Output ONLY JSON: {{"issues": ["short description", …], "severe": true|false, "edits": [{{"old": "exact text from the draft", "new": "replacement"}}, …]}} – each "old" must be copied character for character from the draft and be long enough to occur only once (a few words to a sentence); "edits" is [] if nothing needs fixing; "severe" is true if the draft contained a factual or legal error."""


SHORTEN = """Shorten this {lang} news text to at most {n} characters. Keep its meaning, every hedge/attribution ("al parecer", "según", "iddiaya göre" …), names and numbers; cut only less important words. The German original ("de") is for reference. Output ONLY JSON: {{"text": "…"}}"""


def apply_edits(draft, edits):
    """Korrekturen des Korrektors als Ersetzungen anwenden (spart Ausgabe-Tokens gegenüber einer Komplettfassung).
    Gibt (neue Fassung, Zahl angewandter, Zahl nicht anwendbarer Korrekturen) zurück."""
    new = json.loads(json.dumps(draft))
    slots = []   # (Behälter, Schlüssel) aller Texte
    for part in ('L', 'x'):
        for k, v in (new.get(part) or {}).items():
            if isinstance(v, str):
                slots.append((new[part], k))
            elif isinstance(v, list):
                slots += [(v, i) for i, x in enumerate(v) if isinstance(x, str)]
    ok = bad = 0
    if not isinstance(edits, list):
        edits = []
    for ed in edits:
        if not isinstance(ed, dict):
            bad += 1; continue
        o, n = ed.get('old'), ed.get('new')
        if not isinstance(o, str) or not isinstance(n, str) or not o:
            bad += 1; continue
        hits = [(b, k) for b, k in slots if o in b[k]]
        if len(hits) == 1 and hits[0][0][hits[0][1]].count(o) == 1:
            b, k = hits[0]
            b[k] = b[k].replace(o, n); ok += 1; continue
        # unscharf: Anführungszeichen, Apostrophe und Leerraum dürfen abweichen
        pat = re.compile(''.join('[«»“”"„\'’‘‹›]' if c in '«»“”"„\'’‘‹›' else (r'\s+' if c.isspace() else re.escape(c)) for c in o.strip()))
        hits = [(b, k) for b, k in slots if len(pat.findall(b[k])) == 1]
        if len(hits) == 1:
            b, k = hits[0]
            b[k] = pat.sub(lambda m: n, b[k]); ok += 1
        else:
            bad += 1
    return new, ok, bad


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


HEDGE_DE = re.compile(r'\b(mutmaßlich\w*|offenbar|angeblich|laut|nach Angaben|zufolge)\b', re.I)
HEDGE_X = {   # Wörter, an denen eine Einschränkung/Zuordnung in der Übersetzung erkennbar ist
    'tr': r"göre|iddia|şüpheli|görünüşe|olduğu|söyledi|belirtti|açıkladı|bildirdi|anlaşılan|muhtemel|ileri sürül|ifade|tahmin|dediğ",
    'es': r"presunt|al parecer|aparente|supuest|según|habría|sería|estaría|afirm|dijo|asegur|indic|informa",
    'it': r"presunt|a quanto pare|apparente|secondo|sarebbe|avrebbe|sembr|ha detto|afferm|riferi|indica",
}


KONJ = re.compile(r'\b(sei|seien|habe|gebe|werde|müsse|solle|könne|dürfe|wolle|wisse|bestehe|liege|beruhe|komme|gehe|stehe|fehle|brauche|bleibe|handle|zeige|gelte|trage|sehe|halte|lasse|mache|bringe|finde|plane|arbeite|biete|erwarte|rechne|bedeute|treffe|führe|wäre|hätte|würde)\b')


def konj_sentences(L):
    """Sätze mit Konjunktiv (indirekte Rede) – müssen in der Übersetzung zugeordnet bleiben."""
    out = []
    for p in ([L.get('t', ''), L.get('d', '')] + (L.get('body') if isinstance(L.get('body'), list) else [])):
        for snt in re.split(r'(?<=[.!?])\s+', p or ''):
            if KONJ.search(snt) and '„' not in snt[:3]:
                out.append(snt.strip())
    return out[:12]


def german_leftovers(it, out):
    """Längere Wörter, die wörtlich aus dem Deutschen übernommen wurden, aber nicht in der englischen Fassung stehen
    (Namen stehen auch im Englischen) – Hinweis auf vergessene Übersetzung."""
    de = flat({k: v for k, v in it.get('de', {}).items() if isinstance(v, (str, list))})
    en = flat({k: v for k, v in (it.get('en') or {}).items() if isinstance(v, (str, list))})
    words = set(re.findall(r'[A-Za-zÄÖÜäöüß]{7,}', flat(out.get('L') or {})))
    return sorted(w for w in words if w in de and w not in en and re.search(r'[a-zäöüß]', w))[:6]


def check(src, out, lang=None):
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
    if lang in HEDGE_X:   # Einschränkung in Titel/Teaser darf nicht verloren gehen
        for k in ('t', 'd'):
            if HEDGE_DE.search(L.get(k, '') or '') and not re.search(HEDGE_X[lang], oL.get(k, '') or '', re.I):
                errs.append(f'Einschränkung/Zuordnung in "{k}" fehlt (Original: „{HEDGE_DE.search(L[k]).group(0)}“)')
    return errs


MODELS = {'t': os.environ.get('TRANSLATE_MODEL_T') or CFG.get('model_translate') or CFG['model'],
          'r': os.environ.get('TRANSLATE_MODEL_R') or CFG.get('model_review') or CFG['model']}
EFFORT = {'t': os.environ.get('TRANSLATE_EFFORT_T') or CFG.get('effort_translate'),
          'r': os.environ.get('TRANSLATE_EFFORT_R') or CFG.get('effort_review')}
PRICES = CFG.get('prices', {   # $ je 1 Mio. Tokens: Eingabe, Cache-Schreiben, Cache-Lesen, Ausgabe (inkl. Denk-Tokens)
    'claude-sonnet-5-5': [2.0, 2.5, 0.1, 10.0], 'claude-haiku-5-5': [0.1, 0.125, 0.01, 0.5]})


def build_body(system, user, kind):
    body = {'model': MODELS[kind], 'max_tokens': 16000,
            'system': [{'type': 'text', 'text': system, 'cache_control': {'type': 'ephemeral'}}],
            'messages': [{'role': 'user', 'content': user}]}
    if EFFORT[kind]:
        body['output_config'] = {'effort': EFFORT[kind]}   # weniger „Nachdenken“ = deutlich weniger Ausgabe-Tokens
    return body


def parse_msg(d, model, factor=1.0):
    """Antwort (Message) → (JSON-Ergebnis, Verbrauch mit Kosten in Mikro-$). factor 0.5 = Batch-Rabatt."""
    txt = ''.join(c.get('text', '') for c in d.get('content', []) if c.get('type') == 'text').strip()
    txt = re.sub(r'^```(?:json)?\s*|\s*```$', '', txt)
    u = {k: v for k, v in d.get('usage', {}).items() if isinstance(v, int)}
    pr = PRICES.get(model, [2.0, 2.5, 0.1, 10.0])
    u['usd_micro'] = round(factor * (u.get('input_tokens', 0) * pr[0] + u.get('cache_creation_input_tokens', 0) * pr[1] +
                                     u.get('cache_read_input_tokens', 0) * pr[2] + u.get('output_tokens', 0) * pr[3]))
    return json.loads(txt[txt.index('{'):txt.rindex('}') + 1]), u


def api(method, url, data=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data is not None else None, method=method, headers={
        'x-api-key': os.environ['ANTHROPIC_API_KEY'], 'anthropic-version': '2023-06-01', 'content-type': 'application/json'})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def call(system, user, kind='t'):
    body = build_body(system, user, kind)
    for attempt in range(4):
        try:
            d = json.loads(api('POST', API, body))
            return parse_msg(d, body['model'])
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


class NeedBatch(Exception):
    """Antwort liegt noch nicht vor – Anfrage(n) gehen in den nächsten Sammelauftrag."""
    def __init__(self, reqs):
        super().__init__(f'{len(reqs)} Anfrage(n) offen')
        self.reqs = reqs


class BatchCaller:
    """Spielt die Übersetzung einer Meldung mit gespeicherten Batch-Antworten ab; fehlt eine Antwort, wird sie angefordert.
    Der Ablauf ist bei gleichen Antworten immer gleich, deshalb geht er so Schritt für Schritt über mehrere Läufe voran."""
    def __init__(self, cache):
        self.cache, self.used = cache, set()

    def __call__(self, system, user, kind='t'):
        body = build_body(system, user, kind)
        key = hashlib.sha1(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        self.used.add(key)
        hit = self.cache.get(key)
        if hit is None:
            raise NeedBatch([(key, body)])
        if hit.get('err'):
            raise RuntimeError(hit['err'])
        return hit['res'], {}   # Kosten wurden schon beim Abholen gezählt


def translate(it, langs, caller=None):
    caller = caller or call
    src = {'L': {k: v for k, v in it['de'].items() if isinstance(v, (str, list)) and v}, 'x': lang_extra.extras(it)}
    if isinstance(src['L'].get('body'), str):
        src['L']['body'] = [p.strip() for p in src['L']['body'].replace('\r', '').split('\n') if p.strip()]
    if not src['x']:
        src.pop('x')
    system = SYSTEM.format(langs=' and '.join(LANG_NAME[l] for l in langs), shape=_shape(langs))
    ctx = f"Section: {it.get('s', '')}. English reference version (for meaning only; translate from German): " + json.dumps({k: it.get('en', {}).get(k) for k in ('t', 'd')}, ensure_ascii=False)
    user = ctx + '\n\nGerman original:\n' + json.dumps(src, ensure_ascii=False)
    ks = konj_sentences(src['L'])
    if ks:
        user += '\n\nWatch out – these German sentences are INDIRECT SPEECH (Konjunktiv): in every language keep the attribution (said/according to/conditional), never state them as fact:\n- ' + '\n- '.join(ks)
    usage = {}
    res, u = caller(system, user)
    for k, v in u.items():
        if isinstance(v, int): usage[k] = usage.get(k, 0) + v
    result, waiting = {}, []

    def one(l):
        nonlocal usage
        out = res.get(l) or {}
        errs = check(src, out, l)
        if errs:   # einmal gezielt nachbessern
            fix = user + f'\n\nYour previous {LANG_NAME[l]} translation had these problems: ' + '; '.join(errs) + \
                '. Translate again for ' + LANG_NAME[l] + ' only, fixing them. Output {"' + l + '": {...}} only.'
            try:
                res2, u = caller(SYSTEM.format(langs=LANG_NAME[l], shape=_shape([l])), fix)
                for k, v in u.items():
                    if isinstance(v, int): usage[k] = usage.get(k, 0) + v
                out2 = res2.get(l) or {}
                errs2 = check(src, out2, l)
                if not errs2 or len(errs2) < len(errs):
                    out, errs = out2, errs2
            except RuntimeError as e:
                errs.append(str(e))
        rev_issues, rev_dbg = [], None
        if out.get('L') and not any(x.startswith('Schlüssel') for x in errs):   # Zweitprüfung durch einen „Korrektor“
            try:
                hints = ''
                ks = konj_sentences(src['L'])
                if ks:
                    hints += '\n\nThese German sentences are INDIRECT SPEECH (Konjunktiv) – in the draft each must keep an explicit attribution or a conditional/reporting marker; fix every one that reads like a plain fact:\n- ' + '\n- '.join(ks)
                lo = german_leftovers(it, out)
                if lo:
                    hints += '\n\nThese German words appear untranslated in the draft – translate them unless they are proper names: ' + ', '.join(lo)
                rev, u = caller(REVIEW.format(lang=LANG_NAME[l]), 'German original:\n' + json.dumps(src, ensure_ascii=False) + hints +
                              f'\n\n{LANG_NAME[l]} draft:\n' + json.dumps({k: out[k] for k in ('L', 'x') if k in out}, ensure_ascii=False), 'r')
                for k, v in u.items():
                    if isinstance(v, int): usage[k] = usage.get(k, 0) + v
                rev = rev if isinstance(rev, dict) else {}
                iss = rev.get('issues') if isinstance(rev.get('issues'), list) else ([rev['issues']] if rev.get('issues') else [])
                rev_issues = [str(x)[:200] for x in iss][:8]
                draft = {k: out[k] for k in ('L', 'x') if k in out}
                fixed, n_ok, n_bad = apply_edits(draft, rev.get('edits'))
                rev_dbg = [len(iss), n_ok, n_bad]
                errs3 = check(src, fixed, l) if n_ok else errs
                if n_ok and len(errs3) <= len(errs):
                    out, errs = fixed, errs3
                elif n_ok:
                    print(f'  ! Korrektur {it["id"]}/{l} verworfen: {errs3}')
                    rev_issues = []
                    if rev.get('severe'):
                        errs.append('Korrektor: schwerer Fehler, Korrektur nicht prüfbar')
                if n_bad:
                    print(f'  ! {it["id"]}/{l}: {n_bad} Korrektur(en) nicht anwendbar')
                if rev.get('severe') and (n_bad or not n_ok):
                    errs.append('Korrektor: schwerer Fehler, Korrektur nicht (vollständig) anwendbar')
                if not n_ok:
                    rev_issues = []
            except RuntimeError as e:
                print(f'  ! Korrektor {it["id"]}/{l}: {e}')
        for k, lim in (('t', 90), ('d', 220)):   # zu lange Titel/Teaser gezielt kürzen statt die Meldung zurückzuhalten
            txt = (out.get('L') or {}).get(k)
            if isinstance(txt, str) and len(txt) > lim:
                try:
                    r, u = caller(SHORTEN.format(lang=LANG_NAME[l], n=lim - 5), json.dumps({'de': src['L'].get(k, ''), 'text': txt}, ensure_ascii=False), 't')
                    for kk, v in u.items():
                        if isinstance(v, int): usage[kk] = usage.get(kk, 0) + v
                    short = r.get('text') if isinstance(r, dict) else None
                    if isinstance(short, str) and 0 < len(short) <= lim:
                        out['L'][k] = short
                        errs = check(src, out, l)
                except RuntimeError as e:
                    print(f'  ! Kürzen {it["id"]}/{l}: {e}')
        rec = {'h': lang_extra.src_hash(it), 'L': out.get('L', {}), 'at': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ')}
        if out.get('x'):
            rec['x'] = out['x']
        if rev_dbg:
            rec['rev_dbg'] = rev_dbg   # Korrektor: gemeldete Probleme / angewandte / nicht anwendbare Korrekturen
        if rev_issues:
            rec['rev'] = rev_issues   # was der Korrektor verbessert hat (Nachvollziehbarkeit)
        if errs:
            rec['flag'] = errs
        result[l] = rec

    for l in langs:
        try:
            one(l)
        except NeedBatch as nb:   # diese Sprache wartet noch auf eine Batch-Antwort, die andere kann weiterlaufen
            waiting += nb.reqs
    if waiting:
        raise NeedBatch(waiting)
    return result, usage


def _status(fatal, force):
    """Zustand für Kontrollaufgaben (nur bei Änderung schreiben, sonst entstünde bei jedem Lauf ein Commit)."""
    st = {'ok': fatal is None, 'error': re.sub(r',?"request_id":"[^"]*"', '', fatal)[:300] if fatal else None}
    sp = os.path.join(HERE, OUTD, 'status.json')
    old = json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else None
    if old != st and (force or old is not None):
        os.makedirs(os.path.dirname(sp), exist_ok=True)
        json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


PRICE = CFG.get('price_per_mtok', {'input_tokens': 2.0, 'cache_creation_input_tokens': 2.5, 'cache_read_input_tokens': 0.1, 'output_tokens': 10.0})


def cost(tok):
    if 'usd_micro' in tok:
        return tok['usd_micro'] / 1e6
    return sum(tok.get(k, 0) * v for k, v in PRICE.items()) / 1e6


def usage_file():
    return os.path.join(HERE, OUTD, 'usage', datetime.datetime.utcnow().strftime('%Y-%m') + '.json')


BATCH_API = 'https://api.anthropic.com/v1/messages/batches'


def run_batch(items, store, flagged, spent, budget):
    """Batch-Ablauf: fertige Sammelaufträge abholen, Meldungen mit den Antworten weiterführen, neue Anfragen sammeln und senden."""
    sp = os.path.join(HERE, OUTD, 'batch', 'state.json')
    st = json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else {}
    st.setdefault('batches', []); st.setdefault('inflight', {}); st.setdefault('cache', {}); st.setdefault('tries', {})
    before = json.dumps(st, sort_keys=True)
    tot, done, fatal = {}, 0, None
    now = datetime.datetime.utcnow()
    # 1) fertige Sammelaufträge abholen
    for bid in list(st['batches']):
        try:
            b = json.loads(api('GET', f'{BATCH_API}/{bid}'))
        except urllib.error.HTTPError as e:
            print(f'  ! Batch {bid}: HTTP {e.code}'); continue
        if b.get('processing_status') != 'ended':
            continue
        lines = api('GET', b['results_url']).decode('utf-8').splitlines() if b.get('results_url') else []
        for ln in lines:
            if not ln.strip():
                continue
            r = json.loads(ln); key = r.get('custom_id'); res = r.get('result') or {}
            st['inflight'].pop(key, None)
            if res.get('type') == 'succeeded':
                msg = res['message']
                try:
                    out, u = parse_msg(msg, msg.get('model', ''), 0.5)
                    st['cache'][key] = {'res': out, 't': now.isoformat()}
                except (ValueError, KeyError):
                    u = parse_msg({'usage': msg.get('usage', {})} | {'content': [{'type': 'text', 'text': '{}'}]}, msg.get('model', ''), 0.5)[1]
                    st['tries'][key] = st['tries'].get(key, 0) + 1
                    if st['tries'][key] >= 2:
                        st['cache'][key] = {'err': 'Antwort nicht lesbar', 't': now.isoformat()}
                for k, v in u.items(): tot[k] = tot.get(k, 0) + v
            else:   # errored / expired / canceled: noch einmal anfordern, nach 3 Versuchen aufgeben
                st['tries'][key] = st['tries'].get(key, 0) + 1
                if st['tries'][key] >= 3:
                    st['cache'][key] = {'err': f'Batch: {res.get("type")}', 't': now.isoformat()}
        for k in [k for k, v in st['inflight'].items() if v == bid]:
            st['inflight'].pop(k)
        st['batches'].remove(bid)
    # 2) Meldungen mit den vorliegenden Antworten weiterführen
    new, used_done = {}, set()
    for date, it, need, _b in items:
        bc = BatchCaller(st['cache'])
        try:
            res, _u = translate(it, need, bc)
        except NeedBatch as nb:
            for key, body in nb.reqs:
                if key not in st['inflight']:
                    new[key] = body
            continue
        except Exception as e:
            print(f'  ! {it["id"]}: {type(e).__name__}: {e}'); continue
        used_done |= bc.used
        for l, rec in res.items():
            store[os.path.join(HERE, OUTD, l, f'{date}.json')]['items'][it['id']] = rec
            if rec.get('flag'):
                flagged.append({'id': it['id'], 'date': date, 'lang': l, 'why': rec['flag']})
        done += 1
    for k in used_done:   # erledigt – Antworten nicht mehr nötig
        st['cache'].pop(k, None); st['tries'].pop(k, None)
    old = (now - datetime.timedelta(days=3)).isoformat()
    for k in [k for k, v in st['cache'].items() if v.get('t', '') < old]:
        st['cache'].pop(k)
    # 3) neue Anfragen als Sammelauftrag senden
    if new and spent + cost(tot) < budget:
        reqs = [{'custom_id': k, 'params': b} for k, b in list(new.items())[:2000]]
        try:
            r = json.loads(api('POST', BATCH_API, {'requests': reqs}))
            st['batches'].append(r['id'])
            for q in reqs:
                st['inflight'][q['custom_id']] = r['id']
            print(f'translate: Sammelauftrag {r["id"]} mit {len(reqs)} Anfragen gesendet')
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors='replace')[:300]
            print(f'  ! Sammelauftrag nicht gesendet: HTTP {e.code} {msg}')
            if e.code in (400, 401, 403) and ('credit' in msg or 'billing' in msg or e.code in (401, 403)):
                fatal = f'API nicht nutzbar ({e.code}): {msg}'
    print(f'translate: Batch – {done} fertig, {len(new)} neue Anfragen, {len(st["inflight"])} in Arbeit, {len(st["batches"])} Aufträge offen')
    if json.dumps(st, sort_keys=True) != before:
        os.makedirs(os.path.dirname(sp), exist_ok=True)
        json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    return tot, done, fatal


def main():
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print('translate: kein ANTHROPIC_API_KEY – übersprungen'); return
    # Monatsbudget (Nedy 27.10.2026: unter dem API-Guthaben von 200 $ bleiben)
    uf = usage_file()
    month = json.load(open(uf, encoding='utf-8')) if os.path.exists(uf) else {'usd': 0.0, 'tokens': {}, 'items': 0}
    budget = float(CFG.get('monthly_budget_usd', 190))
    if month['usd'] >= budget:
        print(f'translate: Monatsbudget erreicht ({month["usd"]:.2f} $ von {budget:.0f} $) – keine Übersetzungen bis Monatsende')
        _status(f'Monatsbudget erreicht ({month["usd"]:.2f} $ von {budget:.0f} $)', True); return
    langs, start = (os.environ.get('TRANSLATE_LANGS') or ','.join(CFG['langs'])).split(','), CFG['start']
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
                fp = os.path.join(HERE, OUTD, l, f'{d["date"]}.json')
                if fp not in store:
                    store[fp] = json.load(open(fp, encoding='utf-8')) if os.path.exists(fp) else {'date': d['date'], 'items': {}}
                old = store[fp]['items'].get(it['id'])
                if not old or old.get('h') != h:
                    need.append(l)
            if need:
                todo.append((d['date'], it, need, f.endswith('-breaking.json')))
    todo.sort(key=lambda x: (x[0], x[1].get('time', '')), reverse=True)   # neueste zuerst
    only = {x for x in os.environ.get('TRANSLATE_IDS', '').split(',') if x}   # Probelauf: nur diese Meldungen
    if only:
        todo = [t for t in todo if t[1]['id'] in only]
    tot, done, flagged, fatal = {}, 0, [], None
    if CFG.get('batch') and (not only or os.environ.get('TRANSLATE_FORCE_BATCH')):   # Sammelauftrag (50 % günstiger): alles außer Breaking News (Nedy 27.10.2026)
        forced = bool(os.environ.get('TRANSLATE_FORCE_BATCH'))
        bt = [t for t in todo if forced or not t[3]]
        todo = [t for t in todo if t[3] and not forced]
        try:
            ub, nb_done, fatal = run_batch(bt, store, flagged, month['usd'], budget)
            for k, v in ub.items(): tot[k] = tot.get(k, 0) + v
            done += nb_done
        except Exception as e:
            print(f'translate: Batch-Fehler {type(e).__name__}: {e}')
    todo = todo[:CFG.get('max_items_per_run', 200)]
    print(f'translate: {len(todo)} Meldungen sofort')
    with cf.ThreadPoolExecutor(CFG.get('workers', 6)) as ex:
        futs = {ex.submit(translate, it, need): (date, it) for date, it, need, _b in todo} if not fatal else {}
        for fu in cf.as_completed(futs):
            date, it = futs[fu]
            try:
                res, u = fu.result()
            except SystemExit as e:   # Guthaben/Limit erreicht oder Schlüssel ungültig: Bisheriges speichern, Rest später
                fatal = str(e); print(f'translate: {e}'); ex.shutdown(cancel_futures=True); break
            except Exception as e:   # einzelne Meldung fehlerhaft – Lauf nicht abbrechen
                print(f'  ! {it["id"]}: {type(e).__name__}: {e}'); continue
            for k, v in u.items(): tot[k] = tot.get(k, 0) + v
            for l, rec in res.items():
                fp = os.path.join(HERE, OUTD, l, f'{date}.json')
                store[fp]['items'][it['id']] = rec
                if rec.get('flag'):
                    flagged.append({'id': it['id'], 'date': date, 'lang': l, 'why': rec['flag']})
            done += 1
            if month['usd'] + cost(tot) >= budget:
                fatal = f'Monatsbudget erreicht ({month["usd"] + cost(tot):.2f} $ von {budget:.0f} $)'
                print('translate: ' + fatal); ex.shutdown(cancel_futures=True); break
            if time.time() - T0 > CFG.get('max_seconds', 600):
                print('translate: Zeitlimit erreicht – Rest beim nächsten Lauf'); ex.shutdown(cancel_futures=True); break
    for fp, data in store.items():
        if data['items']:
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            json.dump(data, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
    # Liste aller markierten (nicht veröffentlichten) Übersetzungen
    allf = []
    for fp in [f for x in ('tr', 'es', 'it') for f in glob.glob(os.path.join(HERE, OUTD, x, '*.json'))]:   # nur Sprachordner (nicht usage/)
        l = fp.split(os.sep)[-2]
        for k, rec in json.load(open(fp, encoding='utf-8')).get('items', {}).items():
            if rec.get('flag'):
                allf.append({'date': os.path.basename(fp)[:10], 'lang': l, 'id': k, 'why': rec['flag']})
    if allf or os.path.exists(os.path.join(HERE, OUTD, 'flagged.json')):
        os.makedirs(os.path.join(HERE, OUTD), exist_ok=True)
        json.dump(sorted(allf, key=lambda x: (x['date'], x['id'], x['lang'])), open(os.path.join(HERE, OUTD, 'flagged.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if tot:
        for k, v in tot.items(): month['tokens'][k] = month['tokens'].get(k, 0) + v
        month['usd'] = round(month['usd'] + cost(tot), 4); month['items'] = month.get('items', 0) + done
        os.makedirs(os.path.dirname(uf), exist_ok=True)
        json.dump(month, open(uf, 'w', encoding='utf-8'), indent=1)
        print(f'translate: Monat bisher {month["usd"]:.2f} $ (Budget {budget:.0f} $)')
    _status(fatal, bool(todo))
    print(f'translate: {done} übersetzt, {len(flagged)} markiert, Tokens {tot}')


if __name__ == '__main__':
    main()
