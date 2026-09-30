"""Cut the Rock Canyon DEM extract for Lab 5 out of the USGS 1/3 arc-second tile n41w112.

The tile is a cloud-optimized GeoTIFF of about 380 MB. This reads only the window we need over
HTTP and writes it unchanged (same CRS, same cell values, same 1/3 arc-second cells) to
C:\\Ames\\Lab05\\Data\\RockCanyon_DEM.tif. Run with the standalone Python 3.14 (rasterio).
"""
import json
import os

import rasterio
from rasterio.windows import from_bounds

URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/n41w112/USGS_13_n41w112.tif"
# West, south, east, north in decimal degrees (NAD 1983). Rock Canyon's basin sits well inside this box.
BOUNDS = (-111.665, 40.225, -111.515, 40.335)
OUT = r"C:\Ames\Lab05\Data\RockCanyon_DEM.tif"

os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
with rasterio.open("/vsicurl/" + URL) as src:
    win = from_bounds(*BOUNDS, transform=src.transform).round_offsets().round_lengths()
    data = src.read(1, window=win)
    profile = src.profile.copy()
    profile.update(width=win.width, height=win.height, transform=src.window_transform(win),
                   compress="deflate", predictor=3, tiled=True, blockxsize=256, blockysize=256)
    profile.pop("photometric", None)
    tags = src.tags()
    crs = src.crs.to_wkt()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with rasterio.open(OUT, "w", **profile) as dst:
    dst.write(data, 1)
nod = profile.get("nodata")
valid = data[data != nod] if nod is not None else data
info = dict(width=win.width, height=win.height, dtype=str(data.dtype), nodata=nod,
            min=float(valid.min()), max=float(valid.max()), bounds=list(rasterio.windows.bounds(win, src.transform)),
            res=list(src.res), bytes=os.path.getsize(OUT), tags=tags)
print(json.dumps(info, indent=1))
print(crs[:200])
