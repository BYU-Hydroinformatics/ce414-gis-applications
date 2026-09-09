"""Schematic spectral-signature figure for the Week 3 raster deck: reflectance of green vegetation,
dry soil and clear water from 0.4 to 1.0 micrometers, with the Landsat 8/9 red (Band 4) and NIR
(Band 5) windows marked. The curves are textbook shapes (Jensen; Lillesand, Kiefer and Chipman),
drawn by hand as smooth polylines, not measurements: the figure says so in its caption.

    python tools/week03_spectral_signature.py  ->  slides/week-03/images/ra-spectral-signature.svg
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "slides", "week-03", "images", "ra-spectral-signature.svg")
W, H = 760, 420
L, R, T, B = 70, 730, 30, 340          # plot box
NAVY, GRAY = "#002e5d", "#5a6472"
FONT = "font-family='Segoe UI, Helvetica, Arial, sans-serif'"

def x(um): return L + (um - 0.4) / 0.6 * (R - L)
def y(pct): return B - pct / 60.0 * (B - T)

# (wavelength um, reflectance %) control points, textbook shapes
veg = [(0.40, 4), (0.45, 4), (0.50, 6), (0.55, 12), (0.60, 7), (0.65, 4), (0.68, 4), (0.70, 12), (0.72, 30), (0.75, 45), (0.80, 50), (0.90, 50), (1.00, 48)]
soil = [(0.40, 8), (0.50, 14), (0.60, 20), (0.70, 24), (0.80, 27), (0.90, 30), (1.00, 32)]
water = [(0.40, 7), (0.45, 8), (0.50, 7), (0.55, 5), (0.60, 4), (0.65, 3), (0.70, 2), (0.80, 1), (0.90, 0.5), (1.00, 0.3)]

def path(pts, color, width=4):
    d = "M " + " L ".join(f"{x(u):.1f} {y(p):.1f}" for u, p in pts)
    return f"<path d='{d}' fill='none' stroke='{color}' stroke-width='{width}' stroke-linejoin='round'/>"

s = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}'>",
     f"<rect width='{W}' height='{H}' fill='#ffffff'/>"]
# band windows: Landsat 8/9 OLI red 0.64-0.67, NIR 0.85-0.88; visible band tint
s.append(f"<rect x='{x(0.4)}' y='{T}' width='{x(0.7)-x(0.4)}' height='{B-T}' fill='#f7f7f7'/>")
for u0, u1, col, lab in [(0.64, 0.67, "#e53935", "red, Band 4"), (0.85, 0.88, "#8e24aa", "NIR, Band 5")]:
    s.append(f"<rect x='{x(u0)}' y='{T}' width='{x(u1)-x(u0)}' height='{B-T}' fill='{col}' fill-opacity='0.18'/>")
    s.append(f"<text x='{(x(u0)+x(u1))/2}' y='{T+18}' text-anchor='middle' font-size='14' font-weight='700' fill='{col}' {FONT}>{lab}</text>")
# axes
s.append(f"<line x1='{L}' y1='{B}' x2='{R}' y2='{B}' stroke='{NAVY}' stroke-width='2'/>")
s.append(f"<line x1='{L}' y1='{T}' x2='{L}' y2='{B}' stroke='{NAVY}' stroke-width='2'/>")
for u in [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
    s.append(f"<line x1='{x(u)}' y1='{B}' x2='{x(u)}' y2='{B+6}' stroke='{NAVY}' stroke-width='2'/>")
    s.append(f"<text x='{x(u)}' y='{B+24}' text-anchor='middle' font-size='14' fill='{NAVY}' {FONT}>{u:.1f}</text>")
for p in [0, 20, 40, 60]:
    s.append(f"<line x1='{L-6}' y1='{y(p)}' x2='{L}' y2='{y(p)}' stroke='{NAVY}' stroke-width='2'/>")
    s.append(f"<text x='{L-10}' y='{y(p)+5}' text-anchor='end' font-size='14' fill='{NAVY}' {FONT}>{p}</text>")
s.append(f"<text x='{(L+R)/2}' y='{B+48}' text-anchor='middle' font-size='15' fill='{NAVY}' {FONT}>wavelength, micrometers</text>")
s.append(f"<text x='18' y='{(T+B)/2}' text-anchor='middle' font-size='15' fill='{NAVY}' transform='rotate(-90 18 {(T+B)/2})' {FONT}>reflectance, percent</text>")
# visible color strip along the bottom of the plot
for u, col in [(0.40, "#7b4fbf"), (0.45, "#2e5bd6"), (0.50, "#1fa64a"), (0.55, "#c9d400"), (0.60, "#f0a500"), (0.65, "#e53935")]:
    s.append(f"<rect x='{x(u)}' y='{B-8}' width='{x(u+0.05)-x(u)}' height='8' fill='{col}'/>")
s.append(f"<text x='{x(0.55)}' y='{B-14}' text-anchor='middle' font-size='12' fill='{GRAY}' {FONT}>visible</text>")
s.append(f"<text x='{x(0.85)}' y='{B-14}' text-anchor='middle' font-size='12' fill='{GRAY}' {FONT}>near-infrared</text>")
# curves and labels
s.append(path(veg, "#2e7d32")); s.append(path(soil, "#a1662f")); s.append(path(water, "#1e88e5"))
s.append(f"<text x='{x(0.905)}' y='{y(50)-10}' font-size='15' font-weight='700' fill='#2e7d32' {FONT}>green vegetation</text>")
s.append(f"<text x='{x(0.905)}' y='{y(30)-8}' font-size='15' font-weight='700' fill='#a1662f' {FONT}>dry soil</text>")
s.append(f"<text x='{x(0.905)}' y='{y(0.5)-8}' font-size='15' font-weight='700' fill='#1e88e5' {FONT}>clear water</text>")
# the red edge
s.append(f"<text x='{x(0.71)+6}' y='{y(28)}' font-size='13' fill='{GRAY}' {FONT}>the red edge</text>")
s.append(f"<text x='{L}' y='{H-8}' font-size='12' fill='{GRAY}' {FONT}>Schematic curves after Jensen and Lillesand, Kiefer and Chipman; band windows from the USGS Landsat 8/9 OLI table.</text>")
s.append("</svg>")
with open(OUT, "w", encoding="utf-8") as f: f.write("\n".join(s) + "\n")
print(OUT)
