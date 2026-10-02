"""Week 7 (Lake Bathymetry) figures, all from published data. Nothing is invented.

Sources, fetched into DATA (default: the session scratch folder; pass --data DIR):
  gsl_dv.rdb        USGS NWIS daily lake elevation, gage 10010000 (Great Salt Lake at Saltair Boat
                    Harbor), parameter 62614, ft NGVD29, 1847 to today:
                    https://waterservices.usgs.gov/nwis/dv/?format=rdb&sites=10010000&parameterCd=62614&startDT=1847-01-01&statCd=00003
  eav_total.csv     USGS elevation-area-volume table for the whole lake, Root (2023),
                    https://doi.org/10.5066/P9DGG75W (ScienceBase child 6467b42fd34ec11ae4a8afb1)
  hm/hydromap/data/extent/gsl-extent-NNNN.geojson
                    shorelines at whole-foot levels (ft NGVD29) baked from the same USGS DEM by
                    github.com/danames/hydromap-app (commit 70c0d84); each carries source = the DOI
  hm/hydromap/data/crosssections/gsl-causeway.json
                    a south-arm cross-section from the Tarboton & Merck HydroShare DEM (a different,
                    older DEM; labeled as such)

Outputs into slides/week-07/images/ (lb-*). Run with the ArcGIS Pro Python (matplotlib, arcpy):
    "C:/Program Files/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe" tools/week07_figures.py [name ...]
"""
import csv
import importlib.util
import json
import os
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
IMG = HERE.parent / "slides" / "week-07" / "images"
IMG.mkdir(parents=True, exist_ok=True)
DATA = pathlib.Path(os.environ.get("GSL_DATA", r"C:\Users\dpame\AppData\Local\Temp\claude\C--Users-dpame-code-ce414-gis-applications--claude-worktrees-zen-sanderson-76aa2f\6a1816a3-d8b2-4560-a0c3-e38887d67f2c\scratchpad\gsl-research"))
EXT = DATA / "hm" / "hydromap" / "data" / "extent"
NAVY, BLUE, ORANGE, GRAY, RED, SAND = "#002e5d", "#0062b8", "#e07a1f", "#5b6770", "#b3261e", "#e9d8b8"
plt.rcParams.update({"font.family": "Segoe UI", "font.size": 13, "axes.spines.top": False, "axes.spines.right": False})
LEVELS = [4210, 4205, 4200, 4195, 4190]


def gage():
    rows = [l.rstrip("\n").split("\t") for l in open(DATA / "gsl_dv.rdb", encoding="utf-8") if l.startswith("USGS")]
    import datetime as dt
    return [(dt.date.fromisoformat(r[2]), float(r[3])) for r in rows if r[3]]


def eav():
    return [(float(r["elev_ft_NGVD29"]), float(r["area_mi2"]), float(r["volume_acreft"]))
            for r in csv.DictReader(open(DATA / "eav_total.csv", encoding="utf-8"))]


def history():
    v = gage()
    hi = max(v, key=lambda t: t[1]); lo = min(v, key=lambda t: t[1]); now = v[-1]
    hi86 = max((t for t in v if t[0].year >= 1980), key=lambda t: t[1])
    fig, ax = plt.subplots(figsize=(11, 4.6), dpi=150)
    ax.plot([t[0] for t in v], [t[1] for t in v], color=BLUE, lw=1.2)
    for (d, z), lab, off in ((hi, f"{hi[1]:,.1f} ft, {hi[0].year}", (10, -4)), (hi86, f"{hi86[1]:,.1f} ft, {hi86[0].year}", (-150, -4)),
                             (lo, f"record low {lo[1]:,.1f} ft, {lo[0]:%b %Y}", (-260, -6)), (now, f"{now[0]:%b %d, %Y}: {now[1]:,.1f} ft", (-200, 20))):
        ax.plot([d], [z], "o", color=RED if "low" in lab else NAVY, ms=7)
        ax.annotate(lab, (d, z), textcoords="offset points", xytext=off, fontsize=12, color=NAVY)
    ax.set_ylabel("Lake elevation (ft, NGVD29)")
    ax.set_title("Great Salt Lake at Saltair, USGS gage 10010000, 1847–2026", loc="left", color=NAVY, fontsize=15)
    ax.grid(axis="y", color="#e5e8eb")
    fig.tight_layout(); fig.savefig(IMG / "lb-level-history.png"); plt.close(fig)
    print("lb-level-history.png", hi, hi86, lo, now)


