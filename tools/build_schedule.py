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
    (3,  "raster-analysis-b",              "Raster Analysis and Map Algebra, Part B",     "Local, focal, zonal and global functions: moving windows, what a mean does to an edge, one number per zone, and where the tools sit in the Geoprocessing pane; then the NDVI model as a tool with a threshold parameter, and a Con() threshold sweep in ArcGIS Pro on the Lab 2 data.", "Thu"),
    (4,  "georectifying-images",           "Georectifying Images",                       "Giving a scanned map or photo real-world coordinates: control points, transformations, and what can go wrong.", "Tue"),
    (4,  "remote-sensing",                 "Remote Sensing",                             "How sensors see the Earth: the electromagnetic spectrum, what a digital image stores, splitting images into bands, false color, hyperspectral imagery, and the satellites that take the pictures.", "Thu"),
    (5,  "elevation-data-lidar",           "Elevation Data and LiDAR",                   "What an elevation surface is, how LiDAR measures one, and where to download a DEM — the National Map and 3DEP, SRTM, ASTER GDEM and ALOS, and what cell size costs you.", "Tue"),
    (5,  "terrain-analysis",               "Terrain Analysis",                           "What you compute from a DEM: shaded relief, contours, slope, aspect and curvature from local neighborhoods, plus viewsheds from line of sight.", "Thu"),
    (6,  "watershed-delineation-a",        "Watershed Delineation, Part A",              "What a watershed is and why water is managed by them — Powell, nested hydrologic units from Rock Canyon to the Great Salt Lake, the water balance — then Lab 5 and the first three steps from a DEM: the elevation surface, Fill, slope and aspect against D8, and the flow direction grid.", "Tue"),
    (6,  "watershed-delineation-b",        "Watershed Delineation, Part B",              "From flow direction to watersheds: flow accumulation, the stream threshold, stream links, pour points and subwatersheds, the Lab 5 model that runs all eight steps, and a watershed delineated by hand and with USGS StreamStats.", "Thu"),
    (7,  "lake-bathymetry",                "Lake Bathymetry, Part A",                    "A lake with no outlet: the Great Salt Lake's level as its water balance, how lake bottoms are measured, the USGS lake-bottom DEM, two vertical datums, and elevation-area-volume curves.", "Tue"),
    (7,  "lake-depth-explorer",            "Lake Bathymetry, Part B",                    "One model, many runs: ModelBuilder iterators, %Value% in expressions and output names, Collect Values and Merge, and Lab 6 — Lake Depth Explorer at Lake Powell.", "Thu"),
    (8,  "interpolation",                  "Interpolation",                              "Estimating a surface from points: Thiessen polygons, IDW, splines, and kriging, and how to judge which one to trust.", None),
    (9,  "ogc-web-services",               "OGC Web Services",                           "Data you ask for instead of download: WMS, WFS, WCS and catalogs, the OGC API generation, ArcGIS REST queries, and cloud-native COG and STAC, all on live Utah services.", "Thu"),
    (10, "raster-spatial-analysis",        "Raster-Based Spatial Analysis",              "The raster suitability workflow end to end — criteria, data, rasterization, reclassification, overlay, and heat maps.", None),
    (11, "least-cost-path",                "Least Cost Path Analysis",                   "Cost surfaces and the cheapest route across them, with a power-line corridor as the example.", "Tue"),
    (11, "coordinate-systems-projections", "Coordinate Systems and Projections",        "Datums, projections, and coordinate systems as decisions: distortion, units, and choosing a CRS for analysis.", "Thu"),
    (12, "final-project-introduction",     "The Final Project",                          "What the capstone project is for, how big it should be, the requirements, the proposal meeting, milestones, and how it is scored.", "Tue?"),
    (12, "gps-triangulation",              "GPS and Positioning",                        "How satellite positioning works, what limits its accuracy, and what that means for field data.", "Thu"),
]
LABS = {1:"Walmart Site Selection",2:"NDVI",3:"Georectifying and Digitizing Images",4:"Cell Phone Tower Placement",
        5:"Watershed Delineation",6:"Lake Depth Explorer",7:"Avalanche Hazard",8:"Big Southern Butte",
        9:"Interpolation Explorer",10:"Wind Farm Site Selection",11:"Least Cost Path Power Line Analysis"}
