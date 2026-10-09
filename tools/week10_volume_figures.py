r"""Figures for the Week 10 decks (slides/week-10/cut-and-fill.md and raster-volumes.md).

Cut and fill: a HYPOTHETICAL level building pad (150 m x 100 m) placed on the real Lab 5 DEM of
Provo's east bench (USGS 3DEP 1/3 arc-second, projected to NAD 1983 UTM 12N at 10 m, bilinear, as
Lab 5 does). ArcGIS Pro's Cut Fill tool (Spatial Analyst) is run on the existing and the design
surface, and the same volumes are recomputed cell by cell with numpy as a check. A sweep of the pad
elevation gives cut and fill as functions of the design grade.

Raster volumes: the Lab 9 package (Big Southern Butte, 10 m, Butte_Boundary), projected the same
way the lab does. Volume above three FLAT base planes taken from the outline's edge, against the
lab's published baseline (5.145 km3 above an IDW plain, the page's Step 8 check). No Step 9
sensitivity results are computed or shown here.

Writes slides/week-10/images/vo-*.png and tools/week10_volume_numbers.json.   ArcGIS Pro Python.
"""
import json, os
import numpy as np
import arcpy
from arcpy.sa import CutFill, Hillshade, Slope
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(REPO, "slides", "week-10", "images")
os.makedirs(OUT, exist_ok=True)
W = r"C:\Ames\Week10"
if not arcpy.Exists(os.path.join(W, "w10.gdb")):
    arcpy.management.CreateFileGDB(W, "w10.gdb")
