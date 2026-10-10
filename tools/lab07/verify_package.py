"""Lab 7 (HAND): reproduce every check value on the student page from the hosted zip ALONE,
following the page's tool settings. Writes package_checks.json (then run personal.py for the private grading lookup).

Student path (docs/assignments/lab-07/README.md):
  Step 0  environments: Extent, Snap Raster and Cell Size = Provo_DEM
  Step 2  Fill -> Flow Direction (D8, Normal)
  Step 3  Flow Accumulation -> Raster Calculator Con("Flow_Accumulation" > Threshold, 1)
          -> Buffer Provo_River 30 m (dissolve all) -> Extract by Mask = River_Cells
  Step 4  Flow Distance (VERTICAL, D8, MINIMUM; surface = Filled_DEM, flow direction given) = HAND
  Step 5  loop over Stage_Table.H_CM: Con("HAND" <= H_CM / 100, 1) -> Raster to Polygon
          (no simplify, multipart) -> Calculate Field H_CM -> Merge = Floods
  Step 6  Join Field (RETURN_YR, Q_CFS) ; Spatial Join with Buildings (one to one, intersect)
          -> Join_Count ; 100-yr: Pairwise Clip to Comparison_Area, Pairwise Intersect with
          FEMA_Floodplain_1pct -> hit rate, false-alarm ratio, CSI
  Step 7  personal flow Q = 900 + 12 dd -> first rating row >= Q -> h_cm ; threshold runs
Usage: verify_package.py [zip]   (default docs/data/lab07-provo-river-hand.zip)
"""
import csv
import json
import os
import shutil
import sys
import time
import zipfile

import arcpy
import numpy as np
from arcpy.sa import Con, ExtractByMask, Fill, FlowAccumulation, FlowDirection, FlowDistance, Raster

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ZIP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "docs", "data", "lab07-provo-river-hand.zip")
OUT = r"C:\Ames\HAND\PkgCheck"
P = os.path.join(OUT, "lab07-provo-river-hand")
G = os.path.join(P, "ProvoData.gdb")
FT = 0.3048


def area(fc):
    return sum(r[0] for r in arcpy.da.SearchCursor(fc, ["SHAPE@AREA"]))


def count(fc):
    return int(arcpy.management.GetCount(fc)[0])


def hand_builder(WG, dem, threshold, tag=""):
    """Steps 2-4. Returns dict of check values and the HAND path."""
    with arcpy.EnvManager(extent=dem, snapRaster=dem, cellSize=dem, workspace=WG, scratchWorkspace=WG):
        fill = Fill(dem)
        fill.save(os.path.join(WG, f"Filled_DEM{tag}"))
        fdr = FlowDirection(fill, "NORMAL", "#", "D8")
        fdr.save(os.path.join(WG, f"Flow_Direction{tag}"))
        acc = FlowAccumulation(fdr, "#", "FLOAT", "D8")
        acc.save(os.path.join(WG, f"Flow_Accumulation{tag}"))
        st = Con(Raster(os.path.join(WG, f"Flow_Accumulation{tag}")) > threshold, 1)
        st.save(os.path.join(WG, f"Stream_Cells{tag}"))
        corr = os.path.join(WG, "River_Corridor")
        if not arcpy.Exists(corr):
            arcpy.analysis.Buffer(os.path.join(G, "Provo_River"), corr, "30 Meters", dissolve_option="ALL")
        rv = ExtractByMask(st, corr)
        rv.save(os.path.join(WG, f"River_Cells{tag}"))
        hand = FlowDistance(rv, fill, fdr, "VERTICAL", "D8", "MINIMUM")
        hand.save(os.path.join(WG, f"HAND{tag}"))
    out = {}
    for name in ("Filled_DEM", "Flow_Accumulation", "HAND"):
        r = Raster(os.path.join(WG, f"{name}{tag}"))
        a = arcpy.RasterToNumPyArray(r, nodata_to_value=-9999)
        v = a > -9999
        out[name] = {"min": float(a[v].min()), "max": float(a[v].max()), "mean": float(a[v].mean()),
                     "cells": int(v.sum()), "cols": r.width, "rows": r.height}
    for name in ("Stream_Cells", "River_Cells"):
        a = arcpy.RasterToNumPyArray(os.path.join(WG, f"{name}{tag}"), nodata_to_value=0)
        out[name] = {"cells": int((a > 0).sum())}
    fd = arcpy.RasterToNumPyArray(os.path.join(WG, f"Flow_Direction{tag}"), nodata_to_value=-1)
    out["Flow_Direction"] = {"values": sorted(int(x) for x in np.unique(fd) if x >= 0)}
    fl = arcpy.RasterToNumPyArray(os.path.join(WG, f"Filled_DEM{tag}"), nodata_to_value=np.nan)
    de = arcpy.RasterToNumPyArray(dem, nodata_to_value=np.nan)
    diff = fl - de
    out["fill_raised"] = {"cells": int((diff > 0).sum()), "km2": round(float((diff > 0).sum()) * 25 / 1e6, 3),
                          "max_m": float(np.nanmax(diff))}
    return out, os.path.join(WG, f"HAND{tag}")


