r"""Lab 12 example layouts, rendered by ArcGIS Pro (arcpy.mp) from run_model.py's reference outputs in
C:\Ames\Lab12\ref\Ref.gdb (run run_model.py first). Map 1 is the baseline: the 4 and 8 minute service
areas, the blocks outside 4 minutes and the stations. Map 2 is the straight-line contrast: the 3.75 km
buffer beside the 4 minute network area, with the blocks the buffer counts as covered but the roads
do not. Reuses the Lab 5 layout helpers.

    python build_figures.py
Writes docs/assignments/lab-12/images/lab12-example-map-baseline.png and -crow.png, and prints
every number the layouts state.   ArcGIS Pro Python.
"""
import importlib.util
import json
import os
import pathlib
import urllib.parse
import urllib.request

import arcpy

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bf", HERE.parent / "lab05" / "build_figures.py")
bf = importlib.util.module_from_spec(spec); spec.loader.exec_module(bf)
spec = importlib.util.spec_from_file_location("rm", HERE / "run_model.py")
rm = importlib.util.module_from_spec(spec); spec.loader.exec_module(rm)
IMG = HERE.parents[1] / "docs" / "assignments" / "lab-12" / "images"
bf.IMG = IMG
G = rm.G
SRC = rm.SRC
APRX = r"C:\Ames\Lab12\Lab12_Figures.aprx"
FIG = r"C:\Ames\Lab12\fig.gdb"   # the figure's own data, so it never writes into Ref.gdb
UTM = arcpy.SpatialReference(26912)
rgb = bf.rgb
CK = json.loads((HERE / "check_values.json").read_text())
CK["sensitivity"] = json.load(open(rm.sensitivity_path(str(HERE), "12")))  # private repo
UGRC = "https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services"


def prep():
    rm.setup()
    arcpy.env.workspace = FIG
    if not arcpy.Exists(FIG):
        arcpy.management.CreateFileGDB(os.path.dirname(FIG), os.path.basename(FIG))
    if not arcpy.Exists(os.path.join(FIG, "Utah_County")):
        q = urllib.parse.urlencode({"where": "NAME = 'UTAH'", "outFields": "NAME,FIPS", "returnGeometry": "true", "outSR": 26912, "f": "json"})
        with urllib.request.urlopen(f"{UGRC}/UtahCountyBoundaries/FeatureServer/0/query", q.encode(), timeout=120) as r:
            jp = os.path.join(os.path.dirname(FIG), "county.json"); open(jp, "w").write(r.read().decode())
        arcpy.conversion.JSONToFeatures(jp, os.path.join(FIG, "Utah_County"))
    # blocks the buffer counts as covered but the network does not: unserved by the roads, center inside the buffer
    lyr = arcpy.management.MakeFeatureLayer(os.path.join(G, "Unserved_base"), "ub")
    arcpy.management.SelectLayerByLocation(lyr, "HAVE_THEIR_CENTER_IN", os.path.join(G, "Crow_base"))
    arcpy.management.CopyFeatures(lyr, os.path.join(FIG, "Crow_Only"))
    pop = int(sum(r[0] or 0 for r in arcpy.da.SearchCursor(os.path.join(FIG, "Crow_Only"), ["PP_TOTAL"])))
    n = lambda fc, where: int(arcpy.management.GetCount(arcpy.management.MakeFeatureLayer(fc, "n_" + os.path.basename(fc), where))[0])
    return {"crow_only_people": pop, "crow_only_blocks": int(arcpy.management.GetCount(os.path.join(FIG, "Crow_Only"))[0]),
            "crow_only_populated": n(os.path.join(FIG, "Crow_Only"), "PP_TOTAL > 0"),
            "unserved_populated": n(os.path.join(G, "Unserved_base"), "PP_TOTAL > 0")}


def project():
    if os.path.exists(APRX):
        os.remove(APRX)
    p = arcpy.mp.ArcGISProject(bf.BLANK); p.saveACopy(APRX); p = arcpy.mp.ArcGISProject(APRX)
    for x in p.listLayouts() + p.listMaps():
        p.deleteItem(x)
    bf.p_global = p
    return p


def add(m, path, name):
    lyr = m.addDataFromPath(path); lyr.name = name
    return lyr


