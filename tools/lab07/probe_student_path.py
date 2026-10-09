"""Lab 7 (HAND): probe the exact tool settings the student page will use, on the package.

  1. HAND chain with NO environments set (does Flow Distance keep the DEM's extent when the
     stream raster comes from Extract by Mask with a corridor polygon?)
  2. Con with a where clause 'Value * 100 <= 153' (the Flood Loop's expression with H_CM)
  3. Raster to Polygon with create_multipart_features (one row per flood) and no simplify
  4. Spatial Join (JOIN_ONE_TO_ONE, INTERSECT) Join_Count vs Select Layer By Location count
Writes probe_student_path.json.
"""
import json
import os
import shutil

import arcpy
import numpy as np
from arcpy.sa import Con, ExtractByMask, Fill, FlowAccumulation, FlowDirection, FlowDistance, Raster

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
HERE = os.path.dirname(os.path.abspath(__file__))
P = r"C:\Ames\HAND\PkgCheck\lab07-provo-river-hand"
G = os.path.join(P, "ProvoData.gdb")
OUT = r"C:\Ames\HAND\Probe"
if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
arcpy.management.CreateFileGDB(OUT, "Probe.gdb")
WG = os.path.join(OUT, "Probe.gdb")
arcpy.env.workspace = WG
arcpy.env.scratchWorkspace = WG
res = {}
dem = Raster(os.path.join(P, "Provo_DEM.tif"))
fill = Fill(dem); fill.save(os.path.join(WG, "Filled_DEM"))
fdr = FlowDirection(fill, "NORMAL", "#", "D8"); fdr.save(os.path.join(WG, "Flow_Direction"))
acc = FlowAccumulation(fdr, "#", "FLOAT", "D8"); acc.save(os.path.join(WG, "Flow_Accumulation"))
st = Con(acc > 2000, 1); st.save(os.path.join(WG, "Stream_Cells"))
arcpy.analysis.Buffer(os.path.join(G, "Provo_River"), os.path.join(WG, "River_Corridor"), "30 Meters", dissolve_option="ALL")
rv = ExtractByMask(st, os.path.join(WG, "River_Corridor")); rv.save(os.path.join(WG, "River_Cells"))
hand = FlowDistance(rv, fill, fdr, "VERTICAL", "D8", "MINIMUM"); hand.save(os.path.join(WG, "HAND"))
hand = Raster(os.path.join(WG, "HAND"))
a = arcpy.RasterToNumPyArray(hand, nodata_to_value=-9999)
r = Raster(os.path.join(WG, "River_Cells"))
res["no_env"] = {"river_extent": [r.extent.XMin, r.extent.YMin, r.extent.XMax, r.extent.YMax],
                 "river_cells": int((arcpy.RasterToNumPyArray(r, nodata_to_value=0) > 0).sum()),
                 "hand_extent": [hand.extent.XMin, hand.extent.YMin, hand.extent.XMax, hand.extent.YMax],
                 "hand_cols_rows": [hand.width, hand.height], "hand_cells": int((a > -9999).sum()),
                 "hand_max": hand.maximum, "fill_max": Raster(os.path.join(WG, "Filled_DEM")).maximum,
                 "acc_max": Raster(os.path.join(WG, "Flow_Accumulation")).maximum}
print(res["no_env"])
# 2. where clause
for cm in (153,):
    w = Con(hand <= cm / 100, 1)  # what Raster Calculator does with Con("%HAND%" <= %Value% / 100, 1)
    w.save(os.path.join(WG, f"flood_{cm}"))
    wa = arcpy.RasterToNumPyArray(w, nodata_to_value=0)
    direct = int(((a > -9999) & (a <= cm / 100)).sum())
    res["where_clause"] = {"cm": cm, "cells_where": int((wa > 0).sum()), "cells_numpy_h": direct,
                           "cells_numpy_x100": int(((a > -9999) & (a * 100 <= cm)).sum())}
    print(res["where_clause"])
    # 3. multipart polygon, no simplify
    poly = os.path.join(WG, f"floodpoly_{cm}")
    arcpy.conversion.RasterToPolygon(w, poly, "NO_SIMPLIFY", "Value", "MULTIPLE_OUTER_PART")
    n = int(arcpy.management.GetCount(poly)[0])
    area = sum(x[0] for x in arcpy.da.SearchCursor(poly, ["SHAPE@AREA"]))
    res["raster_to_polygon"] = {"rows": n, "area_m2": area, "cells_x25": res["where_clause"]["cells_where"] * 25}
    print(res["raster_to_polygon"])
    # 4. spatial join vs select by location
    sj = os.path.join(WG, "sj")
    arcpy.analysis.SpatialJoin(poly, os.path.join(G, "Buildings"), sj, "JOIN_ONE_TO_ONE", "KEEP_ALL",
                               match_option="INTERSECT")
    jc = [x[0] for x in arcpy.da.SearchCursor(sj, ["Join_Count"])]
    lay = arcpy.management.MakeFeatureLayer(os.path.join(G, "Buildings"), "b")
    arcpy.management.SelectLayerByLocation(lay, "INTERSECT", poly)
    res["buildings"] = {"spatial_join_join_count": jc, "select_by_location": int(arcpy.management.GetCount(lay)[0])}
    print(res["buildings"])
json.dump(res, open(os.path.join(HERE, "probe_student_path.json"), "w"), indent=1, default=float)
