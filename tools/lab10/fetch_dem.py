r"""Cut the Y Mountain DEM extract for Lab 10 out of the USGS 1/3 arc-second 3DEP tile n41w112.

The window runs from the BYU campus on the valley floor, up the mountain front past the Y, to the
summit of Y Mountain and the head of Slide Canyon, so the surface has flat ground, a steep front
and a summit ridge for the interpolators to struggle with. Cell values, cell size and coordinate
system are unchanged. Writes C:\Ames\Lab09\Data\YMountain_DEM.tif.
Run with the standalone Python 3.14 (rasterio).
"""
import json
import os

import rasterio
from rasterio.windows import from_bounds

URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/n41w112/USGS_13_n41w112.tif"
# West, south, east, north (NAD 1983 degrees).
BOUNDS = (-111.68, 40.20, -111.57, 40.27)
OUT = r"C:\Ames\Lab09\Data\YMountain_DEM.tif"

os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
with rasterio.open("/vsicurl/" + URL) as src:
    win = from_bounds(*BOUNDS, transform=src.transform).round_offsets().round_lengths()
    data = src.read(1, window=win)
    profile = src.profile.copy()
    profile.update(width=win.width, height=win.height, transform=src.window_transform(win),
                   compress="deflate", predictor=3, tiled=True, blockxsize=256, blockysize=256)
    profile.pop("photometric", None)
    desc = src.tags().get("TIFFTAG_IMAGEDESCRIPTION", "")
    tags = src.tags()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with rasterio.open(OUT, "w", **profile) as dst:
    dst.write(data, 1)
nod = profile.get("nodata")
v = data[data != nod]
print(json.dumps(dict(width=int(win.width), height=int(win.height), nodata=nod,
                      nodata_cells=int((data == nod).sum()), min=float(v.min()), max=float(v.max()),
                      res=[profile["transform"].a, -profile["transform"].e], bytes=os.path.getsize(OUT),
                      description=desc, tags=tags), indent=1), flush=True)
os._exit(0)