G = os.path.join(W, "w10.gdb")
UTM = arcpy.SpatialReference(26912)
NUM = {}
plt.rcParams.update({"font.size": 13, "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    fig.tight_layout(); fig.savefig(os.path.join(OUT, name), dpi=150); plt.close(fig)


def project(src, name):
    out = os.path.join(G, name)
    if not arcpy.Exists(out):
        arcpy.management.ProjectRaster(src, out, UTM, "BILINEAR", "10")
    return arcpy.Raster(out)


def arr(r, ll, cols, rows):
    return arcpy.RasterToNumPyArray(r, ll, cols, rows, nodata_to_value=np.nan).astype("float64")


# ------------------------------------------------------------------ cut and fill
dem = project(os.path.join(W, "lab05-rock-canyon-dem", "RockCanyon_DEM.tif"), "RC_UTM")
slope = Slope(dem, "PERCENT_RISE")
# Search the bench for a 150 m x 100 m window with ground between 1,450 and 1,560 m and a mean slope
# nearest 8 %. The pad is hypothetical; the terrain under it is real.
D = arr(dem, arcpy.Point(dem.extent.XMin, dem.extent.YMin), dem.width, dem.height)
S = arr(slope, arcpy.Point(dem.extent.XMin, dem.extent.YMin), dem.width, dem.height)
best = None
for r0 in range(20, D.shape[0] - 40, 5):
    for c0 in range(20, D.shape[1] - 40, 5):
        zz = D[r0:r0 + 10, c0:c0 + 15]; ss = S[r0:r0 + 10, c0:c0 + 15]
        if np.isnan(zz).any() or np.isnan(ss).any():
            continue
        if not (1450 < zz.mean() < 1560) or ss.max() > 15:
            continue
        score = abs(ss.mean() - 8)
        if best is None or score < best[0]:
            best = (score, r0, c0, float(ss.mean()))
_, r0, c0, mslope = best
x0 = dem.extent.XMin + c0 * 10; y0 = dem.extent.YMax - (r0 + 10) * 10
cp = arcpy.PointGeometry(arcpy.Point(x0 + 75, y0 + 50), UTM).projectAs(arcpy.SpatialReference(4269)).firstPoint
lon, lat = round(cp.X, 5), round(cp.Y, 5)
NUM["pad"] = dict(lon=lon, lat=lat, x0=x0, y0=y0, width_m=150, depth_m=100, mean_slope_pct=round(mslope, 1))

# window: pad plus 200 m around it
wx0, wy0, wc, wr = x0 - 200, y0 - 200, 15 + 40, 10 + 40
E = arr(dem, arcpy.Point(wx0, wy0), wc, wr)          # rows top->bottom
pad = np.zeros_like(E, dtype=bool)
pad[20:30, 20:35] = True                              # 10 rows x 15 cols of 10 m cells
Z = E[pad]
NUM["pad"].update(ground_min=round(float(Z.min()), 2), ground_max=round(float(Z.max()), 2),
                  ground_mean=round(float(Z.mean()), 2), cells=int(pad.sum()))
A = 100.0
zs = np.linspace(Z.min(), Z.max(), 60)
cut = np.array([np.sum(np.clip(Z - z, 0, None)) * A for z in zs])
fil = np.array([np.sum(np.clip(z - Z, 0, None)) * A for z in zs])
zbal = float(Z.mean())
cut_b = float(np.sum(np.clip(Z - zbal, 0, None)) * A); fil_b = float(np.sum(np.clip(zbal - Z, 0, None)) * A)
NUM["balance"] = dict(z=round(zbal, 2), cut_m3=round(cut_b), fill_m3=round(fil_b))

# ArcGIS Pro Cut Fill on the same pad at the balance grade, as a cross-check
design = E.copy(); design[pad] = zbal
ll = arcpy.Point(wx0, wy0)
for name, a in (("Pad_Before", E), ("Pad_After", design)):
    arcpy.NumPyArrayToRaster(a, ll, 10, 10, np.nan).save(os.path.join(G, name))
    arcpy.management.DefineProjection(os.path.join(G, name), UTM)
cf = CutFill(os.path.join(G, "Pad_Before"), os.path.join(G, "Pad_After"), 1)
cf.save(os.path.join(G, "Pad_CutFill"))
rows = [r for r in arcpy.da.SearchCursor(os.path.join(G, "Pad_CutFill"), ["VALUE", "COUNT", "VOLUME", "AREA"])]
NUM["cutfill_tool_rows"] = [[int(v), int(c), round(vol, 1), round(a, 1)] for v, c, vol, a in rows]
pos = sum(r[2] for r in rows if r[2] > 0); neg = sum(r[2] for r in rows if r[2] < 0)
NUM["cutfill_tool_sum"] = dict(positive_m3=round(pos), negative_m3=round(neg))
# Sign check off balance: raise the grade 2 m, so fill must exceed cut.
d2 = E.copy(); d2[pad] = zbal + 2
arcpy.NumPyArrayToRaster(d2, ll, 10, 10, np.nan).save(os.path.join(G, "Pad_After2"))
arcpy.management.DefineProjection(os.path.join(G, "Pad_After2"), UTM)
CutFill(os.path.join(G, "Pad_Before"), os.path.join(G, "Pad_After2"), 1).save(os.path.join(G, "Pad_CutFill2"))
r2 = [r for r in arcpy.da.SearchCursor(os.path.join(G, "Pad_CutFill2"), ["VOLUME"])]
NUM["sign_check_grade_plus_2m"] = dict(tool_positive=round(sum(v for (v,) in r2 if v > 0)), tool_negative=round(sum(v for (v,) in r2 if v < 0)),
    numpy_cut=round(float(np.sum(np.clip(Z - zbal - 2, 0, None)) * A)), numpy_fill=round(float(np.sum(np.clip(zbal + 2 - Z, 0, None)) * A)))

# figures: sweep
fig, ax = plt.subplots(figsize=(10, 5.2))
ax.plot(zs, cut / 1000, color="#c05621", lw=3, label="cut (soil removed)")
ax.plot(zs, fil / 1000, color="#2b6cb0", lw=3, label="fill (soil placed)")
ax.axvline(zbal, color="#2d3748", ls="--")
ax.text(zbal - 0.3, max(cut.max(), fil.max()) / 1000 * 0.62,
        f"balance: {zbal:.1f} m\n= mean ground height\ncut = fill = {cut_b/1000:,.1f} thousand m³", ha="right")
ax.set_xlabel("pad grade (m above sea level)"); ax.set_ylabel("volume (thousand m³)")
ax.set_title("A 150 m × 100 m level pad on Provo's east bench (hypothetical)")
ax.legend(frameon=False, loc="upper right")
save(fig, "vo-pad-sweep.png")

# figure: map at the balance grade
hs = arcpy.RasterToNumPyArray(Hillshade(dem), ll, wc, wr, nodata_to_value=0).astype("float64")
d = np.where(pad, E - zbal, np.nan)
fig, ax = plt.subplots(figsize=(8.5, 6))
ext = [wx0, wx0 + wc * 10, wy0, wy0 + wr * 10]
ax.imshow(hs, cmap="gray", extent=ext)
lim = float(np.nanmax(np.abs(d)))
im = ax.imshow(d, cmap="RdBu_r", norm=TwoSlopeNorm(0, -lim, lim), extent=ext, alpha=0.9)
cb = fig.colorbar(im, ax=ax, fraction=0.04); cb.set_label("ground minus pad grade (m)\nred = cut, blue = fill")
ax.set_xticks([]); ax.set_yticks([])
ax.set_title(f"Cut and fill at the balance grade, {zbal:.1f} m")
save(fig, "vo-pad-map.png")

# figure: profile along the pad's long axis (middle row), extended
row = 25
xs = np.arange(wc) * 10 + 5
fig, ax = plt.subplots(figsize=(10, 4.2))
ax.plot(xs, E[row], color="#2d3748", lw=2, label="existing ground")
dz = design[row]
ax.plot(xs, dz, color="#2f855a", lw=2.5, label="design surface")
ax.fill_between(xs, E[row], dz, where=E[row] > dz, color="#c05621", alpha=0.6, label="cut")
ax.fill_between(xs, E[row], dz, where=E[row] < dz, color="#2b6cb0", alpha=0.6, label="fill")
ax.set_xlabel("distance along the pad (m)"); ax.set_ylabel("elevation (m)")
ax.legend(frameon=False, ncol=4, loc="upper left")
save(fig, "vo-pad-profile.png")

# ------------------------------------------------------------------ raster volumes (Big Southern Butte)
bdem = project(os.path.join(W, "lab09-big-southern-butte", "BigSouthernButte_DEM.tif"), "BSB_UTM")
outline = os.path.join(W, "lab09-big-southern-butte", "Lab09.gdb", "Butte_Boundary")
bll = arcpy.Point(bdem.extent.XMin, bdem.extent.YMin)
B = arr(bdem, bll, bdem.width, bdem.height)
mask_r = os.path.join(G, "Butte_Mask")
with arcpy.EnvManager(snapRaster=bdem, extent=bdem, cellSize=bdem):
    arcpy.conversion.PolygonToRaster(outline, "OBJECTID", mask_r, "CELL_CENTER", "", 10)
M = arcpy.RasterToNumPyArray(arcpy.Raster(mask_r), bll, bdem.width, bdem.height, nodata_to_value=-1).astype("float64"); M[M < 0] = np.nan
inside = np.isfinite(M) & np.isfinite(B)
# edge cells: inside cells with an outside 4-neighbor
pad_in = np.pad(inside, 1)
edge = inside & ~(pad_in[:-2, 1:-1] & pad_in[2:, 1:-1] & pad_in[1:-1, :-2] & pad_in[1:-1, 2:])
e = B[edge]
planes = {"lowest edge cell": float(e.min()), "mean of the edge": float(e.mean()), "highest edge cell": float(e.max())}
NUM["butte"] = dict(cells=int(inside.sum()), area_km2=round(inside.sum() * 100 / 1e6, 2),
                    dem_max=round(float(B[inside].max()), 1), lab_baseline_km3=5.145, planes={})
for k, z in planes.items():
    v = float(np.sum(B[inside] - z) * 100 / 1e9)
    NUM["butte"]["planes"][k] = dict(z=round(z, 1), volume_km3=round(v, 3))
fig, ax = plt.subplots(figsize=(10, 5))
names = list(planes) + ["IDW plain (Lab 9, Step 8)"]
vals = [NUM["butte"]["planes"][k]["volume_km3"] for k in planes] + [5.145]
cols = ["#a0aec0", "#a0aec0", "#a0aec0", "#2b6cb0"]
ax.barh(names, vals, color=cols)
for i, v in enumerate(vals):
    ax.text(v + 0.05, i, f"{v:.2f} km³", va="center")
ax.set_xlabel("volume of Big Southern Butte (km³)")
ax.set_title("Same DEM, same outline, four different bases")
ax.invert_yaxis()
save(fig, "vo-butte-bases.png")

# profile north-south through the summit
r_, c_ = np.unravel_index(np.nanargmax(np.where(inside, B, np.nan)), B.shape)
col = B[:, c_]; ins = inside[:, c_]
idx = np.where(ins)[0]; lo, hi = max(idx.min() - 150, 0), min(idx.max() + 150, len(col) - 1)
yy = (np.arange(lo, hi) - lo) * 10 / 1000
fig, ax = plt.subplots(figsize=(10, 4.4))
ax.fill_between(yy, col[lo:hi].min() - 20, col[lo:hi], color="#cbd5e0")
ax.plot(yy, col[lo:hi], color="#2d3748", lw=1.5, label="DEM (north to south through the summit)")
for (k, z), c in zip(planes.items(), ["#c05621", "#2f855a", "#805ad5"]):
    ax.axhline(z, ls="--", lw=1.4, color=c, label=f"flat base: {k} ({z:.0f} m)")
ax.set_xlabel("distance (km)"); ax.set_ylabel("elevation (m)")
ax.legend(frameon=False, loc="upper left")
save(fig, "vo-butte-profile.png")
NUM["butte"]["summit_col"] = int(c_)

json.dump(NUM, open(os.path.join(REPO, "tools", "week10_volume_numbers.json"), "w"), indent=1)
print(json.dumps(NUM, indent=1))
