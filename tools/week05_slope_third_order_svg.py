"""Week 5 Terrain Analysis: the 3rd-order finite difference figure.

  ta-slope-third-order.svg  the nine elevations from the four-nearest-cells slide, beside the
                            dZ/dx and dZ/dy kernels, cells numbered Z0 (center) to Z8 as on
                            that slide. Drawn in the same style as ta-slope-four-nearest-diagram.svg.

Replaces a scanned figure whose dZ/dy formula was labeled "dZ/dx" and whose slope (22.9 degrees)
came from rounding dZ/dx and dZ/dy to two places first; unrounded it is 22.8 degrees. The
equations and the worked numbers sit on the slide as MathJax, not in the SVG.

Run with any Python 3:  python tools/week05_slope_third_order_svg.py
"""
import math
from pathlib import Path

IMG = Path(__file__).resolve().parent.parent / "slides" / "week-05" / "images"
NAVY, INK, GRAY, MUTED = "#002e5d", "#22262e", "#6b7280", "#a0a7b2"
BLUE, BLUE_BG, BLUE_BG2 = "#0062b8", "#e3eefa", "#c4dcf5"
ORANGE, ORANGE_BG, ORANGE_BG2 = "#c26a00", "#fbeedd", "#f5d6ac"

ELEV = [[42, 45, 47], [40, 44, 49], [44, 48, 52]]
ZNUM = [[1, 2, 3], [4, 0, 5], [6, 7, 8]]
KX = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
KY = [[1, 2, 1], [0, 0, 0], [-1, -2, -1]]
S, TOP = 92, 40


def num(v):
    return f"−{-v}" if v < 0 else str(v)


def grid(x0, title, values, style):
    o = [f'<text x="{x0 + 1.5 * S}" y="26" font-size="22" font-weight="700" fill="{NAVY}" text-anchor="middle">{title}</text>']
    for r in range(3):
        for c in range(3):
            x, y = x0 + c * S, TOP + r * S
            fill, colour, weight = style(r, c, values[r][c])
            o.append(f'<rect x="{x}" y="{y}" width="{S}" height="{S}" fill="{fill}" stroke="{INK}" stroke-width="2"/>')
            o.append(f'<text x="{x + 7}" y="{y + 20}" font-size="15" fill="{GRAY}">Z<tspan font-size="11" dy="4">{ZNUM[r][c]}</tspan></text>')
            o.append(f'<text x="{x + S / 2}" y="{y + 58}" font-size="32" font-weight="{weight}" fill="{colour}" '
                     f'text-anchor="middle">{num(values[r][c])}</text>')
    return o


def elev_style(r, c, v):
    return ("#ffffff", MUTED, 400) if r == c == 1 else ("#ffffff", INK, 700)


def kernel_style(colour, bg, bg2):
    def style(r, c, v):
        if v == 0:
            return "#ffffff", MUTED, 400
        return (bg2 if abs(v) == 2 else bg), colour, 700
    return style


def main():
    W, H = 1060, 346
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         'font-family="Helvetica,Arial,sans-serif" role="img" aria-label="Nine elevations numbered Z0 to Z8, '
         'beside the third-order finite difference kernels for dZ/dx and dZ/dy">']
    o += grid(0, "Elevations (m)", ELEV, elev_style)
    o.append(f'<text x="{1.5 * S}" y="342" font-size="18" text-anchor="middle" fill="{INK}">cell size C = 10 m</text>')
    o += grid(380, "Kernel for dZ/dx", KX, kernel_style(BLUE, BLUE_BG, BLUE_BG2))
    o += grid(760, "Kernel for dZ/dy", KY, kernel_style(ORANGE, ORANGE_BG, ORANGE_BG2))
    o.append(f'<text x="{380 + 1.5 * S}" y="342" font-size="18" text-anchor="middle" fill="{INK}">east minus west</text>')
    o.append(f'<text x="{760 + 1.5 * S}" y="342" font-size="18" text-anchor="middle" fill="{INK}">north minus south</text>')
    o.append("</svg>")
    (IMG / "ta-slope-third-order.svg").write_text("".join(o), encoding="utf-8")

    z = {ZNUM[r][c]: ELEV[r][c] for r in range(3) for c in range(3)}
    dx = ((z[3] - z[1]) + 2 * (z[5] - z[4]) + (z[8] - z[6])) / 80
    dy = ((z[1] - z[6]) + 2 * (z[2] - z[7]) + (z[3] - z[8])) / 80
    print(f"wrote ta-slope-third-order.svg  dZ/dx={dx}  dZ/dy={dy}  "
          f"slope={math.degrees(math.atan(math.hypot(dx, dy))):.2f} deg")


if __name__ == "__main__":
    main()
