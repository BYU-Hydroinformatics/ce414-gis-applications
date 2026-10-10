"""Lab 7 (HAND flood mapping): arcpy reference model for the Provo River.

  DEM -> Fill -> Flow Direction (D8) -> Flow Accumulation -> Con(acc > T) streams
      -> Extract by Mask (river corridor)        [keeps only the Provo River's cells]
      -> Flow Distance (VERTICAL, D8) = HAND
      -> for each return period: Con(HAND <= h) -> flooded area, buildings, FEMA comparison

Usage (ArcGIS Pro python):
  run_model.py                 default run (2 m lidar, T, corridor) + writes check_values.json
  run_model.py --sweep         sensitivity runs -> sensitivity.json
  run_model.py --personal      personal-stage lookup table -> ce414-private/grading-oracles/lab07_personal_lookup.csv
"""
import csv
import json
import math
import os
import sys
import time

import arcpy
from arcpy.sa import (Con, ExtractByMask, Fill, FlowAccumulation, FlowDirection, FlowDistance,
                      IsNull, Raster, SetNull)

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"C:\Ames\HAND"
GDB = os.path.join(ROOT, "HAND.gdb")
WORK = os.path.join(ROOT, "work")
UTM = arcpy.SpatialReference(26912)
STAGES = [r for r in csv.DictReader(open(os.path.join(HERE, "stage_table.csv"))) if r["design"] == "True"]

DEFAULT = {"cell": 5, "threshold_km2": 0.05, "corridor_m": 30, "dem": "lidar"}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def prep_static():
    """Corridor polygon, FEMA riverine 1% polygon, comparison domain, building centroids."""
    out = {}
    river = os.path.join(GDB, "Provo_River")
    if not arcpy.Exists(river):
        arcpy.analysis.Select(os.path.join(GDB, "NHD_Flowlines"), river,
                              "GNIS_Name = 'Provo River'")
        arcpy.management.Dissolve(river, river + "_d")
        arcpy.management.Delete(river)
        arcpy.management.Rename(river + "_d", river)
    out["river_km"] = sum(r[0] for r in arcpy.da.SearchCursor(river, ["SHAPE@LENGTH"])) / 1000
    fema = os.path.join(GDB, "FEMA_Riverine_1pct")
    if not arcpy.Exists(fema):
        # riverine 1%-annual-chance zones: A, AE (incl. floodway), AH, AO; not the Utah Lake
        # coastal zones (AE/AH "COASTAL FLOODPLAIN", VE)
        arcpy.analysis.Select(os.path.join(GDB, "FEMA_Zones"), fema + "_s",
                              "FLD_ZONE IN ('A','AE','AH','AO') AND (ZONE_SUBTY IS NULL OR "
                              "ZONE_SUBTY NOT LIKE '%COASTAL FLOODPLAIN%')")
        arcpy.management.Dissolve(fema + "_s", fema)
        arcpy.management.Delete(fema + "_s")
    coast = os.path.join(GDB, "FEMA_Coastal")
    if not arcpy.Exists(coast):
        arcpy.analysis.Select(os.path.join(GDB, "FEMA_Zones"), coast + "_s",
                              "FLD_ZONE = 'VE' OR ZONE_SUBTY LIKE '%COASTAL FLOODPLAIN%'")
        arcpy.management.Dissolve(coast + "_s", coast)
        arcpy.management.Delete(coast + "_s")
    pts = os.path.join(GDB, "Building_Points")
    if not arcpy.Exists(pts):
        arcpy.management.FeatureToPoint(os.path.join(GDB, "Buildings"), pts, "INSIDE")
    return out


def corridor(width):
    fc = os.path.join(GDB, f"Corridor_{width}m")
    if not arcpy.Exists(fc):
        arcpy.analysis.Buffer(os.path.join(GDB, "Provo_River"), fc, f"{width} Meters", dissolve_option="ALL")
    return fc


