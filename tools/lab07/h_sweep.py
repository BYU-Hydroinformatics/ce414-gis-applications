"""Lab 7 (HAND): CSI against FEMA's riverine 1% zone as a function of the HAND threshold h,
with and without a connectivity filter (keep only flooded regions that touch the river cells).
Uses the default run's rasters in C:/Ames/HAND/work/<tag>/. Writes h_sweep.json.
"""
import json
import os
import sys

import arcpy
import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
W = r"C:\Ames\HAND\work"
tag = sys.argv[1] if len(sys.argv) > 1 else "lidar_2m_T0.05_C100"
cell = int(sys.argv[2]) if len(sys.argv) > 2 else 2
r = arcpy.Raster(os.path.join(W, tag, "hand.tif"))
ext = r.extent
hand = arcpy.RasterToNumPyArray(r, nodata_to_value=-9999)
fema = arcpy.RasterToNumPyArray(os.path.join(W, f"fema_{cell}m.tif"), ext.lowerLeft, r.width, r.height, nodata_to_value=0) > 0
dom = arcpy.RasterToNumPyArray(os.path.join(W, f"dom_{cell}m.tif"), ext.lowerLeft, r.width, r.height, nodata_to_value=0) > 0
river = hand == 0  # stream cells have HAND 0


def score(wet):
    h = (wet & fema & dom).sum(); m = (~wet & fema & dom).sum(); f = (wet & ~fema & dom).sum()
    return {"hit_rate": round(h / (h + m), 3), "far": round(f / (h + f), 3), "csi": round(h / (h + m + f), 3),
            "area_km2": round(wet.sum() * cell * cell / 1e6, 3)}


out = []
for h in np.round(np.arange(0.25, 2.51, 0.25), 2).tolist() + [0.408, 0.664, 0.827, 1.028, 1.174, 1.319, 1.789]:
    wet = (hand > -9999) & (hand <= h)
    lab, n = ndimage.label(wet, structure=np.ones((3, 3)))
    keep = np.unique(lab[river & wet])
    conn = np.isin(lab, keep[keep > 0])
    row = {"h_m": h, "raw": score(wet), "connected": score(conn)}
    out.append(row)
    print(row)
json.dump({"tag": tag, "rows": out}, open(os.path.join(HERE, f"h_sweep_{tag}.json"), "w"), indent=1)
