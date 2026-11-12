"""Lab 10 design exploration (November 11, 2026): does an elevation term, as in the pre-2026 handout,
push the route around the west side of Utah Lake? Two forms, each at city weights 1, 5 and 10:

  sum:     Elev_Score + Road_Score + city_w * City_Score + Line_Score, where Elev_Score bands the DEM,
           lower = cheaper (the bands are a test choice, not from any handout: < 1,450 m: 1;
           1,450-1,550: 2; 1,550-1,650: 4; 1,650-1,800: 6; 1,800-2,000: 8; > 2,000: 10)
  product: Elevation (raw meters) * Road_Score * City_Score**city_w * Line_Score, the old handout's
           "multiply the reclassified rasters together" with the raw DEM as the multiplier
           (city_w as an exponent, since a weight in a product is a power)

Lakes are barriers as in run_model.py (run that first). Writes explore_elevation.json.
ArcGIS Pro Python (propy.bat).
"""
import json
import os

import arcpy
from arcpy.sa import Power, Raster, Reclassify, RemapRange

import run_model as rm

rm.setup()
lake = max((r[0] for r in arcpy.da.SearchCursor("Major_Lakes", ["SHAPE@"])), key=lambda g: g.area)
cx, cy = lake.centroid.X, lake.centroid.Y
BANDS = [[0, 1450, 1], [1450, 1550, 2], [1550, 1650, 4], [1650, 1800, 6], [1800, 2000, 8], [2000, 9000, 10]]


def side(g):
    pts = [g.positionAlongLine(k).firstPoint for k in range(0, int(g.length), 30)]
    near = min(pts, key=lambda p: abs(p.Y - cy))
    return "west" if near.X < cx else "east"


Reclassify(rm.DEM, "Value", RemapRange(BANDS)).save("Elev_Score")
OUT = {"bands": BANDS}
ep = os.path.join(rm.SRC, "Endpoints")
for form in ("sum", "product"):
    for cw in (1, 5, 10):
        tag = f"elev_{form}_city{cw}"
        if form == "sum":
            c = Raster("Elev_Score") + Raster("Road_Score") + cw * Raster("City_Score") + Raster("Line_Score")
        else:
            c = Raster(rm.DEM) * Raster("Road_Score") * Power(Raster("City_Score"), cw) * Raster("Line_Score")
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
json.dump(OUT, open(os.path.join(rm.HERE, "explore_elevation.json"), "w"), indent=1)
