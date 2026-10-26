"""Week 9 Tuesday elevation figures: one real DEM, one set of samples, five interpolators.

They replace the Bolstad contour figures on the Tuesday deck's elevation slides (the Elevation
Interpolation Scenario, Thiessen, IDW, trend and spline, and the kriged surface). Figures only, not
ArcGIS Pro screenshots, so they are computed here with numpy, scipy and pykrige:

- Truth: USGS 3DEP elevation around Mount Timpanogos, 7.2 x 7.2 km at 30 m in UTM zone 12N
  (EPSG:26912), from the 3DEPElevation ImageServer. Y Mountain is avoided because Lab 8 uses it.
- Samples: 150 cells drawn at random (seed 414), kept 4 cells from the edge, valued at the DEM cell.
- Thiessen (nearest sample), IDW (power 2, 6 and 12 nearest), a 2nd-order trend surface (least
  squares), a thin-plate spline (scipy RBFInterpolator, no smoothing) and ordinary kriging (pykrige,
  spherical model fitted to the samples). Every surface is computed at the DEM's cell centers and
  scored against the DEM (RMSE over every cell) and at its own samples (the exactness test).

    python tools/week09_elevation_figures.py   (any Python with matplotlib, numpy, scipy, tifffile, pykrige)

Writes slides/week-09/images/ip-tp-*.png and tools/week09_elevation_numbers.json.
"""

import io
import json
import pathlib
import urllib.parse
import urllib.request

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import tifffile
from PIL import Image
from matplotlib.colors import LightSource, LinearSegmentedColormap
from pykrige.ok import OrdinaryKriging
from scipy.interpolate import RBFInterpolator
from scipy.optimize import curve_fit
from scipy.spatial import Voronoi, cKDTree

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "slides" / "week-09" / "images"
plt.rcParams.update({"font.family": ["Segoe UI", "Arial", "DejaVu Sans"], "font.size": 12})
NAVY, GRAY = "#002e5d", "#5b6770"

# --- truth -----------------------------------------------------------------------------------------
CX, CY, HALF, CELL = 445200, 4471300, 3600, 30          # Mount Timpanogos summit is near the center
N = 2 * HALF // CELL
q = dict(bbox=f"{CX - HALF},{CY - HALF},{CX + HALF},{CY + HALF}", bboxSR=26912, imageSR=26912,
         size=f"{N},{N}", format="tiff", pixelType="F32", noDataInterpretation="esriNoDataMatchAny",
         interpolation="RSP_BilinearInterpolation", f="image")
url = ("https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage?"
       + urllib.parse.urlencode(q))
T = tifffile.imread(io.BytesIO(urllib.request.urlopen(url, timeout=120).read())).astype(float)
assert T.shape == (N, N) and not np.isnan(T).any()
x = (np.arange(N) + 0.5) * CELL / 1000                  # km from the west edge
y = (np.arange(N) + 0.5) * CELL / 1000                  # km from the north edge (row order)
XX, YY = np.meshgrid(x, y)
cells = np.c_[XX.ravel(), YY.ravel()]

# --- samples ---------------------------------------------------------------------------------------
rng = np.random.default_rng(414)
idx = rng.choice((N - 8) ** 2, 150, replace=False)
r, c = idx // (N - 8) + 4, idx % (N - 8) + 4
P = np.c_[x[c], y[r]]
V = T[r, c]

# --- surfaces --------------------------------------------------------------------------------------
tree = cKDTree(P)
_, nn = tree.query(cells, k=1)
surf = {"thiessen": V[nn].reshape(N, N)}


def idw(k, power=2):
    d, i = tree.query(cells, k=k)
    w = 1 / np.maximum(d, 1e-9) ** power
    return ((w * V[i]).sum(1) / w.sum(1)).reshape(N, N)


