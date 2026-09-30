"""Run Lab 5's model step for step in C:\\Ames\\Lab05\\Check.gdb and record every check value.

Usage:  run_model.py [threshold ...]
With no thresholds it runs the baseline and the sensitivity sweep. Writes check_values.json next to
this script. Run with the ArcGIS Pro Python (arcgispro-py3).
"""
import json
import os
import sys
import time

import arcpy
import numpy as np
from arcpy.sa import *

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"C:\Ames\Lab05"
GDB = os.path.join(ROOT, "Check.gdb")
DEM = os.path.join(ROOT, "Data", "RockCanyon_DEM.tif")
NHD = os.path.join(ROOT, "Data", "nhd_bbox.json")
OUTLET_LATLON = (40.26525, -111.63000)   # Rock Canyon trailhead, on the creek
SNAP = 50                                 # meters
BASELINE = 5000
SWEEP = [500, 1000, 2000, 5000, 10000, 20000, 50000]

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
if not arcpy.Exists(GDB):
    arcpy.management.CreateFileGDB(ROOT, "Check.gdb")
arcpy.env.workspace = GDB
UTM = arcpy.SpatialReference(26912)
arcpy.env.outputCoordinateSystem = UTM
out = {}


def cells(r, value=None):
    a = arcpy.RasterToNumPyArray(r, nodata_to_value=-9999)
    return int((a != -9999).sum()) if value is None else int((a == value).sum())


t0 = time.time()
# Project the DEM once, outside the model (Step 1)
arcpy.management.ProjectRaster(DEM, "DEM_UTM", UTM, "BILINEAR", "10 10")
d = arcpy.Raster("DEM_UTM")
out["dem_utm"] = dict(cols=d.width, rows=d.height, cell=d.meanCellWidth, min=d.minimum, max=d.maximum)
src = arcpy.Raster(DEM)
out["dem_src"] = dict(cols=src.width, rows=src.height, cellx=src.meanCellWidth, min=src.minimum, max=src.maximum,
                      sr=src.spatialReference.name)

# Outlet point (Step 2)
fc = arcpy.management.CreateFeatureclass(GDB, "Outlet", "POINT", spatial_reference=UTM)[0]
pt = arcpy.PointGeometry(arcpy.Point(OUTLET_LATLON[1], OUTLET_LATLON[0]), arcpy.SpatialReference(4326)).projectAs(UTM)
with arcpy.da.InsertCursor(fc, ["SHAPE@"]) as cur:
    cur.insertRow([pt])
out["outlet_utm"] = [round(pt.firstPoint.X, 1), round(pt.firstPoint.Y, 1)]

# The model: shared part
fill = Fill("DEM_UTM"); fill.save("Filled_DEM")
depth = Minus("Filled_DEM", "DEM_UTM")
da = arcpy.RasterToNumPyArray(depth, nodata_to_value=0)
out["fill"] = dict(cells_raised=int((da > 0).sum()), max_depth=float(da.max()),
                   filled_min=fill.minimum, filled_max=fill.maximum)
fd = FlowDirection("Filled_DEM", "NORMAL", None, "D8"); fd.save("Flow_Direction")
fdv = arcpy.RasterToNumPyArray(fd, nodata_to_value=-1)
out["flowdir_values"] = {int(k): int(v) for k, v in zip(*np.unique(fdv, return_counts=True))}
fa = FlowAccumulation("Flow_Direction", None, "FLOAT", "D8"); fa.save("Flow_Accumulation")
out["flowacc_max"] = fa.maximum
sp = SnapPourPoint("Outlet", "Flow_Accumulation", SNAP); sp.save("Snapped_Outlet")
spa = arcpy.RasterToNumPyArray(sp, nodata_to_value=-1)
r, c = [int(v[0]) for v in np.where(spa >= 0)]
fav = arcpy.RasterToNumPyArray(fa, lower_left_corner=arcpy.Point(sp.extent.XMin, sp.extent.YMin), ncols=spa.shape[1], nrows=spa.shape[0])
out["snapped_outlet"] = dict(x=sp.extent.XMin + (c + .5) * 10, y=sp.extent.YMax - (r + .5) * 10, flowacc=float(fav[r, c]))
nsp = Watershed("Flow_Direction", SnapPourPoint("Outlet", "Flow_Accumulation", 0))
out["unsnapped_basin_cells"] = cells(nsp)
ws = Watershed("Flow_Direction", "Snapped_Outlet"); ws.save("Basin_Raster")
arcpy.conversion.RasterToPolygon("Basin_Raster", "Rock_Canyon_Basin", "NO_SIMPLIFY", "Value", "MULTIPLE_OUTER_PART")
basin_cells = cells(ws)
area = sum(r[0] for r in arcpy.da.SearchCursor("Rock_Canyon_Basin", ["SHAPE@AREA"]))
out["basin"] = dict(cells=basin_cells, km2=basin_cells * 100 / 1e6, polygon_km2=area / 1e6,
                    polygons=int(arcpy.management.GetCount("Rock_Canyon_Basin")[0]))
