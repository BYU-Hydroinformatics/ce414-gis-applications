r"""Figures for the Week 8 flood decks (slides/week-08/flood-models.md and hand.md).

All data are the Lab 7 package and its sources (tools/lab07/): USGS 10163000 Provo River at Provo
annual peaks and current rating (package CSVs), FEMA Utah County FIS Table 9 flows (read from the FIS
report, 49049CV001B), FEMA NFHL cross-sections (C:\Ames\HAND\HAND.gdb\FEMA_XS), the 5 m lidar DEM,
and the HAND raster the package chain produces (Fill > Flow Direction > Flow Accumulation > streams
> 30 m river corridor > Flow Distance VERTICAL), copied to C:\Ames\Week08.

Writes slides/week-08/images/fl-*.png and tools/week08_flood_numbers.json.   ArcGIS Pro Python.
"""
import csv, json, math, os
import numpy as np
import arcpy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(REPO, "slides", "week-08", "images")
os.makedirs(OUT, exist_ok=True)
W8 = r"C:\Ames\Week08"
PKG = os.path.join(W8, "pkg")
GDB = r"C:\Ames\HAND\HAND.gdb"
FEMA = {"10%": 1475, "4%": 1810, "2%": 2065, "1%": 2325, "0.2%": 2935}   # FIS Table 9, Provo River
NUM = {}
plt.rcParams.update({"font.size": 13, "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    fig.tight_layout(); fig.savefig(os.path.join(OUT, name), dpi=150); plt.close(fig)


# ---- peaks
peaks = []
for r in csv.DictReader(open(os.path.join(PKG, "peaks_10163000.csv"))):
    try:
        peaks.append((int(r["peak_date"][:4]), float(r["peak_cfs"]), r["peak_code"]))
    except ValueError:
        pass
yrs = [p[0] for p in peaks]; q = [p[1] for p in peaks]
NUM["peaks"] = dict(n=len(q), first=min(yrs), last=max(yrs), max=max(q), max_year=yrs[q.index(max(q))],
                    all_code_6=all("6" in p[2] for p in peaks))
fig, ax = plt.subplots(figsize=(11, 5))
ax.bar(yrs, q, width=0.8, color="#2b6cb0")
ax.axhline(FEMA["1%"], color="#c05621", ls="--", lw=2)
ax.text(min(yrs) + 1, FEMA["1%"] + 60, "FEMA 1% annual-chance flow, 2,325 ft³/s", color="#c05621")
ax.set_ylabel("annual peak flow (ft³/s)"); ax.set_xlabel("year")
ax.set_title("Provo River at Provo (USGS 10163000): the largest flow of each year")
save(fig, "fl-peaks.png")

# ---- frequency (Weibull plotting positions) with FEMA's flows
qs = sorted(q, reverse=True); n = len(qs)
T = [(n + 1) / (i + 1) for i in range(n)]
fig, ax = plt.subplots(figsize=(10, 5.2))
ax.scatter(T, qs, s=22, color="#2b6cb0", label=f"{n} measured annual peaks (rank-based return period)")
fx = {"10%": 10, "4%": 25, "2%": 50, "1%": 100, "0.2%": 500}
ax.scatter([fx[k] for k in FEMA], list(FEMA.values()), marker="D", s=70, color="#c05621", label="FEMA published flows")
for k, v in FEMA.items():
    ax.annotate(k, (fx[k], v), textcoords="offset points", xytext=(6, -14), color="#c05621")
ax.set_xscale("log"); ax.set_xlabel("return period (years, log scale)"); ax.set_ylabel("peak flow (ft³/s)")
ax.set_xticks([1, 2, 5, 10, 25, 50, 100, 500]); ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax.legend(frameon=False, loc="upper left")
save(fig, "fl-frequency.png")

# ---- rating
rt = [(float(r["gage_height_ft"]), float(r["discharge_cfs"])) for r in csv.DictReader(open(os.path.join(PKG, "rating_10163000.csv")))]
gh = [a for a, b in rt]; cfs = [b for a, b in rt]
NUM["rating"] = dict(rows=len(rt), gh_min=min(gh), gh_max=max(gh), q_min=min(cfs), q_max=max(cfs))
fig, ax = plt.subplots(figsize=(10, 5.2))
ax.plot(cfs, gh, color="#2b6cb0", lw=3, label="USGS rating: gage height for each flow")
ax.axvspan(max(cfs), 3100, color="#e2e8f0")
ax.text(max(cfs) + 30, min(gh) + 0.3, "beyond the\nrating:\nextrapolated", color="#4a5568")
for k, v in FEMA.items():
    if k == "0.2%":
        continue
    ax.axvline(v, color="#c05621", ls=":", lw=1.5)
    ax.text(v + 15, max(gh) - 0.35, k, color="#c05621")
ax.set_xlim(0, 3100); ax.set_xlabel("flow (ft³/s)"); ax.set_ylabel("gage height (ft)")
ax.legend(frameon=False, loc="lower right")
save(fig, "fl-rating.png")

# ---- FEMA cross-sections vs the DEM
dem = arcpy.Raster(os.path.join(PKG, "Provo_DEM.tif"))
ext = dem.extent
xs = []
for oid, shp, ltr, wsel, bed in arcpy.da.SearchCursor(os.path.join(GDB, "FEMA_XS"), ["OID@", "SHAPE@", "XS_LTR", "WSEL_REG", "STRMBED_EL"]):
    c = shp.centroid
    if ext.XMin < c.X < ext.XMax and ext.YMin < c.Y < ext.YMax and wsel > 0 and bed > 0:
        xs.append((c.Y, ltr, shp, wsel * 0.3048, bed * 0.3048))
xs.sort(key=lambda t: t[0])
pick = [xs[int(i)] for i in np.linspace(0, len(xs) - 1, 3)] if len(xs) >= 3 else xs
NUM["xs_in_dem"] = len(xs)
NUM["xs_depths_m"] = [round(w - b, 2) for _, _, _, w, b in xs]
fig, axes = plt.subplots(1, len(pick), figsize=(12, 4.4), sharey=False)
for ax, (_, ltr, shp, w, b) in zip(np.atleast_1d(axes), pick):
    L = shp.length
    d = np.linspace(0, L, 120)
    z = []
    for s in d:
        p = shp.positionAlongLine(s).firstPoint
        v = arcpy.management.GetCellValue(dem, f"{p.X} {p.Y}").getOutput(0)
        z.append(float(v) if v not in ("NoData", "") else np.nan)
    z = np.array(z)
    ax.fill_between(d, np.nanmin(z) - 1, z, color="#a0aec0")
    ax.plot(d, z, color="#2d3748", lw=1.5, label="lidar ground")
    ax.fill_between(d, z, w, where=z < w, color="#63b3ed", alpha=0.7)
    ax.axhline(w, color="#2b6cb0", lw=2, label="FEMA 1% water surface")
    ax.axhline(b, color="#c05621", ls="--", lw=1.5, label="FEMA streambed")
    ax.set_title(f"Section {ltr}: depth {w - b:.1f} m")
    ax.set_xlabel("distance across (m)")
    ax.set_ylim(np.nanmin(z) - 1, max(w, np.nanmax(z)) + 1)
np.atleast_1d(axes)[0].set_ylabel("elevation (m, NAVD 88)")
np.atleast_1d(axes)[0].legend(frameon=False, fontsize=10, loc="upper left")
save(fig, "fl-fema-xs.png")

# ---- HAND map
hand = arcpy.Raster(os.path.join(W8, "hand.tif"))
river = arcpy.Raster(os.path.join(W8, "river.tif"))
LL = arcpy.Point(hand.extent.XMin, hand.extent.YMin)
H = arcpy.RasterToNumPyArray(hand, LL, hand.width, hand.height, nodata_to_value=np.nan)
R = arcpy.RasterToNumPyArray(river, LL, hand.width, hand.height, nodata_to_value=0)
F = arcpy.RasterToNumPyArray(arcpy.Raster(os.path.join(W8, "fill.tif")), LL, hand.width, hand.height, nodata_to_value=np.nan)
valid = np.isfinite(H)
NUM["hand"] = dict(cells=int(valid.sum()), min=round(float(np.nanmin(H)), 2), max=round(float(np.nanmax(H)), 2),
                   pct_under_2m=round(float((H[valid] < 2).mean() * 100), 1), pct_under_5m=round(float((H[valid] < 5).mean() * 100), 1),
                   river_cells=int((R > 0).sum()))
bounds = [0, 1, 2, 3, 5, 10, 25, 1000]
cmap = ListedColormap(["#08306b", "#2171b5", "#6baed6", "#c6dbef", "#fdd0a2", "#fd8d3c", "#a63603"])
norm = BoundaryNorm(bounds, cmap.N)
x0, x1 = hand.extent.XMin, hand.extent.XMax; y0, y1 = hand.extent.YMin, hand.extent.YMax
fig, axes = plt.subplots(1, 2, figsize=(13, 6.2))
im0 = axes[0].imshow(F, extent=[x0, x1, y0, y1], cmap="terrain")
axes[0].set_title("Elevation above sea level (m)")
fig.colorbar(im0, ax=axes[0], fraction=0.046)
im1 = axes[1].imshow(H, extent=[x0, x1, y0, y1], cmap=cmap, norm=norm)
rr = np.where(R > 0, 1.0, np.nan)
axes[1].imshow(rr, extent=[x0, x1, y0, y1], cmap=ListedColormap(["#e53e3e"]), interpolation="nearest")
axes[1].set_title("Height above the Provo River (HAND, m); river in red")
cb = fig.colorbar(im1, ax=axes[1], fraction=0.046, ticks=bounds[:-1])
for a in axes:
    a.set_xticks([]); a.set_yticks([])
save(fig, "fl-hand-map.png")

json.dump(NUM, open(os.path.join(REPO, "tools", "week08_flood_numbers.json"), "w"), indent=1)
print(json.dumps(NUM, indent=1))


# ================================================================ part 2: the final Lab 7 package
# Read from C:\Ames\HAND\PkgCheck (tools/lab07/verify_package.py rebuilds it from the hosted zip).
# The 1% (100-yr) row of the FEMA stage table: h = 1.527 m (153 cm), water elevation at the gage
# 1,372.036 m NAVD 88 (tools/lab07/package_checks.json).
from arcpy.sa import Con, FlowDistance
arcpy.CheckOutExtension("Spatial"); arcpy.env.overwriteOutput = True
PK = r"C:\Ames\HAND\PkgCheck"; WG = os.path.join(PK, "Work.gdb")
PD = os.path.join(PK, "lab07-provo-river-hand", "ProvoData.gdb")
checks = json.load(open(os.path.join(REPO, "tools", "lab07", "package_checks.json")))
row100 = [r for r in checks["stage_table"] if r["RETURN_YR"] == 100][0]
H100, Z100 = row100["H_M"], row100["ELEV_M"]
fillr = arcpy.Raster(os.path.join(WG, "Filled_DEM")); hr = arcpy.Raster(os.path.join(WG, "HAND"))
LL2 = arcpy.Point(fillr.extent.XMin, fillr.extent.YMin); C2, R2 = fillr.width, fillr.height
def grid(r, nd=np.nan):
    return arcpy.RasterToNumPyArray(r, LL2, C2, R2, nodata_to_value=nd).astype("float64")
Fz = grid(fillr); Hh = grid(hr)
cell = fillr.meanCellWidth ** 2
bath = np.isfinite(Fz) & (Fz <= Z100)
handw = np.isfinite(Hh) & (Hh <= H100)
# every gully a stream: HAND to all stream cells, no river corridor
with arcpy.EnvManager(snapRaster=fillr, extent=fillr, cellSize=fillr):
    hall = FlowDistance(os.path.join(WG, "Stream_Cells"), fillr, os.path.join(WG, "Flow_Direction"), "VERTICAL", "D8", "MINIMUM")
    Ha = grid(hall)
allw = np.isfinite(Ha) & (Ha <= H100)
# FEMA comparison inside the comparison area, on the same grid
def rast(fc, name):
    out = os.path.join(W8, name + ".tif")
    with arcpy.EnvManager(snapRaster=fillr, extent=fillr, cellSize=fillr):
        arcpy.conversion.PolygonToRaster(fc, "OBJECTID", out, "CELL_CENTER", "", fillr.meanCellWidth)
    return grid(arcpy.Raster(out), -1) >= 0
fema = rast(os.path.join(PD, "FEMA_Floodplain_1pct"), "fema1pct")
comp = rast(os.path.join(PD, "Comparison_Area"), "comparea")
hits = comp & fema & handw; miss = comp & fema & ~handw; fa = comp & ~fema & handw
# Official values are the Lab 7 page's (polygon overlay in verify_package.py); the raster tallies here
# differ in the third decimal and are used only to draw the map.
off = [r for r in checks["floods_default"] if r["return_yr"] == 100][0]
NUM["final"] = dict(h100=H100, z100=Z100, bathtub_km2=round(bath.sum() * cell / 1e6, 2),
                    hand_km2=round(handw.sum() * cell / 1e6, 4), every_gully_km2=round(allw.sum() * cell / 1e6, 2),
                    hit_rate=round(hits.sum() / (hits.sum() + miss.sum()), 3),
                    false_alarm=round(fa.sum() / (hits.sum() + fa.sum()), 3),
                    csi=round(hits.sum() / (hits.sum() + miss.sum() + fa.sum()), 3))
hs = np.where(np.isfinite(Fz), Fz, np.nan)
ext2 = [fillr.extent.XMin, fillr.extent.XMax, fillr.extent.YMin, fillr.extent.YMax]
def panel(ax, wet, title, color):
    ax.imshow(hs, cmap="gray", extent=ext2)
    ax.imshow(np.where(wet, 1.0, np.nan), cmap=ListedColormap([color]), extent=ext2, interpolation="nearest")
    ax.set_title(title, fontsize=13); ax.set_xticks([]); ax.set_yticks([])
fig, axes = plt.subplots(1, 2, figsize=(12, 7))
panel(axes[0], bath, f"Bathtub: everything below {Z100:.2f} m\n{NUM['final']['bathtub_km2']} km² wet", "#2b6cb0")
panel(axes[1], handw, f"HAND ≤ {H100:.3f} m\n{off['area_km2']:.2f} km² wet", "#c05621")
fig.suptitle("The FEMA 1% flood at the Provo River gage, two ways", fontsize=15)
save(fig, "fl-bathtub-vs-hand.png")
fig, axes = plt.subplots(1, 2, figsize=(12, 7))
panel(axes[0], allw, f"Every gully a stream\n{NUM['final']['every_gully_km2']} km² wet", "#805ad5")
panel(axes[1], handw, f"Provo River only (30 m corridor)\n{off['area_km2']:.2f} km² wet", "#c05621")
fig.suptitle(f"Same DEM, same depth (h = {H100:.3f} m): only the stream definition changed", fontsize=15)
save(fig, "fl-stream-definition.png")
cls = np.full(Fz.shape, np.nan); cls[fa] = 0; cls[miss] = 1; cls[hits] = 2
rows_, cols_ = np.where(comp)
r0, r1, c0, c1 = rows_.min(), rows_.max(), cols_.min(), cols_.max()
fig, ax = plt.subplots(figsize=(9, 8))
x0c = ext2[0] + c0 * fillr.meanCellWidth; x1c = ext2[0] + (c1 + 1) * fillr.meanCellWidth
y1c = ext2[3] - r0 * fillr.meanCellWidth; y0c = ext2[3] - (r1 + 1) * fillr.meanCellWidth
ax.imshow(hs[r0:r1 + 1, c0:c1 + 1], cmap="gray", extent=[x0c, x1c, y0c, y1c])
ax.imshow(cls[r0:r1 + 1, c0:c1 + 1], cmap=ListedColormap(["#c05621", "#805ad5", "#2b6cb0"]), vmin=-0.5, vmax=2.5,
          extent=[x0c, x1c, y0c, y1c], interpolation="nearest")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color="#2b6cb0", label="hit: both flood"), Patch(color="#805ad5", label="miss: only FEMA floods"),
                   Patch(color="#c05621", label="false alarm: only HAND floods")], loc="upper left", frameon=True)
ax.set_title(f"HAND 1% flood against FEMA's 1% floodplain\nhit rate {off['hit_rate']}, false-alarm ratio {off['false_alarm_ratio']}, CSI {off['csi']}")
ax.set_xticks([]); ax.set_yticks([])
save(fig, "fl-fema-compare.png")
json.dump(NUM, open(os.path.join(REPO, "tools", "week08_flood_numbers.json"), "w"), indent=1)
NUM["final"]["official_100yr"] = {k: off[k] for k in ("area_km2", "buildings", "hit_rate", "false_alarm_ratio", "csi")}
json.dump(NUM, open(os.path.join(REPO, "tools", "week08_flood_numbers.json"), "w"), indent=1)
print("FINAL", json.dumps(NUM["final"]))
