# Midterm 1 Study Guide

**Midterm 1** is a closed-book, concept-based exam in the Testing Center, 100 points. It opens
**Tuesday of Week 8 at 8:00 am** and closes **Thursday at 9:00 pm**; the Testing Center charges a late
fee from 2:00 pm Thursday, so go earlier. It covers **Weeks 1–7**.

**Conditions.** Paper and pencil, closed book and closed notes, with no computer, phone or other
device. **Bring a calculator**: any calculator is allowed, as long as it is not a phone. You have
**3 hours**, which is plenty: most students should finish in about half that.

**What the exam looks like.** **100 multiple-choice questions, 1 point each.** Every question has
four options and exactly one best answer. The questions are grouped by week, Week 1 through Week 7.
Some are built on ArcGIS Pro screenshots from the labs and lectures; some ask you to compare four
figures (grids, maps or triangulations) and pick the right one; and some are short hand
calculations of the kind worked in class. You write your answers on an **answer sheet**, the last
page of the exam booklet, and only the answer sheet is scored. Circle answers and do scratch work in
the booklet as you go, but leave time at the end to copy every letter onto the sheet.

## How to study for this exam

- **Take your Learning Suite reading quizzes again.** A good number of questions come straight from
  them. If you studied those quizzes closely, you will recognize those questions.
- **Retake the self-check quizzes** linked under each week below. Many exam questions test the same
  ideas, in different words.
- **Reread each lab's warnings and "Check the result" boxes.** Several questions are about the
  mistakes those boxes warn about: the setting that changes the answer without an error message, the
  wrong field type, the wrong units, the default you were told to change. For each lab, be able to
  say what the model does, why each tool is there, and what the sensitivity step showed.
- **Practice the hand calculations.** The slope formulas and the D8 direction codes are printed on
  the exam, so practice *using* them rather than memorizing them. Work a `Con()` grid that has
  NoData in it, slope at a cell by both methods, a D8 direction (remember that a diagonal neighbor
  is farther away than a side neighbor), and flow accumulation by the Esri convention. Bring your
  calculator.
- **Read all four options before you choose.** The wrong options are mostly the mistakes students
  really make, so an option that looks right at first glance may be one of them.
- **Pace yourself.** 100 questions in 3 hours is almost two minutes each, with time left over to
  fill in the answer sheet.

**How to use the weekly lists.** Each week lists what you should be able to do. Turn every line into
a question and answer it out loud without notes. If you cannot, open that week's slides (press
<kbd>P</kbd> for the speaker notes, which carry the explanations) and the self-check quiz.

## Week 1 — Data Models

*Reading:* Bolstad, Chapters 1 and 2. *Slides:* [Data Models Refresher](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-01/data-models-refresher.html). *Self-check:* [Data Models](../quizzes/data-models/index.html).

- Explain what it means to call a GIS dataset a **model** — an abstraction chosen for a purpose
- Distinguish the **vector**, **raster** and **TIN** data models, and say when each is appropriate
- Separate a **data model** from its **file format** (vector vs. shapefile vs. geodatabase)
- Say what the saying “raster is faster, but vector is correcter” means
- Convert a latitude in degrees, minutes and seconds to **decimal degrees**
- From the reading: define **topology**, and the GIS terms in Chapters 1 and 2

## Week 2 — ModelBuilder

*Reading:* Chapter 13. *Slides:* [Part A](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-02/modelbuilder-a.html), [Part B](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-02/modelbuilder-b.html). *Self-check:* [ModelBuilder Basics](../quizzes/modelbuilder-basics/index.html), [Model Parameters](../quizzes/model-parameters/index.html). *Lab:* [Lab 1](../assignments/lab-01/README.md).

- Say what a **model** is, and when to reach for **ModelBuilder** instead of running tools one at a time
- Read a ModelBuilder canvas: inputs, tools, outputs, and what the **environments** decide
- Turn a model variable into a **parameter** so the model runs as a tool, and say why that matters
- Read the state of a model from its canvas: what a **green check** and a **gray** element mean, and where to start fixing
- Say why a model can need its data **projected** before a buffer, and what the **dissolve** option changes
- Judge when a smaller model is the better model; write **metadata** someone else can use
- For Lab 1: the order of the tools that built the density field, why it had to be **Double**, and which Boolean idea the **Erase** step carries out
- From the reading: classify a model as **cartographic**, **simple spatial** or **spatio-temporal**, and tell **ranking** from **weighting**; write site criteria as a **Boolean** expression (AND, OR, NOT); tell a **general** criterion from a **refined** one; say why most cartographic models are **temporally static**

## Week 3 — Raster Analysis

*Reading:* Chapter 10. *Slides:* [Part A](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-03/raster-analysis-a.html), [Part B](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-03/raster-analysis-b.html). *Self-check:* [Raster Types](../quizzes/raster-types/index.html), [Raster Functions](../quizzes/raster-functions/index.html). *Lab:* [Lab 2](../assignments/lab-02/README.md).