LAB_PAGE = {n: f"../assignments/lab-{n:02d}/README.md" for n in range(1, 12)}
WEEK_TITLES = {1:"Data Models Refresher",2:"ModelBuilder",3:"Raster Analysis and Map Algebra",4:"Imagery",
               5:"Terrain Analysis",6:"Watershed Delineation",7:"Lake Bathymetry",
               8:"Interpolation and Midterm 1",9:"Interpolation, Part 3, and Web Services",
               10:"Raster-Based Spatial Analysis",11:"Least Cost Path and Coordinate Systems",12:"GPS and the Final Project",
               13:"Final Project Work",14:"Presentations and Midterm 2",15:"Final Project Presentations"}
DAY_NAME = {"Tue": "Tuesday", "Thu": "Thursday"}
# Weeks whose page should point at the final project page. The project is introduced in Week 12 and
# runs to the end, and the page is not in the site menu — these pointers are how students reach it.
FINAL_PROJECT_WEEKS = (12, 13, 14, 15)

# Weeks with no new slide deck: what happens in class, shown in the In-Class Practice card.
NO_DECK = {
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
             other=[("In-class activity: Read the USGS Lake Table (Excel)", "done in class Tuesday; upload the workbook by 9:30 am, fifteen minutes after class"),
                    ("In-class activity: Three Lake Levels", "done in class Thursday; upload a screen capture by 9:30 am, fifteen minutes after class")]),  # Oct 1: replaces the two old Week 7 activities; Learning Suite still has the old ones
    8:  dict(reading="Chapter 12", quiz=(7, "Sampling and Interpolation"), lab=7,
             other=[("In-class activity: Air Temperature Interpolation", "done in class Tuesday; upload a screen capture or photo by 9:30 am, fifteen minutes after class"),
                    ("**Midterm 1** — closed book, concept based, in the Testing Center, on Weeks 1–7 ([study guide](../study-guides/midterm-1.md))", "opens Tuesday 8:00 am and closes Thursday 9:00 pm; the Testing Center late fee starts Thursday 2:00 pm")]),
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

