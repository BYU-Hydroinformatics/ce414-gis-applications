"""Render slides/week-02/images/mba-globe.gif: an antique-styled desk globe spinning through one
full rotation. Coastlines come from Natural Earth 1:110m land polygons (public domain); the
parchment colors, brass meridian ring and wooden stand are drawn, not photographed. This exists
because no openly licensed animation of a real physical globe could be found on Wikimedia Commons.
Usage: python tools/make_antique_globe_gif.py path/to/ne_110m_land.geojson"""
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

src = sys.argv[1]
TW, TH = 2880, 1440                      # equirectangular texture
land = json.load(open(src, encoding='utf-8'))
tex = Image.new('RGB', (TW, TH), (232, 216, 178))          # parchment ocean
d = ImageDraw.Draw(tex)
def px(lon, lat): return ((lon + 180) / 360 * TW, (90 - lat) / 180 * TH)
for f in land['features']:
    g = f['geometry']; polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    for poly in polys:
        for k, ring in enumerate(poly):
            pts = [px(*c[:2]) for c in ring]
            d.polygon(pts, fill=(196, 160, 104) if k == 0 else (232, 216, 178), outline=(110, 78, 40))
for lon in range(-180, 180, 15):
    x = px(lon, 0)[0]; d.line([(x, 0), (x, TH)], fill=(150, 120, 80), width=2)
for lat in range(-75, 90, 15):
    y = px(0, lat)[1]; d.line([(0, y), (TW, y)], fill=(150, 120, 80), width=3 if lat == 0 else 2)
tex = np.asarray(tex).astype(np.float32)

S = 480; R = 170; cx, cy = S // 2, 205
tilt = math.radians(23.5)
yy, xx = np.mgrid[0:S, 0:S]
X = (xx - cx) / R; Y = -(yy - cy) / R
inside = X**2 + Y**2 <= 1
Z = np.sqrt(np.clip(1 - X**2 - Y**2, 0, 1))
# rotate the view so the axis is tilted toward the viewer's right (like a stand's axis)
Yt = Y * math.cos(tilt) - X * math.sin(tilt)
Xt = X * math.cos(tilt) + Y * math.sin(tilt)
lat = np.arcsin(np.clip(Yt, -1, 1))
shade = (0.55 + 0.45 * Z) * (0.8 + 0.2 * np.clip(Xt * -0.4 + Z, 0, 1))   # limb darkening + soft light

frames = []
N = 36
for i in range(N):
    lon0 = i * 2 * math.pi / N
    lon = np.arctan2(Xt, Z) + lon0
    u = ((lon / (2 * math.pi) + 0.5) % 1.0) * (TW - 1)
    v = ((0.5 - lat / math.pi) % 1.0) * (TH - 1)
    ui = u.astype(int); vi = v.astype(int)
    rgb = tex[vi, ui] * shade[..., None]
    img = np.full((S, S, 3), 255, np.uint8)
    img[inside] = np.clip(rgb[inside], 0, 255).astype(np.uint8)
    im = Image.fromarray(img)
    dr = ImageDraw.Draw(im)
    # stand: base, pillar, and a brass meridian ring
    dr.ellipse([cx - 120, S - 62, cx + 120, S - 18], fill=(92, 58, 30))
    dr.rectangle([cx - 12, cy + R - 4, cx + 12, S - 42], fill=(120, 80, 40))
    dr.ellipse([cx - 22, cy + R - 12, cx + 22, cy + R + 12], fill=(160, 130, 70))
    # meridian ring drawn as a tilted ellipse arc around the sphere edge
    ring = Image.new('RGBA', (S, S), (0, 0, 0, 0)); rd = ImageDraw.Draw(ring)
    rd.ellipse([cx - R - 10, cy - R - 10, cx + R + 10, cy + R + 10], outline=(184, 140, 60, 255), width=9)
    ring = ring.rotate(-math.degrees(tilt) * 0.0, center=(cx, cy))
    im.paste(ring, (0, 0), ring)
    # dark outline on the sphere limb
    dr.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(70, 50, 30), width=2)
    frames.append(im.convert('P', palette=Image.ADAPTIVE, colors=128))
frames[0].save('slides/week-02/images/mba-globe.gif', save_all=True, append_images=frames[1:],
               duration=90, loop=0, optimize=True)
print('gif written', len(frames), 'frames')
