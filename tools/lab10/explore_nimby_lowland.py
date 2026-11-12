"""Follow-up to explore_nimby.py: a heavy city score alone sends Lab 10's route east over the Wasatch,
never west of Utah Lake. Does it go west once the mountains are closed? Cost as in explore_nimby.py
(slope, road and line weights 1, city weight varied), with every cell above MAX_ELEV set to NoData so
it acts as a barrier like the lakes. Writes explore_nimby_lowland.json.   ArcGIS Pro Python (propy.bat).
"""
import json
import os

import arcpy
from arcpy.sa import Raster, SetNull

import run_model as rm

rm.setup()
lake = max((r[0] for r in arcpy.da.SearchCursor("Major_Lakes", ["SHAPE@"])), key=lambda g: g.area)
cx, cy = lake.centroid.X, lake.centroid.Y


def side(g):
    pts = [g.positionAlongLine(k).firstPoint for k in range(0, int(g.length), 30)]
    near = min(pts, key=lambda p: abs(p.Y - cy))
    return "west" if near.X < cx else "east"


OUT = {}
ep = os.path.join(rm.SRC, "Endpoints")
for max_elev in (1700, 1800, 2000):
    for cw in (1, 3, 5, 10, 20):
        tag = f"low{max_elev}_city{cw}"
        c = Raster("Slope_Score") + Raster("Road_Score") + cw * Raster("City_Score") + Raster("Line_Score")
        SetNull(Raster(rm.DEM) > max_elev, c).save(f"Cost_{tag}")
        src = arcpy.management.MakeFeatureLayer(ep, f"s_{tag}", "Role = 'Source'")
        dst = arcpy.management.MakeFeatureLayer(ep, f"d_{tag}", "Role = 'Destination'")
        rm.DistanceAccumulation(src, in_barrier_data="Major_Lakes", in_cost_raster=f"Cost_{tag}",
                                out_back_direction_raster=f"Back_{tag}").save(f"Acc_{tag}")
        rm.OptimalPathAsLine(dst, f"Acc_{tag}", f"Back_{tag}", f"Route_{tag}")
        g = [r[0] for r in arcpy.da.SearchCursor(f"Route_{tag}", ["SHAPE@"])][0]
        OUT[tag] = {"max_elev_m": max_elev, "city_weight": cw, "length_km": round(g.length / 1000, 2),
                    "side": side(g), "moved": rm.moved(tag)}
        print(tag, OUT[tag], flush=True)
json.dump(OUT, open(os.path.join(rm.HERE, "explore_nimby_lowland.json"), "w"), indent=1)
