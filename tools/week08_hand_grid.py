#!/usr/bin/env python3
"""The 10 x 10 HAND teaching grid for the Week 8 Thursday deck (slides/week-08/hand.md).

    python3 tools/week08_hand_grid.py

A made-up valley, small enough to read every number: a river runs north to south down the middle,
dropping 0.2 m per row, with one bend between rows 3 and 4. The land rises 1 m per cell to the west
and more gently on the east, where a low terrace (0.5 m, then 1.0 m) sits beside the river before
the valley wall. Flow direction is honest D8 (steepest drop, diagonal distances x sqrt 2), computed
here, not drawn by hand; every land cell's path ends on a river cell, its nearest drain, and
HAND = its elevation - that river cell's elevation.

Writes three inline SVGs into hand.md, each on the line after a marker comment
`<!-- generated: tools/week08_hand_grid.py (NAME) -->`, plus the static profile figure
slides/week-08/images/fl-hand-vs-hydraulic.svg and the numbers in tools/week08_hand_grid.json.

The inline SVGs carry their own <style> (a style outside the svg gets scoped by Marp and cannot see
the fragment state). Each reveal is keyed to a key-press fragment on the same slide:
`section:has(li[data-bespoke-marp-fragment="inactive"] .KEY) .TARGET` hides TARGET until the list
item holding the span with class KEY is shown. With no bespoke state (PNG or PDF export, or the
grid read on its own) nothing matches, so the default state is the finished one.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECK = ROOT / "slides" / "week-08" / "hand.md"
OUT_SVG = ROOT / "slides" / "week-08" / "images" / "fl-hand-vs-hydraulic.svg"
OUT_JSON = ROOT / "tools" / "week08_hand_grid.json"

N = 10
RIVER_COL = [4, 4, 4, 4, 5, 5, 5, 5, 5, 5]   # the river's column in each row (one bend)
RIVER_TOP, DROP = 21.8, 0.2                  # river elevation in row 0, and its drop per row (m)
WEST = [1, 2, 3, 4, 5, 6]                    # rise above the river, 1 to 6 cells west of it (m)
EAST = [0.5, 1.0, 2.0, 3.5, 5.0, 6.5]        # the same to the east: a low terrace, then the wall

# Example cells (row, col) the slides point at.
BEND = [(3, 6), (4, 2)]        # near the bend: each drains diagonally to a river cell in another row
CONTRAST = [(0, 3), (9, 8)]    # higher but HAND 1.0, against lower but HAND 2.0


def elevation(r, c):
    d = c - RIVER_COL[r]
    base = RIVER_TOP - DROP * r
    if d == 0:
        return round(base, 1)
    return round(base + (WEST[-d - 1] if d < 0 else EAST[d - 1]), 1)


Z = [[elevation(r, c) for c in range(N)] for r in range(N)]
RIVER = {(r, RIVER_COL[r]) for r in range(N)}


def d8(r, c):
    """The neighbor with the steepest drop; raises on a pit or a tie, so the grid stays honest."""
    best, tie = None, False
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if not (0 <= rr < N and 0 <= cc < N):
                continue
            drop = (Z[r][c] - Z[rr][cc]) / (math.sqrt(2) if dr and dc else 1)
            if drop <= 0:
                continue
            if best is None or drop > best[0] + 1e-9:
                best, tie = (drop, rr, cc), False
            elif abs(drop - best[0]) < 1e-9:
                tie = True
    if best is None or tie:
        raise SystemExit(f"cell {(r, c)}: {'pit' if best is None else 'tie'}; change the grid")
    return best[1], best[2]


PATH, HAND = {}, [[0.0] * N for _ in range(N)]
for r in range(N):
    for c in range(N):
        p = [(r, c)]
        while p[-1] not in RIVER:
            p.append(d8(*p[-1]))
        PATH[(r, c)] = p
        dr_, dc_ = p[-1]
        HAND[r][c] = round(Z[r][c] - Z[dr_][dc_], 1)
LAND = [(r, c) for r in range(N) for c in range(N) if (r, c) not in RIVER]
WET = {lv: [rc for rc in LAND if HAND[rc[0]][rc[1]] <= lv + 1e-9] for lv in (1, 2, 3)}

# ---------------------------------------------------------------------------------------------
CELL, X0, Y0 = 50, 10, 34
SCALE = 1.05                  # drawn size on the slide, relative to the viewBox
W, H = X0 * 2 + CELL * N, Y0 + CELL * N + 34
INK, RIVER_FILL = "#22262e", "#1f5fa8"
FLOOD = {1: "#3f84cc", 2: "#7fb2e3", 3: "#bcd7f1"}
FONT = 'font-family="Helvetica,Arial,sans-serif"'


def ramp(v, lo, hi):
    """Pale green (low) to tan (high), for elevation or HAND."""
    t = max(0.0, min(1.0, (v - lo) / (hi - lo)))
    a, b = (0xe9, 0xf2, 0xdc), (0xcf, 0xb0, 0x86)
    return "#%02x%02x%02x" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def cx(c):
    return X0 + CELL * c + CELL / 2


def cy(r):
    return Y0 + CELL * r + CELL / 2


def rect(r, c, fill, cls="", extra=""):
    k = f' class="{cls}"' if cls else ""
    return (f'<rect{k} x="{X0 + CELL * c}" y="{Y0 + CELL * r}" width="{CELL}" height="{CELL}" '
            f'fill="{fill}" stroke="#ffffff" stroke-width="1.5"{extra}/>')


def text(r, c, s, cls="", fill=INK, size=15, weight="400", arrows_under=True):
    k = f' class="{cls}"' if cls else ""
    return (f'<text{k} x="{cx(c):.0f}" y="{cy(r) + (1 if arrows_under else 6):.0f}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="middle" fill="{fill}">{s}</text>')


def arrow(a, b, color, width, marker):
    """A short arrow across the boundary from cell a toward cell b, clear of both numbers."""
    (r1, c1), (r2, c2) = a, b
    if r1 == r2:   # across: run under the numbers, not through them
        lift, f0, f1 = 13, 0.24, 0.70
    else:          # down or diagonal: cross the shared edge or corner, clear of both numbers
        lift, f0, f1 = 0, 0.36, 0.66
    x1, y1, x2, y2 = cx(c1), cy(r1) + lift, cx(c2), cy(r2) + lift
    return (f'<line x1="{x1 + (x2 - x1) * f0:.1f}" y1="{y1 + (y2 - y1) * f0:.1f}" '
            f'x2="{x1 + (x2 - x1) * f1:.1f}" y2="{y1 + (y2 - y1) * f1:.1f}" stroke="{color}" '
            f'stroke-width="{width}" stroke-linecap="round" marker-end="url(#{marker})"/>')


def markers(p):
    return (f'<defs><marker id="{p}-ah" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="4.5" '
            f'markerHeight="4.5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#4a5568"/></marker>'
            f'<marker id="{p}-ao" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="3.6" '
            f'markerHeight="3.6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#e8792b"/></marker></defs>')


def ring(rc, color="#e8792b", cls=""):
    k = f' class="{cls}"' if cls else ""
    r, c = rc
    return (f'<rect{k} x="{X0 + CELL * c + 2.5}" y="{Y0 + CELL * r + 2.5}" width="{CELL - 5}" '
            f'height="{CELL - 5}" fill="none" stroke="{color}" stroke-width="4" rx="4"/>')


def flow_arrows(p, cls):
    out = [f'<g class="{cls}">']
    for rc in LAND:
        out.append(arrow(rc, PATH[rc][1], "#4a5568", 2.2, f"{p}-ah"))
    out.append("</g>")
    return "".join(out)


def header(label):
    return (f'<text x="{X0}" y="22" font-size="14" fill="#4a5568">{label}</text>'
            f'<text x="{X0 + CELL * N}" y="22" font-size="14" fill="{RIVER_FILL}" font-weight="700" '
            f'text-anchor="end">river flows south ↓</text>')


def hide_until(key, target, extra=""):
    """CSS: TARGET is hidden while the fragment holding KEY has not been shown yet."""
    return (f'section:has(li[data-bespoke-marp-fragment="inactive"] .{key}) .{target}'
            f'{{opacity:0{extra}}}')


def svg_open(p, style):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W * SCALE:.0f}" '
            f'height="{H * SCALE:.0f}" {FONT}><style>{style}</style>{markers(p)}')


def svg_elev():
    """Slide 1: elevations and river cells; key presses add the D8 arrows, then the bend paths."""
    p = "hgA"
    style = (f".{p}-fade{{transition:opacity .7s ease-out}}"
             + hide_until(f"{p}-k1", f"{p}-arrows") + hide_until(f"{p}-k2", f"{p}-bend"))
    s = [svg_open(p, style), header("elevation (m) of each cell")]
    for r in range(N):
        for c in range(N):
            if (r, c) in RIVER:
                s += [rect(r, c, RIVER_FILL), text(r, c, f"{Z[r][c]:.1f}", fill="#ffffff", weight="700")]
            else:
                s += [rect(r, c, ramp(Z[r][c], 20, 27)), text(r, c, f"{Z[r][c]:.1f}")]
    s.append(flow_arrows(p, f"{p}-arrows {p}-fade"))
    s.append(f'<g class="{p}-bend {p}-fade">')
    for rc in BEND:
        path = PATH[rc]
        s.append(ring(rc))
        for a, b in zip(path, path[1:]):
            s.append(arrow(a, b, "#e8792b", 4.5, f"{p}-ao"))
        s.append(ring(path[-1], "#ffd21f"))
    s.append("</g>")
    s.append(f'<text x="{X0}" y="{H - 10}" font-size="13" fill="#4a5568">A made-up valley, 1 cell = 1 '
             f'unit; D8 flow directions computed, not drawn by hand</text></svg>')
    return "".join(s)


def svg_hand():
    """Slide 2: the same grid; one key press rings two cells, the next swaps every elevation for its HAND."""
    p = "hgB"
    style = (f".{p}-fade{{transition:opacity .8s ease-out}}"
             + hide_until(f"{p}-k1", f"{p}-pair")
             + hide_until(f"{p}-k2", f"{p}-hand")
             # elevations show only before the swap; with no fragment state (an export) HAND shows
             + f".{p}-elev{{opacity:0}}"
             + f'section:has(li[data-bespoke-marp-fragment="inactive"] .{p}-k2) .{p}-elev{{opacity:1}}')
    s = [svg_open(p, style), header("elevation (m), then HAND (m)")]
    for r in range(N):
        for c in range(N):
            river = (r, c) in RIVER
            s.append(rect(r, c, RIVER_FILL if river else ramp(Z[r][c], 20, 27), f"{p}-elev {p}-fade"))
            s.append(rect(r, c, RIVER_FILL if river else ramp(HAND[r][c], 0, 6), f"{p}-hand {p}-fade"))
            s.append(text(r, c, f"{Z[r][c]:.1f}", f"{p}-elev {p}-fade", "#ffffff" if river else INK,
                          weight="700" if river else "400"))
            s.append(text(r, c, "0" if river else f"{HAND[r][c]:.1f}", f"{p}-hand {p}-fade",
                          "#ffffff" if river else INK, size=17, weight="700"))
    s.append(f'<g opacity=".35">{flow_arrows(p, "")}</g>')
    s.append(f'<g class="{p}-pair {p}-fade">' + "".join(ring(rc) for rc in CONTRAST) + "</g>")
    s.append(f'<text x="{X0}" y="{H - 10}" font-size="13" fill="#4a5568">HAND = elevation − the '
             f'elevation of the river cell it drains to</text></svg>')
    return "".join(s)


def svg_flood():
    """Slide 3: HAND numbers; each pair of key presses asks a level, then floods HAND <= level."""
    p = "hgC"
    style = f".{p}-fade{{transition:opacity .7s ease-out}}" + "".join(
        hide_until(f"{p}-a{lv}", f"{p}-w{lv}") for lv in (1, 2, 3))
    s = [svg_open(p, style), header("HAND (m); the river rises by h")]
    for r in range(N):
        for c in range(N):
            if (r, c) in RIVER:
                s.append(rect(r, c, RIVER_FILL))
            else:
                s.append(rect(r, c, ramp(HAND[r][c], 0, 6)))
    for lv in (1, 2, 3):   # each level adds only the cells the one below it left dry
        s.append(f'<g class="{p}-w{lv} {p}-fade">')
        for rc in WET[lv]:
            if lv == 1 or rc not in WET[lv - 1]:
                s.append(rect(rc[0], rc[1], FLOOD[lv]))
        s.append("</g>")
    for r in range(N):
        for c in range(N):
            if (r, c) in RIVER:
                s.append(text(r, c, "0", fill="#ffffff", size=17, weight="700", arrows_under=False))
            else:
                s.append(text(r, c, f"{HAND[r][c]:.1f}", size=17, weight="700", arrows_under=False))
    s.append(f'<text x="{X0}" y="{H - 10}" font-size="13" fill="#4a5568">Flooded: every cell with '
             f'HAND ≤ h. Darker blue floods first.</text></svg>')
    return "".join(s)


def svg_profile():
    """Static figure: HAND's one depth everywhere against a hydraulic model's water surface."""
    w, h = 760, 400
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" {FONT}>',
         f'<rect width="{w}" height="{h}" fill="#ffffff"/>']
    # Channel bed along the river: gentle, a steep riffle, gentle again; a bridge near the bottom end.
    xs = [40, 250, 330, 560, 720]
    bed = [130, 175, 270, 300, 318]
    pts = " ".join(f"{x},{y}" for x, y in zip(xs, bed))
    s.append(f'<polygon points="40,{h - 40} {pts} 720,{h - 40}" fill="#d9c7a6"/>')
    s.append(f'<polyline points="{pts}" fill="none" stroke="#8a6a4f" stroke-width="3"/>')
    # HAND: one depth above the river everywhere (parallel to the bed line).
    dh = 46
    s.append(f'<polyline points="{" ".join(f"{x},{y - dh}" for x, y in zip(xs, bed))}" fill="none" '
             f'stroke="#0062b8" stroke-width="3" stroke-dasharray="10 6"/>')
    # Hydraulic water surface: shallower on the steep reach, backed up behind the bridge.
    hyd = [(40, 130 - 50), (250, 175 - 48), (290, 222 - 22), (330, 270 - 22), (400, 279 - 44),
           (520, 295 - 74), (603, 306 - 78), (626, 307 - 36), (720, 318 - 44)]
    s.append(f'<polyline points="{" ".join(f"{x},{y}" for x, y in hyd)}" fill="none" '
             f'stroke="#2e7d32" stroke-width="3.5"/>')
    # Bridge deck and pier.
    s.append('<rect x="586" y="214" width="58" height="10" fill="#4a5568"/>'
             '<rect x="609" y="224" width="12" height="84" fill="#4a5568"/>')
    lab = [(60, 40, "#0062b8", "HAND: the same depth h above the river everywhere"),
           (60, 62, "#2e7d32", "Hydraulic model: the water surface the flow actually makes")]
    for x, y, col, t in lab:
        s.append(f'<text x="{x}" y="{y}" font-size="17" font-weight="700" fill="{col}">{t}</text>')
    s.append('<text x="300" y="318" font-size="15" fill="#22262e" text-anchor="middle">steep reach:</text>'
             '<text x="300" y="336" font-size="15" fill="#22262e" text-anchor="middle">shallower, faster</text>')
    s.append('<text x="615" y="176" font-size="15" fill="#22262e" text-anchor="middle">bridge:</text>'
             '<text x="615" y="194" font-size="15" fill="#22262e" text-anchor="middle">water backs up</text>')
    s.append('<text x="70" y="168" font-size="15" fill="#8a6a4f">riverbed</text>')
    s.append(f'<text x="40" y="{h - 14}" font-size="14" fill="#4a5568">upstream</text>'
             f'<text x="720" y="{h - 14}" font-size="14" fill="#4a5568" text-anchor="end">downstream</text>'
             f'<text x="380" y="{h - 14}" font-size="14" fill="#4a5568" text-anchor="middle">'
             f'Diagram, not to scale</text></svg>')
    return "".join(s)


def write_inline(name, svg):
    marker = f"<!-- generated: tools/week08_hand_grid.py ({name}) -->"
    lines = DECK.read_text(encoding="utf-8").split("\n")
    i = lines.index(marker)
    lines[i + 1] = svg
    DECK.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    write_inline("elev", svg_elev())
    write_inline("hand", svg_hand())
    write_inline("flood", svg_flood())
    OUT_SVG.write_text(svg_profile(), encoding="utf-8")
    OUT_JSON.write_text(json.dumps({
        "elevation": Z, "hand": HAND, "river_cells": sorted(RIVER),
        "drain": {f"{r},{c}": list(PATH[(r, c)][-1]) for r, c in LAND},
        "land_cells": len(LAND), "wet_cells": {str(k): len(v) for k, v in WET.items()},
        "bend_examples": {f"{r},{c}": [list(x) for x in PATH[(r, c)]] for r, c in BEND},
        "contrast": {f"{r},{c}": {"elevation": Z[r][c], "hand": HAND[r][c]} for r, c in CONTRAST},
    }, indent=1), encoding="utf-8")
    print("land cells", len(LAND), "wet", {k: len(v) for k, v in WET.items()})
    for r, c in BEND + CONTRAST:
        print((r, c), Z[r][c], "->", PATH[(r, c)][-1], "HAND", HAND[r][c])
