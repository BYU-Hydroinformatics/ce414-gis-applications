"""Week 12 Thursday in-class activity: "Solve It by Hand", a one-page network worksheet.

Each student works alone on paper, in about fifteen minutes. A made-up neighborhood of twelve
junctions (A to L) and its streets, each labeled with its minutes: a fast arterial through the middle
(1 minute a block), local streets (3 minutes a block), one one-way street, and one street digitized
2 m short of its corner. Two fire stations. People live at each junction. The questions walk through
the three solvers of the Week 12 decks by hand:

  1. Fewest minutes from Station 1 to every junction (what Solve does: Dijkstra's spread).
  2. Service area: which junctions are within 4 minutes, and how many people are outside.
  3. The same 4 minutes as a circle at the arterial's speed: how many people does it wrongly cover.
  4. Closest facility: a fire at D; which station arrives first, and in how many minutes.
  5. Location-allocation: one more station at C, K or H; which brings the most people inside 4 minutes.

Every answer is computed here with Dijkstra and asserted, so the worksheet has exactly one right
answer to each question. The key goes to the PRIVATE repository (it is a graded activity):
../ce414-private/activities/week12-network-worksheet-key.md.

    python tools/week12_network_worksheet.py      (matplotlib)

Writes docs/handouts/network-worksheet.pdf (letter, one page), slides/week-12/images/nab-worksheet.png
(the network figure for the activity slide) and the private key.
"""

import heapq
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch

ROOT = pathlib.Path(__file__).resolve().parent.parent
PDF = ROOT / "docs" / "handouts" / "network-worksheet.pdf"
PNG = ROOT / "slides" / "week-12" / "images" / "nab-worksheet.png"
KEY = ROOT.parent / "ce414-private" / "activities" / "week12-network-worksheet-key.md"
plt.rcParams.update({"font.family": ["Segoe UI", "Arial", "DejaVu Sans"]})
NAVY, BLUE, ORANGE, RED, GRAY, GREEN = "#002e5d", "#0062b8", "#e8792b", "#c8102e", "#5b6770", "#2e8b57"

# Junctions on a 4 x 3 grid of blocks
POS = {"A": (0, 2), "B": (1, 2), "C": (2, 2), "D": (3, 2),
       "E": (0, 1), "F": (1, 1), "G": (2, 1), "H": (3, 1),
       "I": (0, 0), "J": (1, 0), "K": (2, 0), "L": (3, 0)}
PEOPLE = {"A": 60, "B": 90, "C": 120, "D": 80, "E": 40, "F": 150,
          "G": 130, "H": 70, "I": 50, "J": 110, "K": 150, "L": 90}
# Two-way streets (minutes). The middle row is the arterial. B-C is missing: the 2 m gap.
TWO_WAY = [("A", "B", 3), ("C", "D", 3),
           ("E", "F", 1), ("F", "G", 1), ("G", "H", 1),
           ("I", "J", 3), ("J", "K", 3), ("K", "L", 3),
           ("A", "E", 3), ("B", "F", 3), ("C", "G", 3), ("D", "H", 3),
           ("E", "I", 3), ("F", "J", 3), ("G", "K", 3)]
ONE_WAY = [("H", "L", 3)]          # H -> L only; against the arrow costs 100 times (UGRC's rule)
GAP = ("B", "C")
STATIONS = {"Station 1": "E", "Station 2": "L"}
CUTOFF = 4


def graph():
    g = {n: [] for n in POS}
    for a, b, m in TWO_WAY:
        g[a].append((b, m)); g[b].append((a, m))
    for a, b, m in ONE_WAY:
        g[a].append((b, m)); g[b].append((a, 100 * m))
    return g


def dijkstra(src):
    g, dist, pq = graph(), {src: 0}, [(0, src)]
    while pq:
        d, n = heapq.heappop(pq)
        if d > dist[n]:
            continue
        for m, w in g[n]:
            if d + w < dist.get(m, 1e9):
                dist[m] = d + w; heapq.heappush(pq, (d + w, m))
    return dist


