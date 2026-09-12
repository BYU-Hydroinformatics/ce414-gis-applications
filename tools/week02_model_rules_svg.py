#!/usr/bin/env python3
"""Draw the model-diagram rules figure for Week 2, Part B.

    python3 tools/week02_model_rules_svg.py

Writes slides/week-02/images/mbb-model-rules.svg.

The rules come from the board Dan used while teaching Part B in Fall 2026. The figure deliberately
shows TWO shape conventions side by side, because the rule is not "oval means data" — it is "pick a
pair and stay consistent". Ovals and rectangles are what Bolstad's textbook uses and what older
ArcGIS used; ArcGIS Pro today draws data as rounded rectangles and tools as squared-off ones.
A student who invents a third pair and holds to it has followed the rule.
"""
from pathlib import Path

OUT = (Path(__file__).resolve().parent.parent / "slides" / "week-02" / "images"
       / "mbb-model-rules.svg")

NAVY = "#002e5d"
DATA_FILL, DATA_EDGE, DATA_INK = "#bfd7ee", "#4a7fb5", "#12314f"
TOOL_FILL, TOOL_EDGE, TOOL_INK = "#f6e6a8", "#b99a24", "#5c4a06"
BAD = "#c0392b"
MUTED = "#5a6472"

W, H = 118, 50


def label(x, y, text, size=18, fill=None, weight="700", anchor="start", italic=False):
    style = ' font-style="italic"' if italic else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}" fill="{fill or MUTED}"{style}>{text}</text>')


def shape(kind, x, y, text, w=W, h=H):
    """kind: oval | rect | round (rounded rectangle) | square (sharp rectangle)."""
    ink = DATA_INK if kind in ("oval", "round") else TOOL_INK
    fill = DATA_FILL if kind in ("oval", "round") else TOOL_FILL
    edge = DATA_EDGE if kind in ("oval", "round") else TOOL_EDGE
    if kind == "oval":
        body = (f'<ellipse cx="{x}" cy="{y}" rx="{w/2 + 6}" ry="{h/2 - 4}" fill="{fill}" '
                f'stroke="{edge}" stroke-width="2.5"/>')
    else:
        r = {"round": 12, "rect": 3, "square": 0}[kind]
        body = (f'<rect x="{x - w/2}" y="{y - h/2}" width="{w}" height="{h}" rx="{r}" '
                f'fill="{fill}" stroke="{edge}" stroke-width="2.5"/>')
    return body + (f'<text x="{x}" y="{y + 6}" text-anchor="middle" font-size="17" '
                   f'font-weight="700" fill="{ink}">{text}</text>')


def arrow(x0, x1, y, bad=False):
    c = BAD if bad else "#4b5563"
    return (f'<line x1="{x0}" y1="{y}" x2="{x1 - 13}" y2="{y}" stroke="{c}" stroke-width="4"/>'
            f'<polygon points="{x1},{y} {x1 - 15},{y - 9} {x1 - 15},{y + 9}" fill="{c}"/>')


def cross(x, y, r=16):
    return (f'<g stroke="{BAD}" stroke-width="5" stroke-linecap="round">'
            f'<line x1="{x - r}" y1="{y - r}" x2="{x + r}" y2="{y + r}"/>'
            f'<line x1="{x + r}" y1="{y - r}" x2="{x - r}" y2="{y + r}"/></g>')


def main():
    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 372" width="1000" '
         'height="372" font-family="Segoe UI, Avenir Next, Helvetica, Arial, sans-serif" '
         'role="img" aria-label="Two shape conventions, both acceptable: ovals and rectangles as '
         'in the textbook, or rounded and squared rectangles as in ArcGIS Pro. A legal chain runs '
         'data to tool to data. Tool into tool and data into data are crossed out.">']

    # ---- left: what the shapes mean, and that the pair is yours to pick ------
    p.append(label(24, 30, "Pick a pair, then stay consistent", 21, NAVY))

    p.append(label(24, 92, "DATA", 17, DATA_INK, "700"))
    p.append(shape("oval", 150, 86, "flour"))
    p.append(label(228, 92, "or", 16, MUTED, "400", "middle"))
    p.append(shape("round", 310, 86, "flour"))
    p.append(label(24, 126, "a noun", 15, MUTED, "400", italic=True))

    p.append(label(24, 196, "TOOL", 17, TOOL_INK, "700"))
    p.append(shape("square", 150, 190, "mix"))
    p.append(label(24, 236, "an action verb", 15, MUTED, "400", italic=True))

    p.append(label(24, 292, "The oval is your textbook's. ArcGIS Pro rounds a", 15, MUTED, "400"))
    p.append(label(24, 314, "rectangle instead, and squares off its tools. Either", 15, MUTED, "400"))
    p.append(label(24, 336, "is fine — so is a pair you invent, if you never swap them.", 15, MUTED, "400"))

    # ---- right: the one legal pattern, and the two that are not ---------------
    p.append('<line x1="386" y1="18" x2="386" y2="352" stroke="#c3ccd8" stroke-width="2"/>')
    p.append(label(418, 30, "The only legal chain", 21, NAVY))
    p.append(shape("oval", 482, 86, "DATA"))
    p.append(arrow(543, 594, 86))
    p.append(shape("rect", 658, 86, "TOOL"))
    p.append(arrow(719, 770, 86))
    p.append(shape("oval", 834, 86, "DATA"))
    p.append(label(658, 132, "Start and end with data. One direction only.", 15, MUTED, "400",
                   "middle"))

    p.append(label(418, 196, "Never", 21, BAD))
    p.append(shape("rect", 498, 248, "TOOL"))
    p.append(arrow(560, 632, 248, bad=True))
    p.append(shape("rect", 694, 248, "TOOL"))
    p.append(cross(596, 248))
    p.append(label(768, 254, "a tool cannot feed a tool", 15, MUTED, "400"))

    p.append(shape("oval", 498, 320, "DATA"))
    p.append(arrow(560, 632, 320, bad=True))
    p.append(shape("oval", 694, 320, "DATA"))
    p.append(cross(596, 320))
    p.append(label(768, 326, "data cannot feed data", 15, MUTED, "400"))

    p.append("</svg>")
    OUT.write_bytes("\n".join(p).encode("utf-8"))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
