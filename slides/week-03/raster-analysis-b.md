---
marp: true
theme: ce414
paginate: true
footer: "CE 414 · Week 3 — Raster Analysis and Map Algebra, Part B"
---

<!-- _class: lead -->
<!-- _paginate: skip -->

![bg right:45% w:96%](images/ra-pivots-ndvi.png)

![w:130](../theme/images/byu-medallion.svg)

# Raster Analysis and Map Algebra — Part B

## Beyond one cell, and three exercises on your Lab 2 data

CE 414 Engineering Applications of GIS
Civil & Construction Engineering, Brigham Young University

Dr. Dan Ames

<!-- Week 3, Thursday. Part A was the concepts: map algebra, NDVI as a local raster function, the Lab 2 model and its threshold table. Part B is a short run of new material and then ArcGIS Pro open on every desk. The new material is the local, focal, zonal, global families, and the one thing Part A stopped short of: turning the threshold into a model parameter, so the sweep is five runs of a tool rather than five edits of an expression. Then three exercises on the Lab 2 extract, one per family, each ending in a number students write on the activity sheet. Exercise 1 is the start of Lab 2 Step 6, done live. The image is the center pivots near Elberta in the Lab 2 NDVI, where exercise 2 happens. The integer-trap exercise was cut on 2026-09-09: there was not time for four, Part A already teaches integer versus float, and it was the one exercise that taught a bug rather than a family of tools. -->

<!-- stamp:begin -->
<!-- _footer: '<span>CE 414 · Week 3 — Raster Analysis and Map Algebra, Part B<span class="updated">Last Updated: 2026-09-09</span></span><span>© 2026 Daniel P. Ames · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></span>' -->
<!-- stamp:end -->

---

# How today works

<div class="columns" style="grid-template-columns: 1.1fr 0.9fr; align-items: center;">
<div style="font-size:0.85em;">

- **First**, the four families of raster function, and the NDVI model as a tool with a **threshold parameter**
- **Then the rest of the hour**, three exercises in ArcGIS Pro, one on each family. Open your **Lab 2 project** now: you need the two bands and an **NDVI** raster in the map. If you have not run the model yet, run it from its tool dialog, about a minute
- Every tool today is in the **Geoprocessing pane**: search it by name, fill in the boxes, Run
- Each exercise ends in **one number**, an area or a value. Write it on the **activity sheet** and upload the sheet to Learning Suite by **9:30 am**
- Work in pairs if you like, but each of you runs the tools

</div>
<div style="text-align:center;">

![h:400](images/ra-spatial-analyst-toolbox.png)

<span style="font-size:0.65em">Spatial Analyst Tools, by family</span>

</div>
</div>

<!-- Have them open the project while you talk; ten minutes of setup at most. Anyone without a working NDVI raster can compute it in one Raster Calculator line, with Float() around both bands — and Float() is the whole point, as Part A's integer-division slide showed. Check that Spatial Analyst shows Licensed: Yes (Lab 2 Step 0) before anyone gets stuck on a gray Run button. -->

---

<!-- _class: lead -->

# Beyond one cell
## Local, focal, zonal, global

---

# Four kinds of raster function

<div class="columns">
<div>

- **Local**: one cell in, one cell out. Map algebra, Reclassify, NDVI, Con
- **Focal** (neighborhood): a **window** of cells in, one cell out. Focal Statistics, Filter, Slope, Aspect
- **Zonal**: all the cells sharing a **zone** in, one number per zone out. Zonal Statistics
- **Global**: the whole grid in, every cell out. Euclidean Distance, Flow Accumulation, Distance Accumulation

Later today you run one exercise on each of the first three.

</div>
<div>

![h:470 center](images/ra-local-focal-global.png)

<span style="font-size:0.7em">© Paul Bolstad, *GIS Fundamentals*</span>

</div>
</div>

<!-- This four-way split organizes the entire Spatial Analyst toolbox, and it is the reading's organizing idea (Chapter 10). Ask, for each Lab 1 and Lab 2 tool they have used, which family it belongs to. Everything in Lab 2 is local. Terrain analysis in Week 5 is focal; watersheds in Week 6 are global. -->

