"""Build the Lake Powell data for CE 414 Lab 6 (Lake Depth Explorer).

Run on the Mac that holds the HydroMap Powell DEM work. Produces:

  data/student/powell_tbdem_30m.tif        whole lake, 30 m, meters NAVD88 (as the USGS ships it)
  data/student/powell_wahweap_10m.tif      south-end close-up, 10 m, meters NAVD88
  data/student/main_pool_seed.shp          one point in the dam forebay (the "main pool" anchor)
  data/student/powell_elevation_usbr.csv   daily pool elevation, ft NGVD29, 1963 to present
  data/instructor/powell_check_values.csv  the model's answers, computed independently here

Sources:
  Poppenga, Danielson & Tyler (2020), One Meter Topobathymetric DEM for Lake Powell,
  1947-2018, USGS data release, https://doi.org/10.5066/P9XX0J1Y
  USBR Upper Colorado hydrodata, site 919 (Lake Powell), datatype 49 (pool elevation)

The 30 m surface is the 30 m average-resampled copy made for HydroMap on 2026-07-13
(sha256 09a2cc41...c60) with nodata rewritten to -9999 and values rounded to 1 cm.
"""
import hashlib
import shutil
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
import shapefile  # pyshp
from pyproj import CRS, Transformer
from rasterio.enums import Resampling
from rasterio.windows import from_bounds
from scipy import ndimage

PKG = Path(__file__).resolve().parents[1]
STUDENT = PKG / "data" / "student"
INSTR = PKG / "data" / "instructor"
SRC_1M = Path("/Users/dan/hydromap/powell-dem-work/data/lake_powell_tbdem.tif")
SRC_30M = Path("/Users/dan/hydromap/powell-dem-work/data/lake_powell_tbdem_30m.tif")
SRC_30M_SHA = "09a2cc41685705af0db141da748c9fcae31e96720d7fb311c168bd8474892c60"

NODATA = -9999.0
M_TO_FT = 1 / 0.3048
NAVD_TO_NGVD_FT = 2.91          # NGVD29 = NAVD88 - 2.91 ft at Lake Powell (USGS SIR 2022-5017)
SEED_UTM = (458886.0, 4088928.0)  # main channel ~2.1 km upstream of Glen Canyon Dam, bed ~3,191 ft NGVD29;
                                  # chosen as the deepest cell 1.2-2.5 km from the dam in the largest pool at dead pool
WAHWEAP_LONLAT = (-111.565, 36.915, -111.375, 37.085)  # W, S, E, N

# USGS SIR 2022-5017 area table, as used by HydroMap (ft NGVD29, sq mi)
SIR_AREA = [(3370.1, 29.6), (3400.0, 39.1), (3449.8, 55.1), (3489.9, 71.6), (3525.0, 90.3),
            (3555.2, 108.3), (3574.8, 121.9), (3600.1, 141.6), (3650.0, 193.5), (3699.8, 248.7)]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_gtiff(path, arr, profile):
    prof = profile.copy()
    prof.update(driver="GTiff", dtype="float32", nodata=NODATA, compress="deflate",
                predictor=3, tiled=True, blockxsize=256, blockysize=256, count=1)
    with rasterio.open(path, "w", **prof) as d:
        d.write(arr.astype("float32"), 1)
        d.update_tags(UNITS="meters", VERTICAL_DATUM="NAVD88",
                      SOURCE="USGS 1 m Topobathymetric DEM of Lake Powell 1947-2018, doi:10.5066/P9XX0J1Y")


def surface_30m():
    assert sha256(SRC_30M) == SRC_30M_SHA, "30 m source changed since HydroMap provenance"
    with rasterio.open(SRC_30M) as d:
        a = d.read(1, masked=True)
        prof = d.profile
    out = np.where(a.mask, NODATA, np.round(a.filled(0), 2))
    write_gtiff(STUDENT / "powell_tbdem_30m.tif", out, prof)
    return out, prof


