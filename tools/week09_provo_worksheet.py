"""Week 9 printable worksheet for the "What Is the Temperature in Provo?" activity.

Each student works alone on paper. They look up the current temperature in American Fork, Moab and
Cedar City, find each city's straight-line distance to Provo (scale bar or a map's measure tool), and
estimate Provo four ways: their own method, Thiessen polygons drawn by hand on the map, the average
of the two nearest cities, and IDW with power 2. Last, they look up Provo and say which came closest.

The map uses the same UGRC state boundary and municipal-boundary centroids as the slide map
(tools/week09_tuesday_figures.py), with a 0-200 km scale bar and an inset of American Fork and Provo,
which are too close together to measure at state scale. The answer distances (19, 259, 311 km) are
in the slide's speaker notes, not on the worksheet.

    python tools/week09_provo_worksheet.py      (matplotlib, numpy; Google Chrome for the PDF)

Writes docs/handouts/provo-temperature-worksheet.pdf.
"""

import base64
import io
import json
import math
import pathlib
import subprocess
import tempfile
import urllib.request

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "handouts" / "provo-temperature-worksheet.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
plt.rcParams.update({"font.family": ["Avenir Next", "Segoe UI", "Arial", "DejaVu Sans"], "font.size": 11})
NAVY, BLUE, ORANGE, GRAY = "#002e5d", "#0062b8", "#e07a1f", "#5b6770"

STATE = ("https://services1.arcgis.com/99lidPhWCzftIe9K/arcgis/rest/services/UtahStateBoundary/FeatureServer/0/"
         "query?where=STATE%3D%27Utah%27&outSR=4326&f=json&returnGeometry=true&geometryPrecision=4")
st = json.loads(urllib.request.urlopen(STATE, timeout=60).read())
cities = json.loads((ROOT / "tools" / "week08_interpolation_numbers.json").read_text())["cities_lonlat"]


def km_per_deg_lon(lat):
    return 2 * math.pi * 6371 / 360 * math.cos(math.radians(lat))


def scalebar(ax, x0, y0, lat, total, step, label_every):
    """A black-and-white checkered scale bar, total km long, in an axes whose x unit is degrees of longitude."""
    deg = 1 / km_per_deg_lon(lat)
    h = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.012
    for k in range(int(total / step)):
        ax.add_patch(plt.Rectangle((x0 + k * step * deg, y0), step * deg, h, fc="black" if k % 2 == 0 else "white",
                                   ec="black", lw=0.8, zorder=8))
    for v in range(0, total + 1, label_every):
        ax.text(x0 + v * deg, y0 - 1.2 * h, f"{v}", ha="center", va="top", fontsize=9, zorder=8)
    ax.text(x0 + total * deg + 0.04 * (ax.get_xlim()[1] - ax.get_xlim()[0]), y0 + h / 2, "km",
            va="center", fontsize=9, zorder=8)


def city(ax, name, size=9, label=True, offsets=None):
    lon, lat = cities[name]
    provo = name == "Provo"
    ax.plot(lon, lat, "o", ms=size + 2 if provo else size, color=ORANGE if provo else BLUE, mec="white", mew=1.4, zorder=6)
    if label:
        dx, dy, ha = (offsets or {}).get(name, (0.12, 0, "left"))
        ax.text(lon + dx, lat + dy, name, ha=ha, va="center", fontsize=11, color=ORANGE if provo else NAVY,
                weight="bold" if provo else "normal", zorder=7)


# --- The map ----------------------------------------------------------------------------------------
fig = plt.figure(figsize=(7.0, 7.2), dpi=220)
ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
ax.set_xlim(-114.25, -108.75); ax.set_ylim(36.75, 42.15)
ax.set_aspect(1 / math.cos(math.radians(39.3)), adjustable="box"); ax.axis("off")
for feat in st["features"]:
    for ring in feat["geometry"]["rings"]:
        r = np.array(ring)
        ax.fill(r[:, 0], r[:, 1], color="#f6f6f6", ec=GRAY, lw=1.2)
offsets = {"American Fork": (-0.3, 0.1, "right"), "Provo": (0.3, -0.12, "left")}
for name in cities:
    city(ax, name, offsets=offsets)
scalebar(ax, -113.9, 37.0, 39.3, 200, 50, 50)
ax.text(-109.0, 41.95, "N", ha="center", fontsize=13, weight="bold", color=NAVY)
ax.annotate("", xy=(-109.0, 41.9), xytext=(-109.0, 41.55), arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.6))

# Inset of American Fork and Provo, in the empty corner northeast of the state.
box = (-111.95, -111.5, 40.17, 40.45)
ax.add_patch(plt.Rectangle((box[0], box[2]), box[1] - box[0], box[3] - box[2], fill=False, ec=NAVY, lw=1, zorder=7))
ins = fig.add_axes([0.66, 0.66, 0.30, 0.26])
ins.set_xlim(box[0], box[1]); ins.set_ylim(box[2], box[3])
ins.set_aspect(1 / math.cos(math.radians(40.3)), adjustable="box")
ins.set_xticks([]); ins.set_yticks([]); ins.set_facecolor("#ffffff")
for sp in ins.spines.values():
    sp.set_color(NAVY)
city(ins, "American Fork", offsets={"American Fork": (0.02, 0.025, "left")})
city(ins, "Provo", offsets={"Provo": (0.02, -0.02, "left")})
scalebar(ins, box[0] + 0.03, box[2] + 0.03, 40.3, 20, 5, 10)
ins.set_title("Zoomed in", fontsize=10, color=NAVY, loc="left")
ax.annotate("", xy=(-111.48, 40.45), xytext=(-110.55, 41.1), arrowprops=dict(arrowstyle="-", color=NAVY, lw=0.8))

