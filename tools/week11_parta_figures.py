r"""Figures for the Week 11 Tuesday deck (slides/week-11/least-cost-path.md).

  lcp-workflow.png        the least-cost path workflow as five boxes, with Lab 10's tools named
  lcp-hand-grid-ask.png   a 5 x 5 cost surface with a source S and a destination D, for working by hand
  lcp-hand-grid-answer.png   the same grid solved: accumulated cost in every cell, the back direction
                          as an arrow, and the cheapest path from D home to S

The hand grid uses a classroom simplification, stated on the slide: moves go up, down, left or
right only, and a move costs the cost of the cell you enter. The solution is an exact Dijkstra
search, and the script asserts that the cheapest path is unique so the answer slide has one right
answer. ArcGIS Pro's Distance Accumulation also allows diagonal moves (at about 1.414 times the
cost) and other angles; Thursday's deck covers that on Lab 10's data.

Writes slides/week-11/images/lcp-*.png and tools/week11_parta_numbers.json. Any Python with
numpy and matplotlib.
"""
import heapq, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(REPO, "slides", "week-11", "images")
NAVY, BLUE, RED, GRAY, GREEN = "#002E5D", "#0062b8", "#c8102e", "#6b7280", "#2e7d32"
plt.rcParams.update({"font.size": 14, "font.family": "DejaVu Sans"})


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=150, bbox_inches="tight", pad_inches=0.1, facecolor="white")
    plt.close(fig)


# ------------------------------------------------------------------ workflow
steps = [("Input layers", "slope, roads, cities,\npower lines, rivers, lakes"),
         ("Reclassify", "each layer to a\n1–10 score (10 = avoid)"),
         ("Raster\nCalculator", "combine scores into\none cost surface"),
         ("Distance\nAccumulation", "from the source: accumulated\ncost + back direction"),
         ("Optimal Path\nAs Line", "from the destination,\nfollow the arrows home")]
fig, ax = plt.subplots(figsize=(15, 3.6))
w, h, gap = 3.0, 2.1, 0.45
for i, (head, body) in enumerate(steps):
    x = i * (w + gap)
    col = BLUE if i < 3 else GREEN
    ax.add_patch(FancyBboxPatch((x, 0), w, h, boxstyle="round,pad=0.04,rounding_size=0.15",
                                fc="white", ec=col, lw=2.5))
    ax.text(x + w / 2, h - 0.55, f"{i + 1}. {head}", ha="center", va="center", fontsize=14,
            fontweight="bold", color=col)
    ax.text(x + w / 2, 0.5, body, ha="center", va="center", fontsize=11.5, color="#333")
    if i < len(steps) - 1:
        ax.add_patch(FancyArrowPatch((x + w + 0.04, h / 2), (x + w + gap - 0.04, h / 2),
                                     arrowstyle="-|>", mutation_scale=20, color=GRAY, lw=2))
ax.annotate("", (0, -0.35), (3 * w + 2 * gap, -0.35), arrowprops=dict(arrowstyle="<->", color=BLUE, lw=1.5))
ax.text((3 * w + 2 * gap) / 2, -0.62, "build the cost surface: most of the work, and all of the judgment",
        ha="center", va="center", color=BLUE, fontsize=12.5)
x3 = 3 * (w + gap)
ax.annotate("", (x3, -0.35), (x3 + 2 * w + gap, -0.35), arrowprops=dict(arrowstyle="<->", color=GREEN, lw=1.5))
ax.text(x3 + (2 * w + gap) / 2, -0.62, "route: two tools", ha="center", va="center", color=GREEN, fontsize=12.5)
ax.set_xlim(-0.2, 5 * w + 4 * gap + 0.2); ax.set_ylim(-0.9, h + 0.15); ax.set_aspect("equal"); ax.axis("off")
save(fig, "lcp-workflow.png")

# ------------------------------------------------------------------ hand grid
C = np.array([[1, 1, 3, 9, 1],
              [1, 9, 3, 9, 1],
              [1, 9, 1, 1, 1],
              [1, 9, 9, 9, 1],
              [2, 2, 2, 1, 1]], float)
