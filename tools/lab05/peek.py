"""Quick look PNG: hillshade, streams at 5,000 cells, and candidate outlets."""
import sys
import arcpy
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")
arcpy.env.workspace = r"C:\Ames\Lab05\explore.gdb"
hs = Hillshade("DEM_UTM")
h = arcpy.RasterToNumPyArray(hs, nodata_to_value=0)
fa = arcpy.RasterToNumPyArray("Flow_Accumulation", nodata_to_value=0)
ext = arcpy.Raster("DEM_UTM").extent
x0, y1 = ext.XMin, ext.YMax
zoom = sys.argv[1:] and [float(v) for v in sys.argv[1:5]]
fig, ax = plt.subplots(figsize=(12, 12))
E = [ext.XMin, ext.XMax, ext.YMin, ext.YMax]
ax.imshow(h, cmap="gray", extent=E)
s = np.ma.masked_where(fa < 5000, np.log10(fa + 1))
ax.imshow(s, cmap="winter", extent=E, alpha=0.9)
utm = arcpy.SpatialReference(26912)
for lon, lat in [(-111.6275, 40.2660), (-111.6245, 40.2665), (-111.6200, 40.2670)]:
    p = arcpy.PointGeometry(arcpy.Point(lon, lat), arcpy.SpatialReference(4269)).projectAs(utm).firstPoint
    ax.plot(p.X, p.Y, "r+", ms=14)
if zoom:
    ax.set_xlim(zoom[0], zoom[1]); ax.set_ylim(zoom[2], zoom[3])
ax.grid(True, alpha=0.3)
plt.savefig(r"C:\Ames\Lab05\peek.png", dpi=80, bbox_inches="tight")
