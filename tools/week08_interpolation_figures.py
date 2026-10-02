"""Week 8 interpolation figures from real data, with a known answer.

The truth is the Lab 7 Little Cottonwood Canyon DEM (C:\\Ames\\Lab07\\Check.gdb\\DEM_UTM, from
tools/lab07/run_model.py), resampled to 30 m. 150 sample points and 60 hold-out points are drawn at
random (seed 414) and snapped to 30 m cell centers, so that a method that passes through its data
returns the sampled value exactly at those cells. Six ArcGIS Pro methods interpolate the 150 points:
Thiessen polygons (Create Thiessen Polygons), Natural Neighbor, IDW (power 2, 12 points), Spline
(regularized), ordinary Kriging (spherical) and a 2nd-order Trend surface. Each is scored against
the truth (every cell inside the points' hull) and at the 60 hold-out points, and read back at the
150 sample cells (the exactness test). An empirical semivariogram of the 150 points gets a fitted
spherical model. The truth surface is decomposed into a 2nd-order trend, a smooth autocorrelated
part and the rest.

    python tools/week08_interpolation_figures.py      (ArcGIS Pro Python)

Writes slides/week-08/images/ip-*.png (new ones) and tools/week08_interpolation_numbers.json.
"""
import json
import math
import pathlib
import urllib.request

import arcpy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from arcpy.sa import (Idw, Kriging, KrigingModelOrdinary, NaturalNeighbor, RadiusVariable, Raster, Spline,
                      Trend, Hillshade)

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "slides" / "week-08" / "images"
GDB = r"C:\Ames\Week08\Interp.gdb"
SRC = r"C:\Ames\Lab07\Check.gdb\DEM_UTM"
SR = arcpy.SpatialReference(26912)
CELL = 30
plt.rcParams.update({"font.family": "Segoe UI", "font.size": 12, "axes.spines.top": False, "axes.spines.right": False})
NAVY, BLUE, ORANGE, GRAY, RED = "#002e5d", "#0062b8", "#e07a1f", "#5b6770", "#b3261e"

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
pathlib.Path(GDB).parent.mkdir(parents=True, exist_ok=True)
if not arcpy.Exists(GDB):
    arcpy.management.CreateFileGDB(str(pathlib.Path(GDB).parent), pathlib.Path(GDB).name)
arcpy.env.workspace = GDB

# --- truth at 30 m -----------------------------------------------------------------------------
truth_path = GDB + r"\Truth30"
arcpy.management.Resample(SRC, truth_path, CELL, "BILINEAR")
truth = Raster(truth_path)
arcpy.env.snapRaster = truth
arcpy.env.extent = truth
arcpy.env.cellSize = truth
arcpy.env.outputCoordinateSystem = SR
x0, y0 = truth.extent.XMin, truth.extent.YMax
T = arcpy.RasterToNumPyArray(truth, nodata_to_value=np.nan)
nr, nc = T.shape

rng = np.random.default_rng(414)
margin = 8                                   # cells kept away from the edge
cells = rng.choice((nr - 2 * margin) * (nc - 2 * margin), 210, replace=False)
rows = margin + cells // (nc - 2 * margin)
cols = margin + cells % (nc - 2 * margin)
xs = x0 + (cols + 0.5) * CELL
ys = y0 - (rows + 0.5) * CELL
zs = T[rows, cols]


def make_points(name, idx):
    fc = GDB + "\\" + name
    arcpy.management.CreateFeatureclass(GDB, name, "POINT", spatial_reference=SR)
    arcpy.management.AddField(fc, "Z", "DOUBLE")
    with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "Z"]) as cur:
        for i in idx:
            cur.insertRow([(float(xs[i]), float(ys[i])), float(zs[i])])
    return fc


pts = make_points("Samples", range(150))
hold = make_points("Holdout", range(150, 210))

