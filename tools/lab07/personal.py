"""Lab 7 (HAND): the personal design flow, for every possible last two digits (00-99) of the
nine-digit BYU ID number. Grading lookup table -> personal_lookup.csv (and the summary into
package_checks.json['personal_summary']).

Rule (Step 7 of the page):
  Q = 900 + 12 * dd  ft3/s                       (900 to 2,088: always inside the rating table)
  gage height = the FIRST row of rating_10163000.csv whose discharge is >= Q
  h = (gage height - 3.20) * 0.3048, in meters, rounded to 3 decimals (millimeters)
  flood = Con("HAND" <= h, 1) -> Raster to Polygon (no simplify, multipart) -> Spatial Join with
          Buildings (one to one, intersect) -> Join_Count ; area from the polygon
Run after verify_package.py (uses C:/Ames/HAND/PkgCheck/Work.gdb/HAND, built from the zip).
"""
import csv
import json
import os

import arcpy
import numpy as np
from arcpy.sa import Con, Raster

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
HERE = os.path.dirname(os.path.abspath(__file__))
PC = r"C:\Ames\HAND\PkgCheck"
P = os.path.join(PC, "lab07-provo-river-hand")
G = os.path.join(P, "ProvoData.gdb")
WG = os.path.join(PC, "Work.gdb")


def main():
    rating = [(float(r["gage_height_ft"]), float(r["discharge_cfs"]))
              for r in csv.DictReader(open(os.path.join(P, "rating_10163000.csv")))]
    hp = os.path.join(WG, "HAND")
    hand = arcpy.RasterToNumPyArray(hp, nodata_to_value=-9999)
    valid = hand > -9999
    cache, rows = {}, []
    for dd in range(100):
        q = 900 + 12 * dd
        gh = next(g for g, d in rating if d >= q)
        h = round((gh - 3.20) * 0.3048, 3)
        if h not in cache:
            with arcpy.EnvManager(extent=hp, snapRaster=hp, cellSize=hp):
                Con(Raster(hp) <= h, 1).save(os.path.join(WG, "pers"))
            pp = os.path.join(WG, "pers_poly")
            arcpy.conversion.RasterToPolygon(os.path.join(WG, "pers"), pp, "NO_SIMPLIFY", "Value", "MULTIPLE_OUTER_PART")
            sj = os.path.join(WG, "pers_sj")
            arcpy.analysis.SpatialJoin(pp, os.path.join(G, "Buildings"), sj, "JOIN_ONE_TO_ONE", "KEEP_ALL",
                                       match_option="INTERSECT")
            jc, a = [x for x in arcpy.da.SearchCursor(sj, ["Join_Count", "SHAPE@AREA"])][0]
            cache[h] = (int((valid & (hand <= h)).sum()), round(a / 1e6, 4), int(jc))
        cells, area, b = cache[h]
        rows.append({"last_two_digits": f"{dd:02d}", "q_cfs": q, "gage_height_ft": gh, "h_m": h,
                     "wet_cells": cells, "area_km2": area, "buildings": b})
    with open(os.path.join(HERE, "personal_lookup.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    summ = {"distinct_h": len({r["h_m"] for r in rows}), "distinct_area": len({r["area_km2"] for r in rows}),
            "distinct_buildings": len({r["buildings"] for r in rows}),
            "examples": [rows[89], rows[2], rows[0], rows[99]]}
    c = json.load(open(os.path.join(HERE, "package_checks.json")))
    c["personal_summary"] = summ
    json.dump(c, open(os.path.join(HERE, "package_checks.json"), "w"), indent=1, default=float)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
