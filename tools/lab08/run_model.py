"""Reference run of the Lab 8 (avalanche terrain) analysis in arcpy, with the check values.

    python run_model.py [shift ...]      (ArcGIS Pro Python; default shifts: 0 -400 -200 200)

Steps, as the draft page has them:
  1. Project Raster: LittleCottonwood_DEM.tif -> NAD 1983 UTM zone 12N, bilinear, 10 m cells.
  2. Slope (degrees) and Aspect.
  3. Reclassify slope and aspect with Table 1; altitude with Table 1 shifted by SHIFT meters
     (Raster Calculator, so the shift can be a model parameter).
  4. Combine: (a) the "all three agree" Con method; (b) the product, 1-125, grouped into five
     classes by its cube root (the geometric mean of the three classes), rounded.
  5. Areas by class inside the Snowbird boundary (UGRC SkiAreaBoundaries, OBJECTID 13).

Writes C:\\Ames\\Lab07\\Check.gdb and tools/lab08/check_values.json.
"""
import json
import os
import sys
import time
import urllib.request

import arcpy
import numpy as np
from arcpy.sa import Aspect, Con, Float, Int, Power, Raster, Reclassify, RemapRange, Slope

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"C:\Ames\Lab07"
DEM = os.path.join(ROOT, "Data", "LittleCottonwood_DEM.tif")
GDB = os.path.join(ROOT, "Check.gdb")
SHIFTS = [float(v) for v in sys.argv[1:]] or [0, -400, -200, 200]
UTM = arcpy.SpatialReference(26912)
BOUNDARY_URL = ("https://services1.arcgis.com/99lidPhWCzftIe9K/arcgis/rest/services/SkiAreaBoundaries/"
                "FeatureServer/0/query?where=OBJECTID+IN+(13,14)&outFields=OBJECTID,NAME&outSR=26912&f=json")

# Table 1 of the lab (from a Sawtooth Avalanche Center advisory). Slope's Low band starts at 0
# (the handout's -1 is the Aspect tool's flat code, not a slope).
SLOPE = [[0, 25, 1], [25, 30, 2], [30, 32, 3], [32, 35, 4], [35, 45, 5], [45, 50, 4], [50, 55, 3], [55, 60, 2], [60, 90, 1]]
ASPECT = [[-1, 45, 5], [45, 90, 4], [90, 135, 3], [135, 180, 2], [180, 225, 1], [225, 270, 2], [270, 315, 3], [315, 360, 4]]
ALT = [2200, 2400, 2600, 2800]          # class 1 below 2,200 m ... class 5 above 2,800 m

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
os.makedirs(ROOT, exist_ok=True)
if not arcpy.Exists(GDB):
    arcpy.management.CreateFileGDB(ROOT, "Check.gdb")
arcpy.env.workspace = GDB

t0 = time.time()
proj = os.path.join(GDB, "DEM_UTM")
arcpy.management.ProjectRaster(DEM, proj, UTM, "BILINEAR", "10")
arcpy.env.snapRaster = proj
arcpy.env.cellSize = proj
arcpy.env.extent = proj
dem = Raster(proj)
slope = Slope(dem, "DEGREE")
slope.save(os.path.join(GDB, "Slope_Deg"))
aspect = Aspect(dem)
aspect.save(os.path.join(GDB, "Aspect_Deg"))
slope_c = Reclassify(slope, "VALUE", RemapRange(SLOPE), "NODATA")
slope_c.save(os.path.join(GDB, "Slope_Class"))
aspect_c = Reclassify(aspect, "VALUE", RemapRange(ASPECT), "NODATA")
aspect_c.save(os.path.join(GDB, "Aspect_Class"))

# Snowbird and Alta boundaries from UGRC, projected
js = json.loads(urllib.request.urlopen(BOUNDARY_URL, timeout=60).read())
bnd = os.path.join(GDB, "SkiAreas")
if arcpy.Exists(bnd):
    arcpy.management.Delete(bnd)
