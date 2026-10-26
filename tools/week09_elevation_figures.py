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

Thursday's kriging figures (the trend/autocorrelated/random split, the semivariogram, the kriged result)
and the method comparison (six methods, 60 hold-out points, the exactness test, the class vote) use the
same samples, so both days of Week 9 tell one story.

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
# 60 hold-out cells for Thursday's checkpoint test, drawn after the samples so the samples do not change.
rest = np.setdiff1d(np.arange((N - 8) ** 2), idx)
hidx = rng.choice(rest, 60, replace=False)
hr, hc = hidx // (N - 8) + 4, hidx % (N - 8) + 4

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
# exact_values=False lets a nugget pull the surface off the samples, as ArcGIS Pro's Kriging does.
ok = OrdinaryKriging(P[:, 0], P[:, 1], V, variogram_model="spherical", variogram_parameters=[cc, a_, c0],
                     exact_values=False)
surf["kriging"] = ok.execute("grid", x, y)[0].data
# The careless version: let pykrige fit its own spherical model with its default 6 lags. Thursday's lesson
# that one setting can make kriging worse than a far simpler method.
ok_auto = OrdinaryKriging(P[:, 0], P[:, 1], V, variogram_model="spherical", exact_values=False)
surf["kriging_auto"] = ok_auto.execute("grid", x, y)[0].data

nums = {"dem": "USGS 3DEP 3DEPElevation ImageServer, 30 m, EPSG:26912",
        "extent_utm": [CX - HALF, CY - HALF, CX + HALF, CY + HALF], "n_samples": len(V),
        "truth_range_m": [round(T.min()), round(T.max())],
        "kriging_spherical": dict(zip(["sill_partial", "range_km", "nugget"],
                                      [round(float(v), 3) for v in ok.variogram_model_parameters])),
        "kriging_auto_spherical": dict(zip(["sill_partial", "range_km", "nugget"],
                                           [round(float(v), 3) for v in ok_auto.variogram_model_parameters])),
        "n_holdout": len(hidx), "pairs": int(len(h)),
        "mean_only_rmse_holdout_m": round(float(np.sqrt(((V.mean() - T[hr, hc]) ** 2).mean())), 1),
        "methods": {}}
for k, s in surf.items():
    nums["methods"][k] = {"rmse_m": round(float(np.sqrt(((s - T) ** 2).mean())), 1),
                          "rmse_holdout_m": round(float(np.sqrt(((s[hr, hc] - T[hr, hc]) ** 2).mean())), 1),
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


# --- Thursday: kriging and the method comparison on the same samples ------------------------------
# The three components kriging separates, shown on the DEM itself: a 2nd-order trend fitted to every cell,
# what is left smoothed over 210 m (7 cells: the autocorrelated part), and the remainder (random).
from scipy.ndimage import uniform_filter
coef_all = np.linalg.lstsq(A(cells[:, 0], cells[:, 1]), T.ravel(), rcond=None)[0]
trend_all = (A(cells[:, 0], cells[:, 1]) * coef_all).sum(1).reshape(N, N)
auto = uniform_filter(T - trend_all, 7, mode="nearest")
rand = T - trend_all - auto
nums["decomposition_std_m"] = {k: round(float(v.std()), 1) for k, v in
                               [("trend", trend_all), ("autocorrelated", auto), ("random", rand)]}
fig, axs = plt.subplots(1, 4, figsize=(17.5, 3.5), dpi=150)
panels = [(T, "The surface", TERRAIN, (VMIN, VMAX)), (trend_all, "Trend: a smooth 2nd-order surface", TERRAIN, (VMIN, VMAX)),
          (auto, "Autocorrelated: what is left, smoothed over 210 m", "RdBu_r", (-500, 500)),
          (rand, "Random: what is left after that", "RdBu_r", (-60, 60))]
for ax, (Z, ttl, cm, (lo, hi)) in zip(axs, panels):
    im = ax.imshow(Z, cmap=cm, vmin=lo, vmax=hi, extent=(0, 7.2, 7.2, 0))
    ax.set_title(ttl, fontsize=11.5, color=NAVY, loc="left"); ax.set_xticks([]); ax.set_yticks([])
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03).ax.tick_params(labelsize=8)
fig.tight_layout(); fig.savefig(IMG / "ip-tp-decomposition.png"); plt.close(fig)

