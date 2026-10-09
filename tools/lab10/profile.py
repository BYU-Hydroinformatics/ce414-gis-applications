r"""Figure B data: an east-west profile across the study area through the true DEM and the three
250-point rebuilds (seed 1) left in C:\Ames\Lab09\Check.gdb by run_model.py, plus the 250 sample
points within 150 m of the line. Writes tools/lab10/profile.json for make_svgs.py."""
import json, os, sys
import arcpy, numpy as np
from arcpy.sa import Raster
GDB = r"C:\Ames\Lab09\Check.gdb"
Y = float(sys.argv[1]) if len(sys.argv) > 1 else 4454000.0
T = Raster(os.path.join(GDB, "True_DEM"))
def row(name):
    r = Raster(os.path.join(GDB, name))
    a = arcpy.RasterToNumPyArray(r, arcpy.Point(T.extent.XMin, T.extent.YMin), T.width, T.height, nodata_to_value=np.nan)
    i = int((T.extent.YMax - Y) // 30)
    return [None if np.isnan(v) else round(float(v), 1) for v in a[i]]
out = dict(y=Y, x0=T.extent.XMin + 15, dx=30,
           true=row("True_DEM"), thiessen=row("Thiessen_n250_s1"), idw=row("IDW_n250_s1_p2"), kriging=row("Kriging_n250_s1_SPH"))
out["points"] = [(round(x, 1), round(z, 1)) for x, y, z in arcpy.da.SearchCursor(os.path.join(GDB, "Points_n250_s1"), ["SHAPE@X", "SHAPE@Y", "RASTERVALU"]) if abs(y - Y) < 150]
p = arcpy.PointGeometry(arcpy.Point(T.extent.XMin, Y), arcpy.SpatialReference(26912)).projectAs(arcpy.SpatialReference(4269))
out["lat"] = round(p.firstPoint.Y, 4)
json.dump(out, open(os.path.join(os.path.dirname(__file__), "profile.json"), "w"))
t = [v for v in out["true"] if v is not None]
print(Y, out["lat"], len(t), min(t), max(t), len(out["points"]))
