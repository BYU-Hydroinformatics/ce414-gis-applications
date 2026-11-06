"""Rebuild Lab 5's Rock Canyon subwatersheds into D:\\Smith\\Tips\\Watershed.gdb for the ArcGIS Tips
captures: flow accumulation, the snapped outlet at 0 m and at 50 m (Snap Pour Point's default
and the lab's setting), and Raster to Polygon with and without "Create multipart features".
Prints the counts the tips pages quote, so the captions use numbers measured here.

    propy.bat tools\\screenshots\\tips_watershed.py
"""
import os

import arcpy
from arcpy.sa import Con, FlowAccumulation, SnapPourPoint, StreamLink, Watershed

SRC = r"C:\Ames\Lab05GUI\Lab05.gdb"
GDB = r"D:\Smith\Tips\Watershed.gdb"

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
if not arcpy.Exists(GDB):
    arcpy.management.CreateFileGDB(os.path.dirname(GDB), os.path.basename(GDB))
arcpy.env.workspace = GDB
fdir = os.path.join(SRC, "Flow_Directiond8")
arcpy.env.snapRaster = fdir
arcpy.env.extent = fdir
arcpy.env.cellSize = fdir

acc = FlowAccumulation(fdir)
acc.save("Flow_Accumulation")

# Outlet offset 40 m east of Lab 5's outlet, the "click beside the channel" case on the page.
arcpy.management.CopyFeatures(os.path.join(SRC, "Outlet"), "Outlet_Click")
with arcpy.da.UpdateCursor("Outlet_Click", ["SHAPE@XY"]) as cur:
    for (x, y), in cur:
        cur.updateRow([(x + 40, y)])

for name, pts, dist in [("Snap0", "Outlet_Click", 0), ("Snap50", "Outlet_Click", 50),
                        ("SnapLab", os.path.join(SRC, "Outlet"), 50)]:
    snapped = SnapPourPoint(pts, acc, dist)
    snapped.save(name)
    ws = Watershed(fdir, snapped)
    ws.save("Basin_" + name)
    cells = int(arcpy.management.GetRasterProperties(ws, "UNIQUEVALUECOUNT")[0]) if False else None
    arr = arcpy.RasterToNumPyArray(ws, nodata_to_value=-1)
    print(name, "snap", dist, "m: basin cells", int((arr >= 0).sum()),
          "area km2", round((arr >= 0).sum() * 100 / 1e6, 3))

basin = arcpy.Raster("Basin_SnapLab")
streams = Con((basin >= 0) & (acc > 5000), 1)
streams.save("Stream_Cells")
links = StreamLink(streams, fdir)
links.save("Stream_Links")
sub = Watershed(fdir, links)
sub.save("Subwatershed_Raster")

arcpy.conversion.RasterToPolygon(sub, "Subwatersheds_SinglePart", "SIMPLIFY", "Value",
                                 "SINGLE_OUTER_PART")
arcpy.conversion.RasterToPolygon(sub, "Subwatersheds_Multipart", "SIMPLIFY", "Value",
                                 "MULTIPLE_OUTER_PART")
for fc in ("Subwatersheds_SinglePart", "Subwatersheds_Multipart"):
    print(fc, arcpy.management.GetCount(fc)[0])
