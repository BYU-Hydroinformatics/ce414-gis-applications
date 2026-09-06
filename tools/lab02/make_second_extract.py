# Build the second prepared extract for Lab 2: red and NIR of one Landsat 8 scene clipped to a
# study box, scaled to surface reflectance, floored at 0, stored as reflectance x 10,000 (S16, LZW),
# with the scene's MTL and a READ-ME, zipped into docs/data/.
#   python make_second_extract.py <scene_dir> <lon_min> <lat_min> <lon_max> <lat_max> <area_name> <zip_basename>
import arcpy, os, sys, re, zipfile, datetime
from arcpy.sa import *

scene_dir, area = sys.argv[1], sys.argv[6]
lon0, lat0, lon1, lat1 = map(float, sys.argv[2:6])
zip_base = sys.argv[7]
arcpy.CheckOutExtension("Spatial"); arcpy.env.overwriteOutput = True
arcpy.env.compression = "LZW"
mtl = [f for f in os.listdir(scene_dir) if f.endswith("_MTL.txt")][0]
txt = open(os.path.join(scene_dir, mtl)).read()
pid = re.search(r'LANDSAT_PRODUCT_ID = "(LC0\d_L2SP[^"]+)"', txt).group(1)
mult = float(re.search(r"REFLECTANCE_MULT_BAND_4 = ([-\d.eE]+)", txt).group(1))
add = float(re.search(r"REFLECTANCE_ADD_BAND_4 = ([-\d.eE]+)", txt).group(1))
acq = re.search(r"DATE_ACQUIRED = (\S+)", txt).group(1)
ctime = re.search(r'SCENE_CENTER_TIME = "([^"]+)"', txt).group(1)[:8]
cloud = re.search(r"CLOUD_COVER = ([\d.]+)", txt).group(1)
zone = re.search(r"UTM_ZONE = (\d+)", txt).group(1)
path_, row_ = re.search(r"WRS_PATH = (\d+)", txt).group(1), re.search(r"WRS_ROW = (\d+)", txt).group(1)
b4 = [f for f in os.listdir(scene_dir) if f.endswith("_SR_B4.TIF")][0]
b5 = [f for f in os.listdir(scene_dir) if f.endswith("_SR_B5.TIF")][0]
out_dir = os.path.join(os.path.dirname(scene_dir.rstrip("\\/")), zip_base)
os.makedirs(out_dir, exist_ok=True)
sr = arcpy.Describe(os.path.join(scene_dir, b4)).spatialReference
# study box: geographic corners projected to the scene's UTM zone, then the enclosing rectangle
pts = [arcpy.PointGeometry(arcpy.Point(x, y), arcpy.SpatialReference(4326)).projectAs(sr).firstPoint
       for x, y in ((lon0, lat0), (lon1, lat0), (lon1, lat1), (lon0, lat1))]
xs, ys = [p.X for p in pts], [p.Y for p in pts]
ext = "%f %f %f %f" % (min(xs), min(ys), max(xs), max(ys))
print("scene", pid, "zone", zone, "box", ext)
names = {}
for band, src, label in (("B4", b4, "Red"), ("B5", b5, "NIR")):
    clip = os.path.join(out_dir, "tmp_%s.tif" % band)
    arcpy.management.Clip(os.path.join(scene_dir, src), ext, clip, "#", "0", "NONE", "NO_MAINTAIN_EXTENT")
    r = Raster(clip)
    refl = Float(r) * mult + add
    refl = Con(refl < 0, 0, refl)               # floor the few negatives (deep water, shadow) at 0
    scaled = Int(refl * 10000 + 0.5)
    scaled = SetNull(IsNull(r) | (r == 0), scaled)  # keep the scene's fill as NoData
    out = os.path.join(out_dir, "%s_%s_%s_SR_x10000.tif" % (area, label, band))
    arcpy.management.CopyRaster(scaled, out, pixel_type="16_BIT_SIGNED", nodata_value="-32768", format="TIFF")
    arcpy.management.CalculateStatistics(out)
    a = arcpy.RasterToNumPyArray(out, nodata_to_value=-32768)
    nd = (a == -32768).mean()
    print(label, out, a.shape, "NoData fraction %.3f" % nd, "min %d max %d" % (a[a > -32768].min(), a[a > -32768].max()))
    names[label] = os.path.basename(out)
    arcpy.management.Delete(clip)
    for junk in (out + ".aux.xml", out + ".ovr", out + ".vat.dbf", out + ".vat.cpg"):
        pass
