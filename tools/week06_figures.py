"""Week 6 figures rendered by ArcGIS Pro (arcpy.mp) from the Lab 5 Rock Canyon data.

These replace the ArcView-era screen captures and the low-resolution panels the Week 6 decks
inherited from the PowerPoint source. Every map is the real Lab 5 data, rendered by ArcGIS Pro 3.7;
nothing is drawn by hand. The hydrologic units come live from the USGS Watershed Boundary Dataset
map service (hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer).

Needs C:\\Ames\\Lab05\\Check.gdb from tools/lab05/run_model.py and its Hillshade/Log_Accumulation
layers from tools/lab05/build_figures.py (prep). Run with the ArcGIS Pro Python:

    "C:/Program Files/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe" tools/week06_figures.py [name ...]

Writes into slides/week-06/images/ (ws-pro-*.jpg / .png) and prints what it wrote.
"""
import importlib.util
import json
import os
import pathlib
import sys
import urllib.parse
import urllib.request

import arcpy
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bf", HERE / "lab05" / "build_figures.py")
bf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bf)
IMG = HERE.parent / "slides" / "week-06" / "images"
bf.IMG = IMG
GDB = bf.GDB
W6 = r"C:\Ames\Week06\Week06.gdb"
APRX = r"C:\Ames\Week06\Week06_Figures.aprx"
UTM = bf.UTM
rgb = bf.rgb
WBD = "https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer"
TRAILHEAD = (-111.63, 40.26525)
FONT = "C:/Windows/Fonts/segoeui.ttf"
FONTB = "C:/Windows/Fonts/segoeuib.ttf"


def project():
    os.makedirs(r"C:\Ames\Week06", exist_ok=True)
    if not arcpy.Exists(W6):
        arcpy.management.CreateFileGDB(r"C:\Ames\Week06", "Week06.gdb")
    if os.path.exists(APRX):
        os.remove(APRX)
    p = arcpy.mp.ArcGISProject(bf.BLANK)
    p.saveACopy(APRX)
    p = arcpy.mp.ArcGISProject(APRX)
    for x in p.listLayouts() + p.listMaps():
        p.deleteItem(x)
    bf.p_global = p
    return p


def addp(m, path, name):
    lyr = m.addDataFromPath(path)
    lyr.name = name
    return lyr


def box(x, y, half_w, half_h):
    return arcpy.Extent(x - half_w, y - half_h, x + half_w, y + half_h, spatial_reference=UTM)


def labels(lyr, expr, size=9, color=(20, 20, 20), halo=True, bold=True):
    lyr.showLabels = True
    lc = lyr.listLabelClasses()[0]
    lc.expression = expr
    d = lyr.getDefinition("V3")
    for c in d.labelClasses:
        ts = c.textSymbol.symbol
        ts.height = size
        ts.symbol.symbolLayers[0].color.values = list(color) + [100]
        if bold:
            ts.fontStyleName = "Bold"
        if halo:
            ts.haloSize = 1.5
            hs = arcpy.cim.CreateCIMObjectFromClassName("CIMPolygonSymbol", "V3")
            fill = arcpy.cim.CreateCIMObjectFromClassName("CIMSolidFill", "V3")
            fill.color = arcpy.cim.CreateCIMObjectFromClassName("CIMRGBColor", "V3")
            fill.color.values = [255, 255, 255, 100]
            hs.symbolLayers = [fill]
            ts.haloSymbol = hs
    lyr.setDefinition(d)


def unique_raster(m, ras, name, colors, labels_=None, transparency=0):
    lyr = addp(m, os.path.join(GDB, ras), name)
    sym = lyr.symbology
    sym.updateColorizer("RasterUniqueValueColorizer")
    sym.colorizer.field = "Value"
    for grp in sym.colorizer.groups:
        for it in grp.items:
            v = int(float(it.values[0]))
            it.color = rgb(*colors[v]) if isinstance(colors, dict) else rgb(*colors[v % len(colors)])
            if labels_:
                it.label = labels_.get(v, str(v))
    lyr.symbology = sym
    lyr.transparency = transparency
    return lyr


