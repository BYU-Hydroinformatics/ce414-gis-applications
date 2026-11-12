"""Lab 10 design exploration for the Week 11 NIMBY slide (and the Fall 2027 lab): how heavy must the
city score be before the route leaves the cities on the east side of Utah Lake and goes around the
west side? Cost = slope_w * Slope_Score + Road_Score + city_w * City_Score + Line_Score, lakes as barriers,
everything else as in run_model.py (run that first: it builds the scores and Route_base in
C:\\Ames\\Lab10\\ref\\Ref.gdb). Writes explore_nimby.json.   ArcGIS Pro Python (propy.bat).
"""
import json
import os

import arcpy
from arcpy.sa import Raster

import run_model as rm

rm.setup()

# Utah Lake: the largest of the barrier lakes. A route is "west" if, at the lake's middle latitude,
# it lies west of the lake's centroid.
lake = max((r[0] for r in arcpy.da.SearchCursor("Major_Lakes", ["SHAPE@"])), key=lambda g: g.area)
cx, cy = lake.centroid.X, lake.centroid.Y


def side(tag):
    g = [r[0] for r in arcpy.da.SearchCursor(f"Route_{tag}", ["SHAPE@"])][0]
    pts = [g.positionAlongLine(k).firstPoint for k in range(0, int(g.length), 30)]
    near = min(pts, key=lambda p: abs(p.Y - cy))
    return "west" if near.X < cx else "east"


OUT = {"base_side": side("base")}
ep = os.path.join(rm.SRC, "Endpoints")
# (slope weight, city weight): first the city weight alone, then with slope heavier too, since a heavy
# city score alone sends the route over the Wasatch, east, where slope at weight 1 is cheap.
RUNS = ([(1, w) for w in (2, 3, 4, 5, 6, 8, 10, 15, 20)]
        + [(s, w) for s in (3, 5, 10) for w in (5, 10, 20)]
        + [(30, 20), (100, 20), (30, 50), (100, 100)])
for sw, cw in RUNS:
    tag = f"city{cw}" if sw == 1 else f"slope{sw}_city{cw}"
    c = (sw * Raster("Slope_Score") + Raster("Road_Score") + cw * Raster("City_Score") + Raster("Line_Score"))
    c.save(f"Cost_{tag}")
    src = arcpy.management.MakeFeatureLayer(ep, f"s_{tag}", "Role = 'Source'")
    dst = arcpy.management.MakeFeatureLayer(ep, f"d_{tag}", "Role = 'Destination'")
    rm.DistanceAccumulation(src, in_barrier_data="Major_Lakes", in_cost_raster=f"Cost_{tag}",
                            out_back_direction_raster=f"Back_{tag}").save(f"Acc_{tag}")
    rm.OptimalPathAsLine(dst, f"Acc_{tag}", f"Back_{tag}", f"Route_{tag}")
    g = [r[0] for r in arcpy.da.SearchCursor(f"Route_{tag}", ["SHAPE@"])][0]
    # share of the route in or within 1 km of a city (city score 10), and near an existing line
    A = rm.score_arrays()
    n = int(g.length // 30); c10 = l1 = 0
    for k in range(n + 1):
        p = g.positionAlongLine(k * 30).firstPoint
        i, j = A["cell"](p.X, p.Y)
        c10 += A["City_Score"][i, j] == 10
        l1 += A["Line_Score"][i, j] == 1
    OUT[tag] = {"slope_weight": sw, "city_weight": cw, "length_km": round(g.length / 1000, 2), "side": side(tag),
                "pct_city_score_10": float(round(100 * c10 / (n + 1), 1)),
                "pct_within_500m_line": float(round(100 * l1 / (n + 1), 1)), "moved": rm.moved(tag)}
    print(tag, OUT[tag], flush=True)
json.dump(OUT, open(os.path.join(rm.HERE, "explore_nimby.json"), "w"), indent=1)
