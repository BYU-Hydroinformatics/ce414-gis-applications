"""Week 9 Tuesday figures that need no ArcGIS Pro: the Provo distance hint and the gold-grade
sampling maps.

1. The Utah activity map, redrawn, plus a transparent overlay of the same size with straight-line
   (great-circle) distances from Provo to American Fork, Moab and Cedar City. The deck stacks the
   overlay on the map and reveals it on a click. City locations are the UGRC municipal-boundary
   centroids already recorded in tools/week08_interpolation_numbers.json; the state outline comes
   from UGRC's UtahStateBoundary service.
2. A made-up gold-grade field (g/t) for the "gold nuggets under a landscape" scenario: a few ore
   bodies along a northeast-trending vein, smaller pods, and smooth background noise. It replaces
   the Bolstad contour figures on the sampling-design slides. Each design gets 96 points on the same
   field so the comparison is fair, and a 2 x 2 panel for the class vote.

    python tools/week09_tuesday_figures.py      (any Python with matplotlib, numpy and scipy)

Writes slides/week-09/images/ip-utah-activity-map*.png and ip-gold-*.png.
"""

import json
import math
import pathlib
import urllib.request

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import gaussian_filter, sobel

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "slides" / "week-09" / "images"
plt.rcParams.update({"font.family": ["Segoe UI", "Arial", "DejaVu Sans"], "font.size": 12})
NAVY, BLUE, ORANGE, GRAY = "#002e5d", "#0062b8", "#e07a1f", "#5b6770"

# --- 1. Utah activity map and distance overlay ----------------------------------------------------
STATE = ("https://services1.arcgis.com/99lidPhWCzftIe9K/arcgis/rest/services/UtahStateBoundary/FeatureServer/0/"
         "query?where=STATE%3D%27Utah%27&outSR=4326&f=json&returnGeometry=true&geometryPrecision=4")
st = json.loads(urllib.request.urlopen(STATE, timeout=60).read())
cities = json.loads((ROOT / "tools" / "week08_interpolation_numbers.json").read_text())["cities_lonlat"]


def km(a, b):
    """Great-circle distance, spherical Earth of radius 6371 km."""
    (lo1, la1), (lo2, la2) = [(math.radians(x), math.radians(y)) for x, y in (a, b)]
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def utah_axes():
    # Fixed figure and axes geometry (no tight_layout) so the map and its overlay line up pixel for pixel.
    fig = plt.figure(figsize=(6.2, 7.2), dpi=150)
    ax = fig.add_axes([0.04, 0.02, 0.92, 0.88])
    ax.set_xlim(-114.25, -108.85); ax.set_ylim(36.8, 42.2)
    ax.set_aspect(1 / math.cos(math.radians(39.3)), adjustable="box")
    ax.axis("off")
    return fig, ax


fig, ax = utah_axes()
for feat in st["features"]:
    for ring in feat["geometry"]["rings"]:
        r = np.array(ring)
        ax.fill(r[:, 0], r[:, 1], color="#f2f2f2", ec=GRAY, lw=1.2)
for name, (lon, lat) in cities.items():
    provo = name == "Provo"
    ax.plot(lon, lat, "o", ms=11 if provo else 9, color=ORANGE if provo else BLUE, mec="white", mew=1.5, zorder=5)
    lab = "Provo  ?" if provo else name
    dx = -0.12 if name == "American Fork" else 0.12
    ax.text(lon + dx, lat + (0.06 if name == "American Fork" else 0), lab, ha="right" if dx < 0 else "left",
            va="center", fontsize=12, color=ORANGE if provo else NAVY, weight="bold" if provo else "normal")
fig.text(0.07, 0.95, "Three known temperatures, one unknown", color=NAVY, fontsize=14)
fig.savefig(IMG / "ip-utah-activity-map.png"); plt.close(fig)

fig, ax = utah_axes()
dist = {}
for name in ("American Fork", "Moab", "Cedar City"):
    p, q = cities["Provo"], cities[name]
    d = km(p, q); dist[name] = round(d)
    ax.plot([p[0], q[0]], [p[1], q[1]], color=ORANGE, lw=2.5, ls=(0, (6, 3)), zorder=3)
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    if name == "American Fork":
        mx, my = p[0] + 0.55, p[1] + 0.32          # the line is too short to label in place
        ax.annotate("", xy=((p[0] + q[0]) / 2, (p[1] + q[1]) / 2), xytext=(mx - 0.05, my - 0.05),
                    arrowprops=dict(arrowstyle="-", color=ORANGE, lw=1.2))
    ax.text(mx, my, f"{d:.0f} km", ha="center", va="center", fontsize=13, weight="bold", color=NAVY,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=ORANGE, lw=1.5), zorder=6)
fig.savefig(IMG / "ip-utah-activity-map-distances.png", transparent=True); plt.close(fig)
print("straight-line km from Provo:", dist)

