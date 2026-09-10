#!/usr/bin/env python3
"""Generate docs/schedule/week-NN.md, docs/schedule/README.md, and the Schedule section of
mkdocs.yml from the DECKS and DUE tables below. Everything is expressed in week numbers so the
site survives re-offering. Edit the tables, then run:  python3 tools/build_schedule.py

Hand-written notes in a week page survive below a "<!-- notes -->" marker; everything above it
is regenerated. This replaces the old docs/lectures/ + tools/build_lectures.py: the site is
organized one page per week, not a separate "Lectures" menu — each week's page carries that
week's Tuesday and Thursday lecture slides, the lab due, and study guides once they exist.

The DUE table was transcribed from the Fall 2026 Learning Suite syllabus (printed September 7,
2026). Standing rule from that syllabus: reading quizzes and labs are due Saturday at 11:59 pm of
the week they are listed under. In-class activities are due at 9:30 am the day they happen,
fifteen minutes after the 8:00-9:15 class.

Day-of-week ("Tue"/"Thu") on a deck comes from the Learning Suite migration notes (see
LEARNING_SUITE_MIGRATION_PLAN.md and learning-suite-snapshots/), not from the order decks happen to
sit in DECKS. A trailing "?" means the day is inferred rather than confirmed against a completed
Learning Suite edit; leave it None rather than guess — see CLAUDE.md rule 4. A week's slides render
under Tuesday/Thursday headings only when every deck that week has a distinct, known day; otherwise
they render as a plain list, which is also correct for a week where one deck spans both class days.

Decisions still pending (Sept 7, 2026, see ROADMAP.md "Syllabus decisions"): the reading quizzes may
be replaced by pre- and post-class quizzes. Settled September 8, 2026: midterms in Weeks 8 and 14;
Lab 6 is the new Lake Depth Explorer lab, Labs 6 to 10 of the Word era became 7 to 11, and Choose
Your Own Adventure is gone. Settled September 9, 2026: Week 3 rebuilt around NDVI folded into raster
analysis (Tuesday) plus a new hands-on deck (Thursday), retiring ModelBuilder Part C. Settled
September 9, 2026: that pair was resplit as Part A and Part B, matching Week 2 — Part A ends with the
NDVI threshold table, and Part B carries the raster-function families, the threshold as a model
parameter, and the four hands-on exercises."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE = "https://byu-hydroinformatics.github.io/ce414-gis-applications"
TEXT = "*GIS Fundamentals*, 7th edition (Bolstad)"
# Point values from the Learning Suite assignments view (printed September 7, 2026)
QUIZ_PTS, LAB_PTS, ACTIVITY_PTS = 20, 50, 5

# week, slug, title, one-line description, day ("Tue"/"Thu"/"Tue?"/None)
DECKS = [
    (1,  "data-models-refresher",          "Data Models Refresher",                      "What a model is, and the vector, raster, and TIN data models that every later week builds on.", "Thu"),
    (2,  "modelbuilder-a",                 "ModelBuilder, Part A",                       "Why models, then ModelBuilder in ArcGIS Pro: toolboxes, a first model, environments, reading a canvas, the Cities Near Rivers example start to finish, and how Lab 1 is the same pattern.", "Tue"),
    (2,  "modelbuilder-b",                 "ModelBuilder, Part B",                       "The cookie model, then making a working model reusable: Add To Display, gray elements, renaming, parameters so the model runs as a tool, metadata; then a Lab 1 clinic on the rubric, a complete submission, checking your answer, and peer review.", "Thu"),
    (3,  "raster-analysis-a",              "Raster Analysis and Map Algebra, Part A",     "Rasters as grids of numbers, map algebra cell by cell, the four things that must line up, the integer trap, and NDVI built up from the red edge to the Lab 2 model and its threshold table.", "Tue"),
    (3,  "raster-analysis-b",              "Raster Analysis and Map Algebra, Part B",     "Local, focal, zonal and global functions; the NDVI model as a tool with a threshold parameter; then three exercises in ArcGIS Pro on the Lab 2 data, one per family: a Con() threshold sweep, Focal Statistics at a field edge, and Zonal Statistics as Table by census tract.", "Thu"),
    (4,  "georectifying-images",           "Georectifying Images",                       "Giving a scanned map or photo real-world coordinates: control points, transformations, and what can go wrong.", "Tue"),
    (4,  "remote-sensing",                 "Remote Sensing",                             "How sensors see the Earth: the electromagnetic spectrum, what a digital image stores, bands and false color, hyperspectral imagery, and a gallery of what orbit looks like.", "Thu"),
    (5,  "elevation-data-lidar",           "Elevation Data and LiDAR",                   "What an elevation surface is, how LiDAR measures one, and where to download a DEM — the National Map and 3DEP, SRTM, ASTER GDEM and ALOS, and what cell size costs you.", "Tue"),
    (5,  "terrain-analysis",               "Terrain Analysis",                           "What you compute from a DEM: shaded relief, contours, slope, aspect, curvature and viewsheds, each from a moving window.", "Thu"),
    (6,  "watershed-delineation",          "Watershed Delineation",                      "From a DEM to watersheds and streams: fill, flow direction, flow accumulation, thresholds, and pour points.", None),
    (8,  "interpolation",                  "Interpolation",                              "Estimating a surface from points: Thiessen polygons, IDW, splines, and kriging, and how to judge which one to trust.", None),
    (9,  "ogc-web-services",               "Overview of OGC Web Services",               "Interoperability and open standards for sharing spatial data over the web: WMS, WFS, WCS, and their relatives.", "Thu"),
    (10, "raster-spatial-analysis",        "Raster-Based Spatial Analysis",              "The raster suitability workflow end to end — criteria, data, rasterization, reclassification, overlay, and heat maps.", None),
    (11, "least-cost-path",                "Least Cost Path Analysis",                   "Cost surfaces and the cheapest route across them, with a power-line corridor as the example.", "Tue"),
    (11, "coordinate-systems-projections", "Coordinate Systems and Projections",        "Datums, projections, and coordinate systems as decisions: distortion, units, and choosing a CRS for analysis.", "Thu"),
    (12, "final-project-introduction",     "The Final Project",                          "What the capstone project is for, how big it should be, the requirements, the proposal meeting, milestones, and how it is scored.", "Tue?"),
    (12, "gps-triangulation",              "GPS and Positioning",                        "How satellite positioning works, what limits its accuracy, and what that means for field data.", "Thu"),
]
LABS = {1:"Walmart Site Selection",2:"NDVI",3:"Georectifying and Digitizing Images",4:"Cell Phone Tower Placement",
        5:"Watershed Delineation",6:"Lake Depth Explorer",7:"Avalanche Hazard",8:"Big Southern Butte",
        9:"Practicing with Interpolation",10:"Wind Farm Site Selection",11:"Least Cost Path Power Line Analysis"}
LAB_PAGE = {n: f"../assignments/lab-{n:02d}/README.md" for n in range(1, 12)}
WEEK_TITLES = {1:"Data Models Refresher",2:"ModelBuilder",3:"Raster Analysis and Map Algebra",4:"Imagery",
               5:"Terrain Analysis",6:"Watershed Delineation",7:"Watershed Delineation, Part 3",
               8:"Interpolation and Midterm 1",9:"Interpolation, Part 3, and Web Services",
               10:"Raster-Based Spatial Analysis",11:"Least Cost Path and Coordinate Systems",12:"GPS and the Final Project",
               13:"Final Project Work",14:"Presentations and Midterm 2",15:"Final Project Presentations"}
DAY_NAME = {"Tue": "Tuesday", "Thu": "Thursday"}
# Weeks whose page should point at the final project page. The project is introduced in Week 12 and
# runs to the end, and the page is not in the site menu — these pointers are how students reach it.
FINAL_PROJECT_WEEKS = (12, 13, 14, 15)

# Weeks with no new slide deck still get a page, with this description of what happens in class.
NO_DECK = {
    7:  "No new deck. Tuesday is hands-on practice with the hydrology tools in ArcGIS Pro (Fill, Flow Direction, "
        "Flow Accumulation, flow path), a look at USGS StreamStats, and the *Where is my watershed?* activity. "
        "Thursday introduces Lab 6 — Lake Depth Explorer and the ModelBuilder idea it is built on: a model that "
        "**loops** over a list of water-surface elevations instead of being run once per elevation.",
    13: "Tuesday is a final-project work day with your partner; Thursday is Thanksgiving, no class.",
    14: "Tuesday is a final-project work day with the instructor available; Thursday is the first day of final "
        "project presentations, eight minutes each. Sign up for a day on the class Google document. Midterm 2 is "
        "open in the Testing Center from Tuesday morning to Thursday evening.",
    15: "Tuesday is the second day of presentations. Thursday is the last day of class. The final exam is the "
        "following week.",
}

# What is due in each week. Quizzes and labs are due Saturday 11:59 pm; everything else says when.
# reading: chapters for the week's quiz; quiz: (number, title); lab: number; other: list of (what, when) rows.
DUE = {
    1:  dict(reading="Chapters 1 and 2", quiz=(1, "Basic Concepts and Data Models"), lab=None,
             other=[("In-class activity: your professional stamp", "done in class Thursday; upload the image the same day by 9:30 am, fifteen minutes after class")]),
    2:  dict(reading="Chapter 13", quiz=(2, "Cartographic Models and Modeling"), lab=1,
             other=[("In-class activity: Model a Cookie", "done in class Thursday; upload a screen capture of your result by 9:30 am, fifteen minutes after class")]),
    3:  dict(reading="Chapter 10", quiz=(3, "Raster Analysis and Map Algebra"), lab=2,
             other=[("In-class activity: Simple Map Algebra (Excel)", "done in class Tuesday; upload the workbook by 9:30 am, fifteen minutes after class"),
                    ("In-class activity: Raster Analysis Hands-On", "done in class Thursday; upload the numbers sheet by 9:30 am, fifteen minutes after class")]),
    4:  dict(reading="Chapter 6", quiz=(4, "Remote Sensing"), lab=3,
             other=[("In-class activity: Georeference Your Home", "done in class Tuesday; upload a screen capture by 9:30 am, fifteen minutes after class")]),
    5:  dict(reading="Chapter 11", quiz=(5, "Terrain Analysis"), lab=4,
             other=[("In-class activity: Terrain Analysis, Slope (Excel)", "done in class Tuesday; upload the workbook by 9:30 am, fifteen minutes after class")]),
    6:  dict(reading="Chapter 10 review; some of this quiz needs a web search", quiz=(6, "Watershed Delineation"), lab=5,
             other=[("In-class activity: Aspect and D8 Flow Direction (Excel)", "done in class Tuesday; upload the workbook by 9:30 am, fifteen minutes after class")]),
    7:  dict(reading=None, quiz=None, lab=6,   # Lab 6 (Lake Depth Explorer) is introduced Thursday and due the same Saturday; see ROADMAP item 4
             other=[("In-class activity: Practicing Hydrology Tools", "done in class Tuesday; upload a screen capture by 9:30 am, fifteen minutes after class"),
                    ("In-class activity: Where is my watershed?", "done in class Tuesday; upload a screen capture by 9:30 am, fifteen minutes after class")]),
    8:  dict(reading="Chapter 12", quiz=(7, "Sampling and Interpolation"), lab=7,
             other=[("In-class activity: Air Temperature Interpolation", "done in class Tuesday; upload a screen capture or photo by 9:30 am, fifteen minutes after class"),
                    ("**Midterm 1** — closed book, concept based, in the Testing Center", "opens Tuesday 8:00 am and closes Thursday 9:00 pm; the Testing Center late fee starts Thursday 2:00 pm")]),
    9:  dict(reading="Chapter 14", quiz=(8, "Data Standards and Data Quality"), lab=8, other=[]),
    10: dict(reading="Chapter 9", quiz=(9, "Spatial Analysis"), lab=9, other=[]),
    11: dict(reading="Chapter 3", quiz=(10, "Projections and Coordinate Systems"), lab=10, other=[]),
    12: dict(reading="Chapter 5", quiz=(11, "GPS and GNSS Data"), lab=11, other=[]),
    # Lab N is due the Saturday of Week N+1 from Lab 7 on; Lab 6 is the exception (due in Week 7, its own week).
    13: dict(reading=None, quiz=None, lab=None, other=[]),
    14: dict(reading=None, quiz=None, lab=None,
             other=[("**Midterm 2** — closed book, concept based, in the Testing Center", "opens Tuesday 8:00 am and closes Thursday 9:00 pm; the Testing Center late fee starts Thursday 2:00 pm"),
                    ("Final project **proposal meeting** with the instructor", "by Friday 5:00 pm; update the class Google document with your team, idea, and data")]),
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

def slides_section(decks):
    """Render this week's lecture(s). Tuesday/Thursday headings only when every deck this week has
    a distinct, known day; otherwise a plain list — correct for a week where one deck spans both
    class days, and honest about a week where the split just isn't confirmed yet."""
    if not decks:
        return []
    lines = ["## Slides", ""]
    bases = [d[4].rstrip("?") if d[4] else None for d in decks]
    if all(bases) and len(set(bases)) == len(decks):
        for day in ("Tue", "Thu"):
            d = next((x for x in decks if x[4] and x[4].rstrip("?") == day), None)
            if not d:
                continue
            w, slug, title, desc, deck_day = d
            lines += [f"### {DAY_NAME[day]}", "", f"[{title}]({deck_url(w, slug)}) — {desc}"]
            if deck_day.endswith("?"):
                lines += ["", "*(day inferred from the Learning Suite migration notes, not yet confirmed — see "
                               "`LEARNING_SUITE_MIGRATION_PLAN.md`)*"]
            lines.append("")
    else:
        for w, slug, title, desc, day in decks:
            prefix = f"{DAY_NAME[day.rstrip('?')]} — " if day else ""
            lines.append(f"- {prefix}[{title}]({deck_url(w, slug)}) — {desc}")
        lines.append("")
    lines += ["Navigate with the arrow keys; press <kbd>F</kbd> for fullscreen and <kbd>P</kbd> for presenter view "
              "with speaker notes.", ""]
    return lines

