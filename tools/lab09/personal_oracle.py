"""Lab 9 personal-run oracle (October 28, 2026): the Step 9 wide-outline run for every pair of
BYU ID digits. The student widens the supplied outline by 3 x (last two digits) meters with the
Buffer tool (00 = the supplied outline itself), then runs the model with seed 1, 1,000 points and
IDW power 2; the sampling ring is rebuilt 1,500 m around the widened outline, as the model does.

Writes ../ce414-private/grading-oracles/lab09_personal_lookup.csv (never public).
Needs DEM_UTM and Butte_Boundary in C:\\Ames\\Lab08\\Check.gdb. Run with propy.bat; about an hour.
"""
import csv
import os
import sys

import arcpy
import numpy as np
from arcpy.sa import ExtractByMask, Idw, RadiusVariable, Raster, ZonalStatistics

GDB = r"C:\Ames\Lab08\Check.gdb"
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = GDB
dem = Raster(os.path.join(GDB, "DEM_UTM"))
arcpy.env.snapRaster = dem
arcpy.env.cellSize = dem
CELL = dem.meanCellWidth
priv = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..",
                                     "ce414-private", "grading-oracles"))
dest = os.path.join(priv, "lab09_personal_lookup.csv")
if not os.path.isdir(priv):
    sys.exit(f"private checkout not found: {priv}")


def area_km2(fc):
    return round(sum(r[0] for r in arcpy.da.SearchCursor(fc, ["SHAPE@AREA"])) / 1e6, 3)


def run(dd):
    widen = 3 * dd
    if widen == 0:
        outline = "Butte_Boundary"
    else:
        outline = f"PO_{dd:02d}"
        arcpy.analysis.Buffer("Butte_Boundary", outline, f"{widen} Meters", dissolve_option="ALL")
    ring = f"PR_{dd:02d}"
    arcpy.analysis.Buffer(outline, ring, "1500 Meters", dissolve_option="ALL")
    arcpy.env.randomGenerator = "1 ACM599"
    arcpy.management.CreateRandomPoints(GDB, f"PP_{dd:02d}", ring, "", 1000)
    arcpy.sa.ExtractValuesToPoints(f"PP_{dd:02d}", dem, f"PV_{dd:02d}")
    arcpy.analysis.Erase(f"PV_{dd:02d}", outline, f"PN_{dd:02d}")
    kept = int(arcpy.management.GetCount(f"PN_{dd:02d}")[0])
    surf = Idw(f"PN_{dd:02d}", "RASTERVALU", CELL, 2, RadiusVariable(12))
    b = ExtractByMask(dem, outline)
    p = ExtractByMask(surf, outline)
    h = b - p
    v = h * CELL * CELL / (1000 ** 3)
    z = ZonalStatistics(outline, "OBJECTID", v, "SUM")
    row = dict(last_two_digits=f"{dd:02d}", widen_m=widen, kept=kept, outline_km2=area_km2(outline),
               volume_km3=round(float(z.maximum), 4), tallest_m=round(float(h.maximum), 1),
               lowest_m=round(float(h.minimum), 1), mean_m=round(float(h.mean), 1))
    for name in (f"PP_{dd:02d}", f"PV_{dd:02d}", f"PN_{dd:02d}", ring) + ((outline,) if widen else ()):
        arcpy.management.Delete(name)
    return row


fields = ["last_two_digits", "widen_m", "kept", "outline_km2", "volume_km3", "tallest_m", "lowest_m", "mean_m"]
with open(dest, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for dd in range(100):
        row = run(dd)
        w.writerow(row)
        f.flush()
        print(row, flush=True)
print("written", dest)
