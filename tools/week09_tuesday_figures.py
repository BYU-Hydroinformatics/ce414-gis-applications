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
   field so the comparison is fair, and a 2 x 2 panel for the "which design is best" discussion.

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
from scipy.ndimage import gaussian_filter

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
# Adaptive: a first pass of 24 points scattered at random, then 72 infill points also placed at random but
# weighted by the grade (cubed, so the richest ground dominates), so the dots crowd on and around the hot spots.
rich = gaussian_filter(g, 5) ** 3
rich[:8], rich[-8:], rich[:, :8], rich[:, -8:] = 0, 0, 0, 0
p = (rich / rich.sum()).ravel()
pick = rng.choice(p.size, 72, replace=False, p=p)
designs["adaptive"] = np.vstack([np.c_[rng.uniform(8, NX - 8, 24), rng.uniform(8, NY - 8, 24)],
                                 np.clip(np.c_[pick % NX, pick // NX] + rng.uniform(-3, 3, (72, 2)), 8, [NX - 8, NY - 8])])

fig, ax = plt.subplots(figsize=(4.4, 5.6), dpi=200)
im = gold_axes(ax)
cb = fig.colorbar(im, ax=ax, fraction=0.05, pad=0.03); cb.set_label("Gold grade (grams of gold per tonne of rock)", color=NAVY)
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

# --- 3. Growth chart: sampling and interpolation in one dimension ----------------------------------
# A made-up girl whose curve follows the shape of the CDC (2000) stature-for-age median for girls,
# scaled so she finishes at 5 ft 8 in, measured on each birthday from 1 to 18 and rounded to the
# half inch a pencil mark on a wall supports. Four layers on fixed axes so the deck can stack them:
# the birthday points, the 12-and-a-half question, the linear interpolation, and the monthly line.
shape = [29.5, 34, 37.5, 40, 42.5, 45, 47.5, 50, 52.5, 54.5, 57, 59.5, 62, 63, 63.5, 64, 64, 64.2]
age = np.arange(1, 19)
ht = np.round(np.array(shape) * 68 / shape[-1] * 2) / 2
y0, y1 = ht[11], ht[12]
h125 = y0 + (y1 - y0) * (12.5 - 12) / (13 - 12)


def ftin(v):
    return f"{int(v // 12)}′ {v % 12:g}″"


def growth_axes(size=(7.6, 4.7), dpi=150):
    fig = plt.figure(figsize=size, dpi=dpi)
    ax = fig.add_axes([0.11, 0.14, 0.86, 0.82] if size[0] > 6 else [0.15, 0.16, 0.82, 0.80])
    ax.set_xlim(0, 18.8); ax.set_ylim(24, 72)
    return fig, ax


fig, ax = growth_axes()
ax.set_xticks(range(0, 19, 2)); ax.set_yticks(range(24, 73, 6))
ax.set_yticklabels([ftin(v) for v in range(24, 73, 6)])
ax.set_xlabel("Age (years)", color=NAVY); ax.set_ylabel("Height", color=NAVY)
ax.grid(color="#e3e8ef", lw=0.8); ax.spines[["top", "right"]].set_visible(False)
ax.plot(age, ht, "o", ms=8, color=BLUE, mec="white", mew=1.5, zorder=5)
fig.savefig(IMG / "ip-growth-points.png"); plt.close(fig)

fig, ax = growth_axes(); ax.axis("off")
ax.axvline(12.5, color=ORANGE, lw=2, ls=(0, (5, 3)))
ax.text(12.5, 27, "  12½?", color=ORANGE, fontsize=15, weight="bold", va="bottom")
fig.savefig(IMG / "ip-growth-question.png", transparent=True); plt.close(fig)

fig, ax = growth_axes(); ax.axis("off")
ax.plot([12, 13], [y0, y1], color=ORANGE, lw=3)
ax.plot([12.5], [h125], "o", ms=12, color=ORANGE, mec="white", mew=2, zorder=6)
ax.plot([0, 12.5], [h125, h125], color=ORANGE, lw=1.5, ls=(0, (2, 2)))
ax.text(9.2, h125 + 1.2, "≈ " + ftin(round(h125 * 4) / 4).replace(".25", "¼").replace(".5", "½").replace(".75", "¾"), color=ORANGE, fontsize=15, weight="bold", ha="right")
fig.savefig(IMG / "ip-growth-answer.png", transparent=True); plt.close(fig)

months = np.arange(12, 18 * 12 + 1) / 12
fig, ax = growth_axes(); ax.axis("off")
ax.plot(months, np.interp(months, age, ht), color=NAVY, lw=2, zorder=3)
ax.plot(months, np.interp(months, age, ht), ".", ms=2.5, color=NAVY, zorder=3)
fig.savefig(IMG / "ip-growth-line.png", transparent=True); plt.close(fig)

fig, ax = growth_axes(size=(5.2, 3.6))
ax.set_xticks(range(0, 19, 3)); ax.set_yticks(range(24, 73, 12))
ax.set_yticklabels([ftin(v) for v in range(24, 73, 12)])
ax.set_xlabel("Age (years)", color=NAVY); ax.set_ylabel("Height", color=NAVY)
ax.grid(color="#e3e8ef", lw=0.8); ax.spines[["top", "right"]].set_visible(False)
ax.plot(months, np.interp(months, age, ht), color=NAVY, lw=2)
ax.plot(age, ht, "o", ms=7, color=BLUE, mec="white", mew=1.3, zorder=5)
fig.savefig(IMG / "ip-growth-small.png"); plt.close(fig)
print("heights (in):", dict(zip(age.tolist(), ht.tolist())), "at 12.5:", h125)

# --- 4. The same idea in two dimensions: temperature stations and an interpolated grid -------------
# A made-up afternoon temperature field (deg F) over a 60 x 40 cell grid: warm in the southwest, cool
# toward a high spot in the northeast. 16 stations sample it; IDW (power 2, all stations) fills every
# cell. Two images of the same size: stations alone, then the stations on the interpolated grid.
GX, GY = 60, 40
yy2, xx2 = np.mgrid[0:GY, 0:GX] + 0.5
temp = 74 - 0.22 * xx2 - 0.25 * (GY - yy2) - 16 * np.exp(-((xx2 - 44) ** 2 + (yy2 - 12) ** 2) / 120)
st_rng = np.random.default_rng(1414)
pts = []
while len(pts) < 16:                                 # keep stations at least 7 cells apart so labels do not collide
    q = st_rng.uniform([3, 3], [GX - 6, GY - 3])
    if all(np.hypot(*(q - r)) >= 7 for r in pts): pts.append(q)
sx, sy = np.array(pts).T
sv = np.round(temp[sy.astype(int), sx.astype(int)])
d = np.hypot(xx2[..., None] - sx, yy2[..., None] - sy)
w = 1 / np.maximum(d, 1e-6) ** 2
surf = (w * sv).sum(-1) / w.sum(-1)
TCMAP = plt.get_cmap("RdYlBu_r")


def temp_axes(show_surface):
    fig = plt.figure(figsize=(6.0, 3.55), dpi=150)
    ax = fig.add_axes([0.02, 0.03, 0.80, 0.94])
    cax = fig.add_axes([0.85, 0.10, 0.03, 0.80])
    if show_surface:
        im = ax.imshow(surf, cmap=TCMAP, vmin=40, vmax=72, extent=(0, GX, GY, 0))
    else:
        im = ax.imshow(np.full((GY, GX), np.nan), cmap=TCMAP, vmin=40, vmax=72, extent=(0, GX, GY, 0))
        ax.set_facecolor("#f4f6f9")
    for k in range(0, GX + 1, 4): ax.axvline(k, color="white" if show_surface else "#d5dbe3", lw=0.5)
    for k in range(0, GY + 1, 4): ax.axhline(k, color="white" if show_surface else "#d5dbe3", lw=0.5)
    ax.plot(sx, sy, "o", ms=8, color="black", mec="white", mew=1.4)
    for x_, y_, v_ in zip(sx, sy, sv):
        ax.text(x_ + 1.1, y_ - 0.9, f"{v_:.0f}°", fontsize=10, weight="bold", color=NAVY,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))
    ax.set_xlim(0, GX); ax.set_ylim(GY, 0); ax.set_xticks([]); ax.set_yticks([])
    cb = fig.colorbar(im, cax=cax); cb.set_label("Temperature (°F)", color=NAVY)
    return fig


fig = temp_axes(False); fig.savefig(IMG / "ip-temp-stations.png"); plt.close(fig)
fig = temp_axes(True); fig.savefig(IMG / "ip-temp-surface.png"); plt.close(fig)

# --- 5. Exact or not, in one dimension: a made-up stock "XYZ" priced on the first of ten months --------
# Five layers on fixed axes for the "Does the surface give the points back?" slide: the ten prices, then
# Thiessen (nearest month: a staircase), IDW (power 2, all points: flat little bumps at every price),
# a natural cubic spline, and a 2nd-order trend line with its misses drawn in red.
from scipy.interpolate import CubicSpline
mo = np.arange(1, 11)
price = np.array([42, 46, 44, 50, 55, 52, 57, 63, 58, 61], float)
xf = np.linspace(1, 10, 1801)
d_ = np.abs(xf[:, None] - mo[None, :])
w_ = 1 / np.maximum(d_, 1e-9) ** 2
lines = {"thiessen": price[np.argmin(d_, 1)], "idw": (w_ * price).sum(1) / w_.sum(1),
         "spline": CubicSpline(mo, price, bc_type="natural")(xf), "trend": np.polyval(np.polyfit(mo, price, 2), xf)}
STYLE = {"thiessen": ("#0062b8", "Thiessen (nearest month)"), "idw": ("#e07a1f", "IDW (power 2)"),
         "spline": ("#2e8b57", "Spline"), "trend": ("#7b3fa0", "Trend (2nd order)")}


def stock_axes():
    fig = plt.figure(figsize=(7.0, 4.6), dpi=150)
    ax = fig.add_axes([0.11, 0.13, 0.86, 0.83])
    ax.set_xlim(0.5, 10.5); ax.set_ylim(38, 68)
    return fig, ax


def stock_points(ax):
    ax.plot(mo, price, "o", ms=9, color=NAVY, mec="white", mew=1.6, zorder=10)


fig, ax = stock_axes()
ax.set_xticks(mo); ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"])
ax.set_ylabel("XYZ share price ($)", color=NAVY); ax.set_xlabel("First trading day of the month, 2026", color=NAVY)
ax.grid(color="#e3e8ef", lw=0.8); ax.spines[["top", "right"]].set_visible(False)
stock_points(ax)
fig.savefig(IMG / "ip-stock-points.png"); plt.close(fig)

for k, key in enumerate(["thiessen", "idw", "spline", "trend"]):
    col, lab = STYLE[key]
    fig, ax = stock_axes(); ax.axis("off")
    ax.plot(xf, lines[key], color=col, lw=2.6, zorder=4)
    if key == "trend":
        fit = np.polyval(np.polyfit(mo, price, 2), mo)
        for m_, p_, f_ in zip(mo, price, fit):
            ax.plot([m_, m_], [p_, f_], color="#b3261e", lw=2, zorder=5)
    stock_points(ax)
    ax.text(0.8, 66 - 2.6 * k, "— " + lab, color=col, fontsize=13, weight="bold", va="top")
    fig.savefig(IMG / f"ip-stock-{key}.png", transparent=True); plt.close(fig)
print("trend misses ($):", np.round(price - np.polyval(np.polyfit(mo, price, 2), mo), 2))
