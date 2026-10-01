"""Notify IndexNow (Bing, Yandex, Seznam, Naver …) about new/changed URLs from the sitemap."""
import json, urllib.request, xml.etree.ElementTree as ET, datetime, sys
KEY = '2049bbf38319833cc271f38180251969'
HOST = 'terraworldnews.com'
ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
root = ET.parse('out/sitemap.xml').getroot()
since = (datetime.date.today() - datetime.timedelta(days=2)).isoformat()
urls = [u.find('s:loc', ns).text for u in root.findall('s:url', ns)
        if (u.find('s:lastmod', ns) is None) or u.find('s:lastmod', ns).text[:10] >= since]
urls = urls[:10000]
if not urls: sys.exit(0)
body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': f'https://{HOST}/{KEY}.txt', 'urlList': urls}).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
try:
    with urllib.request.urlopen(req, timeout=30) as r: print('IndexNow', r.status, len(urls), 'URLs')
except Exception as e: print('IndexNow failed:', e)
