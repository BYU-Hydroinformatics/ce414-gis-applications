# Lab 6: Lake Depth Explorer

**Civil Engineering 414 — Engineering Applications of GIS**

Fall 2026 · Dr. Dan Ames

*Shorelines at Every Water Level — Looping in ModelBuilder*

<!-- **Revision notes.** This page was created on September 8, 2026, as a placeholder for a new
lab, written to the anatomy in `tools/lab-conversion-guide.md`. It is the first lab in the course
that was not converted from a Word handout. What is settled: the analytical question, the parameters
the student varies, the tool list, the step titles, the deliverables, and the rubric. What is not
settled, and is marked `TODO(instructor)` throughout: the lake, the elevation surface and its
vertical datum, the prepared data package, the water-surface elevation range and step, every check
value, every figure, and the example maps. The lab has not been built in ArcGIS Pro yet; nothing on
this page has been verified against data. Do not publish the Week 7 page as final until the
migration notes at the bottom say the lab was run and piloted. -->

> [!WARNING]
> **This lab is being built.** The question, the deliverables, and the rubric below are final. The
> data package, the check values, and the figures are not on this page yet; they will be added
> before the lab is assigned in Week 7. Until then, read this page to understand what the lab asks,
> and do not start work on it.

## Background

A reservoir is a valley with a dam across it, and the lake behind the dam is not one shape. It is a
different shape at every water-surface elevation: as the lake rises it spreads up side canyons and
across benches, and as it drops it retreats to the old river channel, leaving boat ramps, marinas,
and water intakes stranded above the water line. Anyone who plans around a reservoir — an engineer
sizing an intake, a park service deciding which ramp to extend, a river runner planning a trip —
needs to know where the shoreline will be at the elevation the lake is *going* to be, not where it
is today.