dem_in = ExtractByMask("DEM_UTM", "Basin_Raster")
out["basin"]["elev_min"] = dem_in.minimum; out["basin"]["elev_max"] = dem_in.maximum
dep_in = arcpy.RasterToNumPyArray(ExtractByMask(depth, "Basin_Raster"), nodata_to_value=0)
out["basin"]["fill_cells_raised"] = int((dep_in > 0).sum()); out["basin"]["fill_max_depth"] = float(dep_in.max())
# Where the Fill tool raised the surface most (outside the basin, in the check-value note)
i = np.unravel_index(np.argmax(da), da.shape)
dx = d.extent.XMin + (i[1] + .5) * 10; dy = d.extent.YMax - (i[0] + .5) * 10
gp = arcpy.PointGeometry(arcpy.Point(dx, dy), UTM).projectAs(arcpy.SpatialReference(4326)).firstPoint
out["fill"]["max_at"] = [round(dx), round(dy), round(gp.Y, 5), round(gp.X, 5)]
out["fill"]["cells_raised_1m"] = int((da > 1).sum())

# NHD inside the basin
arcpy.conversion.JSONToFeatures(NHD, "NHD_bbox")
arcpy.analysis.Clip("NHD_bbox", "Rock_Canyon_Basin", "NHD_Basin")
nhd = [(r[0], r[1], r[2]) for r in arcpy.da.SearchCursor("NHD_Basin", ["SHAPE@LENGTH", "FCode", "GNIS_Name"])]
out["nhd_basin"] = dict(features=len(nhd), km=sum(x[0] for x in nhd) / 1000,
                        by_fcode={str(k): round(sum(x[0] for x in nhd if x[1] == k) / 1000, 2) for k in set(x[1] for x in nhd)},
                        names=sorted(set(str(x[2]) for x in nhd)))
out["shared_seconds"] = round(time.time() - t0, 1)


def run(th, keep=False):
    t = time.time()
    tag = f"{th}"
    # Step 9's Raster Calculator: Con(("%Basin_Raster%" >= 0) & ("%Flow_Accumulation%" > %Threshold%), 1)
    sc = Con((Raster("Basin_Raster") >= 0) & (Raster("Flow_Accumulation") > th), 1); sc.save(f"Stream_Cells_{tag}")
    sl = StreamLink(f"Stream_Cells_{tag}", "Flow_Direction"); sl.save(f"Stream_Links_{tag}")
    links = int(arcpy.Raster(f"Stream_Links_{tag}").maximum or 0)
    sub = Watershed("Flow_Direction", f"Stream_Links_{tag}"); sub.save(f"Subwatershed_Raster_{tag}")
    sc, sl, sub = f"Stream_Cells_{tag}", f"Stream_Links_{tag}", f"Subwatershed_Raster_{tag}"
    s_fc = f"Streams_{tag}"; w_fc = f"Subwatersheds_{tag}"
    StreamToFeature(sl, "Flow_Direction", s_fc, "SIMPLIFY")
    arcpy.conversion.RasterToPolygon(sub, w_fc, "SIMPLIFY", "Value", "MULTIPLE_OUTER_PART")
    arcpy.conversion.RasterToPolygon(sub, "tmp_single", "SIMPLIFY", "Value", "SINGLE_OUTER_PART")
    lengths = [r[0] for r in arcpy.da.SearchCursor(s_fc, ["SHAPE@LENGTH"])]
    areas = [r[0] for r in arcpy.da.SearchCursor(w_fc, ["SHAPE@AREA"])]
    sub_cells = cells(sub)
    res = dict(threshold=th, threshold_km2=th * 100 / 1e6, stream_cells=cells(sc), links=links,
               stream_features=len(lengths), stream_km=sum(lengths) / 1000,
               subwatersheds=len(areas), single_part_polygons=int(arcpy.management.GetCount("tmp_single")[0]),
               sub_cells=sub_cells, mean_sub_km2=(sum(areas) / len(areas) / 1e6) if areas else None,
               min_sub_km2=min(areas) / 1e6 if areas else None, max_sub_km2=max(areas) / 1e6 if areas else None,
               seconds=round(time.time() - t, 1))
    res["drainage_density"] = res["stream_km"] / out["basin"]["km2"]
    print(json.dumps(res))
    return res


ths = [int(a) for a in sys.argv[1:]] or SWEEP
out["runs"] = [run(th, keep=(th == BASELINE)) for th in ths]
path = os.path.join(HERE, "check_values.json")
with open(path, "w") as fh:
    json.dump(out, fh, indent=1, default=float)
print(json.dumps({k: v for k, v in out.items() if k != "runs"}, indent=1, default=float))