def week_page(w, decks):
    lines = [f"# Week {w}: {WEEK_TITLES[w]}", ""]
    lines += slides_section(decks)
    if w in NO_DECK:
        lines += ["## In class", "", NO_DECK[w], ""]
    lines += due_section(w)
    if w in FINAL_PROJECT_WEEKS:
        lines += ["## Final project", "",
                  "See the [Final Project](../assignments/final-project.md) page for the requirements, "
                  "the proposal meeting, the milestones, and how the project is scored.", ""]
    lines += ["> [!NOTE]", "> Deadlines are from the Fall 2026 Learning Suite syllabus and are stated by week number so they",
              "> survive re-offering. If Learning Suite and this page disagree, Learning Suite wins.", ""]
    return "\n".join(lines)

def index_page(weeks):
    lines = ["# Schedule", "",
             "One page per week: that week's Tuesday and Thursday lecture slides, the lab due, and study guides "
             "once they exist. Weeks are numbered from the first class meeting so the same site serves every "
             "offering; the authoritative dates live in the Learning Suite syllabus.", "",
             "**Class meets** Tuesdays and Thursdays, 8:00 to 9:15 am, in 234 CB. The 2:00 to 2:50 pm period on "
             "those days is an open lab: the computer lab is reserved for this class so you can work on your lab "
             "assignment individually, with help available.", "",
             "| Week | Topic | Lab due |", "| --- | --- | --- |"]
    for w in sorted(weeks):
        lab = DUE.get(w, {}).get("lab")
        lab_cell = f"Lab {lab} — {LABS[lab]}" if lab else "—"
        lines.append(f"| [{w}](week-{w:02d}.md) | {WEEK_TITLES[w]} | {lab_cell} |")
    lines += ["", "## Exams", "",
              "- **Midterms 1 and 2** are closed-book, concept-based exams in the Testing Center, 100 points each. "
              "Each opens **Tuesday at 8:00 am** and closes **Thursday at 9:00 pm** (Weeks 8 and 14); the Testing "
              "Center charges its late fee from 2:00 pm Thursday, so go earlier. Study the readings and the "
              "quizzes. Any exception to the schedule must be approved at least one week in advance.",
              "- **The final exam** (100 points) is in class during finals week: one question, done in ArcGIS Pro "
              "at a lab computer, open book and open computer, with a three-hour block and a single PDF to "
              "upload. It should take about 45 minutes; the block is long to allow for software trouble and "
              "accommodations.", "",
              "## Final project milestones", "",
              "| Step | When |", "| --- | --- |",
              "| Proposal meeting with the instructor; team, idea, and data on the class Google document | "
              "Week 14, by Friday 5:00 pm |",
              "| Presentation: poster, slides, or video, eight minutes | Week 15, Wednesday 11:59 pm |",
              "| Group lab assignment written like the [Cell Phone Tower lab](../assignments/lab-04/README.md), "
              "submitted by each team member with an effort note | Week 15, Thursday 11:59 pm |",
              "| Notes on at least ten classmates' presentations | Week 15, Thursday 11:59 pm |", "",
              "See the [Final Project](../assignments/final-project.md) page for the requirements.", "",
              "> [!NOTE]",
              "> Transcribed from the Fall 2026 Learning Suite syllabus. If this page and Learning Suite "
              "disagree, Learning Suite wins.", ""]
    return "\n".join(lines)

