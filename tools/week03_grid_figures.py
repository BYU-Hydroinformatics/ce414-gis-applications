"""Small grid figures for the Week 3 raster decks, written as SVG into slides/week-03/images.

    python tools/week03_grid_figures.py

ra-map-algebra-add.svg      A + B = C on two 4x4 grids, one NoData cell, the cell-by-cell rule
ra-predict-exercise.svg     two 3x3 grids and an expression, output grid blank (the paper exercise)
ra-predict-answer.svg       the same with the output filled in
ra-integer-division.svg     the same division done on integers and on floats
ra-ndvi-cell.svg            NDVI as a local function: one cell of red, one of NIR, one answer
ra-focal-window.svg         a 3x3 mean window on a 5x5 grid, one output cell worked
ra-zonal-idea.svg           two zones over a grid, one number per zone
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "slides", "week-03", "images")
NAVY, ORANGE, GRAY, LIGHT = "#002e5d", "#e8792b", "#5a6472", "#eef3f9"
FONT = "font-family='Segoe UI, Helvetica, Arial, sans-serif'"
ND = "ND"


def grid(x, y, cells, size=44, label=None, hi=None, color="#ffffff", bold=None):
    """cells: list of rows; hi: set of (r,c) to highlight; ND draws gray."""
    s = []
    n = len(cells)
    for r, row in enumerate(cells):
        for c, v in enumerate(row):
            fill = "#d9dde3" if v == ND else color
            if hi and (r, c) in hi: fill = "#ffe9b3"
            if bold and (r, c) in bold: fill = "#ffd21f"
            s.append(f"<rect x='{x+c*size}' y='{y+r*size}' width='{size}' height='{size}' fill='{fill}' stroke='{NAVY}' stroke-width='1.5'/>")
            txt = "" if v is None else str(v)
            fs = 15 if len(txt) <= 3 else 12
            s.append(f"<text x='{x+c*size+size/2}' y='{y+r*size+size/2+5}' text-anchor='middle' font-size='{fs}' fill='{GRAY if v == ND else NAVY}' {FONT}>{txt}</text>")
    if label:
        s.append(f"<text x='{x+n*size/2}' y='{y-10}' text-anchor='middle' font-size='16' font-weight='700' fill='{NAVY}' {FONT}>{label}</text>")
    return "\n".join(s)


def op(x, y, sym, size=34):
    return f"<text x='{x}' y='{y}' text-anchor='middle' font-size='{size}' font-weight='700' fill='{ORANGE}' {FONT}>{sym}</text>"


def caption(x, y, text, size=15, color=GRAY, anchor="start", weight="400"):
    return f"<text x='{x}' y='{y}' text-anchor='{anchor}' font-size='{size}' font-weight='{weight}' fill='{color}' {FONT}>{text}</text>"


def svg(name, w, h, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' width='{w}' height='{h}'>\n"
                f"<rect width='{w}' height='{h}' fill='#ffffff'/>\n{body}\n</svg>\n")
    print(name)


# 1. A + B = C
A = [[3, 5, 2, 8], [4, 1, 7, 6], [9, 2, 3, 5], [1, 6, 4, 2]]
B = [[1, 1, 2, 2], [1, ND, 2, 2], [3, 3, 4, 4], [3, 3, 4, 4]]
C = [[a + b if b != ND else ND for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]
body = grid(30, 50, A, label="Layer A") + op(230, 145, "+") + grid(260, 50, B, label="Layer B") + op(460, 145, "=") + grid(490, 50, C, label="A + B", hi={(2, 1)})
body += "".join([f"<rect x='{30+1*44}' y='{50+2*44}' width='44' height='44' fill='none' stroke='{ORANGE}' stroke-width='3'/>",
                 f"<rect x='{260+1*44}' y='{50+2*44}' width='44' height='44' fill='none' stroke='{ORANGE}' stroke-width='3'/>",
                 f"<rect x='{490+1*44}' y='{50+2*44}' width='44' height='44' fill='none' stroke='{ORANGE}' stroke-width='3'/>"])
body += caption(30, 262, "Same cell in, same cell out: row 3, column 2 is 2 + 3 = 5. Nothing else on either grid is consulted.", 15)
body += caption(30, 286, f"ND is NoData. Anything combined with NoData is NoData: the hole in B is a hole in the answer.", 15)
svg("ra-map-algebra-add.svg", 780, 300, body)

# 2. prediction exercise: Con(A > 5, B, 0), with NoData
A3 = [[2, 7, 6], [9, 4, ND], [5, 8, 1]]
B3 = [[10, 20, 30], [40, 50, 60], [70, 80, 90]]
ans = [[(b if a > 5 else 0) if a != ND else ND for a, b in zip(ra, rb)] for ra, rb in zip(A3, B3)]
blank = [[None] * 3 for _ in range(3)]
head = f"<rect x='30' y='20' width='720' height='44' rx='8' fill='{NAVY}'/>" + caption(390, 49, "Con( A > 5 ,  B ,  0 )", 22, "#ffffff", "middle", "700")
body = head + grid(60, 110, A3, 48, label="A") + grid(260, 110, B3, 48, label="B") + op(430, 190, "→") + grid(480, 110, blank, 48, label="Output")
body += caption(60, 290, "Fill in the nine output cells on paper first. Where A is NoData, what is the output?", 15)
svg("ra-predict-exercise.svg", 780, 310, body)
body = head + grid(60, 110, A3, 48, label="A") + grid(260, 110, B3, 48, label="B") + op(430, 190, "→") + grid(480, 110, ans, 48, label="Output")
body += caption(60, 290, "Where A > 5 the output copies B, elsewhere 0; the NoData cell stays NoData. Con is local.", 15)
svg("ra-predict-answer.svg", 780, 310, body)

# 3. integer division
NIRg = [[3200, 4100, 900], [4800, 2600, 300], [3900, 3500, 3700]]
REDg = [[1100, 700, 800], [600, 2200, 500], [1000, 2900, 1200]]
fdiv = [[round((n - r) / (n + r), 2) for n, r in zip(rn, rr)] for rn, rr in zip(NIRg, REDg)]
idiv = [[int((n - r) / (n + r)) for n, r in zip(rn, rr)] for rn, rr in zip(NIRg, REDg)]
body = grid(30, 60, NIRg, 54, label="NIR (integer)") + op(215, 150, "−") + grid(240, 60, REDg, 54, label="red (integer)")
body += caption(30, 260, "(NIR − red) ÷ (NIR + red), cell by cell:", 16, NAVY, "start", "700")
body += grid(30, 300, idiv, 54, label="both integers") + grid(240, 300, fdiv, 54, label="after Float")
body += caption(430, 330, "Integer ÷ integer keeps only the whole part.", 15)
body += caption(430, 354, "Every NDVI between −1 and 1 becomes 0.", 15)
body += caption(430, 378, "The lone −1 is the cell where NIR is below red.", 15)
body += caption(430, 412, "Float first, and the decimals survive.", 15, NAVY, "start", "700")
body += caption(430, 436, "That is the whole reason Lab 2 has Step 1.", 15)
svg("ra-integer-division.svg", 790, 480, body)

# 4. NDVI as a local function on one cell
body = f"<rect x='20' y='20' width='660' height='60' rx='8' fill='{NAVY}'/>" + caption(350, 58, "NDVI  =  (NIR − red) ÷ (NIR + red)", 24, "#ffffff", "middle", "700")
cells = [("red band", "0.09", "#f4c6c6"), ("NIR band", "0.47", "#cfe8ff"), ("NDVI", "0.68", "#d8f5d0")]
x = 60
for i, (lab, val, col) in enumerate(cells):
    body += f"<rect x='{x}' y='120' width='120' height='120' rx='6' fill='{col}' stroke='{NAVY}' stroke-width='2'/>"
    body += caption(x + 60, 195, val, 30, NAVY, "middle", "700") + caption(x + 60, 262, lab, 15, GRAY, "middle")
    if i < 2: body += op(x + 180, 190, "→" if i == 1 else "+")
    x += 240
body += caption(60, 300, "One cell of a center-pivot field near Elberta in the Lab 2 scene. Reflectance in, one number out,", 15)
body += caption(60, 322, "and the six million other cells get the same two-line treatment with no reference to their neighbors.", 15)
svg("ra-ndvi-cell.svg", 700, 340, body)

# 5. focal window
G = [[2, 3, 3, 4, 5], [2, 3, 9, 4, 5], [3, 3, 4, 4, 6], [3, 4, 4, 5, 6], [4, 4, 5, 5, 7]]
win = {(r, c) for r in range(0, 3) for c in range(1, 4)}
body = grid(30, 50, G, 46, label="Input", hi=win, bold={(1, 2)})
body += f"<rect x='{30+1*46}' y='{50+0*46}' width='138' height='138' fill='none' stroke='{ORANGE}' stroke-width='3' stroke-dasharray='6 4'/>"
vals = [G[r][c] for (r, c) in sorted(win)]
mean = sum(vals) / 9
outg = [[None] * 5 for _ in range(5)]; outg[1][2] = round(mean, 1)
body += op(300, 170, "→") + grid(340, 50, outg, 46, label="3 × 3 mean", bold={(1, 2)})
body += caption(30, 310, f"Nine cells in, one cell out: ({' + '.join(str(v) for v in vals)}) ÷ 9 = {mean:.1f}", 15)
body += caption(30, 334, "The window then steps one cell to the right and does it again. The spike of 9 is smoothed to 4.1.", 15)
body += caption(30, 358, "At the grid edge the window hangs off the data: border cells are NoData unless the tool is told otherwise.", 15)
svg("ra-focal-window.svg", 780, 380, body)

# 6. zonal idea
Z = [["A", "A", "A", "B", "B"], ["A", "A", "B", "B", "B"], ["A", "A", "B", "B", "B"], ["A", "B", "B", "B", "B"], ["A", "B", "B", "B", "B"]]
V = [[0.2, 0.3, 0.2, 0.6, 0.7], [0.1, 0.2, 0.5, 0.7, 0.8], [0.2, 0.3, 0.6, 0.6, 0.7], [0.2, 0.7, 0.8, 0.7, 0.6], [0.3, 0.6, 0.7, 0.8, 0.7]]
za = [V[r][c] for r in range(5) for c in range(5) if Z[r][c] == "A"]
zb = [V[r][c] for r in range(5) for c in range(5) if Z[r][c] == "B"]
body = grid(30, 50, Z, 46, label="Zones (tracts)") + grid(300, 50, V, 46, label="Values (NDVI)") + op(560, 170, "→")
body += f"<rect x='590' y='110' width='90' height='40' rx='6' fill='{LIGHT}' stroke='{NAVY}'/>" + caption(635, 136, f"A: {sum(za)/len(za):.2f}", 16, NAVY, "middle", "700")
body += f"<rect x='590' y='170' width='90' height='40' rx='6' fill='{LIGHT}' stroke='{NAVY}'/>" + caption(635, 196, f"B: {sum(zb)/len(zb):.2f}", 16, NAVY, "middle", "700")
body += caption(30, 310, "A zonal function reads every cell that shares a zone value and writes one number per zone, not per cell.", 15)
body += caption(30, 334, "Zonal Statistics as Table gives the mean, min, max, range and count of NDVI for every zone at once.", 15)
svg("ra-zonal-idea.svg", 780, 350, body)