# --- six methods ----------------------------------------------------------------------------
surf = {}
th = GDB + r"\Thiessen_poly"
arcpy.analysis.CreateThiessenPolygons(pts, th, "ALL")
arcpy.conversion.PolygonToRaster(th, "Z", GDB + r"\Thiessen", "CELL_CENTER", "", CELL)
surf["Thiessen polygons"] = Raster(GDB + r"\Thiessen")
surf["Natural neighbor"] = NaturalNeighbor(pts, "Z", CELL)
surf["IDW (power 2, 12 points)"] = Idw(pts, "Z", CELL, 2, RadiusVariable(12))
surf["Spline (regularized)"] = Spline(pts, "Z", CELL, "REGULARIZED", 0.1)
surf["Kriging, default lag"] = Kriging(pts, "Z", KrigingModelOrdinary("SPHERICAL"), CELL)
surf["Kriging (spherical, 300 m lag)"] = Kriging(pts, "Z", KrigingModelOrdinary("SPHERICAL", 300), CELL)
surf["Trend (2nd order)"] = Trend(pts, "Z", CELL, 2, "LINEAR")
for k, r in list(surf.items()):
    p = GDB + "\\S_" + "".join(ch for ch in k if ch.isalnum())[:24]
    r.save(p)
    surf[k] = Raster(p)

ll = arcpy.Point(truth.extent.XMin, truth.extent.YMin)
A = {k: arcpy.RasterToNumPyArray(r, ll, nc, nr, nodata_to_value=np.nan) for k, r in surf.items()}
hull = ~np.isnan(A["Natural neighbor"])      # natural neighbor is NoData outside the points' hull
nums = {"n_samples": 150, "n_holdout": 60, "cell_m": CELL, "methods": {}}
for k, a in A.items():
    err = a - T
    hold_err = a[rows[150:], cols[150:]] - zs[150:]
    samp_err = a[rows[:150], cols[:150]] - zs[:150]
    nums["methods"][k] = dict(
        rmse_all_m=round(float(np.sqrt(np.nanmean(err[hull] ** 2))), 1),
        rmse_holdout_m=round(float(np.sqrt(np.nanmean(hold_err ** 2))), 1),
        max_abs_at_samples_m=round(float(np.nanmax(np.abs(samp_err))), 2),
        mean_abs_at_samples_m=round(float(np.nanmean(np.abs(samp_err))), 2))
    print(k, nums["methods"][k], flush=True)
nums["truth_range_m"] = [round(float(np.nanmin(T)), 1), round(float(np.nanmax(T)), 1)]
nums["mean_only_rmse_holdout_m"] = round(float(np.sqrt(np.mean((zs[150:] - zs[:150].mean()) ** 2))), 1)

# --- figure: six surfaces + truth --------------------------------------------------------------
hs = arcpy.RasterToNumPyArray(Hillshade(truth, 315, 45), ll, nc, nr, nodata_to_value=0).astype(float)
ext = (truth.extent.XMin, truth.extent.XMax, truth.extent.YMin, truth.extent.YMax)
vmin, vmax = np.nanmin(T), np.nanmax(T)
fig, axs = plt.subplots(2, 4, figsize=(17, 8.2), dpi=120)
panels = [("The truth (30 m DEM)", T)] + list(A.items())
for ax, (k, a) in zip(axs.flat, panels[:8]):
    ax.imshow(a, extent=ext, cmap="terrain", vmin=vmin, vmax=vmax)
    if k.startswith("The truth"):
        ax.imshow(hs, extent=ext, cmap="gray", alpha=0.35)
    ax.plot(xs[:150], ys[:150], ".", color="k", ms=2.5)
    sub = "" if k.startswith("The truth") else f"\nerror {nums['methods'][k]['rmse_holdout_m']:.0f} m at 60 hold-out points"
    ax.set_title(k + sub, fontsize=12, color=NAVY, loc="left")
    ax.set_xticks([]); ax.set_yticks([])
fig.tight_layout(); fig.savefig(IMG / "ip-six-methods.png", bbox_inches="tight"); plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 4.4), dpi=150)
names = list(A)
vals = [nums["methods"][k]["rmse_holdout_m"] for k in names]
ax.barh(range(len(names)), vals, color=[ORANGE if v == min(vals) else BLUE for v in vals])
for i_, v in enumerate(vals):
    ax.text(v, i_, f"  {v:.0f} m", va="center", fontsize=10)
ax.axvline(nums["mean_only_rmse_holdout_m"], color=GRAY, ls=":")
ax.text(nums["mean_only_rmse_holdout_m"], -0.7, "just the mean of the samples ", color=GRAY, fontsize=10, ha="right", va="bottom")
ax.set_yticks(range(len(names))); ax.set_yticklabels(names); ax.invert_yaxis()
ax.set_xlabel("Root-mean-square error at the 60 hold-out points (m)")
ax.set_title("Which one to trust? Hold some points out, and measure", loc="left", color=NAVY, fontsize=14)
fig.tight_layout(); fig.savefig(IMG / "ip-holdout-error.png"); plt.close(fig)

