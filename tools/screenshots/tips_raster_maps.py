"""Example maps for the ArcGIS Tips page "Make your raster symbology look good", rendered by
ArcGIS Pro (arcpy.mp) from the course's own rasters.

    propy.bat tools\\screenshots\\tips_raster_maps.py OUT_DIR [name ...]

Each figure is a layout with two (or six) map frames, "as ArcGIS Pro draws it" against "finished",
exported as JPEG. Every symbology choice below is one a student can make in the Symbology pane;
the page says where. Data:
  Rock Canyon 10 m DEM, flow direction and flow accumulation (Lab 5 GUI build, tips_watershed.py)
  Y Mountain true DEM, interpolated surfaces and error rasters (Lab 8 check run, seed 1, 2,500 points)
Works on D:\\Smith\\Tips\\TipsRaster.aprx (a copy), so ArcGIS Pro may have Tips.aprx open.
"""
import os
import sys

import arcpy
from arcpy.sa import Hillshade

OUT = sys.argv[1]
ONLY = set(sys.argv[2:])
TIPS = r"D:\Smith\Tips"
SCR = os.path.join(TIPS, "MapFigs.gdb")
LAB5 = r"C:\Ames\Lab05GUI\Lab05.gdb"
WS = os.path.join(TIPS, "Watershed.gdb")
LAB8 = r"C:\Ames\Lab09\Check.gdb"
UTM = arcpy.SpatialReference(26912)
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

APRX = os.path.join(TIPS, "TipsRaster.aprx")
if not os.path.exists(APRX):  # keep it between runs: a partial run must not drop the other maps
    arcpy.mp.ArcGISProject(os.path.join(TIPS, "Tips.aprx")).saveACopy(APRX)
aprx = arcpy.mp.ArcGISProject(APRX)


def ramp(name):
    return aprx.listColorRamps(name)[0]


def rgb(r, g, b, a=100):
    return {"RGB": [r, g, b, a]}


def hillshade(dem, name):
    out = os.path.join(SCR, name)
    if not arcpy.Exists(out):
        Hillshade(dem, 315, 45, "NO_SHADOWS", 1).save(out)
    return out


def fresh_map(name):
    for m in aprx.listMaps(name):
        aprx.deleteItem(m)
    m = aprx.createMap(name)
    for lyr in m.listLayers():
        try:
            m.removeLayer(lyr)
        except RuntimeError:
            pass
    return m


def add(m, path, name=None):
    lyr = m.addDataFromPath(path)
    if name:
        lyr.name = name
    return lyr


def stretch(lyr, ramp_name, stype="MinimumMaximum", lo=None, hi=None, invert=False,
            resample="Bilinear"):
    """A stretched ramp; lo/hi fix the ends (the 'Custom' statistics in the pane)."""
    sym = lyr.symbology
    sym.updateColorizer("RasterStretchColorizer")
    sym.colorizer.colorRamp = ramp(ramp_name)
    lyr.symbology = sym
    d = lyr.getDefinition("V3")
    c = d.colorizer
    c.stretchType = stype
    c.invert = invert
    c.resamplingType = resample
    if lo is not None:
        c.useCustomStretchMinMax = True
        c.customStretchMin, c.customStretchMax = lo, hi
    lyr.setDefinition(d)
    return lyr


def classify(lyr, breaks, minimum, resample="Bilinear"):
    """breaks: (upper bound, label, color or None for no color)."""
    sym = lyr.symbology
    sym.updateColorizer("RasterClassifyColorizer")
    sym.colorizer.classificationMethod = "ManualInterval"
    sym.colorizer.breakCount = len(breaks)
    for brk, (ub, label, color) in zip(sym.colorizer.classBreaks, breaks):
        brk.upperBound, brk.label = ub, label
        brk.color = color if color else rgb(255, 255, 255, 0)
    lyr.symbology = sym
    d = lyr.getDefinition("V3")
    d.colorizer.minimumBreak = minimum
    d.colorizer.resamplingType = resample
    lyr.setDefinition(d)
    return lyr


