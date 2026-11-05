#!/usr/bin/env python3
"""TWN Radio – „TWN in 90 Sekunden“: Morgenausgabe mit Nedys ElevenLabs-Stimme (DE/BG/EN).

Läuft in der GitHub Action (.github/workflows/audio.yml), Schlüssel aus dem Secret ELEVENLABS_API_KEY.
Sprechtext = Aufmacher + Top-Meldungen aus content/<Datum>.json (bereits geprüfte Texte: Titel + Kurztext),
keine neuen Fakten. Ergebnis:
  static/audio/news/<Datum>-<lang>.mp3  (Mono, 64 kbps; nur die letzten 7 Tage bleiben liegen)
  content/audio/news.json               (Liste für den Player)

  python3 tools/audio_bulletin.py                 # heutige Ausgabe (Europe/Berlin), fehlende Sprachen erzeugen
  python3 tools/audio_bulletin.py --probe          # Probe nach audio/probe/ (nicht veröffentlicht)
  python3 tools/audio_bulletin.py --dry            # nur Sprechtexte ausgeben, keine Credits
"""
import argparse, datetime as dt, glob, json, os, sys, urllib.request, urllib.error
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BERLIN = ZoneInfo('Europe/Berlin')
VOICE = os.environ.get('TWN_VOICE_ID', 'TCAJda6jOtzTY3hdxbdK')          # Nedy John Cross (ElevenLabs)
MODEL = os.environ.get('TWN_TTS_MODEL', 'eleven_flash_v2_5')            # Flash = halbe Credits; Alternative eleven_multilingual_v2
LANGS = ['de', 'bg', 'en']
N_ITEMS = 4            # Aufmacher + 3 weitere Meldungen
MAX_CHARS = 1900       # Kostenbremse pro Ausgabe
KEEP_DAYS = 7
SEC_ORDER = ['bulgarien', 'welt', 'europa', 'deutschland', 'wirtschaft', 'ki', 'klima', 'energie']

WD = {'de': ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'],
      'bg': ['понеделник', 'вторник', 'сряда', 'четвъртък', 'петък', 'събота', 'неделя'],
      'en': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
MO = {'de': ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'],
      'bg': ['януари', 'февруари', 'март', 'април', 'май', 'юни', 'юли', 'август', 'септември', 'октомври', 'ноември', 'декември'],
      'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']}

def intro(l, d):
    w, m = WD[l][d.weekday()], MO[l][d.month - 1]
    return {'de': f'Guten Morgen. Hier ist TERRA WORLD NEWS mit den Nachrichten am {w}, {d.day}. {m}.',
            'bg': f'Добро утро. Това е TERRA WORLD NEWS с новините за {w}, {d.day} {m}.',
            'en': f'Good morning. This is TERRA WORLD NEWS with the news for {w}, {m} {d.day}.'}[l]

OUTRO = {'de': 'Das waren die Nachrichten. Mehr lesen Sie auf terraworldnews.com. Terra World News – die Fakten, der Kontext, die Welt.',
         'bg': 'Това бяха новините. Още можете да прочетете на terraworldnews.com. Terra World News – фактите, контекстът, светът.',
         'en': 'That was the news. Read more at terraworldnews.com. Terra World News – the facts, the context, the world.'}
TITLE = {'de': 'TWN in 90 Sekunden', 'bg': 'TWN за 90 секунди', 'en': 'TWN in 90 seconds'}

def pick(date):
    fp = os.path.join(HERE, 'content', f'{date}.json')
    items = json.load(open(fp, encoding='utf-8'))['items']
    lead = next((i for i in items if i.get('lead')), items[0])
    out, used = [lead], {lead.get('s')}
    for s in SEC_ORDER:
        if len(out) >= N_ITEMS: break
        it = next((i for i in items if i.get('s') == s and i is not lead), None)
        if it and s not in used:
            out.append(it); used.add(s)
    return out

def dot(t):
    t = t.strip()
    return t if t[-1:] in '.!?…' else t + '.'

