"""Lab 7 / Week 8 lecture figure numbers: a 'bathtub' flood (one water-surface elevation for the
whole box, the 100-yr stage elevation at the gage) versus HAND at the same stage.
Bathtub = DEM <= elevation, (a) everywhere and (b) only cells connected to the gage's river cell.
Writes bathtub.json. Run after run_model.py (default run).
"""
import csv
import json
import os

import arcpy
import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
DEM = r"C:\Ames\HAND\work\dem_lidar_2m.tif"
HAND = r"C:\Ames\HAND\work\lidar_2m_T0.05_C30\hand.tif"
GAGE = (439504.805, 4454555.338)
rows = [r for r in csv.DictReader(open(os.path.join(HERE, "stage_table.csv"))) if r["design"] == "True"]
r = arcpy.Raster(DEM)
ext = r.extent
dem = arcpy.RasterToNumPyArray(r, nodata_to_value=np.nan)
hand = arcpy.RasterToNumPyArray(HAND, ext.lowerLeft, r.width, r.height, nodata_to_value=-9999)
gr, gc = int((ext.YMax - GAGE[1]) / 2), int((GAGE[0] - ext.XMin) / 2)
# the gage sits on the bank; use the lowest cell within 30 m as the seed
w = dem[gr - 15:gr + 16, gc - 15:gc + 16]
k = np.nanargmin(w)
seed = (gr - 15 + k // w.shape[1], gc - 15 + k % w.shape[1])
out = {"seed_elev_m": float(dem[seed]), "rows": []}
for s in rows:
    z = float(s["elev_m_navd88"])
    h = float(s["hand_h_m"])
    tub = dem <= z
    lab, _ = ndimage.label(tub, structure=np.ones((3, 3)))
    conn = lab == lab[seed] if tub[seed] else np.zeros_like(tub)
    hd = (hand > -9999) & (hand <= h)
    # how far upstream (north) does each reach?
    def ymax(mask):
        rr = np.nonzero(mask.any(axis=1))[0]
        return float(ext.YMax - rr.min() * 2) if rr.size else None
    out["rows"].append({"return_period_yr": int(s["return_period_yr"]), "elev_m": z, "h_m": h,
                        "bathtub_km2": round(tub.sum() * 4 / 1e6, 3),
                        "bathtub_connected_km2": round(conn.sum() * 4 / 1e6, 3),
                        "hand_km2": round(hd.sum() * 4 / 1e6, 3),
                        "bathtub_connected_north_m": ymax(conn), "hand_north_m": ymax(hd)})
    print(out["rows"][-1])
out["gage_y"] = GAGE[1]
json.dump(out, open(os.path.join(HERE, "bathtub.json"), "w"), indent=1)