def export(p, m, out, ext, w_in=7.0, dpi=150, jpg=True):
    ratio = ext.height / ext.width
    lay = p.createLayout(w_in, w_in * ratio, "INCH", "Render " + out)
    mf = lay.createMapFrame(bf.poly(0, 0, w_in, w_in * ratio), m, "Frame")
    cim = mf.getDefinition("V3")
    if cim.graphicFrame:
        cim.graphicFrame.borderSymbol = None
    mf.setDefinition(cim)
    mf.camera.setExtent(ext)
    path = str(IMG / out)
    if jpg:
        lay.exportToJPEG(path, resolution=dpi, jpeg_quality=90)
    else:
        lay.exportToPNG(path, resolution=dpi)
    print(out, os.path.getsize(path) // 1000, "KB")
    return lay, mf


def font(size, bold=False):
    return ImageFont.truetype(FONTB if bold else FONT, size)


def caption_strip(img_paths, captions, out, pad=24, cap_h=64, title=None):
    ims = [Image.open(IMG / f).convert("RGB") for f in img_paths]
    h = max(i.height for i in ims)
    ims = [i.resize((int(i.width * h / i.height), h)) for i in ims]
    top = (70 if title else 0)
    W = sum(i.width for i in ims) + pad * (len(ims) + 1)
    sheet = Image.new("RGB", (W, h + cap_h + pad * 2 + top), "white")
    d = ImageDraw.Draw(sheet)
    if title:
        d.text((pad, pad), title, fill=(0, 46, 93), font=font(36, True))
    x = pad
    f = font(28, True)
    for im, cap in zip(ims, captions):
        sheet.paste(im, (x, pad + top))
        d.rectangle([x, pad + top, x + im.width - 1, pad + top + h - 1], outline=(150, 160, 170), width=2)
        lines, cur = [], ""
        for w in cap.split():
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) > im.width:
                lines.append(cur); cur = w
            else:
                cur = t
        lines.append(cur)
        for k, ln in enumerate(lines):
            d.text((x, pad + top + h + 10 + 36 * k), ln, fill=(0, 46, 93), font=f)
        x += im.width + pad
    sheet.save(IMG / out, quality=90)
    for f in img_paths:
        os.remove(IMG / f)
    print(out, sheet.size)


# ----------------------------------------------------------------------------------------------
D8 = {1: "1  east", 2: "2  southeast", 4: "4  south", 8: "8  southwest",
      16: "16  west", 32: "32  northwest", 64: "64  north", 128: "128  northeast"}
D8C = {1: (230, 75, 53), 2: (240, 160, 40), 4: (250, 220, 70), 8: (120, 190, 80),
       16: (40, 150, 140), 32: (60, 110, 200), 64: (120, 80, 170), 128: (200, 90, 160)}
RANDOM = [(141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114), (128, 177, 211),
          (253, 180, 98), (179, 222, 105), (252, 205, 229), (217, 217, 217), (188, 128, 189),
          (204, 235, 197), (255, 237, 111)]


def dem(p):
    m = bf.new_map(p, "DEM")
    bf.gray_raster(m, "Hillshade", "Hillshade")
    bf.stretch(m, "DEM_UTM", "Elevation", "Elevation #1", 45)
    e = arcpy.Describe(os.path.join(GDB, "DEM_UTM")).extent
    export(p, m, "ws-pro-dem.jpg", arcpy.Extent(e.XMin, e.YMin, e.XMax, e.YMax, spatial_reference=UTM))


def flowdir(p):
    m = bf.new_map(p, "FlowDir")
    unique_raster(m, "Flow_Direction", "Flow direction (D8 code)", D8C, D8, 0)
    x, y = 450007, 4459047
    ext = box(x, y, 300, 200)
    lay = p.createLayout(7.75, 4.0, "INCH", "FlowDir layout")   # legend sits tight against the map
    mf = lay.createMapFrame(bf.poly(0, 0, 6.0, 4.0), m, "Frame")
    mf.camera.setExtent(ext)
    style = (p.listStyleItems("ArcGIS 2D", "LEGEND", "Legend 1") or [None])[0]
    leg = lay.createMapSurroundElement(bf.poly(6.15, 0.2, 7.7, 3.8), "LEGEND", mf, style, "Legend")
    leg.title = "D8 code and direction"
    d = leg.getDefinition("V3")
    for it in d.items:
        it.showHeading = False
        it.showLayerName = False
    leg.setDefinition(d)
    lay.exportToPNG(str(IMG / "ws-pro-flow-direction.png"), resolution=150)
    print("ws-pro-flow-direction.png")


