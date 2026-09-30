"""Delineate the basin above candidate outlets and check it clears the DEM edge."""
import arcpy
import numpy as np
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Ames\Lab05\explore.gdb"
utm = arcpy.SpatialReference(26912)
fa = arcpy.Raster("Flow_Accumulation")
ext = fa.extent
for lon, lat in [(-111.6275, 40.2660), (-111.6290, 40.2658), (-111.6245, 40.2665)]:
    p = arcpy.PointGeometry(arcpy.Point(lon, lat), arcpy.SpatialReference(4269)).projectAs(utm)
    fc = arcpy.management.CreateFeatureclass("in_memory", "pp", "POINT", spatial_reference=utm)[0]
    with arcpy.da.InsertCursor(fc, ["SHAPE@"]) as cur:
        cur.insertRow([p])
    for snap in (0, 30, 50, 100):
        sp = SnapPourPoint(fc, "Flow_Accumulation", snap)
        ws = Watershed("Flow_Direction", sp)
        a = arcpy.RasterToNumPyArray(ws, nodata_to_value=-1)
        n = int((a >= 0).sum())
        rows, cols = np.where(a >= 0)
        spa = arcpy.RasterToNumPyArray(sp, nodata_to_value=-1)
        r, c = [int(v[0]) for v in np.where(spa >= 0)]
        sx = sp.extent.XMin + (c + .5) * 10; sy = sp.extent.YMax - (r + .5) * 10
        print(f"{lon},{lat} snap {snap}: {n} cells {n*100/1e6:.3f} km2; pour ({sx:.0f},{sy:.0f}); "
              f"rows {rows.min()}-{rows.max()} of {a.shape[0]}, cols {cols.min()}-{cols.max()} of {a.shape[1]}")