def poly(m, path, name, fill, outline, width, transparency=0, dashed=False, where=None):
    lyr = add(m, path, name)
    if where:
        lyr.definitionQuery = where
    sym = lyr.symbology; s = sym.renderer.symbol
    s.color = fill; s.outlineColor = outline; s.outlineWidth = width
    lyr.symbology = sym; lyr.transparency = transparency
    if dashed:
        d = lyr.getDefinition("V3")
        for sl in d.renderer.symbol.symbol.symbolLayers:
            if sl.__class__.__name__ == "CIMSolidStroke":
                eff = arcpy.cim.CreateCIMObjectFromClassName("CIMGeometricEffectDashes", "V3")
                eff.dashTemplate = [6, 3]; sl.effects = [eff]
        lyr.setDefinition(d)
    return lyr


def rings(m, path, name4, name8):
    """The two-cutoff service area, one color per ring (ToBreak 4 and 8)."""
    lyr = add(m, path, "rings")
    sym = lyr.symbology
    sym.updateRenderer("UniqueValueRenderer")
    sym.renderer.fields = ["ToBreak"]
    for grp in sym.renderer.groups:
        for it in grp.items:
            v = float(it.values[0][0])
            it.label = name4 if v <= 4 else name8
            it.symbol.color = rgb(30, 90, 200, 100) if v <= 4 else rgb(120, 170, 240, 100)
            it.symbol.outlineColor = rgb(255, 255, 255, 60); it.symbol.outlineWidth = 0.4
    lyr.symbology = sym
    lyr.name = "Drive time from the nearest fire station"
    d = lyr.getDefinition("V3")
    for grp in d.renderer.groups:
        grp.heading = ""
    lyr.setDefinition(d)
    return lyr


def stations(m):
    lyr = add(m, rm.STATIONS, "Fire stations (42)")
    sym = lyr.symbology; s = sym.renderer.symbol
    s.applySymbolFromGallery("Circle 3"); s.color = rgb(220, 0, 0); s.size = 9; lyr.symbology = sym
    return lyr


def layout(p, lname, m, title, subtitle, notes, fname):
    lyt = p.createLayout(8.5, 11, "INCH", lname)
    p.createPredefinedGraphicElement(lyt, bf.poly(0.35, 0.35, 8.15, 10.65), "RECTANGLE", None, "Neatline")
    for txt, y, sz, nm in ((title, 10.28, 17, "Title"), (subtitle, 9.98, 9, "Subtitle")):
        el = p.createTextElement(lyt, arcpy.Point(4.25, y), "POINT", txt, sz, None, nm)
        try:
            el.setAnchor("CENTER_POINT"); el.elementPositionX = 4.25
        except Exception as ex:
            print("anchor:", ex)
    mf = lyt.createMapFrame(bf.poly(0.5, 3.35, 8.0, 9.75), m, "Main")
    ext = arcpy.Describe(os.path.join(G, "Served_rings")).extent
    pad = 3000
    mf.camera.setExtent(arcpy.Extent(ext.XMin - pad, ext.YMin - pad, ext.XMax + pad, ext.YMax + pad, spatial_reference=UTM))
    style = lambda cls, name: (p.listStyleItems("ArcGIS 2D", cls, name) or [None])[0]
    leg = lyt.createMapSurroundElement(bf.poly(0.5, 1.4, 8.0, 3.3), "LEGEND", mf, style("LEGEND", "Legend 1"), "Legend")
    for it in leg.items:
        if any(k in it.name for k in ("Imagery", "World", "Reference", "Utah County")):
            leg.removeItem(it)
    leg.title = ""; leg.fittingStrategy = "AdjustColumnsAndFont"
    if leg.isOverflowing:
        print("legend overflowing")
    lyt.createMapSurroundElement(arcpy.Point(7.75, 9.25), "NORTH_ARROW", mf, style("NORTH_ARROW", "ArcGIS North 1"), "North")
    sb = lyt.createMapSurroundElement(bf.poly(0.65, 3.5, 2.9, 3.85), "SCALE_BAR", mf, style("SCALE_BAR", "Scale Line 1"), "Scale")
    try:
        sd = sb.getDefinition("V3")
        if isinstance(sd.units, dict):
            sd.units["uwkid"] = 9036
        else:
            sd.units.uwkid = 9036
        sd.unitLabel = "km"; sd.fittingStrategy = "AdjustFrame"; sd.division = 5; sd.divisions = 2
        sd.subdivisions = 1; sd.divisionsBeforeZero = 0; sd.labelFrequency = "Divisions"
        sb.setDefinition(sd)
    except Exception as ex:
        print("scale bar:", ex)
    p.createPredefinedGraphicElement(lyt, bf.poly(0.5, 0.5, 8.0, 1.3), "RECTANGLE", None, "TextBoxFrame")
    p.createTextElement(lyt, bf.poly(0.57, 0.53, 7.95, 1.27), "POLYGON", notes[0] + "\n" + " ".join(notes[1:]), 6.5, None, "Notes")
    out = IMG / fname
    lyt.exportToPNG(str(out), resolution=150)
    print("exported", out)