def thresholds(p):
    ext = bf.ext_of("Rock_Canyon_Basin", 250)
    outs = []
    for th in (500, 5000):
        m = bf.new_map(p, f"T{th}")
        bf.gray_raster(m, "Hillshade", "Hillshade")
        bf.poly_layer(m, "Rock_Canyon_Basin", "Basin", fill=rgb(255, 255, 255, 35), outline=rgb(40, 40, 40), width=1.6)
        bf.line_layer(m, f"Streams_{th}", "Streams", rgb(0, 70, 210), 1.6)
        export(p, m, f"_t{th}.jpg", ext, w_in=5.2)
        outs.append(f"_t{th}.jpg")
    caption_strip(outs, ["500 cells (0.05 km²): 290 segments, 83 km of stream",
                         "5,000 cells (0.5 km²): 29 segments, 23 km of stream"], "ws-pro-thresholds.jpg")


def junction():
    """A node of Streams_5000 where two links meet a third, to zoom on."""
    ends = {}
    with arcpy.da.SearchCursor(os.path.join(GDB, "Streams_5000"), ["from_node", "to_node", "SHAPE@"]) as cur:
        rows = list(cur)
    for f, t, g in rows:
        ends.setdefault(t, []).append(g)
    e = arcpy.Describe(os.path.join(GDB, "Rock_Canyon_Basin")).extent
    cx, cy = (e.XMin + e.XMax) / 2, (e.YMin + e.YMax) / 2
    best, bd = None, None
    for node, gs in ends.items():
        if len(gs) == 2:
            pt = gs[0].lastPoint
            d = (pt.X - cx) ** 2 + (pt.Y - cy) ** 2
            if bd is None or d < bd:      # the junction nearest the middle of the basin
                best, bd = pt, d
    return best


def links(p):
    pt = junction()
    m = bf.new_map(p, "Links")
    bf.gray_raster(m, "Hillshade", "Hillshade", 30)
    unique_raster(m, "Stream_Links_5000", "Stream_Links (raster)", RANDOM, None, 0)
    lyr = bf.line_layer(m, "Streams_5000", "Streams (lines)", rgb(20, 20, 20), 1.0)
    labels(lyr, '"grid_code " + $feature.grid_code', 11)
    d = lyr.getDefinition("V3")
    for c in d.labelClasses:
        c.maplexLabelPlacementProperties.linePlacementMethod = "OffsetHorizontalFromLine"
    lyr.setDefinition(d)
    export(p, m, "ws-pro-links-gridcode.jpg", box(pt.X, pt.Y, 450, 260), w_in=8.0)


def subwatersheds(p):
    m = bf.new_map(p, "Subs")
    bf.gray_raster(m, "Hillshade", "Hillshade")
    bf.unique_polys(m, "Subwatersheds_5000", "Subwatersheds", 40)
    lyr = bf.poly_layer(m, "Subwatersheds_5000", "Subwatershed labels", fill=rgb(0, 0, 0, 0), outline=rgb(255, 255, 255), width=0.8)
    labels(lyr, "$feature.gridcode", 9)
    bf.line_layer(m, "Streams_5000", "Streams", rgb(0, 60, 200), 1.6)
    export(p, m, "ws-pro-subwatersheds-ids.jpg", bf.ext_of("Rock_Canyon_Basin", 200), w_in=8.0)
    m = bf.new_map(p, "SubsImagery", "Imagery")
    bf.unique_polys(m, "Subwatersheds_5000", "Subwatersheds", 50, rgb(255, 255, 255), 1.0)
    bf.line_layer(m, "Streams_5000", "Streams", rgb(255, 120, 0), 1.8)
    bf.poly_layer(m, "Rock_Canyon_Basin", "Basin", fill=rgb(0, 0, 0, 0), outline=rgb(255, 255, 0), width=2.2)
    bf.point_layer(m, "Snapped_Outlet_Point", "Outlet", "Circle 3", rgb(255, 0, 0), 9)
    export(p, m, "ws-pro-subwatersheds-imagery.jpg", bf.ext_of("Rock_Canyon_Basin", 350), w_in=8.0)


