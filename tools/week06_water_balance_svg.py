"""Week 6 (Thursday): the water balance of one watershed, drawn on the real Rock Canyon basin.

Writes slides/week-06/images/ws-water-balance.svg. The basin outline is Lab 5's Rock_Canyon_Basin
(C:\\Ames\\Lab05\\Check.gdb, from tools/lab05/run_model.py), simplified to 30 m; the arrows and the
equation are the textbook watershed water balance, not measured values — no numbers are shown.

    "C:/Program Files/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe" tools/week06_water_balance_svg.py
"""
import pathlib

import arcpy

ROOT = pathlib.Path(__file__).resolve().parent.parent
FC = r"C:\Ames\Lab05\Check.gdb\Rock_Canyon_Basin"
OUT = ROOT / "slides" / "week-06" / "images" / "ws-water-balance.svg"
FONT = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"
NAVY, BLUE, ORANGE, GREEN, BROWN, GRAY = "#002e5d", "#0062b8", "#e07a1f", "#4c8c3a", "#8a5a2b", "#5b6770"

with arcpy.da.SearchCursor(FC, ["SHAPE@"]) as cur:
    geom = next(cur)[0].generalize(30)
part = max((list(p) for p in geom), key=len)
pts = [(pt.X, pt.Y) for pt in part if pt]
xs, ys = [p[0] for p in pts], [p[1] for p in pts]
x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
BX, BY, BW = 210, 120, 560                    # where the basin sits in the figure
s = BW / (x1 - x0)
BH = (y1 - y0) * s
path = "M" + " L".join(f"{BX + (x - x0) * s:.1f},{BY + (y1 - y) * s:.1f}" for x, y in pts) + " Z"
# the outlet is the westernmost vertex (the trailhead)
ox, oy = min(pts, key=lambda p: p[0])
OX, OY = BX + (ox - x0) * s, BY + (y1 - oy) * s

W, H = 1000, 640
o = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' "
     f"aria-label='The water balance of the Rock Canyon watershed'>",
     f"<rect width='{W}' height='{H}' fill='white'/>",
     "<defs>" + "".join(
         f"<marker id='m{n}' viewBox='0 0 10 10' refX='8' refY='5' markerWidth='5' markerHeight='5' orient='auto'>"
         f"<path d='M0,0 L10,5 L0,10 z' fill='{c}'/></marker>" for n, c in
         (("b", BLUE), ("o", ORANGE), ("n", NAVY), ("r", BROWN))) + "</defs>",
     f"<path d='{path}' fill='#e3eef8' stroke='{NAVY}' stroke-width='3' stroke-linejoin='round'/>",
     f"<text x='{BX + BW * 0.55}' y='{BY + BH * 0.52}' text-anchor='middle' font-family='{FONT}' font-size='34' "
     f"font-weight='bold' fill='{NAVY}'>ΔS</text>",
     f"<text x='{BX + BW * 0.55}' y='{BY + BH * 0.52 + 24}' text-anchor='middle' font-family='{FONT}' font-size='19' "
     f"fill='{GRAY}'>change in storage: snow, soil water, groundwater</text>"]


def arrow(x1_, y1_, x2_, y2_, color, mk, label, sub, lx, ly, anchor="middle"):
    o.append(f"<line x1='{x1_}' y1='{y1_}' x2='{x2_}' y2='{y2_}' stroke='{color}' stroke-width='6' marker-end='url(#{mk})'/>")
    o.append(f"<text x='{lx}' y='{ly}' text-anchor='{anchor}' font-family='{FONT}' font-size='32' font-weight='bold' fill='{color}'>{label}</text>")
    o.append(f"<text x='{lx}' y='{ly + 26}' text-anchor='{anchor}' font-family='{FONT}' font-size='20' fill='{GRAY}'>{sub}</text>")


arrow(BX + BW * 0.35, 20, BX + BW * 0.35, BY + BH * 0.25, BLUE, "mb", "P", "precipitation (rain, snow)", BX + BW * 0.35 - 18, 50, "end")
arrow(BX + BW * 0.78, BY + BH * 0.3, BX + BW * 0.78, 20, ORANGE, "mo", "ET", "evapotranspiration", BX + BW * 0.78 + 18, 50, "start")
arrow(OX + 6, OY, 40, OY, BLUE, "mb", "Q", "streamflow at the outlet", 40, OY - 66, "start")
arrow(BX + BW * 0.45, BY + BH * 0.8, BX + BW * 0.45, BY + BH + 70, BROWN, "mr", "G", "deep groundwater leaving", BX + BW * 0.45 - 18, BY + BH + 50, "end")
o.append(f"<circle cx='{OX:.1f}' cy='{OY:.1f}' r='8' fill='#b3261e' stroke='white' stroke-width='2'/>")
o.append(f"<text x='{W - 30}' y='{H - 40}' text-anchor='end' font-family='{FONT}' font-size='30' font-weight='bold' fill='{NAVY}'>ΔS = P − ET − Q − G</text>")
o.append(f"<text x='{W - 30}' y='{H - 16}' text-anchor='end' font-family='{FONT}' font-size='14' fill='{GRAY}'>"
         "Basin outline: Rock Canyon above the trailhead (Lab 5). Arrows are the terms, not measurements.</text>")
o.append("</svg>")
OUT.write_text("\n".join(o), encoding="utf-8")
print("wrote", OUT, f"basin {len(pts)} vertices, outlet at {ox:.0f} {oy:.0f}")
