"""Lab 7 (HAND): build the hosted data package in C:/Ames/HAND/pkg/lab07-provo-river-hand/
and zip it to C:/Ames/HAND/pkg/lab07-provo-river-hand.zip. (Copying the zip to docs/data/ is a
maintainer step after the instructor approves the plan.)

  Provo_DEM.tif        bare-earth DEM, NAD 1983 UTM 12N, CELL m, float32, LZW (3DEP 1 m lidar
                       via the 3DEP image service, averaged from 2 m)
  Lab07.gdb
    Provo_River        NHD Provo River (UGRC UtahStreamsNHD, GNIS_Name = 'Provo River', dissolved)
    Gage               USGS 10163000 (NWIS site coordinates)
    Buildings          UGRC building footprints within 1 km of the river
    FEMA_Floodplain_1pct  FEMA NFHL riverine 1%-annual-chance zones (A, AE, AH, AO; not coastal)
    Comparison_Area    500 m of the river minus FEMA's Utah Lake coastal zones
    FEMA_Cross_Sections   FEMA NFHL S_XS for the Provo River (WSEL_REG, STRMBED_EL, feet NAVD 88)
    Stage_Table        the six design rows of stage_table.csv (+ H_CM integer for iteration)
  rating_10163000.csv  USGS rating 30.0 (gage height ft, discharge ft3/s)
  peaks_10163000.csv   NWIS annual peaks (water year, date, discharge, gage height, codes)
  READ-ME-FIRST.txt
Usage: make_extract.py [cell_m]   (default 3)
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
CELL = int(sys.argv[1]) if len(sys.argv) > 1 else 3
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
    gdb = os.path.join(PKG, "Lab07.gdb")
    arcpy.management.CreateFileGDB(PKG, "Lab07.gdb")
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
              ("ELEV_M", "DOUBLE"), ("H_M", "DOUBLE"), ("H_CM", "SHORT")]
    for f, ty in fields:
        arcpy.management.AddField(t, f, ty)
    with arcpy.da.InsertCursor(t, [f for f, _ in fields]) as c:
        for r in rows:
            c.insertRow([int(r["return_period_yr"]), float(r["aep_pct"]), int(r["q_cfs"]),
                         float(r["gage_height_ft"]), float(r["elev_m_navd88"]), float(r["hand_h_m"]),
                         int(round(float(r["hand_h_m"]) * 100))])
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
    for d, _, files in os.walk(PKG):
        for fn in files:
            if not d.endswith(".gdb"):
                print(fn, round(os.path.getsize(os.path.join(d, fn)) / 1e6, 2), "MB")


README = """Lab 7 - Flood Mapping with HAND: Provo River at Provo, Utah
(DRAFT package built by tools/lab07/make_extract.py; wording to be finalized with the lab page)

Provo_DEM.tif  Bare-earth elevation in meters above NAVD 88, {cell} m cells, NAD 1983 UTM zone 12N.
  Source: USGS 3D Elevation Program, best-available 1 m lidar, read from the 3DEP elevation image
  service (https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer)
  on October 8-9, 2026 at 2 m and averaged to {cell} m. Hydro-flattened: the river is a flat water
  surface at the time the lidar was flown, not the channel bed.

Lab07.gdb
  Provo_River          USGS National Hydrography Dataset via UGRC (UtahStreamsNHD), dissolved.
  Gage                 USGS 10163000 PROVO RIVER AT PROVO, UT. Gage datum 4,493.22 ft NAVD 88.
  Buildings            UGRC building footprints (Microsoft, computer-vision), within 1 km of the river.
  FEMA_Floodplain_1pct FEMA National Flood Hazard Layer, Utah County (DFIRM 49049C, effective
                       June 23, 2026): riverine 1%-annual-chance zones A, AE, AH, AO. Utah Lake's
                       coastal zones are left out, and only zones within 500 m of the river are kept.
  Comparison_Area      Where the HAND map is compared with FEMA: within 500 m of the river, minus
                       Utah Lake's coastal flood zones.
  FEMA_Cross_Sections  FEMA NFHL cross-sections on the Provo River: 1% water surface (WSEL_REG) and
                       streambed (STRMBED_EL), feet NAVD 88.
  Stage_Table          Flood flows for 2- to 100-year return periods, their stage at the gage, and
                       the HAND threshold H_M (meters) = gage height - 3.20 ft. H_CM = H_M x 100.

rating_10163000.csv   USGS stage-discharge rating 30.0 for the gage (gage height ft, discharge ft3/s).
peaks_10163000.csv    USGS annual peak flows, every one coded 6 (regulated by upstream dams).
"""

if __name__ == "__main__":
    main()
