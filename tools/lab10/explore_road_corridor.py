"""Lab 10 design exploration (November 11, 2026): the pre-2026 handout kept the route inside a road
corridor: every cell more than 2 km from a major road was NoData, a hard barrier ("Reclassify values to
either 1 or NODATA"). Does that, with the handout's product form, send the route west of Utah Lake?

  old:      Elevation (raw meters) * Corridor * City_Score**city_w * Line_Score
  current:  Slope_Score + Road_Score + city_w * City_Score + Line_Score, inside the same corridor

Corridor = 1 within 2 km of a major road (Lab 10's Major_Roads), NoData beyond. City weights 1, 5, 10.
Lakes are barriers as in run_model.py (run that first). Writes explore_road_corridor.json.
ArcGIS Pro Python (propy.bat).
"""
import json
import os

import arcpy
from arcpy.sa import Power, Raster, SetNull

import run_model as rm

rm.setup()
lake = max((r[0] for r in arcpy.da.SearchCursor("Major_Lakes", ["SHAPE@"])), key=lambda g: g.area)
cx, cy = lake.centroid.X, lake.centroid.Y


def side(g):
    pts = [g.positionAlongLine(k).firstPoint for k in range(0, int(g.length), 30)]
    near = min(pts, key=lambda p: abs(p.Y - cy))
    return "west" if near.X < cx else "east"


SetNull(Raster("Road_Distance") > 2000, 1).save("Road_Corridor")
OUT = {}
ep = os.path.join(rm.SRC, "Endpoints")
for form in ("old", "current"):
    for cw in (1, 5, 10):
        tag = f"corr_{form}_city{cw}"
        if form == "old":
            c = Raster(rm.DEM) * Raster("Road_Corridor") * Power(Raster("City_Score"), cw) * Raster("Line_Score")
        else:
            c = Raster("Road_Corridor") * (Raster("Slope_Score") + Raster("Road_Score") + cw * Raster("City_Score")
                                           + Raster("Line_Score"))
        c.save(f"Cost_{tag}")
        src = arcpy.management.MakeFeatureLayer(ep, f"s_{tag}", "Role = 'Source'")
        dst = arcpy.management.MakeFeatureLayer(ep, f"d_{tag}", "Role = 'Destination'")
        rm.DistanceAccumulation(src, in_barrier_data="Major_Lakes", in_cost_raster=f"Cost_{tag}",
                                out_back_direction_raster=f"Back_{tag}").save(f"Acc_{tag}")
        rm.OptimalPathAsLine(dst, f"Acc_{tag}", f"Back_{tag}", f"Route_{tag}")
        g = [r[0] for r in arcpy.da.SearchCursor(f"Route_{tag}", ["SHAPE@"])][0]
        OUT[tag] = {"form": form, "city_weight": cw, "length_km": round(g.length / 1000, 2),
                    "side": side(g), "moved": rm.moved(tag)}
        print(tag, OUT[tag], flush=True)
json.dump(OUT, open(os.path.join(rm.HERE, "explore_road_corridor.json"), "w"), indent=1)
