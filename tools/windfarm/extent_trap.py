"""Lab 10 probe: what happens when the distance sources lie outside the processing extent?

All turbines near the six counties are outside them (USWTDB has none inside). Run after
probe_model.py has built C:\\Ames\\Lab10\\probe_100m.gdb.
"""
import json, os
import numpy as np
import arcpy
from arcpy import sa

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Ames\Lab10\probe_100m.gdb"
arcpy.env.cellSize = 100
arcpy.env.snapRaster = "Study_Grid"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extent_trap.json")
study = arcpy.Describe("Study_Grid").extent
ctx = arcpy.Describe("Context").extent
res = {}

def summary(r):
    a = arcpy.RasterToNumPyArray(sa.ExtractByMask(r, "Study_Grid"), nodata_to_value=np.nan).astype(float)
    g = arcpy.RasterToNumPyArray("Study_Grid", nodata_to_value=0) > 0
    v = a[g]
    return {"valid_cells_in_area": int(np.isfinite(v).sum()), "area_cells": int(g.sum()),
            "min": None if not np.isfinite(v).any() else round(float(np.nanmin(v)), 1),
            "max": None if not np.isfinite(v).any() else round(float(np.nanmax(v)), 1)}

for label, ext, mask in [("extent=study,mask=study", study, "Study_Grid"),
                         ("extent=study,no mask", study, None),
                         ("extent=context(20mi buffer),no mask", ctx, None)]:
    with arcpy.EnvManager(extent=ext, mask=mask):
        for tool in ["DistanceAccumulation", "EucDistance"]:
            try:
                r = getattr(sa, tool)("Turbines")
                r.save("trap_%s" % tool)
                res["%s | %s" % (tool, label)] = summary(r)
            except Exception as e:
                res["%s | %s" % (tool, label)] = "ERROR " + str(e).splitlines()[0]
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