arcpy.management.CreateFeatureclass(GDB, "SkiAreas", "POLYGON", spatial_reference=UTM)
arcpy.management.AddField(bnd, "NAME", "TEXT", field_length=60)
with arcpy.da.InsertCursor(bnd, ["SHAPE@", "NAME"]) as cur:
    for f in js["features"]:
        rings = f["geometry"]["rings"]
        arr = arcpy.Array([arcpy.Array([arcpy.Point(*xy) for xy in ring]) for ring in rings])
        cur.insertRow([arcpy.Polygon(arr, UTM), f["attributes"]["NAME"]])

cell_km2 = (dem.meanCellWidth * dem.meanCellHeight) / 1e6
mask_lyr = arcpy.management.MakeFeatureLayer(bnd, "snowbird", "NAME LIKE 'Snowbird%'")
mask = arcpy.sa.ExtractByMask(Raster(proj) * 0 + 1, mask_lyr)
mask.save(os.path.join(GDB, "Snowbird_Mask"))
m = arcpy.RasterToNumPyArray(mask, arcpy.Point(dem.extent.XMin, dem.extent.YMin), dem.width, dem.height, nodata_to_value=0) > 0


def counts(r, classes=range(0, 6)):
    a = arcpy.RasterToNumPyArray(r, arcpy.Point(dem.extent.XMin, dem.extent.YMin), dem.width, dem.height, nodata_to_value=-9)
    return {int(k): round(float(((a == k) & m).sum() * cell_km2), 3) for k in classes}


out = dict(dem=dict(min=float(dem.minimum), max=float(dem.maximum), cols=dem.width, rows=dem.height, cell=dem.meanCellWidth),
           snowbird_km2=round(float(m.sum() * cell_km2), 3), slope_max=float(Raster(os.path.join(GDB, "Slope_Deg")).maximum),
           slope_classes=counts(slope_c), aspect_classes=counts(aspect_c), runs={})
flat = arcpy.RasterToNumPyArray(aspect, nodata_to_value=-9)
out["flat_cells_total"] = int((flat == -1).sum())

for shift in SHIFTS:
    a1, a2, a3, a4 = (v + shift for v in ALT)
    alt_c = Con(dem <= a1, 1, Con(dem <= a2, 2, Con(dem <= a3, 3, Con(dem <= a4, 4, 5))))
    tag = f"{int(shift):+d}".replace("+", "p").replace("-", "m")
    alt_c.save(os.path.join(GDB, f"Alt_Class_{tag}"))
    agree = Con((alt_c == 1) & (slope_c == 1) & (aspect_c == 1), 1,
                Con((alt_c == 2) & (slope_c == 2) & (aspect_c == 2), 2,
                    Con((alt_c == 3) & (slope_c == 3) & (aspect_c == 3), 3,
                        Con((alt_c == 4) & (slope_c == 4) & (aspect_c == 4), 4,
                            Con((alt_c == 5) & (slope_c == 5) & (aspect_c == 5), 5, 0)))))
    agree.save(os.path.join(GDB, f"Agree_{tag}"))
    product = alt_c * slope_c * aspect_c
    product.save(os.path.join(GDB, f"Product_{tag}"))
    combined = Int(Power(Float(product), 1.0 / 3.0) + 0.5)
    combined.save(os.path.join(GDB, f"Combined_{tag}"))
    pa = arcpy.RasterToNumPyArray(product, nodata_to_value=-9)
    out["runs"][str(int(shift))] = dict(
        alt_classes=counts(alt_c), agree_classes=counts(agree), combined_classes=counts(combined),
        product_min=int(pa[pa > 0].min()), product_max=int(pa.max()),
        product_values=int(len(np.unique(pa[pa > 0]))))
    print(shift, out["runs"][str(int(shift))]["combined_classes"], flush=True)

out["seconds"] = round(time.time() - t0, 1)
json.dump(out, open(os.path.join(HERE, "check_values.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "runs"}, indent=1))
