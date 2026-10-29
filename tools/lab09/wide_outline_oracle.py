"""Lab 9 Step 9 oracle for the Week 10 cut (October 28, 2026): the two Step 9 runs as a student's
model produces them, with seed 1. Run 1 is 250 points on the reference outline; Run 2 is 1,000
points on Butte_Boundary_Wide, the reference outline buffered by 200 m. Unlike run_model.py's
outline rows, the sampling ring is rebuilt from the new outline, as the student's model does.

Writes ../ce414-private/sensitivity/lab09_step9_oracle.json (never public).
Needs DEM_UTM and Butte_Boundary in C:\\Ames\\Lab08\\Check.gdb. Run with propy.bat.
"""
import json
import os

import arcpy
from arcpy.sa import ExtractByMask, Idw, RadiusVariable, Raster, ZonalStatistics

GDB = r"C:\Ames\Lab08\Check.gdb"
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = GDB
dem = Raster(os.path.join(GDB, "DEM_UTM"))
arcpy.env.snapRaster = dem
arcpy.env.cellSize = dem
CELL = dem.meanCellWidth


def area_km2(fc):
    return round(sum(r[0] for r in arcpy.da.SearchCursor(fc, ["SHAPE@AREA"])) / 1e6, 3)


def run(outline, n, tag):
    ring = f"PB_{tag}"
    arcpy.analysis.Buffer(outline, ring, "1500 Meters", dissolve_option="ALL")
    arcpy.env.randomGenerator = "1 ACM599"
    arcpy.management.CreateRandomPoints(GDB, f"RP_{tag}", ring, "", n)
    arcpy.sa.ExtractValuesToPoints(f"RP_{tag}", dem, f"PV_{tag}")
    arcpy.analysis.Erase(f"PV_{tag}", outline, f"NB_{tag}")
    kept = int(arcpy.management.GetCount(f"NB_{tag}")[0])
    vals = [r[0] for r in arcpy.da.SearchCursor(f"NB_{tag}", ["RASTERVALU"])]
    surf = Idw(f"NB_{tag}", "RASTERVALU", CELL, 2, RadiusVariable(12))
    b = ExtractByMask(dem, outline)
    p = ExtractByMask(surf, outline)
    h = b - p
    h.save(os.path.join(GDB, f"H_{tag}"))
    v = h * CELL * CELL / (1000 ** 3)
    z = ZonalStatistics(outline, "OBJECTID", v, "SUM")
    return dict(outline=outline, points=n, kept=kept, ring_km2=area_km2(ring),
                outline_km2=area_km2(outline), plain_rv_min=round(min(vals), 1),
                plain_rv_max=round(max(vals), 1), plain_rv_mean=round(sum(vals) / len(vals), 1),
                tallest_m=round(float(h.maximum), 1), mean_m=round(float(h.mean), 1),
                volume_km3=round(float(z.maximum), 4))


arcpy.analysis.Buffer("Butte_Boundary", "Butte_Boundary_Wide", "200 Meters", dissolve_option="ALL")
out = {"baseline_1000": run("Butte_Boundary", 1000, "b1000"),
       "run1_250": run("Butte_Boundary", 250, "b250"),
       "run2_wide_1000": run("Butte_Boundary_Wide", 1000, "w1000")}
priv = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..",
                                     "ce414-private", "sensitivity"))
dest = os.path.join(priv, "lab09_step9_oracle.json")
json.dump(out, open(dest, "w"), indent=1)
print(json.dumps(out, indent=1))
print("written", dest)
