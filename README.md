# TERRA WORLD NEWS

Static news site for https://terraworldnews.com (publisher FILMPARTNER 24 EOOD).

- `content/YYYY-MM-DD.json` – one file per daily edition (bg + de)
- `build.py` – generator (Python 3 stdlib) → `out/`
- `tools/fetch_images.py` – GitHub Action downloads Wikimedia Commons photos into `static/assets/news/`
- Hosting: Cloudflare Pages, build command `python3 build.py`, output directory `out`