surf["idw6"], surf["idw12"] = idw(6), idw(12)
A = lambda u, v: np.c_[np.ones_like(u), u, v, u ** 2, v ** 2, u * v]
coef = np.linalg.lstsq(A(P[:, 0], P[:, 1]), V, rcond=None)[0]
surf["trend"] = (A(cells[:, 0], cells[:, 1]) * coef).sum(1).reshape(N, N)
surf["spline"] = RBFInterpolator(P, V, kernel="thin_plate_spline").__call__(cells).reshape(N, N)
# Spherical model fitted to the samples' semivariogram, binned every 0.3 km out to 4.5 km (pykrige's own
# fit collapsed the range to a few meters on these points, so it is fitted here and passed in).
h = np.hypot(*(P[:, None, :] - P[None, :, :]).transpose(2, 0, 1))
g2 = 0.5 * (V[:, None] - V[None, :]) ** 2
iu = np.triu_indices(len(V), 1)
h, g2 = h[iu], g2[iu]
edges = np.arange(0, 4.8, 0.3)
mid = (edges[:-1] + edges[1:]) / 2
gam = np.array([g2[(h >= lo) & (h < hi)].mean() for lo, hi in zip(edges[:-1], edges[1:])])


def spherical(hh, c0, cc, a):
    s_ = np.where(hh < a, 1.5 * hh / a - 0.5 * (hh / a) ** 3, 1.0)
    return c0 + cc * s_


(c0, cc, a_), _ = curve_fit(spherical, mid, gam, p0=[1000, gam.max(), 2.0], bounds=([0, 0, 0.2], [np.inf, np.inf, 20]))
ok = OrdinaryKriging(P[:, 0], P[:, 1], V, variogram_model="spherical", variogram_parameters=[cc, a_, c0])
surf["kriging"] = ok.execute("grid", x, y)[0].data

nums = {"dem": "USGS 3DEP 3DEPElevation ImageServer, 30 m, EPSG:26912",
        "extent_utm": [CX - HALF, CY - HALF, CX + HALF, CY + HALF], "n_samples": len(V),
        "truth_range_m": [round(T.min()), round(T.max())],
        "kriging_spherical": dict(zip(["sill_partial", "range_km", "nugget"],
                                      [round(float(v), 3) for v in ok.variogram_model_parameters])),
        "methods": {}}
for k, s in surf.items():
    nums["methods"][k] = {"rmse_m": round(float(np.sqrt(((s - T) ** 2).mean())), 1),
                          "mean_abs_at_samples_m": round(float(np.abs(s[r, c] - V).mean()), 2),
                          "range_m": [round(float(s.min())), round(float(s.max()))]}
(ROOT / "tools" / "week09_elevation_numbers.json").write_text(json.dumps(nums, indent=2))
print(json.dumps(nums["methods"], indent=1))

# --- figures ---------------------------------------------------------------------------------------
TERRAIN = LinearSegmentedColormap.from_list(
    "terr", ["#3f7f3a", "#8fb35a", "#d9c98a", "#b88a5a", "#8a6a55", "#c9c2bb", "#ffffff"])
VMIN, VMAX = 1800, 3600
ls = LightSource(azdeg=315, altdeg=40)


def shaded(Z):
    return ls.shade(Z, cmap=TERRAIN, vert_exag=1, dx=CELL, dy=CELL, blend_mode="soft",
                    vmin=VMIN, vmax=VMAX)


def surface_3d(Z, path, step=2):
    fig = plt.figure(figsize=(7.2, 5.2), dpi=170)
    ax = fig.add_axes([-0.12, -0.14, 1.24, 1.3], projection="3d")
    rgb = shaded(Z)
    ax.plot_surface(XX[::step, ::step], -YY[::step, ::step], Z[::step, ::step], facecolors=rgb[::step, ::step],
                    rstride=1, cstride=1, linewidth=0, antialiased=False, shade=False)
    ax.set_zlim(VMIN - 600, VMAX + 200); ax.set_box_aspect((1, 1, 0.42))
    ax.view_init(elev=32, azim=-62); ax.set_axis_off()
    fig.savefig(path, transparent=True); plt.close(fig)   # transparent: the title slide is navy
    im = Image.open(path)                                 # crop to the drawn pixels; 3D axes leave wide margins
    im.crop(im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()).save(path)


def map_2d(ax, Z, title=None, points=True, contours=True):
    ax.imshow(shaded(Z), extent=(0, x[-1] + 0.015, y[-1] + 0.015, 0))
    if contours:
        ax.contour(XX, YY, Z, levels=np.arange(1800, 3700, 100), colors="k", linewidths=0.35, alpha=0.55)
    if points:
        ax.plot(P[:, 0], P[:, 1], "o", ms=3.2, color="black", mec="white", mew=0.6)
    ax.set_xlim(0, 7.2); ax.set_ylim(7.2, 0); ax.set_xticks([]); ax.set_yticks([])
    if title: ax.set_title(title, fontsize=14, color=NAVY, loc="left")


