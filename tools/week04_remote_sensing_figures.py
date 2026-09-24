#!/usr/bin/env python3
"""Figures for the Week 4 remote-sensing deck (slides/week-04/remote-sensing.md).

    python3 tools/week04_remote_sensing_figures.py

writes into slides/week-04/images/:

  rs-rgb-stack.svg          three band "sheets" of grid paper stacked into one full-color sheet
  rs-camera-bands.svg       the visible slice with a camera's three windows marked (section divider)
  rs-band-ruler.svg         0.4-2.5 um: eye, Landsat 8/9 OLI, and a 224-band hyperspectral sensor,
                            with the water-vapor absorption notches shaded
  rs-image-chain.svg        sun -> atmosphere -> surface -> atmosphere -> satellite -> numbers
  rs-orbits.svg             sun-synchronous polar orbit vs geostationary (not to scale)
  rs-four-resolutions.svg   spatial / spectral / temporal / radiometric icon strip
  rs-band-<name>-{red,green,blue}.jpg
                            each example image split into its three bands, each band drawn on a
                            black-to-color ramp so the three add back up to the original

The band splits are computed from the pixels of the images already in the deck; they are not
ArcGIS Pro captures. tools/week04-arcgis-capture-plan.md lists the ArcGIS Pro versions to make.

Band edges: Landsat 8/9 OLI from the USGS band designations; the hyperspectral row is drawn as
224 contiguous ~10 nm bands from 0.4 to 2.5 um (the AVIRIS layout). The camera windows are
schematic, not a particular camera's filter curves. The 4x4 pixel values in the stack figure are
illustrative, chosen to look like water, grass, a red roof and pavement.
"""
from __future__ import annotations

import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "slides", "week-04", "images")
NAVY, GRAY, INK = "#002e5d", "#5a6472", "#22262e"
FONT = "font-family='Avenir Next, Segoe UI, Helvetica, Arial, sans-serif'"
CH = {"red": (192, 57, 43), "green": (30, 132, 73), "blue": (31, 95, 191)}
CH_HEX = {k: "#%02x%02x%02x" % v for k, v in CH.items()}


def write(name: str, parts: list[str]) -> None:
    with open(os.path.join(OUT, name), "w") as f:
        f.write("\n".join(parts) + "\n")
    print("wrote", name)


def svg_open(w: int, h: int) -> list[str]:
    return [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' width='{w}' height='{h}' {FONT}>",
            f"<rect width='{w}' height='{h}' fill='#ffffff'/>"]


def wl_color(nm: float) -> str:
    """Approximate display color for a visible wavelength (Bruton's piecewise ramp)."""
    if nm < 440: r, g, b = -(nm - 440) / 60, 0, 1
    elif nm < 490: r, g, b = 0, (nm - 440) / 50, 1
    elif nm < 510: r, g, b = 0, 1, -(nm - 510) / 20
    elif nm < 580: r, g, b = (nm - 510) / 70, 1, 0
    elif nm < 645: r, g, b = 1, -(nm - 645) / 65, 0
    else: r, g, b = 1, 0, 0
    return "#%02x%02x%02x" % tuple(int(255 * max(0, min(1, v))) for v in (r, g, b))


def gradient(id_: str, lo: float = 400, hi: float = 700) -> str:
    stops = "".join(f"<stop offset='{(nm - lo) / (hi - lo):.3f}' stop-color='{wl_color(nm)}'/>"
                    for nm in range(int(lo), int(hi) + 1, 10))
    return f"<linearGradient id='{id_}' x1='0' x2='1' y1='0' y2='0'>{stops}</linearGradient>"


# ---------------------------------------------------------------------------------------------
# 1. RGB stack: three sheets of grid paper, one per band, and the full-color sheet they make
# ---------------------------------------------------------------------------------------------
# rows of a 4x4 scene: water, water/grass, grass/roof, pavement
SCENE = [
    [(40, 90, 160), (45, 100, 170), (60, 140, 70), (70, 150, 80)],
    [(50, 110, 175), (80, 150, 90), (65, 145, 75), (200, 60, 50)],
    [(75, 145, 85), (90, 160, 95), (210, 70, 55), (190, 55, 45)],
    [(150, 150, 150), (160, 160, 160), (155, 155, 155), (145, 145, 145)],
]


