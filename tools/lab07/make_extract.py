"""Zip the Little Cottonwood Canyon DEM (from fetch_dem.py) with its READ-ME into
docs/data/lab07-little-cottonwood-dem.zip."""
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\Ames\Lab07\Data\LittleCottonwood_DEM.tif"
OUT = os.path.join(HERE, "..", "..", "docs", "data", "lab07-little-cottonwood-dem.zip")
FOLDER = "lab07-little-cottonwood-dem"

README = """LITTLE COTTONWOOD CANYON DEM - prepared extract for CE 414 Lab 7 (Avalanche Terrain)
==================================================================================

WHAT
  LittleCottonwood_DEM.tif - a bare-earth digital elevation model: one band of 32-bit
  floating-point elevations in METERS above the North American Vertical Datum of 1988 (NAVD 88).
  1,296 columns x 864 rows of 1/3 arc-second cells (about 10.3 m north-south and 7.8 m
  east-west at this latitude). NoData value -999999 (there are no NoData cells in the extract).
  Elevations run from about 2,176 m (the canyon floor at the west edge) to about 3,500 m
  (the summits above Snowbird and Alta).

WHERE
  A rectangle over upper Little Cottonwood Canyon, Salt Lake County, Utah, taking in the
  Snowbird and Alta ski areas: 111.70 W to 111.58 W, 40.53 N to 40.61 N.
  Coordinate system: GCS North American 1983 (latitude/longitude, decimal degrees), exactly as
  the USGS distributes it. Slope and Aspect need a projected coordinate system with meters for
  both the cell size and the elevations; Lab 7, Step 1 projects it.

WHEN
  Source tile USGS_13_n41w112, "current" version, published 2026-05-20 (metadata title
  "USGS 1/3 Arc Second n41w112 20260519"). The seamless 3DEP tile is a mosaic of source data
  collected between 1946 and 2023, and the tile metadata does not say which source covers
  this canyon. Cut for this course on 2026-10-02.

WHY / HOW
  The USGS 3D Elevation Program (3DEP) seamless 1/3 arc-second layer: "best available"
  elevation data of diverse origin (lidar, older contour-derived models, ifsar), resampled to a
  common grid and datum. It is bare earth: it shows the ground surface, not trees, buildings,
  lift towers or the winter snowpack.

WHO
  U.S. Geological Survey, The National Map. Public domain.
  Tile: https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/n41w112/USGS_13_n41w112.tif
  Metadata: https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/n41w112/USGS_13_n41w112.xml

PROCESSING
  1. Read the window above out of the cloud-optimized tile (about 400 MB for the whole
     one-degree tile) over HTTP with rasterio.
  2. Wrote it unchanged - same cells, same values, same coordinate system - as a compressed
     GeoTIFF. Nothing was filled, smoothed, projected or resampled.
  Scripts: tools/lab07/fetch_dem.py and tools/lab07/make_extract.py in the course repo.

THE SKI AREA BOUNDARIES are not in this zip. Lab 7 adds them live from the Utah Geospatial
Resource Center (layer SkiAreaBoundaries); see the lab page.

LICENSE
  U.S. government data, public domain. Credit line:
  "Elevation: USGS 3D Elevation Program, 1/3 arc-second DEM, tile n41w112 (May 2026)."
"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(SRC, f"{FOLDER}/LittleCottonwood_DEM.tif")
    z.writestr(f"{FOLDER}/READ-ME-FIRST.txt", README.replace("\n", "\r\n"))
print(OUT, os.path.getsize(OUT))
