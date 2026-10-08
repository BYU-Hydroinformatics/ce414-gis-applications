r"""Reproduce Lab 9's check values from the hosted zip alone, the way the page builds the model:
environments Cell Size 30, Snap Raster and Extent True_DEM; Thiessen (polygons -> Polygon to Raster),
IDW (power 2, 12 points), Kriging (ordinary spherical, 12 points); error, square, Zonal Statistics as
Table MEAN over Study_Area, sqrt. Runs all three hosted point sets, and with --seed the Step 7 personal
point set (Create Random Points 2,500 + Extract Values to Points) and its two parameter runs.
Writes tools/lab09/package_checks.json.   ArcGIS Pro Python.
"""
import argparse, json, math, os, shutil, zipfile
import arcpy
import numpy as np
from arcpy.sa import Idw, Kriging, KrigingModelOrdinary, RadiusVariable, Raster, Square, ZonalStatisticsAsTable

HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = os.path.join(HERE, "..", "..", "docs", "data", "lab09-y-mountain.zip")
ROOT = r"C:\Ames\Lab09\ZipCheck"
ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int); a = ap.parse_args()

if os.path.exists(ROOT):
    shutil.rmtree(ROOT)
zipfile.ZipFile(ZIP).extractall(ROOT)
GDB = os.path.join(ROOT, "lab09-y-mountain", "Lab09.gdb")
arcpy.CheckOutExtension("Spatial"); arcpy.env.overwriteOutput = True; arcpy.env.workspace = GDB
TRUE = os.path.join(GDB, "True_DEM")
arcpy.env.cellSize = 30; arcpy.env.snapRaster = TRUE; arcpy.env.extent = TRUE


def stats(r):
    v = arcpy.RasterToNumPyArray(Raster(r) if isinstance(r, str) else r, nodata_to_value=np.nan)
    return dict(cells=int(np.isfinite(v).sum()), min=round(float(np.nanmin(v)), 1), max=round(float(np.nanmax(v)), 1),
                mean=round(float(np.nanmean(v)), 2))


def rmse(surf, tag):
    err = Raster(TRUE) - surf
    ZonalStatisticsAsTable("Study_Area", "OBJECTID", Square(err), f"ZS_{tag}", "DATA", "MEAN")
    c, area, m = next(arcpy.da.SearchCursor(f"ZS_{tag}", ["COUNT", "AREA", "MEAN"]))
    return dict(rmse=round(math.sqrt(m), 2), mean_sq=round(m, 1), count=int(c), area=round(area), error=stats(err),
                surface=stats(surf))


def run(pts, tag, power=2, model="SPHERICAL"):
    arcpy.analysis.CreateThiessenPolygons(pts, f"TP_{tag}", "ALL")
    arcpy.conversion.PolygonToRaster(f"TP_{tag}", "RASTERVALU", f"TH_{tag}", "CELL_CENTER", "", 30)
    out = dict(Thiessen=rmse(Raster(f"TH_{tag}"), f"th_{tag}"),
               IDW=rmse(Idw(pts, "RASTERVALU", 30, power, RadiusVariable(12)), f"idw_{tag}"),
               Kriging=rmse(Kriging(pts, "RASTERVALU", KrigingModelOrdinary(model), 30, RadiusVariable(12)), f"kr_{tag}"))
    print(tag, {k: v["rmse"] for k, v in out.items()}, flush=True)
    return out


res = dict(true_dem=stats(TRUE))
for n in (250, 2500, 10000):
    fc = f"Sample_Points_{n}"
    v = [r[0] for r in arcpy.da.SearchCursor(fc, ["RASTERVALU"])]
    first = next(arcpy.da.SearchCursor(fc, ["SHAPE@X", "SHAPE@Y"], sql_clause=(None, "ORDER BY OBJECTID")))
    res[fc] = dict(n=len(v), min=round(min(v), 1), max=round(max(v), 1), first=[round(first[0], 1), round(first[1], 1)],
                   fields=[f.name for f in arcpy.ListFields(fc)], runs=run(fc, f"n{n}"))
if a.seed is not None:
    arcpy.env.randomGenerator = f"{a.seed} ACM599"
    arcpy.management.CreateRandomPoints(GDB, "My_Random", "Study_Area", "", 2500)
    arcpy.sa.ExtractValuesToPoints("My_Random", TRUE, "My_Points")
    res["personal"] = {"seed": a.seed, "baseline": run("My_Points", "my"),
                       "IDW 1 / exponential": run("My_Points", "my_a", 1, "EXPONENTIAL"),
                       "IDW 3 / Gaussian": run("My_Points", "my_b", 3, "GAUSSIAN")}
json.dump(res, open(os.path.join(HERE, "package_checks.json"), "w"), indent=1)
print(json.dumps({k: (v if k == "true_dem" else {kk: vv for kk, vv in v.items() if kk != "runs"}) for k, v in res.items() if k != "personal"}, indent=1))
