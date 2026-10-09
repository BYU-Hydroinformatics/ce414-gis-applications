"""Lab 7 (HAND): compare the DEM channel with FEMA's Provo River cross-sections and the gage.

For every FEMA cross-section (NFHL S_XS, Utah County DFIRM 49049C): the lowest 2 m DEM cell
within 15 m of the river centerline on the section line, FEMA's 1% water-surface elevation
(WSEL_REG) and streambed (STRMBED_EL), all NAVD 88. The "FEMA-implied HAND threshold" at a
section is WSEL - DEM channel. Also locates the gage between sections B and C (by distance along
the dissolved NHD Provo River) and interpolates FEMA's 1% WSEL there.
Writes xs_check.json. Run with the ArcGIS Pro python after run_model.py.
"""
import json
import os

import arcpy
import numpy as np
from arcpy.sa import Raster

HERE = os.path.dirname(os.path.abspath(__file__))
G = r"C:\Ames\HAND\HAND.gdb"
FT = 0.3048
DEM = r"C:\Ames\HAND\work\dem_lidar_2m.tif"


def main():
    river = [r[0] for r in arcpy.da.SearchCursor(G + r"\Provo_River", ["SHAPE@"])][0]
    dem = Raster(DEM)
    ext = dem.extent
    arr = arcpy.RasterToNumPyArray(dem, nodata_to_value=np.nan)

    def z(x, y):
        c = int((x - ext.XMin) / 2)
        r = int((ext.YMax - y) / 2)
        return float(arr[r, c])

    rows = []
    for ltr, stn, wsel, bed, shp in arcpy.da.SearchCursor(
            G + r"\FEMA_XS", ["XS_LTR", "STREAM_STN", "WSEL_REG", "STRMBED_EL", "SHAPE@"]):
        inter = shp.intersect(river, 1)
        if inter.pointCount == 0:
            continue
        p = inter.firstPoint
        m = river.measureOnLine(p)
        # lowest DEM cell on the section line within 15 m of the centerline crossing
        zs = []
        L = shp.length
        for k in range(0, int(L) + 1):
            q = shp.positionAlongLine(k).firstPoint
            if (q.X - p.X) ** 2 + (q.Y - p.Y) ** 2 <= 15 ** 2:
                zs.append(z(q.X, q.Y))
        chan = min(zs) if zs else None
        rows.append({"xs": ltr or "", "stn_ft": stn, "along_m": round(m, 1),
                     "wsel_m": round(wsel * FT, 3) if wsel and wsel > 0 else None,
                     "bed_m": round(bed * FT, 3), "dem_channel_m": round(chan, 3) if chan else None,
                     "fema_depth_m": round((wsel - bed) * FT, 3) if wsel and wsel > 0 else None,
                     "fema_implied_h_m": round(wsel * FT - chan, 3) if wsel and wsel > 0 and chan else None,
                     "dem_minus_bed_m": round(chan - bed * FT, 3) if chan else None})
    rows.sort(key=lambda r: r["stn_ft"])
    g = [r for r in arcpy.da.SearchCursor(G + r"\Gage", ["SHAPE@"])][0][0]
    gm = river.measureOnLine(g.firstPoint)
    snap = river.queryPointAndDistance(g.firstPoint)
    # interpolate WSEL at the gage between the bracketing sections (by along-river distance)
    ok = [r for r in rows if r["wsel_m"]]
    al = np.array([r["along_m"] for r in ok])
    order = np.argsort(al)
    gage_wsel = float(np.interp(gm, al[order], np.array([r["wsel_m"] for r in ok])[order]))
    gage_bed = float(np.interp(gm, al[order], np.array([r["bed_m"] for r in ok])[order]))
    h = np.array([r["fema_implied_h_m"] for r in ok if r["fema_implied_h_m"] is not None])
    d = np.array([r["fema_depth_m"] for r in ok])
    out = {"sections": rows, "gage_along_m": round(gm, 1), "gage_offset_from_line_m": round(snap[2], 1),
           "fema_1pct_wsel_at_gage_m": round(gage_wsel, 3), "fema_bed_at_gage_m": round(gage_bed, 3),
           "fema_implied_h": {"n": int(h.size), "min": float(h.min()), "median": float(np.median(h)),
                              "max": float(h.max())},
           "fema_depth": {"min": float(d.min()), "median": float(np.median(d)), "max": float(d.max())}}
    json.dump(out, open(os.path.join(HERE, "xs_check.json"), "w"), indent=1)
    for r in rows:
        print(r)
    print({k: v for k, v in out.items() if k != "sections"})


if __name__ == "__main__":
    main()
