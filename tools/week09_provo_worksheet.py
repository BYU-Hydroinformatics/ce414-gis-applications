"""Week 9 printable worksheet for the "What Is the Temperature in Provo?" activity, on one page.

Each student works alone on paper. They look up the current temperature in American Fork, Moab and
Cedar City, find each city's straight-line distance to Provo (scale bar or a map's measure tool), and
estimate Provo four ways: their own method, Thiessen polygons drawn by hand on the map, the average
of the two nearest cities, and IDW with power 2. Last, they look up Provo and say which came closest.

The map is zoomed to the four cities, using the same UGRC state boundary and municipal-boundary
centroids as the slide map (tools/week09_tuesday_figures.py), with a 0-200 km scale bar. American Fork
is close enough to Provo that a rough reading off the scale bar is enough. The answer distances
(19, 259, 311 km) are in the slide's speaker notes, not on the worksheet. The sections are spread down
the page so the gaps between them are room for working, and the footer says how to hand it in.

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
plt.rcParams.update({"font.family": ["Avenir Next", "Segoe UI", "Arial", "DejaVu Sans"], "font.size": 9})
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
    h = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.014
    for k in range(int(total / step)):
        ax.add_patch(plt.Rectangle((x0 + k * step * deg, y0), step * deg, h, fc="black" if k % 2 == 0 else "white",
                                   ec="black", lw=0.7, zorder=8))
    for v in range(0, total + 1, label_every):
        ax.text(x0 + v * deg, y0 - 1.2 * h, f"{v}", ha="center", va="top", fontsize=7.5, zorder=8)
    ax.text(x0 + total * deg + 0.03 * (ax.get_xlim()[1] - ax.get_xlim()[0]), y0 + h / 2, "km",
            va="center", fontsize=7.5, zorder=8)


def city(ax, name, dx, dy, ha):
    lon, lat = cities[name]
    provo = name == "Provo"
    ax.plot(lon, lat, "o", ms=8 if provo else 7, color=ORANGE if provo else BLUE, mec="white", mew=1.2, zorder=6)
    ax.text(lon + dx, lat + dy, name, ha=ha, va="center", fontsize=9, color=ORANGE if provo else NAVY,
            weight="bold" if provo else "normal", zorder=7)


# --- The map, zoomed to the four cities -------------------------------------------------------------
fig = plt.figure(figsize=(3.7, 3.7), dpi=250)
ax = fig.add_axes([0.01, 0.01, 0.98, 0.98])
ax.set_xlim(-113.6, -108.85); ax.set_ylim(36.85, 40.75)
ax.set_aspect(1 / math.cos(math.radians(39.0)), adjustable="datalim")
ax.set_xticks([]); ax.set_yticks([])
for sp in ax.spines.values():
    sp.set_color(GRAY); sp.set_linewidth(0.8)
for feat in st["features"]:
    for ring in feat["geometry"]["rings"]:
        r = np.array(ring)
        ax.fill(r[:, 0], r[:, 1], color="#f6f6f6", ec=GRAY, lw=1.0)
city(ax, "American Fork", -0.3, 0.1, "right")
city(ax, "Provo", -0.3, -0.14, "right")
city(ax, "Moab", 0.0, -0.17, "center")
city(ax, "Cedar City", 0.12, 0.0, "left")
scalebar(ax, -112.1, 37.15, 39.0, 200, 50, 100)
ax.annotate("", xy=(-113.25, 39.35), xytext=(-113.25, 39.0), arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.3))
ax.text(-113.25, 39.42, "N", ha="center", fontsize=10, weight="bold", color=NAVY)

buf = io.BytesIO(); fig.savefig(buf, format="png", facecolor="white"); plt.close(fig)
MAP = base64.b64encode(buf.getvalue()).decode()

# --- The worksheet ----------------------------------------------------------------------------------
blank = '<span class="blank"></span>'
short = '<span class="blank short"></span>'
cities_rows = lambda cols: "".join(f"<tr><td>{c}</td>{'<td></td>' * cols}</tr>" for c in ("American Fork", "Moab", "Cedar City"))
lines = lambda n: '<div class="line"></div>' * n

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: letter; margin: 0.45in 0.5in; }}
html, body {{ height: 100%; }}
body {{ display: flex; flex-direction: column; font-family: "Avenir Next", "Segoe UI", Arial, sans-serif; color: #22262e; font-size: 9.5pt; line-height: 1.3; margin: 0; }}
h1 {{ color: {NAVY}; font-size: 15pt; margin: 0; }}
h2 {{ color: {NAVY}; font-size: 10.5pt; margin: 9pt 0 2pt; }}
h2:first-child {{ margin-top: 0; }}
.head {{ display: flex; justify-content: space-between; align-items: baseline; }}
.sub {{ color: {GRAY}; font-size: 8.5pt; }}
.who {{ display: flex; gap: 20pt; margin: 4pt 0 8pt; }}
.who span {{ flex: 1; border-bottom: 1px solid #555; }}
.top {{ display: grid; grid-template-columns: 3.85in 1fr; gap: 14pt; align-items: start; }}
.map {{ width: 3.85in; display: block; }}
.bottom {{ flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 18pt; margin-top: 4pt; }}
.bottom > div {{ display: flex; flex-direction: column; }}
.work {{ flex: 1; min-height: 0.5in; }}
.foot {{ text-align: center; color: {GRAY}; font-size: 8.5pt; margin-top: 6pt; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 4pt; }}
th, td {{ border: 1px solid #8a94a3; padding: 3pt 5pt; text-align: left; }}
th {{ background: #eef3f9; color: {NAVY}; font-size: 8.5pt; }}
td {{ height: 15pt; }}
.blank {{ display: inline-block; width: 0.9in; border-bottom: 1px solid #555; }}
.short {{ width: 0.5in; }}
.line {{ border-bottom: 1px solid #b5bcc7; height: 17pt; }}
.ans {{ margin-top: 5pt; }}
.ans b {{ color: {NAVY}; }}
.hint {{ color: {GRAY}; font-size: 8pt; margin-top: 3pt; }}
.eq {{ font-family: "Times New Roman", serif; font-size: 11.5pt; text-align: center; margin: 3pt 0 0; }}
strong {{ color: {NAVY}; }}
</style></head><body>

<div class="head"><h1>What Is the Temperature in Provo?</h1>
<span class="sub">CE 414 · Week 9 · in-class worksheet, done on your own</span></div>
<div class="who"><span>Name:</span><span>Date and time:</span></div>

<div class="top">
<img class="map" src="data:image/png;base64,{MAP}">
<div>
<h2>1. Gather the samples</h2>
Look up the <strong>current air temperature</strong> in each city (weather.com or similar). Find each city's
<strong>straight-line distance to Provo</strong> with the scale bar or an online map's
measure tool.
<table><tr><th>City</th><th>Temp (°F)</th><th>Distance to Provo (km)</th></tr>{cities_rows(2)}</table>
<div class="hint">Temperature source: {blank}{blank}</div>

<h2>2. Your own method</h2>
Estimate Provo any way you like from the three temperatures.
<div class="ans"><b>Provo:</b> {short} °F &nbsp; How?</div>
{lines(3)}
</div>
</div>

<div class="bottom">
<div>
<section><h2>3. Thiessen polygons (nearest neighbor)</h2>
On the map, join each pair of known cities, draw the <strong>perpendicular bisector</strong> of each line, and
join the bisectors into three polygons. Provo takes the value of the polygon it falls in.
<div class="ans"><b>Polygon:</b> {blank} &nbsp; <b>Provo:</b> {short} °F</div>
</section><div class="work"></div>

<section><h2>4. Nearest neighbors, n = 2</h2>
Average the temperatures of the <strong>two cities closest</strong> to Provo.
<div class="ans">( {short} + {short} ) ÷ 2 = <b>Provo:</b> {short} °F</div>
</section><div class="work"></div>

<section><h2>6. Check</h2>
<div class="ans"><b>Provo's actual temperature now:</b> {short} °F</div>
Which method came closest, and why?
{lines(4)}
</section>
</div>

<div>
<section><h2>5. Inverse distance weighted (IDW), power 2</h2>
Weight each city by <strong>1 / d²</strong> and take the weighted average of all three.
<div class="eq">Provo = Σ ( w · T ) ⁄ Σ w, &nbsp; w = 1 ⁄ d²</div>
<table><tr><th>City</th><th>w = 1 / d²</th><th>w · T</th></tr>{cities_rows(2)}
<tr><td><b>Sum</b></td><td></td><td></td></tr></table>
<div class="ans"><b>Provo</b> = Σ(w · T) ÷ Σw = {short} °F</div>
<div class="hint">The weights are tiny: keep three significant figures, or use 1 / (d ÷ 10)² instead.
Scaling every weight by the same amount does not change the answer.</div>
</section><div class="work"></div>
</div>
</div>

<div class="foot">Take a picture of this sheet and submit it on Learning Suite for today's in-class activity.</div>

</body></html>"""

OUT.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    page = pathlib.Path(tmp) / "worksheet.html"
    page.write_text(html, encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={OUT}", page.as_uri()], check=True, capture_output=True)
print("wrote", OUT)
