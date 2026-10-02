"""Week 6 pit-filling figures from the real Lab 5 DEM.

The deepest pit Fill finds in the Lab 5 DEM is a closed hollow high in the mountains east of Rock
Canyon (UTM 454,727 E 4,456,097 N, about 40.2541 N 111.5324 W), raised 13.48 m. A 500 m west-east
transect through it gives both figures:

  ws-pit-fill-concept.svg       before and after Fill, as two drawn profiles of the real transect
  ws-pit-fill-profile-map.jpg   the transect as a chart (original vs filled) beside an ArcGIS Pro map
                                of every cell Fill raised in the whole DEM

Needs C:\\Ames\\Lab05\\Check.gdb (DEM_UTM, Filled_DEM, Hillshade, Rock_Canyon_Basin) from
tools/lab05/run_model.py and build_figures.py. Run with the ArcGIS Pro Python.
"""
import importlib.util
import os
import pathlib

import arcpy
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
IMG = HERE.parent / "slides" / "week-06" / "images"
GDB = r"C:\Ames\Lab05\Check.gdb"
W6 = r"C:\Ames\Week06\Week06.gdb"
UTM = arcpy.SpatialReference(26912)
PX, PY = 454727, 4456097          # deepest fill, from tools/lab05 check values
WEST, EAST = 25, 40               # cells west and east of the pit: a 660 m transect that reaches the spill
FONT = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"
NAVY, BLUE, BROWN, GRAY, SAND = "#002e5d", "#0062b8", "#8a5a2b", "#5b6770", "#e9d8b8"
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True


def transect():
    ll = arcpy.Point(PX - (WEST + 0.5) * 10, PY - 0.5 * 10)
    n = WEST + EAST + 1
    d = arcpy.RasterToNumPyArray(os.path.join(GDB, "DEM_UTM"), ll, n, 1)[0].astype(float)
    f = arcpy.RasterToNumPyArray(os.path.join(GDB, "Filled_DEM"), ll, n, 1)[0].astype(float)
    x = (np.arange(n) - WEST) * 10.0
    return x, d, f


