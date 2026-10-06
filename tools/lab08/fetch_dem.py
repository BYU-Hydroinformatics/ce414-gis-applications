"""Cut the Big Southern Butte DEM extract for Lab 8 out of the USGS 1/3 arc-second 3DEP tiles.

The butte (43.40 N, 113.03 W) sits beside the 113 W tile edge, so the window is read from tiles
n44w114 and n44w113 over HTTP and the two pieces are joined edge to edge. Cell values, cell size and
coordinate system are unchanged. Writes C:\\Ames\\Lab08\\Data\\BigSouthernButte_DEM.tif.
Run with the standalone Python 3.14 (rasterio).
"""
import json
import os

import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.windows import from_bounds

TILES = ["n44w114", "n44w113"]
URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/{t}/USGS_13_{t}.tif"
# West, south, east, north (NAD 1983 degrees): the butte with a wide margin of plain around it.
BOUNDS = (-113.17, 43.32, -112.89, 43.49)
OUT = r"C:\Ames\Lab08\Data\BigSouthernButte_DEM.tif"

os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
srcs = [rasterio.open("/vsicurl/" + URL.format(t=t)) for t in TILES]
data, transform = merge(srcs, bounds=BOUNDS, nodata=srcs[0].nodata)
profile = srcs[0].profile.copy()
profile.update(width=data.shape[2], height=data.shape[1], transform=transform, count=1,
               compress="deflate", predictor=3, tiled=True, blockxsize=256, blockysize=256)
profile.pop("photometric", None)
tags = {t: s.tags() for t, s in zip(TILES, srcs)}
for s in srcs:
    s.close()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with rasterio.open(OUT, "w", **profile) as dst:
    dst.write(data[0], 1)
nod = profile.get("nodata")
v = data[0][data[0] != nod]
print(json.dumps(dict(width=int(data.shape[2]), height=int(data.shape[1]), nodata=nod,
                      nodata_cells=int((data[0] == nod).sum()), min=float(v.min()), max=float(v.max()),
                      res=[transform.a, -transform.e], bytes=os.path.getsize(OUT),
                      titles={t: tg.get("TIFFTAG_IMAGEDESCRIPTION", "") for t, tg in tags.items()}), indent=1), flush=True)
os._exit(0)   # skip GDAL's slow /vsicurl/ teardown (Lab 7's fetch hung here)