buf = io.BytesIO(); fig.savefig(buf, format="png", facecolor="white"); plt.close(fig)
MAP = base64.b64encode(buf.getvalue()).decode()

# --- The worksheet ----------------------------------------------------------------------------------
blank = '<span class="blank"></span>'
short = '<span class="blank short"></span>'
rows = "".join(f"<tr><td>{c}</td><td></td><td></td></tr>" for c in ("American Fork", "Moab", "Cedar City"))
idw_rows = "".join(f"<tr><td>{c}</td><td></td><td></td><td></td><td></td></tr>" for c in ("American Fork", "Moab", "Cedar City"))
lines = lambda n: '<div class="line"></div>' * n

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: letter; margin: 0.55in 0.65in; }}
body {{ font-family: "Avenir Next", "Segoe UI", Arial, sans-serif; color: #22262e; font-size: 10.5pt; line-height: 1.35; margin: 0; }}
h1 {{ color: {NAVY}; font-size: 17pt; margin: 0 0 2pt; }}
h2 {{ color: {NAVY}; font-size: 12pt; margin: 12pt 0 3pt; }}
.sub {{ color: {GRAY}; font-size: 9.5pt; margin-bottom: 6pt; }}
.who {{ display: flex; gap: 24pt; margin: 6pt 0 4pt; }}
.who span {{ flex: 1; border-bottom: 1px solid #555; padding-bottom: 1pt; }}
.map {{ display: block; width: 5.3in; margin: 2pt auto 0; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 4pt; }}
th, td {{ border: 1px solid #8a94a3; padding: 5pt 6pt; text-align: left; }}
th {{ background: #eef3f9; color: {NAVY}; font-size: 9.5pt; }}
td {{ height: 16pt; }}
td:first-child {{ width: 26%; }}
.blank {{ display: inline-block; width: 1in; border-bottom: 1px solid #555; }}
.short {{ width: 0.6in; }}
.line {{ border-bottom: 1px solid #b5bcc7; height: 20pt; }}
.ans {{ margin-top: 6pt; }}
.ans b {{ color: {NAVY}; }}
.hint {{ color: {GRAY}; font-size: 9pt; }}
.eq {{ font-family: "Times New Roman", serif; font-size: 13pt; text-align: center; margin: 4pt 0; }}
.page2 {{ break-before: page; }}
strong {{ color: {NAVY}; }}
</style></head><body>

<h1>What Is the Temperature in Provo?</h1>
<div class="sub">CE 414 · Week 9 · Sampling and Interpolation · in-class worksheet, done on your own</div>
<div class="who"><span>Name:</span><span>Date and time:</span></div>

<img class="map" src="data:image/png;base64,{MAP}">

<h2>1. Gather the samples</h2>
Look up the <strong>current air temperature</strong> in each city (weather.com or similar). Then find each city's
<strong>straight-line distance to Provo</strong>: measure it on the map with the scale bar (use the zoomed-in box
for American Fork), or use the measure tool in an online map.
<table><tr><th>City</th><th>Temperature (°F)</th><th>Straight-line distance to Provo (km)</th></tr>{rows}</table>
<div class="hint">Source of the temperatures: {blank}{blank}</div>

<div class="page2">

<h2>2. Your own method</h2>
Using only the three temperatures above, estimate Provo's temperature any way you like.
<div class="ans"><b>Provo estimate:</b> {blank} °F</div>
How did you get it?
{lines(3)}

<h2>3. Thiessen polygons (nearest neighbor)</h2>
On the map, draw a line joining each pair of known cities, then the <strong>perpendicular bisector</strong> of each
line. Join the bisectors into three polygons. Provo takes the value of the polygon it falls in.
<div class="ans"><b>Provo falls in the polygon of:</b> {blank}{blank} &nbsp; <b>Provo estimate:</b> {blank} °F</div>

<h2>4. Nearest neighbors, n = 2</h2>
Average the temperatures of the <strong>two cities closest</strong> to Provo.
<div class="ans"><b>Two closest:</b> {blank}{short} &nbsp; ( {short} + {short} ) ÷ 2 = <b>Provo:</b> {short} °F</div>

<h2>5. Inverse distance weighted (IDW), power 2</h2>
Weight each city by <strong>1 / d²</strong>, so closer cities count more, and take the weighted average of all three.
<div class="eq">Provo = Σ ( w · T ) ⁄ Σ w, &nbsp;&nbsp; w = 1 ⁄ d²</div>
<table><tr><th>City</th><th>T (°F)</th><th>d (km)</th><th>w = 1 / d²</th><th>w · T</th></tr>{idw_rows}
<tr><td><b>Sum</b></td><td style="background:#f2f2f2"></td><td style="background:#f2f2f2"></td><td></td><td></td></tr></table>
<div class="ans"><b>Provo estimate</b> = Σ(w · T) ÷ Σw = {blank} °F</div>
<div class="hint">Tip: the weights are tiny numbers. Keep at least three significant figures, or work in
1 / (d ÷ 10)² instead: scaling every weight by the same amount does not change the answer.</div>

<h2>6. Check</h2>
<div class="ans"><b>Provo's actual temperature right now:</b> {blank} °F</div>
Which method came closest, and why do you think it did? Which would you trust if Provo had no thermometer?
{lines(3)}

</div></body></html>"""

OUT.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    page = pathlib.Path(tmp) / "worksheet.html"
    page.write_text(html, encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={OUT}", page.as_uri()], check=True, capture_output=True)
print("wrote", OUT)
