"""Extra failure-mode check values for the Lab 5 page (appends to extra_checks.json)."""
import json, os
import arcpy, numpy as np
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial"); arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Ames\Lab05\Check.gdb"
UTM = arcpy.SpatialReference(26912)
out = {}
# a) Flow Direction straight from the unfilled DEM
fd0 = FlowDirection("DEM_UTM", "NORMAL", None, "D8")
v = arcpy.RasterToNumPyArray(fd0, nodata_to_value=-1)
pw = {1, 2, 4, 8, 16, 32, 64, 128, -1}
out["unfilled_flowdir_nonpower_cells"] = int((~np.isin(v, list(pw))).sum())
out["unfilled_flowdir_distinct"] = int(np.unique(v).size)
fa0 = FlowAccumulation(fd0)
out["unfilled_flowacc_max"] = fa0.maximum
# b) basin polygon, simplified (the tool default)
arcpy.conversion.RasterToPolygon("Basin_Raster", "Basin_Simplified", "SIMPLIFY", "Value")
out["basin_simplified_km2"] = sum(r[0] for r in arcpy.da.SearchCursor("Basin_Simplified", ["SHAPE@AREA"])) / 1e6
out["basin_simplified_count"] = int(arcpy.management.GetCount("Basin_Simplified")[0])
# subwatersheds simplified total area and single-part count at baseline
out["sub5000_total_km2"] = sum(r[0] for r in arcpy.da.SearchCursor("Subwatersheds_5000", ["SHAPE@AREA"])) / 1e6
# c) where the flow accumulation maximum is
fa = arcpy.Raster("Flow_Accumulation")
a = arcpy.RasterToNumPyArray(fa, nodata_to_value=0)
r, c = np.unravel_index(np.argmax(a), a.shape)
x = fa.extent.XMin + (c + .5) * 10; y = fa.extent.YMax - (r + .5) * 10
g = arcpy.PointGeometry(arcpy.Point(x, y), UTM).projectAs(arcpy.SpatialReference(4326)).firstPoint
out["flowacc_max_at"] = [round(x), round(y), round(g.Y, 5), round(g.X, 5), int(r), int(c), a.shape]
# d) NHD lengths as Web Mercator would report them, and geodesic
arcpy.management.Project("NHD_Basin", "NHD_Basin_WM", arcpy.SpatialReference(3857))
out["nhd_webmercator_km"] = sum(r[0] for r in arcpy.da.SearchCursor("NHD_Basin_WM", ["SHAPE@LENGTH"])) / 1000
out["nhd_geodesic_km"] = sum(r[0].getLength("GEODESIC", "METERS") for r in arcpy.da.SearchCursor("NHD_Basin", ["SHAPE@"])) / 1000
out["nhd_utm_km"] = sum(r[0] for r in arcpy.da.SearchCursor("NHD_Basin", ["SHAPE@LENGTH"])) / 1000
# e) Snap distance 0 with a point 40 m north of the channel (a typical click)
fc = arcpy.management.CreateFeatureclass("in_memory", "off", "POINT", spatial_reference=UTM)[0]
with arcpy.da.InsertCursor(fc, ["SHAPE@XY"]) as cur:
    cur.insertRow([(446432, 4457428)])
for snap in (0, 10, 50):
    w = Watershed("Flow_Direction", SnapPourPoint(fc, "Flow_Accumulation", snap))
    out[f"offchannel_40m_snap{snap}_cells"] = int((arcpy.RasterToNumPyArray(w, nodata_to_value=-1) >= 0).sum())
# f) mean elevation, relief, basin perimeter
out["basin_perimeter_km"] = sum(r[0] for r in arcpy.da.SearchCursor("Rock_Canyon_Basin", ["SHAPE@LENGTH"])) / 1000
print(json.dumps(out, indent=1, default=str))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "extra_checks.json"), "w"), indent=1, default=str)
