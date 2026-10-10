r"""Lab 11 reference run: the page's model in arcpy, on the hosted package only.

    python run_model.py               baseline + step checks + sensitivity runs -> check_values.json
    python run_model.py personal      the personal-parameter sweep -> ../../../ce414-private/grading-oracles/lab11_personal_lookup.csv
                                      (private repo; falls back to personal_lookup.csv here, which is git-ignored)

The model (one ModelBuilder model on the page):
  Select   Major_Roads = Roads where DOT_FCLASS IN ('Interstate', 'Other Freeway', 'Principal Arterial')
           Major_Lakes = Lakes where AreaSqKm > 1
           Major_Streams = Streams where IsMajor = 1
           Existing_Lines = Power_Lines where LAYER LIKE 'KV-%'
  Slope (degrees) of Elevation.tif, and three straight-line distance rasters made with Distance
  Accumulation (no cost raster): to Major_Roads, Cities, Existing_Lines
  Reclassify each to a 1-10 score (SCORES below); Polyline to Raster the major streams (crossing cells)
  Raster Calculator:  Cost = %Slope_Weight% * Slope_Score + Road_Score + City_Score
                             + %Line_Weight% * Line_Score + Con(IsNull(River_Cells), 0, 10)
  Distance Accumulation from the Source, cost = Cost, barrier = Major_Lakes -> accumulation, back direction
  Optimal Path As Line to the Destination -> Route
Environments: extent, snap raster and cell size = Elevation.tif (30 m), output NAD 1983 UTM 12N.
ArcGIS Pro Python (3.7.1).
"""
import csv
import json
import math
import os
import sys
import zipfile

import arcpy
from arcpy.sa import (Con, DistanceAccumulation, IsNull, OptimalPathAsLine, Raster, Reclassify,
                      RemapRange, Slope)

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
HERE = os.path.dirname(os.path.abspath(__file__))


def private_path(here, name):
    """Grading oracles belong in the private companion repo (../ce414-private/grading-oracles/).
    If that checkout is absent, write beside the script; the public .gitignore keeps it out of git."""
    priv = os.path.normpath(os.path.join(here, "..", "..", "..", "ce414-private", "grading-oracles"))
    return os.path.join(priv, name) if os.path.isdir(priv) else os.path.join(here, name.split("_", 1)[1])
ZIP = os.path.join(HERE, "..", "..", "docs", "data", "lab11-power-line.zip")
ROOT = r"C:\Ames\Lab11\ref"
DATA = os.path.join(ROOT, "lab11-power-line")
SRC = os.path.join(DATA, "PowerLineData.gdb")
DEM = os.path.join(DATA, "Elevation.tif")
G = os.path.join(ROOT, "Ref.gdb")
BIG = 1e9
SCORES = {
    "slope": [[0, 5, 1], [5, 10, 2], [10, 15, 4], [15, 20, 6], [20, 30, 8], [30, 90, 10]],          # degrees
    "road": [[0, 1000, 1], [1000, 2000, 3], [2000, 5000, 6], [5000, BIG, 10]],                     # m to a major road
    "city": [[0, 1000, 10], [1000, 2000, 8], [2000, 3000, 6], [3000, 4000, 4], [4000, 5000, 2], [5000, BIG, 1]],
    "line": [[0, 500, 1], [500, 2000, 5], [2000, BIG, 10]],                                        # m to an existing kV line
}
DEFAULTS = {"slope_weight": 1.0, "line_weight": 1.0}
CROSSING = 10


def setup():
    if not os.path.exists(DATA):
        os.makedirs(ROOT, exist_ok=True)
        zipfile.ZipFile(ZIP).extractall(ROOT)
    if not arcpy.Exists(G):
        arcpy.management.CreateFileGDB(ROOT, "Ref.gdb")
    arcpy.env.workspace = G
    arcpy.env.extent = arcpy.env.snapRaster = arcpy.env.cellSize = DEM
    arcpy.env.outputCoordinateSystem = arcpy.Describe(DEM).spatialReference


def count(fc):
    return int(arcpy.management.GetCount(fc)[0])


def stats(r):
    r = Raster(r) if isinstance(r, str) else r
    arcpy.management.CalculateStatistics(r)
    return {"min": float(r.minimum), "max": float(r.maximum), "mean": round(float(r.mean), 4)}


