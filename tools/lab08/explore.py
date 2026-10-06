"""First look at the Big Southern Butte DEM: project to UTM 12N at 10 m, hillshade, slope, and a
picture with contours for choosing the reference outline. Writes C:\\Ames\\Lab08\\Check.gdb and
C:\\Ames\\Lab08\\explore.png. ArcGIS Pro Python."""
import os
import arcpy
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from arcpy.sa import Hillshade, Raster, Slope

ROOT = r"C:\Ames\Lab08"
GDB = os.path.join(ROOT, "Check.gdb")
arcpy.CheckOutExtension("Spatial"); arcpy.env.overwriteOutput = True
if not arcpy.Exists(GDB):
    arcpy.management.CreateFileGDB(ROOT, "Check.gdb")
arcpy.env.workspace = GDB
utm = os.path.join(GDB, "DEM_UTM")
arcpy.management.ProjectRaster(os.path.join(ROOT, "Data", "BigSouthernButte_DEM.tif"), utm,
                               arcpy.SpatialReference(26912), "BILINEAR", "10")
d = Raster(utm)
arcpy.env.snapRaster = d; arcpy.env.extent = d; arcpy.env.cellSize = d
Hillshade(d, 315, 45).save("Hillshade")
Slope(d, "DEGREE").save("Slope_Deg")
ll = arcpy.Point(d.extent.XMin, d.extent.YMin)
A = lambda n: arcpy.RasterToNumPyArray(arcpy.sa.Float(Raster(os.path.join(GDB, n))), ll, d.width, d.height, nodata_to_value=np.nan).astype(float)
dem, hs, sl = A("DEM_UTM"), A("Hillshade"), A("Slope_Deg")
print("DEM_UTM", d.width, d.height, np.nanmin(dem), np.nanmax(dem), d.extent)
ext = (d.extent.XMin, d.extent.XMax, d.extent.YMin, d.extent.YMax)
fig, axs = plt.subplots(1, 2, figsize=(20, 9), dpi=110)
axs[0].imshow(hs, extent=ext, cmap="gray")
yy = np.linspace(ext[3], ext[2], d.height); xx = np.linspace(ext[0], ext[1], d.width)
cs = axs[0].contour(xx, yy, dem, levels=np.arange(1500, 2320, 20), linewidths=0.4, colors="orange")
axs[0].clabel(cs, levels=np.arange(1500, 2320, 100), fontsize=7, fmt="%d")
axs[1].imshow(np.clip(sl, 0, 30), extent=ext, cmap="viridis")
for ax in axs:
    ax.grid(color="white", alpha=0.3); ax.ticklabel_format(style="plain")
fig.tight_layout(); fig.savefig(os.path.join(ROOT, "explore.png"))
# plain elevation statistics in a ring far from the summit
r, c = np.unravel_index(np.nanargmax(dem), dem.shape)
sx, sy = ext[0] + (c + 0.5) * 10, ext[3] - (r + 0.5) * 10
print("summit", round(float(np.nanmax(dem)), 1), "at", round(sx), round(sy))
Y, X = np.mgrid[0:d.height, 0:d.width]
dist = np.hypot((X - c) * 10, (Y - r) * 10)
for r0 in (4000, 5000, 6000, 8000):
    ring = (dist > r0) & (dist < r0 + 500)
    print("ring", r0, "elev mean/min/max", round(float(np.nanmean(dem[ring])), 1), round(float(np.nanmin(dem[ring])), 1),
          round(float(np.nanmax(dem[ring])), 1), "slope mean", round(float(np.nanmean(sl[ring])), 2))