- Say whether a cell's number is a **measurement** or a **label**
- Define **map algebra**; name the four things that must line up before two rasters combine, and what **integer division** does to a ratio
- Write the **NDVI** equation and say why red and near-infrared are the two bands
- Put a tool in the right family — **local**, **focal**, **zonal**, **global** — and say what **Zonal Statistics as Table** gives back
- Read a `Con()` expression and say what area it classifies, including where an input is **NoData**; say why Lab 2 uses `Con()` rather than a Reclassify table
- From the reading: say what a smoothing, a high-pass and a **majority** filter do; say what a **null** cell does in map algebra, and how Boolean map algebra treats zero and non-zero values

## Week 4 — Georectifying and Remote Sensing

*Reading:* Chapter 6. *Slides:* [Georectifying Images](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-04/georectifying-images.html), [Remote Sensing](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-04/remote-sensing.html). *Self-check:* [Georectifying](../quizzes/georectifying/index.html), [Remote Sensing](../quizzes/remote-sensing/index.html). *Lab:* [Lab 3](../assignments/lab-03/README.md).

- Say what it means to **georectify** an image and what a georectified raster stores
- Name the order **georectify → digitize → analyze**, and why
- Say where **control points** belong, and why their spread beats their number; read a **residual** and a **total RMS error**, and why a small one proves nothing
- Find visible, **near-infrared**, **thermal** and radar on the spectrum, and say why healthy leaves are bright in near-infrared
- Split a color image into **bands**, read a **false-color** image, tell **multispectral** from **hyperspectral**, and name the four resolutions a satellite trades off
- For Lab 3: say what it tells you when a feature you digitized lands somewhere it cannot be, even though the RMS error was small
- From the reading: tell a **passive** sensor from an **active** one, and **LiDAR** from **radar**

## Week 5 — Elevation Data and Terrain Analysis

*Reading:* Chapter 11. *Slides:* [Elevation Data and LiDAR](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-05/elevation-data-lidar.html), [Terrain Analysis](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-05/terrain-analysis.html). *Self-check:* [Elevation and LiDAR](../quizzes/elevation-lidar/index.html), [Terrain Analysis](../quizzes/terrain-analysis/index.html). *Lab:* [Lab 4](../assignments/lab-04/README.md).

- Define an **elevation surface** and the ways a **DEM** represents one; say how **LiDAR** measures a surface and what a **return** is
- Name free DEM sources and the **cell size** each gives; choose a cell size for a job
- Explain **slope**, **aspect**, **curvature** and **hillshade**, and compute slope at a cell **by hand** by both methods from class; tell **plan** curvature from **profile** curvature (picture skiing down the hill)
- Explain why cell size, vertical units and the slope algorithm are part of the reported value; say what a **viewshed** is, and how to use viewsheds to find what a place can see
- For Lab 4: the pixel type of the mosaic, the **resampling** method for elevation, **degrees** against **percent** slope, why the towers are clipped to a buffer before Kernel Density, the units of the search radius, and what multiplying two 1/0 rasters gives

## Week 6 — Watersheds

*Reading:* Chapter 10 review. *Slides:* [Part A](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-06/watershed-delineation-a.html), [Part B](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-06/watershed-delineation-b.html). *Self-check:* [Which Way Does Water Go?](../quizzes/watersheds/index.html), [Follow the Water](../quizzes/basins/index.html). *Lab:* [Lab 5](../assignments/lab-05/README.md).

- Walk through the steps that turn a DEM into streams and watersheds: fill, flow direction, flow accumulation, threshold, stream links, pour point
- Tell a cell's **aspect** from its **D8 flow direction**, and compute D8 by hand
- Say what **flow accumulation** counts, how a **threshold** makes streams, and why a watershed is always the watershed **of a point**
- Read **nested hydrologic units**; write a **water balance** and say which term a DEM informs
- For Lab 5: what **Snap Pour Point** does, what each **Stream Link** value identifies, and how a threshold in cells becomes a contributing area
- From the reading: say when a pit in a DEM should be **filled** and when it should be **breached**; why a derived stream can stop at a sink and start again below it; where aspect is a fair stand-in for flow direction; how **D-infinity** splits flow between two neighbors

## Week 7 — Lake Bathymetry and Iterators

*Slides:* [Part A](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-07/lake-bathymetry.html), [Part B](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-07/lake-depth-explorer.html). *Self-check:* [Lake Bathymetry](../quizzes/bathymetry/index.html), [Lake Depth Explorer](../quizzes/iterators/index.html). *Lab:* [Lab 6](../assignments/lab-06/README.md).

- Say why a **terminal lake's level** is its water balance; name four ways a lake bottom is measured
- Explain why a level needs a **vertical datum**, and what mixing two does
- Read an **elevation–area–volume** table, and say why one foot of level is not one foot of lake
- Say what an **iterator** does that running a tool twice does not; use `%Value%` in an expression and an output name (Lab 6 renames it `%Elevation%`); gather a loop's outputs with **Collect Values** and **Merge**
- For Lab 6: how many times a **For** loop runs, what a fixed output name does, why the surface must be in **feet NGVD29**, why the model keeps only the **main pool**, what **Simplify polygons** changes, and which field types hold an elevation and an area
