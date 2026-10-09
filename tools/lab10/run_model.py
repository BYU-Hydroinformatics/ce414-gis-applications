r"""Lab 10 reference run: the interpolation-comparison model the students build, run with arcpy, plus
the sensitivity runs. Writes tools/lab10/check_values.json.

Model: Project Raster (UTM 12N, 30 m, bilinear) -> Extract by Mask (Study_Area) = True_DEM ->
Create Random Points (in Study_Area, fixed seed) -> Extract Values to Points ->
  Thiessen:  Create Thiessen Polygons -> Polygon to Raster (RASTERVALU)
  IDW:       IDW (power, variable 12)
  Kriging:   Kriging (ordinary, semivariogram model, variable 12)
each -> Raster Calculator (True_DEM - surface = error) -> Raster Calculator (Square) ->
Zonal Statistics as Table (MEAN, Study_Area) -> Calculate Field RMSE = sqrt(MEAN).
Environments: snap raster and extent True_DEM, cell size 30.

ArcGIS Pro Python. Needs C:\Ames\Lab09\Data\YMountain_DEM.tif; builds C:\Ames\Lab09\Check.gdb.
Usage: run_model.py   (the original reference run). Since October 7, 2026 the lab uses only the hosted
point sets and a personal IDW power; the grading table for every power is verify_package.py ->
package_checks.json['personal_power']. The --seed mode is kept for a possible future personal-seed version.
"""
import argparse
import json
import math
import os
import time

import arcpy
import numpy as np
from arcpy.sa import (ExtractByMask, Idw, Kriging, KrigingModelOrdinary, Raster, RadiusVariable,
                      Square, ZonalStatisticsAsTable)

DEM = r"C:\Ames\Lab09\Data\YMountain_DEM.tif"
GDB = r"C:\Ames\Lab09\Check.gdb"
OUT = os.path.join(os.path.dirname(__file__), "check_values.json")
UTM = arcpy.SpatialReference(26912)        # NAD 1983 UTM Zone 12N
# xmin, ymin, xmax, ymax in UTM 12N meters, on the 30 m grid of DEM_UTM (origin 442,124.873 E,
# top 4,457,947.050 N) so every cell inside it is whole: 289 x 233 cells, 60.6 km2.
STUDY = (442514.873, 4450507.050, 451184.873, 4457497.050)

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True


def setup():
    if not arcpy.Exists(GDB):
        arcpy.management.CreateFileGDB(os.path.dirname(GDB), os.path.basename(GDB))
    arcpy.env.workspace = GDB
    sa = os.path.join(GDB, "Study_Area")
    if arcpy.Exists(sa):   # rebuilt every time so a change to STUDY takes effect
        arcpy.management.Delete(sa)
    if not arcpy.Exists(sa):
        x0, y0, x1, y1 = STUDY
        arcpy.management.CreateFeatureclass(GDB, "Study_Area", "POLYGON", spatial_reference=UTM)
        with arcpy.da.InsertCursor(sa, ["SHAPE@"]) as cur:
            ring = arcpy.Array([arcpy.Point(x0, y0), arcpy.Point(x0, y1), arcpy.Point(x1, y1),
                                arcpy.Point(x1, y0), arcpy.Point(x0, y0)])
            cur.insertRow([arcpy.Polygon(ring, UTM)])
    arcpy.management.ProjectRaster(DEM, "DEM_UTM", UTM, "BILINEAR", 30)
    true = ExtractByMask("DEM_UTM", "Study_Area")
    true.save("True_DEM")
    arcpy.env.snapRaster = os.path.join(GDB, "True_DEM")
    arcpy.env.extent = os.path.join(GDB, "True_DEM")
    arcpy.env.cellSize = 30
    t = Raster("True_DEM")
    a = arcpy.RasterToNumPyArray(t, nodata_to_value=np.nan)
    return dict(dem_utm=dict(cols=Raster("DEM_UTM").width, rows=Raster("DEM_UTM").height,
                             min=round(Raster("DEM_UTM").minimum, 1), max=round(Raster("DEM_UTM").maximum, 1)),
                true_dem=dict(cols=t.width, rows=t.height, cells=int(np.isfinite(a).sum()),
                              min=round(float(np.nanmin(a)), 1), max=round(float(np.nanmax(a)), 1),
                              mean=round(float(np.nanmean(a)), 1)),
                study_km2=round((STUDY[2] - STUDY[0]) * (STUDY[3] - STUDY[1]) / 1e6, 2))