def blend(lyr, mode=None, transparency=0):
    d = lyr.getDefinition("V3")
    if mode:
        d.blendingMode = mode
    d.transparency = transparency
    lyr.setDefinition(d)


def layout(name, frames, w=10.0, h=5.0, cols=None, gap=0.25, title_pt=13):
    """frames: list of (map, extent, title). Equal panels in rows of `cols`."""
    for l in aprx.listLayouts(name):
        aprx.deleteItem(l)
    lyt = aprx.createLayout(w, h, "INCH", name)
    n = len(frames)
    cols = cols or n
    rows = (n + cols - 1) // cols
    fw = (w - gap * (cols + 1)) / cols
    rh = (h - gap) / rows
    fh = rh - 0.45
    for i, (m, ext, title) in enumerate(frames):
        r, c = divmod(i, cols)
        x0 = gap + c * (fw + gap)
        y0 = h - (r + 1) * rh
        box = arcpy.Polygon(arcpy.Array([arcpy.Point(x0, y0), arcpy.Point(x0 + fw, y0),
                                         arcpy.Point(x0 + fw, y0 + fh), arcpy.Point(x0, y0 + fh)]))
        mf = lyt.createMapFrame(box, m, f"Frame {i + 1}")
        mf.camera.setExtent(fit(ext, fw / fh))
        aprx.createTextElement(lyt, arcpy.Point(x0, y0 + fh + 0.08), "POINT", title, title_pt)
    return lyt


def export(lyt, fname, dpi=150):
    lyt.exportToJPEG(os.path.join(OUT, fname), resolution=dpi, jpeg_quality=90)
    print("wrote", fname)


def fit(e, aspect):
    """Grow an extent to the frame's width/height ratio, so no white margins appear."""
    x0, y0, x1, y1 = e.XMin, e.YMin, e.XMax, e.YMax
    w, h = x1 - x0, y1 - y0
    if w / h < aspect:
        d = (h * aspect - w) / 2
        x0, x1 = x0 - d, x1 + d
    else:
        d = (w / aspect - h) / 2
        y0, y1 = y0 - d, y1 + d
    return arcpy.Extent(x0, y0, x1, y1, spatial_reference=UTM)


def ext_of(path, pad=0.0):
    e = arcpy.Describe(path).extent
    return arcpy.Extent(e.XMin - pad, e.YMin - pad, e.XMax + pad, e.YMax + pad,
                        spatial_reference=UTM)


def ext_around(x, y, hw, hh):
    return arcpy.Extent(x - hw, y - hh, x + hw, y + hh, spatial_reference=UTM)


def want(name):
    return not ONLY or name in ONLY


DEM5 = os.path.join(LAB5, "DEM_UTM")
HS5 = hillshade(DEM5, "HS_RockCanyon")
BASIN = os.path.join(SCR, "Basin_snap50")
HS_T = 35  # hillshade transparency in Multiply: 0 is too dark, 50 too faint

# 1. Terrain: as it arrives vs a stretched elevation ramp under a multiplied hillshade ---------
if want("terrain"):
    m0 = fresh_map("Terrain default")
    add(m0, DEM5, "DEM")
    m1 = fresh_map("Terrain finished")
    stretch(add(m1, DEM5, "DEM"), "Elevation #1", "PercentMinimumMaximum")
    blend(add(m1, HS5, "Hillshade"), "Multiply", HS_T)
    e = ext_of(BASIN, 300)
    export(layout("Terrain", [(m0, e, "As it arrives: gray, Percent Clip"),
                              (m1, e, "Elevation #1 ramp, hillshade on top in Multiply")]),
           "raster-terrain.jpg")

