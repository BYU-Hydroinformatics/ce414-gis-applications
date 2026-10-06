# Midterm 1 Study Guide

**Midterm 1** is a closed-book, concept-based exam in the Testing Center, 100 points. It opens
**Tuesday of Week 8 at 8:00 am** and closes **Thursday at 9:00 pm**; the Testing Center charges a late
fee from 2:00 pm Thursday, so go earlier. It covers **Weeks 1–7**.

**How to use this page.** Each week lists what you should be able to do. Turn every line into a
question and answer it out loud without notes. If you cannot, open that week's slides (press
<kbd>P</kbd> for the speaker notes, which carry the explanations) and the self-check quiz. The labs
are the best review of all: for each one, be able to say what the model does, why each tool is
there, and what the sensitivity step showed.

## Week 1 — Data Models

*Reading:* Bolstad, Chapters 1 and 2. *Slides:* [Data Models Refresher](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-01/data-models-refresher.html). *Self-check:* [Data Models](../quizzes/data-models/index.html).

- Explain what it means to call a GIS dataset a **model** — an abstraction chosen for a purpose
- Distinguish the **vector**, **raster** and **TIN** data models, and say when each is appropriate
- Separate a **data model** from its **file format** (vector vs. shapefile vs. geodatabase)

## Week 2 — ModelBuilder

*Reading:* Chapter 13. *Slides:* [Part A](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-02/modelbuilder-a.html), [Part B](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-02/modelbuilder-b.html). *Self-check:* [ModelBuilder Basics](../quizzes/modelbuilder-basics/index.html), [Model Parameters](../quizzes/model-parameters/index.html). *Lab:* [Lab 1](../assignments/lab-01/README.md).

- Say what a **model** is, and when to reach for **ModelBuilder** instead of running tools one at a time
- Read a ModelBuilder canvas: inputs, tools, outputs, and what the **environments** decide
- Turn a model variable into a **parameter** so the model runs as a tool, and say why that matters
- Judge when a smaller model is the better model; write **metadata** someone else can use

## Week 3 — Raster Analysis

*Reading:* Chapter 10. *Slides:* [Part A](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-03/raster-analysis-a.html), [Part B](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-03/raster-analysis-b.html). *Self-check:* [Raster Types](../quizzes/raster-types/index.html), [Raster Functions](../quizzes/raster-functions/index.html). *Lab:* [Lab 2](../assignments/lab-02/README.md).

- Say whether a cell's number is a **measurement** or a **label**
- Define **map algebra**; name the four things that must line up before two rasters combine, and what **integer division** does to a ratio
- Write the **NDVI** equation and say why red and near-infrared are the two bands
- Put a tool in the right family — **local**, **focal**, **zonal**, **global** — and say what a moving window does to an edge
- Read a `Con()` expression and say what area it classifies

## Week 4 — Georectifying and Remote Sensing

*Reading:* Chapter 6. *Slides:* [Georectifying Images](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-04/georectifying-images.html), [Remote Sensing](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-04/remote-sensing.html). *Self-check:* [Georectifying](../quizzes/georectifying/index.html), [Remote Sensing](../quizzes/remote-sensing/index.html). *Lab:* [Lab 3](../assignments/lab-03/README.md).

- Say what it means to **georectify** an image and what a georectified raster stores
- Name the order **georectify → digitize → analyze**, and why
- Say where **control points** belong, and why their spread beats their number; read a **residual** and a **total RMS error**, and why a small one proves nothing
- Find visible, **near-infrared**, **thermal** and radar on the spectrum; say what an **atmospheric window** is
- Split a color image into **bands**, read a **false-color** image, tell **multispectral** from **hyperspectral**, and name the four resolutions a satellite trades off

## Week 5 — Elevation Data and Terrain Analysis

*Reading:* Chapter 11. *Slides:* [Elevation Data and LiDAR](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-05/elevation-data-lidar.html), [Terrain Analysis](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-05/terrain-analysis.html). *Self-check:* [Elevation and LiDAR](../quizzes/elevation-lidar/index.html), [Terrain Analysis](../quizzes/terrain-analysis/index.html). *Lab:* [Lab 4](../assignments/lab-04/README.md).

- Define an **elevation surface** and the ways a **DEM** represents one; say how **LiDAR** measures a surface and what a **return** is
- Name free DEM sources and the **cell size** each gives; choose a cell size for a job
- Explain **slope**, **aspect**, **curvature** and **hillshade**, and compute slope at a cell **by hand**
- Explain why cell size, vertical units and the slope algorithm are part of the reported value; say what a **viewshed** is

## Week 6 — Watersheds

*Reading:* Chapter 10 review. *Slides:* [Part A](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-06/watershed-delineation-a.html), [Part B](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-06/watershed-delineation-b.html). *Self-check:* [Which Way Does Water Go?](../quizzes/watersheds/index.html), [Follow the Water](../quizzes/basins/index.html). *Lab:* [Lab 5](../assignments/lab-05/README.md).

- Walk through the steps that turn a DEM into streams and watersheds: fill, flow direction, flow accumulation, threshold, stream links, pour point
- Tell a cell's **aspect** from its **D8 flow direction**, and compute D8 by hand
- Say what **flow accumulation** counts, how a **threshold** makes streams, and why a watershed is always the watershed **of a point**
- Read **nested hydrologic units**; write a **water balance** and say which term a DEM informs

## Week 7 — Lake Bathymetry and Iterators

*Slides:* [Part A](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-07/lake-bathymetry.html), [Part B](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-07/lake-depth-explorer.html). *Self-check:* [Lake Bathymetry](../quizzes/bathymetry/index.html), [Lake Depth Explorer](../quizzes/iterators/index.html). *Lab:* [Lab 6](../assignments/lab-06/README.md).

- Say why a **terminal lake's level** is its water balance; name four ways a lake bottom is measured
- Explain why a level needs a **vertical datum**, and what mixing two does
- Read an **elevation–area–volume** table, and say why one foot of level is not one foot of lake
- Say what an **iterator** does that running a tool twice does not; use `%Value%` in an expression and an output name; gather a loop's outputs with **Collect Values** and **Merge**
