"""First look: project, fill, flow direction/accumulation, and find the Rock Canyon outlet."""
import arcpy
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
ws = r"C:\Ames\Lab05\explore.gdb"
if not arcpy.Exists(ws):
    arcpy.management.CreateFileGDB(r"C:\Ames\Lab05", "explore.gdb")
arcpy.env.workspace = ws
utm = arcpy.SpatialReference(26912)
arcpy.management.ProjectRaster(r"C:\Ames\Lab05\Data\RockCanyon_DEM.tif", "DEM_UTM", utm, "BILINEAR", "10 10")
d = arcpy.Raster("DEM_UTM")
print("DEM_UTM", d.width, d.height, d.meanCellWidth, d.minimum, d.maximum, d.extent)
arcpy.env.snapRaster = "DEM_UTM"
arcpy.env.cellSize = "DEM_UTM"
fill = Fill("DEM_UTM"); fill.save("Filled_DEM")
fd = FlowDirection("Filled_DEM", "NORMAL", None, "D8"); fd.save("Flow_Direction")
fa = FlowAccumulation("Flow_Direction", None, "FLOAT", "D8"); fa.save("Flow_Accumulation")
diff = Minus("Filled_DEM", "DEM_UTM"); diff.save("Fill_Depth")
print("fill depth max", diff.maximum)
# Candidate outlet near the canyon mouth
g = arcpy.PointGeometry(arcpy.Point(-111.6275, 40.2660), arcpy.SpatialReference(4269)).projectAs(utm)
print("mouth guess UTM", g.firstPoint.X, g.firstPoint.Y)
import numpy as np
arr = arcpy.RasterToNumPyArray(fa, nodata_to_value=0)
ext = fa.extent; cs = fa.meanCellWidth
c = int((g.firstPoint.X - ext.XMin) / cs); r = int((ext.YMax - g.firstPoint.Y) / cs)
win = arr[r-60:r+61, c-60:c+61]
i = np.unravel_index(np.argmax(win), win.shape)
rr, cc = r-60+i[0], c-60+i[1]
x = ext.XMin + (cc+0.5)*cs; y = ext.YMax - (rr+0.5)*cs
print("max acc within 600 m:", win.max(), "at", x, y, "area km2", win.max()*100/1e6)
print("global max acc", arr.max())
