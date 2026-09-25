"""Reproduce Lab 4 (Cell Phone Tower Placement) with arcpy and measure its check values.

Mirrors the ModelBuilder model the lab page describes, step for step, so every number the page
publishes can be regenerated. Run with the ArcGIS Pro Python:

    "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" tools/lab04/run_model.py [--sens]

Inputs (downloaded as the page tells students to):
    C:\\Ames\\Lab04\\Data\\DEM\\USGS_1_n4?w11?.tif          four USGS 1 arc-second tiles
    C:\\Ames\\Lab04\\Data\\lab04-utah-cell-towers\\...      the prepared tower extract (make_extract.py)
    C:\\Ames\\Lab04\\Data\\Counties\\Counties.shp           UGRC county boundaries
    C:\\Ames\\Lab04\\Data\\UDOT_Routes\\UDOT_Routes.shp     UDOT routes (ALRS)
"""
import arcpy, json, sys, time, pathlib
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

ROOT = pathlib.Path(r"C:\Ames\Lab04")
DATA = ROOT / "Data"
GDB = str(ROOT / "Check.gdb")
TILES = [str(DATA / "DEM" / f"USGS_1_{t}.tif") for t in ("n40w112", "n40w113", "n41w112", "n41w113")]
TOWERS = str(DATA / "lab04-utah-cell-towers" / "UtahCellTowers.shp")
COUNTIES = str(DATA / "Counties" / "Counties.shp")
ROUTES = str(DATA / "UDOT_Routes" / "UDOT_Routes.shp")
UTM = arcpy.SpatialReference(26912)   # NAD 1983 UTM zone 12N
CELL = 30
EDGE_BUFFER = "50 Kilometers"
KM2 = 1e6
SQMI = 2589988.110336

DEFAULT = dict(max_slope=5, road_km=1, radius_m=20000, max_density=20)


def setup():
    if not arcpy.Exists(GDB):
        arcpy.management.CreateFileGDB(str(ROOT), "Check.gdb")
    arcpy.env.workspace = GDB
    arcpy.env.outputCoordinateSystem = UTM
    arcpy.env.cellSize = CELL


def area(fc):
    return sum(r[0] for r in arcpy.da.SearchCursor(fc, "SHAPE@AREA"))


def ones(ras):
    """Cells equal to 1 in an integer raster, via its attribute table."""
    ras = ras if isinstance(ras, str) else ras.catalogPath
    arcpy.management.BuildRasterAttributeTable(ras, "Overwrite")
    n = {r[0]: r[1] for r in arcpy.da.SearchCursor(ras, ["Value", "Count"])}
    return n


def shared(log):
    """Steps that do not depend on the four parameters: county, DEM mosaic, slope, tower clip."""
    t = time.time()
    arcpy.env.cellSize = "MAXOF"
    arcpy.analysis.Select(COUNTIES, "Utah_County", "NAME = 'UTAH'")
    log["county_features"] = int(arcpy.management.GetCount("Utah_County")[0])
    log["county_km2"] = area("Utah_County") / KM2

    # Spatial Reference and Cellsize are left BLANK in Mosaic To New Raster. Typing 30 into its
    # Cellsize box while it reprojects gave a 117,789 x 128,657-cell raster (38 minutes); left
    # blank it takes the Output Coordinate System environment and makes 24.05 x 30.96 m cells,
    # which Project Raster then resamples to square 30 m cells.
    t0 = time.time()
    if not arcpy.Exists("DEM_Mosaic"):
        arcpy.management.MosaicToNewRaster(TILES, GDB, "DEM_Mosaic", None, "32_BIT_FLOAT", None, 1)
    m = arcpy.Describe("DEM_Mosaic")
    log["mosaic"] = dict(cols=m.width, rows=m.height, cellx=m.meanCellWidth, celly=m.meanCellHeight,
                         sr=m.spatialReference.name, s=round(time.time() - t0))
    t0 = time.time()
    if not arcpy.Exists("DEM_UtahCo"):
        arcpy.management.ProjectRaster("DEM_Mosaic", "DEM_UtahCo", UTM, "BILINEAR", CELL)
    d = arcpy.Describe("DEM_UtahCo")
    dem = Raster("DEM_UtahCo")
    log["project_s"] = round(time.time() - t0)
    log["dem"] = dict(cols=d.width, rows=d.height, cell=d.meanCellWidth, min=dem.minimum,
                      max=dem.maximum, sr=d.spatialReference.name)

    if not arcpy.Exists("Slope_Degrees"):
        Slope("DEM_UtahCo", "DEGREE", 1, "PLANAR", "METER").save("Slope_Degrees")
    s = Raster("Slope_Degrees")
    log["slope"] = dict(min=s.minimum, max=s.maximum)
    # slope inside the county only, for a check value
    ZonalStatisticsAsTable("Utah_County", "NAME", "Slope_Degrees", "slope_zs", "DATA", "ALL")
    r = next(arcpy.da.SearchCursor("slope_zs", ["MEAN", "MAX", "COUNT"]))
    log["slope_county"] = dict(mean=r[0], max=r[1], cells=r[2])

    # UGRC documents CARTO_CODE: 1 Interstate, 2 US highway, 3 State highway, 5-8 interchange
    # pieces and ramps, 9 local federal-aid routes, I institutional.
    arcpy.analysis.Select(ROUTES, "Major_Highways", "CARTO_CODE IN ('1', '2', '3')")
    log["routes_all"] = int(arcpy.management.GetCount(ROUTES)[0])
    log["major_highways"] = int(arcpy.management.GetCount("Major_Highways")[0])

    arcpy.analysis.Buffer("Utah_County", "Utah_County_Buffer", EDGE_BUFFER)
    arcpy.analysis.Clip(TOWERS, "Utah_County_Buffer", "Towers_Clip")
    log["towers_in_buffer"] = int(arcpy.management.GetCount("Towers_Clip")[0])
    arcpy.analysis.Clip(TOWERS, "Utah_County", "Towers_in_County")
    log["towers_in_county"] = int(arcpy.management.GetCount("Towers_in_County")[0])
    log["shared_s"] = round(time.time() - t)
    arcpy.env.cellSize = CELL


