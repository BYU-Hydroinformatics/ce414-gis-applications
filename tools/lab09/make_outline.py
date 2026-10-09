"""Derive the reference butte outline for Lab 9 from the DEM itself, so the check values rest on
a reproducible boundary rather than on someone's digitizing.

Method: fit a least-squares plane to the plain in a ring 4.5-8 km from the summit (the plain tilts
gently), take height above that plane, keep the connected region of cells more than THRESH m above
it that holds the summit, fill holes, and convert to a simplified polygon. Writes Butte_Boundary and
Points_Boundary (Butte_Boundary buffered by BUF m) to C:\\Ames\\Lab08\\Check.gdb.
ArcGIS Pro Python; run tools/lab09/explore.py first (it makes DEM_UTM).
"""
import json
import os
import sys

import arcpy
import numpy as np
from scipy import ndimage

THRESH = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0
BUF = 1500
GDB = r"C:\Ames\Lab08\Check.gdb"
arcpy.env.overwriteOutput = True
arcpy.env.workspace = GDB
d = arcpy.Raster(os.path.join(GDB, "DEM_UTM"))
ll = arcpy.Point(d.extent.XMin, d.extent.YMin)
dem = arcpy.RasterToNumPyArray(d, ll, d.width, d.height, nodata_to_value=np.nan).astype(float)
cs = d.meanCellWidth
rows, cols = np.mgrid[0:d.height, 0:d.width]
X = d.extent.XMin + (cols + 0.5) * cs
Y = d.extent.YMax - (rows + 0.5) * cs
r, c = np.unravel_index(np.nanargmax(dem), dem.shape)
dist = np.hypot(X - X[r, c], Y - Y[r, c])
ring = (dist > 4500) & (dist < 8000) & np.isfinite(dem)
A = np.column_stack([X[ring] - X[r, c], Y[ring] - Y[r, c], np.ones(ring.sum())])
coef, *_ = np.linalg.lstsq(A, dem[ring], rcond=None)
plane = coef[0] * (X - X[r, c]) + coef[1] * (Y - Y[r, c]) + coef[2]
h = dem - plane
lab, n = ndimage.label(np.nan_to_num(h, nan=-1) > THRESH)
mask = ndimage.binary_fill_holes(lab == lab[r, c])
mask = ndimage.binary_opening(mask, iterations=3)          # drop one-cell spurs
mask = ndimage.binary_fill_holes(mask)
lab2, _ = ndimage.label(mask)
mask = lab2 == lab2[r, c]
ras = arcpy.NumPyArrayToRaster(mask.astype(np.uint8), ll, cs, cs, 0)
arcpy.management.DefineProjection(ras, d.spatialReference)
ras.save(os.path.join(GDB, "OutlineCells"))
arcpy.conversion.RasterToPolygon(os.path.join(GDB, "OutlineCells"), "Outline_raw", "SIMPLIFY", "Value")
arcpy.cartography.SmoothPolygon("Outline_raw", "Butte_Boundary", "PAEK", "200 Meters")
arcpy.management.DeleteField("Butte_Boundary", ["gridcode", "Id", "InPoly_FID", "SmoPgnFlag"])
arcpy.analysis.Buffer("Butte_Boundary", "Points_Boundary", f"{BUF} Meters", dissolve_option="ALL")
area = sum(row[0] for row in arcpy.da.SearchCursor("Butte_Boundary", ["SHAPE@AREA"]))
pb = sum(row[0] for row in arcpy.da.SearchCursor("Points_Boundary", ["SHAPE@AREA"]))
ext = arcpy.Describe("Butte_Boundary").extent
print(json.dumps(dict(thresh_m=THRESH, plane_slope_e_per_km=round(coef[0] * 1000, 2), plane_slope_n_per_km=round(coef[1] * 1000, 2),
                      plane_at_summit=round(coef[2], 1), ring_resid_sd=round(float(np.std(dem[ring] - plane[ring])), 2),
                      outline_km2=round(area / 1e6, 3), points_boundary_km2=round(pb / 1e6, 3),
                      outline_extent=[round(ext.XMin), round(ext.YMin), round(ext.XMax), round(ext.YMax)],
                      volume_above_plane_km3_cells=round(float(np.nansum(np.where(mask, h, 0)) * cs * cs / 1e9), 3)), indent=1))