# --- figure: exactness test bar chart ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 4.2), dpi=150)
mx = [nums["methods"][k]["mean_abs_at_samples_m"] for k in names]
ax.barh(range(len(names)), mx, color=[BLUE if v < 0.01 else ORANGE for v in mx])
for i, v in enumerate(mx):
    ax.text(v, i, f"  {v:.2f} m", va="center", fontsize=10)
ax.set_yticks(range(len(names))); ax.set_yticklabels(names); ax.invert_yaxis()
ax.set_xlabel("Mean difference between the surface and the sample value, at the 150 sample cells (m)")
ax.set_title("Exact or not? Read each surface back at its own sample points", loc="left", color=NAVY, fontsize=14)
fig.tight_layout(); fig.savefig(IMG / "ip-exactness-test.png"); plt.close(fig)

# --- figure: semivariogram cloud, binned, spherical fit ----------------------------------------
from scipy.optimize import curve_fit
X, Y, Z = xs[:150], ys[:150], zs[:150]
i, j = np.triu_indices(150, 1)
h = np.hypot(X[i] - X[j], Y[i] - Y[j])
g = 0.5 * (Z[i] - Z[j]) ** 2
bins = np.arange(0, 6001, 300)
bc = 0.5 * (bins[1:] + bins[:-1])
gb = np.array([g[(h >= a) & (h < b)].mean() if ((h >= a) & (h < b)).any() else np.nan for a, b in zip(bins[:-1], bins[1:])])


def spherical(hh, c0, c, a):
    hh = np.asarray(hh, float)
    return np.where(hh < a, c0 + c * (1.5 * hh / a - 0.5 * (hh / a) ** 3), c0 + c)


ok = ~np.isnan(gb)
(c0, c, a), _ = curve_fit(spherical, bc[ok], gb[ok], p0=[1000, np.nanmax(gb), 3000], bounds=([0, 0, 100], [np.inf, np.inf, 20000]))
nums["semivariogram"] = dict(nugget_m2=round(float(c0)), sill_m2=round(float(c0 + c)), range_m=round(float(a)),
                             pairs=int(len(h)), lag_bin_m=300)
fig, axs = plt.subplots(1, 2, figsize=(14, 5), dpi=130)
axs[0].plot(h, g / 1000, ".", color=GRAY, ms=2, alpha=0.4)
axs[0].set_title(f"The cloud: all {len(h):,} pairs of the 150 points", loc="left", color=NAVY)
axs[1].plot(bc[ok], gb[ok] / 1000, "o", color=BLUE, label="semivariance, pairs binned every 300 m")
hh = np.linspace(0, 6000, 300)
axs[1].plot(hh, spherical(hh, c0, c, a) / 1000, "-", color=ORANGE, lw=2.5, label="spherical model, fitted")
axs[1].axhline((c0 + c) / 1000, color=GRAY, ls=":"); axs[1].axvline(a, color=GRAY, ls=":")
axs[1].annotate(f"sill ≈ {(c0 + c) / 1000:,.0f} thousand m²", (3600, (c0 + c) / 1000), xytext=(0, 8), textcoords="offset points", color=GRAY)
axs[1].annotate(f"range ≈ {a:,.0f} m", (a, 0), xytext=(6, 8), textcoords="offset points", color=GRAY)
axs[1].annotate(f"nugget ≈ {c0:,.0f}", (0, c0 / 1000), xytext=(10, 4), textcoords="offset points", color=RED)
axs[1].plot([0], [c0 / 1000], "o", color=RED)
axs[1].set_title("The model: bin the pairs, fit a curve", loc="left", color=NAVY)
axs[1].legend(frameon=False, loc="upper left")
axs[1].set_ylim(0, np.nanmax(gb) / 1000 * 1.35)
axs[1].set_ylabel("Semivariance (thousand m²)")
for ax in axs:
    ax.set_xlabel("Lag distance h between the two points (m)")
axs[0].set_ylabel("Semivariance ½(Zi − Zj)² (thousand m²)")
axs[0].set_ylim(0, np.nanpercentile(g / 1000, 99))
fig.tight_layout(); fig.savefig(IMG / "ip-semivariogram-real.png"); plt.close(fig)

