"""Run Lab 6's analysis in arcpy for any range and step, and record the check values.

The same steps as the student's ModelBuilder model (Steps 1 and 3-6): convert the surface to ft
NGVD29, flood it with Con, Raster to Polygon (no simplify, single part), keep the polygon that
intersects the seed, label it with Elevation and AreaSqMi, and merge. Grown from the Mac package's
verify_in_arcgis.py, which ran unchanged on 2026-10-01 and reproduced the Mac check values exactly
(every level, 3,500-3,700 by 10, to 0.01 sq mi; polygon counts identical).

    python run_model.py <data_dir> <surface: 30m|10m> <low> <high> <step> [tag]

Writes C:\\Ames\\Lab06\\Check.gdb\\shorelines_<tag> and appends one row per run to
tools/lab06/runs.csv (low, high, step, shorelines, area at low and high, seconds), and one row per
level to tools/lab06/levels_<tag>.csv. Run with the ArcGIS Pro Python.
"""
import csv
import os
import sys
import time

import arcpy
from arcpy.sa import Con, Raster

DATA, WHICH = sys.argv[1], sys.argv[2]
LOW, HIGH, STEP = (float(v) for v in sys.argv[3:6])
TAG = sys.argv[6] if len(sys.argv) > 6 else f"{WHICH}_{LOW:g}_{HIGH:g}_{STEP:g}"
HERE = os.path.dirname(os.path.abspath(__file__))
SURF = os.path.join(DATA, "powell_tbdem_30m.tif" if WHICH == "30m" else "powell_wahweap_10m.tif")
SEED = os.path.join(DATA, "main_pool_seed.shp")
ROOT = r"C:\Ames\Lab06"
GDB = os.path.join(ROOT, "Check.gdb")
os.makedirs(ROOT, exist_ok=True)
if not arcpy.Exists(GDB):
    arcpy.management.CreateFileGDB(ROOT, "Check.gdb")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = GDB
for k in ("snapRaster", "cellSize", "extent"):
    setattr(arcpy.env, k, SURF)
arcpy.env.outputCoordinateSystem = arcpy.Describe(SURF).spatialReference

ft_path = os.path.join(GDB, f"surface_ft_{WHICH}")
if not arcpy.Exists(ft_path):
    ((Raster(SURF) / 0.3048) - 2.91).save(ft_path)
ft = Raster(ft_path)

levels, e = [], LOW
while e <= HIGH + 1e-9:          # the For iterator includes the To value (VERIFY in ArcGIS Pro)
    levels.append(round(e, 3)); e += STEP
t_run = time.time()
rows, pools = [], []
for elev in levels:
    t0 = time.time()
    name = str(elev).replace(".", "_")
    wet = Con(ft <= elev, 1)
    wet_cells = int(arcpy.management.GetRasterProperties(wet, "UNIQUEVALUECOUNT").getOutput(0)) if False else None
    wp = os.path.join("memory", f"wet_{name}")
    arcpy.conversion.RasterToPolygon(wet, wp, "NO_SIMPLIFY", "Value", "SINGLE_OUTER_PART")
    n_poly = int(arcpy.management.GetCount(wp)[0])
    lyr = arcpy.management.MakeFeatureLayer(wp, f"lyr_{name}")
    arcpy.management.SelectLayerByLocation(lyr, "INTERSECT", SEED)
    pool = os.path.join(GDB, f"pool_{TAG}_{name}")
    arcpy.management.CopyFeatures(lyr, pool)
    arcpy.management.AddField(pool, "Elevation", "DOUBLE")
    arcpy.management.CalculateField(pool, "Elevation", str(elev))
    arcpy.management.AddField(pool, "AreaSqMi", "DOUBLE")
    arcpy.management.CalculateField(pool, "AreaSqMi", "!shape.area@squaremiles!", "PYTHON3")
    area = sum(r[0] for r in arcpy.da.SearchCursor(pool, ["AreaSqMi"]))
    arcpy.management.Delete(wp)
    rows.append(dict(elevation_ft=elev, wet_polygons=n_poly, pool_sqmi=round(area, 2), seconds=round(time.time() - t0, 1)))
    pools.append(pool)
    print(rows[-1], flush=True)
out = os.path.join(GDB, f"shorelines_{TAG}")
arcpy.management.Merge(pools, out)
for pl in pools:
    arcpy.management.Delete(pl)
total = round(time.time() - t_run, 1)
n = int(arcpy.management.GetCount(out)[0])
with open(os.path.join(HERE, f"levels_{TAG}.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
new = not os.path.exists(os.path.join(HERE, "runs.csv"))
with open(os.path.join(HERE, "runs.csv"), "a", newline="") as f:
    w = csv.writer(f)
    if new:
        w.writerow(["tag", "surface", "low_ft", "high_ft", "step_ft", "shorelines", "area_low_sqmi", "area_high_sqmi", "seconds"])
    w.writerow([TAG, WHICH, LOW, HIGH, STEP, n, rows[0]["pool_sqmi"], rows[-1]["pool_sqmi"], total])
print("merged", n, "rows into", out, "in", total, "s")
