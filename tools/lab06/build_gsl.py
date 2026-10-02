"""Build the ALTERNATE Great Salt Lake data for CE 414 Lab 6.

  data/alternate_gsl/gsl_dem_30m.tif            whole lake, 30 m, meters NGVD29 (as Tarboton ships it)
  data/alternate_gsl/main_pool_seed_gsl.shp     one point in open water in the south arm
  data/alternate_gsl/gsl_elevation_usgs_10010000.csv   daily lake elevation, ft NGVD29, 1847 to present
  data/alternate_gsl/gsl_check_values.csv       the model's answers, computed here

Source DEM: Tarboton, D. (2015), Great Salt Lake Bathymetry, HydroShare,
http://www.hydroshare.org/resource/582060f00f6b443bb26e896426d9f62a  (GSLDEM.tif: BIO-WEST
bathymetry from Baskin 2005/2006 USGS surveys + 2009-11 surveys, extended with 10 m NED shifted
-0.97 m to NGVD29; 9.33 m cells; NAD83 UTM 12N).

Usage: python build_gsl.py /path/to/GSLDEM.tif
"""
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
import shapefile
from pyproj import CRS
from rasterio.enums import Resampling
from scipy import ndimage

PKG = Path(__file__).resolve().parents[1]
OUT = PKG / "data" / "alternate_gsl"
NODATA = -9999.0
CELL = 30.0
M_TO_FT = 1 / 0.3048
SEED_SEARCH_LONLAT = (-112.45, 41.00)  # open south-arm water between Antelope and Stansbury Islands

# USGS 2023 EAV (P9DGG75W) as used by HydroMap, total lake, ft NGVD29 -> sq mi
EAV = [(4188.5, 894), (4190.0, 938), (4192.0, 1014), (4196.0, 1248), (4200.0, 1602),
       (4204.0, 1940), (4208.0, 2179), (4211.5, 2229)]


def resample(src_path):
    with rasterio.open(src_path) as d:
        w = int(round((d.bounds.right - d.bounds.left) / CELL))
        h = int(round((d.bounds.top - d.bounds.bottom) / CELL))
        a = d.read(1, out_shape=(h, w), resampling=Resampling.average, masked=True)
        prof = d.profile
        prof.update(width=w, height=h, transform=rasterio.transform.from_origin(
            d.bounds.left, d.bounds.top, CELL, CELL))
    out = np.where(a.mask, NODATA, np.round(a.filled(0), 2)).astype("float32")
    prof.update(driver="GTiff", dtype="float32", nodata=NODATA, compress="deflate", predictor=3,
                tiled=True, blockxsize=256, blockysize=256)
    with rasterio.open(OUT / "gsl_dem_30m.tif", "w", **prof) as dst:
        dst.write(out, 1)
        dst.update_tags(UNITS="meters", VERTICAL_DATUM="NGVD29",
                        SOURCE="Tarboton 2015, Great Salt Lake Bathymetry, HydroShare 582060f00f6b443bb26e896426d9f62a")
    return out, prof


def pick_seed(ft, prof):
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, prof["crs"], always_xy=True)
    r0, c0 = rasterio.transform.rowcol(prof["transform"], *tr.transform(*SEED_SEARCH_LONLAT))
    win = ft[r0 - 100:r0 + 100, c0 - 100:c0 + 100]
    i = np.unravel_index(np.argmin(win), win.shape)
    r, c = r0 - 100 + i[0], c0 - 100 + i[1]
    x, y = rasterio.transform.xy(prof["transform"], r, c)
    with shapefile.Writer(str(OUT / "main_pool_seed_gsl"), shapeType=shapefile.POINT) as w:
        w.field("Name", "C", 40)
        w.point(x, y)
        w.record("South arm open water")
    (OUT / "main_pool_seed_gsl.prj").write_text(CRS.from_user_input(prof["crs"]).to_wkt(version="WKT1_ESRI"))
    print(f"seed {x:.0f},{y:.0f} bed {ft[r, c]:.1f} ft", Transformer.from_crs(prof["crs"], 4326, always_xy=True).transform(x, y))
    return r, c


def gage_record():
    url = ("https://waterservices.usgs.gov/nwis/dv/?format=rdb&sites=10010000&parameterCd=62614"
           "&startDT=1847-01-01&statCd=00003")
    rows = [l.split("\t") for l in urllib.request.urlopen(url).read().decode().splitlines()
            if l.startswith("USGS")]
    d = pd.DataFrame([(r[2], r[3], r[4]) for r in rows], columns=["date", "elevation_ft_ngvd29", "qualifier"])
    d = d[d.elevation_ft_ngvd29 != ""]
    d.to_csv(OUT / "gsl_elevation_usgs_10010000.csv", index=False)
    return d


def checks(surf, prof, seed_rc):
    ft = np.where(surf != NODATA, surf * M_TO_FT, np.inf)
    cell_sqmi = CELL * CELL / 2589988.11
    four = ndimage.generate_binary_structure(2, 1)
    eight = ndimage.generate_binary_structure(2, 2)
    xs, ys = zip(*EAV)
    rows = []
    for e in range(4170, 4215):
        wet = ft <= e
        out = {"elevation_ft_ngvd29": e, "elevation_m_ngvd29": round(e / M_TO_FT, 3),
               "wet_cells_all": int(wet.sum()), "wet_sqmi_all": round(wet.sum() * cell_sqmi, 1)}
        for name, st in (("4conn", four), ("8conn", eight)):
            lab, n = ndimage.label(wet, structure=st)
            k = lab[seed_rc]
            out[f"main_pool_sqmi_{name}"] = round((lab == k).sum() * cell_sqmi, 1) if k else 0.0
            out[f"regions_{name}"] = int(n)
        out["usgs_eav_total_sqmi"] = round(float(np.interp(e, xs, ys)), 0) if xs[0] <= e <= xs[-1] else ""
        rows.append(out)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    surf, prof = resample(sys.argv[1])
    v = surf[surf != NODATA]
    stats = {"columns": prof["width"], "rows": prof["height"], "cell_m": CELL, "valid_cells": int(v.size),
             "min_m": float(v.min()), "max_m": float(v.max()),
             "min_ft": round(float(v.min()) * M_TO_FT, 1), "max_ft": round(float(v.max()) * M_TO_FT, 1),
             "crs": prof["crs"].to_string()}
    pd.DataFrame([stats]).to_csv(OUT / "gsl_surface_stats.csv", index=False)
    print(stats)
    ft = np.where(surf != NODATA, surf * M_TO_FT, np.inf)
    seed = pick_seed(ft, prof)
    rec = gage_record()
    print("gage", rec.date.iloc[0], rec.date.iloc[-1], len(rec))
    cv = checks(surf, prof, seed)
    cv.to_csv(OUT / "gsl_check_values.csv", index=False)
    print(cv.to_string(index=False))