def curve():
    e = [r for r in eav() if r[1] > 0]
    z = [r[0] for r in e]; a = [r[1] for r in e]; vol = [r[2] / 1e6 for r in e]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6), dpi=150)
    ax1.plot(a, z, color=BLUE, lw=2.4); ax1.set_xlabel("Lake area (sq mi)"); ax1.set_ylabel("Water-surface elevation (ft, NGVD29)")
    ax2.plot(vol, z, color=NAVY, lw=2.4); ax2.set_xlabel("Lake volume (million acre-ft)")
    for ax in (ax1, ax2):
        ax.axhline(4188.5, color=RED, lw=1, ls="--"); ax.grid(color="#e5e8eb")
    ax1.text(a[-1] * 0.02, 4188.9, "2022 record low, 4,188.5 ft", color=RED, fontsize=11)
    ax1.set_title("Area", loc="left", color=NAVY); ax2.set_title("Volume", loc="left", color=NAVY)
    fig.suptitle("Elevation–area–volume curves, USGS (Root, 2023)", x=0.01, ha="left", color=NAVY, fontsize=15)
    fig.tight_layout(); fig.savefig(IMG / "lb-eav-curves.png"); plt.close(fig)
    # area added per foot of rise
    per = []
    for lo in range(4171, 4211):
        al = min(e, key=lambda r: abs(r[0] - lo)); ah = min(e, key=lambda r: abs(r[0] - (lo + 1)))
        per.append((lo + 0.5, ah[1] - al[1]))
    fig, ax = plt.subplots(figsize=(11, 4.4), dpi=150)
    ax.bar([p[0] for p in per], [p[1] for p in per], width=0.85, color=BLUE)
    ax.set_xlabel("Water-surface elevation (ft, NGVD29)"); ax.set_ylabel("Area gained per foot (sq mi)")
    ax.set_title("How much lakebed one foot of water covers, by level", loc="left", color=NAVY, fontsize=15)
    ax.axvline(4188.5, color=RED, lw=1, ls="--"); ax.grid(axis="y", color="#e5e8eb")
    fig.tight_layout(); fig.savefig(IMG / "lb-area-per-foot.png"); plt.close(fig)
    big = max(per, key=lambda p: p[1])
    print("lb-eav-curves.png, lb-area-per-foot.png; biggest step", big, "at 4188.5-4189.5:", [p for p in per if p[0] == 4188.5 or p[0] == 4189.5])


def causeway():
    j = json.loads((DATA / "hm" / "hydromap" / "data" / "crosssections" / "gsl-causeway.json").read_text(encoding="utf-8"))
    x, z = j["distance_mi"], j["bottom_ft"]
    print("causeway source:", j.get("source"), j.get("datum"), j.get("unit"))
    fig, ax = plt.subplots(figsize=(11, 4.0), dpi=150)
    ax.fill_between(x, z, min(z) - 3, color=SAND, edgecolor="#8a5a2b", lw=1.5)
    for lev, col, lab in ((4211.6, NAVY, "record high, 4,211.6 ft"), (4189.7, BLUE, "Sept 30, 2026: 4,189.7 ft"), (4188.5, RED, "record low, 4,188.5 ft")):
        ax.axhline(lev, color=col, lw=1.4, ls="-" if col == BLUE else "--")
        if col == BLUE:
            ax.text(x[0] + 0.3, lev + 0.5, lab, ha="left", color=col, fontsize=11)
        elif col == RED:
            ax.text(x[-1] - 0.3, lev - 1.6, lab, ha="right", va="top", color=col, fontsize=11)
        else:
            ax.text(x[-1] - 0.3, lev + 0.5, lab, ha="right", color=col, fontsize=11)
    ax.set_xlabel("Distance west to east (mi)"); ax.set_ylabel("Elevation (ft, NGVD29)")
    ax.set_ylim(min(z) - 3, 4215)
    ax.set_title("South arm cross-section, about 2 km south of the railroad causeway", loc="left", color=NAVY, fontsize=15)
    fig.tight_layout(); fig.savefig(IMG / "lb-cross-section.png"); plt.close(fig)
    print("lb-cross-section.png", min(z), max(z), len(x))


