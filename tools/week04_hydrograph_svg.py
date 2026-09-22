#!/usr/bin/env python3
"""Build the inline SVG for the Week 4 slide "The error it reports is measured on the
points you fitted".

The figure is a 2-D stand-in for the spline problem in georectifying: 20 observations
laid out like a stream hydrograph, 5 of them picked as "control points", and a cubic
spline forced through exactly those 5. The spline has zero residual at every point it
was fitted to and still misses most of the other 15 — the same reason a Spline
transformation always reports a total RMS error of 0.0.

Run it to regenerate the markup, which is pasted into
slides/week-04/georectifying-images.md. The <style> element with the animation rules is
emitted inside the <svg> on purpose - see the comment in build():

    python3 tools/week04_hydrograph_svg.py            # SVG to stdout
    python3 tools/week04_hydrograph_svg.py out.svg    # ... or to a file

Requires numpy and scipy. Nothing in the deck build depends on this script; it exists so
the geometry is reproducible rather than hand-tuned in the markup.
"""

from __future__ import annotations

import sys

import numpy as np
from scipy.interpolate import CubicSpline

# ---------------------------------------------------------------------------
# The 20 observations, in data units: time (hours) against flow (cfs).
# Low flat baseflow, a steep rising limb, a sharp peak, a slower recession that
# settles back toward baseflow.
# ---------------------------------------------------------------------------
T = np.arange(20, dtype=float)
FLOW = np.array(
    [
        12.0, 12.5, 13.0, 14.0,      # 0-3   baseflow
        26.0, 52.0, 84.0, 103.0,     # 4-7   rising limb
        112.0,                       # 8     peak
        99.0, 80.0, 64.0, 52.0,      # 9-12  steep early recession
        43.0, 36.0, 30.0, 25.0,      # 13-16 slower late recession
        21.0, 18.0, 16.0,            # 17-19 back toward baseflow
    ]
)

# ---------------------------------------------------------------------------
# The five control points.
#
# Chosen the way a hurried student picks control points: spread evenly across the
# x axis without looking at the shape of the data. Index 8 (the actual peak) is
# deliberately NOT among them, so the spline has nothing anchoring the crest and
# nothing damping the curvature on the recession:
#
#   0  baseflow, before anything happens
#   6  part-way up the rising limb
#  10  part-way down the early recession
#  14  on the late recession
#  19  the last point, back near baseflow
#
# The result is an obviously bad fit that still has zero residual everywhere it
# was fitted:
#
#   * with no knot at the crest, the curve tops out at 88 and cuts 24 units off
#     the observed peak of 112;
#   * the long 0-to-6 span smears the flat baseflow into a ramp, missing t=3 by
#     44 units;
#   * evenly spaced knots cannot follow a decaying recession, so between 14 and
#     19 the curve sags below the data (down to 11 where the data is 18-25) and
#     then curls back up to meet the last control point.
#
# Every one of the five sits exactly on the curve regardless: residual 0.0 at
# each, total RMS 0.0.
# ---------------------------------------------------------------------------
CP = [0, 6, 10, 14, 19]

# ---------------------------------------------------------------------------
# SVG canvas, in px. Rendered about 620 px wide on the slide.
# ---------------------------------------------------------------------------
W, H = 620, 430
PAD_L, PAD_R, PAD_T, PAD_B = 62, 18, 26, 54

X_MIN, X_MAX = -0.6, 19.6
Y_MIN, Y_MAX = 0.0, 150.0

INK = "#22262e"
NAVY = "#002e5d"
GREEN = "#1f8a4c"
GRID = "#dfe4ea"
SPLINE = "#b3261e"


def sx(t: np.ndarray | float) -> np.ndarray | float:
    """Data time -> SVG x."""
    return PAD_L + (np.asarray(t, dtype=float) - X_MIN) / (X_MAX - X_MIN) * (
        W - PAD_L - PAD_R
    )


def sy(q: np.ndarray | float) -> np.ndarray | float:
    """Data flow -> SVG y (y grows downward)."""
    return H - PAD_B - (np.asarray(q, dtype=float) - Y_MIN) / (Y_MAX - Y_MIN) * (
        H - PAD_T - PAD_B
    )