# The semivariogram: every pair (the cloud), then the pairs binned every 300 m and the fitted model.
hh = np.linspace(0, 5.5, 300)                       # model drawn past the last bin so the sill shows


def model_panel(ax, labels=True):
    ax.plot(mid * 1000, gam / 1000, "o", color="#0062b8", ms=6, label="semivariance, pairs binned every 300 m")
    ax.plot(hh * 1000, spherical(hh, c0, cc, a_) / 1000, color="#e07a1f", lw=2.5, label="spherical model, fitted")
    ax.set_xlabel("Lag distance h between the two points (m)"); ax.set_ylabel("Semivariance (thousand m²)")
    ax.spines[["top", "right"]].set_visible(False); ax.set_xlim(0, 5500); ax.set_ylim(0, None)
    if labels:
        sill = (c0 + cc) / 1000
        ax.axhline(sill, color=GRAY, ls=":", lw=1); ax.axvline(a_ * 1000, color=GRAY, ls=":", lw=1)
        ax.text(150, sill * 0.97, f"sill ≈ {sill:.0f} thousand m²", color=NAVY, fontsize=10, va="top")
        ax.text(a_ * 1000 + 60, sill * 0.55, f"range ≈ {a_ * 1000:,.0f} m", color=NAVY, fontsize=10, ha="left")
        ax.text(250, c0 / 1000 + sill * 0.02, f"nugget = {c0:.0f}", color="#b3261e", fontsize=10, va="bottom")
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.08), fontsize=9, frameon=False)


fig, ax = plt.subplots(figsize=(6.2, 4.3), dpi=150)
model_panel(ax); ax.set_title("The model: bin the pairs, fit a curve", fontsize=12, color=NAVY, loc="left")
fig.tight_layout(); fig.savefig(IMG / "ip-tp-semivariogram-model.png"); plt.close(fig)
fig, axs = plt.subplots(1, 2, figsize=(12.2, 4.3), dpi=150)
axs[0].plot(h * 1000, g2 / 1000, ".", ms=1.5, color=GRAY, alpha=0.35)
axs[0].set_xlabel("Lag distance h between the two points (m)"); axs[0].set_ylabel("½(Zᵢ − Zⱼ)² (thousand m²)")
axs[0].spines[["top", "right"]].set_visible(False)
axs[0].set_title(f"The cloud: all {len(h):,} pairs of the {len(V)} points", fontsize=12, color=NAVY, loc="left")
model_panel(axs[1]); axs[1].set_title("The model: bin the pairs, fit a curve", fontsize=12, color=NAVY, loc="left")
fig.tight_layout(); fig.savefig(IMG / "ip-tp-semivariogram.png"); plt.close(fig)

# The kriged result beside the truth, in 2D.
fig = plt.figure(figsize=(9.4, 4.8), dpi=160)
map_2d(fig.add_axes([0.01, 0.02, 0.42, 0.86]), T, "True surface (DEM)", points=False)
map_2d(fig.add_axes([0.445, 0.02, 0.42, 0.86]), surf["kriging"], "Ordinary kriging, spherical model")
colorbar(fig, [0.885, 0.1, 0.022, 0.74])
fig.savefig(IMG / "ip-tp-kriging-result.png"); plt.close(fig)

# Same points, six methods: the truth, then each surface with its hold-out error; hold-outs as open circles.
SIX = [("thiessen", "Thiessen polygons"), ("idw12", "IDW (power 2, 12 points)"), ("spline", "Spline (thin plate)"),
       ("kriging", "Kriging (spherical, fitted)"), ("kriging_auto", "Kriging (automatic fit)"), ("trend", "Trend (2nd order)")]
