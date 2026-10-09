"""Lab 7 (HAND): fetch the terrain for the Provo River corridor.

1. 3DEP elevation image service (best-available, 1 m lidar here) exported at 2 m in
   NAD 1983 UTM zone 12N (EPSG 26912) over the study box -> C:/Ames/HAND/dem/dem_2m.tif
2. The 1/3 arc-second seamless tile n41w112 (downloaded separately to C:/Ames/HAND/raw/)
   clipped to the same box, kept in its native GCS -> C:/Ames/HAND/dem/dem13_gcs.tif

Run with the ArcGIS Pro python.
"""
import json
import os
import urllib.parse
import urllib.request

import arcpy

BOX_LL = (-111.750, 40.225, -111.650, 40.320)  # lon/lat study box (W, S, E, N)
OUT = r"C:\Ames\HAND\dem"
RAW = r"C:\Ames\HAND\raw"
SVC = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage"
CELL = 2.0
UTM = arcpy.SpatialReference(26912)


def utm_box():
    gcs = arcpy.SpatialReference(4269)
    pts = [arcpy.PointGeometry(arcpy.Point(x, y), gcs).projectAs(UTM)
           for x in BOX_LL[0::2] for y in BOX_LL[1::2]]
    xs = [p.firstPoint.X for p in pts]
    ys = [p.firstPoint.Y for p in pts]
    # snap outward to a 10 m grid so 2, 5 and 10 m grids nest
    import math
    return (math.floor(min(xs) / 10) * 10, math.floor(min(ys) / 10) * 10,
            math.ceil(max(xs) / 10) * 10, math.ceil(max(ys) / 10) * 10)


def main():
    os.makedirs(OUT, exist_ok=True)
    xmin, ymin, xmax, ymax = utm_box()
    w, h = int((xmax - xmin) / CELL), int((ymax - ymin) / CELL)
    params = {
        "bbox": f"{xmin},{ymin},{xmax},{ymax}", "bboxSR": 26912, "imageSR": 26912,
        "size": f"{w},{h}", "format": "tiff", "pixelType": "F32", "noData": -9999,
        "interpolation": "RSP_BilinearInterpolation", "f": "image",
    }
    tif = os.path.join(OUT, "dem_2m.tif")
    if not os.path.exists(tif):
        # the service times out (504) on one 4,300 x 5,300 request: fetch 1,000-pixel tiles
        tiles = []
        step = 1000 * CELL
        y = ymin
        while y < ymax:
            x = xmin
            while x < xmax:
                x2, y2 = min(x + step, xmax), min(y + step, ymax)
                p = dict(params, bbox=f"{x},{y},{x2},{y2}",
                         size=f"{int(round((x2 - x) / CELL))},{int(round((y2 - y) / CELL))}")
                t = os.path.join(OUT, "tiles", f"t_{int(x)}_{int(y)}.tif")
                os.makedirs(os.path.dirname(t), exist_ok=True)
                for attempt in range(4):
                    try:
                        if not os.path.exists(t):
                            urllib.request.urlretrieve(SVC + "?" + urllib.parse.urlencode(p), t)
                        break
                    except Exception as e:  # retry transient 504s
                        print("retry", t, e)
                tiles.append(t)
                x = x2
            y = y2
        arcpy.management.MosaicToNewRaster(tiles, OUT, "dem_2m.tif", UTM, "32_BIT_FLOAT", CELL, 1, "FIRST")
    r = arcpy.Raster(tif)
    info = {"box_utm": [xmin, ymin, xmax, ymax], "size": [w, h],
            "dem_2m": {"cols": r.width, "rows": r.height, "cell": r.meanCellWidth,
                        "min": r.minimum, "max": r.maximum, "sr": r.spatialReference.factoryCode}}
    src = os.path.join(RAW, "USGS_13_n41w112_20260519.tif")
    if os.path.exists(src):
        g = os.path.join(OUT, "dem13_gcs.tif")
        if not os.path.exists(g):
            arcpy.management.Clip(src, " ".join(str(v) for v in BOX_LL), g, "#", "#", "NONE", "NO_MAINTAIN_EXTENT")
        rg = arcpy.Raster(g)
        info["dem13_gcs"] = {"cols": rg.width, "rows": rg.height, "min": rg.minimum, "max": rg.maximum}
    json.dump(info, open(os.path.join(OUT, "dem_info.json"), "w"), indent=2)
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