# --- 2. Gold-grade field and four sampling designs ------------------------------------------------
rng = np.random.default_rng(414)
NX, NY = 300, 420                                   # portrait, like the Bolstad panels
yy, xx = np.mgrid[0:NY, 0:NX].astype(float)
g = gaussian_filter(rng.normal(size=(NY, NX)), 22); g = 1.1 * g / g.std()   # broad background variation
# A vein trending northeast across the map, richer in some places along its length than others.
t = (xx - 60) * 0.55 + (NY - yy) * 0.83
s = -(xx - 60) * 0.83 + (NY - yy) * 0.55 - 40
g += 2.2 * np.exp(-(s / 18) ** 2) * (0.5 + 0.5 * np.sin(t / 38))
# Ore pods of different sizes and richness scattered across the map.
for cx, cy, amp, r in [(110, 300, 4.6, 22), (205, 150, 5.0, 18), (240, 55, 3.8, 15), (55, 105, 4.2, 24),
                       (255, 335, 3.6, 18), (150, 225, 3.0, 14), (45, 385, 3.2, 20), (175, 395, 3.4, 12),
                       (110, 35, 2.8, 14), (270, 235, 3.6, 13), (30, 240, 2.6, 18), (190, 290, 2.4, 10)]:
    g += amp * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r ** 2))
h = gaussian_filter(rng.normal(size=(NY, NX)), 5); g += 0.35 * h / h.std()   # small-scale texture
g = np.clip(g - np.percentile(g, 2), 0, None); g = 10 * g / g.max()   # grams of gold per tonne, 0-10
GOLD = LinearSegmentedColormap.from_list("gold", ["#1b1035", "#4a1d5e", "#9c2e45", "#dd6a26", "#f5b51c", "#fff3a6"])


def gold_axes(ax, title=None):
    im = ax.imshow(g, cmap=GOLD, vmin=0, vmax=10, interpolation="bilinear")
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_color(GRAY)
    if title: ax.set_title(title, fontsize=17, color=NAVY, loc="left")
    return im


def dots(ax, pts):
    ax.plot(pts[:, 0], pts[:, 1], "o", ms=6.5, color="black", mec="white", mew=1.2)
    ax.set_xlim(-0.5, NX - 0.5); ax.set_ylim(NY - 0.5, -0.5)


N = 96
gx, gy = np.meshgrid(np.linspace(20, NX - 20, 8), np.linspace(20, NY - 20, 12))
designs = {"systematic": np.c_[gx.ravel(), gy.ravel()],
           "random": np.c_[rng.uniform(8, NX - 8, N), rng.uniform(8, NY - 8, N)]}
centers = np.c_[rng.uniform(30, NX - 30, 12), rng.uniform(30, NY - 30, 12)]
designs["cluster"] = np.vstack([c + rng.normal(0, 9, (8, 2)) for c in centers])
# Adaptive: a coarse first pass on a 4 x 6 grid, then 72 infill points drawn where the grade changes fastest.
grad = np.hypot(sobel(gaussian_filter(g, 6), 0), sobel(gaussian_filter(g, 6), 1))
grad[:8], grad[-8:], grad[:, :8], grad[:, -8:] = 0, 0, 0, 0
p = (grad / grad.sum()).ravel()
pick = rng.choice(p.size, 72, replace=False, p=p)
cx, cy = np.meshgrid(np.linspace(35, NX - 35, 4), np.linspace(35, NY - 35, 6))
designs["adaptive"] = np.vstack([np.c_[cx.ravel(), cy.ravel()],
                                 np.clip(np.c_[pick % NX, pick // NX] + rng.uniform(-3, 3, (72, 2)), 8, [NX - 8, NY - 8])])

fig, ax = plt.subplots(figsize=(4.4, 5.6), dpi=200)
im = gold_axes(ax)
cb = fig.colorbar(im, ax=ax, fraction=0.05, pad=0.03); cb.set_label("Gold grade (g/t)", color=NAVY)
fig.tight_layout(); fig.savefig(IMG / "ip-gold-grade.png"); plt.close(fig)

for name, pts in designs.items():
    fig, ax = plt.subplots(figsize=(3.6, 5.0), dpi=200)
    gold_axes(ax); dots(ax, pts)
    fig.tight_layout(pad=0.3); fig.savefig(IMG / f"ip-gold-{name}.png"); plt.close(fig)

fig, axs = plt.subplots(2, 2, figsize=(7.2, 10.0), dpi=170)
for ax, (name, pts) in zip(axs.ravel(), designs.items()):
    gold_axes(ax, name.capitalize()); dots(ax, pts)
fig.tight_layout(h_pad=1.2, w_pad=1.5); fig.savefig(IMG / "ip-gold-compare.png"); plt.close(fig)
print({k: len(v) for k, v in designs.items()})
