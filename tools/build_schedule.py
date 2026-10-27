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
parameter, and the four hands-on exercises.

Settled October 8, 2026: a new Lab 7, Flood Mapping with HAND, follows the two water labs
(watersheds, bathymetry, flooding); Avalanche Hazard, Big Southern Butte and Interpolation Explorer
became Labs 8 to 10, the Wind Farm lab was retired (docs/assignments/windfarm-backup), and a new
Lab 12 (Network Analyst) closes the labs. Lab 7 is introduced Tuesday of Week 8 and due Saturday of
Week 9; Labs 8 to 12 follow one a week, Lab 12 due in Week 14.

Settled October 9, 2026: one lab a week from Week 7 on, each lab introduced and due in its own week:
Lab 7 HAND (Week 8, with Midterm 1), Lab 8 Interpolation Explorer (9), Lab 9 Big Southern Butte (10),
Lab 10 Avalanche Hazard (11, with refresher lectures on projections and GPS), Lab 11 Least Cost Path (12),
no lab in Week 13 (final project introduced Tuesday; Thanksgiving), Lab 12 Network Analysis (14), and no
class in Week 15 (final project due by the last day of classes). The OGC Web Services and Raster-Based
Spatial Analysis decks were retired to slides/retired/ (not built).

Settled October 21, 2026 (and kept for Fall 2027): the Week 11 coordinate systems and GPS refreshers
are dropped (CCE 114 teaches both; decks and their two self-check quizzes are in
slides/retired/week-11-crs-gps/). Least cost paths move up to Week 11 and network analysis to Week 12,
so both are taught before Midterm 2. The labs were renumbered to match: Least Cost Path is Lab 10
(Week 11), Network Analysis Lab 11 (Week 12), and Avalanche Hazard, which needs only Week 5 tools,
is Lab 12, due in Week 14 with Midterm 2. Quiz 9 is Least Cost Paths, Quiz 10 Network Analysis."""
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
    (6,  "watershed-delineation-b",        "Watershed Delineation, Part B",              "A watershed delineated by hand and then with USGS StreamStats, then the rest of the steps in ArcGIS Pro: flow accumulation, the stream threshold, stream links, pour points and subwatersheds, and the Lab 5 model that runs all eight.", "Thu"),
    (7,  "lake-bathymetry",                "Lake Bathymetry, Part A",                    "A lake with no outlet: the Great Salt Lake's level as its water balance, how lake bottoms are measured, the USGS lake-bottom DEM, two vertical datums, and elevation-area-volume curves.", "Tue"),
    (7,  "lake-depth-explorer",            "Lake Bathymetry, Part B",                    "One model, many runs: ModelBuilder iterators, %Value% in expressions and output names, Collect Values and Merge, and Lab 6 — Lake Depth Explorer at Lake Powell.", "Thu"),
    (8,  "flood-models",                   "Flood Mapping, Part A",                      "Why a river is not a bathtub, HAND cell by cell (pull the river down to zero), the stream definition, and Lab 7's two models: prepare HAND once, flood it once per flow.", "Tue"),
    (8,  "hand",                           "Flood Mapping, Part B",                      "Measuring flow in rivers (the river's ruler and the rating curve), annual peaks and the 100-year flood as a 1% chance, FEMA's maps as GIS, how good HAND is against FEMA's map, the ladder from bathtub to 2-D hydraulics, and final tips for Lab 7 in ModelBuilder.", "Thu"),
    (9,  "interpolation",                  "Sampling, Nearest Neighbor, and IDW",        "Estimating a surface from points: sampling designs, Thiessen (nearest neighbor) polygons, fixed-radius averaging and IDW, by hand and in ArcGIS Pro, and which methods give the measured values back.", "Tue"),
    (9,  "interpolation-explorer",         "Kriging and Interpolation Error",            "Kriging and the semivariogram (nugget, sill, range, and three models), then how wrong each surface is: error rasters, RMSE, a six-method test, and Lab 8.", "Thu"),
    (10, "cut-and-fill",                   "Cut and Fill",                               "Earthwork as the difference of two surfaces: cut and fill cell by cell, the balance grade of a level pad, ArcGIS Pro's Cut Fill tool, average end area for roads, and what a grid volume leaves out.", "Tue"),
    (10, "raster-volumes",                 "Volumes with Rasters",                       "How much rock is in a mountain: height times cell area summed, Raster Calculator and Zonal Statistics versus Surface Volume, why the base surface decides the answer, and Lab 9.", "Thu"),
    (11, "least-cost-path",                "Least Cost Path Analysis, Part A",           "Cost surfaces and the cheapest route across them, with a power-line corridor as the example.", "Tue"),
    (11, "least-cost-path-b",              "Least Cost Path Analysis, Part B",           "ArcGIS Pro's current tools, Distance Accumulation and Optimal Path As Line; the back direction raster as a compass angle; Lab 10's route computed from its own rules; which decisions moved the line; and a corridor of nearly-as-good routes.", "Thu"),
    (12, "network-analysis-a",             "Network Analysis, Part A",                   "Distance along the roads: what a network dataset is made of, edges, junctions and connectivity, impedance in minutes, one-way streets and turns, and why the shortest route is not the fastest.", "Tue"),
    (12, "network-analysis-b",             "Network Analysis, Part B",                   "Three solvers on one network: service areas, closest facility and location-allocation in ArcGIS Pro, a buffer against a service area for the same four minutes, and Lab 11.", "Thu"),
    (13, "final-project-introduction",     "The Final Project",                          "What the capstone project is for, how big it should be, the requirements, the proposal meeting, milestones, and how it is scored.", "Tue"),
]
LABS = {1:"Walmart Site Selection",2:"NDVI",3:"Georectifying and Digitizing Images",4:"Cell Phone Tower Placement",
        5:"Watershed Delineation",6:"Lake Depth Explorer",7:"Flood Mapping with HAND",8:"Interpolation Explorer",
        9:"Big Southern Butte",10:"Least Cost Path Power Line Analysis",11:"Network Analysis",
        12:"Avalanche Hazard"}
LAB_PAGE = {n: f"../assignments/lab-{n:02d}/README.md" for n in range(1, 13)}
WEEK_TITLES = {1:"Data Models Refresher",2:"ModelBuilder",3:"Raster Analysis and Map Algebra",4:"Imagery",
               5:"Terrain Analysis",6:"Watershed Delineation",7:"Lake Bathymetry",
               8:"Flood Mapping and Midterm 1",9:"Interpolation",10:"Cut, Fill, and Raster Volumes",
               11:"Least Cost Path",12:"Network Analysis",13:"Final Project Intro",
               14:"Midterm 2 and Avalanche Hazard",15:"Final Project Due"}
DAY_NAME = {"Tue": "Tuesday", "Thu": "Thursday"}
# Weeks whose page should point at the final project page. The project is introduced in Week 13 and
# runs to the end, and the page is not in the site menu — these pointers are how students reach it.
FINAL_PROJECT_WEEKS = (13, 14, 15)

# Weeks with no new slide deck: what happens in class, shown in the In-Class Practice card.
NO_DECK = {
    13: "Thursday is Thanksgiving, no class.",
    14: "No new lecture: Midterm 2 is open in the Testing Center, and class time Tuesday and Thursday is open lab for Lab 12 and the final project proposal meetings.",
    15: "No class this week. Work on your final project and submit it by the last day of classes.",
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
                    ("In-class activity: Three Lake Levels", "done in class Thursday; upload a screen capture by 9:30 am, fifteen minutes after class"),
                    ("**Midterm 1 is next week**, on Weeks 1–7: read the [study guide](../study-guides/midterm-1.md) now", "opens Tuesday of Week 8 at 8:00 am")]),  # Oct 1: replaces the two old Week 7 activities; Learning Suite still has the old ones
    8:  dict(reading=None, quiz=None, lab=7,
             other=[("**Midterm 1** — closed book, concept based, in the Testing Center, on Weeks 1–7 ([study guide](../study-guides/midterm-1.md))", "opens Tuesday 8:00 am and closes Thursday 9:00 pm; the Testing Center late fee starts Thursday 2:00 pm")]),
    9:  dict(reading="Chapter 12", quiz=(7, "Sampling and Interpolation"), lab=8,
             other=[("In-class activity: Air Temperature Interpolation", "done in class Tuesday, each student on their own copy of the [printable worksheet](../handouts/provo-temperature-worksheet.pdf) (PDF, 1 page); upload a photo of the completed worksheet by 9:30 am, fifteen minutes after class")]),
    # Fall 2026 only: the instructor is away Week 10, so there is no class. Remove after November 5.
    10: dict(reading=None, quiz=(8, "Cut, Fill, and Raster Volumes"), lab=9,   # no reading; Quiz 8 is built from the two decks
             other=[("**No class on Tuesday, November 3, or Thursday, November 5**",
                     "study the two slide decks below on your own and work on Lab 9; Quiz 8 is built from those two decks, not from the textbook")]),
    11: dict(reading=None, quiz=(9, "Least Cost Paths"), lab=10, other=[]),
    12: dict(reading=None, quiz=(10, "Network Analysis"), lab=11, other=[]),
    # From Lab 7 on, each lab is introduced and due in the same week (Saturday); Week 13 has no lab.
    # Quizzes 8-11 follow the lectures (Oct 21): Week 10 volumes, Week 11 least cost paths, Week 12
    # network analysis, Week 13 data standards. Week 14 (Midterm 2, Lab 12) has no quiz.
    13: dict(reading="Chapter 14", quiz=(11, "Data Standards and Data Quality"), lab=None,
             other=[("**Midterm 2 is next week**, on Weeks 8–13: read the [study guide](../study-guides/midterm-2.md) now", "opens Tuesday of Week 14 at 8:00 am")]),
    14: dict(reading=None, quiz=None, lab=12,
             other=[("**Midterm 2** — closed book, concept based, in the Testing Center, on Weeks 8–13 ([study guide](../study-guides/midterm-2.md))", "opens Tuesday 8:00 am and closes Thursday 9:00 pm; the Testing Center late fee starts Thursday 2:00 pm"),
                    ("Final project **proposal meeting** with the instructor", "by Friday 5:00 pm; update the class Google document with your team, idea, and data")]),
    15: dict(reading=None, quiz=None, lab=None,
             other=[("Final project **presentation video** (eight minutes; post the link on the class Google document)", "Wednesday 11:59 pm"),
                    ("Peer-review stamp log: a memo listing the ten or more classmates whose work you reviewed", "Wednesday 11:59 pm"),
                    ("Final project **lab assignment** (each team member submits)", "Thursday 11:59 pm"),
                    ("Notes on at least ten classmates' presentation videos", "Thursday 11:59 pm"),
                    ("Course evaluation (extra credit)", "Friday 11:59 pm")]),
}

# What a lab's submission consists of, where it is more than one PDF (the lab page is the authority).
LAB_FILES_DEFAULT = "as one PDF report on Learning Suite"
LAB_FILES = {
    6: "on Learning Suite as a PDF report plus each map as its own layout PDF",
    7: "on Learning Suite as a PDF report, each map as its own layout PDF, and your `Lab07.atbx` toolbox",
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
    8: [("hand", "Height Above What?",
         "Six questions on what HAND measures, which cells flood when the river rises, the tool that computes HAND, why the stream definition matters, and why Lab 7 is two models."),
        ("floods", "How Big, How High?",
         "Six questions on how a gage reading becomes a flow, what a 100-year flood means, when a bathtub is the right model, scoring a flood map, and two Lab 7 ModelBuilder mistakes.")],
    9: [("interpolation", "Points Into Surfaces",
         "Five questions on estimating a surface from points: Thiessen polygons, IDW and kriging, which methods give the measured values back, and how you would judge which one to trust."),
        ("rmse", "How Wrong Is the Surface?",
         "Seven questions on how kriging differs from IDW, what an error raster's sign means, why RMSE squares the errors, what it hides, where the error lives, and the Gaussian model.")],
    10: [("earthwork", "Cut or Fill?",
          "Five questions on cut versus fill, raising a pad's grade, the balance grade, the sign of Cut Fill's VOLUME, and what a grid volume leaves out."),
         ("volumes", "The Base Is the Answer",
          "Five questions on a cell's volume, why a DEM must be projected first, when Surface Volume is enough, and why the base surface decides a mountain's volume.")],
    11: [("least-cost-path", "Cheapest or Shortest?",
          "Five questions on cost surfaces, the accumulated cost and back link rasters, and why the cheapest route is usually not the shortest one."),
         ("cost-paths", "What Moved the Line?",
          "Five questions on the current tools, the back direction raster as a compass angle, which cost factors actually move a route, and what a corridor shows.")],
    12: [("networks", "Along the Roads",
          "Five questions on what a network dataset is made of: junctions and connectivity, one-way streets as a cost, two impedances that give two routes, what UGRC's 1.5 factor stands for, and which distance belongs to a fire engine."),
         ("service-areas", "Four Minutes Away",
          "Five questions on Solve, which solver answers which question, why a buffer and a service area disagree about the same four minutes, and what Lab 11's cutoff decides.")],
    13: [("final-project", "Ready to Pitch?",
          "Five questions on what the final project asks of you: what counts as a big enough project, raster and vector and a model someone else can run, what the proposal meeting is for, and how you would show the result is right.")],
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
                        f"Due **Saturday at 11:59 pm** {LAB_FILES.get(d['lab'], LAB_FILES_DEFAULT)} — {LAB_PTS} points."]

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
