"""Compare the GUI build's outputs (C:\\Ames\\Lab11GUI\\Lab11.gdb) with check_values.json.
    python check_gui.py [GDB]            ArcGIS Pro Python."""
import json
import os
import sys

import arcpy
from arcpy.sa import Raster

arcpy.CheckOutExtension("Spatial")
G = sys.argv[1] if len(sys.argv) > 1 else r"C:\Ames\Lab11GUI\Lab11.gdb"
CK = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "check_values.json")))
arcpy.env.workspace = G
print("rasters", sorted(arcpy.ListRasters()))
print("features", sorted(arcpy.ListFeatureClasses()))


def n(fc):
    return int(arcpy.management.GetCount(fc)[0])


for fc in ("Major_Roads", "Major_Lakes", "Major_Streams", "Existing_Lines"):
    if arcpy.Exists(fc):
        print(fc, n(fc), "expected", CK[fc])
for r in ("Slope_Degrees", "Road_Distance", "City_Distance", "Line_Distance", "Cost_Surface", "Accumulated_Cost"):
    if arcpy.Exists(r):
        x = Raster(r)
        print(r, x.width, x.height, round(x.minimum, 2), round(x.maximum, 2), round(x.mean, 4))
for r in ("Slope_Score", "Road_Score", "City_Score", "Line_Score", "River_Cells"):
    if arcpy.Exists(r):
        print(r, {int(v): int(c) for v, c in arcpy.da.SearchCursor(r, ["VALUE", "COUNT"])})
for fc in ("Route",) + tuple(sys.argv[2:]):
    if arcpy.Exists(fc):
        L = sum(row[0] for row in arcpy.da.SearchCursor(fc, ["SHAPE@LENGTH"])) / 1000
        print(fc, round(L, 2), "km; expected base", CK["base"]["length_km"])
print("expected base", CK["base"])
