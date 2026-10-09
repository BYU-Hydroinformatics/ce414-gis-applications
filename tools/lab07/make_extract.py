"""Lab 7 (HAND): build the hosted data package in C:/Ames/HAND/pkg/lab07-provo-river-hand/
and zip it to C:/Ames/HAND/pkg/lab07-provo-river-hand.zip, then copy the zip to
docs/data/lab07-provo-river-hand.zip (the hosted copy students download).

  Provo_DEM.tif        bare-earth DEM, NAD 1983 UTM 12N, CELL m, float32, LZW (3DEP 1 m lidar
                       via the 3DEP image service, averaged from 2 m)
  ProvoData.gdb
    Provo_River        NHD Provo River (UGRC UtahStreamsNHD, GNIS_Name = 'Provo River', dissolved)
    Gage               USGS 10163000 (NWIS site coordinates)
    Buildings          UGRC building footprints within 1 km of the river
    FEMA_Floodplain_1pct  FEMA NFHL riverine 1%-annual-chance zones (A, AE, AH, AO; not coastal)
    Comparison_Area    500 m of the river minus FEMA's Utah Lake coastal zones
    FEMA_Cross_Sections   FEMA NFHL S_XS for the Provo River (WSEL_REG, STRMBED_EL, feet NAVD 88)
    Stage_Table        FEMA's five published flows (10-500 yr) -> gage height -> H_M, H_CM
  rating_10163000.csv  USGS rating 30.0 (gage height ft, discharge ft3/s)
  peaks_10163000.csv   NWIS annual peaks (water year, date, discharge, gage height, codes)
  READ-ME-FIRST.txt
Usage: make_extract.py [cell_m]   (default 5, the lab's package)
"""
import csv
import os
import shutil
import sys
import zipfile

import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"C:\Ames\HAND"
SRC = os.path.join(ROOT, "HAND.gdb")
CELL = int(sys.argv[1]) if len(sys.argv) > 1 else 5
NAME = "lab07-provo-river-hand"
PKG = os.path.join(ROOT, "pkg", NAME)


