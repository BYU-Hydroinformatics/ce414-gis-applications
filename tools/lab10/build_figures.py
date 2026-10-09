r"""Lab 10 example layouts, rendered by ArcGIS Pro (arcpy.mp) from the rasters run_model.py leaves in
C:\Ames\Lab09\Check.gdb (seed 1). Reuses the Lab 5 layout helpers.

    python build_figures.py
Writes docs/assignments/lab-10/images/lab10-example-map-baseline.png (2,500 points) and
lab10-example-map-scenario.png (250 points): one landscape sheet each, the true DEM and the three
surfaces in one row on one elevation scale, the three error rasters beneath their surfaces on one
diverging scale, each labeled with its RMSE.
"""
import importlib.util
import json
import os
import pathlib

import arcpy
from arcpy.sa import Hillshade, Raster

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bf", HERE.parent / "lab05" / "build_figures.py")
bf = importlib.util.module_from_spec(spec); spec.loader.exec_module(bf)
IMG = HERE.parents[1] / "docs" / "assignments" / "lab-10" / "images"
GDB = r"C:\Ames\Lab09\Check.gdb"
APRX = r"C:\Ames\Lab09\Lab10_Figures.aprx"
UTM = arcpy.SpatialReference(26912)
CV = json.load(open(HERE / "check_values.json"))
rgb, poly = bf.rgb, bf.poly
bf.GDB, bf.IMG = GDB, IMG
arcpy.CheckOutExtension("Spatial")
arcpy.env.workspace = GDB
arcpy.env.overwriteOutput = True

# Elevation classes, the same in all four top panels (m above NAVD 88)
RAMP = [(200, 222, 185), (160, 200, 140), (225, 215, 145), (215, 175, 115), (180, 135, 100), (160, 125, 115),
        (195, 180, 175), (245, 242, 240)]
ELEV = [(1400 + 200 * i, f"{1200 + 200 * i:,} – {1400 + 200 * i:,} m", rgb(*c)) for i, c in enumerate(RAMP)]
ELEV[0] = (1400, "below 1,400 m", ELEV[0][2])
ELEV[-1] = (2900, "2,600 – 2,900 m", ELEV[-1][2])
# Error classes: True DEM minus surface. Red = the surface is too high; blue = too low.
ERR = [(-100, "over 100 m high", rgb(165, 0, 38)), (-50, "50 – 100 m high", rgb(215, 48, 39)),
       (-20, "20 – 50 m high", rgb(244, 109, 67)), (-5, "5 – 20 m high", rgb(253, 174, 97)),
       (5, "within 5 m", rgb(245, 245, 245)), (20, "5 – 20 m low", rgb(171, 217, 233)),
       (50, "20 – 50 m low", rgb(116, 173, 209)), (100, "50 – 100 m low", rgb(69, 117, 180)),
       (300, "over 100 m low", rgb(49, 54, 149))]


def classify(m, ras, name, breaks, minimum, transparency=0):
    lyr = m.addDataFromPath(os.path.join(GDB, ras))
    lyr.name = name
    sym = lyr.symbology
    sym.updateColorizer("RasterClassifyColorizer")
    sym.colorizer.classificationMethod = "ManualInterval"
    sym.colorizer.breakCount = len(breaks)
    for brk, (ub, label, color) in zip(sym.colorizer.classBreaks, breaks):
        brk.upperBound, brk.label, brk.color = ub, label, color
    lyr.symbology = sym
    try:
        d = lyr.getDefinition("V3")
        d.colorizer.minimumBreak = minimum
        for g in getattr(d.colorizer, "groups", None) or []:
            g.heading = ""
        lyr.setDefinition(d)
    except Exception as ex:
        print("min break:", ex)
    lyr.transparency = transparency
    return lyr


def project():
    if os.path.exists(APRX):
        os.remove(APRX)
    p = arcpy.mp.ArcGISProject(bf.BLANK); p.saveACopy(APRX); p = arcpy.mp.ArcGISProject(APRX)
    for x in p.listLayouts() + p.listMaps():
        p.deleteItem(x)
    return p


def panel(p, lyt, name, ras, kind, box, label, points=None):
    m = bf.new_map(p, name)
    if kind == "elev":
        classify(m, ras, "Elevation", ELEV, 1300.0, transparency=25)
        hs = m.addDataFromPath(os.path.join(GDB, "Hillshade_True")); hs.name = "Hillshade"
        m.moveLayer(m.listLayers()[0], hs, "AFTER")
    else:
        classify(m, ras, "Surface error", ERR, -300.0)
    if points:
        bf.point_layer(m, points, "Sample points", "Circle 1", rgb(20, 20, 20), 1.6)
    mf = lyt.createMapFrame(poly(*box), m, name)
    e = arcpy.Describe(os.path.join(GDB, "Study_Area")).extent
    mf.camera.setExtent(arcpy.Extent(e.XMin - 60, e.YMin - 60, e.XMax + 60, e.YMax + 60, spatial_reference=UTM))
    p.createTextElement(lyt, arcpy.Point(box[0], box[3] + 0.07), "POINT", label, 8.5, None, name + " label")
    return mf


def legend(p, lyt, mf, box, name):
    style = lambda cls, nm: (p.listStyleItems("ArcGIS 2D", cls, nm) or [None])[0]
    leg = lyt.createMapSurroundElement(poly(*box), "LEGEND", mf, style("LEGEND", "Legend 1"), name)
    try:
        leg.title = ""
        for it in leg.items:
            if "Hillshade" in it.name or "Sample" in it.name:
                leg.removeItem(it)
        leg.fittingStrategy = "AdjustFontSize"
        d = leg.getDefinition("V3")
        for it in d.items:
            it.showHeading = False
        leg.setDefinition(d)
        if leg.isOverflowing:
            print("legend overflowing:", name)
    except Exception as ex:
        print("legend:", ex)
    return leg


