"""Week 6 (Thursday): what a watershed does, drawn three times on the real Rock Canyon basin.

Writes slides/week-06/images/ws-watershed-functions.svg. Three panels, one per budget the watershed
is the accounting boundary for: water, sediment and chemistry, and habitat. The basin outline and the
streams are Lab 5's (C:\\Ames\\Lab05\\Check.gdb: Rock_Canyon_Basin, Streams_5000); in the middle panel each
stream link's width is drawn from its real contributing area (Flow_Accumulation 90 % of the way down
the link), so the channel visibly carries more toward the outlet. No other numbers are shown.

    "C:/Program Files/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe" tools/week06_processes_svg.py
"""
import math
import pathlib

import arcpy

ROOT = pathlib.Path(__file__).resolve().parent.parent
GDB = r"C:\Ames\Lab05\Check.gdb"
OUT = ROOT / "slides" / "week-06" / "images" / "ws-watershed-functions.svg"
FONT = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"
NAVY, BLUE, ORANGE, GREEN, BROWN, GRAY = "#002e5d", "#0062b8", "#e07a1f", "#3c8d3a", "#8a5a2b", "#5b6770"

with arcpy.da.SearchCursor(GDB + r"\Rock_Canyon_Basin", ["SHAPE@"]) as c:
    basin = max((list(p) for p in next(c)[0].generalize(30)), key=len)
streams = []
fa = arcpy.Raster(GDB + r"\Flow_Accumulation")
with arcpy.da.SearchCursor(GDB + r"\Streams_5000", ["SHAPE@"]) as c:
    for (g,) in c:
        g2 = g.generalize(15)
        pts = [(p.X, p.Y) for part in g2 for p in part if p]
        end = g.positionAlongLine(0.9, True).firstPoint   # inside the link, not on the junction cell
        v = arcpy.management.GetCellValue(GDB + r"\Flow_Accumulation", f"{end.X} {end.Y}").getOutput(0)
        try:
            acc = float(v)
        except ValueError:
            acc = 5000.0
        streams.append((pts, acc))
bx = [p.X for p in basin if p]; by = [p.Y for p in basin if p]
x0, x1, y0, y1 = min(bx), max(bx), min(by), max(by)
PW, TOP, GAP = 320, 130, 70
s = PW / (x1 - x0)
PH = (y1 - y0) * s
W, H = 3 * PW + 2 * GAP + 80, int(TOP + PH + 120)
out_x, out_y = min(((p.X, p.Y) for p in basin if p), key=lambda t: t[0])


def P(ox, x, y):
    return ox + (x - x0) * s, TOP + (y1 - y) * s


def outline(ox):
    return "M" + " L".join("%.1f,%.1f" % P(ox, p.X, p.Y) for p in basin if p) + " Z"


def line(ox, pts):
    return "M" + " L".join("%.1f,%.1f" % P(ox, x, y) for x, y in pts)


o = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' "
     "aria-label='Three things a watershed does, drawn on the Rock Canyon basin'>",
     f"<rect width='{W}' height='{H}' fill='white'/>",
     "<defs>" + "".join(f"<marker id='m{n}' viewBox='0 0 10 10' refX='8' refY='5' markerWidth='5' markerHeight='5' orient='auto'>"
                        f"<path d='M0,0 L10,5 L0,10 z' fill='{c}'/></marker>" for n, c in (("b", BLUE), ("r", BROWN), ("o", ORANGE))) + "</defs>"]
panels = [("Water", ["collects, stores and", "releases water"], BLUE),
          ("Sediment and chemistry", ["carries what washes off", "the slopes downstream"], BROWN),
          ("Habitat", ["streams and their banks", "are corridors for life"], GREEN)]
amax = max(a for _, a in streams)
for k, (title, sub, color) in enumerate(panels):
    ox = 40 + k * (PW + GAP)
    o.append(f"<text x='{ox}' y='40' font-family='{FONT}' font-size='26' font-weight='bold' fill='{color}'>{title}</text>")
    for j, ln in enumerate(sub):
        o.append(f"<text x='{ox}' y='{68 + 22 * j}' font-family='{FONT}' font-size='18' fill='{GRAY}'>{ln}</text>")
    fill = {0: "#e3eef8", 1: "#f3eadb", 2: "#eef5e9"}[k]
    o.append(f"<path d='{outline(ox)}' fill='{fill}' stroke='{NAVY}' stroke-width='2.5' stroke-linejoin='round'/>")
    if k == 2:   # riparian corridor under every stream
        for pts, _ in streams:
            o.append(f"<path d='{line(ox, pts)}' fill='none' stroke='{GREEN}' stroke-opacity='0.35' stroke-width='16' stroke-linecap='round' stroke-linejoin='round'/>")
    for pts, acc in streams:
        w = 1.5 + 6.5 * math.log(max(acc, 5000.0) / 5000.0) / math.log(amax / 5000.0) if k == 1 else 2.2
        col = BROWN if k == 1 else BLUE
        o.append(f"<path d='{line(ox, pts)}' fill='none' stroke='{col}' stroke-width='{w:.2f}' stroke-linecap='round' stroke-linejoin='round'/>")
    ox_, oy_ = P(ox, out_x, out_y)
    o.append(f"<circle cx='{ox_:.1f}' cy='{oy_:.1f}' r='6' fill='#b3261e' stroke='white' stroke-width='2'/>")
    if k == 0:
        for fx in (0.35, 0.6, 0.85):
            o.append(f"<line x1='{ox + PW * fx:.1f}' y1='{TOP - 18}' x2='{ox + PW * fx:.1f}' y2='{TOP + PH * 0.25:.1f}' stroke='{BLUE}' stroke-width='3' marker-end='url(#mb)'/>")
        o.append(f"<line x1='{ox_ - 4:.1f}' y1='{oy_:.1f}' x2='{ox_ - 34:.1f}' y2='{oy_:.1f}' stroke='{BLUE}' stroke-width='4' marker-end='url(#mb)'/>")
    if k == 1:
        o.append(f"<line x1='{ox_ - 4:.1f}' y1='{oy_:.1f}' x2='{ox_ - 34:.1f}' y2='{oy_:.1f}' stroke='{BROWN}' stroke-width='4' marker-end='url(#mr)'/>")
    foot = {0: ["Rain and snow in;", "streamflow out at the outlet"],
            1: ["Line width grows with the", "area draining to each link"],
            2: ["The stream network is", "the habitat network"]}[k]
    for j, ln in enumerate(foot):
        o.append(f"<text x='{ox}' y='{TOP + PH + 34 + 22 * j:.0f}' font-family='{FONT}' font-size='18' fill='{NAVY}'>{ln}</text>")
o.append(f"<text x='{W - 40}' y='{H - 16}' text-anchor='end' font-family='{FONT}' font-size='14' fill='{GRAY}'>"
         "Rock Canyon above the trailhead (Lab 5): basin, outlet (red) and the 29 stream links at 5,000 cells.</text>")
o.append("</svg>")
OUT.write_text("\n".join(o), encoding="utf-8")
print("wrote", OUT, len(streams), "links, max contributing cells", int(amax))
