"""Per-step check values for the Lab 8 page, from the baseline run left in Check.gdb by
run_model.py (RP_base, PV_base, NB_base). Writes tools/lab08/step_checks.json. ArcGIS Pro Python."""
import json
import os

import arcpy
import numpy as np
from arcpy.sa import ExtractByMask, Idw, RadiusVariable, Raster, ZonalStatistics

GDB = r"C:\Ames\Lab08\Check.gdb"
arcpy.CheckOutExtension("Spatial"); arcpy.env.overwriteOutput = True; arcpy.env.workspace = GDB
dem = Raster("DEM_UTM"); arcpy.env.snapRaster = dem; arcpy.env.cellSize = dem
out = {}
out["dem_utm"] = dict(cols=dem.width, rows=dem.height, min=round(dem.minimum, 1), max=round(dem.maximum, 1),
                      cell=dem.meanCellWidth)
area = lambda fc: round(sum(r[0] for r in arcpy.da.SearchCursor(fc, ["SHAPE@AREA"])) / 1e6, 3)
out["butte_km2"] = area("Butte_Boundary"); out["points_boundary_km2"] = area("Points_Boundary")
rv = [r[0] for r in arcpy.da.SearchCursor("PV_base", ["RASTERVALU"])]
out["random_points"] = dict(n=len(rv), min=round(min(rv), 1), max=round(max(rv), 1), mean=round(float(np.mean(rv)), 1))
nb = [r[0] for r in arcpy.da.SearchCursor("NB_base", ["RASTERVALU"])]
out["not_butte"] = dict(n=len(nb), min=round(min(nb), 1), max=round(max(nb), 1), mean=round(float(np.mean(nb)), 1))
first = [r for r in arcpy.da.SearchCursor("RP_base", ["OID@", "SHAPE@X", "SHAPE@Y"])][:3]
out["first_points"] = [[o, round(x, 1), round(y, 1)] for o, x, y in first]
# IDW with the extent the GUI would use by default (the input points' extent), snapped to the DEM
arcpy.env.extent = "MAXOF"
plain = Idw("NB_base", "RASTERVALU", 10, 2, RadiusVariable(12))
out["plain"] = dict(cols=plain.width, rows=plain.height, min=round(plain.minimum, 1), max=round(plain.maximum, 1))
b = ExtractByMask(dem, "Butte_Boundary"); p = ExtractByMask(plain, "Butte_Boundary")
out["dem_butte"] = dict(min=round(b.minimum, 1), max=round(b.maximum, 1), mean=round(b.mean, 1))
out["plain_butte"] = dict(min=round(p.minimum, 1), max=round(p.maximum, 1), mean=round(p.mean, 1))
h = b - p
v = h * 10 * 10 / (1000 ** 3)
out["height"] = dict(min=round(h.minimum, 1), max=round(h.maximum, 1), mean=round(h.mean, 1))
out["volume_cell_max_km3"] = v.maximum
z = ZonalStatistics("Butte_Boundary", "OBJECTID", v, "SUM")
out["volume_km3_default_extent"] = round(z.maximum, 4)
a = arcpy.RasterToNumPyArray(v, nodata_to_value=np.nan)
out["volume_cells"] = int(np.isfinite(a).sum())
json.dump(out, open(os.path.join(os.path.dirname(__file__), "step_checks.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
