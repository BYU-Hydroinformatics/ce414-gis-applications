"""Lab 6 (Lake Depth Explorer): the personal run, for every possible last two digits (00-99) of the
nine-digit BYU ID number. Grading lookup table ->
../../../ce414-private/grading-oracles/lab06_personal_lookup.csv (private repo; falls back to
personal_lookup.csv here, which is git-ignored).

Rule (Step 7 of the page, Oct 13 2026 version):
  E = 3,450 + 2 * dd  ft NGVD29                   (3,450 to 3,648)
  Run 2: From Value = E, To Value = E + 40, By Value = 10  -> five levels E, E+10, ..., E+40
  report: the attribute table of that run: Elevation, AreaSqMi (0.01) and Shape_Length (meters)

The 100 runs share levels (every even foot from 3,450 to 3,688, 120 distinct), so each level is
computed once. Same arithmetic as run_model.py (reproduced the Mac key exactly on 2026-10-01):
convert the surface to ft NGVD29, Con(ft <= E, 1), Raster to Polygon (no simplify, single part),
keep the polygon that intersects the seed, area in square miles. Run with the ArcGIS Pro Python.
"""
import csv
import os
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
    for d in (r"C:\Ames\Lab06GUI", r"C:\Ames\Pilot06\data", r"C:\Ames\Lab06Pkg\CE414_Lab06_Package\data\student",
              r"C:\Ames\Lab06Pkg\CE414_Lab06_Package\data"):
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

levels = {}
t_all = time.time()
for e in range(3450, 3690, 2):
    t0 = time.time()
    wet = Con(ft <= e, 1)
    wp = os.path.join("memory", f"wet_{e}")
    arcpy.conversion.RasterToPolygon(wet, wp, "NO_SIMPLIFY", "Value", "SINGLE_OUTER_PART")
    n_poly = int(arcpy.management.GetCount(wp)[0])
    lyr = arcpy.management.MakeFeatureLayer(wp, f"lyr_{e}")
    arcpy.management.SelectLayerByLocation(lyr, "INTERSECT", SEED)
    geoms = [r[0] for r in arcpy.da.SearchCursor(lyr, ["SHAPE@"])]
    area = sum(g.area for g in geoms) / 2589988.110336
    length = sum(g.length for g in geoms)
    arcpy.management.Delete(lyr); arcpy.management.Delete(wp)
    levels[e] = dict(pool_sqmi=round(area, 2), shoreline_m=round(length), water_bodies=n_poly, main_pool_polygons=len(geoms))
    print(e, levels[e], round(time.time() - t0, 1), "s", flush=True)

OUT = private_path(HERE, "lab06_personal_lookup.csv")
with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["last_two_digits", "E_ft", "level_ft", "pool_sqmi", "shoreline_m", "water_bodies", "main_pool_polygons"])
    for dd in range(100):
        E = 3450 + 2 * dd
        for lv in range(E, E + 41, 10):
            r = levels[lv]
            w.writerow([f"{dd:02d}", E, lv, r["pool_sqmi"], r["shoreline_m"], r["water_bodies"], r["main_pool_polygons"]])
print("wrote", OUT, "in", round(time.time() - t_all), "s")
