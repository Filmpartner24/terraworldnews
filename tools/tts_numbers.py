#!/usr/bin/env python3
"""Zahlen für die Sprachausgabe ausschreiben (Nedy 05.11.2026: „Zahlen als Wort, nicht als Zahl“).

spell(text, lang) – lang in de | en | bg. Erwartet Text ohne Tausendertrenner (siehe audio_bulletin.speakable).
DE/EN über num2words, Bulgarisch mit eigenem Regelwerk (num2words kann kein Bulgarisch).
"""
import re
from num2words import num2words

MONTHS = {
    'de': 'Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember',
    'en': 'January|February|March|April|May|June|July|August|September|October|November|December',
    'bg': 'януари|февруари|март|април|май|юни|юли|август|септември|октомври|ноември|декември',
}

# ---------- Bulgarisch ----------
BG_U = ['нула', 'едно', 'две', 'три', 'четири', 'пет', 'шест', 'седем', 'осем', 'девет', 'десет',
        'единадесет', 'дванадесет', 'тринадесет', 'четиринадесет', 'петнадесет', 'шестнадесет',
        'седемнадесет', 'осемнадесет', 'деветнадесет']
BG_T = ['', '', 'двадесет', 'тридесет', 'четиридесет', 'петдесет', 'шестдесет', 'седемдесет', 'осемдесет', 'деветдесет']
BG_H = ['', 'сто', 'двеста', 'триста', 'четиристотин', 'петстотин', 'шестстотин', 'седемстотин', 'осемстотин', 'деветстотин']
BG_ORD = {1: 'първи', 2: 'втори', 3: 'трети', 4: 'четвърти', 5: 'пети', 6: 'шести', 7: 'седми', 8: 'осми', 9: 'девети',
          10: 'десети', 11: 'единадесети', 12: 'дванадесети', 13: 'тринадесети', 14: 'четиринадесети',
          15: 'петнадесети', 16: 'шестнадесети', 17: 'седемнадесети', 18: 'осемнадесети', 19: 'деветнадесети',
          20: 'двадесети', 30: 'тридесети', 40: 'четиридесети', 50: 'петдесети', 60: 'шестдесети',
          70: 'седемдесети', 80: 'осемдесети', 90: 'деветдесети'}

def _join(words):
    """Bulgarisch: „и“ vor dem letzten Glied (сто петдесет и три, сто и пет)."""
    return words[0] if len(words) == 1 else ' '.join(words[:-1]) + ' и ' + words[-1]