def script(items, l, d):
    parts = [intro(l, d)]
    for it in items:
        x = it.get(l) or {}
        if x.get('t') and x.get('d'):
            parts.append(dot(x['t']) + ' ' + dot(x['d']))
    parts.append(OUTRO[l])
    txt = '\n\n'.join(parts)
    while len(txt) > MAX_CHARS and len(parts) > 3:       # notfalls letzte Meldung weglassen
        parts.pop(-2); txt = '\n\n'.join(parts)
    return txt

def tts(text, l, dest):
    key = os.environ.get('ELEVENLABS_API_KEY')
    if not key: raise SystemExit('ELEVENLABS_API_KEY fehlt (GitHub-Secret)')
    body = {'text': text, 'model_id': MODEL, 'language_code': l,
            'voice_settings': {'stability': 0.55, 'similarity_boost': 0.8, 'style': 0.0, 'use_speaker_boost': True}}
    req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_64',
                                 data=json.dumps(body).encode(), method='POST',
                                 headers={'xi-api-key': key, 'Content-Type': 'application/json', 'Accept': 'audio/mpeg'})
    try:
        with urllib.request.urlopen(req, timeout=180) as r: data = r.read()
    except urllib.error.HTTPError as e:
        raise SystemExit(f'ElevenLabs-Fehler {e.code}: {e.read()[:400].decode("utf-8", "replace")}')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, 'wb').write(data)
    return len(data)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date'); ap.add_argument('--probe', action='store_true'); ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    now = dt.datetime.now(BERLIN)
    date = a.date or now.date().isoformat()
    d = dt.date.fromisoformat(date)
    if not os.path.exists(os.path.join(HERE, 'content', f'{date}.json')):
        sys.exit(f'Keine Tagesausgabe content/{date}.json – keine Audio-Ausgabe.')
    items = pick(date)
    if a.dry:
        for l in LANGS: t = script(items, l, d); print(f'--- {l} ({len(t)} Zeichen)\n{t}\n')
        return
    if a.probe:
        for l in LANGS:
            t = script(items, l, d)
            n = tts(t, l, os.path.join(HERE, 'audio', 'probe', f'{date}-{l}.mp3'))
            open(os.path.join(HERE, 'audio', 'probe', f'{date}-{l}.txt'), 'w', encoding='utf-8').write(t)
            print(l, len(t), 'Zeichen →', n, 'Bytes')
        return
    idx_fp = os.path.join(HERE, 'content', 'audio', 'news.json')
    try: idx = json.load(open(idx_fp, encoding='utf-8'))
    except (FileNotFoundError, ValueError): idx = {'items': []}
    have = {(x['date'], x['lang']) for x in idx['items']}
    for l in LANGS:
        rel = f'/audio/news/{date}-{l}.mp3'
        if (date, l) in have and os.path.exists(os.path.join(HERE, 'static' + rel)): continue
        t = script(items, l, d)
        n = tts(t, l, os.path.join(HERE, 'static' + rel))
        idx['items'] = [x for x in idx['items'] if not (x['date'] == date and x['lang'] == l)]
        idx['items'].append({'date': date, 'lang': l, 'f': rel, 'bytes': n, 'chars': len(t), 'time': now.strftime('%H:%M'),
                             'title': TITLE[l], 'ids': [i['id'] for i in items], 'voice': 'Nedy John Cross (ElevenLabs)', 'model': MODEL})
        print(l, len(t), 'Zeichen →', rel)
    cut = (d - dt.timedelta(days=KEEP_DAYS - 1)).isoformat()
    idx['items'] = sorted([x for x in idx['items'] if x['date'] >= cut], key=lambda x: (x['date'], x['lang']), reverse=True)
    for f in glob.glob(os.path.join(HERE, 'static', 'audio', 'news', '*.mp3')):
        if os.path.basename(f)[:10] < cut: os.remove(f)
    os.makedirs(os.path.dirname(idx_fp), exist_ok=True)
    json.dump(idx, open(idx_fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