# 2. Three ways to add the hillshade ------------------------------------------------------------
if want("hillshade-ways"):
    c = fresh_map("HS none")
    stretch(add(c, DEM5, "DEM"), "Elevation #1", "PercentMinimumMaximum")
    a = fresh_map("HS under")
    add(a, HS5, "Hillshade")
    d = stretch(add(a, DEM5, "DEM"), "Elevation #1", "PercentMinimumMaximum")
    blend(d, None, 45)
    b = fresh_map("HS multiply")
    stretch(add(b, DEM5, "DEM"), "Elevation #1", "PercentMinimumMaximum")
    blend(add(b, HS5, "Hillshade"), "Multiply", HS_T)
    e = ext_around(447800, 4458200, 1800, 1600)
    export(layout("Hillshade ways", [(c, e, "No hillshade"),
                                     (a, e, "DEM 45% transparent over hillshade"),
                                     (b, e, "Hillshade on top, Multiply, 35%")],
                  h=3.9, title_pt=11),
           "raster-hillshade-ways.jpg")

# 3. Stretch types matter on skewed data: flow accumulation -------------------------------------
ACC = os.path.join(WS, "Flow_Accumulation")
if want("stretch-types"):
    frames = []
    e = ext_around(446800, 4457300, 1300, 1100)
    for stype, label in (("MinimumMaximum", "Minimum Maximum"),
                         ("PercentMinimumMaximum", "Percent Clip, 0.5 %"),
                         ("StandardDeviations", "Standard Deviation, n = 2.5")):
        m = fresh_map("Stretch " + stype)
        stretch(add(m, ACC, "Flow accumulation"), "Blues (Continuous)", stype,
                resample="NearestNeighbor")
        frames.append((m, e, label))
    export(layout("Stretch types", frames, h=3.6, title_pt=11), "raster-stretch-types.jpg")

# 3b. Statistics from the dataset vs from the current view, zoomed into one valley --------------
if want("stats-view"):
    e = ext_around(444900, 4456450, 450, 380)
    frames = []
    for stats, label in (("Dataset", "Statistics: Dataset"),
                         ("AreaOfView", "Statistics: DRA (current display extent)")):
        m = fresh_map("Stats " + stats)
        lyr = stretch(add(m, DEM5, "DEM"), "Elevation #1", "PercentMinimumMaximum")
        dd = lyr.getDefinition("V3")
        dd.colorizer.statsType = stats
        lyr.setDefinition(dd)
        blend(add(m, HS5, "Hillshade"), "Multiply", HS_T)
        frames.append((m, e, label))
    export(layout("Stats view", frames), "raster-stats-view.jpg")

# 4. Lab 8: the error maps on their own stretches vs one shared set of classes ----------------
TRUE8 = os.path.join(LAB8, "True_DEM")
HS8 = hillshade(TRUE8, "HS_True8")
STUDY = os.path.join(LAB8, "Study_Area")
ERRS = [("Error_Th_n2500_s1", "Thiessen", 28.29), ("Error_IDW_n2500_s1_p2", "IDW", 20.71),
        ("Error_Kr_n2500_s1_SPH", "Kriging", 14.46)]
ERR = [(-100, "over 100 m high", rgb(165, 0, 38)), (-50, "50 - 100 m high", rgb(215, 48, 39)),
       (-20, "20 - 50 m high", rgb(244, 109, 67)), (-5, "5 - 20 m high", rgb(253, 174, 97)),
       (5, "within 5 m", None), (20, "5 - 20 m low", rgb(171, 217, 233)),
       (50, "20 - 50 m low", rgb(116, 173, 209)), (100, "50 - 100 m low", rgb(69, 117, 180)),
       (700, "over 100 m low", rgb(49, 54, 149))]
if want("lab8-errors"):
    e8 = ext_of(STUDY, 30)
    frames = []
    for r, lab, rmse in ERRS:
        m = fresh_map("Own " + r)
        stretch(add(m, os.path.join(LAB8, r), lab), "Red-Blue (Continuous)", "MinimumMaximum",
                resample="NearestNeighbor")
        frames.append((m, e8, f"{lab}: its own stretch"))
    for r, lab, rmse in ERRS:
        m = fresh_map("Shared " + r)
        blend(add(m, HS8, "Hillshade"), None, 55)
        classify(add(m, os.path.join(LAB8, r), lab), ERR, -700, resample="NearestNeighbor")
        frames.append((m, e8, f"{lab}: shared classes, RMSE {rmse} m"))
    export(layout("Lab 8 errors", frames, h=6.0, cols=3, title_pt=11), "raster-lab8-errors.jpg")

