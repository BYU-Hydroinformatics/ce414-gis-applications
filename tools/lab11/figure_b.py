r"""Lab 11 Figure B: the study area, drawn from the hosted package only (C:\Ames\Lab11\ref, extracted by
run_model.py): shaded relief of Elevation.tif, the lakes and marshes over 1 km2 (the barrier), the
existing kV lines, the major roads, the two substations and the straight line between them.

    python figure_b.py      -> docs/assignments/lab-11/images/lab11-study-area.png   ArcGIS Pro Python."""
import math
import os

import arcpy
import numpy as np
from arcpy.sa import Hillshade
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "docs", "assignments", "lab-11", "images", "lab11-study-area.png")
PKG = os.path.join(r"C:\Ames\Lab11\ref", "lab11-power-line")
SRC = os.path.join(PKG, "PowerLineData.gdb")
DEM = os.path.join(PKG, "Elevation.tif")


def parts(fc, where=None):
    out = []
    for (g,) in arcpy.da.SearchCursor(fc, ["SHAPE@"], where):
        for part in g:
            out.append(np.array([[p.X, p.Y] if p else [np.nan, np.nan] for p in part]) / 1000)
    return out


d = arcpy.Describe(DEM)
x0, y0, x1, y1 = d.extent.XMin, d.extent.YMin, d.extent.XMax, d.extent.YMax
hs = arcpy.RasterToNumPyArray(Hillshade(DEM, 315, 45), nodata_to_value=0)
fig, ax = plt.subplots(figsize=(8, 9.6))
ax.imshow(hs, cmap="gray", extent=[x0 / 1000, x1 / 1000, y0 / 1000, y1 / 1000], vmin=0, vmax=255, alpha=0.9)
for p in parts(SRC + r"\Roads", "DOT_FCLASS IN ('Interstate', 'Other Freeway', 'Principal Arterial')"):
    ax.plot(p[:, 0], p[:, 1], c="#555555", lw=0.6)
for p in parts(SRC + r"\Power_Lines", "LAYER LIKE 'KV-%'"):
    ax.plot(p[:, 0], p[:, 1], c="#e6b800", lw=1.1)
for p in parts(SRC + r"\Lakes", "AreaSqKm > 1"):
    ax.fill(p[:, 0], p[:, 1], fc="#6baed6", ec="#2171b5", lw=0.6)
xy = {r: (x / 1000, y / 1000) for r, (x, y) in arcpy.da.SearchCursor(SRC + r"\Endpoints", ["Role", "SHAPE@XY"])}
(sx, sy), (dx, dy) = xy["Source"], xy["Destination"]
ax.plot([sx, dx], [sy, dy], "--", c="k", lw=1.4)
km = math.dist((sx, sy), (dx, dy))
ax.text((sx + dx) / 2 + 1.2, (sy + dy) / 2, f"{km:.2f} km\nstraight line", fontsize=11, ha="left", va="center",
        bbox=dict(fc="white", ec="none", alpha=0.85))
ax.plot(sx, sy, "^", ms=13, mfc="#00a000", mec="w", mew=1.5, zorder=10)
ax.plot(dx, dy, "s", ms=12, mfc="#d00000", mec="w", mew=1.5, zorder=10)
ax.annotate("Source: substation at the mouth\nof Spanish Fork Canyon", (sx, sy), (sx - 30, sy - 8), fontsize=11,
            arrowprops=dict(arrowstyle="-", color="k"), bbox=dict(fc="white", ec="none", alpha=0.85))
ax.annotate("Destination: substation at\nPoint of the Mountain, Bluffdale", (dx, dy), (dx + 4, dy + 5), fontsize=11,
            arrowprops=dict(arrowstyle="-", color="k"), bbox=dict(fc="white", ec="none", alpha=0.85))
ax.text(431, 4448, "Utah Lake", fontsize=12, style="italic", color="#08306b", ha="center")
ax.set_xlim(x0 / 1000, x1 / 1000); ax.set_ylim(y0 / 1000, y1 / 1000); ax.set_aspect("equal")
ax.set_xlabel("UTM zone 12N easting (km)"); ax.set_ylabel("northing (km)")
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
ax.legend(handles=[Line2D([], [], c="#e6b800", lw=1.5, label="existing 46-345 kV lines"),
                   Line2D([], [], c="#555555", lw=1, label="major roads"),
                   Patch(fc="#6baed6", ec="#2171b5", label="lakes and marshes over 1 km² (barrier)")],
          loc="lower right", fontsize=10, framealpha=0.95)
fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print(OUT, f"{km:.2f}")