def domain(width=500):
    """Comparison domain: within `width` m of the river, minus the Utah Lake coastal zones."""
    fc = os.path.join(GDB, f"Domain_{width}m")
    if not arcpy.Exists(fc):
        arcpy.analysis.Buffer(os.path.join(GDB, "Provo_River"), fc + "_b", f"{width} Meters", dissolve_option="ALL")
        arcpy.analysis.Erase(fc + "_b", os.path.join(GDB, "FEMA_Coastal"), fc)
        arcpy.management.Delete(fc + "_b")
    return fc


def dem_for(cell, source):
    os.makedirs(WORK, exist_ok=True)
    out = os.path.join(WORK, f"dem_{source}_{cell}m.tif")
    if arcpy.Exists(out):
        return out
    if source == "lidar":
        src = os.path.join(ROOT, "dem", "dem_2m.tif")
        if cell == 2:
            arcpy.management.CopyRaster(src, out)
        elif cell % 2:
            # odd cell sizes cannot nest in the 2 m grid: bilinear resample (snapped to the 2 m origin)
            arcpy.management.Resample(src, out, cell, "BILINEAR")
        else:
            # mean of the 2 m cells (Aggregate) keeps the grids nested
            arcpy.sa.Aggregate(src, int(cell / 2), "MEAN", "EXPAND", "DATA").save(out)
    else:  # the USGS 1/3 arc-second product, projected bilinear
        with arcpy.EnvManager(snapRaster=os.path.join(ROOT, "dem", "dem_2m.tif")):
            arcpy.management.ProjectRaster(os.path.join(ROOT, "dem", "dem13_gcs.tif"), out, UTM,
                                           "BILINEAR", cell)
    return out


def build(cell=2, threshold_km2=0.05, corridor_m=100, dem="lidar", tag=None, keep=False):
    tag = tag or f"{dem}_{cell}m_T{threshold_km2}_C{corridor_m}"
    d = os.path.join(WORK, tag)
    os.makedirs(d, exist_ok=True)
    src = dem_for(cell, dem)
    with arcpy.EnvManager(snapRaster=src, extent=src, cellSize=src, outputCoordinateSystem=UTM):
        t0 = time.time()
        fill = Fill(src)
        fdr = FlowDirection(fill, "NORMAL", "#", "D8")
        acc = FlowAccumulation(fdr, "#", "FLOAT", "D8")
        cells = threshold_km2 * 1e6 / (cell * cell)
        streams = Con(acc > cells, 1)
        river = ExtractByMask(streams, corridor(corridor_m))
        hand = FlowDistance(river, fill, fdr, "VERTICAL", "D8", "MINIMUM")
        hand.save(os.path.join(d, "hand.tif"))
        if keep:
            fill.save(os.path.join(d, "fill.tif"))
            fdr.save(os.path.join(d, "fdr.tif"))
            acc.save(os.path.join(d, "acc.tif"))
            river.save(os.path.join(d, "river.tif"))
        secs = time.time() - t0
    hand = Raster(os.path.join(d, "hand.tif"))
    r = {"tag": tag, "cell": cell, "threshold_km2": threshold_km2, "threshold_cells": cells,
         "corridor_m": corridor_m, "dem": dem, "seconds": round(secs, 1),
         "dem_cols": hand.width, "dem_rows": hand.height,
         "dem_min": Raster(src).minimum, "dem_max": Raster(src).maximum,
         "hand_min": hand.minimum, "hand_max": hand.maximum, "hand_mean": hand.mean}
    arr = arcpy.RasterToNumPyArray(river, nodata_to_value=0)
    r["river_cells"] = int((arr > 0).sum())
    harr = arcpy.RasterToNumPyArray(hand, nodata_to_value=-9999)
    r["hand_cells"] = int((harr > -9999).sum())
    return r, os.path.join(d, "hand.tif")