def sheet(ox: float, oy: float, cell: float, values, fill_fn, label: str, label_color: str,
          text_fn=None, font=13) -> list[str]:
    """One sheet of grid paper seen obliquely: local grid (col*cell, row*cell) sheared back."""
    k, s = 0.7, 0.5           # shear right as rows go back, and foreshorten depth
    p = [f"<g transform='matrix(1,0,{k},{s},{ox},{oy})'>"]
    n = len(values)
    p.append(f"<rect x='-4' y='-4' width='{n * cell + 8}' height='{n * cell + 8}' fill='#f4f6f9' stroke='{GRAY}' stroke-width='2'/>")
    for r in range(n):
        for c in range(n):
            p.append(f"<rect x='{c * cell}' y='{r * cell}' width='{cell}' height='{cell}' fill='{fill_fn(values[r][c])}' stroke='#ffffff' stroke-width='2'/>")
    p.append("</g>")
    # numbers are placed at the sheared cell centers but drawn upright, so they stay legible
    if text_fn:
        for r in range(n):
            for c in range(n):
                txt, col = text_fn(values[r][c])
                lx, ly = c * cell + cell / 2, r * cell + cell / 2
                p.append(f"<text x='{lx + k * ly + ox:.1f}' y='{s * ly + oy + font * 0.36:.1f}' font-size='{font}' "
                         f"font-weight='700' text-anchor='middle' fill='{col}'>{txt}</text>")
    # label to the left of the sheet's front edge
    p.append(f"<text x='{ox - 16}' y='{oy + n * cell * s * 0.55}' font-size='22' font-weight='700' "
             f"text-anchor='end' fill='{label_color}'>{label}</text>")
    return p


def rgb_stack() -> None:
    W, H = 1180, 560
    cell = 66
    p = svg_open(W, H)
    x0, y0, gap = 210, 30, 172
    for i, (name, col) in enumerate(CH.items()):
        vals = [[px[i] for px in row] for row in SCENE]

        def fill(v, i=i):
            rgb = [0, 0, 0]
            rgb[i] = v
            return "rgb(%d,%d,%d)" % tuple(rgb)

        p += sheet(x0, y0 + i * gap, cell, vals, fill, f"{name.capitalize()} band", CH_HEX[name],
                   text_fn=lambda v: (str(v), "#ffffff"), font=19)
    # "+" signs between sheets
    for i in range(2):
        p.append(f"<text x='120' y='{y0 + i * gap + 150}' font-size='40' font-weight='700' fill='{GRAY}' text-anchor='middle'>+</text>")
    # arrow to the composite
    p.append(f"<defs><marker id='ah' viewBox='0 0 10 10' refX='8' refY='5' markerWidth='7' markerHeight='7' orient='auto'>"
             f"<path d='M0,0 L10,5 L0,10 z' fill='{NAVY}'/></marker></defs>")
    p.append(f"<line x1='630' y1='255' x2='735' y2='255' stroke='{NAVY}' stroke-width='6' marker-end='url(#ah)'/>")
    p.append(f"<text x='682' y='228' font-size='20' font-weight='700' fill='{NAVY}' text-anchor='middle'>combine</text>")
    # composite sheet, drawn larger
    p += sheet(770, 175, 62, SCENE, lambda c: "rgb(%d,%d,%d)" % c, "", NAVY)
    p.append(f"<text x='935' y='345' font-size='24' font-weight='700' fill='{NAVY}' text-anchor='middle'>Full-color image</text>")
    p.append(f"<text x='935' y='375' font-size='18' fill='{INK}' text-anchor='middle'>every pixel = three numbers</text>")
    # call out one pixel: row 1, col 3 (the roof)
    r, g, b = SCENE[1][3]
    p.append(f"<text x='935' y='417' font-size='18' fill='{INK}' text-anchor='middle'>roof pixel: R {r} · G {g} · B {b}</text>")
    p.append(f"<text x='935' y='449' font-family='Menlo, Consolas, monospace' font-size='26' font-weight='700' "
             f"fill='{INK}' text-anchor='middle'>#{r:02X}{g:02X}{b:02X}</text>")
    p.append(f"<rect x='1040' y='428' width='28' height='28' fill='rgb({r},{g},{b})' stroke='{GRAY}'/>")
    p.append("</svg>")
    write("rs-rgb-stack.svg", p)


