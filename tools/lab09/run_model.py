"""Lab 9 reference run: the butte-volume model the students build, run with arcpy, plus the
sensitivity runs. Writes tools/lab09/check_values.json.

Model: Create Random Points (in Points_Boundary, fixed seed) -> Extract Values to Points ->
Erase (Butte_Boundary) -> interpolate the plain -> Extract by Mask (DEM and plain) ->
Raster Calculator (height x cell area / 1e9) -> Zonal Statistics SUM.
ArcGIS Pro Python; needs DEM_UTM, Butte_Boundary, Points_Boundary in C:\\Ames\\Lab08\\Check.gdb.
"""
import json
import os

import arcpy
import numpy as np
from arcpy.sa import (Idw, ExtractByMask, Kriging, KrigingModelOrdinary, NaturalNeighbor, Raster,
                      Spline, Trend, ZonalStatistics, RadiusVariable)

GDB = r"C:\Ames\Lab08\Check.gdb"
OUT = os.path.join(os.path.dirname(__file__), "check_values.json")
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = GDB
dem = Raster(os.path.join(GDB, "DEM_UTM"))
arcpy.env.snapRaster = dem
arcpy.env.cellSize = dem
# no extent override: the GUI default (each tool's own inputs) is what students get; Spline depends on it
CELL = dem.meanCellWidth


def points(n, seed, tag):
    arcpy.env.randomGenerator = f"{seed} ACM599"
    rp = f"RP_{tag}"
    arcpy.management.CreateRandomPoints(GDB, rp, "Points_Boundary", "", n)
    arcpy.sa.ExtractValuesToPoints(rp, dem, f"PV_{tag}")
    arcpy.analysis.Erase(f"PV_{tag}", "Butte_Boundary", f"NB_{tag}")
    xy = [r for r in arcpy.da.SearchCursor(rp, ["SHAPE@X", "SHAPE@Y"])]
    return xy, int(arcpy.management.GetCount(f"NB_{tag}")[0])


def plain(method, tag):
    fc = f"NB_{tag}"
    if method == "IDW":
        return Idw(fc, "RASTERVALU", CELL, 2, RadiusVariable(12))
    if method == "Natural Neighbor":
        return NaturalNeighbor(fc, "RASTERVALU", CELL)
    if method == "Spline":
        return Spline(fc, "RASTERVALU", CELL, "REGULARIZED", 0.1, 12)
    if method == "Kriging":
        return Kriging(fc, "RASTERVALU", KrigingModelOrdinary("SPHERICAL"), CELL)
    if method == "Trend (plane)":
        return Trend(fc, "RASTERVALU", CELL, 1, "LINEAR")
    raise ValueError(method)


def volume(surface, outline="Butte_Boundary"):
    b = ExtractByMask(dem, outline)
    p = ExtractByMask(surface, outline)
    v = (b - p) * CELL * CELL / (1000 ** 3)
    z = ZonalStatistics(outline, "OBJECTID", v, "SUM")
    a = arcpy.RasterToNumPyArray(v, nodata_to_value=np.nan)
    h = arcpy.RasterToNumPyArray(b - p, nodata_to_value=np.nan)
    zone = float(z.maximum)
    return dict(volume_km3=round(zone, 4), cells=int(np.isfinite(a).sum()),
                max_height_m=round(float(np.nanmax(h)), 1), neg_cells=int((h < 0).sum()),
                neg_volume_km3=round(float(np.nansum(np.where(a < 0, a, 0))), 4)), v


res = {}
xy1, nb = points(1000, 1, "base")
xy1b, _ = points(1000, 1, "repeat")
res["seed_reproducible"] = xy1 == xy1b
res["first_point"] = [round(xy1[0][0], 2), round(xy1[0][1], 2)]
res["baseline_points_kept"] = nb
base, vras = volume(plain("IDW", "base"))
vras.save(os.path.join(GDB, "Volume_per_cell"))
res["baseline"] = base
res["outline_km2"] = round(sum(r[0] for r in arcpy.da.SearchCursor("Butte_Boundary", ["SHAPE@AREA"])) / 1e6, 3)
plane_dem = arcpy.RasterToNumPyArray(ExtractByMask(dem, "Butte_Boundary"), nodata_to_value=np.nan)
res["butte_dem_max_m"] = round(float(np.nanmax(plane_dem)), 1)

res["methods"] = {}
for m in ("IDW", "Natural Neighbor", "Spline", "Kriging", "Trend (plane)"):
    res["methods"][m] = volume(plain(m, "base"))[0]
    print(m, res["methods"][m], flush=True)

res["counts"] = {}
for n in (250, 500, 2000, 4000):
    _, k = points(n, 1, f"n{n}")
    res["counts"][n] = dict(kept=k, **volume(plain("IDW", f"n{n}"))[0])
    print(n, res["counts"][n], flush=True)

res["seeds"] = {}
for s in (2, 3, 4, 5, 6):
    _, k = points(1000, s, f"s{s}")
    res["seeds"][s] = dict(kept=k, **volume(plain("IDW", f"s{s}"))[0])
    print("seed", s, res["seeds"][s], flush=True)

# Outline sensitivity: grow and shrink the reference outline, as a digitizer might.
res["outline"] = {}
for d in (-200, -100, 100, 200):
    arcpy.analysis.Buffer("Butte_Boundary", f"BB_{abs(d)}{'m' if d < 0 else 'p'}", f"{d} Meters")
for d in (-200, -100, 100, 200):
    o = f"BB_{abs(d)}{'m' if d < 0 else 'p'}"
    arcpy.analysis.Erase("PV_base", o, "NB_o")
    surf = Idw("NB_o", "RASTERVALU", CELL, 2, RadiusVariable(12))
    r = volume(surf, o)[0]
    r["area_km2"] = round(sum(x[0] for x in arcpy.da.SearchCursor(o, ["SHAPE@AREA"])) / 1e6, 3)
    res["outline"][d] = r
    print("outline", d, r, flush=True)

json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps({k: res[k] for k in ("seed_reproducible", "first_point", "baseline_points_kept", "baseline", "outline_km2", "butte_dem_max_m")}, indent=1))