# ---------------------------------------------------------------- answers
d1 = dijkstra("E")
covered = {n for n, d in d1.items() if d <= CUTOFF}
outside = sorted(set(POS) - covered)
people_out = sum(PEOPLE[n] for n in outside)
total = sum(PEOPLE.values())
d2 = dijkstra("L")
fire = "D"
cand = {c: {n for n, d in dijkstra(c).items() if d <= CUTOFF} & set(outside) for c in ("C", "K", "H")}
gain = {c: sum(PEOPLE[n] for n in s) for c, s in cand.items()}
best = max(gain, key=gain.get)

assert d1 == {"E": 0, "F": 1, "G": 2, "H": 3, "A": 3, "I": 3, "B": 4, "J": 4, "C": 5, "K": 5, "D": 6, "L": 6}, d1
assert outside == ["C", "D", "K", "L"] and people_out == 440 and total == 1140
assert d1[fire] == 6 and d2[fire] == 10 and d1[fire] < d2[fire]       # Station 1 wins despite the map
assert gain == {"C": 200, "K": 240, "H": 440} and best == "H"
assert sorted(gain.values()) == [200, 240, 440]                         # no ties


# ---------------------------------------------------------------- the network figure
def draw(ax, big=True):
    fs = 15 if big else 13
    for a, b, m in TWO_WAY + ONE_WAY:
        (x0, y0), (x1, y1) = POS[a], POS[b]
        art = m == 1
        ax.plot([x0, x1], [y0, y1], color=NAVY if art else "#8fa3b8", lw=7 if art else 4, solid_capstyle="round", zorder=1)
        xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
        dx, dy = (0, -0.14) if y0 == y1 else (0.15, 0)
        ax.text(xm + dx, ym + dy, f"{m} min", ha="center", va="center", fontsize=fs - 3, color=NAVY if art else GRAY,
                weight="bold" if art else "normal", zorder=3,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9))
    # one-way arrows on H -> L
    (x0, y0), (x1, y1) = POS["H"], POS["L"]
    for f in (0.35, 0.65):
        ax.add_patch(FancyArrowPatch((x0, y0 + (y1 - y0) * (f - 0.07)), (x0, y0 + (y1 - y0) * (f + 0.07)),
                                     arrowstyle="-|>,head_width=0.35,head_length=0.5", color=ORANGE, lw=2.5,
                                     mutation_scale=16, zorder=4))
    ax.text(x0 + 0.1, y1 + 0.22, "one-way,\nH to L only", fontsize=fs - 4, color=ORANGE, va="center", ha="left",
            weight="bold")
    # the gap B-C: two stubs that stop short
    (bx, by), (cx, cy) = POS[GAP[0]], POS[GAP[1]]
    ax.plot([bx, bx + 0.46], [by, by], color="#8fa3b8", lw=4, solid_capstyle="butt", zorder=1)
    ax.plot([cx - 0.44, cx], [cy, cy], color="#8fa3b8", lw=4, solid_capstyle="butt", zorder=1)
    ax.text((bx + cx) / 2, by - 0.13, "2 m gap", ha="center", va="top", fontsize=fs - 4, color=RED, weight="bold")
    for n, (x, y) in POS.items():
        st = [s for s, v in STATIONS.items() if v == n]
        ax.add_patch(Circle((x, y), 0.16, fc=RED if st else "white", ec=NAVY, lw=2, zorder=5))
        ax.text(x, y, n, ha="center", va="center", fontsize=fs, weight="bold", color="white" if st else NAVY, zorder=6)
        ax.text(x - 0.17, y + 0.12, f"{PEOPLE[n]} people", fontsize=fs - 4, color=GRAY, ha="right", va="bottom",
                zorder=6)
        if st:
            right = x == max(px for px, _ in POS.values())
            ax.text(x + (0.21 if right else -0.19), y - (0.0 if right else 0.12), st[0], ha="left" if right else "right",
                    va="center" if right else "top", fontsize=fs - 3, color=RED, weight="bold", zorder=6)
    ax.set_xlim(-0.75, 3.75); ax.set_ylim(-0.45, 2.45); ax.set_aspect("equal"); ax.axis("off")


# slide figure
fig, ax = plt.subplots(figsize=(8.4, 6.2), dpi=200)
draw(ax, big=True)
fig.savefig(PNG, facecolor="white", bbox_inches="tight", pad_inches=0.05); plt.close(fig)