def run(p, log, keep=False):
    """One model run with parameters p. Returns the measured result."""
    t = time.time()
    tag = "" if keep else "_s"
    res = dict(p)
    # terrain
    flat = Con(Raster("Slope_Degrees") < p["max_slope"], 1, 0)
    flat.save("Flat_Enough" + tag)
    # roads
    arcpy.analysis.Buffer("Major_Highways", "Roads_Buffer" + tag, f"{p['road_km']} Kilometers",
                          dissolve_option="ALL")
    arcpy.analysis.Clip("Roads_Buffer" + tag, "Utah_County", "Road_Corridor" + tag)
    res["corridor_km2"] = area("Road_Corridor" + tag) / KM2
    near = ExtractByMask("Flat_Enough" + tag, "Road_Corridor" + tag)
    near.save("Flat_Near_Road" + tag)
    n = ones(near)
    res["corridor_cells"] = sum(n.values())
    res["flat_near_road_km2"] = n.get(1, 0) * CELL * CELL / KM2
    # towers
    kd = KernelDensity("Towers_Clip", "NONE", CELL, p["radius_m"], "SQUARE_KILOMETERS",
                       "DENSITIES", "PLANAR")
    kd.save("Tower_Density" + tag)
    res["kd_max_per10k"] = kd.maximum * 10000
    low = Con(10000 * kd < p["max_density"], 1, 0)
    low.save("Low_Tower_Density" + tag)
    # low-density share of the county
    ExtractByMask(low, "Utah_County").save("Low_Density_County" + tag)
    m = ones("Low_Density_County" + tag)
    res["low_density_county_km2"] = m.get(1, 0) * CELL * CELL / KM2
    # combine
    final = Raster("Flat_Near_Road" + tag) * low
    final.save("Suitable_Sites" + tag)
    f = ones(final)
    res["suitable_cells"] = f.get(1, 0)
    res["suitable_km2"] = f.get(1, 0) * CELL * CELL / KM2
    res["suitable_sqmi"] = f.get(1, 0) * CELL * CELL / SQMI
    res["pct_county"] = 100 * res["suitable_km2"] / log["county_km2"]
    # separate zones
    if f.get(1, 0):
        z = SetNull(final != 1, 1)
        arcpy.conversion.RasterToPolygon(z, "Suitable_Polys" + tag, "NO_SIMPLIFY", "Value")
        a = sorted((r[0] / KM2 for r in arcpy.da.SearchCursor("Suitable_Polys" + tag, "SHAPE@AREA")),
                   reverse=True)
        res["zones"] = len(a)
        res["zones_ge_1km2"] = sum(1 for x in a if x >= 1)
        res["largest_km2"] = a[0]
    else:
        res.update(zones=0, zones_ge_1km2=0, largest_km2=0)
    res["seconds"] = round(time.time() - t)
    return res


SCENARIOS = (
    [dict(DEFAULT, max_density=v) for v in (5, 10, 40, 80)]
    + [dict(DEFAULT, radius_m=v) for v in (10000, 40000)]
    + [dict(DEFAULT, max_slope=v) for v in (3, 10, 15)]
    + [dict(DEFAULT, road_km=v) for v in (0.5, 2, 5)]
)


def main():
    setup()
    log = {}
    shared(log)
    print(json.dumps(log, indent=1))
    base = run(DEFAULT, log, keep=True)
    print("BASELINE", json.dumps(base, indent=1))
    out = dict(shared=log, baseline=base)
    if "--sens" in sys.argv:
        out["scenarios"] = []
        for p in SCENARIOS:
            r = run(p, log)
            out["scenarios"].append(r)
            print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})
    pathlib.Path(__file__).with_name("check_values.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
