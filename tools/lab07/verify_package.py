"""Lab 7 (HAND): run the student chain on the unzipped package only (no other inputs) and
record the check values a student should reproduce. Writes package_checks.json.

  Provo_DEM -> Fill -> Flow Direction (D8) -> Flow Accumulation -> Con(acc > 2000) [0.05 km2 at 5 m]
  Provo_River -> Buffer 30 m -> Extract by Mask(streams)
  Flow Distance (VERTICAL, D8, MINIMUM) = HAND
  per Stage_Table row: Con(HAND <= H_M) -> Raster to Polygon -> area; Buildings INTERSECT -> count
  100-yr: CSI against FEMA_Floodplain_1pct (polygons, domain = 500 m of the river, the hosted layer)
  personal: Q = 900 + 12*dd -> rating row -> h; every dd 00-99
"""
import csv
import json
import os
import shutil
import zipfile

import arcpy
from arcpy.sa import Con, ExtractByMask, Fill, FlowAccumulation, FlowDirection, FlowDistance, Raster

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = r"C:\Ames\HAND\pkg\lab07-provo-river-hand.zip"
OUT = r"C:\Ames\HAND\PkgCheck"


def area(fc):
    return sum(r[0] for r in arcpy.da.SearchCursor(fc, ["SHAPE@AREA"]))


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    zipfile.ZipFile(ZIP).extractall(OUT)
    P = os.path.join(OUT, "lab07-provo-river-hand")
    G = os.path.join(P, "Lab07.gdb")
    arcpy.management.CreateFileGDB(OUT, "Work.gdb")
    WG = os.path.join(OUT, "Work.gdb")
    dem = Raster(os.path.join(P, "Provo_DEM.tif"))
    res = {"dem": {"cols": dem.width, "rows": dem.height, "cell": dem.meanCellWidth,
                   "min": dem.minimum, "max": dem.maximum,
                   "extent": [dem.extent.XMin, dem.extent.YMin, dem.extent.XMax, dem.extent.YMax]}}
    with arcpy.EnvManager(snapRaster=dem, extent=dem, cellSize=dem, workspace=WG, scratchWorkspace=WG):
        fill = Fill(dem)
        fdr = FlowDirection(fill, "NORMAL", "#", "D8")
        acc = FlowAccumulation(fdr, "#", "FLOAT", "D8")
        streams = Con(acc > 2000, 1)
        corr = os.path.join(WG, "River_Corridor")
        arcpy.analysis.Buffer(os.path.join(G, "Provo_River"), corr, "30 Meters", dissolve_option="ALL")
        river = ExtractByMask(streams, corr)
        hand = FlowDistance(river, fill, fdr, "VERTICAL", "D8", "MINIMUM")
        hand.save(os.path.join(OUT, "hand.tif"))
    hand = Raster(os.path.join(OUT, "hand.tif"))
    fill.save(os.path.join(OUT, "fill.tif"))
    res["fill"] = {"min": Raster(os.path.join(OUT, "fill.tif")).minimum, "max": Raster(os.path.join(OUT, "fill.tif")).maximum}
    acc.save(os.path.join(OUT, "acc.tif"))
    res["acc_max"] = Raster(os.path.join(OUT, "acc.tif")).maximum
    river.save(os.path.join(OUT, "river.tif"))
    rv = Raster(os.path.join(OUT, "river.tif"))
    import numpy as np
    res["river_cells"] = int((arcpy.RasterToNumPyArray(rv, nodata_to_value=0) > 0).sum())
    ha = arcpy.RasterToNumPyArray(hand, nodata_to_value=-9999)
    res["hand"] = {"min": hand.minimum, "max": hand.maximum, "mean": round(hand.mean, 3),
                   "cells": int((ha > -9999).sum())}
    blay = arcpy.management.MakeFeatureLayer(os.path.join(G, "Buildings"), "bl")
    res["buildings_total"] = int(arcpy.management.GetCount(blay)[0])
    fema = os.path.join(G, "FEMA_Floodplain_1pct")
    A_f = area(fema)
    res["fema_km2"] = round(A_f / 1e6, 4)
    dom = os.path.join(G, "Comparison_Area")
    res["rows"] = []
    for rp, h, cm in arcpy.da.SearchCursor(os.path.join(G, "Stage_Table"), ["RETURN_YR", "H_M", "H_CM"]):
        wet = Con(hand <= h, 1)
        poly = os.path.join(WG, f"flood_{cm}")
        arcpy.conversion.RasterToPolygon(wet, poly, "SIMPLIFY", "Value")
        arcpy.management.SelectLayerByLocation(blay, "INTERSECT", poly)
        nb = int(arcpy.management.GetCount(blay)[0])
        arcpy.management.SelectLayerByAttribute(blay, "CLEAR_SELECTION")
        both = os.path.join(WG, f"both_{cm}")
        arcpy.analysis.PairwiseIntersect([poly, fema], both)
        hd = os.path.join(WG, f"hd_{cm}")
        arcpy.analysis.PairwiseClip(poly, dom, hd)
        a_b, a_h = area(both), area(hd)
        row = {"return_yr": rp, "h_m": h, "H_CM": cm, "cells": int(((ha > -9999) & (ha <= h)).sum()),
               "area_km2": round(area(poly) / 1e6, 4), "polygons": int(arcpy.management.GetCount(poly)[0]),
               "buildings_intersect": nb, "hand_in_comparison_km2": round(a_h / 1e6, 4),
               "overlap_km2": round(a_b / 1e6, 4), "hit_rate": round(a_b / A_f, 3),
               "csi": round(a_b / (a_h + A_f - a_b), 3)}
        res["rows"].append(row)
        print(row)
    # personal design flow
    rating = [(float(r["gage_height_ft"]), float(r["discharge_cfs"]))
              for r in csv.DictReader(open(os.path.join(P, "rating_10163000.csv")))]
    pers = []
    for dd in range(100):
        q = 900 + 12 * dd
        gh = next(g for g, d in rating if d >= q)
        h = round((gh - 3.20) * 0.3048, 3)
        pers.append({"dd": f"{dd:02d}", "q_cfs": q, "gage_height_ft": gh, "h_m": h,
                     "cells": int(((ha > -9999) & (ha <= h)).sum()),
                     "area_km2": round(((ha > -9999) & (ha <= h)).sum() * 25 / 1e6, 4)})
    res["personal"] = pers
    json.dump(res, open(os.path.join(HERE, "package_checks.json"), "w"), indent=1, default=float)
    print({k: v for k, v in res.items() if k not in ("rows", "personal")})


if __name__ == "__main__":
    main()
