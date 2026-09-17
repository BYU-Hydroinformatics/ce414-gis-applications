#!/usr/bin/env python3
"""Generate the QR code PNG that sits on each deck's closing quiz slide.

Every lecture quiz lives at <SITE>/quizzes/<slug>/ and is reached in class by scanning a
code projected on the last slide. The codes are generated here rather than by hand so that
the URL a code encodes is always the URL the slide prints beside it, and so a moved quiz is
one edit and one re-run away from a correct code.

    python3 tools/make_quiz_qr.py            # regenerate every code in QUIZZES
    python3 tools/make_quiz_qr.py raster-types

Requires segno (pure Python, no build step):  python3 -m pip install --user segno
"""
import sys
import pathlib

try:
    import segno
except ImportError:  # pragma: no cover - a setup problem, not a logic one
    sys.exit("segno is not installed. Run: python3 -m pip install --user segno")

SITE = "https://byu-hydroinformatics.github.io/ce414-gis-applications"
REPO = pathlib.Path(__file__).resolve().parent.parent

# slug -> week. The slug is both the quiz directory under docs/quizzes/ and the stem of the
# PNG written into that week's deck images folder. Keep it short: a projected code is read
# from the back row, and every extra character adds modules.
QUIZZES = {
    "data-models":          1,
    "modelbuilder-basics":  2,
    "model-parameters":     2,
    "raster-types":         3,
    "raster-functions":     3,
    "georectifying":        4,
    "remote-sensing":       4,
    "elevation-lidar":      5,
    "terrain-analysis":     5,
    "watersheds":           6,
    "interpolation":        8,
    "web-services":         9,
    "suitability":         10,
    "least-cost-path":     11,
    "coordinate-systems":  11,
    "final-project":       12,
    "gps":                 12,
}

# 860 px square matches the pilot code and is more than enough for a 1280x720 slide.
TARGET_PX = 860


def quiz_url(slug):
    return f"{SITE}/quizzes/{slug}/"


def write_code(slug, week):
    url = quiz_url(slug)
    # Error correction M survives a projector and a phone camera at an angle; H would add
    # modules for no benefit here, since nothing is overlaid on the code.
    qr = segno.make(url, error="m")
    modules = qr.symbol_size(scale=1, border=0)[0]
    border = 4
    scale = max(1, round(TARGET_PX / (modules + 2 * border)))
    out = REPO / f"slides/week-{week:02d}/images/quiz-{slug}-qr.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    qr.save(out, scale=scale, border=border, dark="#1a202c", light="#ffffff")
    size = qr.symbol_size(scale=scale, border=border)[0]
    print(f"{out.relative_to(REPO)}  {modules}x{modules} modules, {size}px  ->  {url}")


def main(argv):
    wanted = argv[1:] or sorted(QUIZZES)
    unknown = [s for s in wanted if s not in QUIZZES]
    if unknown:
        sys.exit(f"unknown quiz slug(s): {', '.join(unknown)}")
    for slug in wanted:
        write_code(slug, QUIZZES[slug])


if __name__ == "__main__":
    main(sys.argv)
