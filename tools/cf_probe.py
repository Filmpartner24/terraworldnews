"""Diagnose: Cloudflare-Sicherheitsereignisse für Googlebot (nur lesen)."""
import json, os, urllib.request, datetime as dt
T = os.environ.get('CF_ANALYTICS_TOKEN', '')
out = {}
def call(url, data=None):
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                                     headers={'Authorization': f'Bearer {T}', 'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
    except urllib.error.HTTPError as e: return {'http': e.code, 'body': e.read().decode()[:500]}
    except Exception as e: return {'err': str(e)}
out['verify'] = call('https://api.cloudflare.com/client/v4/user/tokens/verify')
z = call('https://api.cloudflare.com/client/v4/zones?name=terraworldnews.com')
out['zones'] = z if 'result' not in z else [{'id': x['id'], 'name': x['name'], 'plan': x.get('plan', {}).get('name')} for x in z['result']]
zid = z['result'][0]['id'] if z.get('result') else None
since = (dt.datetime.utcnow() - dt.timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%SZ')
until = dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
if zid:
    q = '''query($z:String!,$s:Time!,$u:Time!){viewer{zones(filter:{zoneTag:$z}){
      fw:firewallEventsAdaptiveGroups(limit:50,filter:{datetime_geq:$s,datetime_lt:$u,userAgent_like:"%Googlebot%"},orderBy:[count_DESC]){count dimensions{action source ruleId description clientCountryName clientRequestPath botScore verifiedBotCategory}}
      st:httpRequestsAdaptiveGroups(limit:50,filter:{datetime_geq:$s,datetime_lt:$u,userAgent_like:"%Googlebot%"},orderBy:[count_DESC]){count dimensions{edgeResponseStatus clientRequestPath}}
    }}}'''
    out['gql'] = call('https://api.cloudflare.com/client/v4/graphql', {'query': q, 'variables': {'z': zid, 's': since, 'u': until}})
    for k in ('bot_management', 'settings/security_level', 'settings/browser_check'):
        out[k] = call(f'https://api.cloudflare.com/client/v4/zones/{zid}/{k}')
os.makedirs('probe', exist_ok=True)
json.dump(out, open('probe/result.json', 'w'), indent=1)
print(json.dumps(out)[:3000])