# 5. Lab 8: the surfaces over the true DEM's hillshade vs over their own -----------------------
SURF = [("Thiessen_n2500_s1", "Thiessen"), ("IDW_n2500_s1_p2", "IDW"),
        ("Kriging_n2500_s1_SPH", "Kriging")]
if want("lab8-surfaces"):
    e8 = ext_around(448900, 4453400, 2200, 1650)  # the mountain, where the methods differ
    frames = []
    for row in ("true", "own"):
        for sname, lab in SURF:
            m = fresh_map(f"{row} {sname}")
            sp = os.path.join(LAB8, sname)
            stretch(add(m, sp, lab), "Elevation #1", "MinimumMaximum", 1350, 2900)
            hs = HS8 if row == "true" else hillshade(sp, "HS_" + sname)
            blend(add(m, hs, "Hillshade"), "Multiply", HS_T)
            frames.append((m, e8, f"{lab} over the true hillshade" if row == "true"
                           else f"{lab} over its own hillshade"))
    export(layout("Lab 8 surfaces", frames, h=6.0, cols=3, title_pt=11),
           "raster-lab8-surfaces.jpg")

# 6. Flow accumulation: as it arrives vs log-spaced classes over a light hillshade ------------
FACC = [(1000, "fewer than 1,000 cells", None), (10000, "1,000 - 10,000", rgb(107, 174, 214)),
        (100000, "10,000 - 100,000", rgb(33, 113, 181)), (500000, "over 100,000", rgb(8, 48, 107))]
if want("flow-accumulation"):
    m0 = fresh_map("Acc default")
    add(m0, ACC, "Flow accumulation")
    m1 = fresh_map("Acc finished")
    blend(add(m1, HS5, "Hillshade"), None, 45)
    classify(add(m1, ACC, "Flow accumulation"), FACC, 0, resample="NearestNeighbor")
    e = ext_around(449600, 4457300, 2400, 2000)
    export(layout("Flow accumulation", [(m0, e, "As it arrives: almost all black"),
                                        (m1, e, "Classes by powers of 10, small ones hidden")]),
           "raster-flow-accumulation.jpg")

# 7. Flow direction: unique values as they arrive vs a hue wheel over the hillshade ------------
FDIR = os.path.join(LAB5, "Flow_Directiond8")
# D8 codes run clockwise from east; the hues run once round the wheel, so similar
# directions get similar colors.
WHEEL = [(1, "E", (228, 26, 28)), (2, "SE", (255, 127, 0)), (4, "S", (255, 221, 51)),
         (8, "SW", (77, 175, 74)), (16, "W", (0, 190, 190)), (32, "NW", (55, 126, 184)),
         (64, "N", (117, 70, 170)), (128, "NE", (222, 80, 170))]
if want("flow-direction"):
    m0 = fresh_map("Fdir default")
    add(m0, FDIR, "Flow direction")
    m1 = fresh_map("Fdir wheel")
    f = add(m1, FDIR, "Flow direction")
    sym = f.symbology
    if sym.colorizer.type != "RasterUniqueValueColorizer":
        sym.updateColorizer("RasterUniqueValueColorizer")
        sym.colorizer.field = "Value"
    for grp in sym.colorizer.groups:
        for it in grp.items:
            v = int(float(it.values[0]))
            for code, lab, col in WHEEL:
                if code == v:
                    it.label, it.color = lab, rgb(*col)
    f.symbology = sym
    blend(add(m1, HS5, "Hillshade"), "Multiply", 50)
    e = ext_around(449300, 4457600, 700, 600)
    export(layout("Flow direction", [(m0, e, "As it arrives: unique values, random colors"),
                                     (m1, e, "A hue wheel, E round to NE, hillshade on top")]),
           "raster-flow-direction.jpg")

aprx.save()