---

# Moving windows

![w:700 center](images/ra-focal-window.svg)

<div style="font-size:0.9em;">

- A **kernel** is the set of weights the window applies; 1/9 in every cell is the 3 × 3 mean
- The same window with a different function: **mean** smooths, **range** finds edges, **majority** cleans up a classified map
- Slope and aspect are focal functions on a DEM; Week 5 is built on them

</div>

<!-- The dashed box is the window; it steps one cell at a time across the whole grid and writes one number at every stop. The spike of 9 becomes 4.1: smoothing removes noise, and it removes real detail with it, which is why a smoothed DEM makes a worse slope map. Ask what happens at the edge of the grid: the window hangs off the data, and the border cells are NoData unless the tool is told to ignore them. -->

---

# Kernels and noise

<div class="columns">
<div>

![w:480 center](images/ra-moving-window-kernels.png)

</div>
<div>

![h:440 center](images/ra-noise-filtering.png)

</div>
</div>

<span style="font-size:0.7em">© Paul Bolstad, *GIS Fundamentals*</span>

<!-- Left: three window shapes and the weights they carry. Right: an input layer with a spike, a high-pass kernel, and the output, with one window position worked out longhand in the middle. A low-pass filter averages the spike away; a high-pass filter makes it stand out. The second exercise today runs a 5 by 5 mean over NDVI and looks at what it does to the edge of a center-pivot field. -->

---

# Where the tools live in ArcGIS Pro

![bg right:36% h:96%](images/ra-spatial-analyst-toolbox.png)

<div style="font-size:0.82em;">

The **Spatial Analyst** toolbox is organized the way this lecture was:

- **Local**: Map Algebra (Raster Calculator), Math (Float, Plus, Minus, Divide), Reclass, Conditional
- **Neighborhood**: Focal Statistics, Filter, Block Statistics
- **Zonal**: Zonal Statistics, Zonal Statistics as Table, Tabulate Area
- **Surface**: Slope, Aspect, Hillshade, Contour, Viewshed
- **Hydrology**: Fill, Flow Direction, Flow Accumulation, Watershed

Find any of them by name in the **Geoprocessing pane** search box, or browse **Toolboxes ▸ Spatial Analyst Tools**.

</div>

<!-- Spend a minute in the live toolbox rather than the screenshot, which is the Geoprocessing pane's Toolboxes tab in ArcGIS Pro 3.7.1 with Spatial Analyst Tools expanded. The toolsets are the families we just named. Every Lab 2 tool is in Math, Map Algebra or Reclass, which is to say local. -->

---

<!-- _class: lead -->

# The threshold as a parameter
## What Part A stopped short of

---

# Make the threshold a parameter

![w:800 center](images/ra-threshold-parameter.png)

<div style="font-size:0.82em;">

- Mark the variable as a **parameter**, exactly as in Week 2: right-click it, choose **Parameter**, a **P** appears
- That is why Lab 2 classifies with `Con()`: a number in a Reclassify table cannot be a parameter, a number in an expression can

</div>

<!-- Say the first half out loud, because it is no longer a bullet: in Part A the threshold was a number inside the model, and changing it meant opening the canvas and retyping the expression. This is the one idea Part A stopped short of, and it is Lab 2 Step 5. The Week 2 procedure applies unchanged, which is the point worth making: nothing about ModelBuilder is different because the data are rasters. Both halves of the figure are real captures of the Lab 2 model in ArcGIS Pro 3.7.1 on Sept 9, 2026, composed by tools/week03_threshold_parameter_figure.py; the schematic they replaced is gone. Worth doing live if the room is with you: the Geoprocessing pane only re-reads a model's parameters after the model is saved and the tool re-opened, which is a good thing to have hit once yourself before thirty students hit it. -->

---

# One tool, five answers

<div class="columns" style="grid-template-columns: 1.05fr 0.95fr; align-items: center;">
<div style="font-size:0.88em;">

Same model, same data, five runs of the tool dialog:

| Threshold | Square miles | Share of county |
| --- | ---: | ---: |
| 0.3 | 1,327 | 63 % |
| 0.4 | 1,111 | 53 % |
| 0.5 | 917 | 44 % |
| 0.6 | 722 | 34 % |
| 0.7 | 496 | 24 % |

