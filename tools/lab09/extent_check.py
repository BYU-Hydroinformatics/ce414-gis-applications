r"""Failure value for Step 9: the cell COUNT Zonal Statistics as Table reports when the Processing Extent
environment is left at its default (each tool's own inputs), versus 67,337 with Extent = True_DEM."""
import os, arcpy
from arcpy.sa import Idw, Kriging, KrigingModelOrdinary, RadiusVariable, Raster, Square, ZonalStatisticsAsTable
GDB = r"C:\Ames\Lab09\Check.gdb"
arcpy.CheckOutExtension("Spatial"); arcpy.env.overwriteOutput = True; arcpy.env.workspace = GDB
arcpy.env.snapRaster = os.path.join(GDB, "True_DEM"); arcpy.env.cellSize = 30
pts = "Points_n2500_s1"
for name, surf in (("IDW", Idw(pts, "RASTERVALU", 30, 2, RadiusVariable(12))),
                   ("Kriging", Kriging(pts, "RASTERVALU", KrigingModelOrdinary("SPHERICAL"), 30, RadiusVariable(12)))):
    ZonalStatisticsAsTable("Study_Area", "OBJECTID", Square(Raster("True_DEM") - surf), "ZS_noext", "DATA", "MEAN")
    c, m = next(arcpy.da.SearchCursor("ZS_noext", ["COUNT", "MEAN"]))
    print(name, "no extent env: surface", surf.width, "x", surf.height, "COUNT", int(c), "RMSE", round(m ** 0.5, 2))
arcpy.analysis.CreateThiessenPolygons(pts, "TP_fid", "ONLY_FID")
print("Thiessen ONLY_FID fields:", [f.name for f in arcpy.ListFields("TP_fid")])