def concept(x, d, f):
    W, H = 1100, 400
    pw, ph, top, pad = 500, 260, 70, 30
    lo, hi = d.min() - 5, d.max() + 5
    def path(ox, z):
        return " L".join(f"{ox + (xi - x[0]) / (x[-1] - x[0]) * pw:.1f},{top + ph - (zi - lo) / (hi - lo) * ph:.1f}" for xi, zi in zip(x, z))
    def py(z):
        return top + ph - (z - lo) / (hi - lo) * ph
    def px(ox, xi):
        return ox + (xi - x[0]) / (x[-1] - x[0]) * pw
    raised = np.where(f - d > 0.01)[0]
    spill = f[raised].max()
    o = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' aria-label='A pit in the Lab 5 DEM before and after Fill'>",
         f"<rect width='{W}' height='{H}' fill='white'/>",
         "<defs><marker id='a' viewBox='0 0 10 10' refX='8' refY='5' markerWidth='6' markerHeight='6' orient='auto'><path d='M0,0 L10,5 L0,10 z' fill='#0062b8'/></marker></defs>"]
    for k, (ox, title) in enumerate(((pad, "Before Fill: the pit is a sink"), (pad + pw + 2 * pad, f"After Fill: raised to its spill level, {spill:,.1f} m"))):
        ground = d if k == 0 else f
        o.append(f"<text x='{ox}' y='34' font-family='{FONT}' font-size='22' font-weight='bold' fill='{NAVY}'>{title}</text>")
        o.append(f"<path d='M{path(ox, ground)} L{ox + pw},{top + ph} L{ox},{top + ph} Z' fill='{SAND}' stroke='{BROWN}' stroke-width='3'/>")
        if k == 1:   # the filled wedge, over the original profile
            o.append(f"<path d='M{path(ox, d)}' fill='none' stroke='{BROWN}' stroke-width='1.5' stroke-dasharray='5 4'/>")
            seg = range(raised.min() - 1, raised.max() + 2)
            fill_poly = " L".join(f"{px(ox, x[i]):.1f},{py(f[i]):.1f}" for i in seg) + " L" + " L".join(f"{px(ox, x[i]):.1f},{py(d[i]):.1f}" for i in reversed(seg))
            o.append(f"<path d='M{fill_poly} Z' fill='#c9a46a' fill-opacity='0.75'/>")
            mid = raised[len(raised) // 2]
            o.append(f"<text x='{px(ox, x[mid]):.1f}' y='{py(spill) - 12:.1f}' text-anchor='middle' font-family='{FONT}' font-size='16' fill='{BROWN}'>filled cells</text>")
            # flow follows the filled surface: down the west slope, across the filled stretch, out over the spill
            path_pts = " L".join(f"{px(ox, x[i]):.1f},{py(f[i]) - 12:.1f}" for i in range(3, len(x) - 2))
            o.append(f"<path d='M{path_pts}' fill='none' stroke='{BLUE}' stroke-width='4' marker-end='url(#a)'/>")
            o.append(f"<text x='{px(ox, x[-1]):.1f}' y='{py(f[-18]) - 34:.1f}' text-anchor='end' font-family='{FONT}' font-size='16' fill='{BLUE}'>flow continues</text>")
        else:
            bot = WEST   # the pit cell itself
            path_pts = " L".join(f"{px(ox, x[i]):.1f},{py(d[i]) - 12:.1f}" for i in range(3, bot + 1))
            o.append(f"<path d='M{path_pts}' fill='none' stroke='{BLUE}' stroke-width='4' marker-end='url(#a)'/>")
            o.append(f"<text x='{px(ox, x[bot]):.1f}' y='{py(d[bot]) + 28:.1f}' text-anchor='middle' font-family='{FONT}' font-size='16' fill='{BLUE}'>flow stops here</text>")
        o.append(f"<text x='{ox}' y='{top + ph + 26}' font-family='{FONT}' font-size='14' fill='{GRAY}'>west</text>")
        o.append(f"<text x='{ox + pw}' y='{top + ph + 26}' text-anchor='end' font-family='{FONT}' font-size='14' fill='{GRAY}'>east · {x[-1] - x[0]:.0f} m</text>")
    o.append(f"<text x='{W - pad}' y='{H - 12}' text-anchor='end' font-family='{FONT}' font-size='13' fill='{GRAY}'>A real {x[-1] - x[0]:.0f} m west–east transect of the Lab 5 DEM (10 m cells) through the deepest pit Fill found: {d[WEST]:,.1f} m raised to {spill:,.1f} m.</text>")
    o.append("</svg>")
    (IMG / "ws-pit-fill-concept.svg").write_text("\n".join(o), encoding="utf-8")
    print("ws-pit-fill-concept.svg", round(d[WEST], 2), round(spill, 2), len(raised), "cells raised on the transect")


def chart(x, d, f):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = "Segoe UI"
    fig, ax = plt.subplots(figsize=(6.0, 4.4), dpi=150)
    ax.fill_between(x, d, f, where=f - d > 0.01, color="#c9a46a", alpha=0.8, label="raised by Fill", step=None)
    ax.plot(x, d, color="#8a5a2b", lw=2.2, label="original DEM")
    ax.plot(x, f, color="#0062b8", lw=1.6, ls="--", label="filled DEM")
    i = int(np.argmax(f - d))
    ax.annotate(f"{(f - d)[i]:.1f} m deep", xy=(x[i], (d[i] + f[i]) / 2), xytext=(x[i] + 70, d[i] + 2),
                fontsize=11, color="#002e5d", arrowprops=dict(arrowstyle="-", color="#002e5d"))
    ax.set_xlabel("Distance from the pit, west to east (m)")
    ax.set_ylabel("Elevation (m)")
    ax.legend(frameon=False, loc="lower left", fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(f"A {x[-1] - x[0]:.0f} m profile through the deepest pit", fontsize=13, color="#002e5d", loc="left")
    fig.tight_layout()
    out = IMG / "_pit_chart.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def fill_map():
    spec = importlib.util.spec_from_file_location("bf", HERE / "lab05" / "build_figures.py")
    bf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bf)
    bf.IMG = IMG
    depth = arcpy.sa.Minus(os.path.join(GDB, "Filled_DEM"), os.path.join(GDB, "DEM_UTM"))
    arcpy.sa.SetNull(depth < 0.01, depth).save(os.path.join(W6, "Fill_Depth"))
    arcpy.management.CreateFeatureclass(W6, "Pit_Transect", "POLYLINE", spatial_reference=UTM)
    with arcpy.da.InsertCursor(os.path.join(W6, "Pit_Transect"), ["SHAPE@"]) as c:
        c.insertRow([arcpy.Polyline(arcpy.Array([arcpy.Point(PX - WEST * 10, PY), arcpy.Point(PX + EAST * 10, PY)]), UTM)])
    p = arcpy.mp.ArcGISProject(r"C:\Ames\Week06\Week06_Figures.aprx")
    bf.p_global = p
    for mp in p.listMaps("FillDepth"):
        p.deleteItem(mp)
    for ly in p.listLayouts("Render _pit_map.jpg"):
        p.deleteItem(ly)
    m = bf.new_map(p, "FillDepth")
    bf.gray_raster(m, "Hillshade", "Hillshade")
    lyr = m.addDataFromPath(os.path.join(W6, "Fill_Depth")); lyr.name = "Raised by Fill (m)"
    sym = lyr.symbology
    sym.updateColorizer("RasterStretchColorizer")
    sym.colorizer.colorRamp = p.listColorRamps("Yellow to Red")[0]
    lyr.symbology = sym
    dd = lyr.getDefinition("V3")
    dd.colorizer.statsType = "GlobalStats"; dd.colorizer.useCustomStretchMinMax = True
    dd.colorizer.customStretchMin = 0; dd.colorizer.customStretchMax = 3
    lyr.setDefinition(dd)
    bf.poly_layer(m, "Rock_Canyon_Basin", "Basin", fill=bf.rgb(0, 0, 0, 0), outline=bf.rgb(0, 46, 93), width=2.0)
    t = m.addDataFromPath(os.path.join(W6, "Pit_Transect"))
    sym = t.symbology; sym.renderer.symbol.color = bf.rgb(0, 98, 184); sym.renderer.symbol.size = 3.5; t.symbology = sym
    e = arcpy.Describe(os.path.join(GDB, "Rock_Canyon_Basin")).extent
    bf.export_map(p, m, "_pit_map.jpg", arcpy.Extent(e.XMin - 300, e.YMin - 500, PX + 900, e.YMax + 300, spatial_reference=UTM), w_in=5.6)
    p.save()
    return IMG / "_pit_map.jpg"


def combine(ch, mp):
    a, b = Image.open(ch).convert("RGB"), Image.open(mp).convert("RGB")
    h = max(a.height, b.height)
    b = b.resize((int(b.width * a.height / b.height), a.height))
    pad = 30
    out = Image.new("RGB", (a.width + b.width + 3 * pad, a.height + 2 * pad + 80), "white")
    out.paste(a, (pad, pad)); out.paste(b, (2 * pad + a.width, pad))
    dr = ImageDraw.Draw(out)
    dr.rectangle([2 * pad + a.width, pad, 2 * pad + a.width + b.width - 1, pad + b.height - 1], outline=(150, 160, 170), width=2)
    f = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 24)
    dr.text((2 * pad + a.width, pad + b.height + 12), "Cells Fill raised (yellow to red, 0–3+ m)", fill=(0, 46, 93), font=f)
    dr.text((2 * pad + a.width, pad + b.height + 42), "Rock Canyon basin in navy; the transect in blue", fill=(91, 103, 112),
            font=ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22))
    out.save(IMG / "ws-pit-fill-profile-map.jpg", quality=90)
    os.remove(ch); os.remove(mp)
    print("ws-pit-fill-profile-map.jpg", out.size)


if __name__ == "__main__":
    x, d, f = transect()
    concept(x, d, f)
    combine(chart(x, d, f), fill_map())