def colorbar(fig, rect):
    cax = fig.add_axes(rect)
    sm = plt.cm.ScalarMappable(cmap=TERRAIN, norm=plt.Normalize(VMIN, VMAX))
    cb = fig.colorbar(sm, cax=cax); cb.set_label("Elevation (m)", color=NAVY)


def scalebar(ax):
    ax.plot([0.4, 2.4], [6.85, 6.85], color="white", lw=5, solid_capstyle="butt")
    ax.plot([0.4, 2.4], [6.85, 6.85], color="black", lw=2.5, solid_capstyle="butt")
    ax.text(1.4, 6.6, "2 km", ha="center", va="bottom", fontsize=11, weight="bold",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.8))


# The truth in 3D, and the samples alone (all the interpolator gets to see).
surface_3d(T, IMG / "ip-tp-dem-3d.png")
fig = plt.figure(figsize=(5.4, 5.0), dpi=170)
ax = fig.add_axes([0.02, 0.02, 0.78, 0.94])
sc = ax.scatter(P[:, 0], P[:, 1], c=V, cmap=TERRAIN, vmin=VMIN, vmax=VMAX, s=34, edgecolors="black", linewidths=0.6)
ax.set_xlim(0, 7.2); ax.set_ylim(7.2, 0); ax.set_xticks([]); ax.set_yticks([]); ax.set_facecolor("#fbfbfb")
scalebar(ax)
colorbar(fig, [0.84, 0.12, 0.04, 0.76])
fig.savefig(IMG / "ip-tp-samples.png"); plt.close(fig)

# Thiessen: the polygons, colored by their sample's elevation, then the stepped surface in 3D.
fig = plt.figure(figsize=(5.0, 5.0), dpi=170)
ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
ax.imshow(surf["thiessen"], cmap=TERRAIN, vmin=VMIN, vmax=VMAX, extent=(0, 7.2, 7.2, 0), interpolation="nearest")
vor = Voronoi(np.vstack([P, [[-50, -50], [-50, 60], [60, -50], [60, 60]]]))
for a, b in vor.ridge_vertices:
    if a >= 0 and b >= 0:
        ax.plot(*vor.vertices[[a, b]].T, color="black", lw=0.7)
ax.plot(P[:, 0], P[:, 1], "o", ms=3.2, color="black", mec="white", mew=0.6)
ax.set_xlim(0, 7.2); ax.set_ylim(7.2, 0); ax.set_xticks([]); ax.set_yticks([])
fig.savefig(IMG / "ip-tp-thiessen-polygons.png"); plt.close(fig)
surface_3d(surf["thiessen"], IMG / "ip-tp-thiessen-3d.png", step=1)

# IDW: 6 against 12 nearest points, then the 12-point surface in 3D.
fig = plt.figure(figsize=(9.4, 5.0), dpi=170)
for k, (key, lab) in enumerate([("idw6", "IDW, power 2, 6 nearest points"), ("idw12", "IDW, power 2, 12 nearest points")]):
    map_2d(fig.add_axes([0.01 + k * 0.435, 0.02, 0.42, 0.86]), surf[key], lab)
colorbar(fig, [0.885, 0.1, 0.022, 0.74])
fig.savefig(IMG / "ip-tp-idw-6-vs-12.png"); plt.close(fig)
surface_3d(surf["idw12"], IMG / "ip-tp-idw-3d.png")

# Trend and spline, each beside the truth.
for key, lab in [("trend", "Trend surface (2nd order)"), ("spline", "Spline (thin plate)")]:
    fig = plt.figure(figsize=(8.4, 4.6), dpi=170)
    map_2d(fig.add_axes([0.01, 0.02, 0.48, 0.86]), T, "True surface (DEM)", points=False)
    map_2d(fig.add_axes([0.51, 0.02, 0.48, 0.86]), np.clip(surf[key], VMIN - 400, VMAX + 400), lab)
    fig.savefig(IMG / f"ip-tp-{key}.png"); plt.close(fig)

# Kriging in 3D: Thursday's preview and the title slide.
surface_3d(surf["kriging"], IMG / "ip-tp-kriged-3d.png")
