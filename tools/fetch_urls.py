#!/usr/bin/env python3
"""Generic download bridge: bridge/requests.txt (one URL per line) -> bridge/files/<name>.
Used to bring files from sites the editing container cannot reach. Working area only."""
import os, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
req = os.path.join(HERE, 'bridge', 'requests.txt')
if os.path.exists(req):
    out = os.path.join(HERE, 'bridge', 'files'); os.makedirs(out, exist_ok=True)
    for line in [l.strip() for l in open(req) if l.strip() and not l.startswith('#')]:
        u, _, name = line.partition(' ')  # optional: "URL dateiname"
        name = name.strip() or urllib.parse.unquote(u.split('?')[0].rstrip('/').split('/')[-1]) or 'index.html'
        dest = os.path.join(out, name)
        if os.path.exists(dest): continue
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (bridge)'}), timeout=60)
            open(dest, 'wb').write(r.read()); print('ok', name)
        except Exception as e: print('fail', u, e)