def sample(n, seed, tag):
    arcpy.env.randomGenerator = f"{seed} ACM599"
    rp = f"RP_{tag}"
    arcpy.management.CreateRandomPoints(GDB, rp, "Study_Area", "", n)
    arcpy.sa.ExtractValuesToPoints(rp, "True_DEM", f"Points_{tag}")
    raw = [r[0] for r in arcpy.da.SearchCursor(f"Points_{tag}", ["RASTERVALU"])]
    vals = [v for v in raw if v is not None and v != -9999]
    first = next(arcpy.da.SearchCursor(rp, ["SHAPE@X", "SHAPE@Y"]))
    return f"Points_{tag}", dict(n=len(vals), min=round(min(vals), 1), max=round(max(vals), 1),
                                 nodata=len(raw) - len(vals),
                                 first_point=[round(first[0], 1), round(first[1], 1)])


def thiessen(pts, tag):
    arcpy.analysis.CreateThiessenPolygons(pts, f"Thiessen_Poly_{tag}", "ALL")
    npoly = int(arcpy.management.GetCount(f"Thiessen_Poly_{tag}")[0])
    arcpy.conversion.PolygonToRaster(f"Thiessen_Poly_{tag}", "RASTERVALU", f"Thiessen_{tag}", "CELL_CENTER", "", 30)
    return Raster(f"Thiessen_{tag}"), npoly


def idw(pts, power, tag):
    r = Idw(pts, "RASTERVALU", 30, power, RadiusVariable(12))
    r.save(f"IDW_{tag}")
    return r


def kriging(pts, model, tag):
    r = Kriging(pts, "RASTERVALU", KrigingModelOrdinary(model), 30, RadiusVariable(12))
    r.save(f"Kriging_{tag}")
    return r


def score(surface, tag, checkpoints=None):
    """Error raster, squared error, Zonal Statistics as Table MEAN, sqrt -- as the students do it."""
    err = Raster("True_DEM") - surface
    err.save(f"Error_{tag}")
    sq = Square(err)
    ZonalStatisticsAsTable("Study_Area", "OBJECTID", sq, f"ZS_{tag}", "DATA", "MEAN")
    mean_sq = next(arcpy.da.SearchCursor(f"ZS_{tag}", ["MEAN"]))[0]
    s = arcpy.RasterToNumPyArray(surface, nodata_to_value=np.nan)
    e = arcpy.RasterToNumPyArray(err, nodata_to_value=np.nan)
    t = arcpy.RasterToNumPyArray(Raster("True_DEM"), nodata_to_value=np.nan)
    iy, ix = np.unravel_index(np.nanargmax(np.abs(e)), e.shape)
    ext = err.extent
    worst = [round(ext.XMin + (ix + 0.5) * 30, 0), round(ext.YMax - (iy + 0.5) * 30, 0)]
    res = dict(rmse=round(math.sqrt(mean_sq), 2), mean_sq=round(mean_sq, 1),
               surf_min=round(float(np.nanmin(s)), 1), surf_max=round(float(np.nanmax(s)), 1),
               err_min=round(float(np.nanmin(e)), 1), err_max=round(float(np.nanmax(e)), 1),
               mean_err=round(float(np.nanmean(e)), 2), cells=int(np.isfinite(e).sum()),
               worst_xy=worst, worst_err=round(float(e[iy, ix]), 1),
               cells_above_true_max=int((s > np.nanmax(t)).sum()),
               within_5m=round(float((np.abs(e) <= 5).sum() / np.isfinite(e).sum()), 3))
    if checkpoints:
        arcpy.sa.ExtractValuesToPoints(checkpoints, surface, f"CP_{tag}")
        arcpy.sa.ExtractMultiValuesToPoints(f"CP_{tag}", [[os.path.join(GDB, "True_DEM"), "TRUE_Z"]])
        d = [(a - b) for a, b in arcpy.da.SearchCursor(f"CP_{tag}", ["TRUE_Z", "RASTERVALU"])
             if a is not None and b is not None and b != -9999]
        res["checkpoint_rmse"] = round(math.sqrt(sum(x * x for x in d) / len(d)), 2)
        res["checkpoints_used"] = len(d)
    return res


