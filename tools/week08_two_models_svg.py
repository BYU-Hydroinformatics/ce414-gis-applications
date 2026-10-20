"""Draw slides/week-08/images/fl-two-models.svg: Lab 7's two models as two boxes, each tool shown
with the lab pages' own tool icon (docs/assignments/lab-0N/images/icon-*.svg, inlined as nested
<svg> elements so the diagram is self-contained).

    python tools/week08_two_models_svg.py
"""
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "slides" / "week-08" / "images" / "fl-two-models.svg"
ICONS = {
    "fill": "lab-05/images/icon-fill.svg", "flowdir": "lab-05/images/icon-flow-direction.svg",
    "flowacc": "lab-05/images/icon-flow-accumulation.svg", "mask": "lab-04/images/icon-extract-by-mask.svg",
    "flowdist": "lab-07/images/icon-flow-distance.svg", "iterate": "lab-07/images/icon-iterate-field-values.svg",
    "con": "lab-06/images/icon-con.svg", "r2p": "lab-06/images/icon-raster-to-polygon.svg",
    "collect": "lab-06/images/icon-collect-values.svg", "merge": "lab-06/images/icon-merge.svg",
}


def icon(name, x, y, w=60, h=45):
    src = (ROOT / "docs" / "assignments" / ICONS[name]).read_text(encoding="utf-8")
    m = re.search(r"viewBox=['\"]([^'\"]+)['\"]", src)
    vb = m.group(1) if m else "0 0 120 90"
    inner = re.sub(r"^.*?<svg[^>]*>", "", src, count=1, flags=re.S)
    inner = re.sub(r"</svg>\s*$", "", inner, flags=re.S)
    inner = re.sub(r"<title>.*?</title>", "", inner, flags=re.S)
    return (f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{vb}" '
            f'preserveAspectRatio="xMidYMid meet">{inner}</svg>')


parts = []
P = parts.append
P('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 640" '
  'font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16">')
P("<title>Lab 7's two models: HAND Builder prepares the terrain once; Flood Loop floods it once per flow</title>")
P('<rect width="1200" height="640" fill="#ffffff"/>')
P('<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto">'
  '<path d="M0,0 L10,5 L0,10 z" fill="#4a5568"/></marker>'
  '<marker id="ab" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="10" markerHeight="10" orient="auto">'
  '<path d="M0,0 L10,5 L0,10 z" fill="#2b6cb0"/></marker></defs>')

PW, PH = 118, 92   # tool pill


def pill(x, y, label, ic=None, stroke="#4a5568", bold=False, fill="#ffffff"):
    P(f'<rect x="{x}" y="{y}" width="{PW}" height="{PH}" rx="10" fill="{fill}" stroke="{stroke}" '
      f'stroke-width="{2 if bold else 1.5}"/>')
    if ic:
        P(icon(ic, x + (PW - 60) / 2, y + 6))
    lines = label.split("|")
    y0 = (y + (PH - 14 * len(lines)) / 2 + 12) if not ic else y + 64
    weight = ' font-weight="700"' if bold else ""
    for i, ln in enumerate(lines):
        P(f'<text x="{x + PW / 2}" y="{y0 + i * 14}" text-anchor="middle" font-size="12.5" '
          f'fill="#1a202c"{weight}>{ln}</text>')


