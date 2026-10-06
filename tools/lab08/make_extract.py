"""Zip the Big Southern Butte DEM (from fetch_dem.py) and the reference outline (from
make_outline.py) with a READ-ME into docs/data/lab08-big-southern-butte.zip. ArcGIS Pro Python."""
import os
import shutil
import zipfile

import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
DEM = r"C:\Ames\Lab08\Data\BigSouthernButte_DEM.tif"
CHECK = r"C:\Ames\Lab08\Check.gdb"
STAGE = r"C:\Ames\Lab08\Stage"
OUT = os.path.join(HERE, "..", "..", "docs", "data", "lab08-big-southern-butte.zip")
FOLDER = "lab08-big-southern-butte"

README = """BIG SOUTHERN BUTTE - prepared data for CE 414 Lab 8 (Butte Volume)
=================================================================

WHAT
  BigSouthernButte_DEM.tif - a bare-earth digital elevation model: one band of 32-bit
  floating-point elevations in METERS above the North American Vertical Datum of 1988 (NAVD 88).
  3,024 columns x 1,836 rows of 1/3 arc-second cells (about 10.3 m north-south and 7.5 m
  east-west at this latitude). There are no NoData cells in the extract.
  Elevations run from about 1,500 m (the plain at the north edge) to about 2,307 m (the summit).

  Lab08.gdb / Butte_Boundary - one polygon, the reference outline of the base of the butte
  (28.03 square kilometers), in NAD 1983 UTM Zone 12N. It was derived from the DEM, not
  digitized; see PROCESSING. Lab 8 asks you to draw your own outline as well and compare.

WHERE
  A rectangle over Big Southern Butte on the eastern Snake River Plain, Butte County, Idaho:
  113.17 W to 112.89 W, 43.32 N to 43.49 N. The butte is near the middle; the small raised
  feature near the east edge is a separate landform and is not part of the lab.
  DEM coordinate system: GCS North American 1983 (latitude/longitude, decimal degrees), exactly
  as the USGS distributes it. A volume needs meters in both the cell size and the elevations;
  Lab 8, Step 1 projects it.

WHEN
  Source tiles USGS_13_n44w114 and USGS_13_n44w113, "current" versions, both published
  2026-04-07 (metadata titles "USGS 1/3 Arc Second n44w114 20260407" and "... n44w113
  20260407"). The seamless 3DEP tiles are mosaics of source data; the tile metadata gives source
  dates of 1957-2024 for n44w114 and 2019-2024 for n44w113 without saying which source covers
  the butte. Cut for this course on 2026-10-05.

WHY / HOW
  The USGS 3D Elevation Program (3DEP) seamless 1/3 arc-second layer: "best available"
  elevation data of diverse origin, resampled to a common grid and datum. It is bare earth.
  The butte straddles the 113 W tile edge, so the window comes from two tiles.

WHO
  U.S. Geological Survey, The National Map. Public domain.
  https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/n44w114/USGS_13_n44w114.tif
  https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/n44w113/USGS_13_n44w113.tif
  (metadata: the same addresses ending in .xml)

PROCESSING
  DEM
  1. Read the window above out of each cloud-optimized tile over HTTP with rasterio.
  2. Joined the two pieces edge to edge and wrote them unchanged - same cells, same values, same
     coordinate system - as one compressed GeoTIFF. Nothing was filled, smoothed or resampled.
  Butte_Boundary
  1. Projected the DEM to NAD 1983 UTM Zone 12N at 10 m (bilinear).
  2. Fitted a least-squares plane to the plain in a ring 4.5-8 km from the summit. The plain
     falls about 5.4 m per kilometer toward the north.
  3. Kept the connected cells standing more than 10 m above that plane around the summit,
     filled holes, converted them to a polygon and smoothed it (PAEK, 200 m).
  It is a reasonable base, not the only one: a 5 m threshold leaks out along lava flows to the
  south; 20 m gives 24.6 square kilometers.
  Scripts: tools/lab08/fetch_dem.py, make_outline.py and make_extract.py in the course repo.

LICENSE
  U.S. government data, public domain. Credit line:
  "Elevation: USGS 3D Elevation Program, 1/3 arc-second DEM, tiles n44w114 and n44w113 (April 2026)."
"""

arcpy.env.overwriteOutput = True
if os.path.exists(STAGE):
    shutil.rmtree(STAGE)
os.makedirs(STAGE)
arcpy.management.CreateFileGDB(STAGE, "Lab08.gdb")
gdb = os.path.join(STAGE, "Lab08.gdb")
arcpy.conversion.ExportFeatures(os.path.join(CHECK, "Butte_Boundary"), os.path.join(gdb, "Butte_Boundary"))
arcpy.management.ClearWorkspaceCache()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(DEM, f"{FOLDER}/BigSouthernButte_DEM.tif")
    for f in sorted(os.listdir(gdb)):
        if not f.endswith(".lock"):
            z.write(os.path.join(gdb, f), f"{FOLDER}/Lab08.gdb/{f}")
    z.writestr(f"{FOLDER}/READ-ME-FIRST.txt", README.replace("\n", "\r\n"))
print(OUT, os.path.getsize(OUT))
