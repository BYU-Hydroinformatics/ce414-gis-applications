"""Cross-check the Lab 6 check values with arcpy, on the Windows machine with ArcGIS Pro.

NOT TESTED: written on a Mac without arcpy. Run it in the ArcGIS Pro Python environment
(Python Command Prompt, or the Python window in Pro), fix what breaks, and record the fixes.

It does in arcpy what the student's ModelBuilder model does, for the default run, and writes
arcgis_check_values.csv to compare with data/instructor/powell_check_values.csv:

  python verify_in_arcgis.py <package_dir> [surface]   surface = 30m (default) | 10m
"""
import csv
import os
import sys
import time

import arcpy
from arcpy.sa import Con, Raster

PKG = sys.argv[1]
WHICH = sys.argv[2] if len(sys.argv) > 2 else "30m"
STUDENT = os.path.join(PKG, "data", "student")
SURF = os.path.join(STUDENT, "powell_tbdem_30m.tif" if WHICH == "30m" else "powell_wahweap_10m.tif")
SEED = os.path.join(STUDENT, "main_pool_seed.shp")
WORK = os.path.join(PKG, "arcgis_work")
os.makedirs(WORK, exist_ok=True)
GDB = os.path.join(WORK, "verify_%s.gdb" % WHICH)
if not arcpy.Exists(GDB):
    arcpy.management.CreateFileGDB(WORK, os.path.basename(GDB))

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = GDB
arcpy.env.snapRaster = SURF
arcpy.env.cellSize = SURF
arcpy.env.extent = SURF
arcpy.env.outputCoordinateSystem = arcpy.Describe(SURF).spatialReference

# Step 1: meters NAVD88 -> feet NGVD29
ft = (Raster(SURF) / 0.3048) - 2.91
ft.save(os.path.join(GDB, "surface_ft"))
print("surface_ft min/max:", ft.minimum, ft.maximum)

rows = []
for elev in range(3500, 3701, 10):
    t0 = time.time()
    wet = Con(ft <= elev, 1)                                          # Step 3
    wet_poly = os.path.join(GDB, "wet_%d" % elev)
    arcpy.conversion.RasterToPolygon(wet, wet_poly, "NO_SIMPLIFY", "Value",
                                     "SINGLE_OUTER_PART")              # Step 4a
    n_poly = int(arcpy.management.GetCount(wet_poly)[0])
    lyr = arcpy.management.MakeFeatureLayer(wet_poly, "wet_lyr_%d" % elev)
    arcpy.management.SelectLayerByLocation(lyr, "INTERSECT", SEED)   # Step 4b
    pool = os.path.join(GDB, "pool_%d" % elev)
    arcpy.management.CopyFeatures(lyr, pool)                          # Step 4c
    arcpy.management.AddField(pool, "Elevation", "LONG")              # Step 5
    arcpy.management.CalculateField(pool, "Elevation", str(elev))
    arcpy.management.AddField(pool, "AreaSqMi", "DOUBLE")
    arcpy.management.CalculateField(pool, "AreaSqMi", "!shape.area@squaremiles!", "PYTHON3")
    area = sum(r[0] for r in arcpy.da.SearchCursor(pool, ["AreaSqMi"]))
    n_pool = int(arcpy.management.GetCount(pool)[0])
    rows.append({"elevation_ft_ngvd29": elev, "wet_polygons": n_poly, "pool_polygons": n_pool,
                 "pool_sqmi": round(area, 2), "seconds": round(time.time() - t0, 1)})
    print(rows[-1])

pools = [os.path.join(GDB, "pool_%d" % e) for e in range(3500, 3701, 10)]
arcpy.management.Merge(pools, os.path.join(GDB, "shorelines_3500_3700_10"))  # Step 6
print("merged rows:", arcpy.management.GetCount(os.path.join(GDB, "shorelines_3500_3700_10"))[0])

with open(os.path.join(WORK, "arcgis_check_values_%s.csv" % WHICH), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print("Compare with data/instructor/powell_check_values.csv (main_pool_sqmi_4conn / _8conn).")