# ---------------------------------------------------------------------------------------------
# 2. Camera bands: the visible slice with three windows
# ---------------------------------------------------------------------------------------------
def camera_bands() -> None:
    W, H = 900, 190
    L, R = 60, 840

    def x(nm): return L + (nm - 400) / 300 * (R - L)
    p = svg_open(W, H)
    p[1] = f"<rect width='{W}' height='{H}' fill='none'/>"
    p.append(f"<defs>{gradient('vis')}</defs>")
    p.append(f"<rect x='{L}' y='95' width='{R - L}' height='34' fill='url(#vis)'/>")
    for nm, lab in ((400, "400 nm"), (500, "500"), (600, "600"), (700, "700 nm")):
        p.append(f"<text x='{x(nm)}' y='155' font-size='18' fill='#c9d3df' text-anchor='middle'>{lab}</text>")
    for name, lo, hi in (("blue", 430, 500), ("green", 510, 580), ("red", 590, 670)):
        p.append(f"<rect x='{x(lo)}' y='40' width='{x(hi) - x(lo)}' height='44' rx='6' fill='{CH_HEX[name]}'/>")
        p.append(f"<text x='{(x(lo) + x(hi)) / 2}' y='69' font-size='20' font-weight='700' fill='#fff' text-anchor='middle'>{name.upper()}</text>")
        p.append(f"<line x1='{(x(lo) + x(hi)) / 2}' y1='84' x2='{(x(lo) + x(hi)) / 2}' y2='95' stroke='{CH_HEX[name]}' stroke-width='3'/>")
    p.append("</svg>")
    write("rs-camera-bands.svg", p)


# ---------------------------------------------------------------------------------------------
# 3. Band ruler: eye vs Landsat 8/9 OLI vs hyperspectral, 0.4-2.5 um
# ---------------------------------------------------------------------------------------------
OLI = [  # (label, lo um, hi um, color)
    ("1", 0.433, 0.453, "#6a3fb5"), ("2", 0.450, 0.515, CH_HEX["blue"]), ("3", 0.525, 0.600, CH_HEX["green"]),
    ("4", 0.630, 0.680, CH_HEX["red"]), ("5", 0.845, 0.885, "#8b1a1a"), ("9", 1.363, 1.384, GRAY),
    ("6", 1.560, 1.660, "#7a5c2e"), ("7", 2.107, 2.294, "#7a5c2e"),
]