def layouts(p, extra):
    b, c = CK["baseline"], CK["crow_default"]
    pop = CK["inputs"]["population"]
    r8 = next(r for r in CK["sensitivity"]["cutoffs"] if r["cutoffs"][0] == 8)
    common = ["Map by Dan Ames, CE 414, October 2026. Projection: NAD 1983 UTM zone 12N.",
              "Data: UGRC Utah Street Network (roads through September 2026; travel minutes are UGRC's, for typical traffic, not",
              "emergency driving), UGRC Fire Stations (last update September 2022), 2020 Census blocks (UGRC); imagery basemap by Esri."]
    # Map 1
    m = bf.new_map(p, "Baseline map", "Imagery")
    poly(m, os.path.join("C:\\Ames\\Lab12\\fig.gdb", "Utah_County"), "Utah County", rgb(0, 0, 0, 0), rgb(255, 255, 255), 1.2)
    poly(m, os.path.join(G, "Unserved_base"), f"Populated blocks whose center is more than 4 minutes from a station ({extra['unserved_populated']:,} of {b['blocks']:,} blocks; {b['population']:,} people)",
         rgb(255, 140, 0, 90), rgb(255, 140, 0, 160), 0.4, where="PP_TOTAL > 0")
    rings(m, os.path.join(G, "Served_rings"), "Within 4 minutes", "4 to 8 minutes")
    stations(m)
    layout(p, "Baseline map", m, "Fire Response Coverage in Utah County",
           f"Baseline: 4 minutes of driving from the 42 fire stations, along the road network\n"
           f"{b['population']:,} of {pop:,} residents ({b['pct_outside']} %) live in blocks whose center is outside that reach",
           [f"Result: the 4-minute service area covers {b['area_km2']:,.1f} sq km and the 8-minute area {r8['area_km2']:,.1f} sq km; "
            f"{r8['population']:,} people ({r8['pct_outside']} %) are outside 8 minutes."] + common,
           "lab12-example-map-baseline.png")
    # Map 2
    m2 = bf.new_map(p, "Crow map", "Imagery")
    poly(m2, os.path.join("C:\\Ames\\Lab12\\fig.gdb", "Utah_County"), "Utah County", rgb(0, 0, 0, 0), rgb(255, 255, 255), 1.2)
    poly(m2, os.path.join(G, "Served_base"), "Within 4 minutes along the roads", rgb(30, 90, 200, 100), rgb(255, 255, 255, 60), 0.4)
    poly(m2, os.path.join(G, "Crow_base"), "Within 3.75 km in a straight line (4 minutes at 35 mph)", rgb(0, 0, 0, 0), rgb(255, 230, 0), 1.8, dashed=True)
    poly(m2, os.path.join("C:\\Ames\\Lab12\\fig.gdb", "Crow_Only"),
         f"Blocks the buffer counts as covered but the roads do not ({extra['crow_only_blocks']:,} blocks, {extra['crow_only_people']:,} people)",
         rgb(255, 140, 0, 110), rgb(255, 140, 0), 0.5)
    stations(m2)
    layout(p, "Crow map", m2, "Straight-Line Distance versus Network Distance",
           f"Changed: the same 4 minutes measured as the crow flies (3.75 km) instead of along the roads\n"
           f"Buffer: {c['population']:,} people outside ({c['pct_outside']} %); network: {b['population']:,} outside ({b['pct_outside']} %)",
           [f"Result: the buffer covers {c['area_km2']:,.1f} sq km against the network's {b['area_km2']:,.1f}; "
            f"{extra['crow_only_people']:,} people live in blocks the buffer reaches that four minutes of driving does not."] + common,
           "lab12-example-map-crow.png")


if __name__ == "__main__":
    extra = prep()
    print(extra)
    p = project()
    layouts(p, extra)
    p.save()
