"""Week 6: one cell of the Lab 5 DEM, its aspect and its D8 direction side by side.

Writes slides/week-06/images/ws-aspect-vs-d8.svg. The numbers are not invented: the nine
elevations are tools/lab05/d8_patch.json (the filled Rock Canyon DEM, Lab 5 Figure B, rows 0-2 and
columns 0-2), and the aspect and slope of the center cell were read from ArcGIS Pro 3.7.1's Aspect
and Slope tools run on that filled DEM on 2026-09-30 (aspect 250.3 degrees, slope 57.8 degrees).
Flow Direction gave the center cell code 8 (southwest), the same value as in d8_patch.json.

Run with any Python 3:  python tools/week06_aspect_d8_svg.py
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
patch = json.loads((ROOT / "tools" / "lab05" / "d8_patch.json").read_text())
z = [[round(v, 1) for v in row[:3]] for row in patch["elev"][:3]]
assert patch["fd"][1][1] == 8
ASPECT = 250.3          # ArcGIS Pro Aspect, center cell
CELL = 10.0             # m

# D8 by hand, to print on the figure: drop / distance to each neighbor
c = z[1][1]
best = None
for dr in (-1, 0, 1):
    for dc in (-1, 0, 1):
        if dr == dc == 0:
            continue
        d = CELL * (math.sqrt(2) if dr and dc else 1)
        s = (c - z[1 + dr][1 + dc]) / d
        if best is None or s > best[0]:
            best = (s, dr, dc, c - z[1 + dr][1 + dc], d)
assert (best[1], best[2]) == (1, -1)       # southwest
drop, dist = best[3], best[4]

FONT = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"
NAVY, ORANGE, BLUE, GRAY = "#002e5d", "#e07a1f", "#1f6fb2", "#5b6770"
W, H = 980, 470
S = 120                 # cell size in px
GX, GY = 40, 60         # grid origin
cx, cy = GX + 1.5 * S, GY + 1.5 * S

out = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' "
       f"role='img' aria-label='Aspect and D8 direction of one cell of the Lab 5 DEM'>",
       f"<rect width='{W}' height='{H}' fill='white'/>",
       "<defs>"
       f"<marker id='ao' viewBox='0 0 10 10' refX='8' refY='5' markerWidth='6' markerHeight='6' orient='auto'><path d='M0,0 L10,5 L0,10 z' fill='{ORANGE}'/></marker>"
       f"<marker id='ab' viewBox='0 0 10 10' refX='8' refY='5' markerWidth='6' markerHeight='6' orient='auto'><path d='M0,0 L10,5 L0,10 z' fill='{BLUE}'/></marker>"
       "</defs>",
       f"<text x='{GX}' y='34' font-family='{FONT}' font-size='18' font-weight='bold' fill='{NAVY}'>"
       "Nine cells of the Rock Canyon DEM (elevation in m, 10 m cells)</text>"]
for r in range(3):
    for col in range(3):
        x, y = GX + col * S, GY + r * S
        fill = "#fff4e0" if (r, col) == (1, 1) else ("#e3eef8" if (r, col) == (2, 0) else "#f7f8f9")
        out.append(f"<rect x='{x}' y='{y}' width='{S}' height='{S}' fill='{fill}' stroke='#9aa5ae' stroke-width='1.5'/>")
        out.append(f"<text x='{x + S / 2}' y='{y + 26}' text-anchor='middle' font-family='{FONT}' "
                   f"font-size='17' fill='{NAVY}'>{z[r][col]:,.1f}</text>")
# aspect arrow: azimuth clockwise from north
L = 1.0 * S
a = math.radians(ASPECT)
ax, ay = cx + L * math.sin(a), cy - L * math.cos(a)
out.append(f"<line x1='{cx}' y1='{cy}' x2='{ax:.1f}' y2='{ay:.1f}' stroke='{ORANGE}' stroke-width='5' marker-end='url(#ao)'/>")
# D8 arrow to the southwest cell center
bx, by = GX + 0.62 * S, GY + 2.62 * S
out.append(f"<line x1='{cx}' y1='{cy}' x2='{bx:.1f}' y2='{by:.1f}' stroke='{BLUE}' stroke-width='5' marker-end='url(#ab)'/>")
out.append(f"<circle cx='{cx}' cy='{cy}' r='6' fill='{NAVY}'/>")

TX = GX + 3 * S + 50
lines = [
    (ORANGE, "Aspect: 250°", "ArcGIS Pro's Aspect tool fits one plane to the 3 × 3 window"),
    (None, "", "and reports the compass direction it faces downhill — any angle"),
    (None, "", "from 0° to 360°. Here, west-southwest: closer to west than southwest."),
    (BLUE, "D8 flow direction: 8 (southwest, 225°)", "Flow Direction looks at the eight neighbors one at a time and"),
    (None, "", f"keeps the steepest single drop: {drop:.1f} m over {dist:.1f} m on the diagonal."),
    (None, "", "Only eight answers are possible, so all the water goes southwest."),
]
y = GY + 30
for color, head, body in lines:
    if head:
        y += 26
        out.append(f"<rect x='{TX}' y='{y - 15}' width='18' height='18' fill='{color}'/>")
        out.append(f"<text x='{TX + 28}' y='{y}' font-family='{FONT}' font-size='19' font-weight='bold' fill='{NAVY}'>{head}</text>")
        y += 28
    out.append(f"<text x='{TX}' y='{y}' font-family='{FONT}' font-size='16' fill='{GRAY}'>{body}</text>")
    y += 24
out.append(f"<text x='{TX}' y='{GY + 3 * S}' font-family='{FONT}' font-size='15' font-style='italic' fill='{GRAY}'>"
           "Same cell, same question — which way is downhill? — two different answers.</text>")
out.append("</svg>")

dest = ROOT / "slides" / "week-06" / "images" / "ws-aspect-vs-d8.svg"
dest.write_text("\n".join(out), encoding="utf-8")
print("wrote", dest, f"(drop {drop:.2f} m over {dist:.2f} m, slope {best[0]:.3f})")