def sheet(p, tag, title, subtitle, rmse, notes, fname):
    lyt = p.createLayout(11, 8.5, "INCH", fname)
    p.createPredefinedGraphicElement(lyt, poly(0.25, 0.25, 10.75, 8.25), "RECTANGLE", None, "Neatline")
    for txt, y, sz in ((title, 7.95, 16), (subtitle, 7.68, 8.5)):
        p.createTextElement(lyt, arcpy.Point(0.45, y), "POINT", txt, sz, None, "T")
    cols = [0.45, 3.05, 5.65, 8.25]
    w, hgt = 2.45, 2.45 * 6.99 / 8.67
    top, mid = 5.25, 2.65
    s = {"n2500": "n2500_s1", "n250": "n250_s1"}[tag]
    mf0 = panel(p, lyt, f"{tag} true", "True_DEM", "elev", (cols[0], top, cols[0] + w, top + hgt),
                "True DEM, with the sample points", f"Points_{s}")
    surf = [(f"Thiessen_{s}", f"Error_Th_{s}", "Thiessen"), (f"IDW_{s}_p2", f"Error_IDW_{s}_p2", "IDW, power 2, 12 points"),
            (f"Kriging_{s}_SPH", f"Error_Kr_{s}_SPH", "Kriging, ordinary, spherical, 12 points")]
    err_mf = None
    for c, (sr, er, lab), r in zip(cols[1:], surf, rmse):
        panel(p, lyt, f"{tag} {lab}", sr, "elev", (c, top, c + w, top + hgt), lab)
        mf = panel(p, lyt, f"{tag} {lab} error", er, "err", (c, mid, c + w, mid + hgt), f"{lab.split(',')[0]} error:  RMSE {r:.2f} m")
        err_mf = err_mf or mf
    legend(p, lyt, mf0, (cols[0], 2.65, cols[0] + 1.2, 4.75), "Elevation legend")
    legend(p, lyt, err_mf, (cols[0] + 1.25, 2.65, cols[0] + 2.5, 4.75), "Error legend")
    style = lambda cls, nm: (p.listStyleItems("ArcGIS 2D", cls, nm) or [None])[0]
    lyt.createMapSurroundElement(arcpy.Point(0.75, 1.0), "NORTH_ARROW", mf0, style("NORTH_ARROW", "ArcGIS North 1"), "North Arrow")
    sb = lyt.createMapSurroundElement(poly(1.2, 0.85, 2.7, 1.25), "SCALE_BAR", mf0, style("SCALE_BAR", "Scale Line 1"), "Scale Bar")
    try:
        sd = sb.getDefinition("V3")
        sd.unitLabel = "km"
        if isinstance(sd.units, dict):
            sd.units["uwkid"] = 9036
        else:
            sd.units.uwkid = 9036
        sd.fittingStrategy = "AdjustFrame"; sd.division = 2; sd.divisions = 2; sd.subdivisions = 0; sd.divisionsBeforeZero = 0
        sb.setDefinition(sd)
    except Exception as ex:
        print("scale bar:", ex)
    p.createPredefinedGraphicElement(lyt, poly(3.05, 0.45, 10.55, 1.45), "RECTANGLE", None, "TextBoxFrame")
    p.createTextElement(lyt, poly(3.12, 0.5, 10.5, 1.4), "POLYGON", "\n".join(notes), 8, None, "Notes")
    lyt.exportToPNG(str(IMG / fname), resolution=150)
    print("exported", fname)


if __name__ == "__main__":
    if not arcpy.Exists("Hillshade_True"):
        Hillshade("True_DEM", 315, 45, "NO_SHADOWS", 1).save("Hillshade_True")
    p = project()
    bf.p_global = p
    b = CV["baseline"]; n250 = CV["counts"]["250"]
    common = ["Example map, CE 414, October 2026. Projection: NAD 1983 UTM Zone 12N, 30 m cells, 60.6 sq km study area.",
              "Data: USGS 3D Elevation Program 1/3 arc-second DEM, tile n41w112 (May 2026), projected with bilinear resampling.",
              "Error = true DEM minus the rebuilt surface (red: the surface is too high; blue: too low); RMSE = square root of the mean squared error over all 67,337 cells."]
    rm = lambda d: [d[k]["rmse"] for k in ("Thiessen", "IDW", "Kriging")]
    sheet(p, "n2500", "Rebuilding Y Mountain from 2,500 Points: Kriging Comes Closest",
          "Three interpolators, the same 2,500 random samples of the true DEM (seed 1), compared cell by cell with the truth",
          rm(b), [f"Result: RMSE {b['Thiessen']['rmse']:.2f} m (Thiessen), {b['IDW']['rmse']:.2f} m (IDW), {b['Kriging']['rmse']:.2f} m (Kriging). "
                  "Every method is within a few meters on the valley floor; the errors live on the mountain front."] + common,
          "lab10-example-map-baseline.png")
    sheet(p, "n250", "The Same Surfaces from 250 Points: Every Error Grows",
          "Changed: 250 random samples instead of 2,500 (seed 1); same methods, same parameters, same color scales",
          rm(n250), [f"Result: RMSE rises to {n250['Thiessen']['rmse']:.2f} m (Thiessen), {n250['IDW']['rmse']:.2f} m (IDW), {n250['Kriging']['rmse']:.2f} m (Kriging). "
                     "Chosen because it changes the picture most: whole ridges are missed, not just the cliff bands."] + common,
          "lab10-example-map-scenario.png")
    p.save()