def flood_stats(hand_path, h_m, cell, dom_arr=None, fema_arr=None, pts=None):
    import numpy as np
    harr = arcpy.RasterToNumPyArray(hand_path, nodata_to_value=-9999)
    wet = (harr > -9999) & (harr <= h_m)
    s = {"h_m": h_m, "cells": int(wet.sum()), "area_km2": round(wet.sum() * cell * cell / 1e6, 4)}
    if dom_arr is not None:
        inside = dom_arr > 0
        f = fema_arr > 0
        hits = int((wet & f & inside).sum())
        misses = int((~wet & f & inside).sum())
        fa = int((wet & ~f & inside).sum())
        s.update(hits=hits, misses=misses, false_alarms=fa,
                 hit_rate=round(hits / max(hits + misses, 1), 3),
                 false_alarm_ratio=round(fa / max(hits + fa, 1), 3),
                 csi=round(hits / max(hits + misses + fa, 1), 3),
                 fema_km2=round((f & inside).sum() * cell * cell / 1e6, 4),
                 hand_in_domain_km2=round((wet & inside).sum() * cell * cell / 1e6, 4))
    if pts is not None:
        rows, cols = pts
        ok = (rows >= 0) & (rows < harr.shape[0]) & (cols >= 0) & (cols < harr.shape[1])
        v = harr[rows[ok], cols[ok]]
        s["buildings"] = int(((v > -9999) & (v <= h_m)).sum())
    return s


def masks(hand_path, cell):
    """FEMA riverine 1% raster and domain raster on the HAND grid; building centroid rows/cols."""
    import numpy as np
    r = Raster(hand_path)
    ext = r.extent
    out = {}
    with arcpy.EnvManager(snapRaster=hand_path, extent=hand_path, cellSize=hand_path, outputCoordinateSystem=UTM):
        for name, fc in (("fema", os.path.join(GDB, "FEMA_Riverine_1pct")), ("dom", domain())):
            p = os.path.join(WORK, f"{name}_{cell}m.tif")
            if not arcpy.Exists(p):
                tmp = fc
                arcpy.management.AddField(tmp, "ONE", "SHORT") if "ONE" not in [f.name for f in arcpy.ListFields(tmp)] else None
                arcpy.management.CalculateField(tmp, "ONE", "1")
                arcpy.conversion.PolygonToRaster(tmp, "ONE", p, "CELL_CENTER", "#", cell)
            a = arcpy.RasterToNumPyArray(p, ext.lowerLeft, r.width, r.height, nodata_to_value=0)
            out[name] = a
    xs, ys = [], []
    for (x, y) in arcpy.da.SearchCursor(os.path.join(GDB, "Building_Points"), ["SHAPE@X", "SHAPE@Y"]):
        xs.append(x)
        ys.append(y)
    xs, ys = np.array(xs), np.array(ys)
    cols = np.floor((xs - ext.XMin) / r.meanCellWidth).astype(int)
    rows = np.floor((ext.YMax - ys) / r.meanCellHeight).astype(int)
    return out["dom"], out["fema"], (rows, cols)


def evaluate(cfg, keep=False):
    r, hp = build(**cfg, keep=keep)
    dom, fema, pts = masks(hp, cfg["cell"])
    r["floods"] = {}
    for s in STAGES:
        h = float(s["hand_h_m"])
        r["floods"][s["return_period_yr"]] = flood_stats(hp, h, cfg["cell"], dom, fema, pts)
    log(json.dumps({k: v for k, v in r.items() if k != "floods"}))
    for k, v in r["floods"].items():
        log(k, v)
    return r


def main():
    info = prep_static()
    log(info)
    if "--sweep" in sys.argv:
        runs = []
        base = dict(DEFAULT)
        variants = [dict(base)]
        for t in (0.01, 0.02, 0.1, 0.2, 0.5):
            variants.append(dict(base, threshold_km2=t))
        for c in (15, 60):
            variants.append(dict(base, corridor_m=c))
        for cell in (2, 3, 10):
            variants.append(dict(base, cell=cell))
        variants.append(dict(base, cell=10, dem="ned13"))
        for v in variants:
            runs.append(evaluate(v))
            json.dump(runs, open(os.path.join(HERE, "sensitivity_5m_base.json"), "w"), indent=1, default=float)
        return
    r = evaluate(dict(DEFAULT), keep=True)
    r.update(info)
    json.dump(r, open(os.path.join(HERE, "check_values.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
