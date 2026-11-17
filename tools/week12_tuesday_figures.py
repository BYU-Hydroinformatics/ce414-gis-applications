"""Week 12 Tuesday (network-analysis-a.md) teaching figures added November 16, 2026.

    python tools/week12_tuesday_figures.py      (any Python with matplotlib)

Writes into slides/week-12/images/:
  na-gap-dead-end.png     a street digitized 2 m short of the one it should meet (made-up streets)
  na-roads-table.png      rows of Lab 11's Roads attribute table, key fields highlighted
  na-oneway-quiz.png      the one-way question: the wrong way against the legal way around
  na-build-flow.png       how a road layer becomes a network dataset

The table rows are real: read with arcpy from Lab 11's package (FireResponse.gdb, Network/Roads),
the segments nearest Provo Fire and Rescue Station 21 plus the longest one-way I-15 segment.
The arithmetic in the table note was checked against the stored F_T_IMP_MIN of OBJECTID 18213:
147.0 m / (25 mph x 1,609.34 m) x 60 = 0.219 min, x 1.5 = 0.329 min.
The one-way diagram uses round illustrative minutes, not a solve.
"""

import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle, Rectangle

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "slides" / "week-12" / "images"
plt.rcParams.update({"font.family": ["Segoe UI", "Arial", "DejaVu Sans"]})
NAVY, BLUE, ORANGE, RED, GRAY, GREEN = "#002e5d", "#0062b8", "#e8792b", "#c8102e", "#8a94a3", "#2e8b57"
STREET = "#3d5a80"


def junction(ax, x, y, r=0.11, color=STREET):
    ax.add_patch(Circle((x, y), r, facecolor="white", edgecolor=color, lw=2.2, zorder=5))