# Self-check quizzes hosted on this site (docs/quizzes/<slug>/index.html). Not graded and not in the
# Due table; they are the web version of a deck's "your turn" slide, reachable by QR code in class and
# by link afterwards. week: [(slug, title, one-liner)]
PRACTICE = {
    # Week -> the lecture quizzes that week's decks end with. Each deck closes on a QR code; this
    # table is how a student who missed the scan still finds the quiz. Slugs are registered in
    # tools/make_quiz_qr.py, and the pages live in docs/quizzes/<slug>/.
    1: [("data-models", "Storing the World",
         "Five questions on vector, raster and TIN: what each model actually stores, what a grid costs you, and why a shapefile is not a data model.")],
    2: [("modelbuilder-basics", "Models and ModelBuilder",
         "Five questions on what a model is, how to read the ModelBuilder canvas, and the projection and dissolve decisions inside the Cities Near Rivers model."),
        ("model-parameters", "Canvas to Tool",
         "Five questions on turning a canvas into a tool someone else can run: why every tool needs its output drawn, parameters, why two right models can disagree, and metadata.")],
    3: [("raster-types", "Categorical or Continuous?",
         "Five real datasets, one question each: is that cell value a label, or a measurement?"),
        ("raster-functions", "Which Family?",
         "Five questions on the four families of raster function, what a moving window does to an edge, what a zone costs you, and why the Lab 2 threshold lives in a Con() expression as a parameter.")],
    4: [("georectifying", "Line It Up",
         "Five questions on putting a scanned image in its place: why you georectify before you digitize, where control points belong, and why a small RMS error is not an accuracy figure."),
        ("remote-sensing", "Light and Bands",
         "Five questions on what a band is, why vegetation is bright in reflected near-infrared, what makes a display false color, and why no one satellite does everything.")],
    5: [("elevation-lidar", "Surfaces and Returns",
         "Five questions on where an elevation surface comes from: how LiDAR measures one, which surface you need, and what cell size costs you."),
        ("terrain-analysis", "Slope, Aspect, Viewshed",
         "Six questions on what you get out of a DEM: what contours and hillshade show, aspect as an azimuth, why the slope method matters, what a viewshed answers, and how to count what a hike can see.")],
    6: [("watersheds", "Which Way Does Water Go?",
         "Five questions on what a watershed is, how watersheds nest, the water balance, why Fill comes first, and aspect against D8 flow direction."),
        ("basins", "Follow the Water",
         "Five questions on the order of the delineation steps, the stream threshold, the watershed of a pour point, snapping, and what StreamStats buys you.")],
    7: [("bathymetry", "Lake Bathymetry",
         "Five questions on a terminal lake's level, measuring the bottom, vertical datums, and what one foot of level does to area."),
        ("iterators", "Lake Depth Explorer",
         "Five questions on iterators, %Value% in expressions and output names, collecting a loop's outputs, and the Lake Powell datum trap.")],
    8: [("interpolation", "Points Into Surfaces",
         "Five questions on estimating a surface from points: Thiessen polygons, IDW and kriging, which methods give the measured values back, and how you would judge which one to trust.")],
    9: [("web-services", "What Comes Back?",
         "Five questions on what each OGC service actually hands you (a picture, the features themselves, the coverage values, or somewhere to find them) and why a standard is a document, not software.")],
    10: [("suitability", "Criteria to Surface",
          "Five questions on the suitability workflow: framing the question, reclassifying criteria onto a common scale, ruling land out, and reading the surface you get.")],
    11: [("least-cost-path", "Cheapest or Shortest?",
          "Five questions on cost surfaces, the accumulated cost and back link rasters, and why the cheapest route is usually not the shortest one."),
         ("coordinate-systems", "Projections and Datums",
          "Five questions on datums against projections, what every projection has to give up, and why a coordinate system is a decision rather than a setting.")],
    12: [("final-project", "Ready to Pitch?",
          "Five questions on what the final project asks of you: what counts as a big enough project, raster and vector and a model someone else can run, what the proposal meeting is for, and how you would show the result is right."),
         ("gps", "Where Am I?",
          "Five questions on how a receiver turns a radio signal into a position: what it measures, why the extra satellite pays for the receiver's own clock, why satellite geometry matters, and what differential correction cannot remove.")],
}

# Extra lines for a week's Presentation Slides card, such as the data an in-lecture exercise uses.
SLIDE_EXTRAS = {
    2: ["**Data for the Part A exercise:** [week02-cities-rivers.zip](../data/week02-cities-rivers.zip) (under 1 MB) — "
        "U.S. cities, major rivers and a country outline for the conterminous United States, from Natural Earth "
        "(1:10m, public domain), in WGS 1984. Project, buffer the rivers 10 miles, intersect, and count; the "
        "answer the slides quote is 256 of 678 cities."],
}

# The four cards every week page carries, in order: (key, heading, icon, text when the week has none).
# Icons are Material Design icons rendered by pymdownx.emoji; each card's color is set in extra.css.
CARDS = [
    ("slides",   "Presentation Slides", "material-presentation-play",     "No slides this week."),
    ("practice", "In-Class Practice",   "material-account-group",         "No in-class practice this week."),
    ("lab",      "Lab Assignment",      "material-flask",                 "No lab this week."),
    ("quiz",     "Reading Quiz",        "material-book-open-page-variant", "No reading quiz this week."),
]

