r"""Two larger figures for the Week 8 Thursday deck (slides/week-08/hand.md), October 21, 2026.

fl-bathtub-vs-hand-big.png: the bathtub and HAND 1% floods side by side, drawn to fill the slide's
right side (same data and colors as fl-bathtub-vs-hand.png in tools/week08_flood_figures.py).
fl-fema-compare-zoom.png: HAND's 1% flood against FEMA's 1% floodplain, the whole comparison area
with a box, and a zoomed window where hits, misses and false alarms are all visible.

Reads the Lab 7 package check (C:\Ames\HAND\PkgCheck, rebuilt by tools/lab07/verify_package.py) and the
FEMA rasters cached by week08_flood_figures.py in C:\Ames\Week08. Official scores are the Lab 7 page's
(tools/lab07/package_checks.json); the raster tally here is only for drawing.   ArcGIS Pro Python.
"""
import json, os
import numpy as np
import arcpy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch, Rectangle

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(REPO, "slides", "week-08", "images")
W8 = r"C:\Ames\Week08"
WG = r"C:\Ames\HAND\PkgCheck\Work.gdb"
checks = json.load(open(os.path.join(REPO, "tools", "lab07", "package_checks.json")))
row = [r for r in checks["stage_table"] if r["RETURN_YR"] == 100][0]
off = [r for r in checks["floods_default"] if r["return_yr"] == 100][0]
H100, Z100 = row["H_M"], row["ELEV_M"]

fillr = arcpy.Raster(os.path.join(WG, "Filled_DEM"))
LL = arcpy.Point(fillr.extent.XMin, fillr.extent.YMin)
C, R, cw = fillr.width, fillr.height, fillr.meanCellWidth


def grid(r, nd=np.nan):
    return arcpy.RasterToNumPyArray(r, LL, C, R, nodata_to_value=nd).astype("float64")


Fz = grid(fillr)
Hh = grid(arcpy.Raster(os.path.join(WG, "HAND")))
bath = np.isfinite(Fz) & (Fz <= Z100)
handw = np.isfinite(Hh) & (Hh <= H100)
fema = grid(arcpy.Raster(os.path.join(W8, "fema1pct.tif")), -1) >= 0
comp = grid(arcpy.Raster(os.path.join(W8, "comparea.tif")), -1) >= 0
ext = [fillr.extent.XMin, fillr.extent.XMax, fillr.extent.YMin, fillr.extent.YMax]
hs = np.where(np.isfinite(Fz), Fz, np.nan)
plt.rcParams.update({"font.size": 15})

# ------------------------------------------------------------------ bathtub and HAND, larger
fig, axes = plt.subplots(1, 2, figsize=(9.2, 6.4))
for ax, wet, color, title in [(axes[0], bath, "#2b6cb0", f"Bathtub: everything\nbelow {Z100:,.2f} m"),
                              (axes[1], handw, "#c05621", f"HAND ≤ {H100:.2f} m")]:
    ax.imshow(hs, cmap="gray", extent=ext)
    ax.imshow(np.where(wet, 1.0, np.nan), cmap=ListedColormap([color]), extent=ext, interpolation="nearest")
    ax.set_title(title, fontsize=16)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
fig.subplots_adjust(left=0.01, right=0.99, top=0.88, bottom=0.01, wspace=0.04)
fig.savefig(os.path.join(OUT, "fl-bathtub-vs-hand-big.png"), dpi=150)
plt.close(fig)

# ------------------------------------------------------------------ FEMA comparison with a zoom
hits = comp & fema & handw
miss = comp & fema & ~handw
fa = comp & ~fema & handw
cls = np.full(Fz.shape, np.nan)
cls[fa] = 0; cls[miss] = 1; cls[hits] = 2
cmap = ListedColormap(["#c05621", "#805ad5", "#2b6cb0"])
# the zoom window: the 140 x 140 cell (700 m) square where the scarcest of the three classes is largest
N = 140
best = None
for r0 in range(0, R - N, 10):
    for c0 in range(0, C - N, 10):
        w = cls[r0:r0 + N, c0:c0 + N]
        k = min((w == 0).sum(), (w == 1).sum(), (w == 2).sum())
        if best is None or k > best[0]:
            best = (k, r0, c0)
_, zr, zc = best
rows_, cols_ = np.where(comp)
r0, r1, c0, c1 = rows_.min(), rows_.max(), cols_.min(), cols_.max()


def xy(r, c):
    return ext[0] + c * cw, ext[3] - r * cw


fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 7.2), gridspec_kw={"width_ratios": [1, 1.55]})
x0, y1 = xy(r0, c0); x1, y0 = xy(r1 + 1, c1 + 1)
a1.imshow(hs[r0:r1 + 1, c0:c1 + 1], cmap="gray", extent=[x0, x1, y0, y1])
a1.imshow(cls[r0:r1 + 1, c0:c1 + 1], cmap=cmap, vmin=-0.5, vmax=2.5, extent=[x0, x1, y0, y1], interpolation="nearest")
zx0, zy1 = xy(zr, zc); zx1, zy0 = xy(zr + N, zc + N)
a1.add_patch(Rectangle((zx0, zy0), zx1 - zx0, zy1 - zy0, fill=False, ec="#e53e3e", lw=3))
a1.set_title("The whole reach", fontsize=16)
a2.imshow(hs[zr:zr + N, zc:zc + N], cmap="gray", extent=[zx0, zx1, zy0, zy1])
a2.imshow(cls[zr:zr + N, zc:zc + N], cmap=cmap, vmin=-0.5, vmax=2.5, extent=[zx0, zx1, zy0, zy1],
          interpolation="nearest", alpha=0.9)
a2.set_title("Zoomed in (700 m across)", fontsize=16)
for s in a2.spines.values():
    s.set_edgecolor("#e53e3e"); s.set_linewidth(3)
for ax in (a1, a2):
    ax.set_xticks([]); ax.set_yticks([])
fig.legend(handles=[Patch(color="#2b6cb0", label="hit: both flood it"),
                    Patch(color="#805ad5", label="miss: only FEMA floods it"),
                    Patch(color="#c05621", label="false alarm: only HAND floods it")],
           loc="lower center", ncol=1, frameon=False, fontsize=15, bbox_to_anchor=(0.62, 0.0))
fig.subplots_adjust(left=0.01, right=0.99, top=0.93, bottom=0.2, wspace=0.05)
fig.savefig(os.path.join(OUT, "fl-fema-compare-zoom.png"), dpi=150)
plt.close(fig)
print("zoom window rows", zr, "cols", zc, "scarcest-class cells", best[0])
print("raster tally hit rate", round(hits.sum() / (hits.sum() + miss.sum()), 3), "official", off["hit_rate"])