def surface_wahweap_10m():
    with rasterio.open(SRC_1M) as d:
        tr = Transformer.from_crs(4326, d.crs, always_xy=True)
        w, s = tr.transform(WAHWEAP_LONLAT[0], WAHWEAP_LONLAT[1])
        e, n = tr.transform(WAHWEAP_LONLAT[2], WAHWEAP_LONLAT[3])
        # snap to a 10 m grid aligned with the 1 m source
        w, s, e, n = np.floor(w / 10) * 10, np.floor(s / 10) * 10, np.ceil(e / 10) * 10, np.ceil(n / 10) * 10
        win = from_bounds(w, s, e, n, d.transform).round_offsets().round_lengths()
        shape = (int(win.height // 10), int(win.width // 10))
        a = d.read(1, window=win, out_shape=shape, resampling=Resampling.average, masked=True)
        prof = d.profile
        prof.update(width=shape[1], height=shape[0],
                    transform=rasterio.transform.from_bounds(w, s, e, n, shape[1], shape[0]))
    out = np.where(a.mask, NODATA, np.round(a.filled(0), 2))
    write_gtiff(STUDENT / "powell_wahweap_10m.tif", out, prof)
    return out, prof


def seed_point(crs):
    x, y = SEED_UTM
    with shapefile.Writer(str(STUDENT / "main_pool_seed"), shapeType=shapefile.POINT) as w:
        w.field("Name", "C", 40)
        w.point(x, y)
        w.record("Glen Canyon Dam forebay")
    (STUDENT / "main_pool_seed.prj").write_text(CRS.from_user_input(crs).to_wkt(version="WKT1_ESRI"))
    return x, y


def usbr_record():
    url = "https://www.usbr.gov/uc/water/hydrodata/reservoir_data/919/csv/49.csv"
    raw = INSTR / "_usbr_919_49_raw.csv"
    urllib.request.urlretrieve(url, raw)
    d = pd.read_csv(raw).dropna()
    d.columns = ["date", "elevation_ft_ngvd29"]
    d["elevation_ft_ngvd29"] = d["elevation_ft_ngvd29"].round(2)
    d.to_csv(STUDENT / "powell_elevation_usbr.csv", index=False)
    raw.unlink()
    return d


def sir_area(e):
    xs, ys = zip(*SIR_AREA)
    return float(np.interp(e, xs, ys)) if xs[0] <= e <= xs[-1] else float("nan")


def check_values(surf, prof, seed_xy, tag):
    valid = surf != NODATA
    ft = np.where(valid, surf * M_TO_FT - NAVD_TO_NGVD_FT, np.inf)
    cell_m2 = abs(prof["transform"].a * prof["transform"].e)
    r, c = rasterio.transform.rowcol(prof["transform"], *seed_xy)
    print(f"[{tag}] seed cell {r},{c} bed elevation {ft[r, c]:.1f} ft NGVD29")
    assert ft[r, c] < 3370, "seed must be wet at dead pool"
    four = ndimage.generate_binary_structure(2, 1)
    eight = ndimage.generate_binary_structure(2, 2)
    rows = []
    for e in range(3370, 3701, 10):
        wet = ft <= e
        out = {"surface": tag, "elevation_ft_ngvd29": e,
               "elevation_m_navd88": round((e + NAVD_TO_NGVD_FT) / M_TO_FT, 3),
               "wet_cells_all": int(wet.sum())}
        for name, st in (("4conn", four), ("8conn", eight)):
            lab, n = ndimage.label(wet, structure=st)
            keep = lab == lab[r, c] if lab[r, c] else np.zeros_like(wet)
            out[f"main_pool_cells_{name}"] = int(keep.sum())
            out[f"main_pool_sqmi_{name}"] = round(keep.sum() * cell_m2 / 2589988.11, 2)
            out[f"regions_{name}"] = int(n)
        out["removed_cells_4conn"] = out["wet_cells_all"] - out["main_pool_cells_4conn"]
        out["usgs_sir2022_5017_sqmi"] = round(sir_area(e), 1) if tag == "powell_30m" else ""
        rows.append(out)
    return pd.DataFrame(rows)


def describe(arr, prof, name):
    v = arr[arr != NODATA]
    return {"file": name, "columns": prof["width"], "rows": prof["height"],
            "cell_size_m": prof["transform"].a, "valid_cells": int(v.size),
            "min_m": float(v.min()), "max_m": float(v.max()), "mean_m": round(float(v.mean()), 2),
            "min_ft_ngvd29": round(float(v.min()) * M_TO_FT - NAVD_TO_NGVD_FT, 1),
            "max_ft_ngvd29": round(float(v.max()) * M_TO_FT - NAVD_TO_NGVD_FT, 1),
            "crs": prof["crs"].to_string(),
            "left": prof["transform"].c, "top": prof["transform"].f}


if __name__ == "__main__":
    STUDENT.mkdir(parents=True, exist_ok=True)
    INSTR.mkdir(parents=True, exist_ok=True)
    s30, p30 = surface_30m()
    s10, p10 = surface_wahweap_10m()
    seed = seed_point(p30["crs"])
    rec = usbr_record()
    pd.DataFrame([describe(s30, p30, "powell_tbdem_30m.tif"),
                  describe(s10, p10, "powell_wahweap_10m.tif")]).to_csv(
        INSTR / "powell_surface_stats.csv", index=False)
    cv = pd.concat([check_values(s30, p30, seed, "powell_30m"),
                    check_values(s10, p10, seed, "wahweap_10m")])
    cv.to_csv(INSTR / "powell_check_values.csv", index=False)
    print(pd.read_csv(INSTR / "powell_surface_stats.csv").T)
    print(cv[cv.surface == "powell_30m"][["elevation_ft_ngvd29", "main_pool_sqmi_4conn",
                                         "main_pool_sqmi_8conn", "usgs_sir2022_5017_sqmi",
                                         "removed_cells_4conn"]].to_string(index=False))
    print("record:", rec.date.iloc[0], "to", rec.date.iloc[-1], len(rec), "days")