</div>
<div style="font-size:0.88em;">

- A parameter turns *"is 0.4 right?"* from an opinion into a table you can put in a report
- The area falls by more than half across the range. Any recommendation that does not say which threshold it used is not a recommendation
- **Exercise 1**, in a few minutes, is three rows of this table, built by you. Lab 2 Step 6 wants the rest

</div>
</div>

<!-- These are the Part A numbers, repeated on purpose: Tuesday they were a result you were shown, today they are a result you produce. Computed from the course extract with the same Con() expression the lab uses; they match the lab page's check values at 0.4 and 0.6. The forest never drops out before the fields do, which is the honest answer to whether one threshold can map irrigation. -->

---

# The three exercises

<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:0.6em 0;">
<div style="background:#eef3f9;border-top:8px solid #e8792b;border-radius:8px;padding:0.7em 0.9em;"><div style="font-size:1.4em;font-weight:800;color:#e8792b;">1</div><div style="font-weight:700;">One expression, three thresholds</div><div style="font-size:0.78em;color:#5a6472;margin-top:0.3em;">Con() in the Raster Calculator. <em>Local.</em></div></div>
<div style="background:#eef3f9;border-top:8px solid #002e5d;border-radius:8px;padding:0.7em 0.9em;"><div style="font-size:1.4em;font-weight:800;color:#002e5d;">2</div><div style="font-weight:700;">Neighborhoods</div><div style="font-size:0.78em;color:#5a6472;margin-top:0.3em;">Focal Statistics at a field edge. <em>Focal.</em></div></div>
<div style="background:#eef3f9;border-top:8px solid #e8792b;border-radius:8px;padding:0.7em 0.9em;"><div style="font-size:1.4em;font-weight:800;color:#e8792b;">3</div><div style="font-weight:700;">Zones</div><div style="font-size:0.78em;color:#5a6472;margin-top:0.3em;">Zonal Statistics as Table by tract. <em>Zonal.</em></div></div>
</div>

One exercise per family, about fifteen minutes each. Two optional ones are at the end for anyone who finishes early.

<!-- Say the family out loud each time a tool runs: this is local, this is focal, this is zonal. That is the reading's organizing idea and it is what the quiz can ask about. The point of the hour is breadth — that the Spatial Analyst toolbox is large and organized — not depth in any one tool. Terrain and hydrology are deliberately absent; they are Weeks 5 and 6. -->

---

<!-- _class: lead -->

# Exercise 1
## One expression, three thresholds

---

# The Raster Calculator

<div class="columns" style="grid-template-columns: 1.1fr 0.9fr; align-items: center;">
<div>

1. Search for **Raster Calculator** (Spatial Analyst)
2. In the expression box type, with the quotes:
   `Con("NDVI" >= 0.4, 1, 0)`
   Double-click a layer in the *Rasters* list to insert it correctly
3. Output `NDVI_class_04`, then **Run**
4. Open the output's attribute table: two rows, **Count** for 0 and for 1

**Write down:** the square miles at 0.4. The lab page has the check value; do you match it?

</div>
<div style="text-align:center;">

![h:470](images/ra-raster-calculator.png)

</div>
</div>

<!-- The Geoprocessing-pane Raster Calculator, ArcGIS Pro 3.7.1. Con reads: where the condition is true, 1, otherwise 0. This is the paper exercise from Part A with a real raster in place of A. The check value at 0.4 is on the lab page (about 3,197,000 cells, 1,111 square miles, 53 percent of the county); a different number usually means the model's environments changed the extent or cell size. Cells times 900 square meters divided by 2,589,988 gives square miles. -->

---

# Now change the number twice

<div class="columns" style="grid-template-columns: 1fr 1fr;">
<div style="font-size:0.88em;">

- Run the same expression at **0.3** and at **0.6**, changing only the number and the output name
- Two runs, about fifteen seconds each. Doing the whole sweep is why Lab 2 exposes the threshold as a **parameter**
- Fill three rows of the table on the activity sheet

