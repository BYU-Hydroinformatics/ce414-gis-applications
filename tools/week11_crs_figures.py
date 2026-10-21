r"""Figures and numbers for the Week 11 Tuesday deck (slides/week-11/coordinate-systems-projections.md).

Every distortion figure is computed, not drawn by hand: pyproj's get_factors() gives the scale factor of
a projection at a point, and the maps color that scale error. Outlines are Natural Earth (public domain),
1:50m states and 1:110m land, read from the GeoJSON files in the directory given as the first argument
(download ne_50m_admin_1_states_provinces_lakes.geojson and ne_110m_land.geojson from
github.com/nvkelso/natural-earth-vector/tree/master/geojson).

  1. crs-scale-error-conus.png: a secant oblique stereographic projection (an azimuthal, planar surface)
     centered on the geographic center of the conterminous US near Lebanon, Kansas (39.83 N, 98.58 W),
     with k0 = 0.99, so scale is 1 % short at the center and true on a circle around it. Six cities are
     marked for the "which pair has the same scale error" question.
  2. crs-tennessee-utm16.png and crs-tennessee-spcs.png: scale error across Tennessee in NAD 1983 UTM
     Zone 16N (EPSG 26916) and in NAD 1983 State Plane Tennessee (EPSG 32136, Lambert Conformal Conic,
     standard parallels 35.25 and 36.4167 N), on one color scale.
  3. crs-utm-zones-world.png: the 60 UTM zones over the world's land, Zone 12 highlighted.
  4. The BYU to University of Utah distance in degrees, in UTM 12N meters, and on the ellipsoid.

Writes slides/week-11/images/crs-*.png and tools/week11_crs_numbers.json. Run with a Python that has
pyproj, numpy and matplotlib (not the ArcGIS Pro environment, which lacks pyproj).
"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.colors import TwoSlopeNorm
from pyproj import Proj, Transformer, Geod

NE = sys.argv[1] if len(sys.argv) > 1 else "."
REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(REPO, "slides", "week-11", "images")
NAVY, BLUE, GRAY = "#002E5D", "#0062b8", "#6b7280"
plt.rcParams.update({"font.size": 13, "font.family": "DejaVu Sans"})
NUM = {}


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=150, bbox_inches="tight", pad_inches=0.08, facecolor="white")
    plt.close(fig)


def rings(geom):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in polys:
        for ring in poly:
            yield np.asarray(ring)


def load(name):
    with open(os.path.join(NE, name), encoding="utf-8") as f:
        return json.load(f)["features"]


states = [f for f in load("ne_50m_admin_1_states_provinces_lakes.geojson")
          if f["properties"].get("adm0_a3") in ("USA", "CAN", "MEX")]
lower48 = [f for f in states if f["properties"]["adm0_a3"] == "USA"
           and f["properties"]["name"] not in ("Alaska", "Hawaii")]
land = load("ne_110m_land.geojson")


def draw(ax, feats, proj, **kw):
    for f in feats:
        for r in rings(f["geometry"]):
            x, y = proj(r[:, 0], r[:, 1])
            ax.plot(x, y, **kw)


def scale_error_pct(p, lon, lat):
    return (np.asarray(p.get_factors(lon, lat).meridional_scale) - 1.0) * 100.0


# ---------------------------------------------------------------- 1. CONUS azimuthal
center = (39.83, -98.58)
p = Proj(proj="sterea", lat_0=center[0], lon_0=center[1], k_0=0.99, ellps="GRS80")
x = np.linspace(-2.6e6, 2.6e6, 400); y = np.linspace(-1.75e6, 1.65e6, 280)
X, Y = np.meshgrid(x, y)
lon, lat = p(X, Y, inverse=True)
E = scale_error_pct(p, lon, lat)
cities = {"Salt Lake City": (-111.89, 40.76), "Louisville": (-85.76, 38.25),
          "Miami": (-80.19, 25.76), "Spokane": (-117.43, 47.66),
          "Amarillo": (-101.83, 35.22), "Brownsville": (-97.50, 25.90)}
NUM["conus_center"] = center
NUM["conus_scale_error_pct"] = {k: round(float(scale_error_pct(p, *v)), 2) for k, v in cities.items()}

fig, ax = plt.subplots(figsize=(12, 7.6))
cf = ax.contourf(X, Y, E, levels=np.arange(-1.0, 3.01, 0.25), cmap="RdBu_r",
                 norm=TwoSlopeNorm(0, -1.2, 3.0), alpha=0.75)
cs = ax.contour(X, Y, E, levels=[-0.5, 0, 1, 2], colors=[GRAY, "black", GRAY, GRAY],
                linewidths=[1.2, 2.4, 1.2, 1.2], linestyles=["--", "-", "--", "--"])
ax.clabel(cs, fmt={-0.5: "−0.5 %", 0: "true scale", 1: "+1 %", 2: "+2 %"}, fontsize=12, inline=True)
draw(ax, lower48, p, color="#333", lw=0.6)
cx, cy = p(center[1], center[0])
ax.plot(cx, cy, "k+", ms=14, mew=2)
ax.annotate("center: −1 %", (cx, cy), (cx + 1.6e5, cy - 2.6e5), fontsize=12,
            arrowprops=dict(arrowstyle="-", color="k"))
for name, (lo, la) in cities.items():
    px, py = p(lo, la)
    ax.plot(px, py, "o", ms=8, mfc=NAVY, mec="white", mew=1.5)
    ax.annotate(name, (px, py), (8, 6), textcoords="offset points", fontsize=12, fontweight="bold",
                color=NAVY, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.8))
ax.set_xlim(x[0], x[-1]); ax.set_ylim(y[0], y[-1]); ax.set_aspect("equal"); ax.axis("off")
cb = fig.colorbar(cf, ax=ax, shrink=0.7, pad=0.01)
cb.set_label("scale error (%)")
ax.set_title("Secant oblique stereographic, centered on Lebanon, Kansas (k₀ = 0.99)", fontsize=14)
save(fig, "crs-scale-error-conus.png")

# The "ask" version: the same map and cities with no distortion shown.
fig, ax = plt.subplots(figsize=(12, 7.6))
draw(ax, lower48, p, color="#333", lw=0.6)
ax.plot(cx, cy, "k+", ms=14, mew=2)
ax.annotate("center of the projection", (cx, cy), (cx + 1.6e5, cy - 2.6e5), fontsize=12,
            arrowprops=dict(arrowstyle="-", color="k"))
for name, (lo, la) in cities.items():
    px, py = p(lo, la)
    ax.plot(px, py, "o", ms=8, mfc=NAVY, mec="white", mew=1.5)
    ax.annotate(name, (px, py), (8, 6), textcoords="offset points", fontsize=12, fontweight="bold", color=NAVY)
ax.set_xlim(x[0], x[-1]); ax.set_ylim(y[0], y[-1]); ax.set_aspect("equal"); ax.axis("off")
save(fig, "crs-scale-error-conus-ask.png")

# ---------------------------------------------------------------- 2. Tennessee
tn = [f for f in lower48 if f["properties"]["name"] == "Tennessee"][0]
tn_paths = [Path(r) for r in rings(tn["geometry"])]
lon = np.linspace(-90.6, -81.4, 460); lat = np.linspace(34.6, 37.0, 160)
LON, LAT = np.meshgrid(lon, lat)
inside = np.zeros(LON.shape, bool)
for pth in tn_paths:
    inside |= pth.contains_points(np.c_[LON.ravel(), LAT.ravel()]).reshape(LON.shape)
cases = {"utm16": ("NAD 1983 UTM Zone 16N (Transverse Mercator)", Proj("EPSG:26916")),
         "spcs": ("NAD 1983 State Plane Tennessee (Lambert Conformal Conic)", Proj("EPSG:32136"))}
NUM["tennessee"] = {}
lim = 2600
for key, (title, pr) in cases.items():
    ppm = scale_error_pct(pr, LON, LAT) * 1e4
    worst = float(np.max(np.abs(ppm[inside])))
    NUM["tennessee"][key] = {"max_abs_ppm": round(worst), "min_ppm": round(float(ppm[inside].min())),
                             "max_ppm": round(float(ppm[inside].max()))}
    PX, PY = pr(LON, LAT)
    fig, ax = plt.subplots(figsize=(12, 4.6))
    m = np.where(inside, ppm, np.nan)
    pc = ax.pcolormesh(PX, PY, m, cmap="RdBu_r", norm=TwoSlopeNorm(0, -lim, lim), shading="auto")
    near = [f for f in lower48 if f["properties"]["name"] in (
        "Tennessee", "Kentucky", "Virginia", "North Carolina", "Georgia", "Alabama", "Mississippi",
        "Arkansas", "Missouri")]
    draw(ax, near, pr, color="#555", lw=0.7)
    if key == "utm16":
        cm = pr(np.full(50, -87.0), np.linspace(34.6, 37.0, 50))
        ax.plot(*cm, color="crimson", lw=3)
        ax.text(cm[0][-1], cm[1][-1] + 8e3, "central meridian 87° W", color="crimson", ha="center",
                fontsize=12, fontweight="bold")
    else:
        for sp in (35 + 15 / 60, 36 + 25 / 60):
            sl = pr(np.linspace(-90.6, -81.4, 80), np.full(80, sp))
            ax.plot(*sl, color="seagreen", lw=3)
        ax.text(*pr(-81.5, 36 + 25 / 60 + 0.08), "standard parallels\n35°15′ and 36°25′ N",
                color="seagreen", ha="right", va="bottom", fontsize=12, fontweight="bold")
    xs, ys = PX[inside], PY[inside]
    ax.set_xlim(xs.min() - 3e4, xs.max() + 3e4); ax.set_ylim(ys.min() - 3e4, ys.max() + 6e4)
    ax.set_aspect("equal"); ax.axis("off")
    cb = fig.colorbar(pc, ax=ax, shrink=0.85, pad=0.01)
    cb.set_label("scale error (parts per million)")
    ax.set_title(f"{title}\nlargest scale error in Tennessee: {worst:,.0f} ppm "
                 f"({worst / 10:,.0f} cm per km)", fontsize=14)
    save(fig, f"crs-tennessee-{key}.png")

# The "ask" version: Tennessee and its neighbors, nothing else.
pr = Proj("EPSG:32136")
fig, ax = plt.subplots(figsize=(12, 4.6))
draw(ax, near, pr, color="#555", lw=0.7)
for r in rings(tn["geometry"]):
    ax.fill(*pr(r[:, 0], r[:, 1]), color="#c9d6e6")
ax.set_xlim(xs.min() - 3e4, xs.max() + 3e4); ax.set_ylim(ys.min() - 3e4, ys.max() + 6e4)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Tennessee: about 710 km east to west, 190 km north to south", fontsize=14)
save(fig, "crs-tennessee-outline.png")

# ---------------------------------------------------------------- 3. UTM zones of the world
fig, ax = plt.subplots(figsize=(13, 6.8))
ident = lambda a, b: (a, b)
for f in land:
    for r in rings(f["geometry"]):
        ax.fill(r[:, 0], r[:, 1], color="#d9dee5", lw=0)
ax.fill_between([-114, -108], -80, 84, color=BLUE, alpha=0.35, lw=0)
for k in range(61):
    ax.plot([-180 + 6 * k] * 2, [-80, 84], color=NAVY, lw=0.6)
ax.plot([-180, 180], [0, 0], color="crimson", lw=1.2)
ax.plot([-180, 180], [84, 84], color=GRAY, lw=0.8, ls="--")
ax.plot([-180, 180], [-80, -80], color=GRAY, lw=0.8, ls="--")
for z in range(1, 61):
    ax.text(-180 + 6 * z - 3, -82, str(z), ha="center", va="top", fontsize=8.5, color=NAVY, clip_on=False)
ax.annotate("Zone 12\n(Utah)", (-111, 40), (-150, 62), fontsize=13, fontweight="bold", color=NAVY,
            arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.5))
ax.text(176, 2, "equator: N and S halves", ha="right", va="bottom", fontsize=11, color="crimson")
ax.text(176, 85.5, "84° N", ha="right", va="bottom", fontsize=10, color=GRAY)
ax.text(176, -78.5, "80° S (Antarctica cut off)", ha="right", va="bottom", fontsize=10, color=GRAY)
ax.set_xlim(-180, 180); ax.set_ylim(-80, 90); ax.set_aspect(1.0); ax.axis("off")
save(fig, "crs-utm-zones-world.png")

# ---------------------------------------------------------------- 4. BYU to the U
byu, uofu = (-111.6493, 40.2518), (-111.8421, 40.7649)
t = Transformer.from_crs(4269, 26912, always_xy=True)
(bx, by), (ux, uy) = t.transform(*byu), t.transform(*uofu)
geod = Geod(ellps="GRS80").inv(*byu, *uofu)[2]
NUM["byu_uofu"] = {"byu_utm": [round(bx), round(by)], "uofu_utm": [round(ux), round(uy)],
                   "dx_m": round(ux - bx), "dy_m": round(uy - by),
                   "utm_distance_m": round(float(np.hypot(ux - bx, uy - by))),
                   "ellipsoid_distance_m": round(geod),
                   "dlat_deg": round(uofu[1] - byu[1], 4), "dlon_deg": round(uofu[0] - byu[0], 4)}

with open(os.path.join(REPO, "tools", "week11_crs_numbers.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(NUM, f, indent=2)
print(json.dumps(NUM, indent=2))