def shorelines():
    import arcpy
    spec = importlib.util.spec_from_file_location("bf", HERE / "lab05" / "build_figures.py")
    bf = importlib.util.module_from_spec(spec); spec.loader.exec_module(bf)
    bf.IMG = IMG
    gdb = r"C:\Ames\Week07\Week07.gdb"
    os.makedirs(r"C:\Ames\Week07", exist_ok=True)
    if not arcpy.Exists(gdb):
        arcpy.management.CreateFileGDB(r"C:\Ames\Week07", "Week07.gdb")
    utm = arcpy.SpatialReference(26912)
    for lev in sorted(set(LEVELS + list(range(4190, 4212, 2)))):
        out = os.path.join(gdb, f"Shore_{lev}")
        if not arcpy.Exists(out):
            arcpy.conversion.JSONToFeatures(str(EXT / f"gsl-extent-{lev}.geojson"), out + "_gcs", "POLYGON")
            arcpy.management.Project(out + "_gcs", out, utm)
            arcpy.management.Delete(out + "_gcs")
    apr = r"C:\Ames\Week07\Week07_Figures.aprx"
    if os.path.exists(apr):
        os.remove(apr)
    p = arcpy.mp.ArcGISProject(bf.BLANK); p.saveACopy(apr); p = arcpy.mp.ArcGISProject(apr)
    for x in p.listLayouts() + p.listMaps():
        p.deleteItem(x)
    bf.p_global = p
    ramp = {4210: (198, 219, 239), 4205: (158, 202, 225), 4200: (107, 174, 214), 4195: (49, 130, 189), 4190: (8, 81, 156)}
    m = bf.new_map(p, "Nested", "Imagery")
    for lev in LEVELS:
        lyr = m.addDataFromPath(os.path.join(gdb, f"Shore_{lev}")); lyr.name = f"{lev:,} ft"
        sym = lyr.symbology; s = sym.renderer.symbol; s.color = bf.rgb(*ramp[lev], 100); s.outlineColor = bf.rgb(255, 255, 255, 60); s.outlineWidth = 0.4; lyr.symbology = sym
    e = arcpy.Describe(os.path.join(gdb, "Shore_4210")).extent
    ext = arcpy.Extent(e.XMin - 4000, e.YMin - 4000, e.XMax + 4000, e.YMax + 4000, spatial_reference=utm)
    lay = p.createLayout(8.0, 8.0 * ext.height / ext.width + 1.2, "INCH", "Nested layout")
    h = 8.0 * ext.height / ext.width
    mf = lay.createMapFrame(bf.poly(0, 1.2, 8.0, 1.2 + h), m, "Main"); mf.camera.setExtent(ext)
    style = (p.listStyleItems("ArcGIS 2D", "LEGEND", "Legend 1") or [None])[0]
    leg = lay.createMapSurroundElement(bf.poly(0.1, 0.05, 7.9, 1.15), "LEGEND", mf, style, "Legend")
    for it in leg.items:
        if any(k in it.name for k in ("Imagery", "World", "Reference")):
            leg.removeItem(it)
    leg.title = "Shoreline at water-surface elevation (ft, NGVD29)"
    try:
        d = leg.getDefinition("V3"); d.fittingStrategy = "AdjustColumnsAndFont"
        for it in d.items:
            it.showHeading = False
        leg.setDefinition(d)
    except Exception as ex:
        print("legend:", ex)
    lay.exportToJPEG(str(IMG / "lb-shorelines-nested.jpg"), resolution=150, jpeg_quality=90)
    print("lb-shorelines-nested.jpg")
    # stepped GIF: the lake falling from 4,210 to 4,190 ft in 2 ft steps
    frames = []
    font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 46)
    for lev in range(4210, 4188, -2):
        mm = bf.new_map(p, f"G{lev}", "Imagery")
        lyr = mm.addDataFromPath(os.path.join(gdb, f"Shore_{lev}"))
        sym = lyr.symbology; s = sym.renderer.symbol; s.color = bf.rgb(30, 110, 200, 100); s.outlineColor = bf.rgb(255, 255, 255); s.outlineWidth = 0.6; lyr.symbology = sym
        lay2, _ = None, None
        bf.export_map(p, mm, f"_g{lev}.jpg", ext, w_in=6.0, dpi=110)
        im = Image.open(IMG / f"_g{lev}.jpg").convert("RGB")
        a = next(arcpy.da.SearchCursor(os.path.join(gdb, f"Shore_{lev}"), ["area_sq_mi"]))[0] if "area_sq_mi" in [f.name for f in arcpy.ListFields(os.path.join(gdb, f"Shore_{lev}"))] else None
        d = ImageDraw.Draw(im)
        txt = f"{lev:,} ft" + (f"   {a:,.0f} sq mi" if a else "")
        d.rectangle([12, 12, 30 + d.textlength(txt, font=font), 78], fill=(0, 46, 93))
        d.text((22, 14), txt, font=font, fill="white")
        frames.append(im); os.remove(IMG / f"_g{lev}.jpg")
    frames[0].save(IMG / "lb-shoreline-falling.gif", save_all=True, append_images=frames[1:], duration=[1400] * (len(frames) - 1) + [2600], loop=0, optimize=True)
    print("lb-shoreline-falling.gif", len(frames), "frames")
    p.save()


ALL = dict(history=history, curve=curve, causeway=causeway, shorelines=shorelines)
if __name__ == "__main__":
    for n in sys.argv[1:] or list(ALL):
        ALL[n]()


def crop_map():
    """A legend-free copy of the nested map for background slides (the legend is the bottom 1.2 in)."""
    im = Image.open(IMG / "lb-shorelines-nested.jpg")
    im.crop((0, 0, im.width, im.height - 180)).save(IMG / "lb-shorelines-nested-map.jpg", quality=90)
