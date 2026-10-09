"""Lab 7 (HAND): default traps for Flow Distance, measured on the 5 m package DEM.
  A. stream raster with 0 (not NoData) off-stream: Con(acc > T, 1, 0)
  B. surface = raw DEM instead of the filled DEM
  C. no flow direction raster given (tool derives its own)
  D. no corridor mask (every Con stream is a drainage)
Writes gotchas.json.
"""
import json
import os

import arcpy
import numpy as np
from arcpy.sa import Con, ExtractByMask, Fill, FlowAccumulation, FlowDirection, FlowDistance, Raster

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
HERE = os.path.dirname(os.path.abspath(__file__))
P = r"C:\Ames\HAND\PkgCheck\lab07-provo-river-hand"
dem = Raster(os.path.join(P, "Provo_DEM.tif"))
corr = r"C:\Ames\HAND\PkgCheck\Work.gdb\River_Corridor"
H100 = 1.789


def stats(r, label):
    a = arcpy.RasterToNumPyArray(r, nodata_to_value=-9999)
    v = a > -9999
    s = {"case": label, "cells": int(v.sum()), "min": float(a[v].min()), "max": float(a[v].max()),
         "negative_cells": int((v & (a < 0)).sum()), "wet_100yr_km2": round(float((v & (a <= H100)).sum()) * 25 / 1e6, 4)}
    print(s)
    return s


out = []
with arcpy.EnvManager(snapRaster=dem, extent=dem, cellSize=dem, scratchWorkspace=r"C:\Ames\HAND\PkgCheck\Work.gdb"):
    fill = Fill(dem)
    fdr = FlowDirection(fill, "NORMAL", "#", "D8")
    acc = FlowAccumulation(fdr, "#", "FLOAT", "D8")
    river = ExtractByMask(Con(acc > 2000, 1), corr)
    out.append(stats(FlowDistance(river, fill, fdr, "VERTICAL", "D8", "MINIMUM"), "reference"))
    try:
        r0 = ExtractByMask(Con(acc > 2000, 1, 0), corr)
        out.append(stats(FlowDistance(r0, fill, fdr, "VERTICAL", "D8", "MINIMUM"), "A: 0 off-stream inside corridor, NoData outside"))
        r00 = Con(acc > 2000, 1, 0)
        out.append(stats(FlowDistance(r00, fill, fdr, "VERTICAL", "D8", "MINIMUM"), "A2: 0 everywhere off-stream, no mask"))
    except Exception as e:
        out.append({"case": "A", "error": str(e)})
    out.append(stats(FlowDistance(river, dem, fdr, "VERTICAL", "D8", "MINIMUM"), "B: raw DEM as surface"))
    try:
        out.append(stats(FlowDistance(river, fill), "C: no flow direction raster"))
    except Exception as e:
        out.append({"case": "C", "error": str(e)})
    out.append(stats(FlowDistance(Con(acc > 2000, 1), fill, fdr, "VERTICAL", "D8", "MINIMUM"), "D: no corridor mask"))
json.dump(out, open(os.path.join(HERE, "gotchas.json"), "w"), indent=1)
