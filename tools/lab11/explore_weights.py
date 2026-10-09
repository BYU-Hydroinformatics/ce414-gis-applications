"""Lab 11 design exploration: which weights actually move the route? Uses run_model.py's factor rasters
in C:\\Ames\\Lab11\\ref\\Ref.gdb (run run_model.py first). Writes explore_weights.json.   ArcGIS Pro Python."""
import json
import os

import arcpy
from arcpy.sa import Con, IsNull, Raster

import run_model as rm

rm.setup()
OUT = {}
for tag, (sw, lw, rw, cw) in {
        "line0": (1, 0, 1, 1), "line0.5": (1, 0.5, 1, 1), "line2": (1, 2, 1, 1),
        "slope5": (5, 1, 1, 1), "road0": (1, 1, 0, 1), "city0": (1, 1, 1, 0),
        "line0_slope2": (2, 0, 1, 1), "line0_slope0": (0, 0, 1, 1)}.items():
    c = (sw * Raster("Slope_Score") + rw * Raster("Road_Score") + cw * Raster("City_Score")
         + lw * Raster("Line_Score") + Con(IsNull("River_Cells"), 0, 10))
    name = f"Cost_x_{tag.replace('.', '_')}"
    c.save(name)
    t = f"x_{tag.replace('.', '_')}"
    ep = os.path.join(rm.SRC, "Endpoints")
    src = arcpy.management.MakeFeatureLayer(ep, f"s{t}", "Role = 'Source'")
    dst = arcpy.management.MakeFeatureLayer(ep, f"d{t}", "Role = 'Destination'")
    rm.DistanceAccumulation(src, in_barrier_data="Major_Lakes", in_cost_raster=name, out_back_direction_raster=f"Back_{t}").save(f"Acc_{t}")
    rm.OptimalPathAsLine(dst, f"Acc_{t}", f"Back_{t}", f"Route_{t}")
    L = sum(r[0] for r in arcpy.da.SearchCursor(f"Route_{t}", ["SHAPE@LENGTH"])) / 1000
    OUT[tag] = {"weights": [sw, lw, rw, cw], "length_km": round(L, 2), "moved": rm.moved(t)}
    print(tag, OUT[tag])
json.dump(OUT, open(os.path.join(rm.HERE, "explore_weights.json"), "w"), indent=1)
