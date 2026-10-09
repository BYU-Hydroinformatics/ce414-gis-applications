"""Lab 7 (HAND): measure the data for Figure B (make_svgs.py) from the verified package run.

  long: the filled DEM along the NHD Provo River (its two parts, each oriented downhill), the lowest
        filled cell within 15 m every 25 m, the 100-yr HAND water surface (river + H_M) and the bathtub level (100-yr stage
        elevation at the gage, ELEV_M) - where each one is above the ground of the river line
  xs:   ground along FEMA cross-section C (the one just upstream of the gage), HAND at each point,
        and FEMA's 1% water surface there
Run after verify_package.py (reads C:/Ames/HAND/PkgCheck). Writes profile.json.
"""
import json
import os

import arcpy
import numpy as np
from arcpy.sa import Raster

HERE = os.path.dirname(os.path.abspath(__file__))
PC = r"C:\Ames\HAND\PkgCheck"
G = os.path.join(PC, "lab07-provo-river-hand", "ProvoData.gdb")
W = os.path.join(PC, "Work.gdb")
FT = 0.3048


def sampler(path):
    r = Raster(path)
    e = r.extent
    a = arcpy.RasterToNumPyArray(r, nodata_to_value=np.nan).astype(float)
    cw = r.meanCellWidth

    def f(x, y):
        c, rr = int((x - e.XMin) / cw), int((e.YMax - y) / cw)
        if 0 <= rr < a.shape[0] and 0 <= c < a.shape[1]:
            v = a[rr, c]
            return None if np.isnan(v) else float(v)
        return None
    return f


def main():
    st = {r[0]: (r[1], r[2]) for r in arcpy.da.SearchCursor(os.path.join(G, "Stage_Table"), ["RETURN_YR", "H_CM", "ELEV_M"])}
    h100, elev100 = st[100][0] / 100, st[100][1]
    fill = sampler(os.path.join(W, "Filled_DEM"))
    dem = sampler(os.path.join(PC, "lab07-provo-river-hand", "Provo_DEM.tif"))
    hand = sampler(os.path.join(W, "HAND"))
    # (a) where the D8 path that starts at the highest river cell leaves the river corridor
    fr = Raster(os.path.join(W, "Filled_DEM"))
    e = fr.extent
    cw = fr.meanCellWidth
    F = arcpy.RasterToNumPyArray(fr, nodata_to_value=np.nan)
    D = arcpy.RasterToNumPyArray(os.path.join(W, "Flow_Direction"), nodata_to_value=0)
    RV = arcpy.RasterToNumPyArray(os.path.join(W, "River_Cells"), e.lowerLeft, fr.width, fr.height, nodata_to_value=0) > 0
    rr, cc = np.nonzero(RV)
    k = np.argmax(F[rr, cc])
    r, c = int(rr[k]), int(cc[k])
    step = {1: (0, 1), 2: (1, 1), 4: (1, 0), 8: (1, -1), 16: (0, -1), 32: (-1, -1), 64: (-1, 0), 128: (-1, 1)}
    path = []
    while 0 <= r < F.shape[0] and 0 <= c < F.shape[1] and int(D[r, c]) in step:
        path.append((r, c))
        dr, dc = step[int(D[r, c])]
        r, c = r + dr, c + dc
    onr = [RV[a, b] for a, b in path]
    first_off = next(i for i in range(1, len(onr)) if onr[i - 1] and not any(onr[i:i + 40]))
    a, b = path[first_off]
    leave = arcpy.PointGeometry(arcpy.Point(e.XMin + (b + 0.5) * cw, e.YMax - (a + 0.5) * cw), fr.spatialReference)
    ll = leave.projectAs(arcpy.SpatialReference(4269)).firstPoint
    d8_leaves = {"utm": [round(leave.firstPoint.X), round(leave.firstPoint.Y)], "lat": round(ll.Y, 5), "lon": round(ll.X, 5),
                 "elev_m": round(float(F[a, b]), 2), "exits_at_row": path[-1][0], "exits_at_col": path[-1][1]}
    # (b) the long profile: along the NHD line's parts, each oriented downhill, upstream part first
    line = [r0[0] for r0 in arcpy.da.SearchCursor(os.path.join(G, "Provo_River"), ["SHAPE@"])][0]
    parts = []
    for pi in range(line.partCount):
        part = arcpy.Polyline(line.getPart(pi), line.spatialReference)
        pa, pb = part.positionAlongLine(20).firstPoint, part.positionAlongLine(part.length - 20).firstPoint
        za, zb = fill(pa.X, pa.Y), fill(pb.X, pb.Y)
        parts.append((max(za or 0, zb or 0), part, (za or 0) >= (zb or 0)))
    parts.sort(key=lambda t: -t[0])
    pts, off, gage_km = [], 0.0, None
    g = [r0[0] for r0 in arcpy.da.SearchCursor(os.path.join(G, "Gage"), ["SHAPE@"])][0].firstPoint
    best = 1e9
    for _, part, down in parts:
        Lp = part.length
        for dd in np.arange(0, Lp, 25.0):
            p = part.positionAlongLine(dd if down else Lp - dd).firstPoint
            zs = [fill(p.X + dx, p.Y + dy) for dx in (-15, -10, -5, 0, 5, 10, 15) for dy in (-15, -10, -5, 0, 5, 10, 15)]
            zs = [z for z in zs if z is not None]
            pts.append([round((off + float(dd)) / 1000, 3), round(min(zs), 2) if zs else None])
            dg = (p.X - g.X) ** 2 + (p.Y - g.Y) ** 2
            if dg < best:
                best, gage_km = dg, (off + float(dd)) / 1000
        off += Lp
    L = off
    on_river = None
    # cross-section C
    xs = [r for r in arcpy.da.SearchCursor(os.path.join(G, "FEMA_Cross_Sections"), ["XS_LTR", "WSEL_REG", "STRMBED_EL", "SHAPE@"])
          if r[0] == "C"][0]
    shp = xs[3]
    prof = []
    for d in np.arange(0, shp.length, 5.0):
        p = shp.positionAlongLine(float(d)).firstPoint
        prof.append([round(float(d), 1), dem(p.X, p.Y), hand(p.X, p.Y)])
    out = {"h100_m": h100, "elev100_m": elev100, "long": pts, "gage_km": round(gage_km, 3),
           "river_km": round(L / 1000, 2), "d8_path_leaves_river": d8_leaves, "nhd_parts": line.partCount,
           "xs": {"name": "C", "wsel_m": round(xs[1] * FT, 3), "bed_m": round(xs[2] * FT, 3), "profile": prof}}
    zs = [z for _, z in pts if z is not None]
    out["long_summary"] = {"top_m": zs[0], "bottom_m": zs[-1], "n": len(zs),
                           "km_below_bathtub": round(L / 1000 - next(k for k, z in pts if z is not None and z <= elev100), 3)}
    xp = [(d, z, hd) for d, z, hd in prof if z is not None]
    out["xs_summary"] = {"length_m": round(shp.length, 1), "ground_min": min(z for _, z, _ in xp), "ground_max": max(z for _, z, _ in xp),
                         "hand_wet_m": 5 * sum(1 for _, _, hd in xp if hd is not None and hd <= h100),
                         "fema_wet_m": 5 * sum(1 for _, z, _ in xp if z <= xs[1] * FT)}
    json.dump(out, open(os.path.join(HERE, "profile.json"), "w"), indent=0)
    print(out["long_summary"], d8_leaves, out["gage_km"], out["xs_summary"], out["xs"]["wsel_m"], out["xs"]["bed_m"])


if __name__ == "__main__":
    main()