def spline_path() -> tuple[str, float]:
    """Return (SVG path `d`, approximate path length in px) for the fitted spline."""
    cs = CubicSpline(T[CP], FLOW[CP])
    ts = np.linspace(T[CP][0], T[CP][-1], 100)
    qs = cs(ts)

    px = np.round(sx(ts), 1)
    py = np.round(sy(qs), 1)

    d = f"M {px[0]:.1f} {py[0]:.1f} " + " ".join(
        f"L {x:.1f} {y:.1f}" for x, y in zip(px[1:], py[1:])
    )
    length = float(np.sum(np.hypot(np.diff(px), np.diff(py))))
    return d, length


def build() -> str:
    d, raw_len = spline_path()
    # Round the dash length up: a dasharray a little longer than the path leaves no
    # visible gap at the end of the draw, while a short one would.
    dash = int(np.ceil(raw_len / 10.0) * 10) + 20

    cs = CubicSpline(T[CP], FLOW[CP])
    misses = np.abs(cs(T) - FLOW)
    held_out = [i for i in range(20) if i not in CP]
    worst = int(max(held_out, key=lambda i: misses[i]))

    out: list[str] = []
    a = out.append

    # The <style> element goes INSIDE the <svg>, not in the markdown body.
    #
    # A top-level <style> block in Marp markdown is collected into the theme and every
    # selector in it is rewritten with the slide-container path prefixed:
    #
    #   .bespoke-marp-active .hyd-cp
    #     -> div#\:\$p > svg > foreignObject > section .bespoke-marp-active .hyd-cp
    #
    # which can never match, because `bespoke-marp-active` sits on the
    # `svg.bespoke-marp-slide` ANCESTOR of the section, not on a descendant of it.
    # (`:root` is rewritten to the section itself, so that is no escape either.)
    # A <style> nested inside an inline <svg> is passed through verbatim and unscoped,
    # so the selectors below apply exactly as written. They are still global to the
    # document, which is why every class and keyframe is prefixed `hyd-`.
    a(f'<svg class="hyd-fig" viewBox="0 0 {W} {H}" width="620" '
      'xmlns="http://www.w3.org/2000/svg" '
      'font-family="Avenir Next, Segoe UI, Helvetica, Arial, sans-serif" '
      'role="img" aria-label="Twenty hydrograph observations. A cubic spline '
      "forced through five of them passes exactly through those five and misses "
      'most of the other fifteen.">')

    a("<style>")
    # Default = the FINAL state, so the PNG and PDF exports get the finished figure.
    a(".hyd-fig { width: 100%; max-width: 620px; height: auto; display: block; }")
    a(".hyd-cp { opacity: 1; }")
    a(".hyd-spline { stroke-dashoffset: 0; }")
    a(".hyd-note { opacity: 1; }")
    # On screen, the bespoke template puts `bespoke-marp-active` on the slide's svg
    # wrapper and restarts animations when a slide becomes active, so these replay on
    # every entry.
    a(".bespoke-marp-active .hyd-cp { animation: hyd-fade 0.8s ease-out 2.5s both; }")
    a(".bespoke-marp-active .hyd-spline "
      "{ animation: hyd-draw 3s ease-in-out 4s both; }")
    a(".bespoke-marp-active .hyd-note { animation: hyd-fade 1.2s ease-out 5s both; }")
    # Anyone who has asked for less motion gets the finished figure immediately.
    a("@media (prefers-reduced-motion: reduce) { .bespoke-marp-active .hyd-cp, "
      ".bespoke-marp-active .hyd-spline, .bespoke-marp-active .hyd-note "
      "{ animation: none; } }")
    a("@keyframes hyd-fade { from { opacity: 0; } to { opacity: 1; } }")
    a("@keyframes hyd-draw { from { stroke-dashoffset: %d; } "
      "to { stroke-dashoffset: 0; } }" % dash)
    a("</style>")

    # --- grid and axes -----------------------------------------------------
    a(f'<g stroke="{GRID}" stroke-width="1">')
    for q in range(0, 151, 30):
        y = sy(q)
        a(f'<line x1="{sx(X_MIN):.1f}" y1="{y:.1f}" x2="{sx(X_MAX):.1f}" y2="{y:.1f}"/>')
    a("</g>")

    a(f'<g stroke="{INK}" stroke-width="1.6">')
    a(
        f'<line x1="{sx(X_MIN):.1f}" y1="{sy(Y_MIN):.1f}" '
        f'x2="{sx(X_MIN):.1f}" y2="{sy(Y_MAX):.1f}"/>'
    )
    a(
        f'<line x1="{sx(X_MIN):.1f}" y1="{sy(Y_MIN):.1f}" '
        f'x2="{sx(X_MAX):.1f}" y2="{sy(Y_MIN):.1f}"/>'
    )
    a("</g>")

    a(f'<g fill="{INK}" font-size="15" text-anchor="end">')
    for q in range(0, 151, 30):
        a(f'<text x="{sx(X_MIN) - 9:.1f}" y="{sy(q) + 5:.1f}">{q}</text>')
    a("</g>")

    a(f'<g fill="{INK}" font-size="17" font-weight="600">')
    a(
        f'<text x="{(sx(X_MIN) + sx(X_MAX)) / 2:.1f}" y="{H - 16}" '
        'text-anchor="middle">time</text>'
    )
    a(
        f'<text x="18" y="{(sy(Y_MIN) + sy(Y_MAX)) / 2:.1f}" text-anchor="middle" '
        f'transform="rotate(-90 18 {(sy(Y_MIN) + sy(Y_MAX)) / 2:.1f})">flow</text>'
    )
    a("</g>")

    # --- the spline, drawn under the dots ----------------------------------
    a(
        f'<path class="hyd-spline" d="{d}" fill="none" stroke="{SPLINE}" '
        f'stroke-width="3" stroke-linecap="round" stroke-dasharray="{dash}"/>'
    )

    # --- the 20 observations -----------------------------------------------
    a(f'<g fill="{INK}">')
    for t, q in zip(T, FLOW):
        a(f'<circle cx="{sx(t):.1f}" cy="{sy(q):.1f}" r="4.6"/>')
    a("</g>")

    # --- the 5 control points, on top of their black dots ------------------
    a(f'<g class="hyd-cp" fill="{GREEN}" stroke="#ffffff" stroke-width="2">')
    for i in CP:
        a(f'<circle cx="{sx(T[i]):.1f}" cy="{sy(FLOW[i]):.1f}" r="9"/>')
    a("</g>")

    # --- legend and the punchline label ------------------------------------
    a('<g class="hyd-cp" font-size="15">')
    a(
        f'<circle cx="{sx(11.0):.1f}" cy="{sy(138.0):.1f}" r="7" fill="{GREEN}" '
        'stroke="#ffffff" stroke-width="2"/>'
    )
    a(
        f'<text x="{sx(11.0) + 14:.1f}" y="{sy(138.0) + 5:.1f}" fill="{NAVY}" '
        'font-weight="600">control points</text>'
    )
    a("</g>")

    a('<g class="hyd-note">')
    a(
        f'<rect x="{sx(5.4):.1f}" y="{sy(129.0):.1f}" width="290" height="30" rx="7" '
        f'fill="#ffffff" fill-opacity="0.92" stroke="{SPLINE}" stroke-width="1.4"/>'
    )
    a(
        f'<text x="{sx(5.4) + 12:.1f}" y="{sy(129.0) + 20:.1f}" font-size="16" '
        f'fill="{SPLINE}" font-weight="600">'
        "RMSE at the 5 control points = 0.0</text>"
    )
    a("</g>")

    a("</svg>")

    # Handy while tuning: the numbers that justify the choice of control points.
    print(
        f"# control points {CP}; spline peak "
        f"{cs(np.linspace(0, 19, 400)).max():.0f} vs observed {FLOW.max():.0f}; "
        f"worst held-out miss at t={worst} ({misses[worst]:.0f} units); "
        f"path length {raw_len:.0f}px, dasharray {dash}",
        file=sys.stderr,
    )

    return "\n".join(out) + "\n"


if __name__ == "__main__":
    svg = build()
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w", encoding="utf-8") as fh:
            fh.write(svg)
    else:
        sys.stdout.write(svg)