def band_ruler() -> None:
    W, H = 1100, 470
    L, R = 190, 1070

    def x(um): return L + (um - 0.4) / 2.1 * (R - L)
    p = svg_open(W, H)
    p.append(f"<defs>{gradient('vis2')}</defs>")
    top, bot = 55, 375
    # water-vapor absorption notches
    for lo, hi in ((1.35, 1.45), (1.80, 1.95)):
        p.append(f"<rect x='{x(lo)}' y='{top}' width='{x(hi) - x(lo)}' height='{bot - top}' fill='#dfe3e8'/>")
    p.append(f"<text x='{x(1.62)}' y='{top - 12}' font-size='19' fill='{GRAY}' text-anchor='middle'>gray: water vapor absorbs these wavelengths, so no satellite band sits there</text>")
    rows = [("Your eye", 110), ("Landsat 8/9", 200), ("Hyperspectral", 300)]
    for lab, y in rows:
        p.append(f"<text x='{L - 14}' y='{y + 8}' font-size='21' font-weight='700' fill='{NAVY}' text-anchor='end'>{lab}</text>")
        p.append(f"<line x1='{L}' y1='{y + 28}' x2='{R}' y2='{y + 28}' stroke='#e6e9ee'/>")
    # eye: the visible slice
    p.append(f"<rect x='{x(0.4)}' y='88' width='{x(0.7) - x(0.4)}' height='40' rx='4' fill='url(#vis2)'/>")
    p.append(f"<text x='{x(0.72)}' y='116' font-size='19' fill='{GRAY}'>3 wide, overlapping bands (cones)</text>")
    # OLI
    for lab, lo, hi, col in OLI:
        p.append(f"<rect x='{x(lo)}' y='178' width='{max(3, x(hi) - x(lo))}' height='40' fill='{col}' opacity='0.9'/>")
        ty = 172 if lab != "1" else 236
        p.append(f"<text x='{(x(lo) + x(hi)) / 2}' y='{ty}' font-size='14' font-weight='700' fill='{INK}' text-anchor='middle'>{lab}</text>")
    p.append(f"<text x='{x(0.95)}' y='252' font-size='19' fill='{GRAY}'>8 bands in this range, each a few tens of nm wide (multispectral)</text>")
    # hyperspectral: 224 contiguous bands
    edges = np.linspace(0.4, 2.5, 225)
    for lo, hi in zip(edges[:-1], edges[1:]):
        mid = (lo + hi) / 2
        col = wl_color(mid * 1000) if mid < 0.7 else "#4a4f57"
        p.append(f"<rect x='{x(lo):.2f}' y='278' width='{max(1.2, x(hi) - x(lo) - 1.2):.2f}' height='40' fill='{col}'/>")
    p.append(f"<text x='{x(1.45)}' y='347' font-size='19' fill='{GRAY}' text-anchor='middle'>224 contiguous bands, about 10 nm each: a full spectrum for every pixel</text>")
    # axis
    p.append(f"<line x1='{L}' y1='{bot}' x2='{R}' y2='{bot}' stroke='{INK}' stroke-width='2'/>")
    for um in (0.4, 0.7, 1.0, 1.5, 2.0, 2.5):
        p.append(f"<line x1='{x(um)}' y1='{bot}' x2='{x(um)}' y2='{bot + 8}' stroke='{INK}' stroke-width='2'/>")
        p.append(f"<text x='{x(um)}' y='{bot + 28}' font-size='17' fill='{INK}' text-anchor='middle'>{um:g}</text>")
    p.append(f"<text x='{(L + R) / 2}' y='{bot + 55}' font-size='18' fill='{INK}' text-anchor='middle'>wavelength (µm)</text>")
    for lo, hi, lab in ((0.4, 0.7, "visible"), (0.7, 1.3, "near-infrared"), (1.3, 2.5, "shortwave infrared")):
        p.append(f"<text x='{(x(lo) + x(hi)) / 2}' y='{bot + 82}' font-size='17' font-weight='700' fill='{NAVY}' text-anchor='middle'>{lab}</text>")
    p.append("</svg>")
    write("rs-band-ruler.svg", p)