def flood_loop(WG, hand_path, rows, tag=""):
    """Steps 5-6 for every Stage_Table row; returns list of per-row results."""
    hand = Raster(hand_path)
    polys = []
    res = []
    for rp, q, cm in rows:
        with arcpy.EnvManager(extent=hand_path, snapRaster=hand_path, cellSize=hand_path, workspace=WG):
            wet = Con(hand <= cm / 100, 1)
            wet.save(os.path.join(WG, f"flood_{cm}{tag}"))
        wa = arcpy.RasterToNumPyArray(os.path.join(WG, f"flood_{cm}{tag}"), nodata_to_value=0)
        poly = os.path.join(WG, f"floodpoly_{cm}{tag}")
        arcpy.conversion.RasterToPolygon(os.path.join(WG, f"flood_{cm}{tag}"), poly, "NO_SIMPLIFY", "Value",
                                         "MULTIPLE_OUTER_PART")
        arcpy.management.CalculateField(poly, "H_CM", str(cm), "PYTHON3", field_type="LONG")
        polys.append(poly)
        res.append({"return_yr": rp, "q_cfs": q, "H_CM": cm, "wet_cells": int((wa > 0).sum())})
    floods = os.path.join(WG, f"Floods{tag}")
    arcpy.management.Merge(polys, floods)
    arcpy.management.JoinField(floods, "H_CM", os.path.join(G, "Stage_Table"), "H_CM", ["RETURN_YR", "Q_CFS"])
    sj = os.path.join(WG, f"Floods_Buildings{tag}")
    arcpy.analysis.SpatialJoin(floods, os.path.join(G, "Buildings"), sj, "JOIN_ONE_TO_ONE", "KEEP_ALL",
                               match_option="INTERSECT")
    got = {int(c): (int(j), a, int(n)) for c, j, a, n in
           arcpy.da.SearchCursor(sj, ["H_CM", "Join_Count", "SHAPE@AREA", "RETURN_YR"])}
    fema = os.path.join(G, "FEMA_Floodplain_1pct")
    A_f = area(fema)
    for r in res:
        j, a, n = got[r["H_CM"]]
        r.update(floods_rows=count(floods), area_km2=round(a / 1e6, 4), buildings=j, joined_return_yr=n)
        clip = os.path.join(WG, f"cmp_{r['H_CM']}{tag}")
        arcpy.analysis.PairwiseClip(os.path.join(WG, f"floodpoly_{r['H_CM']}{tag}"), os.path.join(G, "Comparison_Area"), clip)
        both = os.path.join(WG, f"both_{r['H_CM']}{tag}")
        arcpy.analysis.PairwiseIntersect([clip, fema], both)
        a_h, a_b = area(clip), area(both)
        r.update(hand_in_comparison_km2=round(a_h / 1e6, 4), fema_km2=round(A_f / 1e6, 4),
                 overlap_km2=round(a_b / 1e6, 4), hit_rate=round(a_b / A_f, 3),
                 false_alarm_ratio=round((a_h - a_b) / a_h, 3), csi=round(a_b / (a_h + A_f - a_b), 3))
    return res


