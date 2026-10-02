"""Fetch daily Cloudflare Web Analytics (RUM) figures for terraworldnews.com.
Writes analytics/YYYY-MM-DD.json per Berlin day (yesterday and any missing day of the last 7)."""
import json, os, sys, urllib.request, datetime as dt
from zoneinfo import ZoneInfo

ACC = '327c4606eee7fb4d356da068f3156aa6'
TOKEN = os.environ.get('CF_ANALYTICS_TOKEN', '')
BER = ZoneInfo('Europe/Berlin')
OUT = 'analytics'

Q = '''query($acc:String!,$f:AccountRumPageloadEventsAdaptiveGroupsFilter_InputObject){
 viewer{accounts(filter:{accountTag:$acc}){
  total:rumPageloadEventsAdaptiveGroups(filter:$f,limit:1){count sum{visits}}
  countries:rumPageloadEventsAdaptiveGroups(filter:$f,limit:50,orderBy:[sum_visits_DESC]){count sum{visits} dimensions{countryName}}
  referers:rumPageloadEventsAdaptiveGroups(filter:$f,limit:50,orderBy:[sum_visits_DESC]){count sum{visits} dimensions{refererHost}}
  paths:rumPageloadEventsAdaptiveGroups(filter:$f,limit:200,orderBy:[count_DESC]){count sum{visits} dimensions{requestPath}}
  devices:rumPageloadEventsAdaptiveGroups(filter:$f,limit:10,orderBy:[count_DESC]){count sum{visits} dimensions{deviceType}}
  hosts:rumPageloadEventsAdaptiveGroups(filter:$f,limit:10,orderBy:[count_DESC]){count sum{visits} dimensions{requestHost}}
  hours:rumPageloadEventsAdaptiveGroups(filter:$f,limit:30,orderBy:[datetimeHour_ASC]){count sum{visits} dimensions{datetimeHour}}
 }}}'''


def gql(variables):
    req = urllib.request.Request('https://api.cloudflare.com/client/v4/graphql',
        data=json.dumps({'query': Q, 'variables': variables}).encode(),
        headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def rows(groups, dim):
    return [{'k': g['dimensions'][dim] or '(direkt)' if dim == 'refererHost' else g['dimensions'][dim],
             'views': g['count'], 'visits': g['sum']['visits']} for g in groups]


def day(d):
    start = dt.datetime.combine(d, dt.time(0), BER).astimezone(dt.timezone.utc)
    end = start + dt.timedelta(days=1)
    f = {'datetime_geq': start.strftime('%Y-%m-%dT%H:%M:%SZ'), 'datetime_lt': end.strftime('%Y-%m-%dT%H:%M:%SZ')}
    res = gql({'acc': ACC, 'f': f})
    if res.get('errors'):
        raise RuntimeError(json.dumps(res['errors'])[:2000])
    a = res['data']['viewer']['accounts'][0]
    tot = a['total'][0] if a['total'] else {'count': 0, 'sum': {'visits': 0}}
    paths = rows(a['paths'], 'requestPath')
    lang = {'bg': 0, 'de': 0, 'en': 0}
    for p in paths:
        l = 'de' if p['k'].startswith('/de/') or p['k'] == '/de' else 'en' if p['k'].startswith('/en/') or p['k'] == '/en' else 'bg'
        lang[l] += p['views']
    hours = []
    for g in a['hours']:
        h = dt.datetime.fromisoformat(g['dimensions']['datetimeHour'].replace('Z', '+00:00')).astimezone(BER)
        hours.append({'k': h.strftime('%H'), 'views': g['count'], 'visits': g['sum']['visits']})
    return {'date': d.isoformat(), 'views': tot['count'], 'visits': tot['sum']['visits'],
            'countries': rows(a['countries'], 'countryName'), 'referers': rows(a['referers'], 'refererHost'),
            'paths': paths, 'devices': rows(a['devices'], 'deviceType'), 'hosts': rows(a['hosts'], 'requestHost'),
            'hours': hours, 'lang_views': lang,
            'fetched': dt.datetime.now(BER).isoformat(timespec='minutes')}


def main():
    if not TOKEN:
        print('CF_ANALYTICS_TOKEN missing'); sys.exit(0)
    os.makedirs(OUT, exist_ok=True)
    today = dt.datetime.now(BER).date()
    force = os.environ.get('FORCE_DAYS')
    days = [today - dt.timedelta(days=i) for i in range(1, 8)]
    errs = []
    for d in days:
        fn = f'{OUT}/{d.isoformat()}.json'
        if os.path.exists(fn) and not force and d != today - dt.timedelta(days=1):
            continue
        try:
            data = day(d)
            json.dump(data, open(fn, 'w'), ensure_ascii=False, indent=1)
            print(d, data['visits'], 'visits', data['views'], 'views')
        except Exception as e:
            errs.append(f'{d}: {e}')
            print('ERROR', d, e)
    ef = f'{OUT}/_error.txt'
    if errs:
        open(ef, 'w').write('\n'.join(errs))
    elif os.path.exists(ef):
        os.remove(ef)


if __name__ == '__main__':
    main()
