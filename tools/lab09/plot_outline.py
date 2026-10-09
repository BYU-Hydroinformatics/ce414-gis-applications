"""QA picture: Butte_Boundary and Points_Boundary over the hillshade. ArcGIS Pro Python."""
import os
import arcpy
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

GDB = r"C:\Ames\Lab08\Check.gdb"
hs = arcpy.Raster(os.path.join(GDB, "Hillshade"))
ll = arcpy.Point(hs.extent.XMin, hs.extent.YMin)
a = arcpy.RasterToNumPyArray(hs, ll, hs.width, hs.height, nodata_to_value=0)
e = hs.extent
fig, ax = plt.subplots(figsize=(11, 10), dpi=100)
ax.imshow(a, extent=(e.XMin, e.XMax, e.YMin, e.YMax), cmap="gray")
for fc, col in (("Butte_Boundary", "red"), ("Points_Boundary", "cyan")):
    for (g,) in arcpy.da.SearchCursor(os.path.join(GDB, fc), ["SHAPE@"]):
        for part in g:
            xs = [p.X if p else np.nan for p in part]; ys = [p.Y if p else np.nan for p in part]
            ax.plot(xs, ys, color=col, lw=1.2)
ax.set_xlim(326000, 345000); ax.set_ylim(4799000, 4816000)
fig.tight_layout(); fig.savefig(r"C:\Ames\Lab08\outline.png")