fig, axs = plt.subplots(2, 4, figsize=(15.5, 8.9), dpi=130)
map_2d(axs[0, 0], T, "The truth (30 m DEM)", points=False)
axs[0, 0].plot(x[hc], y[hr], "o", ms=4, mfc="none", mec="#b3261e", mew=1.2)
for ax, (key, lab) in zip(axs.ravel()[1:], SIX):
    map_2d(ax, np.clip(surf[key], VMIN - 400, VMAX + 400), None)
    ax.set_title(f"{lab}\nerror {nums['methods'][key]['rmse_holdout_m']:.0f} m at the 60 hold-out points",
                 fontsize=11, color=NAVY, loc="left")
axs[1, 3].axis("off")
axs[1, 3].text(0.02, 0.6, "Black dots: the 150 samples\nRed circles (first panel):\nthe 60 hold-out points,\nnever used to interpolate",
               fontsize=12, color=NAVY, va="center", transform=axs[1, 3].transAxes)
fig.tight_layout(h_pad=2.5); fig.savefig(IMG / "ip-tp-six-methods.png"); plt.close(fig)


def bars(values, xlabel, title, path, unit_fmt, best_low=True, refline=None):
    labs = [lab for _, lab in SIX]
    vals = [values[k] for k, _ in SIX]
    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=150)
    hi = np.argmin(vals) if best_low else None
    cols = ["#e07a1f" if (i == hi or (not best_low and v > 1)) else "#0062b8" for i, v in enumerate(vals)]
    ax.barh(range(len(vals)), vals, color=cols)
    for i, v in enumerate(vals):
        ax.text(v + max(vals) * 0.01, i, unit_fmt(v), va="center", fontsize=9)
    ax.set_yticks(range(len(vals))); ax.set_yticklabels(labs); ax.invert_yaxis()
    ax.set_xlabel(xlabel); ax.set_title(title, fontsize=12.5, color=NAVY, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    if refline is not None:
        ax.axvline(refline, color=GRAY, ls=":", lw=1.2)
        ax.text(refline, -0.75, "just the mean of the samples", fontsize=9, color=GRAY, ha="center")
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


bars({k: v["rmse_holdout_m"] for k, v in nums["methods"].items()}, "Root-mean-square error at the 60 hold-out points (m)",
     "Which one to trust? Hold some points out, and measure", IMG / "ip-tp-holdout-error.png",
     lambda v: f"{v:.0f} m", refline=nums["mean_only_rmse_holdout_m"])
bars({k: v["mean_abs_at_samples_m"] for k, v in nums["methods"].items()},
     "Mean difference between the surface and the sample value, at the 150 sample cells (m)",
     "Exact or not? Read each surface back at its own sample points", IMG / "ip-tp-exactness.png",
     lambda v: f"{v:.2f} m", best_low=False)

# Class vote: the truth on its own, and the six surfaces with names only (no scores, so the vote is honest).
fig = plt.figure(figsize=(5.0, 5.0), dpi=160)
map_2d(fig.add_axes([0.02, 0.02, 0.96, 0.96]), T, None, points=False)
fig.savefig(IMG / "ip-tp-dem-2d.png"); plt.close(fig)
fig, axs = plt.subplots(3, 2, figsize=(7.0, 10.2), dpi=150)
for ax, (key, lab) in zip(axs.ravel(), SIX):
    map_2d(ax, np.clip(surf[key], VMIN - 400, VMAX + 400), lab)
fig.tight_layout(); fig.savefig(IMG / "ip-tp-compare-methods.png"); plt.close(fig)

(ROOT / "tools" / "week09_elevation_numbers.json").write_text(json.dumps(nums, indent=2))
print(json.dumps({k: (v["rmse_holdout_m"], v["mean_abs_at_samples_m"]) for k, v in nums["methods"].items()}),
      nums["mean_only_rmse_holdout_m"], nums["kriging_auto_spherical"], nums["decomposition_std_m"], (c0, cc, a_))
