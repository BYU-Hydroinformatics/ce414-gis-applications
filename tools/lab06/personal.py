"""Lab 6 (Lake Depth Explorer): the personal water-surface elevation, for every possible last two
digits (00-99) of the nine-digit BYU ID number. Grading lookup table ->
../../../ce414-private/grading-oracles/lab06_personal_lookup.csv (private repo; falls back to
personal_lookup.csv here, which is git-ignored).

Rule (Step 7 of the page):
  E = 3,500 + 2 * dd  ft NGVD29                   (3,500 to 3,698: inside the default range)
  run the model with From = To = E (any step), i.e. one level, on the 30 m surface
  report: the main-pool area at E in square miles to 0.01, and the main pool's shoreline length at E
          (Shape_Length in the attribute table, meters) in km to 0.1

Same arithmetic as run_model.py (which reproduced the Mac key exactly on 2026-10-01): convert the
surface to ft NGVD29, Con(ft <= E, 1), Raster to Polygon (no simplify, single part), keep the
polygon that intersects the seed, area in square miles. Run with the ArcGIS Pro Python.
"""
import csv
import os
import sys
import time

import arcpy
from arcpy.sa import Con, Raster

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
HERE = os.path.dirname(os.path.abspath(__file__))


def private_path(here, name):
    priv = os.path.normpath(os.path.join(here, "..", "..", "..", "ce414-private", "grading-oracles"))
    return os.path.join(priv, name) if os.path.isdir(priv) else os.path.join(here, name.split("_", 1)[1])


def find(name):
    for d in (r"C:\Ames\Lab06GUI", r"C:\Ames\Pilot06\data", r"C:\Ames\Lab06Pkg\CE414_Lab06_Package\data",
              r"C:\Ames\Lab06Pkg\CE414_Lab06_Package"):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


SURF = find("powell_tbdem_30m.tif")
SEED = find("main_pool_seed.shp")
GDB = r"C:\Ames\Lab06\Check.gdb"
arcpy.env.workspace = GDB
for k in ("snapRaster", "cellSize", "extent"):
    setattr(arcpy.env, k, SURF)
arcpy.env.outputCoordinateSystem = arcpy.Describe(SURF).spatialReference
ft_path = os.path.join(GDB, "surface_ft_30m")
if not arcpy.Exists(ft_path):
    ((Raster(SURF) / 0.3048) - 2.91).save(ft_path)
ft = Raster(ft_path)

OUT = private_path(HERE, "lab06_personal_lookup.csv")
digits = [f"{d:02d}" for d in range(100)]
if len(sys.argv) > 1:                       # a quick subset for checking, e.g. personal.py 00 37 99
    digits = [f"{int(a):02d}" for a in sys.argv[1:]]
rows = []
t_all = time.time()
for dd in digits:
    e = 3500 + 2 * int(dd)
    t0 = time.time()
    wet = Con(ft <= e, 1)
    wp = os.path.join("memory", f"wet_{dd}")
    arcpy.conversion.RasterToPolygon(wet, wp, "NO_SIMPLIFY", "Value", "SINGLE_OUTER_PART")
    n_poly = int(arcpy.management.GetCount(wp)[0])
    lyr = arcpy.management.MakeFeatureLayer(wp, f"lyr_{dd}")
    arcpy.management.SelectLayerByLocation(lyr, "INTERSECT", SEED)
    geoms = [r[0] for r in arcpy.da.SearchCursor(lyr, ["SHAPE@"])]
    area = sum(g.area for g in geoms) / 2589988.110336          # m2 -> sq mi
    length = sum(g.length for g in geoms) / 1000.0              # m -> km (the attribute table's Shape_Length, in meters)
    n_sel = len(geoms)
    arcpy.management.Delete(lyr); arcpy.management.Delete(wp)
    rows.append(dict(last_two_digits=dd, elevation_ft=e, pool_sqmi=round(area, 2), shoreline_km=round(length, 1),
                     shoreline_m=round(length * 1000), water_bodies=n_poly, main_pool_polygons=n_sel,
                     seconds=round(time.time() - t0, 1)))
    print(rows[-1], flush=True)
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print("wrote", OUT, len(rows), "rows in", round(time.time() - t_all), "s")