**Write down:** whether the **mountain forest** above Provo is still in class 1 at 0.6

</div>
<div style="font-size:0.88em;">

| Threshold | Square miles | Share |
| --- | ---: | ---: |
| 0.3 | | |
| 0.4 | 1,111 | 53 % |
| 0.6 | | |

- Turn the layers on and off over the imagery basemap to answer the forest question
- These three rows are a start on **Lab 2 Step 6**; the lab asks for more

</div>
</div>

<!-- Instructor's answers, computed from the course extract on Sept 9, 2026: 0.3 gives 1,327 square miles (63 percent) and 0.6 gives 722 (34 percent). The forest never drops out before the fields do: at 0.6 the Wasatch canopy is still in the class while the pivots are thinning. That is the honest answer to Lab 2's third question, and the reason the lab suggests adding elevation or a second date. Leave the table blank on the slide; the numbers are theirs to find. Two extra runs rather than four keeps this to fifteen minutes; the lab is where the full sweep happens. -->

---

<!-- _class: lead -->

# Exercise 2
## Neighborhoods

---

# Focal Statistics

<div class="columns" style="grid-template-columns: 1.05fr 0.95fr; align-items: center;">
<div style="font-size:0.9em;">

1. Search for **Focal Statistics** (Spatial Analyst)
2. Input **NDVI**; neighborhood **Rectangle, 5 by 5 cells**; statistic **Mean**; output `NDVI_focal5_mean`. Run
3. Zoom to the pivots near **Elberta** (Map ▸ Go To XY: 111.95 W, 39.95 N, scale **1:50,000**) and flip between NDVI and the mean

**Write down:** the NDVI of one cell on the **edge** of a pivot, before and after, from the Explore tool pop-up

</div>
<div style="text-align:center;">

![h:440](images/ra-focal-statistics.png)

</div>
</div>

<!-- Focal: a window of cells in, one cell out. Five by five is twenty-five cells. One run rather than two: the 3 by 3 added a size comparison that the next slide makes anyway. Ask what the window does at the county boundary: with Ignore NoData checked it averages whatever data are in the window; unchecked, the border cells become NoData. -->

---

# What a mean does to an edge

<div class="columns" style="grid-template-columns: 1fr 1fr;">
<div style="text-align:center;">

![w:560](images/ra-pivots-ndvi.png)

**NDVI**, 30 m cells

</div>
<div style="text-align:center;">

![w:560](images/ra-pivots-focal5.png)

**5 × 5 mean**, the same cells

</div>
</div>

- The pivots are still there, and the road, but every **edge** is now a ramp instead of a step
- Smoothing removes noise and it removes real detail with it. A smoothed DEM makes a worse slope map (Week 5)
- Try the same window with **Majority** on your classified raster: speckle disappears, and the class area moves

<!-- Both captures are the Lab 2 NDVI at the Elberta pivots in ArcGIS Pro 3.7.1, 1:50,000. Ask which one they would use to count pivots, and which to draw a field boundary. The majority filter on the 0.4 class raster grows class 1 from 1,111 to about 1,133 square miles: it fills holes inside fields and rounds off corners, which is a design decision, not a free clean-up. -->

---

<!-- _class: lead -->

# Exercise 3
## Zones

---

# Zonal Statistics as Table

<div class="columns" style="grid-template-columns: 1.05fr 0.95fr; align-items: center;">
<div style="font-size:0.88em;">

1. Zones: the **Utah County census tracts** from your Lab 1 project. Drag them into this map
2. Search for **Zonal Statistics as Table** (Spatial Analyst)
3. Zone data the tracts, zone field the tract id; value raster **NDVI**; output `NDVI_by_tract`; statistics **Mean**. Run
4. Open the table from **Standalone Tables** in the Contents pane and sort by **MEAN**

**Write down:** the greenest and the least green tract by mean NDVI

</div>
<div style="text-align:center;">

![h:420](images/ra-zonal-statistics.png)

</div>
</div>