# ---------------------------------------------------------------------------------------------
# 4. Image chain: how one satellite pixel gets made
# ---------------------------------------------------------------------------------------------
def image_chain() -> None:
    W, H = 1100, 560
    p = svg_open(W, H)
    p.append(f"<defs><marker id='a1' viewBox='0 0 10 10' refX='8' refY='5' markerWidth='6' markerHeight='6' orient='auto'>"
             f"<path d='M0,0 L10,5 L0,10 z' fill='#e0a800'/></marker>"
             f"<marker id='a2' viewBox='0 0 10 10' refX='8' refY='5' markerWidth='6' markerHeight='6' orient='auto'>"
             f"<path d='M0,0 L10,5 L0,10 z' fill='{CH_HEX['red']}'/></marker>"
             f"<marker id='a3' viewBox='0 0 10 10' refX='8' refY='5' markerWidth='6' markerHeight='6' orient='auto'>"
             f"<path d='M0,0 L10,5 L0,10 z' fill='{NAVY}'/></marker>"
             f"<linearGradient id='sky' x1='0' x2='0' y1='0' y2='1'><stop offset='0' stop-color='#dbe9f7'/><stop offset='1' stop-color='#f3f8fd'/></linearGradient></defs>")
    # atmosphere band and ground
    p.append(f"<rect x='0' y='250' width='760' height='170' fill='url(#sky)'/>")
    p.append(f"<text x='14' y='276' font-size='17' fill='{GRAY}'>atmosphere</text>")
    p.append(f"<rect x='0' y='420' width='760' height='140' fill='#e9e2d0'/>")
    # ground features: field, trees, water
    p.append("<rect x='40' y='440' width='180' height='70' fill='#8fbf5a'/>")
    for cx in (290, 330, 370):
        p.append(f"<circle cx='{cx}' cy='455' r='24' fill='#2f7d3b'/><rect x='{cx - 4}' y='470' width='8' height='30' fill='#6b4a2b'/>")
    p.append("<ellipse cx='560' cy='480' rx='120' ry='32' fill='#3a6ea5'/>")
    # sun
    p.append("<circle cx='90' cy='90' r='50' fill='#ffcc33'/>")
    for a in range(0, 360, 30):
        ang = np.radians(a)
        p.append(f"<line x1='{90 + 58 * np.cos(ang):.1f}' y1='{90 + 58 * np.sin(ang):.1f}' x2='{90 + 72 * np.cos(ang):.1f}' "
                 f"y2='{90 + 72 * np.sin(ang):.1f}' stroke='#ffcc33' stroke-width='5'/>")
    # incoming sunlight
    p.append("<line x1='140' y1='130' x2='330' y2='420' stroke='#e0a800' stroke-width='7' marker-end='url(#a1)'/>")
    # reflected up to satellite
    p.append("<line x1='340' y1='425' x2='590' y2='120' stroke='#e0a800' stroke-width='5' stroke-dasharray='14 8' marker-end='url(#a1)'/>")
    # emitted thermal from water, wavy
    p.append(f"<path d='M 600 445 C 640 400, 590 360, 630 320 S 610 240, 650 200 S 640 150, 660 128' fill='none' stroke='{CH_HEX['red']}' stroke-width='5' marker-end='url(#a2)'/>")
    # satellite
    p.append(f"<g transform='translate(620,70)'><rect x='-26' y='-20' width='52' height='40' rx='5' fill='{NAVY}'/>"
             f"<rect x='-110' y='-12' width='76' height='24' fill='#3d6fb6' stroke='{NAVY}' stroke-width='2'/>"
             f"<rect x='34' y='-12' width='76' height='24' fill='#3d6fb6' stroke='{NAVY}' stroke-width='2'/>"
             f"<line x1='-34' y1='0' x2='-26' y2='0' stroke='{NAVY}' stroke-width='3'/><line x1='26' y1='0' x2='34' y2='0' stroke='{NAVY}' stroke-width='3'/>"
             f"<circle cx='0' cy='26' r='9' fill='#22262e'/></g>")
    # numbered steps, each placed clear of the arrows
    def step(cx, cy, n, lines, color=INK):
        out = [f"<circle cx='{cx}' cy='{cy}' r='15' fill='{NAVY}'/><text x='{cx}' y='{cy + 6}' font-size='17' "
               f"font-weight='700' fill='#fff' text-anchor='middle'>{n}</text>"]
        for j, t in enumerate(lines):
            out.append(f"<text x='{cx + 22}' y='{cy + 7 + j * 24}' font-size='20' fill='{color}'>{t}</text>")
        return out
    p += step(226, 196, "1", ["Sunlight in, peaking", "in the visible"])
    p += step(30, 318, "2", ["Atmosphere absorbs", "and scatters, twice"])
    p += step(250, 532, "3", ["Grass, trees, and water reflect each band differently"])
    p += step(650, 368, "4", ["Warm surfaces also", "emit thermal IR"], CH_HEX["red"])
    # sensor -> numbers -> grids
    p.append(f"<line x1='740' y1='70' x2='800' y2='70' stroke='{NAVY}' stroke-width='5' marker-end='url(#a3)'/>")
    p += step(812, 40, "5", ["The sensor counts energy", "in each band window"], NAVY)
    grid_colors = [("blue", 0), ("green", 1), ("red", 2), ("near-IR", 3), ("thermal", 4)]
    cols = {"blue": CH_HEX["blue"], "green": CH_HEX["green"], "red": CH_HEX["red"], "near-IR": "#8b1a1a", "thermal": "#e8792b"}
    rng = np.random.default_rng(4)
    for name, i in grid_colors:
        gx, gy = 835 + i * 18, 110 + i * 60
        for r in range(4):
            for c in range(4):
                v = int(rng.integers(60, 255))
                p.append(f"<rect x='{gx + c * 22}' y='{gy + r * 12}' width='21' height='11' fill='{cols[name]}' opacity='{v / 255:.2f}'/>")
        p.append(f"<text x='{gx + 98}' y='{gy + 30}' font-size='17' font-weight='700' fill='{cols[name]}'>{name}</text>")
    p.append(f"<text x='815' y='440' font-size='20' fill='{INK}'>one grid of numbers per band,</text>")
    p.append(f"<text x='815' y='466' font-size='20' fill='{INK}'>0–255 in an 8-bit image</text>")
    p.append(f"<text x='815' y='492' font-size='20' fill='{INK}'>(0–4,095 from Landsat 8)</text>")
    p.append("</svg>")
    write("rs-image-chain.svg", p)