def main():
    t0 = time.time()
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    zipfile.ZipFile(ZIP).extractall(OUT)
    arcpy.management.CreateFileGDB(OUT, "Work.gdb")
    WG = os.path.join(OUT, "Work.gdb")
    dem = os.path.join(P, "Provo_DEM.tif")
    d = Raster(dem)
    res = {"zip": os.path.basename(ZIP), "zip_bytes": os.path.getsize(ZIP),
           "dem": {"cols": d.width, "rows": d.height, "cell": d.meanCellWidth, "min": d.minimum, "max": d.maximum,
                   "extent": [d.extent.XMin, d.extent.YMin, d.extent.XMax, d.extent.YMax],
                   "sr": d.spatialReference.name}}
    res["layers"] = {}
    arcpy.env.workspace = G
    for fc in arcpy.ListFeatureClasses() + arcpy.ListTables():
        res["layers"][fc] = count(os.path.join(G, fc))
    res["river_km"] = round(sum(r[0] for r in arcpy.da.SearchCursor(os.path.join(G, "Provo_River"), ["SHAPE@LENGTH"])) / 1000, 2)
    res["gage_xy"] = [list(r[0]) for r in arcpy.da.SearchCursor(os.path.join(G, "Gage"), ["SHAPE@XY"])][0]
    st = [r for r in arcpy.da.SearchCursor(os.path.join(G, "Stage_Table"),
                                            ["RETURN_YR", "Q_CFS", "GAGE_HT_FT", "ELEV_M", "H_M", "H_CM", "RATING"])]
    res["stage_table"] = [dict(zip(["RETURN_YR", "Q_CFS", "GAGE_HT_FT", "ELEV_M", "H_M", "H_CM", "RATING"], r)) for r in st]
    rows = [(r[0], r[1], r[5]) for r in st]
    # the row students verify by hand: 25-year
    rating = [(float(r["gage_height_ft"]), float(r["discharge_cfs"]))
              for r in csv.DictReader(open(os.path.join(P, "rating_10163000.csv")))]
    def stage(q):
        gh = next(g for g, dd in rating if dd >= q)
        h = (gh - 3.20) * FT
        return gh, round(h, 3), int(round(h * 100))
    gh, h, cm = stage(1810)
    res["verify_row_25yr"] = {"q": 1810, "gage_height_ft": gh, "elev_ft": round(4493.22 + gh, 2),
                              "elev_m": round((4493.22 + gh) * FT, 3), "h_ft": round(gh - 3.20, 2), "h_m": h, "h_cm": cm}
    # Steps 2-4 at the default threshold
    res["hand_default"], hp = hand_builder(WG, dem, 2000)
    print(json.dumps(res["hand_default"]))
    res["floods_default"] = flood_loop(WG, hp, rows)
    for r in res["floods_default"]:
        print(r)
    # Step 7: personal flows
    hand = arcpy.RasterToNumPyArray(hp, nodata_to_value=-9999)
    valid = hand > -9999
    pers = []
    cache = {}
    for dd in range(100):
        q = 900 + 12 * dd
        g, hh, c = stage(q)
        if c not in cache:
            wet = Con(Raster(hp) <= c / 100, 1)
            wet.save(os.path.join(WG, "pers"))
            pp = os.path.join(WG, "pers_poly")
            arcpy.conversion.RasterToPolygon(os.path.join(WG, "pers"), pp, "NO_SIMPLIFY", "Value", "MULTIPLE_OUTER_PART")
            sj = os.path.join(WG, "pers_sj")
            arcpy.analysis.SpatialJoin(pp, os.path.join(G, "Buildings"), sj, "JOIN_ONE_TO_ONE", "KEEP_ALL",
                                       match_option="INTERSECT")
            jc = [x[0] for x in arcpy.da.SearchCursor(sj, ["Join_Count"])][0]
            cache[c] = (int((valid & (hand <= c / 100)).sum()), round(area(pp) / 1e6, 4), int(jc))
        cells, a, b = cache[c]
        pers.append({"last_two_digits": f"{dd:02d}", "q_cfs": q, "gage_height_ft": g, "h_m": hh, "h_cm": c,
                     "wet_cells": cells, "area_km2": a, "buildings": b})
    res["personal_summary_cm"] = {"distinct_h_cm": len(set(p["h_cm"] for p in pers)),
                               "distinct_area": len(set(p["area_km2"] for p in pers)),
                               "distinct_buildings": len(set(p["buildings"] for p in pers))}
    # NOTE: this quick pass rounds h to whole centimeters; the page uses h to the millimeter, and the
    # the grading lookup is written by personal.py into the private ce414-private repo (run it after this script).
    print(res["personal_summary_cm"], pers[0], pers[89], pers[2])
    # Step 7: stream-threshold runs
    res["threshold_runs"] = []
    for T in (400, 1000, 4000, 8000):
        hd, hp2 = hand_builder(WG, dem, T, tag=f"_T{T}")
        fl = flood_loop(WG, hp2, rows, tag=f"_T{T}")
        res["threshold_runs"].append({"threshold": T, "river_cells": hd["River_Cells"]["cells"],
                                      "stream_cells": hd["Stream_Cells"]["cells"], "hand_cells": hd["HAND"]["cells"],
                                      "floods": [{k: r[k] for k in ("return_yr", "H_CM", "area_km2", "buildings", "csi", "hit_rate")} for r in fl]})
        print(res["threshold_runs"][-1])
    res["seconds"] = round(time.time() - t0)
    json.dump(res, open(os.path.join(HERE, "package_checks.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
