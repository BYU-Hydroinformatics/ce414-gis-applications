r"""Lab 8 extra measurements on the baseline (seed 1, 2,500 points) in C:\Ames\Lab09\Check.gdb:
Kriging's own error estimate (variance raster) against the real error; where the errors are largest
(slope classes); worst-error locations in lat/lon; the true summit and its value in the 3DEP image
service (REST identify). Writes tools/lab08/extra_checks.json."""
import json, math, os, urllib.request, urllib.parse
import arcpy, numpy as np
from arcpy.sa import Kriging, KrigingModelOrdinary, RadiusVariable, Raster, Slope
GDB = r"C:\Ames\Lab09\Check.gdb"
arcpy.CheckOutExtension("Spatial"); arcpy.env.overwriteOutput = True; arcpy.env.workspace = GDB
arcpy.env.snapRaster = arcpy.env.extent = os.path.join(GDB, "True_DEM"); arcpy.env.cellSize = 30
T = Raster(os.path.join(GDB, "True_DEM"))
def A(r):
    """Read a raster on True_DEM's grid (some outputs come out a cell or two larger)."""
    r = Raster(r) if isinstance(r, str) else r
    return arcpy.RasterToNumPyArray(r, arcpy.Point(T.extent.XMin, T.extent.YMin), T.width, T.height, nodata_to_value=np.nan)
out = {}
Kriging("Points_n2500_s1", "RASTERVALU", KrigingModelOrdinary("SPHERICAL"), 30, RadiusVariable(12), "Kriging_Variance")
var = A("Kriging_Variance"); err = A("Error_Kr_n2500_s1_SPH")
ok = np.isfinite(var) & np.isfinite(err)
se = np.sqrt(var[ok]); e = np.abs(err[ok])
out["kriging_se_rms"] = round(float(np.sqrt(np.mean(var[ok]))), 2)
out["kriging_real_rmse"] = round(float(np.sqrt(np.mean(err[ok] ** 2))), 2)
out["corr_se_abs_err"] = round(float(np.corrcoef(se, e)[0, 1]), 3)
out["var_range"] = [round(float(np.nanmin(var)), 1), round(float(np.nanmax(var)), 1)]
slope = A(Slope("True_DEM", "DEGREE"))
for m, r in (("Thiessen", "Error_Th_n2500_s1"), ("IDW", "Error_IDW_n2500_s1_p2"), ("Kriging", "Error_Kr_n2500_s1_SPH")):
    ee = A(r); res = {}
    for lo, hi in ((0, 10), (10, 25), (25, 35), (35, 90)):
        k = np.isfinite(ee) & np.isfinite(slope) & (slope >= lo) & (slope < hi)
        res[f"{lo}-{hi}"] = dict(cells=int(k.sum()), rmse=round(float(np.sqrt(np.mean(ee[k] ** 2))), 1))
    out[f"rmse_by_slope_{m}"] = res
t = A("True_DEM"); ext = Raster("True_DEM").extent
iy, ix = np.unravel_index(np.nanargmax(t), t.shape)
sx, sy = ext.XMin + (ix + .5) * 30, ext.YMax - (iy + .5) * 30
def ll(x, y):
    p = arcpy.PointGeometry(arcpy.Point(x, y), arcpy.SpatialReference(26912)).projectAs(arcpy.SpatialReference(4269))
    return [round(p.firstPoint.Y, 5), round(p.firstPoint.X, 5)]
out["true_max"] = dict(utm=[sx, sy], latlon=ll(sx, sy), z=round(float(np.nanmax(t)), 1))
out["worst_idw_kriging_latlon"] = ll(447570.0, 4456642.0)
out["worst_thiessen_latlon"] = ll(448110.0, 4453642.0)
lat, lon = out["true_max"]["latlon"]
q = urllib.parse.urlencode(dict(geometry=json.dumps(dict(x=lon, y=lat, spatialReference=dict(wkid=4269))),
    geometryType="esriGeometryPoint", returnGeometry="false", returnCatalogItems="false", f="json"))
try:
    j = json.load(urllib.request.urlopen("https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/identify?" + q, timeout=60))
    out["service_value_at_max"] = j.get("value")
except Exception as ex:
    out["service_err"] = str(ex)
json.dump(out, open(os.path.join(os.path.dirname(__file__), "extra_checks.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
