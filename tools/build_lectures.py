#!/usr/bin/env python3
"""Generate docs/lectures/week-NN.md, docs/lectures/README.md, and the Lectures section of
mkdocs.yml from the DECKS and DUE tables below. Everything is expressed in week numbers so the
site survives re-offering. Edit the tables, then run:  python3 tools/build_lectures.py

Hand-written notes in a week page survive below a "<!-- notes -->" marker; everything above it
is regenerated.

The DUE table was transcribed from the Fall 2026 Learning Suite syllabus (printed September 7,
2026). Standing rule from that syllabus: reading quizzes and labs are due Saturday at 11:59 pm of
the week they are listed under."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE = "https://byu-hydroinformatics.github.io/ce414-gis-applications"
TEXT = "*GIS Fundamentals*, 7th edition (Bolstad)"
# Point values from the Learning Suite assignments view (printed September 7, 2026)
QUIZ_PTS, LAB_PTS, ACTIVITY_PTS = 20, 50, 5

# week, slug, title, one-line description
DECKS = [
    (1,  "data-models-refresher",          "Data Models Refresher",                      "What a model is, and the vector, raster, and TIN data models that every later week builds on."),
    (2,  "modelbuilder-a",                 "ModelBuilder, Part A",                       "Why models, then ModelBuilder in ArcGIS Pro: toolboxes, a first model, environments, reading a canvas, the Cities Near Rivers example start to finish, and how Lab 1 is the same pattern."),
    (2,  "modelbuilder-b",                 "ModelBuilder, Part B",                       "The cookie model, then making a working model reusable: Add To Display, gray elements, renaming, parameters so the model runs as a tool, metadata; then a Lab 1 clinic on the rubric, a complete submission, checking your answer, and peer review."),
    (3,  "modelbuilder-c",                 "ModelBuilder, Part C — NDVI",                "What counts as a model, the NDVI equation and why red and near-infrared carry the vegetation signal, and the same index read at continental, farm-plot, and multi-date scale."),
    (3,  "raster-analysis-map-algebra",    "Raster Analysis and Map Algebra",            "Rasters as grids of numbers: cell-by-cell operations, map algebra, and NDVI as a worked example."),
    (4,  "georectifying-images",           "Georectifying Images",                       "Giving a scanned map or photo real-world coordinates: control points, transformations, and what can go wrong."),
    (4,  "remote-sensing-3d-imaging",      "Remote Sensing and 3D Imaging",              "How sensors see the Earth — the electromagnetic spectrum, Landsat, and imagery in three dimensions."),
    (5,  "terrain-analysis",               "Terrain Analysis",                           "Elevation models and the products derived from them: slope, aspect, hillshade, curvature, and viewsheds."),
    (6,  "watershed-delineation",          "Watershed Delineation",                      "From a DEM to watersheds and streams: fill, flow direction, flow accumulation, thresholds, and pour points."),
    (8,  "interpolation",                  "Interpolation",                              "Estimating a surface from points: Thiessen polygons, IDW, splines, and kriging, and how to judge which one to trust."),
    (9,  "ogc-web-services",               "Overview of OGC Web Services",               "Interoperability and open standards for sharing spatial data over the web: WMS, WFS, WCS, and their relatives."),
    (10, "raster-spatial-analysis",        "Raster-Based Spatial Analysis",              "The raster suitability workflow end to end — criteria, data, rasterization, reclassification, overlay, and heat maps."),
    (11, "least-cost-path",                "Least Cost Path Analysis",                   "Cost surfaces and the cheapest route across them, with a power-line corridor as the example."),
    (11, "coordinate-systems-projections", "Coordinate Systems and Projections",        "Datums, projections, and coordinate systems as decisions: distortion, units, and choosing a CRS for analysis."),
    (12, "gps-triangulation",              "GPS and Positioning",                        "How satellite positioning works, what limits its accuracy, and what that means for field data."),
    (12, "final-project-introduction",     "The Final Project",                          "What the capstone project is for, how big it should be, the requirements, the proposal meeting, milestones, and how it is scored."),
]
LABS = {1:"Walmart Site Selection",2:"NDVI",3:"Georectifying and Digitizing Images",4:"Cell Phone Tower Placement",
        5:"Watershed Delineation",6:"Avalanche Hazard",7:"Big Southern Butte",8:"Practicing with Interpolation",
        9:"Wind Farm Site Selection",10:"Least Cost Path Power Line Analysis",11:"Choose Your Own Adventure"}
LAB_PAGE = {n: f"../assignments/lab-{n:02d}/README.md" for n in range(1, 11)}   # Lab 11 has no page yet
WEEK_TITLES = {1:"Data Models Refresher",2:"ModelBuilder",3:"ModelBuilder and Raster Analysis",4:"Imagery",
               5:"Terrain Analysis",6:"Watershed Delineation",7:"Watershed Delineation, Part 3, and Midterm 1",
               8:"Interpolation",9:"Interpolation, Part 3, and Web Services",
               10:"Raster-Based Spatial Analysis",11:"Least Cost Path and Coordinate Systems",12:"GPS and the Final Project",
               13:"Final Project Work",14:"Final Project Work and Presentations",15:"Final Project Presentations"}

# Weeks with no new slide deck still get a page, with this description of what happens in class.
NO_DECK = {
    7:  "No new deck. Tuesday is hands-on practice with the hydrology tools in ArcGIS Pro (Fill, Flow Direction, "
        "Flow Accumulation, flow path), a look at USGS StreamStats, and the *Where is my watershed?* activity. "
        "Thursday's class time is given to Midterm 1.",
    13: "Tuesday is a final-project work day with your partner; Thursday is Thanksgiving, no class.",
    14: "Tuesday is a final-project work day with the instructor available; Thursday is the first day of final "
        "project presentations, eight minutes each. Sign up for a day on the class Google document.",
    15: "Tuesday is the second day of presentations. Thursday is the last day of class. Friday, an exam-preparation "
        "day with no official class, is an optional third presentation day. The final exam is the following week.",
}

# What is due in each week. Quizzes and labs are due Saturday 11:59 pm; everything else says when.
# reading: chapters for the week's quiz; quiz: (number, title); lab: number; other: list of (what, when) rows.
DUE = {
    1:  dict(reading="Chapters 1 and 2", quiz=(1, "Basic Concepts and Data Models"), lab=None,
             other=[("In-class activity: your professional stamp", "in class Thursday; upload the image the same day")]),
    2:  dict(reading="Chapter 13", quiz=(2, "Cartographic Models and Modeling"), lab=1,
             other=[("In-class activity: Model a Cookie", "in class Thursday; upload a screen capture of your result")]),
    3:  dict(reading="Chapter 10", quiz=(3, "Raster Analysis and Map Algebra"), lab=2,
             other=[("In-class activity: Simple Map Algebra (Excel)", "in class Tuesday; upload the workbook")]),
    4:  dict(reading="Chapter 6", quiz=(4, "Remote Sensing"), lab=3,
             other=[("In-class activity: Georeference Your Home", "in class Tuesday; upload a screen capture")]),
    5:  dict(reading="Chapter 11", quiz=(5, "Terrain Analysis"), lab=4,
             other=[("In-class activity: Terrain Analysis, Slope (Excel)", "in class Tuesday; upload the workbook")]),
    6:  dict(reading="Chapter 10 review; some of this quiz needs a web search", quiz=(6, "Watershed Delineation"), lab=5,
             other=[("In-class activity: Aspect and D8 Flow Direction (Excel)", "in class Tuesday; upload the workbook")]),
    7:  dict(reading=None, quiz=None, lab=6,
             other=[("In-class activity: Practicing Hydrology Tools", "in class Tuesday; upload a screen capture"),
                    ("In-class activity: Where is my watershed?", "in class Tuesday; upload a screen capture"),
                    ("**Midterm 1** — closed book, in the Testing Center", "opens Thursday after class and closes Friday evening")]),
    8:  dict(reading="Chapter 12", quiz=(7, "Sampling and Interpolation"), lab=7,
             other=[("In-class activity: Air Temperature Interpolation", "in class Tuesday; upload a screen capture or photo")]),
    9:  dict(reading="Chapter 14", quiz=(8, "Data Standards and Data Quality"), lab=8, other=[]),
    10: dict(reading="Chapter 9", quiz=(9, "Spatial Analysis"), lab=9, other=[]),
    11: dict(reading="Chapter 3", quiz=(10, "Projections and Coordinate Systems"), lab=10, other=[]),
    12: dict(reading="Chapter 5", quiz=(11, "GPS and GNSS Data"), lab=11,
             other=[("**Midterm 2** — closed book, in the Testing Center", "opens Thursday after class and closes Saturday afternoon")]),
    13: dict(reading=None, quiz=None, lab=None, other=[]),
    14: dict(reading=None, quiz=None, lab=None,
             other=[("Final project **proposal meeting** with the instructor", "by Friday 5:00 pm; update the class Google document with your team, idea, and data")]),
    15: dict(reading=None, quiz=None, lab=None,
             other=[("Final project **presentation** (poster, slides, or video)", "Wednesday 11:59 pm"),
                    ("Peer-review stamp log: a memo listing the ten or more classmates whose work you reviewed", "Wednesday 11:59 pm"),
                    ("Attendance record on the class Google document", "Wednesday 11:59 pm"),
                    ("Final project **lab assignment** (each team member submits)", "Thursday 11:59 pm"),
                    ("Notes on at least ten classmates' presentations", "Thursday 11:59 pm"),
                    ("Course evaluation (extra credit)", "Friday 11:59 pm")]),
}

def deck_url(w, slug): return f"{SITE}/slides/week-{w:02d}/{slug}.html"

def lab_link(n, rel="../assignments"):
    title = f"Lab {n} — {LABS[n]}"
    return f"[{title}]({rel}/lab-{n:02d}/README.md)" if n in LAB_PAGE else f"{title} (on Learning Suite)"

def due_section(w, rel="../assignments"):
    d = DUE.get(w)
    if not d: return []
    lines = ["## Due this week", "",
             "Reading quizzes and labs are due **Saturday at 11:59 pm**. Other items say when.", "",
             "| What | Details |", "| --- | --- |"]
    if d["reading"]:
        lines.append(f"| Reading | {d['reading']} of {TEXT} |")
    if d["quiz"]:
        n, title = d["quiz"]
        lines.append(f"| Quiz {n} | *{title}* — open book, on Learning Suite, done independently — {QUIZ_PTS} points |")
    if d["lab"]:
        lines.append(f"| Lab {d['lab']} | {lab_link(d['lab'], rel)} — one PDF report on Learning Suite — {LAB_PTS} points |")
    for what, when in d["other"]:
        pts = f" — {ACTIVITY_PTS} points" if what.startswith("In-class activity") else ""
        lines.append(f"| {what} | {when}{pts} |")
    if not any([d["reading"], d["quiz"], d["lab"], d["other"]]):
        lines.append("| Nothing is due this week | Work on the final project |")
    lines.append("")
    return lines

def week_page(w, decks):
    lines = [f"# Week {w}: {WEEK_TITLES[w]}", ""]
    if decks:
        lines += ["## Slides", ""]
        for _, slug, title, desc in decks:
            lines.append(f"- [{title}]({deck_url(w, slug)}) — {desc}")
        lines += ["", "Navigate with the arrow keys; press <kbd>F</kbd> for fullscreen and <kbd>P</kbd> for presenter view with speaker notes.", ""]
    if w in NO_DECK:
        lines += ["## In class", "", NO_DECK[w], ""]
    lines += due_section(w)
    lines += ["> [!NOTE]", "> Deadlines are from the Fall 2026 Learning Suite syllabus and are stated by week number so they",
              "> survive re-offering. If Learning Suite and this page disagree, Learning Suite wins.", ""]
    return "\n".join(lines)

def index_page(weeks):
    lines = ["# Lectures", "",
             "Lecture slides are interactive web presentations built with [Marp](https://marp.app/). Navigate with",
             "the arrow keys (or swipe); press <kbd>F</kbd> for fullscreen and <kbd>P</kbd> for presenter view with",
             "speaker notes.", "",
             "Weeks are numbered from the first class meeting so the same site serves every offering; the",
             "authoritative dates live in the Learning Suite syllabus. Each week page lists what is due that week.", ""]
    for w in sorted(weeks):
        lines += [f"## Week {w}: {WEEK_TITLES[w]}", ""]
        for _, slug, title, desc in weeks[w]:
            lines.append(f"- [{title}]({deck_url(w, slug)}) — {desc}")
        if w in NO_DECK:
            lines.append(f"- {NO_DECK[w]}")
        lines += [f"- [Week {w} page](week-{w:02d}.md)", ""]
    lines += ["> [!NOTE]", "> Every deck carries `TODO(instructor)` and `TODO(graphic)` comments from its September 2026",
              "> conversion; see each deck's closing conversion-notes comment for what still needs a decision.", ""]
    return "\n".join(lines)

def update_nav(weeks):
    yml = ROOT / "mkdocs.yml"; text = yml.read_text(encoding="utf-8")
    nav = ["  - Lectures:", "      - Overview: lectures/README.md"]
    for w in sorted(weeks):
        nav.append(f'      - "Week {w} — {WEEK_TITLES[w]}": lectures/week-{w:02d}.md')
    yml.write_bytes(re.sub(r"  - Lectures:\n(?:      .*\n)+", "\n".join(nav) + "\n", text).encode("utf-8"))

def main():
    weeks = {w: [] for w in WEEK_TITLES}
    for d in DECKS: weeks[d[0]].append(d)
    (DOCS / "lectures").mkdir(exist_ok=True)
    for w, decks in weeks.items():
        p = DOCS / "lectures" / f"week-{w:02d}.md"; body = week_page(w, decks)
        if p.exists() and "<!-- notes -->" in p.read_text(encoding="utf-8"):
            body += "\n<!-- notes -->" + p.read_text(encoding="utf-8").split("<!-- notes -->", 1)[1]
        p.write_bytes(body.encode("utf-8"))
    (DOCS / "lectures" / "README.md").write_bytes(index_page(weeks).encode("utf-8"))
    update_nav(weeks)
    print(f"wrote {len(weeks)} week pages, lectures/README.md, and the Lectures nav")

if __name__ == "__main__":
    main()