def topo(p):
    m = bf.new_map(p, "Topo", "Topographic")
    bf.poly_layer(m, "Rock_Canyon_Basin", "Basin", fill=rgb(255, 0, 255, 0), outline=rgb(200, 0, 200), width=2.4)
    bf.line_layer(m, "Streams_5000", "Streams", rgb(0, 70, 220), 1.8)
    bf.point_layer(m, "Snapped_Outlet_Point", "Outlet", "Circle 3", rgb(255, 0, 0), 10)
    export(p, m, "ws-pro-basin-topo.jpg", bf.ext_of("Rock_Canyon_Basin", 500), w_in=6.0)


def panels(p):
    ext = bf.ext_of("Rock_Canyon_Basin", 150)
    specs = []
    m = bf.new_map(p, "P1"); bf.gray_raster(m, "Hillshade", "Hillshade"); bf.stretch(m, "DEM_UTM", "Elevation", "Elevation #1", 45)
    specs.append((m, "(A) DEM"))
    m = bf.new_map(p, "P2"); unique_raster(m, "Flow_Direction", "D8", D8C, D8, 0)
    specs.append((m, "(B) Flow direction"))
    m = bf.new_map(p, "P3"); bf.gray_raster(m, "Hillshade", "Hillshade"); bf.stretch(m, "Log_Accumulation", "acc", "Blues (Continuous)", 0, 1.0, 4.5)
    specs.append((m, "(C) Flow accumulation"))
    m = bf.new_map(p, "P4"); bf.gray_raster(m, "Hillshade", "Hillshade"); bf.line_layer(m, "Streams_5000", "Streams", rgb(0, 70, 210), 2.0)
    bf.poly_layer(m, "Rock_Canyon_Basin", "Basin", fill=rgb(0, 0, 0, 0), outline=rgb(30, 30, 30), width=1.6)
    specs.append((m, "(D) Streams and basin"))
    m = bf.new_map(p, "P5"); bf.gray_raster(m, "Hillshade", "Hillshade"); bf.unique_polys(m, "Subwatersheds_5000", "Subs", 35)
    bf.line_layer(m, "Streams_5000", "Streams", rgb(0, 60, 200), 1.6)
    specs.append((m, "(E) Subwatersheds"))
    outs = []
    for i, (m, cap) in enumerate(specs):
        export(p, m, f"_p{i}.jpg", ext, w_in=3.6)
        outs.append(f"_p{i}.jpg")
    # two rows: A B C / D E
    ims = [Image.open(IMG / f).convert("RGB") for f in outs]
    w, h = ims[0].size
    pad, cap = 20, 50
    sheet = Image.new("RGB", (3 * w + 4 * pad, 2 * (h + cap) + 3 * pad), "white")
    d = ImageDraw.Draw(sheet)
    caps = [c for _, c in specs]
    for i, im in enumerate(ims):
        r, c = divmod(i, 3)
        x = pad + c * (w + pad) + (0 if r == 0 else (w + pad) // 2)
        y = pad + r * (h + cap + pad)
        sheet.paste(im, (x, y))
        d.rectangle([x, y, x + w - 1, y + h - 1], outline=(150, 160, 170), width=2)
        d.text((x, y + h + 8), caps[i], fill=(0, 46, 93), font=font(28, True))
    sheet.save(IMG / "ws-pro-terrain-panels.jpg", quality=90)
    for f in outs:
        os.remove(IMG / f)
    print("ws-pro-terrain-panels.jpg", sheet.size)


def fetch_hucs():
    """Pull the nested hydrologic units around the trailhead from the WBD service."""
    def q(layer, **params):
        base = dict(outFields="*", returnGeometry="true", outSR="4326", f="json", maxAllowableOffset="0.001")
        base.update(params)
        url = f"{WBD}/{layer}/query?" + urllib.parse.urlencode(base)
        with urllib.request.urlopen(url, timeout=120) as r:
            return json.loads(r.read().decode())
    pt = dict(geometry=f"{TRAILHEAD[0]},{TRAILHEAD[1]}", geometryType="esriGeometryPoint", inSR="4326",
              spatialRel="esriSpatialRelIntersects")
    sets = {"HUC4": q(2, maxAllowableOffset="0.01", **pt), "HUC6": q(3, where="huc6 LIKE '1602%'", maxAllowableOffset="0.005"),
            "HUC8": q(4, where="huc8 LIKE '160202%'", maxAllowableOffset="0.002"),
            "HUC10": q(5, where="huc10 LIKE '16020203%'"), "HUC12": q(6, where="huc12 LIKE '1602020305%'")}
    for name, js in sets.items():
        tmp = os.path.join(os.environ["TEMP"], f"wbd_{name}.json")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(js, f)
        gcs = os.path.join(W6, name + "_gcs")
        arcpy.conversion.JSONToFeatures(tmp, gcs)
        arcpy.management.Project(gcs, os.path.join(W6, name), UTM)
        print(name, arcpy.management.GetCount(os.path.join(W6, name))[0], "features")


def hucs(p):
    if not arcpy.Exists(os.path.join(W6, "HUC12")):
        fetch_hucs()
    # left: the Great Salt Lake subregion (HUC4) and its basins (HUC6), Provo (HUC8) highlighted
    m = bf.new_map(p, "HUC big", "Topographic")
    for n, fill, out, w in (("HUC4", rgb(255, 255, 255, 0), rgb(0, 46, 93), 2.6),
                            ("HUC6", rgb(255, 255, 255, 0), rgb(90, 110, 140), 1.2)):
        lyr = addp(m, os.path.join(W6, n), n)
        sym = lyr.symbology; s = sym.renderer.symbol; s.color = fill; s.outlineColor = out; s.outlineWidth = w; lyr.symbology = sym
    lyr = addp(m, os.path.join(W6, "HUC8"), "Provo HUC8")
    lyr.definitionQuery = "huc8 = '16020203'"
    sym = lyr.symbology; s = sym.renderer.symbol; s.color = rgb(230, 120, 30, 55); s.outlineColor = rgb(200, 90, 0); s.outlineWidth = 1.5; lyr.symbology = sym
    e = arcpy.Describe(os.path.join(W6, "HUC4")).extent
    big = arcpy.Extent(e.XMin - 10000, e.YMin - 10000, e.XMax + 10000, e.YMax + 10000, spatial_reference=UTM)
    export(p, m, "_huc_big.jpg", big, w_in=4.4)
    # right: Provo HUC8 > Outlet Provo River HUC10 > its HUC12s > the Lab 5 basin
    m = bf.new_map(p, "HUC small", "Topographic")
    lyr = addp(m, os.path.join(W6, "HUC12"), "HUC12")
    sym = lyr.symbology; s = sym.renderer.symbol; s.color = rgb(255, 255, 255, 0); s.outlineColor = rgb(90, 110, 140); s.outlineWidth = 1.0; lyr.symbology = sym
    lyr = addp(m, os.path.join(W6, "HUC12"), "Rock Canyon HUC12")
    lyr.definitionQuery = "huc12 = '160202030505'"
    sym = lyr.symbology; s = sym.renderer.symbol; s.color = rgb(230, 120, 30, 35); s.outlineColor = rgb(200, 90, 0); s.outlineWidth = 2.0; lyr.symbology = sym
    lyr = addp(m, os.path.join(W6, "HUC10"), "HUC10")
    lyr.definitionQuery = "huc10 = '1602020305'"
    sym = lyr.symbology; s = sym.renderer.symbol; s.color = rgb(255, 255, 255, 0); s.outlineColor = rgb(0, 46, 93); s.outlineWidth = 2.6; lyr.symbology = sym
    bf.poly_layer(m, "Rock_Canyon_Basin", "Lab 5 basin", fill=rgb(200, 0, 0, 45), outline=rgb(200, 0, 0), width=1.6)
    with arcpy.da.SearchCursor(os.path.join(W6, "HUC10"), ["SHAPE@"], "huc10 = '1602020305'") as cur:
        e = next(cur)[0].extent
    small = arcpy.Extent(e.XMin - 1500, e.YMin - 1500, e.XMax + 1500, e.YMax + 1500, spatial_reference=UTM)
    export(p, m, "_huc_small.jpg", small, w_in=4.4)
    caption_strip(["_huc_big.jpg", "_huc_small.jpg"],
                  ["Great Salt Lake subregion (HUC4), its basins (HUC6); Provo (HUC8) in orange",
                   "Outlet Provo River (HUC10) and its subwatersheds (HUC12); Rock Canyon-Provo River HUC12 in orange, the Lab 5 basin in red"],
                  "ws-pro-nested-hucs.jpg", cap_h=120)


def anatomy_points():
    """Label points for the watershed-anatomy scene, computed from the Lab 5 data (towns and the lake
    are placed at their published coordinates)."""
    import numpy as np, math
    fc = os.path.join(W6, "Anatomy_Labels")
    if arcpy.Exists(fc):
        arcpy.management.Delete(fc)
    arcpy.management.CreateFeatureclass(W6, "Anatomy_Labels", "POINT", spatial_reference=UTM)
    arcpy.management.AddField(fc, "Name", "TEXT", field_length=40)
    pts = []
    with arcpy.da.SearchCursor(os.path.join(GDB, "Snapped_Outlet_Point"), ["SHAPE@XY"]) as c:
        pts.append(("Outlet", next(c)[0]))
    with arcpy.da.SearchCursor(os.path.join(GDB, "Rock_Canyon_Basin"), ["SHAPE@"]) as c:
        g = next(c)[0]
    verts = [v for part in g for v in part if v]
    top = max(verts, key=lambda v: v.Y)
    pts.append(("Watershed divide", (top.X, top.Y)))
    dem = arcpy.Raster(os.path.join(GDB, "DEM_UTM"))
    inb = arcpy.sa.ExtractByMask(dem, os.path.join(GDB, "Basin_Raster"))
    a = arcpy.RasterToNumPyArray(inb, nodata_to_value=-9999)
    r, cc = np.unravel_index(np.argmax(a), a.shape)
    pts.append(("Provo Peak (highest point)", (inb.extent.XMin + (cc + .5) * 10, inb.extent.YMax - (r + .5) * 10)))
    rows = [(r_[0], r_[1]) for r_ in arcpy.da.SearchCursor(os.path.join(GDB, "Streams_5000"), ["SHAPE@", "grid_code"])]
    trunk = min(rows, key=lambda t: t[0].extent.XMin)[0]
    pts.append(("Main stem", (trunk.positionAlongLine(0.5, True).firstPoint.X, trunk.positionAlongLine(0.5, True).firstPoint.Y)))
    trib = max(rows, key=lambda t: t[0].extent.YMax)[0]
    pts.append(("Tributary", (trib.positionAlongLine(0.5, True).firstPoint.X, trib.positionAlongLine(0.5, True).firstPoint.Y)))
    subs = [(r_[0], r_[1]) for r_ in arcpy.da.SearchCursor(os.path.join(GDB, "Subwatersheds_5000"), ["SHAPE@", "SHAPE@AREA"])]
    big = max(subs, key=lambda t: t[1])[0]
    pts.append(("Subwatershed", (big.labelPoint.X, big.labelPoint.Y)))
    for name, lon, lat in (("Provo", -111.6585, 40.2338), ("Utah Lake", -111.76, 40.21)):
        q = arcpy.PointGeometry(arcpy.Point(lon, lat), arcpy.SpatialReference(4326)).projectAs(UTM).firstPoint
        pts.append((name, (q.X, q.Y)))
    with arcpy.da.InsertCursor(fc, ["Name", "SHAPE@XY"]) as cur:
        for n, xy in pts:
            cur.insertRow([n, xy])
    print("anatomy labels:", [(n, round(xy[0]), round(xy[1])) for n, xy in pts])
    return fc


def anatomy(p, dist=10500, head=65, pitch=-30, z=5200):
    """Oblique 3D view of the Rock Canyon watershed with its parts labeled.

    Scene labels do not export from a layout, so the points are rendered once in pure magenta, found in
    the image, and labeled there; then the scene is rendered again with white dots and the labels are
    drawn on top. Points outside the view are left out."""
    import math
    import numpy as np
    from scipy import ndimage
    fc = anatomy_points()
    names = [r_[0] for r_ in arcpy.da.SearchCursor(fc, ["Name"])]
    m = p.createMap("Anatomy", "SCENE")
    m.addBasemap("Imagery")
    subs = addp(m, os.path.join(GDB, "Subwatersheds_5000"), "Subwatersheds")
    sym = subs.symbology; s_ = sym.renderer.symbol; s_.color = rgb(255, 255, 255, 0); s_.outlineColor = rgb(255, 255, 255, 70); s_.outlineWidth = 0.8; subs.symbology = sym
    basin = addp(m, os.path.join(GDB, "Rock_Canyon_Basin"), "Basin")
    sym = basin.symbology; s_ = sym.renderer.symbol; s_.color = rgb(255, 210, 0, 12); s_.outlineColor = rgb(255, 215, 0); s_.outlineWidth = 3.0; basin.symbology = sym
    st = addp(m, os.path.join(GDB, "Streams_5000"), "Streams")
    sym = st.symbology; sym.renderer.symbol.color = rgb(40, 150, 255); sym.renderer.symbol.size = 3.0; st.symbology = sym
    lay = p.createLayout(10.0, 5.625, "INCH", "Anatomy")
    mf = lay.createMapFrame(bf.poly(0, 0, 10.0, 5.625), m, "Frame")
    e = arcpy.Describe(os.path.join(GDB, "Rock_Canyon_Basin")).extent
    cx, cy = (e.XMin + e.XMax) / 2, (e.YMin + e.YMax) / 2
    hx, hy = math.sin(math.radians(head)), math.cos(math.radians(head))
    cim = mf.getDefinition("V3")
    cim.autoCamera = None
    cim.view.viewingMode = "SceneLocal"
    cam = cim.view.camera
    cam.x, cam.y, cam.z, cam.pitch, cam.heading, cam.scale = cx - dist * hx, cy - dist * hy, z, pitch, -head, 0
    mf.setDefinition(cim)
    found = {}
    tmp = str(IMG / "_anat_probe.png")
    for n in names:   # one probe render per point, so each magenta blob is known by name
        lyr = addp(m, fc, "probe")
        lyr.definitionQuery = "Name = '" + n.replace("'", "''") + "'"
        sym = lyr.symbology; s_ = sym.renderer.symbol; s_.applySymbolFromGallery("Circle 1"); s_.color = rgb(255, 0, 255); s_.size = 9; lyr.symbology = sym
        lay.exportToPNG(tmp, resolution=150)
        a = np.asarray(Image.open(tmp).convert("RGB")).astype(int)
        mask = (a[..., 0] > 220) & (a[..., 1] < 60) & (a[..., 2] > 220)
        if mask.sum() > 5:
            ys, xs = np.nonzero(mask)
            found[n] = (xs.mean(), ys.mean())
        m.removeLayer(lyr)
    os.remove(tmp)
    lab = addp(m, fc, "Points")
    sym = lab.symbology; s_ = sym.renderer.symbol; s_.applySymbolFromGallery("Circle 1"); s_.color = rgb(255, 255, 255); s_.size = 8; lab.symbology = sym
    out = IMG / "ws-pro-watershed-anatomy.jpg"
    lay.exportToJPEG(str(out), resolution=150, jpeg_quality=92)
    im = Image.open(out).convert("RGB"); d = ImageDraw.Draw(im); f = font(44, True)
    for n, (x, y) in found.items():
        tw = d.textlength(n, font=f)
        tx = min(max(x + 16, 10), im.width - tw - 10); ty = y - 56
        for dx in (-2, -1, 0, 1, 2):
            for dy in (-2, -1, 0, 1, 2):
                d.text((tx + dx, ty + dy), n, font=f, fill=(0, 30, 60))
        d.text((tx, ty), n, font=f, fill=(255, 255, 255))
    im.save(out, quality=92)
    print("ws-pro-watershed-anatomy.jpg; labeled:", list(found))

ALL = dict(dem=dem, flowdir=flowdir, thresholds=thresholds, links=links, subwatersheds=subwatersheds,
           topo=topo, panels=panels, hucs=hucs, anatomy=anatomy)

if __name__ == "__main__":
    names = sys.argv[1:] or list(ALL)
    p = project()
    for n in names:
        ALL[n](p)
    p.save()