# --- figure: trend + autocorrelated + random ------------------------------------------------------
yy, xx = np.mgrid[0:nr, 0:nc]
xn, yn = (xx - nc / 2) / nc, (yy - nr / 2) / nr
M = np.column_stack([np.ones(T.size), xn.ravel(), yn.ravel(), xn.ravel() ** 2, xn.ravel() * yn.ravel(), yn.ravel() ** 2])
good = np.isfinite(T.ravel())
coef, *_ = np.linalg.lstsq(M[good], T.ravel()[good], rcond=None)
trend = (M @ coef).reshape(T.shape)
resid = T - trend
from scipy.ndimage import uniform_filter
smooth = uniform_filter(np.nan_to_num(resid), size=7, mode='nearest')   # 7 x 7 cells = 210 m moving average
smooth[~np.isfinite(T)] = np.nan
rnd = resid - smooth
nums["decomposition_std_m"] = dict(trend=round(float(np.nanstd(trend[np.isfinite(T)])), 1), autocorrelated=round(float(np.nanstd(smooth)), 1),
                                   random=round(float(np.nanstd(rnd)), 1))
fig, axs = plt.subplots(1, 4, figsize=(17, 4.6), dpi=130)
for ax, (title, arr, cmap) in zip(axs, [("The surface", T, "terrain"), ("Trend: a smooth 2nd-order surface", trend, "terrain"),
                                        ("Autocorrelated: what is left, smoothed over 210 m", smooth, "RdBu_r"),
                                        ("Random: what is left after that", rnd, "RdBu_r")]):
    if cmap == "terrain":
        im = ax.imshow(arr, extent=ext, cmap=cmap, vmin=vmin, vmax=vmax)
    else:
        lim = np.nanpercentile(np.abs(arr), 98)
        im = ax.imshow(arr, extent=ext, cmap=cmap, vmin=-lim, vmax=lim)
    ax.set_title(title, fontsize=11, color=NAVY, loc="left"); ax.set_xticks([]); ax.set_yticks([])
    cb = fig.colorbar(im, ax=ax, fraction=0.035); cb.ax.tick_params(labelsize=8)
fig.tight_layout(); fig.savefig(IMG / "ip-trend-autocorrelated-random.png", bbox_inches="tight"); plt.close(fig)

# --- figure: Utah activity locator -------------------------------------------------------------------
STATE = ("https://services1.arcgis.com/99lidPhWCzftIe9K/arcgis/rest/services/UtahStateBoundary/FeatureServer/0/"
         "query?where=STATE%3D%27Utah%27&outSR=4326&f=json&returnGeometry=true&geometryPrecision=4")
MUNI = ("https://services1.arcgis.com/99lidPhWCzftIe9K/arcgis/rest/services/UtahMunicipalBoundaries/FeatureServer/0/"
        "query?where=NAME+IN+(%27Provo%27,%27American+Fork%27,%27Moab%27,%27Cedar+City%27)&outFields=NAME"
        "&returnCentroid=true&returnGeometry=false&outSR=4326&f=json")
st = json.loads(urllib.request.urlopen(STATE, timeout=60).read())
cities = {f["attributes"]["NAME"]: (f["centroid"]["x"], f["centroid"]["y"])
          for f in json.loads(urllib.request.urlopen(MUNI, timeout=60).read())["features"]}
fig, ax = plt.subplots(figsize=(6.2, 7.2), dpi=150)
for feat in st["features"]:
    for ring in feat["geometry"]["rings"]:
        r = np.array(ring)
        ax.fill(r[:, 0], r[:, 1], color="#f2f2f2", ec=GRAY, lw=1.2)
for name, (lon, lat) in cities.items():
    provo = name == "Provo"
    ax.plot(lon, lat, "o", ms=11 if provo else 9, color=ORANGE if provo else BLUE, mec="white", mew=1.5)
    lab = "Provo  ?" if provo else name
    dx = -0.12 if name in ("American Fork",) else 0.12
    ax.text(lon + dx, lat, lab, ha="right" if dx < 0 else "left", va="center", fontsize=12,
            color=ORANGE if provo else NAVY, weight="bold" if provo else "normal")
ax.set_aspect(1 / math.cos(math.radians(39.3)))
ax.axis("off")
ax.set_title("Three known temperatures, one unknown", loc="left", color=NAVY, fontsize=14)
fig.tight_layout(); fig.savefig(IMG / "ip-utah-activity-map.png"); plt.close(fig)
nums["cities_lonlat"] = {k: [round(v[0], 3), round(v[1], 3)] for k, v in cities.items()}

json.dump(nums, open(ROOT / "tools" / "week08_interpolation_numbers.json", "w"), indent=1)
print(json.dumps({k: v for k, v in nums.items() if k != "methods"}, indent=1))
