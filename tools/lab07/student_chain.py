"""Lab 7 (HAND): reproduce what a student's iteration model produces, with vector tools.

For each design return period: Con(HAND <= h) -> Raster to Polygon (default: simplify) ->
area; Buildings that INTERSECT the flood polygons (Select Layer By Location) and footprints whose
centroid is inside. For the 100-yr: polygon CSI against FEMA's riverine 1% zone clipped to the
500 m comparison domain (the layer the package hosts):
    CSI = A(both) / (A(HAND) + A(FEMA) - A(both))   with HAND clipped to the same domain.
Also Fill - DEM along the river cells (where the bare-earth DEM dams the channel).
Writes student_chain.json. Usage: student_chain.py [tag] [cell]
"""
import csv
import json
import os
import sys

import arcpy
import numpy as np
from arcpy.sa import Con, Raster

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
HERE = os.path.dirname(os.path.abspath(__file__))
G = r"C:\Ames\HAND\HAND.gdb"
W = r"C:\Ames\HAND\work"
tag = sys.argv[1] if len(sys.argv) > 1 else "lidar_5m_T0.05_C30"
cell = float(sys.argv[2]) if len(sys.argv) > 2 else 5
d = os.path.join(W, tag)
out_gdb = os.path.join(W, f"{tag}.gdb")
if not arcpy.Exists(out_gdb):
    arcpy.management.CreateFileGDB(W, f"{tag}.gdb")
rows = [r for r in csv.DictReader(open(os.path.join(HERE, "stage_table.csv"))) if r["design"] == "True"]
hand = Raster(os.path.join(d, "hand.tif"))
dom = os.path.join(G, "Domain_500m")
fema_dom = os.path.join(G, "FEMA_Riverine_1pct_dom")
if not arcpy.Exists(fema_dom):
    arcpy.analysis.Clip(os.path.join(G, "FEMA_Riverine_1pct"), dom, fema_dom)
A_fema = sum(r[0] for r in arcpy.da.SearchCursor(fema_dom, ["SHAPE@AREA"]))
blay = arcpy.management.MakeFeatureLayer(os.path.join(G, "Buildings"), "bl")
res = {"tag": tag, "fema_dom_km2": round(A_fema / 1e6, 4), "rows": []}
for r in rows:
    h = float(r["hand_h_m"])
    cm = int(round(h * 100))
    ras = Con(hand <= h, 1)
    poly = os.path.join(out_gdb, f"flood_{cm}")
    arcpy.conversion.RasterToPolygon(ras, poly, "SIMPLIFY", "Value")
    area = sum(x[0] for x in arcpy.da.SearchCursor(poly, ["SHAPE@AREA"]))
    npoly = int(arcpy.management.GetCount(poly)[0])
    arcpy.management.SelectLayerByLocation(blay, "INTERSECT", poly)
    n_int = int(arcpy.management.GetCount(blay)[0])
    arcpy.management.SelectLayerByLocation(blay, "HAVE_THEIR_CENTER_IN", poly)
    n_ctr = int(arcpy.management.GetCount(blay)[0])
    arcpy.management.SelectLayerByAttribute(blay, "CLEAR_SELECTION")
    row = {"return_period_yr": int(r["return_period_yr"]), "h_m": h, "H_CM": cm, "polygons": npoly,
           "area_km2": round(area / 1e6, 4), "buildings_intersect": n_int, "buildings_center_in": n_ctr}
    if int(r["return_period_yr"]) == 100 or True:
        hd = os.path.join("memory", "hd")
        arcpy.analysis.Clip(poly, dom, hd)
        both = os.path.join("memory", "both")
        arcpy.analysis.PairwiseIntersect([hd, fema_dom], both)
        a_h = sum(x[0] for x in arcpy.da.SearchCursor(hd, ["SHAPE@AREA"]))
        a_b = sum(x[0] for x in arcpy.da.SearchCursor(both, ["SHAPE@AREA"]))
        row.update(hand_dom_km2=round(a_h / 1e6, 4), both_km2=round(a_b / 1e6, 4),
                   hit_rate=round(a_b / A_fema, 3), csi=round(a_b / (a_h + A_fema - a_b), 3))
    res["rows"].append(row)
    print(row)
# Fill - DEM on the river cells
if os.path.exists(os.path.join(d, "fill.tif")):
    fill = Raster(os.path.join(d, "fill.tif"))
    ext = fill.extent
    f = arcpy.RasterToNumPyArray(fill, nodata_to_value=np.nan)
    dem = arcpy.RasterToNumPyArray(os.path.join(W, f"dem_lidar_{int(cell)}m.tif"), ext.lowerLeft, fill.width, fill.height, nodata_to_value=np.nan)
    rv = arcpy.RasterToNumPyArray(os.path.join(d, "river.tif"), ext.lowerLeft, fill.width, fill.height, nodata_to_value=0) > 0
    diff = (f - dem)[rv]
    big = np.argwhere(rv & ((f - dem) > 0.5))
    res["fill_minus_dem_river"] = {"cells": int(rv.sum()), "filled_cells": int((diff > 0.01).sum()),
                                   "over_0p5m": int((diff > 0.5).sum()), "max_m": float(np.nanmax(diff)),
                                   "mean_m": float(np.nanmean(diff))}
    whole = f - dem
    res["fill_minus_dem_all"] = {"filled_cells": int((whole > 0.01).sum()),
                                 "filled_km2": round(float((whole > 0.01).sum()) * cell * cell / 1e6, 3),
                                 "max_m": float(np.nanmax(whole))}
    if big.size:
        ys = ext.YMax - (big[:, 0] + 0.5) * cell
        xs = ext.XMin + (big[:, 1] + 0.5) * cell
        res["river_fill_spots_sample"] = [[round(float(x)), round(float(y))] for x, y in zip(xs[::max(1, len(xs) // 10)], ys[::max(1, len(ys) // 10)])]
    print(res.get("fill_minus_dem_river"), res.get("fill_minus_dem_all"))
json.dump(res, open(os.path.join(HERE, "student_chain.json"), "w"), indent=1)