def _bg_small(n):          # 1..999 → Wortliste (ohne „и“)
    w = []
    if n >= 100: w.append(BG_H[n // 100]); n %= 100
    if n >= 20:
        w.append(BG_T[n // 10]); n %= 10
        if n: w.append(BG_U[n])
    elif n: w.append(BG_U[n])
    return w

def bg_card(n):
    if n == 0: return 'нула'
    groups = []
    for size, one, many in ((10**9, 'един милиард', 'милиарда'), (10**6, 'един милион', 'милиона'), (1000, 'хиляда', 'хиляди')):
        if n >= size:
            q, n = divmod(n, size)
            if q == 1: groups.append([one])
            else:
                qw = _bg_small(q)
                if size > 1000 and qw[-1] == 'две': qw[-1] = 'два'      # два милиона
                if size > 1000 and qw[-1] == 'едно': qw[-1] = 'един'
                groups.append([_join(qw), many])
    rest = _bg_small(n) if n else []
    if rest and len(rest) == 1 and groups:          # хиляда и двеста, две хиляди и пет
        return ' '.join(' '.join(g) for g in groups) + ' и ' + rest[0]
    out = [' '.join(g) for g in groups] + ([_join(rest)] if rest else [])
    return ' '.join(out)

def bg_ord(n, fem=False):
    if n in BG_ORD: o = BG_ORD[n]
    elif n < 100: o = BG_T[n // 10] + ' и ' + BG_ORD[n % 10]
    elif n >= 2000 and n < 2100:
        r = n - 2000
        o = 'двехилядни' if r == 0 else 'две хиляди ' + bg_ord(r)
    else: return bg_card(n)
    return o[:-1] + 'а' if fem and o.endswith('и') else o

def bg_dec(i, f):
    return bg_card(int(i)) + ' цяло и ' + bg_card(int(f)) if f else bg_card(int(i))

# ---------- gemeinsam ----------
def _n2w(n, l, **kw):
    return num2words(n, lang=l, **kw)

def card(s, l):
    n = int(s)
    if l == 'bg': return bg_card(n)
    return _n2w(n, l)

ABBR = {'de': [(r'\bMrd\.', 'Milliarden'), (r'\bMio\.', 'Millionen'), (r'\bkm\b', 'Kilometer'), (r'\bca\.', 'circa'), (r'\bz\.\s?B\.', 'zum Beispiel')],
        'bg': [(r'\bмлрд\.', 'милиарда'), (r'\bмлн\.', 'милиона'), (r'\bкм\b', 'километра'), (r'\bлв\.', 'лева')],
        'en': [(r'\bbn\b', 'billion'), (r'\bkm\b', 'kilometres')]}

def spell(t, l):
    M = MONTHS[l]
    for a, b in ABBR[l]:
        t = re.sub(a + r'(?=\s+[A-ZÄÖÜА-Я])', b + '.', t) if a.endswith('\\.') else t   # Abkürzung am Satzende
        t = re.sub(a, b, t)
    t = re.sub(r'\b([A-Za-zА-Яа-я]{2,})(\d+)\b', r'\1 \2', t)        # COP31 → COP 31
    if l == 'en':
        t = re.sub(r'\b(20[1-9]\d)\b(?!\s?(?:euros|dollars|people|votes))', lambda m: _n2w(int(m.group(1)), 'en', to='year'), t)
    # Datum: DE „5. November“, BG „5 ноември“, EN „November 5“
    if l == 'de':
        t = re.sub(r'\b(\d{1,2})\.\s(' + M + r')\b', lambda m: _n2w(int(m.group(1)), 'de', to='ordinal') + 'n ' + m.group(2), t)
    elif l == 'bg':
        t = re.sub(r'\b(\d{1,2})\s(' + M + r')\b', lambda m: bg_ord(int(m.group(1))) + ' ' + m.group(2), t)
        t = re.sub(r'\b(\d{4})\s?г\.', lambda m: bg_ord(int(m.group(1)), fem=True) + ' година', t)
    else:
        t = re.sub(r'\b(' + M + r')\s(\d{1,2})\b(?!,\d)', lambda m: m.group(1) + ' ' + _n2w(int(m.group(2)), 'en', to='ordinal'), t)
        t = re.sub(r'\b(\d+)(st|nd|rd|th)\b', lambda m: _n2w(int(m.group(1)), 'en', to='ordinal'), t)
    # Prozent
    pct = {'de': ' Prozent', 'en': ' percent', 'bg': ' процента'}[l]
    t = re.sub(r'(\d)\s?%', r'\1' + pct, t)
    # Währungszeichen vor/nach der Zahl
    cur = {'de': {'€': 'Euro', '$': 'Dollar', '£': 'Pfund'}, 'en': {'€': 'euros', '$': 'dollars', '£': 'pounds'},
           'bg': {'€': 'евро', '$': 'долара', '£': 'паунда'}}[l]
    t = re.sub(r'([€$£])\s?(\d[\d.,]*)(\s(?:Millionen|Milliarden|million|billion|милиона|милиарда))?',
               lambda m: m.group(2) + (m.group(3) or '') + ' ' + cur[m.group(1)], t)
    t = re.sub(r'(\d)\s?([€$£])', lambda m: m.group(1) + ' ' + cur[m.group(2)], t)
    # Dezimalzahlen
    dsep = ',' if l in ('de', 'bg') else '.'
    def dec(m):
        i, f = m.group(1), m.group(2)
        if l == 'bg': return bg_card(int(i)) + ' цяло и ' + ' '.join(BG_U[int(c)] for c in f) if len(f) > 1 else bg_dec(i, f)
        word = {'de': 'Komma', 'en': 'point'}[l]
        return _n2w(int(i), l) + ' ' + word + ' ' + ' '.join(_n2w(int(c), l) for c in f)
    t = re.sub(r'\b(\d+)' + re.escape(dsep) + r'(\d+)\b', dec, t)
    # Jahreszahlen (DE/EN)
    if l in ('de', 'en'):
        yr = r'(?:Jahr|Jahre|Jahres|im|seit|bis|von|ab|vor|in|since|by|year|until|from|of)'
        t = re.sub(r'\b(' + yr + r'\s)(1[1-9]\d\d|20\d\d)\b', lambda m: m.group(1) + _n2w(int(m.group(2)), l, to='year'), t)
    # restliche ganze Zahlen
    BG_MASC = r'\s(?:милион|милиард|лев|долар|процент|час|ден|дни|месец|път|пъти|град|километ|метр|гол|мач|кръг|паунд)'
    def whole(m):
        n = int(m.group(1)); nxt = m.group(2) or ''
        if l == 'de' and n == 1 and re.match(r'\s[A-Za-zÄÖÜäöüß]', nxt): return 'ein' + nxt
        w = card(m.group(1), l)
        if l == 'de': w = re.sub(r'^ein(hundert|tausend)', r'\1', w)
        if l == 'bg' and re.match(BG_MASC, t[m.end(1):m.end(1) + 12]):
            w = re.sub(r'две$', 'два', re.sub(r'едно$', 'един', w))
        return w + nxt
    t = re.sub(r'(?<![\w.])(\d+)(?![\d.,]\d)(\s?\S?)', lambda m: whole(m), t)
    return t

if __name__ == '__main__':
    tests = {'de': 'Am Donnerstag, 5. November. 153 Abgeordnete, zwischen 50 und 2000 Euro, mehr als 170 Taten, 3,5 % im Jahr 2026, 1 Prozent, 1200 Menschen.',
             'bg': 'за четвъртък, 5 ноември. 153 гласа, между 50 и 2000 евро, над 170 престъпления, 3,5 % през 2026 г., 1200 души, 2 милиона, 105, 120, 21 души.',
             'en': 'Thursday, November 5. 153 votes, between 50 and 2000 euros, more than 170 offences, 3.5% in 2026, $5 billion, 1st place.'}
    for l, s in tests.items(): print(l, '→', spell(s, l))