def deck_url(w, slug): return f"{SITE}/slides/week-{w:02d}/{slug}.html"

def lab_link(n, rel="../assignments"):
    title = f"Lab {n} — {LABS[n]}"
    return f"[{title}]({rel}/lab-{n:02d}/README.md)" if n in LAB_PAGE else f"{title} (on Learning Suite)"

def is_activity(what): return what.startswith("In-class activity")

def week_page(w, decks):
    """Every week page has the same shape: an optional callout for exams and final-project deadlines,
    then four cards — slides, in-class practice, lab, reading quiz — each with its own icon. A card
    with nothing in it says so rather than vanishing."""
    d = DUE.get(w, {})
    body = {k: [] for k, *_ in CARDS}

    for _, slug, title, desc, day in decks:
        when = ""
        if day:
            when = f"**{DAY_NAME[day.rstrip('?')]}**" + (" (day not yet confirmed)" if day.endswith("?") else "") + " — "
        body["slides"].append(f"- {when}[{title}]({deck_url(w, slug)}) — {desc}")
    if decks:
        body["slides"] += ["", "Press <kbd>F</kbd> for fullscreen and <kbd>P</kbd> for presenter view with speaker notes."]
    for extra in SLIDE_EXTRAS.get(w, []):
        body["slides"] += ["", extra]

    # A week with no deck says what happens in class instead.
    if w in NO_DECK:
        body["practice"].append(NO_DECK[w])
    for what, when in d.get("other", []):
        if is_activity(what):
            name = what.split(":", 1)[1].strip()
            name = name[:1].upper() + name[1:]
            body["practice"] += ([""] if body["practice"] and not body["practice"][-1].startswith("- ") else [])
            body["practice"].append(f"- **{name}** (graded, {ACTIVITY_PTS} points) — {when}.")
    if w in PRACTICE:
        if body["practice"]:
            body["practice"].append("")
        body["practice"] += ["Self-check quizzes — not graded; open them on a phone or laptop as often as you like:", ""]
        for slug, title, desc in PRACTICE[w]:
            body["practice"].append(f"- [{title}](../quizzes/{slug}/index.html) — {desc}")

    if d.get("lab"):
        body["lab"] += [lab_link(d["lab"]), "",
                        f"Due **Saturday at 11:59 pm** as one PDF report on Learning Suite — {LAB_PTS} points."]

    if d.get("quiz"):
        n, title = d["quiz"]
        if d.get("reading"):
            body["quiz"] += [f"Read {d['reading']} of {TEXT}.", ""]
        body["quiz"].append(f"**Quiz {n} — {title}** on Learning Suite: open book, done independently. "
                            f"Due **Saturday at 11:59 pm** — {QUIZ_PTS} points.")

    lines = [f"# Week {w}: {WEEK_TITLES[w]}", ""]

    # Exams and final-project deadlines fit none of the four cards; they go in a callout at the top.
    days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
    also = [f"- {what} — {'due ' if when.startswith(days) else ''}{when}."
            for what, when in d.get("other", []) if not is_activity(what)]
    if w in FINAL_PROJECT_WEEKS:
        also.append("- See the [Final Project](../assignments/final-project.md) page for the requirements, "
                    "the proposal meeting, the milestones, and how the project is scored.")
    if also:
        lines += ["> [!IMPORTANT] Also this week"] + [f"> {x}" for x in also] + [""]

    for key, heading, icon, empty in CARDS:
        lines += [f'<div class="week-card week-card--{key}" markdown>', "",
                  f"## :{icon}: {heading}", ""]
        lines += body[key] or [f"*{empty}*"]
        lines += ["", "</div>", ""]
    lines += ["> [!NOTE]", "> If you see a discrepancy between Learning Suite and this page, please let me know so I can rectify it.", ""]
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