# ---------------------------------------------------------------- the worksheet
fig = plt.figure(figsize=(8.5, 11))
fig.text(0.07, 0.955, "CE 414 · Week 12 · In-Class Activity: Solve It by Hand", fontsize=15, weight="bold", color=NAVY)
fig.text(0.07, 0.935, "Name: ____________________________        Work alone, on paper, about 15 minutes.",
         fontsize=10.5, color="#22262e")
intro = ("A small neighborhood as a network. Each street is labeled with the minutes an engine takes to drive it. "
         "The middle row is an arterial (1 minute a block); the other streets are local (3 minutes a block). "
         "Street H to L is one-way, H to L only; against the arrow costs 100 times its minutes. "
         "Streets B and C were digitized 2 m apart and do not meet. The number at each junction is the people who live there.")
fig.text(0.07, 0.915, intro, fontsize=9.5, color="#22262e", va="top", wrap=True)
ax = fig.add_axes([0.04, 0.50, 0.92, 0.37])
draw(ax, big=False)
qs = [
    "1.  Fewest minutes. Starting at Station 1 (E), write beside every junction the fewest minutes it takes to reach it. "
    "Spread outward the way Solve does: always extend the cheapest junction you have not finished.",
    "2.  Service area. Circle the junctions within 4 minutes of Station 1. How many people live OUTSIDE 4 minutes?   ________",
    "3.  A circle instead. At the arterial's speed (1 block a minute), a 4-minute buffer around E is a circle 4 blocks across "
    "the map: it covers every junction. How many people does the circle call covered that the roads do not reach in 4 minutes?   ________",
    "4.  Closest facility. A fire is reported at D. Which station's engine arrives first, and in how many minutes? "
    "Why is the answer not the station that looks closest on the map?   Station ____, ____ minutes",
    "5.  Location-allocation. The city can add ONE station, at C, K or H, to bring the most people now outside 4 minutes "
    "inside 4 minutes of a station (count only people outside in Question 2). Which site wins, and how many people does it add?   Site ____, ____ people",
]
y = 0.485
for q in qs:
    fig.text(0.07, y, q, fontsize=10, color="#22262e", va="top", wrap=True)
    y -= 0.088
fig.text(0.07, 0.04, "Hand it in: take a photo of this page and upload it to Learning Suite (In-class activity: Network Analysis) "
         "by 9:30 am today, fifteen minutes after class.", fontsize=9, color=NAVY, weight="bold", wrap=True)
fig.savefig(PDF); plt.close(fig)

# ---------------------------------------------------------------- the private key
KEY.parent.mkdir(parents=True, exist_ok=True)
KEY.write_text(f"""# Week 12 Thursday in-class activity — Solve It by Hand: answer key

Generated by `ce414-gis-applications/tools/week12_network_worksheet.py`. **Answer key; keep private.**
Worksheet: `docs/handouts/network-worksheet.pdf` (public). 5 points, Attendance and Participation,
upload a photo by 9:30 am Thursday of Week 12.

1. Fewest minutes from Station 1 (E): {", ".join(f"{n} {d1[n]}" for n in sorted(d1))}.
   (B is 4 by way of F, not through the gap; C is 5 by way of G; L is 6 by way of H, the legal direction.)
2. Within 4 minutes: {", ".join(sorted(covered))}. Outside: {", ".join(outside)} = **{people_out} people**
   (of {total}).
3. The circle covers all 12 junctions, so it wrongly covers the same **{people_out} people**.
4. **Station 1, {d1[fire]} minutes** (E-F-G-H on the arterial, then H-D). Station 2 at L looks two blocks
   away, but L to H is against the one-way street (300 minutes); legally it goes L-K-G-H-D, {d2[fire]} minutes.
5. **H, {gain['H']} people**: from H, D and L are 3 minutes, C and K 4 (H-G-C, H-G-K). C adds {gain['C']} (C, D);
   K adds {gain['K']} (K, L). The best site is on the arterial, not in the uncovered corner.

Grading suggestion: 5 points for a completed, legible sheet with an honest attempt at all five;
the answers are a teaching check, not the grade.
""", encoding="utf-8")
print("wrote", PDF, PNG, KEY)
