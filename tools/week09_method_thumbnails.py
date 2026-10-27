"""Week 9 "Interpolation: Many Methods" thumbnails: one map per method the session goes on to show.

Crops the framed map panel out of figures tools/week09_elevation_figures.py already wrote, so the
thumbnails are the same surfaces students see a few slides later: the Thiessen polygons, IDW (power 2,
6 nearest points), the 2nd-order trend surface and the thin-plate spline, all from the same 150
Mount Timpanogos samples. Rerun after the elevation figures change.

    python tools/week09_method_thumbnails.py      (any Python with Pillow)

Writes slides/week-09/images/ip-thumb-{thiessen,idw,trend,spline}.png.
"""

import pathlib

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "slides" / "week-09" / "images"

# (source figure, pixel box of its map panel including the black frame)
PANELS = {
    "thiessen": ("ip-tp-thiessen-polygons.png", (16, 16, 834, 834)),
    "idw": ("ip-tp-idw-6-vs-12.png", (15, 131, 688, 804)),
    "trend": ("ip-tp-trend.png", (734, 92, 1408, 766)),
    "spline": ("ip-tp-spline.png", (734, 92, 1408, 766)),
}

for name, (src, box) in PANELS.items():
    im = Image.open(IMG / src).convert("RGB").crop(box)
    im.thumbnail((400, 400), Image.LANCZOS)
    im.save(IMG / f"ip-thumb-{name}.png", optimize=True)