def class_counts(r):
    out = {}
    for v, c in arcpy.da.SearchCursor(r, ["VALUE", "COUNT"]):
        out[int(v)] = int(c)
    return out


def build_factors(ck):
    s = lambda n: os.path.join(SRC, n)
    for out, fc, where in (("Major_Roads", "Roads", "DOT_FCLASS IN ('Interstate', 'Other Freeway', 'Principal Arterial')"),
                           ("Major_Lakes", "Lakes", "AreaSqKm > 1"),
                           ("Major_Streams", "Streams", "IsMajor = 1"),
                           ("Existing_Lines", "Power_Lines", "LAYER LIKE 'KV-%'")):
        arcpy.analysis.Select(s(fc), out, where)
        ck[out] = count(out)
    ck["inputs"] = {n: count(s(n)) for n in ("Roads", "Lakes", "Streams", "Cities", "Power_Lines", "Endpoints")}
    d = Raster(DEM)
    ck["dem"] = {"cols": d.width, "rows": d.height, "cell": d.meanCellWidth, "min": float(d.minimum), "max": float(d.maximum)}
    sl = Slope(DEM, "DEGREE"); sl.save("Slope_Degrees")
    ck["slope"] = stats("Slope_Degrees")
    for name, fc in (("Road_Distance", "Major_Roads"), ("City_Distance", s("Cities")), ("Line_Distance", "Existing_Lines")):
        DistanceAccumulation(fc).save(name)
        ck[name] = stats(name)
    for key, src, out in (("slope", "Slope_Degrees", "Slope_Score"), ("road", "Road_Distance", "Road_Score"),
                          ("city", "City_Distance", "City_Score"), ("line", "Line_Distance", "Line_Score")):
        Reclassify(src, "VALUE", RemapRange(SCORES[key]), "NODATA").save(out)
        ck[out] = class_counts(out)
    arcpy.management.AddField("Major_Streams", "One", "SHORT")
    arcpy.management.CalculateField("Major_Streams", "One", "1")
    arcpy.conversion.PolylineToRaster("Major_Streams", "One", "River_Cells", "MAXIMUM_LENGTH", cellsize=DEM)
    ck["River_Cells"] = sum(class_counts("River_Cells").values())


_ARR = {}