def data(x, y, label, fill="#cfe3f7", stroke="#2b6cb0", w=118, h=44):
    P(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="{fill}" stroke="{stroke}"/>')
    lines = label.split("|")
    y0 = y + h / 2 + (5 if len(lines) == 1 else -2)
    for i, ln in enumerate(lines):
        P(f'<text x="{x + w / 2}" y="{y0 + i * 14}" text-anchor="middle" font-size="12.5" fill="#1a202c">{ln}</text>')


def arrow(x1, y1, x2, y2, color="#4a5568", width=2, dash=None, marker="a"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    P(f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{color}" stroke-width="{width}" fill="none" '
      f'marker-end="url(#{marker})"{d}/>')


def path(d, color="#4a5568", width=2, dash="5 4", marker="a"):
    P(f'<path d="{d}" stroke="{color}" stroke-width="{width}" fill="none" stroke-dasharray="{dash}" '
      f'marker-end="url(#{marker})"/>')


def text(x, y, s, size=12.5, color="#4a5568", anchor="start", bold=False):
    weight = ' font-weight="700"' if bold else ""
    P(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{color}"{weight}>{s}</text>')


# ---------------- Model 1 ----------------
P('<rect x="24" y="30" width="600" height="470" rx="16" fill="#f3f7fb" stroke="#2b6cb0" stroke-width="2.5"/>')
text(324, 66, "Model 1 — HAND Builder", 24, "#1a202c", "middle", True)
text(324, 92, "prepare the terrain · runs ONCE", 17, "#2b6cb0", "middle", True)
# row 1: DEM -> Fill -> Flow Direction -> Flow Accumulation
data(44, 136, "Provo_DEM.tif")
pill(190, 112, "Fill", "fill")
pill(336, 112, "Flow|Direction", "flowdir")
pill(482, 112, "Flow|Accumulation", "flowacc")
arrow(162, 158, 188, 158)
arrow(308, 158, 334, 158)
arrow(454, 158, 480, 158)
# threshold -> stream cells
data(482, 236, "Threshold|2,000 cells", fill="#fde68a", stroke="#b7791f")
arrow(541, 204, 541, 234)
text(470, 300, "Raster Calculator: cells draining", anchor="end")
text(470, 316, "more than the threshold are stream", anchor="end")
# row 2: River -> Buffer -> Extract by Mask -> Flow Distance
data(44, 362, "Provo_River")
pill(190, 338, "Buffer|30 m corridor")
pill(336, 338, "Extract|by Mask", "mask")
pill(482, 338, "Flow Distance|(Vertical)", "flowdist", stroke="#c05621", bold=True)
arrow(162, 384, 188, 384)
arrow(308, 384, 334, 384)
arrow(454, 384, 480, 384)
path("M541,280 L541,300 L420,300 L420,336")          # stream cells into Extract by Mask
path("M249,204 L249,320 L470,320 L470,336")          # Filled_DEM (and Flow_Direction) into Flow Distance
text(262, 262, "Filled_DEM and", 12)
text(262, 277, "Flow_Direction too", 12)
# HAND output
P('<ellipse cx="672" cy="384" rx="46" ry="30" fill="#c6f6d5" stroke="#2f855a" stroke-width="2.5"/>')
text(672, 381, "HAND", 19, "#22543d", "middle", True)
text(672, 398, "height above river", 10.5, "#22543d", "middle")
arrow(600, 384, 624, 384, color="#2b6cb0", width=3, marker="ab")
text(324, 470, "Fill, Flow Direction, Flow Accumulation, Flow Distance: the slow part, about a minute", 15, anchor="middle")

# ---------------- Model 2 ----------------
P('<rect x="740" y="30" width="436" height="470" rx="16" fill="#fff7f0" stroke="#c05621" stroke-width="2.5"/>')
text(958, 66, "Model 2 — Flood Loop", 24, "#1a202c", "middle", True)
text(958, 92, "run the floods · one pass per flow", 17, "#c05621", "middle", True)
data(760, 136, "Stage_Table|five h values", fill="#fbd9c2", stroke="#c05621")
pill(906, 112, "Iterate|Field Values", "iterate", stroke="#c05621", bold=True)
pill(1040, 112, "Con: HAND ≤ h", "con")
arrow(878, 158, 904, 158)
arrow(1024, 158, 1038, 158)
pill(760, 250, "Raster to|Polygon", "r2p")
pill(906, 250, "Calculate Field|(stamp h)")
pill(1040, 250, "Collect|Values", "collect")
path("M1099,204 L1099,226 L819,226 L819,248", dash="")
arrow(878, 296, 904, 296)
arrow(1024, 296, 1038, 296)
pill(906, 376, "Merge", "merge")
path("M1099,342 L1099,360 L965,360 L965,374", dash="")
# loop bracket
P('<path d="M748,104 L1168,104 L1168,350 L748,350 Z" stroke="#c05621" stroke-width="1.5" fill="none" '
  'stroke-dasharray="5 4"/>')
text(756, 366, "inside the loop: runs 5 times, once per h", 12.5, "#c05621", bold=True)
# HAND into Con
P('<path d="M718,372 C740,300 760,120 1038,140" stroke="#2b6cb0" stroke-width="3" fill="none" '
  'marker-end="url(#ab)" stroke-dasharray="7 5"/>')
text(800, 118, "HAND: Model 2's input", 12, "#2b6cb0", bold=True)
# Floods output
P('<ellipse cx="1090" cy="422" rx="60" ry="28" fill="#c6f6d5" stroke="#2f855a" stroke-width="2.5"/>')
text(1090, 419, "Floods", 19, "#22543d", "middle", True)
text(1090, 436, "5 polygons, 10- to 500-yr", 10.5, "#22543d", "middle")
arrow(1024, 422, 1028, 422)
text(958, 470, "five Cons, five polygons: under a minute in all", 15, anchor="middle")

text(600, 560, "Prepare once. Flood many times.", 20, "#1a202c", "middle", True)
text(600, 590, "Tool icons are the lab pages' own (Labs 4 to 7).", 14, anchor="middle")
P("</svg>")
OUT.write_text("\n".join(parts), encoding="utf-8")
print(OUT, OUT.stat().st_size)