def run(n, seed, power=2, model="SPHERICAL", tag=None, checkpoints=None, which=("Thiessen", "IDW", "Kriging")):
    tag = tag or f"n{n}_s{seed}"
    pts, pinfo = sample(n, seed, tag)
    out = dict(points=pinfo)
    t0 = time.time()
    if "Thiessen" in which:
        th, npoly = thiessen(pts, tag)
        out["Thiessen"] = dict(polygons=npoly, **score(th, f"Th_{tag}", checkpoints))
    if "IDW" in which:
        out["IDW"] = score(idw(pts, power, f"{tag}_p{power}"), f"IDW_{tag}_p{power}", checkpoints)
    if "Kriging" in which:
        out["Kriging"] = score(kriging(pts, model, f"{tag}_{model[:3]}"), f"Kr_{tag}_{model[:3]}", checkpoints)
    out["secs"] = round(time.time() - t0, 1)
    print(tag, json.dumps({k: (v.get("rmse") if isinstance(v, dict) and "rmse" in v else v) for k, v in out.items()}), flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int)
    ap.add_argument("--points", type=int, default=2500)
    a = ap.parse_args()
    res = dict(setup=setup())
    print(json.dumps(res["setup"]), flush=True)
    # checkpoints: 200 independent points, seed 99, never used to interpolate (Step 10, question 3)
    arcpy.env.randomGenerator = "99 ACM599"
    arcpy.management.CreateRandomPoints(GDB, "Checkpoints", "Study_Area", "", 200)
    if a.seed is not None:   # grading oracle: a student's own rows of the Step 8 table (2,500 points at their seed)
        s = a.seed
        table = {"baseline (my points)": run(2500, s, tag=f"p{s}", checkpoints="Checkpoints"),
                 "IDW power 1, Kriging exponential": run(2500, s, power=1, model="EXPONENTIAL", tag=f"p{s}_a"),
                 "IDW power 3, Kriging Gaussian": run(2500, s, power=3, model="GAUSSIAN", tag=f"p{s}_b")}
        print(json.dumps({k: {m: v[m]["rmse"] for m in ("Thiessen", "IDW", "Kriging")} for k, v in table.items()}, indent=1))
        print("checkpoint RMSE:", {m: table["baseline (my points)"][m]["checkpoint_rmse"] for m in ("Thiessen", "IDW", "Kriging")})
        return
    res["baseline"] = run(2500, 1, checkpoints="Checkpoints")
    res["repeat_identical"] = run(2500, 1, tag="repeat", which=("IDW",))["IDW"]["rmse"] == res["baseline"]["IDW"]["rmse"]
    res["counts"] = {n: run(n, 1, checkpoints="Checkpoints") for n in (250, 1000, 10000)}
    res["idw_power"] = {p: run(2500, 1, power=p, tag=f"pow{p}", which=("IDW",))["IDW"] for p in (1, 3, 5)}
    res["kriging_model"] = {m: run(2500, 1, model=m, tag=f"mod{m[:3]}", which=("Kriging",))["Kriging"]
                            for m in ("EXPONENTIAL", "GAUSSIAN", "LINEAR", "CIRCULAR")}
    res["seeds"] = {s: run(2500, s, tag=f"seed{s}") for s in (2, 3, 4, 5)}
    json.dump(res, open(OUT, "w"), indent=1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