# ------------------------------------------------------------------ gap
def gap_figure():
    fig = plt.figure(figsize=(7.2, 10.2), dpi=200)
    ax = fig.add_axes([0.0, 0.37, 1.0, 0.56]); zx = fig.add_axes([0.08, 0.01, 0.84, 0.31])
    ax.set_xlim(0, 10); ax.set_ylim(0, 9); ax.set_aspect("equal"); ax.axis("off")
    ax.plot([6, 6], [0.6, 8.4], color=STREET, lw=6, solid_capstyle="round")
    for y in (1.5, 7.5):
        ax.plot([0.6, 9.4], [y, y], color=STREET, lw=6, solid_capstyle="round")
    ax.plot([6.0, 9.4], [4.5, 4.5], color=STREET, lw=6, solid_capstyle="round")
    ax.plot([0.6, 5.62], [4.5, 4.5], color=ORANGE, lw=6, solid_capstyle="butt")
    for x, y in [(6, 1.5), (6, 7.5), (6, 4.5)]:
        junction(ax, x, y)
    junction(ax, 5.62, 4.5, color=ORANGE)
    ax.text(3.1, 4.85, "300 North", ha="center", fontsize=14, color=ORANGE, weight="bold")
    ax.text(6.3, 8.35, "500 West", ha="left", fontsize=14, color=NAVY, weight="bold")
    ax.text(7.9, 6.6, "connected:\none shared junction", ha="center", fontsize=11, color=NAVY)
    ax.add_patch(Rectangle((5.25, 4.05), 1.1, 0.9, fill=False, ec=RED, lw=2, ls="--"))
    ax.annotate("", xy=(6.6, -0.6), xytext=(6.1, 4.0), annotation_clip=False,
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.8, ls="--"))
    zx.set_xlim(0, 4); zx.set_ylim(0, 2.4); zx.axis("off")
    zx.add_patch(Rectangle((0, 0), 4, 2.4, fill=False, ec=RED, lw=2, ls="--"))
    zx.plot([0.1, 2.35], [1.2, 1.2], color=ORANGE, lw=10, solid_capstyle="butt")
    zx.plot([3.0, 3.0], [0.05, 2.35], color=STREET, lw=10)
    zx.add_patch(Circle((2.35, 1.2), 0.13, facecolor="white", edgecolor=ORANGE, lw=2.5, zorder=5))
    zx.add_patch(Circle((3.0, 1.2), 0.13, facecolor="white", edgecolor=STREET, lw=2.5, zorder=5))
    zx.annotate("", xy=(2.45, 0.75), xytext=(2.9, 0.75), arrowprops=dict(arrowstyle="<->", color=RED, lw=2))
    zx.text(2.3, 0.35, "2 m gap", ha="right", fontsize=14, color=RED, weight="bold")
    zx.text(0.15, 1.9, "Zoomed in: two junctions, not one", fontsize=12, color=NAVY, weight="bold")
    fig.text(0.5, 0.965, "The map seems to show a corner.\nDoes the network have one?", ha="center", va="center", fontsize=16,
             color=NAVY, weight="bold")
    fig.savefig(IMG / "na-gap-dead-end.png", facecolor="white", bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


# ------------------------------------------------------------------ attribute table
ROWS = [  # OBJECTID, FULLNAME, CARTOCODE, ONEWAY, SPEED_LMT, Shape_Length, F_T_IMP_MIN, T_F_IMP_MIN
    (18213, "100 S", "10", "0", 25, 147.00, 0.329, 0.329),
    (31257, "300 W", "11", "0", 25, 153.42, 0.343, 0.343),
    (30991, "CENTER ST", "10", "0", 25, 149.97, 0.336, 0.336),
    (27050, "500 W", "3", "0", 40, 155.41, 0.217, 0.217),
    (30974, "I-15 NB FWY", "1", "1", 65, 4418.55, 3.042, 304.188),
]
COLS = ["OBJECTID", "FULLNAME", "CARTOCODE", "ONEWAY", "SPEED_LMT", "Shape_Length", "F_T_IMP_MIN", "T_F_IMP_MIN"]
KEY = {"ONEWAY": "#fde7c8", "SPEED_LMT": "#dbe9f7", "Shape_Length": "#dbe9f7", "F_T_IMP_MIN": "#d8f0de", "T_F_IMP_MIN": "#d8f0de"}


def table_figure():
    widths = [1.15, 1.6, 1.25, 1.0, 1.25, 1.45, 1.45, 1.45]
    xs = [0]
    for w in widths: xs.append(xs[-1] + w)
    H = 0.55
    fig, ax = plt.subplots(figsize=(12.6, 6.4), dpi=200)
    ax.set_xlim(-0.1, xs[-1] + 0.1); ax.set_ylim(-5.2, 1.0); ax.axis("off")
    for j, c in enumerate(COLS):
        ax.add_patch(Rectangle((xs[j], 0), widths[j], H, facecolor=NAVY if c not in KEY else BLUE, ec="white"))
        ax.text(xs[j] + widths[j] / 2, H / 2, c, ha="center", va="center", color="white", fontsize=11, weight="bold")
    for i, row in enumerate(ROWS):
        y = -(i + 1) * H
        for j, (c, v) in enumerate(zip(COLS, row)):
            fc = KEY.get(c, "white" if i % 2 == 0 else "#f3f5f8")
            ax.add_patch(Rectangle((xs[j], y), widths[j], H, facecolor=fc, ec="#c9d1db", lw=0.8))
            txt = f"{v:,.2f}" if c == "Shape_Length" else (f"{v:.3f}" if c.endswith("MIN") else str(v))
            ax.text(xs[j] + (widths[j] - 0.1 if isinstance(v, (int, float)) else 0.1), y + H / 2, txt,
                    ha="right" if isinstance(v, (int, float)) else "left", va="center", fontsize=11.5, color="#22262e")
    # highlight the I-15 pair
    yI = -5 * H
    ax.add_patch(FancyBboxPatch((xs[6] + 0.03, yI + 0.04), widths[6] + widths[7] - 0.06, H - 0.08,
                                boxstyle="round,pad=0.02,rounding_size=0.1", fill=False, ec=RED, lw=2.6))
    # notes
    notes = [
        (xs[3] + widths[3] / 2, "ONEWAY: 0 two-way, 1 one-way\nin the digitized direction", ORANGE, -3.45),
        (xs[5] - 0.1, "SPEED_LMT (mph) and Shape_Length (m):\nwhat the minutes are computed from", BLUE, -4.25),
        (xs[7] - 0.2, "F_T = minutes along the digitized direction,\nT_F = against it. On one-way I-15: 3.04 vs 304", RED, -3.45),
    ]
    for x, text, col, ty in notes:
        ax.annotate(text, xy=(x, -5 * H - 0.02), xytext=(x, ty), ha="center", va="top", fontsize=11.5, color=col,
                    weight="bold", arrowprops=dict(arrowstyle="-|>", color=col, lw=1.8))
    ax.text(0, 0.75, "Lab 11's Roads attribute table: five of its 41,460 rows", fontsize=13.5, color=NAVY, weight="bold")
    ax.text(0, -5.15, "100 S: 147.0 m ÷ 25 mph (40,234 m/h) = 0.00365 h × 60 = 0.219 min;  × 1.5 for a surface street = 0.329 min",
            fontsize=11.5, color="#22262e")
    fig.savefig(IMG / "na-roads-table.png", facecolor="white", bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


# ------------------------------------------------------------------ one-way quiz diagram
def oneway_figure():
    fig, ax = plt.subplots(figsize=(7.0, 6.4), dpi=200)
    ax.set_xlim(-0.6, 4.6); ax.set_ylim(-0.9, 4.2); ax.set_aspect("equal"); ax.axis("off")
    for y in (1, 3):
        ax.plot([-0.4, 4.4], [y, y], color="#b7c3d0", lw=7, solid_capstyle="round", zorder=1)
    for x in (0, 2, 4):
        ax.plot([x, x], [-0.4, 3.9], color="#b7c3d0", lw=7, solid_capstyle="round", zorder=1)
    # the one-way block between A (station) and B (fire); its arrows point toward A
    for xa in (1.45, 0.95):
        ax.plot([xa, xa - 0.22, xa], [1.13, 1.0, 0.87], color="white", lw=3.2, zorder=3, solid_capstyle="round")
    ax.plot([0, 2], [1, 1], color=ORANGE, lw=13, zorder=2)
    # wrong-way option
    ax.annotate("", xy=(1.9, 0.72), xytext=(0.1, 0.72),
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=2.4, ls="--"))
    ax.text(1.0, 0.25, "against the arrow\n0.33 × 100 = 33 min", ha="center", va="top", fontsize=11, color=RED, weight="bold")
    # around the block option: A (0,1) up to (0,3), right to (2,3), down to (2,1)
    ax.plot([0.12, 0.12, 1.88, 1.88], [1.15, 2.88, 2.88, 1.15], color=GREEN, lw=3.2, zorder=4)
    ax.annotate("", xy=(1.88, 1.13), xytext=(1.88, 1.6), arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=3.2), zorder=4)
    ax.text(1.0, 3.25, "around the block: three blocks\nand two turns, about 1.5 min", ha="center", va="bottom",
            fontsize=11, color=GREEN, weight="bold")
    for (x, y, lab, col) in ((0, 1, "A", NAVY), (2, 1, "B", RED)):
        ax.add_patch(Circle((x, y), 0.26, facecolor=col, edgecolor="white", lw=2, zorder=6))
        ax.text(x, y, lab, ha="center", va="center", color="white", fontsize=14, weight="bold", zorder=7)
    ax.text(-0.45, 1.35, "station", fontsize=10.5, color=NAVY, ha="left")
    ax.text(2.25, 1.32, "fire", fontsize=10.5, color=RED, ha="left")
    ax.text(1.0, -0.85, "One-way block (orange): 0.33 min the legal way, toward A", ha="center", fontsize=10.5, color=ORANGE)
    fig.savefig(IMG / "na-oneway-quiz.png", facecolor="white", bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


# ------------------------------------------------------------------ build flow
def build_figure():
    fig, ax = plt.subplots(figsize=(13, 3.4), dpi=200)
    ax.set_xlim(0, 13); ax.set_ylim(0, 3.4); ax.axis("off")
    boxes = [
        (0.1, "Roads\nfeature class", "lines, one per street\nsegment, with fields:\nspeed, one-way, minutes", "#e8eef5", NAVY),
        (3.35, "Create Network\nDataset", "choose the sources,\nconnectivity rules,\ncosts read from fields,\nturn delays", "#fff3e6", ORANGE),
        (6.6, "Build\nNetwork", "ArcGIS Pro walks every\nsegment and writes a\njunction wherever ends\n(or vertices) meet", "#fff3e6", ORANGE),
        (9.85, "Network\ndataset", "edges + junctions +\ncosts: what the\nsolvers route on", "#e7f4ec", GREEN),
    ]
    for x, title, body, fc, ec in boxes:
        ax.add_patch(FancyBboxPatch((x, 0.1), 3.0, 3.2, boxstyle="round,pad=0.02,rounding_size=0.18", fc=fc, ec=ec, lw=2.5))
        ax.text(x + 1.5, 2.75, title, ha="center", va="center", fontsize=15, weight="bold", color=ec)
        ax.text(x + 1.5, 1.15, body, ha="center", va="center", fontsize=12, color="#22262e", linespacing=1.35)
    for x in (3.1, 6.35, 9.6):
        ax.annotate("", xy=(x + 0.27, 1.7), xytext=(x - 0.02, 1.7),
                    arrowprops=dict(arrowstyle="-|>,head_width=0.6,head_length=0.8", color=NAVY, lw=3))
    fig.savefig(IMG / "na-build-flow.png", facecolor="white", bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


if __name__ == "__main__":
    gap_figure(); table_figure(); oneway_figure(); build_figure()
    print("wrote na-gap-dead-end, na-roads-table, na-oneway-quiz, na-build-flow")
