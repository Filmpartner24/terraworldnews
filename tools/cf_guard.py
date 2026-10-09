"""Tägliche Google-Wache (nur lesen): blockiert Cloudflare Suchmaschinen (Google, Bing, Apple, DuckDuckGo)?
Schreibt guard/latest.json. Problem -> "ok": false (die Morgenkontrolle meldet es per Push)."""
import json, os, urllib.request, urllib.error, datetime as dt
import re
T = os.environ.get('CF_ZONE_TOKEN', '').strip()
m = re.search(r'[A-Za-z0-9_-]{30,}', T.split('Bearer')[-1]) if T else None
T = m.group(0) if m else T
H = {'Authorization': f'Bearer {T}', 'Content-Type': 'application/json'}
def call(url, data=None):
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode() if data is not None else None, headers=H)
        with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
    except urllib.error.HTTPError as e: return {'http': e.code, 'body': e.read().decode()[:400]}
    except Exception as e: return {'err': type(e).__name__}
out = {'checked': dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ'), 'ok': True, 'problems': []}
if not T:
    out.update(ok=False, problems=['Kein CF_ZONE_TOKEN hinterlegt'])
else:
    z = call('https://api.cloudflare.com/client/v4/zones?name=terraworldnews.com')
    if not z.get('result'):
        out.update(ok=False, problems=['Zone nicht lesbar (Schlüssel ungültig oder ohne Rechte)'])
    else:
        zid = z['result'][0]['id']; out['zone'] = zid
        now = dt.datetime.utcnow(); since = (now - dt.timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ'); until = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        variants = [
          ('fwa', 'firewallEventsAdaptive(limit:200,filter:{datetime_geq:$s,datetime_lt:$u},orderBy:[datetime_DESC]){action source ruleId description clientAsn clientRequestPath userAgent datetime}'),
          ('fwag', 'firewallEventsAdaptiveGroups(limit:50,filter:{datetime_geq:$s,datetime_lt:$u},orderBy:[count_DESC]){count dimensions{action source description clientAsn clientRequestPath userAgent}}'),
        ]
        rows = []; out['graphql_errors'] = {}
        for name, body in variants:
            q = 'query($z:String!,$s:Time!,$u:Time!){viewer{zones(filter:{zoneTag:$z}){ev:' + body + '}}}'
            g = call('https://api.cloudflare.com/client/v4/graphql', {'query': q, 'variables': {'z': zid, 's': since, 'u': until}})
            if g.get('errors'): out['graphql_errors'][name] = (g['errors'][0].get('message') or '')[:160]; continue
            ev = (((g.get('data') or {}).get('viewer') or {}).get('zones') or [{}])[0].get('ev') or []
            rows = [{'count': r.get('count', 1), 'dimensions': r.get('dimensions', r)} for r in ev]
            out['source'] = name; break
        bots = ('googlebot', 'bingbot', 'applebot', 'duckduck', 'google-inspectiontool', 'adsbot-google', 'storebot-google')
        bad = [r for r in rows if r['dimensions']['action'] in ('block', 'managed_challenge', 'challenge', 'jschallenge')
               and any(b in (r['dimensions'].get('userAgent') or '').lower() for b in bots)]
        out['blocked_search_bots_24h'] = sum(r['count'] for r in bad)
        out['blocked_detail'] = [{k: r['dimensions'][k] for k in ('action', 'source', 'description', 'clientRequestPath', 'clientAsn')} | {'count': r['count']} for r in bad[:10]]
        if bad: out['ok'] = False; out['problems'].append(f"{out['blocked_search_bots_24h']} Suchmaschinen-Anfragen in 24 h blockiert (Regel: {bad[0]['dimensions'].get('description') or bad[0]['dimensions'].get('source')})")
        if 'source' not in out: out['problems'].append('Sicherheitsereignisse nicht lesbar (Berechtigung)'); out['ok'] = False
        for k in ('settings/browser_check', 'settings/security_level'):
            r = call(f'https://api.cloudflare.com/client/v4/zones/{zid}/{k}'); out[k] = r.get('result', r)
        bc = out.get('settings/browser_check') or {}
        if isinstance(bc, dict) and bc.get('value') == 'on': out['problems'].append('Hinweis: Browser Integrity Check ist an')
os.makedirs('guard', exist_ok=True)
json.dump(out, open('guard/latest.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(out, ensure_ascii=False)[:2500])
