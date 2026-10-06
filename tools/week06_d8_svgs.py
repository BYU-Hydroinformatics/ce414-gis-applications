"""Week 6 Part A: two drawn figures for the flow-direction slides.

  ws-slope-window.svg   the 3 x 3 window (a to i) that ArcGIS Pro's Slope and Aspect tools read,
                        with the center cell e marked as unused: both use only the eight neighbors
  ws-d8-pour-point.svg  the D8 question for one cell: eight arrows out of the center cell, each
                        carrying the Esri code that would be written into that center cell

Diagrams, not data. The codes are the Esri Flow Direction encoding (1 east, then doubling clockwise
to 128 northeast). The equations sit on the slide itself as MathJax, not in the SVG.

Run with any Python 3:  python tools/week06_d8_svgs.py
"""
import math
from pathlib import Path

IMG = Path(__file__).resolve().parent.parent / "slides" / "week-06" / "images"
FONT = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"
NAVY, BLUE, ORANGE, GRAY, LIGHT, PALE = "#002e5d", "#0062b8", "#e07a1f", "#5b6770", "#dbe8f5", "#eef1f4"


def slope_window():
    S, X0, Y0 = 92, 30, 50
    W, H = X0 * 2 + 3 * S, Y0 + 3 * S + 56
    o = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' "
         "aria-label='A three by three window of cells labeled a to i, with the center cell e grayed out as unused'>",
         f"<rect width='{W}' height='{H}' fill='white'/>",
         "<defs><pattern id='h' width='10' height='10' patternUnits='userSpaceOnUse' patternTransform='rotate(45)'>"
         f"<line x1='0' y1='0' x2='0' y2='10' stroke='#c3cad1' stroke-width='3'/></pattern></defs>",
         f"<text x='{W / 2}' y='30' text-anchor='middle' font-family='{FONT}' font-size='19' font-weight='bold' fill='{NAVY}'>The 3 × 3 window</text>"]
    for r in range(3):
        for c in range(3):
            x, y = X0 + c * S, Y0 + r * S
            centre = r == c == 1
            o.append(f"<rect x='{x}' y='{y}' width='{S}' height='{S}' fill='{'url(#h)' if centre else LIGHT}' stroke='{NAVY}' stroke-width='2.5'/>")
            o.append(f"<text x='{x + S / 2}' y='{y + S / 2 + 13}' text-anchor='middle' font-family='Cambria Math, Georgia, serif' "
                     f"font-style='italic' font-size='38' fill='{GRAY if centre else NAVY}'>{'abcdefghi'[r * 3 + c]}</text>")
    o.append(f"<text x='{W / 2}' y='{Y0 + 3 * S + 30}' text-anchor='middle' font-family='{FONT}' font-size='17' fill='{GRAY}'>"
             "the center cell <tspan font-style='italic'>e</tspan> is never used</text>")
    o.append("</svg>")
    (IMG / "ws-slope-window.svg").write_text("\n".join(o), encoding="utf-8")


def pour_point():
    W, H = 640, 560
    cx, cy, half, reach, rb = W / 2, 300, 52, 200, 32
    dirs = [(0, 1, "E"), (45, 2, "SE"), (90, 4, "S"), (135, 8, "SW"),
            (180, 16, "W"), (225, 32, "NW"), (270, 64, "N"), (315, 128, "NE")]   # angle clockwise from east
    o = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' "
         "aria-label='One cell with a question mark, and eight arrows leaving it, each labeled with the Esri flow direction code for that neighbor'>",
         f"<rect width='{W}' height='{H}' fill='white'/>",
         f"<defs><marker id='ah' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='5' markerHeight='5' orient='auto'>"
         f"<path d='M0,0 L10,5 L0,10 z' fill='{BLUE}'/></marker></defs>",
         f"<text x='{cx}' y='34' text-anchor='middle' font-family='{FONT}' font-size='24' font-weight='bold' fill='{NAVY}'>What is the flow direction here?</text>"]
    for ang, code, compass in dirs:
        a = math.radians(ang)
        ux, uy = math.cos(a), math.sin(a)
        # start at the edge of the center square, stop short of the badge
        k = half / max(abs(ux), abs(uy))
        x1, y1 = cx + ux * (k + 6), cy + uy * (k + 6)
        x2, y2 = cx + ux * (reach - rb - 6), cy + uy * (reach - rb - 6)
        bx, by = cx + ux * reach, cy + uy * reach
        o.append(f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='{BLUE}' stroke-width='5' marker-end='url(#ah)'/>")
        o.append(f"<circle cx='{bx:.1f}' cy='{by:.1f}' r='{rb}' fill='white' stroke='{ORANGE}' stroke-width='3.5'/>")
        o.append(f"<text x='{bx:.1f}' y='{by + 9:.1f}' text-anchor='middle' font-family='{FONT}' font-size='{26 if code < 100 else 22}' "
                 f"font-weight='bold' fill='{NAVY}'>{code}</text>")
        # compass letter just outside the badge, along the same ray
        lx, ly = cx + ux * (reach + rb + 16), cy + uy * (reach + rb + 16)
        o.append(f"<text x='{lx:.1f}' y='{ly + 6:.1f}' text-anchor='middle' font-family='{FONT}' font-size='16' fill='{GRAY}'>{compass}</text>")
    o.append(f"<rect x='{cx - half}' y='{cy - half}' width='{2 * half}' height='{2 * half}' rx='6' fill='{LIGHT}' stroke='{NAVY}' stroke-width='3'/>")
    o.append(f"<text x='{cx}' y='{cy + 24}' text-anchor='middle' font-family='{FONT}' font-size='68' font-weight='bold' fill='{ORANGE}'>?</text>")
    o.append("</svg>")
    (IMG / "ws-d8-pour-point.svg").write_text("\n".join(o), encoding="utf-8")


if __name__ == "__main__":
    slope_window()
    pour_point()
    print("wrote ws-slope-window.svg, ws-d8-pour-point.svg")