<!-- Zonal: every cell that shares a zone value in, one number per zone out. Tracts rather than the UGRC municipal boundaries so nobody spends the exercise on a download; the tracts are already on their disk from Lab 1. If you would rather use cities, the boundaries are at gis.utah.gov and the next slide's table is by city. Statistics "Mean" rather than "All" keeps the output narrow enough to read on screen. -->

---

# One number per zone, not per cell

![w:700 center](images/ra-zonal-idea.svg)

<div style="font-size:0.9em;">

- The zones can be any polygons, or any integer raster: cities, census tracts, the classified NDVI itself
- Zonal Statistics as Table writes a **table** you can join back to the polygons and map
- Compare with focal: a window moves and writes a value at every cell; a zone stands still and writes one row

</div>

<!-- The bridge between the tool dialog and the table on the next slide. Ask what "mean NDVI of Provo" leaves out: everything about where inside Provo the green is. That is the price of a zonal summary, and the reason the standard deviation column is worth reading. -->

---

# Optional: the same thing by city

<div class="columns" style="grid-template-columns: 1fr 1fr; font-size:0.85em;">
<div>

Download the Utah Municipal Boundaries from [UGRC](https://gis.utah.gov/products/sgid/boundaries/municipal/) and run Zonal Statistics as Table again, zone field **NAME**. The instructor's run, July 2025 mean NDVI:

**Least green**

| City | Mean |
| --- | ---: |
| Vineyard | −0.03 |
| Eagle Mountain | 0.21 |
| Fairfield | 0.22 |

</div>
<div>

**Greenest**

| City | Mean |
| --- | ---: |
| Woodland Hills | 0.56 |
| Draper (county part) | 0.54 |
| Spring Lake | 0.52 |

![w:420 center](images/ra-zonal-table.png)

</div>
</div>

<!-- Was exercise 4's third slide; now optional, because the download is the slow part. Vineyard's mean is negative because a third of its polygon is Utah Lake, at minus one in the extract. Eagle Mountain and Fairfield are Cedar Valley: dry benches and new subdivisions. The greenest are bench towns with mature trees, and Woodland Hills has forest inside the boundary. Provo is in the middle at 0.42 with the largest standard deviation, 0.29, because it contains everything from the lake to the canyon. Ask what a mean NDVI per city actually measures: tree canopy and lawn, not agriculture. Numbers from tools/week03_prep.py on the course extract, Sept 9, 2026. -->

---

# Optional: an edge detector

<div class="columns" style="grid-template-columns: 1fr 1fr; align-items: center;">
<div>

- **Focal Statistics** again on NDVI: 3 by 3, statistic **Range**, output `NDVI_focal3_range`
- The range is the biggest difference inside the window: near zero in the middle of a field or a lake, large wherever NDVI changes fast
- Symbolize it and look at Elberta: the pivots become **rings**, the canals become lines
- This is the idea behind every edge filter and behind slope: a focal function on how fast the surface changes

</div>
<div>

![w:520 center](images/ra-focal-window.svg)

</div>
</div>

<!-- For anyone ahead. On the course extract the range is zero to 1.87 with a mean of 0.15; the maxima are field edges against bare soil and the lake shore. Slope in Week 5 is the same idea with elevation instead of NDVI and a derivative instead of a range. -->

---

# What you have

<div class="columns" style="grid-template-columns: 1fr 1fr;">
<div>

**On the activity sheet, uploaded by 9:30 am:**

1. Square miles at 0.4, 0.3 and 0.6, and the forest answer
2. One edge cell before and after the 5 × 5 mean
3. Greenest and least green tract

**In your Lab 2 project:** three rows of the Step 6 sweep, and the classified rasters to keep going with

</div>
<div>

**The families, once more**

- **Local**: Con and Reclassify today; Float, Minus, Plus and Divide in the Lab 2 model
- **Focal**: Focal Statistics, and in Week 5, Slope and Aspect
- **Zonal**: Zonal Statistics as Table
- **Global**: Week 6, when a DEM becomes a watershed

</div>
</div>

<!-- Close by naming the family of every tool they ran today. If the quiz asks which family Reclassify belongs to, or what Focal Statistics does at the edge of a raster, they have run both. The Spatial Analyst toolbox has far more than these; the point of the hour was that it is organized, and that terrain and hydrology are the next two weeks. -->

---

# Before Next Class

![bg right:34% w:94%](images/ra-lab2-example-map.png)

- **Lab 2 — NDVI** is due **Saturday 11:59 pm**: [assignments/lab-02](https://byu-hydroinformatics.github.io/ce414-gis-applications/assignments/lab-02/). Step 6 needs the full sweep; you have three of its rows. The two maps and the rubric self-assessment are what remain
- **Today's activity sheet**, with your three numbers, is due on Learning Suite by **9:30 am**
- **Reading**: Chapter 10 of *GIS Fundamentals* (Topics in Raster Analysis)
- **Quiz 3**, open book, on Learning Suite, due **Saturday 11:59 pm**
- **Office hours**: [calendly.com/dan-ames/office-hours](https://calendly.com/dan-ames/office-hours)

<!-- Remind them that the sweep table started in exercise 1 is a required Lab 2 deliverable and needs finishing, and that the map they choose for the scenario should be the run that most changes what a reader would conclude. -->

<!--
Authoring notes (2026-09-09): Part B of the Week 3 pair, for the Thursday session. It combines
Part 4 of the former "Raster Analysis and Map Algebra" deck (local, focal, zonal, global; moving
windows; kernels; the Spatial Analyst toolbox) with the whole of the former raster-hands-on.md,
plus two new slides on the threshold as a model parameter. The split was made on 2026-09-09 at the
instructor's request, immediately after the NDVI material in Part A.
- NEW on 2026-09-09: the "threshold as a parameter" section, which the week page had promised
  ("the NDVI model as a tool with a threshold parameter") but no deck carried. Its figure,
  ra-threshold-parameter.svg, is a hand-drawn schematic and says so on the figure; a real ArcGIS Pro
  capture of the model beside its tool dialog would be better. TODO(instructor). The right-click
  wording is stated as it is in the Week 2 Part B deck and is marked VERIFY on the slide's notes.
- CUT TO THREE EXERCISES on 2026-09-09 at the instructor's request: there was not time for four,
  and the goal of the hour is breadth across the raster tool families rather than depth. The
  integer-trap exercise went, because Part A already teaches integer versus float and it was the
  one exercise that taught a bug rather than a family. What remains is one per family: Con() in the
  Raster Calculator (local), Focal Statistics (focal), Zonal Statistics as Table (zonal). The
  threshold sweep dropped from five runs to three, the focal exercise from two windows to one, and
  the zonal exercise now uses the Lab 1 census tracts, already on the students' disks, instead of a
  UGRC download. The city version of the zonal table and the edge detector are both optional slides
  at the end, so the material is still there for a year with more time.
- Every exercise runs on data students already have: the Lab 2 Utah County extract and the Lab 1
  census tracts. The optional city version needs the UGRC municipal boundaries (link checked
  Sept 9, 200).
- Results were computed headlessly first with tools/week03_prep.py into C:\Ames\Week03\Week03.gdb,
  so the speaker notes carry real numbers: integer division gives -1 on 138 sq mi, 0 on 1,961 sq mi,
  1 on 48 cells; the threshold sweep is 1,327 / 1,111 / 917 / 722 / 496 sq mi at 0.3 to 0.7; the
  5 x 5 majority of the 0.4 class covers 1,133 sq mi; mean NDVI by municipality runs from Vineyard
  (-0.03) to Woodland Hills (0.56).
- ArcGIS Pro 3.7.1 captures (Sept 9, 175 % scaling, C:\Ames\Lab02\Lab02.aprx, project closed
  without saving): the integer-division result with its Contents pane, the Raster Calculator, Focal
  Statistics and Zonal Statistics as Table panes (each stitched from two scrolled grabs), the zonal
  table panel, the Spatial Analyst toolset list, and the Elberta pivots in NDVI and in the 5 x 5
  mean at 1:50,000.
- The sweep table on the exercise slide is deliberately blank except for the 0.4 check value the lab
  already gives; the filled table on the parameter slide is the instructor's own run.
- The Thursday activity (the numbers sheet) needs a matching Learning Suite item; the Excel
  map-algebra activity stays on Tuesday.
-->
