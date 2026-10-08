r"""Zip the Y Mountain DEM (from fetch_dem.py) and the prepared Lab09.gdb (True_DEM, Study_Area and three
sample-point sets, all from run_model.py at seed 1) with a READ-ME into docs/data/lab09-y-mountain.zip.
ArcGIS Pro Python; run run_model.py first."""
import os
import shutil
import zipfile

import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
DEM = r"C:\Ames\Lab09\Data\YMountain_DEM.tif"
CHECK = r"C:\Ames\Lab09\Check.gdb"
STAGE = r"C:\Ames\Lab09\Stage"
OUT = os.path.join(HERE, "..", "..", "docs", "data", "lab09-y-mountain.zip")
FOLDER = "lab09-y-mountain"

README = """Y MOUNTAIN - prepared data for CE 414 Lab 9 (Interpolation Explorer)
==================================================================

WHAT
  YMountain_DEM.tif - a bare-earth digital elevation model: one band of 32-bit floating-point
  elevations in METERS above the North American Vertical Datum of 1988 (NAVD 88).
  1,188 columns x 756 rows of 1/3 arc-second cells (about 10.3 m north-south and 7.9 m
  east-west at this latitude). There are no NoData cells in the extract.
  Elevations run from about 1,368 m (the valley floor in Provo) to about 2,897 m (the ridge
  in the southeast corner).

  You do not need the .tif to build the model. It is the source everything in Lab09.gdb was made
  from, kept so you can read its metadata (Lab 9, Figure A) and compare it with the web service
  (Lab 9, Step 1).

  Lab09.gdb / True_DEM - the DEM projected to NAD 1983 UTM Zone 12N with 30 m cells and cut to
  the study rectangle: 67,337 cells, 1,368.5 to 2,896.5 m. This is "the truth" in Lab 9.

  Lab09.gdb / Study_Area - one rectangle, 8.67 km x 6.99 km (60.6 square kilometers), in
  NAD 1983 UTM Zone 12N, with its edges on the 30 m grid of True_DEM, so every cell inside it is
  whole. It is the area the points sample and the area every error is measured over.

  Lab09.gdb / Sample_Points_250, Sample_Points_2500, Sample_Points_10000 - random points inside
  Study_Area (250, 2,500 and 10,000 of them), each carrying the True_DEM cell value under it in
  the field RASTERVALU (meters). These are the samples you interpolate from.

WHERE
  Provo, Utah County, Utah: the BYU campus and the valley floor in the west, the mountain front
  with the block Y, Y Mountain and the mouth of Rock Canyon in the east.
  111.68 W to 111.57 W, 40.20 N to 40.27 N.
  DEM coordinate system: GCS North American 1983 (latitude/longitude, decimal degrees), exactly
  as the USGS distributes it. Everything in Lab09.gdb is in NAD 1983 UTM Zone 12N.

WHEN
  Source tile USGS_13_n41w112, "current" version, published 2026-05-20 (metadata title
  "USGS 1/3 Arc Second n41w112 20260519"). The seamless 3DEP tiles are mosaics of source data;
  the tile metadata gives source dates of 1946-2023 without saying which source covers Provo.
  Cut for this course on 2026-10-06.

WHY / HOW
  The USGS 3D Elevation Program (3DEP) seamless 1/3 arc-second layer: "best available"
  elevation data of diverse origin, resampled to a common grid and datum. It is bare earth.
  In Lab 9 it plays the part of the truth: you sample it, rebuild it from the samples, and
  measure how far each rebuild is from it.

WHO
  U.S. Geological Survey, The National Map. Public domain.
  https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/n41w112/USGS_13_n41w112.tif
  (metadata: the same address ending in .xml)
  The same elevations are served live by the 3DEP elevation image service, which Lab 9, Step 1
  looks at:
  https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer

PROCESSING
  DEM
  1. Read the window above out of the cloud-optimized tile over HTTP with rasterio.
  2. Wrote it unchanged - same cells, same values, same coordinate system - as a compressed
     GeoTIFF. Nothing was filled, smoothed or resampled.
  True_DEM and Study_Area
  1. Project Raster: NAD 1983 UTM Zone 12N, bilinear resampling, 30 m cells (314 x 262 cells).
     The thin wedges of NoData along its edges come from tilting a latitude/longitude rectangle.
  2. Drew a rectangle well inside it, with its corners on that 30 m grid (Study_Area).
  3. Extract by Mask with Study_Area gave True_DEM.
  Sample points
  4. Create Random Points inside Study_Area, Random Number Generator seed 1 (ACM collected
     algorithm 599), 250, 2,500 and 10,000 points.
  5. Extract Values to Points from True_DEM, which writes RASTERVALU; the CID field Create Random
     Points adds was deleted.
  Scripts: tools/lab09/fetch_dem.py, run_model.py and make_extract.py in the course repo.

LICENSE
  U.S. government data, public domain. Credit line:
  "Elevation: USGS 3D Elevation Program, 1/3 arc-second DEM, tile n41w112 (May 2026)."
"""

arcpy.env.overwriteOutput = True
if os.path.exists(STAGE):
    shutil.rmtree(STAGE)
os.makedirs(STAGE)
arcpy.management.CreateFileGDB(STAGE, "Lab09.gdb")
gdb = os.path.join(STAGE, "Lab09.gdb")
arcpy.conversion.ExportFeatures(os.path.join(CHECK, "Study_Area"), os.path.join(gdb, "Study_Area"))
arcpy.management.CopyRaster(os.path.join(CHECK, "True_DEM"), os.path.join(gdb, "True_DEM"))
for n in (250, 2500, 10000):
    out = os.path.join(gdb, f"Sample_Points_{n}")
    arcpy.conversion.ExportFeatures(os.path.join(CHECK, f"Points_n{n}_s1"), out)
    arcpy.management.DeleteField(out, "CID")
    print(out, arcpy.management.GetCount(out)[0], [f.name for f in arcpy.ListFields(out)])
arcpy.management.ClearWorkspaceCache()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(DEM, f"{FOLDER}/YMountain_DEM.tif")
    for f in sorted(os.listdir(gdb)):
        if not f.endswith(".lock"):
            z.write(os.path.join(gdb, f), f"{FOLDER}/Lab09.gdb/{f}")
    z.writestr(f"{FOLDER}/READ-ME-FIRST.txt", README.replace("\n", "\r\n"))
print(OUT, os.path.getsize(OUT))