readme = """READ-ME-FIRST.txt  --  Lab 2 second prepared extract: Landsat 8 red and near-infrared bands, {area_h}
=====================================================================================================

WHAT THIS IS
  Two single-band GeoTIFF rasters clipped to a study box over {area_h}, from one Landsat 8 scene:
    {red}   Band 4 (red,  0.64-0.67 um) surface reflectance x 10,000
    {nir}   Band 5 (NIR,  0.85-0.88 um) surface reflectance x 10,000
  Pixel type 16-bit signed integer, cell size 30 m, NoData = -32768.
  Coordinate system: WGS 1984 UTM Zone {zone}N, exactly as USGS delivers the scene. NOTE: this is a
  different UTM zone from the Utah County extract (zone 12). ArcGIS Pro projects on the fly for
  display, but the model's Output Coordinate System environment decides what your outputs get.
  Study box (WGS 84): longitude {lon0} to {lon1}, latitude {lat0} to {lat1}.

WHERE IT CAME FROM
  Product ID:      {pid}
  Satellite/sensor Landsat 8, OLI/TIRS
  Acquired:        {acq}, {ctime} UTC, WRS-2 path {path} row {row}
  Processing:      Collection 2, Level-2 Science Product (surface reflectance), Tier 1
  Cloud cover:     {cloud} percent (whole scene)
  Source:          U.S. Geological Survey, distributed through the Microsoft Planetary Computer
                   mirror of the USGS Landsat Collection 2 archive. Retrieved {today}.
  License:         Landsat data are in the public domain (no restrictions). Please credit
                   "Landsat 8 image courtesy of the U.S. Geological Survey."
  The scene's original metadata file is included unchanged: {mtl}

WHAT WE DID TO IT
  1. Clipped bands 4 and 5 to the study box (Clip, cell alignment unchanged).
  2. Applied the Collection 2 Level-2 reflectance scale factor and offset from the metadata file:
        reflectance = DN x {mult} + ({add})
  3. Floored the handful of slightly negative reflectance values at 0 (the Utah County extract does the same).
  4. Multiplied by 10,000 and stored as 16-bit signed integers, LZW compressed.

WHAT WE DID NOT DO
  No resampling, no reprojection, no cloud masking, no filtering. The bands are still integers, so the
  Float step in the lab is still necessary.

HOW TO CITE
  U.S. Geological Survey (2025). Landsat 8 OLI/TIRS Collection 2 Level-2 Surface Reflectance,
  scene {pid}. Extract prepared for BYU CE 414, 2026.
""".format(area_h=area.replace("_", " "), red=names["Red"], nir=names["NIR"], zone=zone, lon0=lon0, lon1=lon1, lat0=lat0, lat1=lat1,
           pid=pid, acq=acq, ctime=ctime, path=path_, row=row_, cloud=cloud, today=datetime.date.today(), mtl=mtl, mult=mult, add=add)
open(os.path.join(out_dir, "READ-ME-FIRST.txt"), "w").write(readme)
zip_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "docs", "data", zip_base + ".zip"))
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(out_dir, "READ-ME-FIRST.txt"), "READ-ME-FIRST.txt")
    z.write(os.path.join(scene_dir, mtl), mtl)
    for label in ("Red", "NIR"):
        z.write(os.path.join(out_dir, names[label]), names[label])
print("zip", zip_path, os.path.getsize(zip_path) // 1_000_000, "MB")
