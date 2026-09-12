#!/usr/bin/env python3
"""Draw the model-diagram rules figure for Week 2, Part B.

    python3 tools/week02_model_rules_svg.py

Writes slides/week-02/images/mbb-model-rules.svg.

These are the rules Dan wrote on the board while teaching Part B in Fall 2026, drawn so the class
can see them while they sketch their cookie. The convention on the board was the plain flowchart
one — oval for data, rectangle for tool — not ArcGIS Pro's own element style, which rounds both.
Keep it that way: the point of the board version is that the shape alone tells you which is which.
"""
from pathlib import Path

OUT = (Path(__file__).resolve().parent.parent / "slides" / "week-02" / "images"
       / "mbb-model-rules.svg")

NAVY = "#002e5d"
DATA_FILL, DATA_EDGE, DATA_INK = "#bfd7ee", "#4a7fb5", "#12314f"
TOOL_FILL, TOOL_EDGE, TOOL_INK = "#f6e6a8", "#b99a24", "#5c4a06"
BAD = "#c0392b"
MUTED = "#5a6472"


def oval(x, y, label, w=124, h=54):
    return (f'<ellipse cx="{x}" cy="{y}" rx="{w/2}" ry="{h/2}" fill="{DATA_FILL}" '
            f'stroke="{DATA_EDGE}" stroke-width="2.5"/>'
            f'<text x="{x}" y="{y + 7}" text-anchor="middle" font-size="19" font-weight="700" '
            f'fill="{DATA_INK}">{label}</text>')


def box(x, y, label, w=132, h=54):
    return (f'<rect x="{x - w/2}" y="{y - h/2}" width="{w}" height="{h}" rx="3" '
            f'fill="{TOOL_FILL}" stroke="{TOOL_EDGE}" stroke-width="2.5"/>'
            f'<text x="{x}" y="{y + 7}" text-anchor="middle" font-size="19" font-weight="700" '
            f'fill="{TOOL_INK}">{label}</text>')


def arrow(x0, x1, y, bad=False):
    c = BAD if bad else "#4b5563"
    return (f'<line x1="{x0}" y1="{y}" x2="{x1 - 13}" y2="{y}" stroke="{c}" stroke-width="4"/>'
            f'<polygon points="{x1},{y} {x1 - 15},{y - 9} {x1 - 15},{y + 9}" fill="{c}"/>')


def cross(x, y, r=17):
    return (f'<g stroke="{BAD}" stroke-width="5" stroke-linecap="round">'
            f'<line x1="{x - r}" y1="{y - r}" x2="{x + r}" y2="{y + r}"/>'
            f'<line x1="{x + r}" y1="{y - r}" x2="{x - r}" y2="{y + r}"/></g>')


def main():
    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 360" width="980" height="360" '
         'font-family="Segoe UI, Avenir Next, Helvetica, Arial, sans-serif" role="img" '
         'aria-label="Oval means data, rectangle means tool. A valid chain runs data to tool to '
         'data. Tool into tool and data into data are both crossed out.">']

    # ---- the two shapes and what they mean -------------------------------------
    p.append(f'<text x="26" y="34" font-size="21" font-weight="700" fill="{NAVY}">Shape tells you which</text>')
    p.append(oval(112, 92, "DATA"))
    p.append(f'<text x="190" y="86" font-size="18" font-weight="600" fill="{MUTED}">a <tspan font-style="italic">noun</tspan></text>')
    p.append(f'<text x="190" y="109" font-size="16" fill="{MUTED}">flour, dough, cookies</text>')
    p.append(box(112, 178, "TOOL"))
    p.append(f'<text x="190" y="172" font-size="18" font-weight="600" fill="{MUTED}">an <tspan font-style="italic">action verb</tspan></text>')
    p.append(f'<text x="190" y="195" font-size="16" fill="{MUTED}">mix, bake, cool</text>')

    # ---- the one legal pattern -------------------------------------------------
    p.append(f'<line x1="392" y1="20" x2="392" y2="340" stroke="#c3ccd8" stroke-width="2"/>')
    p.append(f'<text x="424" y="34" font-size="21" font-weight="700" fill="{NAVY}">The only legal chain</text>')
    p.append(oval(494, 92, "DATA"))
    p.append(arrow(558, 606, 92))
    p.append(box(674, 92, "TOOL"))
    p.append(arrow(742, 790, 92))
    p.append(oval(854, 92, "DATA"))
    p.append(f'<text x="674" y="140" text-anchor="middle" font-size="16" fill="{MUTED}">'
             'Start and end with data. One direction only.</text>')

    # ---- the two illegal ones --------------------------------------------------
    p.append(f'<text x="424" y="196" font-size="21" font-weight="700" fill="{BAD}">Never</text>')
    p.append(box(510, 250, "TOOL"))
    p.append(arrow(578, 646, 250, bad=True))
    p.append(box(714, 250, "TOOL"))
    p.append(cross(612, 250))
    p.append(oval(510, 318, "DATA"))
    p.append(arrow(574, 646, 318, bad=True))
    p.append(oval(714, 318, "DATA"))
    p.append(cross(612, 318))
    p.append(f'<text x="796" y="256" font-size="16" fill="{MUTED}">a tool cannot feed a tool</text>')
    p.append(f'<text x="796" y="324" font-size="16" fill="{MUTED}">data cannot feed data</text>')

    p.append("</svg>")
    OUT.write_bytes("\n".join(p).encode("utf-8"))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