# ---------------------------------------------------------------------------------------------
# 5. Orbits
# ---------------------------------------------------------------------------------------------
def orbits() -> None:
    W, H = 640, 470
    cx, cy = 300, 250
    p = svg_open(W, H)
    # geostationary ring (far), equatorial, seen slightly from above
    p.append(f"<ellipse cx='{cx}' cy='{cy}' rx='270' ry='70' fill='none' stroke='#e8792b' stroke-width='4' stroke-dasharray='12 8'/>")
    # earth
    p.append(f"<circle cx='{cx}' cy='{cy}' r='95' fill='#3a6ea5'/>")
    p.append(f"<path d='M {cx - 60} {cy - 50} q 30 -20 55 5 q 20 25 -5 45 q -30 10 -50 -15 z' fill='#6fae5a'/>")
    p.append(f"<path d='M {cx + 20} {cy + 10} q 35 -5 45 25 q -10 30 -40 25 z' fill='#6fae5a'/>")
    p.append(f"<ellipse cx='{cx}' cy='{cy}' rx='95' ry='18' fill='none' stroke='#ffffff' stroke-opacity='0.5' stroke-width='1.5'/>")
    # polar orbit: tall narrow ellipse, slightly tilted, close to earth
    p.append(f"<ellipse cx='{cx}' cy='{cy}' rx='30' ry='122' transform='rotate(-8 {cx} {cy})' fill='none' stroke='{NAVY}' stroke-width='4'/>")
    # satellites
    p.append(f"<rect x='{cx - 10}' y='{cy - 132}' width='20' height='14' fill='{NAVY}'/>")
    p.append(f"<rect x='{cx + 262}' y='{cy - 8}' width='20' height='14' fill='#e8792b'/>")
    # footprint strip on earth for polar
    p.append(f"<rect x='{cx - 12}' y='{cy - 90}' width='22' height='180' fill='#ffffff' opacity='0.35' transform='rotate(-8 {cx} {cy})'/>")
    # labels
    p.append(f"<text x='{cx - 10}' y='{cy - 150}' font-size='25' font-weight='700' fill='{NAVY}' text-anchor='middle'>Sun-synchronous polar</text>")
    p.append(f"<text x='{cx - 10}' y='{cy - 180}' font-size='22' fill='{INK}' text-anchor='middle'>about 700–800 km up</text>")
    p.append(f"<text x='{W - 10}' y='{cy + 122}' font-size='25' font-weight='700' fill='#c0601a' text-anchor='end'>Geostationary</text>")
    p.append(f"<text x='{W - 10}' y='{cy + 150}' font-size='22' fill='{INK}' text-anchor='end'>35,786 km, over the equator</text>")
    p.append(f"<text x='{cx}' y='{H - 14}' font-size='19' fill='{GRAY}' text-anchor='middle'>Not to scale: the geostationary ring is about 5.6 Earth radii out</text>")
    p.append("</svg>")
    write("rs-orbits.svg", p)