def score_arrays():
    """The three score rasters as arrays, read once, and a (x, y) -> (row, col) function."""
    if not _ARR:
        import numpy as np
        d = arcpy.Describe(DEM)
        for n in ("Road_Score", "Line_Score", "City_Score"):
            _ARR[n] = arcpy.RasterToNumPyArray(n, arcpy.Point(d.extent.XMin, d.extent.YMin), d.width, d.height, -1)
        cs = d.meanCellWidth
        x0, y1 = d.extent.XMin, d.extent.YMax
        _ARR["cell"] = lambda x, y: (min(int((y1 - y) // cs), d.height - 1), min(int((x - x0) // cs), d.width - 1))
    return _ARR


def cost_surface(slope_w, line_w, name):
    c = (slope_w * Raster("Slope_Score") + Raster("Road_Score") + Raster("City_Score") + line_w * Raster("Line_Score")
         + Con(IsNull("River_Cells"), 0, CROSSING))
    c.save(name)
    return name


def route(tag, slope_w, line_w, barrier=True):
    cost = cost_surface(slope_w, line_w, f"Cost_{tag}")
    ep = os.path.join(SRC, "Endpoints")
    src = arcpy.management.MakeFeatureLayer(ep, f"src_{tag}", "Role = 'Source'")
    dst = arcpy.management.MakeFeatureLayer(ep, f"dst_{tag}", "Role = 'Destination'")
    acc = DistanceAccumulation(src, in_barrier_data="Major_Lakes" if barrier else None, in_cost_raster=cost,
                               out_back_direction_raster=f"Back_{tag}")
    acc.save(f"Acc_{tag}")
    OptimalPathAsLine(dst, f"Acc_{tag}", f"Back_{tag}", f"Route_{tag}")
    g = [r[0] for r in arcpy.da.SearchCursor(f"Route_{tag}", ["SHAPE@"])]
    line = g[0]
    for x in g[1:]:
        line = line.union(x)
    dx, dy = [r[0] for r in arcpy.da.SearchCursor(dst, ["SHAPE@XY"])][0]
    total = float(arcpy.management.GetCellValue(f"Acc_{tag}", f"{dx} {dy}").getOutput(0))
    # river crossings: points where the route meets a major stream
    arcpy.analysis.PairwiseIntersect([f"Route_{tag}", "Major_Streams"], f"X_{tag}", "ALL", None, "POINT")
    xs = arcpy.management.MultipartToSinglepart(f"X_{tag}", f"Xs_{tag}")
    pts = {(round(r[0][0] / 30), round(r[0][1] / 30)) for r in arcpy.da.SearchCursor(xs, ["SHAPE@XY"])}
    # share of the route near a road / an existing line: sample every 30 m on the scores
    L = line.length
    n = int(L // 30)
    road1 = line1 = city10 = 0
    A = score_arrays()
    for k in range(n + 1):
        p = line.positionAlongLine(k * 30).firstPoint
        i, j = A["cell"](p.X, p.Y)
        road1 += A["Road_Score"][i, j] == 1
        line1 += A["Line_Score"][i, j] == 1
        city10 += A["City_Score"][i, j] == 10
    return {"length_km": round(L / 1000, 2), "total_cost": round(total, 1), "river_crossings": len(pts),
            "pct_within_1km_road": round(100 * road1 / (n + 1), 1),
            "pct_within_500m_line": round(100 * line1 / (n + 1), 1),
            "pct_city_score_10": round(100 * city10 / (n + 1), 1),
            "slope_weight": slope_w, "line_weight": line_w, "barrier": barrier}


def moved(tag, base="base"):
    """How far a run's route is from the baseline's: sample every 100 m."""
    bl = [r[0] for r in arcpy.da.SearchCursor(f"Route_{base}", ["SHAPE@"])][0]
    rt = [r[0] for r in arcpy.da.SearchCursor(f"Route_{tag}", ["SHAPE@"])][0]
    d = sorted(bl.distanceTo(rt.positionAlongLine(k)) for k in range(0, int(rt.length), 100))
    return {"median_m": round(d[len(d) // 2]), "max_m": round(d[-1]),
            "pct_within_300m": round(100 * sum(x <= 300 for x in d) / len(d), 1)}


def main():
    setup()
    ck = {}
    build_factors(ck)
    ep = os.path.join(SRC, "Endpoints")
    xy = {r[0]: r[1] for r in arcpy.da.SearchCursor(ep, ["Role", "SHAPE@XY"])}
    ck["straight_km"] = round(math.dist(xy["Source"], xy["Destination"]) / 1000, 2)
    ck["base"] = route("base", DEFAULTS["slope_weight"], DEFAULTS["line_weight"])
    c = Raster("Cost_base"); ck["Cost_base"] = stats(c)
    ck["Acc_base"] = stats("Acc_base")
    print("base", ck["base"])
    runs = {"line0": (1, 0, True), "line0_5": (1, 0.5, True), "line2": (1, 2, True),
            "slope0": (0, 1, True), "slope5": (5, 1, True), "nobarrier": (1, 1, False)}
    ck["sensitivity"] = {}
    for tag, (w, x, b) in runs.items():
        r = route(tag, w, x, b)
        r["moved"] = moved(tag)
        ck["sensitivity"][tag] = r
        print(tag, r)
    json.dump(ck, open(os.path.join(HERE, "check_values.json"), "w"), indent=1)


def personal():
    """Line weight from the last two digits of the BYU ID: 0.005 x digits (0 to 0.495), the range where the
    route responds (the pilot found weights above about 0.6 stay within 300 m of the baseline)."""
    setup()
    rows = []
    for d in range(100):
        w = round(0.005 * d, 3)
        r = route(f"p{d:02d}", DEFAULTS["slope_weight"], w)
        rows.append({"digits": f"{d:02d}", "line_weight": w, **{k: r[k] for k in ("length_km", "total_cost", "river_crossings")}})
        print(rows[-1])
        for n in (f"Cost_p{d:02d}", f"Acc_p{d:02d}", f"Back_p{d:02d}"):
            arcpy.management.Delete(n)
    with open(private_path(HERE, "lab11_personal_lookup.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    personal() if len(sys.argv) > 1 and sys.argv[1] == "personal" else main()