def main():
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("Spatial")
    if os.path.exists(PKG):
        shutil.rmtree(PKG)
    os.makedirs(PKG)
    dem2 = os.path.join(ROOT, "dem", "dem_2m.tif")
    out_dem = os.path.join(PKG, "Provo_DEM.tif")
    with arcpy.EnvManager(compression="LZW", tileSize="256 256", pyramid="NONE"):
        if CELL == 2:
            arcpy.management.CopyRaster(dem2, out_dem, pixel_type="32_BIT_FLOAT")
        elif CELL % 2 == 0:
            arcpy.sa.Aggregate(dem2, CELL // 2, "MEAN", "EXPAND", "DATA").save(out_dem)
        else:
            arcpy.management.Resample(dem2, out_dem, CELL, "BILINEAR")
    gdb = os.path.join(PKG, "ProvoData.gdb")
    arcpy.management.CreateFileGDB(PKG, "ProvoData.gdb")
    for name in ("Provo_River", "Gage"):
        arcpy.management.CopyFeatures(os.path.join(SRC, name), os.path.join(gdb, name))
    lay = arcpy.management.MakeFeatureLayer(os.path.join(SRC, "Buildings"), "b")
    buf = os.path.join("memory", "buf1k")
    arcpy.analysis.Buffer(os.path.join(SRC, "Provo_River"), buf, "1000 Meters", dissolve_option="ALL")
    arcpy.management.SelectLayerByLocation(lay, "HAVE_THEIR_CENTER_IN", buf)
    arcpy.management.CopyFeatures(lay, os.path.join(gdb, "Buildings"))
    # riverine 1% zones, NOT dissolved (keeps FLD_ZONE / ZONE_SUBTY), clipped to the comparison area
    sel = os.path.join("memory", "riv")
    arcpy.analysis.Select(os.path.join(SRC, "FEMA_Zones"), sel,
                          "FLD_ZONE IN ('A','AE','AH','AO') AND (ZONE_SUBTY IS NULL OR "
                          "ZONE_SUBTY NOT LIKE '%COASTAL FLOODPLAIN%')")
    arcpy.analysis.Clip(sel, os.path.join(SRC, "Domain_500m"), os.path.join(gdb, "FEMA_Floodplain_1pct"))
    arcpy.management.CopyFeatures(os.path.join(SRC, "FEMA_XS"), os.path.join(gdb, "FEMA_Cross_Sections"))
    arcpy.management.CopyFeatures(os.path.join(SRC, "Domain_500m"), os.path.join(gdb, "Comparison_Area"))
    rows = [r for r in csv.DictReader(open(os.path.join(HERE, "stage_table.csv"))) if r["design"] == "True"]
    t = os.path.join(gdb, "Stage_Table")
    arcpy.management.CreateTable(gdb, "Stage_Table")
    fields = [("RETURN_YR", "SHORT"), ("AEP_PCT", "DOUBLE"), ("Q_CFS", "LONG"), ("GAGE_HT_FT", "DOUBLE"),
              ("ELEV_M", "DOUBLE"), ("H_M", "DOUBLE"), ("H_CM", "SHORT"), ("RATING", "TEXT")]
    for f, ty in fields:
        arcpy.management.AddField(t, f, ty, field_length=20 if ty == "TEXT" else None)
    with arcpy.da.InsertCursor(t, [f for f, _ in fields]) as c:
        for r in rows:
            c.insertRow([int(r["return_period_yr"]), float(r["aep_pct"]), int(r["q_cfs"]),
                         float(r["gage_height_ft"]), float(r["elev_m_navd88"]), float(r["hand_h_m"]),
                         int(r["h_cm"]), "extrapolated" if r["rating"] == "EXTRAPOLATED" else "within table"])
    # rating and peaks as plain CSV
    rat = [l.rstrip("\n").split("\t") for l in open(os.path.join(ROOT, "raw", "rating.rdb")) if not l.startswith("#")][2:]
    with open(os.path.join(PKG, "rating_10163000.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["gage_height_ft", "discharge_cfs"])
        for a in rat:
            if a and a[0]:
                w.writerow([a[0], a[2]])
    pk = [l.rstrip("\n").split("\t") for l in open(os.path.join(ROOT, "raw", "peaks.rdb")) if not l.startswith("#")]
    head = pk[0]
    with open(os.path.join(PKG, "peaks_10163000.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["peak_date", "peak_cfs", "peak_code", "gage_height_ft", "gage_height_code"])
        for a in pk[2:]:
            d = dict(zip(head, a))
            if d.get("peak_va"):
                w.writerow([d["peak_dt"], d["peak_va"], d["peak_cd"], d["gage_ht"], d["gage_ht_cd"]])
    open(os.path.join(PKG, "READ-ME-FIRST.txt"), "w").write(README.format(cell=CELL))
    z = os.path.join(ROOT, "pkg", NAME + ".zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for d, _, files in os.walk(PKG):
            for fn in files:
                if fn.endswith(".lock"):
                    continue
                p = os.path.join(d, fn)
                zf.write(p, os.path.relpath(p, os.path.dirname(PKG)))
    print(z, round(os.path.getsize(z) / 1e6, 1), "MB")
    dst = os.path.join(os.path.dirname(os.path.dirname(HERE)), "docs", "data", NAME + ".zip")
    shutil.copyfile(z, dst)
    print("copied to", dst, os.path.getsize(dst), "bytes")
    for d, _, files in os.walk(PKG):
        for fn in files:
            if not d.endswith(".gdb"):
                print(fn, round(os.path.getsize(os.path.join(d, fn)) / 1e6, 2), "MB")


README = """Lab 7 - Flood Mapping with HAND: the Provo River at Provo, Utah
CE 414 Engineering Applications of GIS, Brigham Young University. Package built October 9, 2026
by tools/lab07/make_extract.py in the course repository.

Everything is in NAD 1983 UTM zone 12N, meters, except where a file says feet.

Provo_DEM.tif
  Bare-earth elevation in meters above NAVD 88; {cell} m cells; 1,718 columns x 2,124 rows;
  436,190-444,780 E, 4,452,930-4,463,550 N; about 1,366.8 to 1,645.5 m.
  Source: USGS 3D Elevation Program (3DEP), best-available 1 m lidar under the river, read from the
  3DEP elevation image service
  (https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer) on October 8,
  2026 at 2 m, then resampled (bilinear) to {cell} m by us. Nothing else was done to it: no filling,
  no smoothing. The lidar is hydro-flattened: the river is a flat water surface at the level it had
  the day the lidar was flown, not the channel bed.

ProvoData.gdb
  Provo_River          The Provo River from the National Hydrography Dataset, as served by the Utah
                       Geospatial Resource Center (UGRC), Utah Streams NHD (last edited March 7,
                       2026); the lines named Provo River, dissolved into one, 17.6 km.
  Gage                 USGS streamgage 10163000 PROVO RIVER AT PROVO, UT, at the NWIS site
                       coordinates (40.23926 N, 111.71119 W). Gage datum 4,493.22 ft above NAVD 88.
  Buildings            UGRC building footprints (Microsoft computer-vision footprints with UGRC
                       attributes; service last edited September 24, 2026), the 11,122 whose center
                       is within 1 km of the river.
  FEMA_Floodplain_1pct FEMA National Flood Hazard Layer, Utah County (DFIRM 49049C, effective June
                       23, 2026): the riverine 1%-annual-chance zones (A, AE, AE floodway, AH)
                       inside Comparison_Area. Utah Lake's coastal flood zones are left out.
  Comparison_Area      Where the lab compares its flood map with FEMA's: within 500 m of the river,
                       minus FEMA's Utah Lake coastal flood zones.
  FEMA_Cross_Sections  FEMA's 43 Provo River cross-sections from the same study: 1% water-surface
                       elevation (WSEL_REG, -8888 where Utah Lake controls) and streambed elevation
                       (STRMBED_EL), in feet NAVD 88.
  Stage_Table          FEMA's published peak flows for the Provo River (Flood Insurance Study,
                       Utah County, volume 49049CV001B, revised June 23, 2026, Table 9: "3 miles
                       above tie-in to Utah Lake"): 10-, 25-, 50-, 100- and 500-year. For each:
                       GAGE_HT_FT = the first row of rating_10163000.csv whose discharge is at
                       least Q_CFS (above 8.00 ft the rating's top segment is extended, RATING =
                       extrapolated); ELEV_M = (4,493.22 + GAGE_HT_FT) x 0.3048;
                       H_M = (GAGE_HT_FT - 3.20) x 0.3048, the flood depth above the zero-flow
                       level, used as the HAND threshold; H_CM = H_M in whole centimeters.

rating_10163000.csv   USGS stage-discharge rating 30.0 for the gage, in force since April 26,
                      2023 (provisional; file retrieved September 1, 2026): gage height in feet,
                      discharge in cubic feet per second, 3.42 to 8.00 ft.
peaks_10163000.csv    USGS annual peak flows for the gage, 1903 and 1934-2024 (retrieved October 9,
                      2026). Every one carries peak code 6: affected by regulation or diversion.

Sources: U.S. Geological Survey (3DEP; NWIS); Federal Emergency Management Agency (NFHL; Flood
Insurance Study, Utah County); Utah Geospatial Resource Center (NHD streams; building footprints).
Public data; credit them on your maps.
"""

if __name__ == "__main__":
    main()