def update_nav(weeks):
    """Replace the whole Schedule section of mkdocs.yml — the '  - Schedule:' line and every
    indented entry under it — with one generated from WEEK_TITLES. Matching the section rather
    than one fixed line keeps this idempotent: it rewrites the nav it wrote last time. Raises if
    the section is not found, because silently doing nothing leaves the menu out of step with the
    week pages this same run just generated."""
    yml = ROOT / "mkdocs.yml"; text = yml.read_text(encoding="utf-8")
    nav = ["  - Schedule:", "      - Overview: schedule/README.md"]
    for w in sorted(weeks):
        nav.append(f'      - "Week {w} — {WEEK_TITLES[w]}": schedule/week-{w:02d}.md')
    text, n = re.subn(r"^  - Schedule:.*\n(?:      .*\n)*", "\n".join(nav) + "\n", text,
                      count=1, flags=re.MULTILINE)
    if n != 1:
        raise SystemExit("mkdocs.yml: no '  - Schedule:' nav section to replace — fix the nav or "
                         "this script's pattern before trusting the menu.")
    yml.write_bytes(text.encode("utf-8"))

def main():
    weeks = {w: [] for w in WEEK_TITLES}
    for d in DECKS: weeks[d[0]].append(d)
    (DOCS / "schedule").mkdir(exist_ok=True)
    for w, decks in weeks.items():
        p = DOCS / "schedule" / f"week-{w:02d}.md"; body = week_page(w, decks)
        if p.exists() and "<!-- notes -->" in p.read_text(encoding="utf-8"):
            body += "\n<!-- notes -->" + p.read_text(encoding="utf-8").split("<!-- notes -->", 1)[1]
        p.write_bytes(body.encode("utf-8"))
    (DOCS / "schedule" / "README.md").write_bytes(index_page(weeks).encode("utf-8"))
    update_nav(weeks)
    print(f"wrote {len(weeks)} week pages, schedule/README.md, and the Schedule nav")

if __name__ == "__main__":
    main()