The two large reservoirs on the Colorado River, Lake Powell and Lake Mead, have moved through more
than a hundred feet of elevation in the last twenty years. The instructor built two web maps that
answer exactly this question for them, and you should spend a few minutes with each before reading
further: the [Lake Powell Depth Explorer](https://lakepowell.hydromap.com){ target="_blank" } and
the [Lake Mead Depth Explorer](https://lakemead.hydromap.com){ target="_blank" }. Drag the water
level and watch the shoreline move. Every shoreline you see there is the output of the same
analysis you will build in this lab.

The analysis itself is simple: the lake bed is an elevation surface, and the shoreline at any
water-surface elevation is the line where that surface equals that elevation. Everything below is
wet; everything above is dry. What makes the problem interesting for a modeler is that nobody wants
*one* shoreline. They want a dozen, at regular intervals, and they want them all from one run. Every
lab so far built a model that runs once and produces one answer. This lab builds a model that
**loops**: it takes a list of water-surface elevations, runs the same tools for each one, and
collects the results into one dataset with the elevation recorded on every shoreline. Once you have
seen that pattern you will find it everywhere, because most real analyses are one analysis repeated
over a list of something.

Like every model, this one is only as good as the choices you make in it: which elevation surface,
in which vertical datum, at what cell size, over what range of elevations and at what step. In
Step 7 you will vary the range and the step, see how far the shorelines and their areas move, and
use what moves to say how much the answer depends on those choices.

> [!IMPORTANT]
> **Your job — see the deliverables below.** Build one ModelBuilder model that loops over a list of
> water-surface elevations and produces a shoreline polygon for each, with the elevation stored as
> an attribute; run it on the study lake; test the elevation range and step; and make two maps of
> the nested shorelines.

## Problem Statement

You are given an elevation surface for a reservoir basin that covers both the lake bed (bathymetry,
surveyed while the lake was full or after it fell) and the surrounding land (topography from a
digital elevation model), merged into one raster. Using that surface, produce the shoreline of the
lake at each of a series of water-surface elevations, from a low elevation to a high one at a fixed
step, as a single polygon feature class in which every polygon carries the elevation it represents.
Report the surface area of the lake at each elevation, map the nested shorelines, and identify the
elevations at which named features on the shore (a boat ramp, a marina, an intake) go dry.

<!-- TODO(instructor): choose the lake. Lake Powell and Lake Mead are the obvious candidates because
the depth explorers exist for them and the Bureau of Reclamation publishes their elevation
records; a smaller Utah reservoir with a public bathymetric survey would make a lighter data
package. The choice decides the data section, every check value, and the named shore features. -->

## Analysis Considerations

Every one of these is a decision somebody made, and every one of them can change the answer:

- **The elevation surface.** Bathymetry and topography come from different surveys, in different
  years, at different resolutions, and are merged into one raster. Where they meet there may be a
  seam. The merged surface you are given has already been built; the data section will say how.
  <!-- TODO(instructor): state the surveys, their dates, and the merge method once the extract exists. -->
- **The vertical datum and units.** Reservoir elevations in the United States are quoted in feet
  above a stated datum; digital elevation models are usually in meters above a different one. If
  the surface and the elevation list are in different units or datums, every shoreline is wrong by
  a constant and nothing in ArcGIS Pro will tell you. The data section states the datum and units
  of the surface; your elevation list must match them.
  <!-- TODO(instructor): the datum and units of the prepared surface. -->
- **The water-surface elevation range and step.** The default run uses a range and a step chosen
  to span the lake's recent history at a spacing that shows the shape of the basin. Both are model
  parameters, and Step 7 varies them.
  <!-- TODO(instructor): the default low elevation, high elevation, and step, in the surface's units. -->
- **Cell size.** The shoreline is only as fine as the surface's cells. A coarser surface runs
  faster and produces smoother, less accurate shorelines; the model's environments fix the cell
  size so every loop iteration uses the same one.
- **The coordinate system.** Area is reported for every shoreline, so the model runs in a
  projected, equal-area-friendly coordinate system set in the environments, not in the geographic
  coordinates the surface may arrive in.
  <!-- TODO(instructor): the output coordinate system, and the check value (the extract's extent
  area in that system) that proves it is set. -->
- **What counts as the lake.** At any elevation, some cells below the water surface are in
  closed depressions on the surrounding land that would not actually fill. The default analysis
  keeps only the polygon connected to the main pool; the step that does this is where the decision
  lives, and you will say in your report what it excluded.

## Data

> [!IMPORTANT]
> **Set up your folder before you download anything.** On the lab machines, work on the
> **D: drive**, in a folder named after you with one folder per lab inside it — `D:\Smith\Lab06\`.
> Put the project and this lab's data there. The C: drive is locked, network drives make ArcGIS Pro
> hang on large rasters, and a USB 3.0 external drive is a legitimate alternative. **Never use a
> space in a folder or file name**: the raster tools fail on paths with spaces and do not say that
> the space is why. The full set of workspace conventions is on the
> [ArcGIS Tips and Reminders](../../arcgis-tips.md){ target="_blank" } page.

This lab's main input is a **surveyed surface**: somebody went out on the water with sonar, or flew
over the drained lake bed with lidar, and turned the measurements into a grid. The six metadata
questions from Lab 1 apply with unusual force, because the *when* decides whether the survey saw
the lake bed at all, the *how* decides its accuracy, and the vertical datum answers a question the
earlier labs never had to ask. You will copy the survey date, the vertical datum, and the cell size
of the prepared surface into your report.

<!-- TODO(graphic): Figure A, an infographic of the six metadata questions answered for the
prepared surface, generated by tools/lab06/make_svgs.py once the data exist (see Lab 2's Figure B
for the pattern). -->

Here is where this lab's data will come from:

| Layer | Where it comes from |
| --- | --- |
| Merged lake-bed and land elevation surface | A **prepared extract** we make for you and host on this site |
| Reservoir elevation record (how high the lake has actually been) | An **official download** from the Bureau of Reclamation, which you read to choose your elevation range |
| Named shore features (ramps, marinas, intakes) | A layer **you create** from the basemap and the agency's facility list, with a rule for what you include |
| Basemap and imagery | A **live web service** you never download at all |

### The prepared surface (prepared for you)

<!-- TODO(instructor): host `docs/data/lab06-<lake>-surface.zip` (under about 30 MB) with a
READ-ME-FIRST.txt giving provenance, processing, vintage, datum, license and a credit line. Build it
with a script in tools/lab06/ so it can be rebuilt. Then replace this paragraph with: the files in
the zip in a table, what was done to them, and the check values a student sees on loading (value
range, cell count, cell size, coordinate system, vertical units). -->

The download link, the file list, and the check values you should see on loading the surface will
appear here when the data package is ready.

### The reservoir elevation record

The Bureau of Reclamation publishes daily water-surface elevations for the reservoirs it operates.
You will read the record for the study lake to choose the low and high elevations for your default
run, and you will cite the dates of the highest and lowest levels in your report.

<!-- TODO(instructor): link the record for the chosen lake. Candidates checked live on
September 8, 2026: the Upper Colorado hydrodata reservoir dashboards under
https://www.usbr.gov/uc/water/hydrodata/ (a dashboard page answered; confirm which reservoir id is Lake Powell) and the Lower Colorado levels archive at
https://www.usbr.gov/lc/region/g4000/levels_archive.html (Lake Mead). -->

### Shore features you create

Choose at least three named features on the shore — a boat ramp, a marina, a water intake, a
campground — and digitize a point for each, with a `Name` field and an `Elevation` field holding
the elevation of the feature's working surface, taken from the prepared raster at the point. State
in your report how you chose them. These points are what turns a stack of shorelines into an
answer: the elevation at which each one goes dry.

## ModelBuilder Tools

The tools this lab uses for the first time. Icons will be added with the figures.

<!-- TODO(instructor): verify every tool name, toolbox location, and menu label below in ArcGIS
Pro 3.7 before the lab is assigned; none has been checked in a live session yet. Add icons to
tools/lab06/make_svgs.py. -->

| Tool | What it does |
| --- | --- |
| **For** (ModelBuilder ▸ Iterators) | The loop. Given a *from* value, a *to* value, and a *by* step, it runs everything downstream of it once per value and hands the current value to those tools as a variable. [Tool reference](https://pro.arcgis.com/en/pro-app/latest/tool-reference/modelbuilder-toolbox/for.htm){ target="_blank" } |
| **Inline variable substitution** | Not a tool but the mechanism that makes the loop useful: writing `%Value%` in a tool's expression or output name inserts the current loop value, so each iteration computes and names its own result. [Help page](https://pro.arcgis.com/en/pro-app/latest/help/analysis/geoprocessing/modelbuilder/inline-variable-substitution.htm){ target="_blank" } |
| **Con** (Spatial Analyst) | Cell-by-cell *if*: where the surface is at or below the current elevation, output 1; elsewhere, output nothing. The wet cells at one water level. [Tool reference](https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/con-.htm){ target="_blank" } |
| **Raster to Polygon** (Conversion) | Turns the wet cells into a polygon whose boundary is the shoreline. [Tool reference](https://pro.arcgis.com/en/pro-app/latest/tool-reference/conversion/raster-to-polygon.htm){ target="_blank" } |
| **Collect Values** (ModelBuilder ▸ Utilities) | Gathers the output of every iteration into one list so a tool after the loop can act on all of them at once. [Tool reference](https://pro.arcgis.com/en/pro-app/latest/tool-reference/modelbuilder-toolbox/collect-values.htm){ target="_blank" } |
| **Merge** (Data Management) | Appends the collected shorelines into one feature class. [Tool reference](https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/merge.htm){ target="_blank" } |

Tools you already know from earlier labs and will use again: **Add Field** and **Calculate Field**
to store the elevation on each shoreline, **Project Raster** if the surface needs it, and the
environment settings from Lab 2's Step 0.

## Example Model

<!-- TODO(instructor): Figure C, the finished model exported from ModelBuilder as SVG (Export ▸
Export To Graphic, nothing selected), every intermediate dataset renamed, the For iterator and the
Collect Values element visible, and the parameters marked P. Cut the per-step snippets from this
export with a copy of tools/lab02/cut_model_snippets.py. -->

The finished model will appear here as **Figure C**. Its shape is the point of the lab: an iterator
at the left, a short chain of tools inside the loop that computes one shoreline, and a collector at
the right that turns the loop's outputs into one dataset. Everything marked `P` in it appears in
the tool dialog you build in Step 6.

## Complete the Lab

For an advanced GIS student, the information up to this point is all you need to complete the
assignment and create an output map from the results. Feel free to try conducting the analysis
using only the information provided above. If you need extra help, follow the step-by-step solution
below. Ensure that you create and screen capture an ArcGIS Pro toolbox interface for your model.

> [!TIP]
> If you complete the lab using only the information provided above — without using the
> step-by-step instructions below — say so in your report.

## Step-by-Step Solution

> [!NOTE]
> **Important Note #1:** The steps below walk through the study lake at the default elevation
> range and step. In Step 7 you will re-run the same model with a different range and step — so
> build it once, and build it so it is easy to change.

> [!NOTE]
> **Important Note #2:** The figures for this lab have not been captured yet. When they are added
> they will come from ArcGIS Pro 3.7 against the surface you download, and they may not match your
> screen exactly; read what is actually in front of you.

<!-- TODO(instructor): every step below needs its tool-dialog figure, its ModelBuilder snippet cut
from the Figure C export, and a "Check the result" TIP with a measured number and what the common
wrong numbers mean. Nothing numeric may be added to a step until it has been measured on the
prepared surface. -->

### Step 0 — Set Up the Project

Create a new project for the lab (the *Location* box does not take a typed path; browse to your
`D:\<you>\Lab06\` folder). Add the prepared surface to a map and answer the *Calculate statistics*
prompt. Confirm the Spatial Analyst extension is licensed. Create a toolbox and a model in the
project's Catalog pane and rename the model. Then set the model's **Environments**: the output
coordinate system, the cell size, and the processing extent, all taken from the prepared surface.

<!-- TODO(instructor): the check value that proves the environments are right, e.g. the extent
area in the output coordinate system or the cell count of the surface. -->

### Step 1 — Read the Surface

Before building anything, read the surface. Note its value range, its cell size, its coordinate
system, and its vertical units, and compare them with the elevation record from the Bureau of
Reclamation. Identify on the map the dam, the old river channel, and at least three named shore
features, and record their elevations from the surface. These become your shore-feature points.

<!-- TODO(instructor): the value range and cell size students should see, and the elevations of
the named features at the chosen lake. -->

### Step 2 — Add the Loop

Add a **For** iterator to the model. Its three inputs are the low elevation, the high elevation,
and the step, in the surface's units. Set them to the default values for this lab. The iterator's
output is a variable holding the current elevation; rename it `Elevation` so the substitution in
the next step reads clearly.

<!-- TODO(instructor): default from/to/by values; the count of iterations they produce, which is
the first check value ("the model reports N iterations"). Verify in ArcGIS Pro 3.7 where the For
iterator sits on the ModelBuilder ribbon and what its parameters are called. -->

### Step 3 — Flood the Surface

Inside the loop, add **Con**. Its condition compares the surface with the current elevation; cells
at or below it get the value 1 and everything else gets no data. Use inline substitution, writing
the loop variable as `%Elevation%` in the expression, so every iteration floods to its own level.
Name the output with the elevation in it the same way, so the intermediate rasters do not overwrite
each other.

> [!WARNING]
> If the surface is in meters and your elevations are in feet, or the other way round, this step
> runs without error and every shoreline is wrong. Check Step 1 before you check anything else.

<!-- TODO(instructor): the exact Con expression as it reads in ArcGIS Pro 3.7, and the wet cell
count at one stated elevation as the check value. -->

### Step 4 — Keep the Main Pool

The flooded raster includes every cell below the elevation, including closed depressions on land
that would never fill. Keep only the region connected to the dam. State in your report what this
removed.

<!-- TODO(instructor): decide the method (Region Group on the flooded raster and a selection of
the region containing the dam is the natural one) and verify it in ArcGIS Pro 3.7 before writing
it as fact. Add the check value: cells removed at the default elevation. -->

### Step 5 — Draw the Shoreline

Add **Raster to Polygon** inside the loop to turn the wet cells into a polygon. Then add a field
named `Elevation` to the polygon and calculate it to `%Elevation%`, so the shoreline carries the
elevation it was drawn at. Every polygon that leaves the loop is labeled.

<!-- TODO(instructor): whether to simplify polygons, and the area of the default-elevation polygon
as the check value. -->

### Step 6 — Collect and Merge

Connect the labeled polygon to **Collect Values**, and connect Collect Values to **Merge**, outside
the loop. When the model runs, the loop finishes every elevation before Merge runs once and writes
all of the shorelines into one feature class. Open its attribute table: one row per elevation, in
order. Then expose the three loop values — low, high, and step — as model parameters, so the run
you are about to repeat is a change in a dialog box, not in the model.

<!-- TODO(instructor): the row count of the merged feature class at the defaults as the check
value; the toolbox interface figure with the three parameters. -->

### Step 7 — Test the Range and Step

The default run gives *a* set of shorelines, not *the* set. Run the model at least three more times
from its tool dialog: once with a finer step, once with a coarser step, and once over a different
range — for example, only the elevations the lake has actually reached in the last ten years. Choose
your values deliberately and say why.

For every run, record in a table the low elevation, the high elevation, the step, the number of
shorelines produced, and the surface area of the lake at the lowest and highest elevations. Then
answer, in your report:

1. **Which shore features go dry, and at what elevation?** Does the answer change with the step,
   and if so, how far?
2. **How much does the lake's area change per unit of elevation**, and is that rate the same at the
   bottom of the range as at the top? What about the basin's shape explains the difference?
3. **What is the smallest step that still shows the shape of the basin?** What did the finer runs
   add, and what did they cost in run time?

Pick one of your runs for your second map, and say on the map what changed and why you chose it.

> [!TIP]
> One of the three runs will tell you far more than the other two. Look at where the shorelines
> bunch together and where they spread apart: that is the basin's shape talking, and the step you
> choose decides whether you can hear it.

## Deliverables

Make **two** professional map layouts:

1. **Your baseline result** — the nested shorelines at the default range and step, symbolized so
   the elevation of each is readable, with your shore-feature points and an inset or close-up of
   one feature at the elevation it goes dry.
2. **One scenario from Step 7** — the same model at a different range or step, whichever of your
   runs most changes the picture. Say on the map what changed and why you chose that run to show.

Write a brief report (2–3 pages of text, plus your figures and maps) covering:

- a title block — assignment title, your name, the date and the course — and the name of your
  peer reviewer
- the requirements of the project and your approach to solving it
- **a description of your model** a reader could repeat from: the iterator and its three values,
  each tool inside the loop and its settings, how the results are collected, and every input,
  intermediate and output dataset with its type
- **one** full-page figure of your model — export it from ModelBuilder (**Export ▸ Export To
  Graphic**) rather than screen-capturing it — and **one** screen capture of its toolbox interface
  showing the three parameters
- **the three metadata values** for the surface — survey date, vertical datum, and cell size — and
  what each one means for your result
- your **shore-feature table**: each feature, its elevation, and the water-surface elevation at
  which it goes dry
- your **range-and-step table** from Step 7 and your answers to its three questions
- **where the shorelines are wrong and why** — the seam between surveys, the cell size, the
  depressions you removed — and what additional data would fix it
- **a copy of the rubric below with your self-assessment filled in** — a score in every row,
  honestly arrived at. The grader will compare it with theirs.

The rubric at the end of this lab gives the point value of every item above, so read it before
you write.

> [!IMPORTANT]
> **Peer review before you submit.** Have another student in the class read your report against
> the rubric and give you feedback, then act on that feedback before the deadline. Name your
> reviewer in the report and say in a sentence what you changed because of them. A report nobody
> else has read is a draft, not a submission.

## References

- Ames, D. P. *Lake Powell Depth Explorer*, [lakepowell.hydromap.com](https://lakepowell.hydromap.com){ target="_blank" }, and *Lake Mead Depth Explorer*, [lakemead.hydromap.com](https://lakemead.hydromap.com){ target="_blank" }.
- Esri. *An overview of the ModelBuilder toolbox*, ArcGIS Pro documentation, [pro.arcgis.com](https://pro.arcgis.com/en/pro-app/latest/tool-reference/modelbuilder-toolbox/an-overview-of-the-modelbuilder-toolbox.htm){ target="_blank" }.
- Bolstad, P. *GIS Fundamentals*, 7th edition. <!-- TODO(instructor): the chapter and pages on raster analysis and on iteration or scripting, if any, to cite here. -->
- <!-- TODO(instructor): the bathymetric survey and the DEM the prepared surface was built from, cited to their agencies, once the lake is chosen. -->

## Example Maps

<!-- TODO(instructor): two real layouts built with arcpy.mp against the default run and one Step 7
scenario, exported at 150 dpi, each captioned with what a student should do better than the
example. See tools/lab02/build_layout.py for the pattern. -->

Example layouts will be added here when the lab has been run. They will be examples, not
templates, and your name must be on your maps.

## Rubric for the Lake Depth Explorer

Fifty points in five parts of ten. The bullets say what each part is worth, so you know exactly
what to submit.

| Item | Points |
| --- | --- |
| **Write-up** (2–3 pages)<br>• Assignment title, your name, date and course; your peer reviewer named, with a sentence on what you changed because of them (1)<br>• The requirements of the project and your approach to solving it, in your own words (2)<br>• The three metadata values for the surface and what each means for your result (2)<br>• The shore-feature table: how you chose the features and the elevation at which each goes dry (2)<br>• Where the shorelines are wrong and why, and what data would fix it (2)<br>• Organized writing, figures numbered and referred to, sources credited, rubric pasted with your self-assessment (1) | /10 |
| **ModelBuilder model** — correct and working<br>• The model runs end to end from its tool dialog, loops over the elevations, and produces one merged feature class with one labeled shoreline per elevation; the shoreline count and the areas at the default values match the check values (4)<br>• A full-page model figure exported from ModelBuilder, with the iterator, the loop, and the collector readable (2)<br>• A screen capture of the toolbox interface with the low, high, and step parameters exposed (2)<br>• A description of the model a reader could repeat from, including how the loop value reaches the tools inside it (2) | /10 |
| **Map 1 — your baseline** (full page, 8.5 × 11)<br>• Title stating the elevation range and step (1)<br>• Neat line, north arrow and scale bar (1)<br>• Text box with author, date, map projection, and the surface's source, survey date and vertical datum (1)<br>• The nested shorelines symbolized so each elevation is readable, with a legend (2)<br>• Your shore-feature points, labeled (1)<br>• An inset or close-up of one feature at the elevation it goes dry (2)<br>• Basemap, scale and legibility appropriate to the lake (2) | /10 |
| **Map 2 — one Step 7 scenario** (full page, 8.5 × 11)<br>• Title stating the elevation range and step (1)<br>• Neat line, north arrow and scale bar (1)<br>• Text box with author, date, map projection, and the surface's source, survey date and vertical datum (1)<br>• The nested shorelines symbolized so each elevation is readable, with a legend (2)<br>• Your shore-feature points, labeled (1)<br>• Title and text box say what changed from Map 1 and why this run was chosen (2)<br>• Basemap, scale and legibility appropriate to the lake (2) | /10 |
| **Range and step sensitivity** (Step 7)<br>• A table of at least three additional runs, giving the range, the step, the number of shorelines, and the areas at the lowest and highest elevations for each (4)<br>• Which features go dry and whether the step changes that answer (2)<br>• How the area changes per unit elevation and what the basin's shape has to do with it (2)<br>• The smallest step that still shows the basin's shape, and what the finer runs cost (2) | /10 |
| **Total** | **/50** |

> [!NOTE]
> **Using AI on this lab.** Use AI freely to understand a tool, work out an error, or
> tighten your write-up, and add one line at the end of your report saying what you used it
> for. Do not take a field name, an expression, a coordinate system, or a number from it —
> those come from your own data, and the rubric asks you to defend every one. See the
> [AI Use Policy](../../policies/ai-policy.md) for the full policy.

<!-- Migration notes (2026-09-08): NEW LAB, no Word source. Created as a placeholder on September 8, 2026, when the Word-era Labs 6 to 10 were renumbered 7 to 11 and "Lab 11 — Choose Your Own Adventure" was dropped; written to the anatomy in tools/lab-conversion-guide.md, section 9. Introduced Thursday of Week 7 (the session freed when Midterm 1 moved to Week 8) and due that Saturday.
NOT VERIFIED: the lab has not been run in ArcGIS Pro. No tool name, menu label, parameter name, expression, check value, or figure on this page has been checked in a live session. The ArcGIS Pro documentation links were checked live (HTTP 200) on September 8, 2026; the two Bureau of Reclamation links in the data-section comment likewise.
DESIGN, settled: one model that loops over water-surface elevations with the ModelBuilder For iterator and inline %Elevation% substitution, floods the surface with Con, keeps the main pool, vectorizes with Raster to Polygon, labels each shoreline with its elevation, and collects and merges the results; the student varies the elevation range and step (Step 7) and creates a shore-feature point layer; two maps; five-row rubric of ten.
TODO(instructor), in order: (1) choose the lake; (2) build the merged bathymetry-plus-topography surface, state its surveys, datum, units and cell size, host it as docs/data/lab06-<lake>-surface.zip with a READ-ME-FIRST.txt and a build script in tools/lab06/; (3) decide the default low, high and step and measure the iteration count, wet-cell counts, polygon areas and merged row count as check values; (4) decide and verify the main-pool method in Step 4 (Region Group is the candidate); (5) verify every tool name, ribbon location and parameter label in ArcGIS Pro 3.7, in particular the For iterator's inputs and where Collect Values lives; (6) capture the dialog figures, export Figure C as SVG and cut the snippets; (7) generate Figure A and the tool icons with tools/lab06/make_svgs.py; (8) build the two example layouts with arcpy.mp; (9) name the shore features and their elevations for the chosen lake; (10) cite the surveys and the textbook chapter; (11) pilot (no-GUI at minimum) and record the results here; (12) remove the under-construction WARNING box when the page is assignable. -->
