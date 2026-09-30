"""Zip the Rock Canyon DEM (from fetch_dem.py) with its READ-ME into docs/data/lab05-rock-canyon-dem.zip."""
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\Ames\Lab05\Data\RockCanyon_DEM.tif"
OUT = os.path.join(HERE, "..", "..", "docs", "data", "lab05-rock-canyon-dem.zip")
FOLDER = "lab05-rock-canyon-dem"

README = """ROCK CANYON DEM - prepared extract for CE 414 Lab 5 (Watershed Delineation)
============================================================================

WHAT
  RockCanyon_DEM.tif - a bare-earth digital elevation model: one band of 32-bit floating-point
  elevations in METERS above the North American Vertical Datum of 1988 (NAVD 88).
  1,620 columns x 1,188 rows of 1/3 arc-second cells (about 10 m north-south, 7.9 m east-west
  at this latitude). NoData value -999999 (there are no NoData cells in the extract).
  Elevations run from about 1,376 m (the east bench of Provo) to about 3,371 m (Provo Peak).

WHERE
  A rectangle over Rock Canyon, on the east side of Provo, Utah County, Utah:
  111.665 W to 111.515 W, 40.225 N to 40.335 N.
  Coordinate system: GCS North American 1983 (latitude/longitude, decimal degrees), exactly as
  the USGS distributes it. Project it before you measure any distance or area (Lab 5, Step 1).

WHEN
  Source tile USGS_13_n41w112, "current" version, published 2026-05-20 (metadata title
  "USGS 1/3 Arc Second n41w112 20260519"). The seamless 3DEP tile is a mosaic of source data
  collected between 1946 and 2023; the tile metadata does not say which source covers
  Rock Canyon. Cut for this course on 2026-09-29.

WHY / HOW
  The USGS 3D Elevation Program (3DEP) seamless 1/3 arc-second layer: "best available"
  elevation data of diverse origin (lidar, older contour-derived models, ifsar), resampled to a
  common grid and datum. It is bare earth (buildings and trees removed) and hydro-flattened
  (lakes and wide rivers are flat).

WHO
  U.S. Geological Survey, The National Map. Public domain.
  Tile: https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/n41w112/USGS_13_n41w112.tif
  Metadata: https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/n41w112/USGS_13_n41w112.xml

PROCESSING
  1. Read the window above out of the cloud-optimized tile (about 380 MB for the whole
     one-degree tile) over HTTP with rasterio.
  2. Wrote it unchanged - same cells, same values, same coordinate system - as a compressed
     GeoTIFF. Nothing was filled, smoothed, projected or resampled.
  Scripts: tools/lab05/fetch_dem.py and tools/lab05/make_extract.py in the course repo.

LICENSE
  U.S. government data, public domain. Credit line:
  "Elevation: USGS 3D Elevation Program, 1/3 arc-second DEM, tile n41w112 (May 2026)."
"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(SRC, f"{FOLDER}/RockCanyon_DEM.tif")
    z.writestr(f"{FOLDER}/READ-ME-FIRST.txt", README.replace("\n", "\r\n"))
print(OUT, os.path.getsize(OUT))
