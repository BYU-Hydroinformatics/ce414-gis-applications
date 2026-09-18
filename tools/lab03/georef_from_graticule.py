#!/usr/bin/env python3
"""Georeference the 1852 Stansbury sheet from its own printed graticule, and check the result.

Run with the ArcGIS Pro Python (numpy and Pillow are both in arcgispro-py3):

    "C:/Program Files/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe" \
        tools/lab03/georef_from_graticule.py

Writes stansbury_gsl_1852.jgw and .prj beside the image. The findings this produced, and the
longitude error it exposed, are written up in GEOREF_FINDINGS.md. Nothing here touches the ArcGIS
Pro GUI; it is all arithmetic on the scan.

Method, in three steps:
  1. find the graticule lines by intensity profile across blank bands of the sheet,
  2. fit each set as an arithmetic ladder, rejecting map content and fold lines,
  3. anchor the ladders to the degree labels read off the printed borders.

The ladders validate each other: the ratio of the longitude and latitude spacings should equal the
cosine of the sheet's mid latitude, and it does, to half a percent.
"""
import os
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

IMAGE = r"C:\Ames\Lab03\Data\stansbury_gsl_1852.jpg"

# Anchors read off the printed borders. The longitude ladder line at x = 3161 carries the
# "113 deg 0'" label; the latitude ladder line at y = 478 carries the "42 deg" label.
LON_ANCHOR_X, LON_ANCHOR = 3161.0, -113.0
LAT_ANCHOR_Y, LAT_ANCHOR = 478.0, 42.0
LON_PX_PER_10MIN, LAT_PX_PER_10MIN = 686.5, 916.0
MID_LATITUDE = 41.1

# Reference coordinates for the check, from Wikipedia's coordinate data. Scan positions were read
# off ruled crops of the sheet and carry roughly +/- 60 px (about 1 km) of estimation error.
CHECKS = [
    # name, scan x, scan y, true lon, true lat
    ("Utah Lake",       7635, 10150, -111.80000, 40.22000),
    ("Antelope Island", 5655,  6200, -112.21389, 40.95833),
    ("Promontory Point", 4657,  4814, -112.41139, 41.22222),
]


def find_lines(profile, prominence=3.0, min_sep=300):
    """Positions darker than the local background by `prominence`, at least `min_sep` apart."""
    background = np.convolve(profile, np.ones(151) / 151, mode="same")
    darkness = background - profile
    keep = []
    for i in np.argsort(-darkness):
        if darkness[i] < prominence:
            break
        if all(abs(i - j) >= min_sep for j in keep):
            keep.append(int(i))
    return sorted(keep)


def fit_ladder(candidates, step_lo, step_hi, tolerance=25):
    """Best arithmetic ladder through the candidates; map content and folds fall off it."""
    best = None
    for start in candidates:
        for step in np.arange(step_lo, step_hi, 0.5):
            on = [c for c in candidates if abs(round((c - start) / step) - (c - start) / step) * step < tolerance]
            if best is None or len(on) > len(best[2]):
                best = (start, step, on)
    return best


def main():
    image = Image.open(IMAGE).convert("L")
    a = np.asarray(image, dtype=np.float32)
    height, width = a.shape
    print(f"scan {width} x {height}")

    rows = find_lines(a[:, 900:2200].mean(axis=1))
    cols = find_lines(a[350:1500, :].mean(axis=0))
    _, lat_step, lat_on = fit_ladder(rows, 880, 960)
    _, lon_step, lon_on = fit_ladder(cols, 660, 720)
    print(f"latitude  ladder: {lat_step:6.1f} px per 10', {len(lat_on)} lines")
    print(f"longitude ladder: {lon_step:6.1f} px per 10', {len(lon_on)} lines")
    ratio, expected = lon_step / lat_step, np.cos(np.radians(MID_LATITUDE))
    print(f"ratio {ratio:.4f} against cos({MID_LATITUDE}) = {expected:.4f} "
          f"-- {abs(ratio - expected) / expected * 100:.1f}% apart")

    # The published world file uses the hand-read spacings above, not the re-fitted ones, so that
    # the numbers in GEOREF_FINDINGS.md and the .jgw on disk cannot drift apart.
    dlon = (10.0 / 60.0) / LON_PX_PER_10MIN
    dlat = -(10.0 / 60.0) / LAT_PX_PER_10MIN

    def lon_of(x):
        return LON_ANCHOR + (x - LON_ANCHOR_X) * dlon

    def lat_of(y):
        return LAT_ANCHOR + (y - LAT_ANCHOR_Y) * dlat

    base = os.path.splitext(IMAGE)[0]
    with open(base + ".jgw", "w") as fh:
        fh.write("\n".join("%.10f" % v for v in (dlon, 0.0, 0.0, dlat, lon_of(0.5), lat_of(0.5))) + "\n")
    with open(base + ".prj", "w") as fh:
        fh.write('GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,'
                 '298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]')
    print(f"wrote {os.path.basename(base)}.jgw and .prj")
    print(f"corners  NW {lon_of(0):.4f}, {lat_of(0):.4f}   SE {lon_of(width):.4f}, {lat_of(height):.4f}")

    print("\ncheck against known positions")
    print(f"  {'feature':18} {'d lat':>9} {'d lon':>9} {'west by':>10}")
    for name, x, y, true_lon, true_lat in CHECKS:
        got_lon, got_lat = lon_of(x), lat_of(y)
        dlat_km = (got_lat - true_lat) * 110.9
        dlon_min = (true_lon - got_lon) * 60.0
        dlon_km = (true_lon - got_lon) * 111.32 * np.cos(np.radians(true_lat))
        print(f"  {name:18} {dlat_km:7.2f}km {dlon_min:8.1f}' {dlon_km:9.1f}km")
    print("\nThe westward error grows with longitude, so it is the sheet's, not a misread anchor:")
    print("a misread anchor would be a constant 10.0'. See GEOREF_FINDINGS.md.")


if __name__ == "__main__":
    main()
