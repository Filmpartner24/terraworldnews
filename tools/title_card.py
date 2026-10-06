#!/usr/bin/env python3
"""Eigene Titelgrafik (1200x675, WebP) für Artikel ohne freies Foto – ersetzt Video-Standbilder/Cover (rechtlich sicher).
Aufruf als Modul: make(path, kicker, title, color) oder CLI: python3 tools/title_card.py out.webp "GAMES" "Titel" "#7b2cbf"."""
import sys, textwrap
from PIL import Image, ImageDraw, ImageFont
BOLD = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
def _font(sz):
    try: return ImageFont.truetype(BOLD, sz)
    except Exception: return ImageFont.load_default()
def make(path, kicker, title, color='#e85d04'):
    W, H = 1200, 675
    im = Image.new('RGB', (W, H)); dr = ImageDraw.Draw(im)
    for y in range(H):
        f = y / H; dr.line([(0, y), (W, y)], fill=(int(12 + f * 16), int(18 + f * 18), int(40 + f * 14)))
    col = color if color.startswith('#') and len(color) == 7 else '#e85d04'
    rgb = tuple(int(col[i:i + 2], 16) for i in (1, 3, 5))
    dr.rectangle([0, H - 14, W, H], fill=rgb); dr.rectangle([70, 92, 78, 150], fill=rgb)
    dr.text((98, 92), kicker.upper(), font=_font(40), fill=rgb)
    size = 62
    for size in (62, 56, 50, 44, 40):
        lines = textwrap.wrap(title, width=int(1040 / (size * 0.52)))
        if len(lines) <= 5: break
    y = 200
    for ln in lines[:5]:
        dr.text((70, y), ln, font=_font(size), fill=(255, 255, 255)); y += int(size * 1.25)
    dr.text((70, H - 70), 'TERRA WORLD NEWS', font=_font(26), fill=(170, 180, 200))
    im.save(path, 'WEBP', quality=88)
if __name__ == '__main__':
    make(*sys.argv[1:5])
