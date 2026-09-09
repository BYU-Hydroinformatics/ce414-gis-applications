---
marp: true
theme: ce414
paginate: true
footer: "CE 414 · Week 3 — Raster Analysis and Map Algebra"
---

<!-- _class: lead -->
<!-- _paginate: skip -->

![bg right:45% w:92%](images/ra-raster-grid-concept.jpg)

![w:130](../theme/images/byu-medallion.svg)

# Raster Analysis and Map Algebra

## NDVI as your first raster model

CE 414 Engineering Applications of GIS
Civil & Construction Engineering, Brigham Young University

Dr. Dan Ames

<!-- Week 3, Tuesday. Two decks this week: today is the concepts and the first raster model, Thursday is hands-on raster analysis in ArcGIS Pro on the Lab 2 data. Everything today points at Lab 2, which is NDVI, which is map algebra on two bands of a satellite image. By the end of class every student should be able to say what the NDVI model does cell by cell, and why the Lab 2 model has a Float step. -->

---

# Today's Goals

![bg right:32% w:88%](images/ra-continuous-grid-stack.png)

<div style="font-size:0.88em;">

By the end of class you should be able to:

- Say what one raster cell stores, and whether that number is a **measurement** or a **label**
- Define **map algebra** and state the rule: *same cell in, same cell out*
- Name the four things that must line up before two rasters can be combined, and what **integer** division does to a ratio
- Write the **NDVI** equation, explain why **red** and **near-infrared** are the two bands, and read it as a **local** raster function
- Recognize the Lab 2 model as that equation, tool by tool
- Tell **local**, **focal**, **zonal** and **global** functions apart

</div>

<!-- Set expectations. Part 1 is a short refresher, Week 1 did the data model. Part 2 is map algebra, with the Excel activity in the middle of it. Part 3 is NDVI, built up from the physics to the Lab 2 model. Part 4 is the taxonomy of raster functions that Thursday's exercises walk through. -->

---

# Where this sits

<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:0.8em 0 0.6em 0;">
<div style="background:#eef3f9;border-top:8px solid #5a6472;border-radius:8px;padding:0.7em 0.8em;"><div style="font-weight:800;color:#5a6472;">Week 1</div><div style="font-size:0.8em;">Data models: a raster is a grid of numbers</div></div>
<div style="background:#eef3f9;border-top:8px solid #5a6472;border-radius:8px;padding:0.7em 0.8em;"><div style="font-weight:800;color:#5a6472;">Week 2</div><div style="font-size:0.8em;">ModelBuilder: chain tools, expose parameters</div></div>
<div style="background:#eef3f9;border-top:8px solid #e8792b;border-radius:8px;padding:0.7em 0.8em;"><div style="font-weight:800;color:#e8792b;">Today</div><div style="font-size:0.8em;">Raster analysis: math on the grid, and NDVI as the first model</div></div>
<div style="background:#eef3f9;border-top:8px solid #002e5d;border-radius:8px;padding:0.7em 0.8em;"><div style="font-weight:800;color:#002e5d;">Thursday and Lab 2</div><div style="font-size:0.8em;">Hands-on raster analysis; the NDVI model as a tool with a threshold parameter</div></div>
</div>

- Lab 1 was **vector** analysis: buffers, intersects, an erase, on features with attribute tables
- Lab 2 is **raster** analysis: the same idea of a model, but every operation is arithmetic on cells
- The vocabulary from Week 2 carries straight over: data, tool, derived data, parameter

<!-- One slide to place the week. Nothing new in ModelBuilder this week; the new thing is what the tools do to a grid. Say out loud that the Lab 2 model is six tools long and that four of them are arithmetic. -->

---

<!-- _class: lead -->

# Part 1
## A raster is a grid of numbers

---

# What is raster data?

<div class="columns">
<div>

