# Render the Week 4 band tiles from C:\Ames\Week04\RemoteSensing.aprx with ArcGIS Pro's own map
# renderer (a layout map frame exported with arcpy), after tools/week04_arcgis_project.py built it.
#   python week04_arcgis_render.py clean     remove the default basemap from every map
#   python week04_arcgis_render.py photos    rs-arcgis-<key>-<band>.jpg, one per band of each photo
#   python week04_arcgis_render.py landsat   rs-arcgis-band-<blue|green|red|nir>.jpg
# Output goes to slides/week-04/images/. Close the project in ArcGIS Pro before running.
import os, sys
import arcpy

APRX = r"C:\Ames\Week04\RemoteSensing.aprx"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "slides", "week-04", "images")
KEYS = {"Eiffel": "eiffel", "Snow": "snow", "Smoke": "smoke", "Night": "night"}
BANDS = {"1": "red", "2": "green", "3": "blue"}
LS = {"B2": "blue", "B3": "green", "B4": "red", "B5": "nir"}


def clean(aprx):
    for m in aprx.listMaps():
        for l in m.listLayers():
            if l.isBasemapLayer or l.name in ("Topographic", "World Hillshade"):
                print("removing", l.name, "from", m.name); m.removeLayer(l)
    aprx.save()


def frame(aprx, w_in, h_in):
    lay = next((l for l in aprx.listLayouts() if l.name == "Render"), None)
    if lay is None:
        lay = aprx.createLayout(w_in, h_in, "INCH", "Render")
    lay.pageWidth, lay.pageHeight = w_in, h_in
    mf = next(iter(lay.listElements("MAPFRAME_ELEMENT")), None)
    if mf is None:
        mf = lay.createMapFrame(arcpy.Point(0, 0), None, "Frame")
    mf.elementPositionX, mf.elementPositionY = 0, 0
    mf.elementWidth, mf.elementHeight = w_in, h_in
    cim = mf.getDefinition("V3")                      # no frame border, no background
    if cim.graphicFrame:
        cim.graphicFrame.borderSymbol = None
        cim.graphicFrame.backgroundSymbol = None
    mf.setDefinition(cim)
    return lay, lay.listElements("MAPFRAME_ELEMENT")[0]


def render(aprx, m, target, out, px_w, dpi=96):
    ext = arcpy.Raster(target.dataSource).extent
    ratio = ext.height / ext.width
    w_in = px_w / dpi
    lay, mf = frame(aprx, w_in, w_in * ratio)
    mf.map = m
    for l in m.listLayers():
        l.visible = l.name == target.name
    mf.camera.setExtent(ext)
    lay.exportToJPEG(out, resolution=dpi, jpeg_quality=92)
    print(out, os.path.getsize(out) // 1000, "KB")


def photos(aprx):
    for m in aprx.listMaps():
        if m.name not in KEYS: continue
        full = next(l for l in m.listLayers() if l.name.endswith("full color"))
        px_w = arcpy.Raster(full.dataSource).width
        for l in m.listLayers():
            if "Band_" not in l.name: continue
            b = BANDS[l.name.split("Band_")[1][0]]
            render(aprx, m, l, os.path.join(OUT, f"rs-arcgis-{KEYS[m.name]}-{b}.jpg"), px_w)


def landsat(aprx):
    from week04_arcgis_project import set_stretch
    m = aprx.listMaps("Landsat")[0]
    for l in m.listLayers():
        if "B5" in l.name:
            # NIR is far brighter over vegetation than any visible band; on the shared 7700-18800
            # stretch every field saturates. Its own 0.5-99.5 percentile stretch (DN 7000-26300).
            set_stretch(l, 7000, 26300, (255, 255, 255))
        b = LS[l.name.split()[2]]
        render(aprx, m, l, os.path.join(OUT, f"rs-arcgis-band-{b}.jpg"), 1400)


if __name__ == "__main__":
    aprx = arcpy.mp.ArcGISProject(APRX)
    {"clean": clean, "photos": photos, "landsat": landsat}[sys.argv[1]](aprx)
    if sys.argv[1] != "clean":
        aprx.save()
