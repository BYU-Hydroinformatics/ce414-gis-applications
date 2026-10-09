"""Lab 7 (HAND): personal design flow -> stage -> HAND threshold -> flooded area and buildings,
for every possible pair of last two BYU ID digits (00-99). Grading lookup table.

Rule (proposed): Q = 900 + 12 * dd  ft3/s   (dd = last two digits of the nine-digit BYU ID)
  -> 900 to 2,088 ft3/s, always inside the published rating table (top row 2,150 ft3/s)
  -> gage height = the FIRST row of the hosted rating table whose discharge is >= Q
  -> h (m) = (gage height - 3.20 ft) * 0.3048, rounded to 0.001 m
  -> flooded = HAND <= h ; area and building-centroid count
Usage: personal.py <hand.tif> <cell_m> [out.csv]
"""
import csv
import os
import sys

import arcpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RATING = r"C:\Ames\HAND\raw\rating.rdb"
GDB = r"C:\Ames\HAND\HAND.gdb"


def rating():
    lines = [l.rstrip("\n").split("\t") for l in open(RATING) if not l.startswith("#")][2:]
    return [(float(a[0]), float(a[2])) for a in lines if a and a[0]]


def h_for(dd, table):
    q = 900 + 12 * dd
    gh = next(g for g, d in table if d >= q)
    return q, gh, round((gh - 3.20) * 0.3048, 3)


def main():
    hand_path, cell = sys.argv[1], float(sys.argv[2])
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "personal_lookup.csv")
    r = arcpy.Raster(hand_path)
    ext = r.extent
    hand = arcpy.RasterToNumPyArray(r, nodata_to_value=-9999)
    valid = hand > -9999
    xs, ys = [], []
    for x, y in arcpy.da.SearchCursor(os.path.join(GDB, "Building_Points"), ["SHAPE@X", "SHAPE@Y"]):
        xs.append(x); ys.append(y)
    cols = np.floor((np.array(xs) - ext.XMin) / cell).astype(int)
    rows = np.floor((ext.YMax - np.array(ys)) / cell).astype(int)
    ok = (rows >= 0) & (rows < hand.shape[0]) & (cols >= 0) & (cols < hand.shape[1])
    bv = hand[rows[ok], cols[ok]]
    table = rating()
    res = []
    for dd in range(100):
        q, gh, h = h_for(dd, table)
        wet = valid & (hand <= h)
        res.append({"last_two_digits": f"{dd:02d}", "q_cfs": q, "gage_height_ft": gh, "h_m": h,
                    "cells": int(wet.sum()), "area_km2": round(wet.sum() * cell * cell / 1e6, 4),
                    "building_centroids": int(((bv > -9999) & (bv <= h)).sum())})
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(res[0]))
        w.writeheader(); w.writerows(res)
    hs = [x["h_m"] for x in res]
    areas = [x["area_km2"] for x in res]
    print("distinct h:", len(set(hs)), "distinct areas:", len(set(areas)), "distinct building counts:",
          len(set(x["building_centroids"] for x in res)))
    print(res[0], res[50], res[99], sep="\n")


if __name__ == "__main__":
    main()