- A **regularly spaced grid** of numeric values; grid cells are pixels
- One cell holds **one number**. No shape, no boundary, no attribute table row of its own
- The cell size is the resolution: **30 m** for the Landsat bands in Lab 2, so every cell is 900 square meters
- Zoom in far enough on any image and it stops being a picture and becomes a table of numbers
- [datacarpentry.org — Introduction to Raster Data](https://datacarpentry.org/organization-geospatial/01-intro-raster-data/)

</div>
<div>

![w:560 center](images/ra-raster-grid-concept.jpg)

</div>
</div>

<!-- Source: Data Carpentry, Introduction to Raster Data. Ask: what is the smallest thing this dataset can tell you about? Answer: one cell. That is why cell size is the first question about any raster. Week 1 covered the data model; this is one slide of reminder. -->

---

# Is the number a measurement or a label?

![bg right:45% w:88%](images/ra-landuse-and-elevation.jpg)

- Same area, two very different rasters
- **Land use** (top): a handful of values, each standing for a category. Averaging code 4 and code 8 is meaningless
- **Elevation** (bottom): a continuous surface, high 532 to low 299. Averaging two elevations is sensible
- The answer decides which operations are legal, how to symbolize it, and how to **resample** it: nearest neighbor for labels, bilinear or cubic for measurements
- NDVI is a measurement. The classified NDVI map in Lab 2 is a label

<!-- This is the one distinction from the old discrete-versus-continuous slides that matters for analysis. It comes back on the resampling slide and again in Lab 2 Step 3, where Reclassify turns a measurement into a label. -->

---

# NoData is not zero

<div class="columns">
<div>

![w:430 center](images/ra-real-world-to-raster.jpg)

![w:430 center](images/ra-discrete-raster-value-table.jpg)

</div>
<div>

- A cell with **no value** is NoData, shown gray here, and stored separately from every real number
- NoData is not zero: zero elevation is sea level, zero NDVI is bare rock; NoData is *we do not know*
- Every tool this week treats it the same way: **anything combined with NoData is NoData**, and statistics skip it
- The Lab 2 extract has NoData outside the county, so the county boundary in your results is where the data stop, not a line anyone drew

</div>
</div>

<!-- Top: the real world resolved into a coarse grid of class letters. Bottom: the same idea with a value attribute table, plus the gray NoData class. Point at it now; it comes back in the next four slides and in every analysis they will run. The Lab 2 sanity check (6,040,284 cells with data) is a NoData count in disguise. -->

---

<!-- _class: quiz -->

# A spatial data mantra?

![bg right:35% w:80%](images/ra-raster-or-vector-cartoon.png)

## "Raster is faster but vector is better"

**Is it true?**

- Faster at *what*?
- Better for *what*?
- Which of Lab 1's steps would have been easier on a grid? Which of Lab 2's would be easier on polygons?

<!-- Let them argue for two or three minutes. Push toward: raster wins on continuous surfaces, per-cell math, and whole-area coverage; vector wins on discrete objects, exact boundaries, network problems, and attribute richness. The honest answer is that the data model should follow the phenomenon. A raster operation is an array operation: no topology to traverse, no geometry to intersect, just walk the array. That is why continental-scale analysis is done on grids. -->

---

<!-- _class: lead -->

# Part 2
## Map algebra: arithmetic on the grid

---

# Map algebra

<div class="columns">
<div>

- Map algebra is a **cell-by-cell** combination of raster layers using mathematical operations
  - **Unary**: one layer in, one out
  - **Binary**: two layers in, one out
- Addition, subtraction, multiplication, division, max, min, comparisons: virtually any operation you would find in a spreadsheet
- Every output cell depends **only** on the input cell at the same place

</div>
<div>

![w:520 center](images/ra-map-algebra-arrays.png)

<span style="font-size:0.7em">© Paul Bolstad, *GIS Fundamentals*</span>

</div>
</div>

<!-- (a) is unary: multiply every cell of one layer by 2. (b) is binary: add LayerA to LayerB cell by cell to get Sumlayer. Note the circled cells, 1 + 2 = 3, and say out loud that the two layers had to be the same size, aligned, and in the same coordinate system for that sentence to even mean anything. That is the slide after next. -->

---

# The rule: same cell in, same cell out

![w:1000 center](images/ra-map-algebra-add.svg)

<!-- Walk one cell: row 3, column 2 of A is 2, of B is 3, so the answer is 5, and nothing else on either grid was consulted. Then the hole: B has a NoData cell, so the answer has a NoData cell in the same place. This is the whole of local map algebra; everything else is which operation you put between the grids. -->

---

<!-- _class: activity -->

# In-class activity: Simple Map Algebra in Excel

<div class="columns" style="grid-template-columns: 1.1fr 0.9fr;">
<div>

- Open the workbook from Learning Suite: two small grids and a blank one
- Fill the blank grid with **formulas**, not numbers: `=B3+H3`, then drag across the block
- Then the three variations on the sheet: a **product**, a **comparison** (`=IF(B3>5,1,0)`), and a division with a **blank** cell in one input
- **Upload the workbook to Learning Suite by 9:30 am**, fifteen minutes after class

</div>
<div>

![w:440 center](images/ra-map-algebra-spreadsheet.png)

<span style="font-size:0.7em">© Paul Bolstad, *GIS Fundamentals*</span>

</div>
</div>

<!-- The spreadsheet formula =B3+H3 is map algebra. Drag it across the block and you have run a binary local function. The blank-cell variation is NoData: Excel treats a blank as zero in addition, which is exactly the mistake a raster GIS is built to avoid. Ten minutes. Collect the workbooks through Learning Suite; the point is that they have typed a cell-by-cell expression before they see the Raster Calculator. -->

<!-- Legacy figure: the spreadsheet capture is Bolstad's, Excel 2003-era. Kept as the concept illustration; the activity workbook itself lives on Learning Suite. -->

---

# Predict before you compute

![w:960 center](images/ra-predict-exercise.svg)

<!-- Paper exercise, two minutes, no computer. Con(A > 5, B, 0) reads: where A is greater than 5, take B, otherwise 0. Have them fill in all nine cells, including the one where A is NoData. Then the next slide. -->

---

# The answer

![w:860 center](images/ra-predict-answer.svg)

<div style="font-size:0.9em;">

- **Con** is the workhorse of the Raster Calculator: *condition, value if true, value if false*
- It is a **local** function: nine cells in, nine cells out, no neighbors consulted
- In Lab 2 Step 5 the same expression classifies six million cells: `Con("NDVI" >= 0.4, 1, 0)`

</div>

<!-- The NoData cell is the one most people get wrong: it is not 0, it is NoData, because the condition cannot be evaluated. Then point at the Lab 2 expression: it is this exercise with a real raster in place of A and constants in place of B. -->

---

# Four things that must line up

<div class="columns" style="grid-template-columns: 1.3fr 0.7fr; align-items: center;">
<div style="font-size:0.9em;">

1. **Coordinate system.** Both grids in the same one, or the cells do not even lie on top of each other
2. **Cell size.** A 30 m cell and a 10 m cell have no one-to-one match; the tool resamples one of them
3. **Alignment.** Same origin, so cell edges coincide (the **snap raster** environment)
4. **Extent.** The output covers the **intersection** of the inputs unless you say otherwise

When a tool has to resample, the choice is yours: **nearest neighbor** for labels, **bilinear** or **cubic** for measurements. In Lab 2 the two bands come from one scene, so all four line up by construction. The day you mix a DEM with a Landsat band, none of them do.

</div>
<div style="text-align:center;">

![w:260](images/ra-noncoincident-layers.png)

<span style="font-size:0.7em">© Paul Bolstad, *GIS Fundamentals*</span>

</div>
</div>

<!-- The figure is the failure mode: Layer1 and Layer2 do not share an origin or a cell size, so "cell A plus cell B" has no well-defined answer until you decide what to resample. In ArcGIS Pro these are the Environments: Output Coordinate System, Cell Size, Snap Raster, Extent, Mask. Lab 2 Step 0 opens that dialog on purpose. -->

---

# Integer or float

![w:920 center](images/ra-integer-division.svg)

<!-- The Lab 2 extract stores reflectance as integers, times ten thousand, to keep the files small. Divide two integer rasters and the Divide tool keeps only the whole part: every NDVI between minus one and one becomes zero, and the map is a single flat color. Thursday's first exercise is to do exactly this on purpose and look at the result. The fix is the Float tool, which is Lab 2 Step 1. Raster Calculator division behaves differently (it returns floating point), which is one reason the lab uses the Spatial Analyst tools explicitly. -->

---

# Map algebra as a switch: the 0/1 mask

<div class="columns">
<div>

- Build a grid where water is `0` and land is `1`, then **multiply** it by an elevation grid
  - `0` wherever water was (x × 0 = 0)
  - the original elevation wherever land was (x × 1 = x)
- You *could* add the two grids instead, and the computer would let you. The result would be meaningless
- Better still in ArcGIS Pro: set the water to **NoData**, and those cells drop out of every downstream statistic instead of dragging the mean toward zero

</div>
<div>

![w:470 center](images/ra-grid-multiply-example.png)

</div>
</div>

<!-- A 0/1 grid is a switch. Ask why adding is meaningless: because you would be adding a unitless class code to meters, and every land cell would silently gain one meter of elevation. The Lab 2 classified map is a 0/1 grid; multiply it by anything and you have masked that thing to irrigated land. -->

---

<!-- _class: lead -->

# Part 3
## NDVI: your first raster model

---

# Why red and near-infrared

![w:640 center](images/ra-spectral-signature.svg)

<div style="font-size:0.85em;">

- Chlorophyll **absorbs red** light for photosynthesis, so a healthy leaf reflects very little of it
- The leaf's cell structure **scatters near-infrared** strongly, so reflectance jumps at the **red edge**
- Soil rises gently across both; water absorbs almost everything past red
- Two bands, one on each side of the red edge, separate living vegetation from everything else

</div>

<!-- The single most common misconception: near-infrared here is reflected sunlight, not heat. Thermal infrared is a different, much longer band. Say it out loud; students carry "NIR = heat" into Lab 2. The curves are schematic, after Jensen and after Lillesand, Kiefer and Chipman; the band windows are the Landsat 8 and 9 OLI table on the Lab 2 page. Week 4's remote sensing lecture goes further into the spectrum and sensors; today only needs the red edge. -->

---

# In the red band, vegetation is dark

![bg left:58% contain](images/ra-modis-band1-red.png)

<div style="font-size:0.85em;">

- One MODIS scene over western Europe, one band at a time: this is **0.65 µm**, red
- Healthy vegetation is **dark**, because chlorophyll absorbs red
- Bare ground is brighter; cloud and snow are brightest of all
- A **band** is one wavelength window stored as its own grid of numbers. Landsat gives you nine of them; Lab 2 uses two

</div>

<!-- Borrowed from the Week 4 remote sensing deck so that the physics arrives before the lab instead of after it. Set the pattern: a band is a raster. The red band and the near-infrared band of one scene are two rasters that line up perfectly, which is why NDVI is the ideal first map-algebra problem. -->

---

# The equation, one cell at a time

![w:760 center](images/ra-ndvi-cell.svg)

<div style="font-size:0.9em;">

- NDVI is **normalized**: always between **−1 and +1**, whatever the sensor or the sun angle
- Dense healthy vegetation is high; bare soil and rock sit near zero; water goes negative
- It is a **local** function: red in, near-infrared in, one number out, six million times

</div>

<!-- Read the arithmetic: 0.47 minus 0.09 over 0.47 plus 0.09 is 0.38 over 0.56, which is 0.68. That is a well-watered pivot in July. The point of drawing it as three cells is to connect the equation to Part 2: this is A and B and an expression, nothing more. The normalization is why an index from a drone and an index from Landsat can be compared at all. -->

---

# What NDVI sees in Utah County

![w:1080 center](images/ra-what-ndvi-sees.svg)

<!-- Measured, not asserted: red and NIR reflectance at five places in the July 12, 2025 scene students download for Lab 2. Two things to point at. The forest above Provo scores higher than the irrigated field near Elberta, so NDVI is a greenness index, not an irrigation detector; and a downtown block and a dry bench are almost indistinguishable at 0.27 and 0.24. The lake at minus 0.99 is an artifact of the extract, explained on the lab page. -->

---

# The same model at every scale

<div class="columns" style="grid-template-columns: 1.15fr 0.85fr; align-items: center;">
<div style="text-align:center;">

![h:300](images/mbc-ndvi-us-2015.jpg)

<span style="font-size:0.6em">Source: <a href="https://newsroom.heart.org/file/aitken-ndvi-map-of-the-united-states?action=">newsroom.heart.org</a></span>

</div>
<div style="text-align:center;">

![h:190](images/mbc-ndvi-farm-plot.jpg)

<span style="font-size:0.6em">Drone NDVI of one field. Source: <a href="https://www.pix4d.com/blog/pix4dmapper-optimizing-the-ROI-of-fungicides-with-NDVI">pix4d.com</a></span>

</div>
</div>

<div style="font-size:0.88em;">

- The **equation does not care about the platform**: kilometers per pixel across a continent, centimeters per pixel across one field
- What changes is the cell size and the question. Run it on three dates and difference the results, and it becomes a monitoring tool

</div>

<!-- Left: the United States. The hundredth meridian shows up as a color break without anyone drawing it; ask why the Wasatch Front reads greener than the West Desert forty miles away. Right: a single field from a drone, used to target fungicide. Same two lines of arithmetic. -->

---

# NDVI as a ModelBuilder model

![w:1150 center](images/ra-ndvi-model.svg)

- **Float** both bands so the division keeps its decimals; **Minus** and **Plus** for the numerator and the denominator; **Divide** for the index
- **Reclassify** turns the measurement into a two-class label at a threshold; **Raster Calculator** does the same with `Con()` so the threshold can be a **parameter**
- Every P is something the tool dialog asks for: the two bands, the threshold, the outputs

<!-- This is the finished Lab 2 model, exported from ModelBuilder. Read it left to right with Part 2's vocabulary: four local operations and two classifications. The two classification branches exist because a number typed into a Reclassify table cannot be a model parameter, and a number in a Con() expression can; that is Lab 2 Step 5, and it is why Thursday's threshold sweep takes a minute per run instead of an afternoon. -->

---

# The threshold is a choice, and a raster model makes it cheap to test

<div class="columns" style="grid-template-columns: 0.8fr 1.2fr; align-items: center;">
<div style="text-align:center;">

![h:380](images/ra-lab2-example-map.png)

</div>
<div style="font-size:0.85em;">

Utah County, July 2025, cells at or above the threshold:

| Threshold | Square miles | Share of county |
| --- | ---: | ---: |
| 0.3 | 1,327 | 63 % |
| 0.4 | 1,111 | 53 % |
| 0.5 | 917 | 44 % |
| 0.6 | 722 | 34 % |
| 0.7 | 496 | 24 % |

- The 0.4 in the handout is the county **median**, and it calls the forested Wasatch Front cropland
- Lab 2 Step 6 asks you to run it at three more thresholds and say what drops in and out. Thursday you will do it live

</div>
</div>

<!-- The numbers were computed from the course extract with the same Con() expression the lab uses; they match the lab page's check values at 0.4 and 0.6. The teaching point is not the numbers, it is that a raster model with a parameter turns "is 0.4 right?" from an opinion into a table. The forest never drops out before the fields do, which is the honest answer to whether one threshold can map irrigation. -->

---

<!-- _class: lead -->

# Part 4
## Beyond one cell: local, focal, zonal, global

---

# Four kinds of raster function

<div class="columns">
<div>

- **Local**: one cell in, one cell out. Map algebra, Reclassify, NDVI, Con
- **Focal** (neighborhood): a **window** of cells in, one cell out. Focal Statistics, Filter, Slope, Aspect
- **Zonal**: all the cells sharing a **zone** in, one number per zone out. Zonal Statistics
- **Global**: the whole grid in, every cell out. Euclidean Distance, Flow Accumulation, Distance Accumulation

Thursday is one exercise on each of the first three.

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

<!-- Left: three window shapes and the weights they carry. Right: an input layer with a spike, a high-pass kernel, and the output, with one window position worked out longhand in the middle. A low-pass filter averages the spike away; a high-pass filter makes it stand out. Thursday's third exercise runs a 5 by 5 mean over NDVI and looks at what it does to the edge of a center-pivot field. -->

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

# Thursday: hands-on raster analysis

<div class="columns" style="grid-template-columns: 1fr 1fr;">
<div>

Bring your **Lab 2 project** with the two bands and your NDVI raster. Four short exercises, each ending in a number you write down:

1. **The integer trap.** Minus, Plus and Divide on the raw bands, no Float. What comes out?
2. **One expression, five thresholds.** `Con()` in the Raster Calculator, then the sweep
3. **Neighborhoods.** Focal Statistics on NDVI, and what a mean does to a field edge
4. **Zones.** Zonal Statistics as Table: which city in Utah County is greenest?

</div>
<div style="text-align:center;">

![w:520](images/ra-pivots-ndvi.png)

<span style="font-size:0.7em">The center pivots near Elberta in the Lab 2 NDVI, where exercise 3 happens</span>

</div>
</div>

<!-- Preview so they arrive with the project open. Exercise 2 is Lab 2 Step 6 done live, so anyone who finishes it in class has half of that step done. The numbers they record are the in-class activity for Thursday. -->

---

# Before Next Class

![bg right:34% w:94%](images/ra-lab2-example-map.png)

- **Lab 2 — NDVI** is due **Saturday 11:59 pm**: [assignments/lab-02](https://byu-hydroinformatics.github.io/ce414-gis-applications/assignments/lab-02/). Steps 0 to 3 are within reach tonight; the model is the six tools on the slide you just saw
- **Thursday**: bring the Lab 2 project to class with the two bands and your NDVI raster loaded
- **Reading**: Chapter 10 of *GIS Fundamentals* (Topics in Raster Analysis)
- **Quiz 3**, open book, on Learning Suite, due **Saturday 11:59 pm**
- **Office hours**: [calendly.com/dan-ames/office-hours](https://calendly.com/dan-ames/office-hours)

<!-- Point them at the lab and connect it back: NDVI is the same cell-by-cell arithmetic, run on two bands of the same image rather than two separate grids, so extent and cell size are guaranteed to match. The reading is the local, focal, zonal, global chapter; NDVI itself is not in it, which is why today carried it. -->

<!--
Revision notes (2026-09-09): this deck now merges the Sept 3 "Raster Analysis and Map Algebra" deck (24 slides)
with the Sept 3 "ModelBuilder, Part C" deck (10 slides of NDVI mislabeled as ModelBuilder), which is retired.
32 slides. Structure: a three-slide raster refresher (Week 1 did the data model), map algebra with the Excel
activity, the paper prediction exercise, the four alignment rules, and the integer-division trap; then NDVI
built up from the red edge to the Lab 2 model and the threshold table; then the local/focal/zonal/global
taxonomy, the Spatial Analyst toolbox, and a preview of Thursday's hands-on deck (raster-hands-on.md).
- New figures, generated by tools/week03_grid_figures.py and tools/week03_spectral_signature.py (SVG):
  A + B = C with NoData, the prediction exercise and its answer, integer versus float division, NDVI on one
  cell, the 3 x 3 window, and the schematic spectral-signature curves (labeled schematic, after Jensen and
  Lillesand, Kiefer and Chipman; Landsat 8/9 band windows from the USGS table on the Lab 2 page).
- New ArcGIS Pro 3.7.1 captures (Sept 9, 175 % scaling, C:\Ames\Lab02\Lab02.aprx): the Geoprocessing pane's
  Toolboxes tab with Spatial Analyst Tools expanded, and the Elberta pivots in the Lab 2 NDVI.
- Reused: Lab 2's model diagram, "What NDVI sees" infographic and example map (copied with ra- prefixes);
  the Week 4 MODIS red-band slide and the Bolstad figures from the old deck.
- The threshold table was computed with tools/week03_prep.py from the course extract; 0.4 and 0.6 match the
  lab page's check values.
- Dropped from the old decks: the ArcGIS 9 ArcScene pair, the ArcMap toolbox tree, the uncited scanned
  overlay-transformations figure, the two ARC/INFO DOCELL code slides (one had a variable-name bug), the
  three Montana TRI panels and TRI formula (terrain is Week 5), the low-resolution uncredited Africa NDVI
  pair, and the change-detection figure. The "how many types of model" slide is Week 2 material.
- The Excel map-algebra activity stays on Tuesday per the instructor (Sept 9).
-->