# ---------------------------------------------------------------------------------------------
# 6. Four resolutions icon strip
# ---------------------------------------------------------------------------------------------
def four_resolutions() -> None:
    W, H = 1100, 170
    p = svg_open(W, H)
    p[1] = f"<rect width='{W}' height='{H}' fill='none'/>"
    panels = ["Spatial", "Spectral", "Temporal", "Radiometric"]
    subs = ["how big is a pixel?", "which bands, how wide?", "how often does it return?", "how many levels per band?"]
    pw = W / 4
    for i, (t, s) in enumerate(zip(panels, subs)):
        ox = i * pw + 20
        if i == 0:   # coarse vs fine pixels
            for r in range(2):
                for c in range(2):
                    p.append(f"<rect x='{ox + c * 32}' y='{14 + r * 32}' width='31' height='31' fill='#7aa9d6'/>")
            for r in range(8):
                for c in range(8):
                    p.append(f"<rect x='{ox + 90 + c * 8}' y='{14 + r * 8}' width='7' height='7' fill='#2f6fae' opacity='{0.4 + 0.6 * ((r * 3 + c * 5) % 7) / 7:.2f}'/>")
        elif i == 1:  # bands on a strip
            p.append(f"<rect x='{ox}' y='60' width='200' height='12' fill='#dfe3e8'/>")
            for j, (lo, w, col) in enumerate(((10, 22, CH_HEX['blue']), (40, 22, CH_HEX['green']), (70, 22, CH_HEX['red']), (115, 18, '#8b1a1a'), (160, 30, '#7a5c2e'))):
                p.append(f"<rect x='{ox + lo}' y='18' width='{w}' height='40' fill='{col}'/>")
        elif i == 2:  # calendar ticks
            for d in range(14):
                on = d % 8 == 0 or d % 8 == 5
                p.append(f"<rect x='{ox + (d % 7) * 28}' y='{14 + (d // 7) * 30}' width='24' height='24' rx='3' fill='{NAVY if on else '#e6e9ee'}'/>")
        else:  # 2-level vs many-level ramp
            for j in range(4):
                v = int(255 * j / 3)
                p.append(f"<rect x='{ox + j * 50}' y='14' width='50' height='22' fill='rgb({v},{v},{v})' stroke='#ccc'/>")
            for j in range(64):
                v = int(255 * j / 63)
                p.append(f"<rect x='{ox + j * 200 / 64:.2f}' y='42' width='{200 / 64 + 0.6:.2f}' height='22' fill='rgb({v},{v},{v})'/>")
        p.append(f"<text x='{ox}' y='104' font-size='22' font-weight='700' fill='{NAVY}'>{t}</text>")
        p.append(f"<text x='{ox}' y='130' font-size='17' fill='{INK}'>{s}</text>")
    p.append("</svg>")
    write("rs-four-resolutions.svg", p)


if __name__ == "__main__":
    rgb_stack()
    camera_bands()
    band_ruler()
    image_chain()
    orbits()
    four_resolutions()