S, D = (0, 0), (0, 4)
n, m = C.shape
dist = np.full(C.shape, np.inf); dist[S] = 0
back = {}
pq = [(0.0, S)]
while pq:
    d, (r, c) = heapq.heappop(pq)
    if d > dist[r, c]: continue
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        rr, cc = r + dr, c + dc
        if 0 <= rr < n and 0 <= cc < m:
            nd = d + C[rr, cc]
            if nd < dist[rr, cc] - 1e-9:
                dist[rr, cc] = nd; back[(rr, cc)] = (r, c); heapq.heappush(pq, (nd, (rr, cc)))


def n_best(cell):
    """Number of distinct cheapest paths from S to cell (ties make a hand exercise ambiguous)."""
    if cell == S: return 1
    r, c = cell; k = 0
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        p = (r + dr, c + dc)
        if 0 <= p[0] < n and 0 <= p[1] < m and abs(dist[p] + C[cell] - dist[cell]) < 1e-9:
            k += n_best(p)
    return k


assert n_best(D) == 1, "the cheapest path to D is not unique"
path = [D]
while path[-1] != S: path.append(back[path[-1]])
straight = float(sum(C[0, 1:5]))
NUM = {"cost": C.astype(int).tolist(), "source": S, "destination": D,
       "accumulated": dist.astype(int).tolist(), "path": path[::-1],
       "path_cost": int(dist[D]), "straight_across_top_cost": int(straight),
       "path_cells_moved": len(path) - 1}


def draw_grid(ax, values, title, path=None, arrows=False):
    for r in range(n):
        for c in range(m):
            v = C[r, c]
            shade = {1: "#ffffff", 2: "#e8eef6", 3: "#c9d6e6", 9: "#5b7aa0"}[int(v)]
            ax.add_patch(plt.Rectangle((c, n - 1 - r), 1, 1, fc=shade, ec="#333", lw=1.2))
            txt = values[r][c]
            ax.text(c + 0.5, n - 1 - r + 0.5, txt, ha="center", va="center", fontsize=20,
                    fontweight="bold", color="white" if v == 9 else NAVY)
    for (r, c), lab in ((S, "S"), (D, "D")):
        ax.text(c + 0.12, n - 1 - r + 0.86, lab, ha="left", va="top", fontsize=14, fontweight="bold", color=RED)
    if arrows:
        for (r, c), (pr, pc) in back.items():
            x0, y0 = c + 0.5, n - 1 - r + 0.5
            dx, dy = (pc - c), -(pr - r)
            ax.annotate("", (x0 + dx * 0.49, y0 + dy * 0.49), (x0 + dx * 0.27, y0 + dy * 0.27),
                        arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.8, mutation_scale=14))
    if path:
        xs = [c + 0.5 for r, c in path]; ys = [n - 1 - r + 0.5 for r, c in path]
        ax.plot(xs, ys, color=RED, lw=4, alpha=0.75, solid_capstyle="round", zorder=5)
    ax.set_xlim(-0.05, m + 0.05); ax.set_ylim(-0.05, n + 0.05); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, fontsize=15, color=NAVY)


fig, ax = plt.subplots(figsize=(6, 6.4))
draw_grid(ax, C.astype(int).tolist(), "Cost surface: the price of entering each cell")
save(fig, "lcp-hand-grid-ask.png")

fig, axs = plt.subplots(1, 2, figsize=(12.5, 6.6))
draw_grid(axs[0], C.astype(int).tolist(), f"Cheapest path S → D: total {int(dist[D])}", path=path[::-1])
draw_grid(axs[1], dist.astype(int).tolist(), "Accumulated cost, and the back direction", arrows=True)
save(fig, "lcp-hand-grid-answer.png")

with open(os.path.join(REPO, "tools", "week11_parta_numbers.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(NUM, f, indent=1)
print(json.dumps({k: NUM[k] for k in ("accumulated", "path", "path_cost", "straight_across_top_cost")}))
