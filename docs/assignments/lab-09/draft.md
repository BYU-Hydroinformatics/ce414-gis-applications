---
search:
  exclude: true
---

# DRAFT — Lab 9: Interpolation Explorer

**Civil Engineering 414 — Engineering Applications of GIS**

Fall 2026 · Dr. Dan Ames

*Rebuilding a mountain from samples, three ways, and measuring how wrong each one is*

> [!WARNING]
> **This is a draft for review.** It is not linked from the course schedule; the assigned page is
> still the September migration of the Word handout. The plan and the measured numbers are in
> `tools/lab09/PARITY_PLAN.md`.
>
> *Changes to what the lab asks students to do:* one study area (the second DEM is gone); a hosted
> extract and study rectangle instead of "download a DEM and draw a box"; a look at the 3DEP image
> service in Step 1 (the Week 9 tie-in); three methods carried all the way to RMSE instead of seven
> surfaces and seven difference chains; the number of points, the IDW power and the Kriging
> semivariogram exposed as parameters; a Step 10 sensitivity table at a personal random seed with
> 200 independent checkpoints; Map 1 is one comparison sheet; individual work, not pairs; rubric in
> five parts of ten.
>
> *Corrections:* RMSE is the root of the **mean** of the squared errors (the handout's summary left
> out the mean); the coordinate system is named as ArcGIS Pro names it; Figure 1 (a reproduced
> textbook figure) is replaced by a measured profile.
>
> *Figures:* Figures A and B are generated from the data (`tools/lab09/make_svgs.py`); the example
> maps are real ArcGIS Pro layouts (`build_figures.py`); Figure C and every step figure come from a
> GUI build in ArcGIS Pro 3.7.1 at 175 % on October 7, 2026 (`C:\Ames\Lab09GUI\Lab09.aprx`).

## Background

Every elevation model, rainfall map and groundwater surface you will use as an engineer started as
points: survey shots, rain gauges, wells. Something turned those points into a surface, and that
something was an **interpolator**. In Lab 8 you used one (IDW) as a tool, to rebuild the plain under
Big Southern Butte. In this lab the interpolator *is* the subject.

The idea is simple. To estimate a value at one place you look at the samples around it and combine
them: take the nearest one (**Thiessen**, or nearest neighbor), average the nearby ones with the
closest weighted most (**inverse distance weighting**, IDW), or weight them by a model of how fast
values stop resembling each other with distance (**Kriging**). A GIS does this at the center of
every cell of an output raster (Bolstad, *GIS Fundamentals*, Chapter 12). Each method has a
personality, and you can see it in the result: Thiessen makes terraces, IDW makes bull's-eyes around
its samples and can never go above the highest one, Kriging smooths.

What you usually cannot do is check the answer, because the true surface is the thing you do not
have. Here you do. You will sample a real elevation model of Y Mountain at random points, rebuild it
from those points three ways, and subtract each rebuild from the truth, cell by cell. That gives you
a map of where each method fails and one number, the root-mean-square error (RMSE), for how badly.

![An elevation profile across the study area from the valley floor in the west to the ridge in the east. The true DEM rises from about 1,390 m to about 2,700 m. A Thiessen line follows it in flat steps that jump at sample points; an IDW line follows it but sags below the ridges; a Kriging line is smooth and cuts the peak short. Ten sample points within 150 m of the row are marked.](images/lab09-profile.svg)

**Figure B.** One row of cells across the study area, the truth and three surfaces rebuilt from only
250 points. Look at the ridge near kilometer 6.5: no method can put back a peak it never sampled.

How close a rebuild comes depends on choices you make: the method, its parameters, and above all how
many points you give it. In Step 10 you vary them, see how far the RMSE moves, and use what moves to
decide which method you would trust with a surface you cannot check.

> [!IMPORTANT]
> **Your job — see the deliverables below.** Build one ModelBuilder model that samples a DEM,
> rebuilds it by Thiessen polygons, IDW and Kriging, and reports each rebuild's error map and RMSE;
> run it on Y Mountain; test how the number of points and each method's parameters change the
> errors; and make two map sheets.

## Problem Statement

You are given a 1/3 arc-second elevation model of Y Mountain and the valley below it, and a study
rectangle. Using them:

1. Sample the elevation model at random points inside the rectangle.
2. Rebuild the surface from the points by Thiessen polygons, IDW and ordinary Kriging.
3. Map each rebuild's error against the true elevation model, and compute its RMSE.
4. Find out which method and which settings rebuild this mountain best, and where every method fails.

## Analysis Considerations

Every one of these is a decision somebody made, and every one of them can change the answer.

- **The truth.** The elevation model is treated as exact. It is not — it is itself a product of
  interpolation from lidar and older sources — but here it is the reference everything else is
  measured against. Your RMSE says how well you rebuilt the DEM, not how well anything matches the
  ground.
- **The cell size.** Step 2 projects the DEM to 30 m cells, as engineering-scale terrain work often
  does, and every surface is built on that grid. A finer grid would make the truth rougher and the
  errors bigger.
- **The samples.** 2,500 random points in a 60.6 km² rectangle: about one point for every 27 cells.
  Random points cluster in some places and leave gaps in others, and the gaps are where the errors
  are. The points are random, so two runs differ — unless you fix the random seed, which Step 0 does
  so that your numbers match this page. Step 10 then gives you your own seed.
- **The method and its parameters.** Thiessen has none. IDW has a **power** (how fast a sample's
  influence falls off with distance; 2 is the default) and a number of neighbors (12). Kriging has a
  **semivariogram model** (spherical is the default) fitted to the points, and a number of neighbors
  (12). Every default is somebody's guess about a typical surface; Step 10 tests the guesses.
- **The measure of error.** RMSE weights large errors heavily, because it squares them. It is one
  number for the whole rectangle, and most of the rectangle is flat valley floor that every method
  gets right. Look at the error maps, not just the number.
- **The coordinate system.** **NAD 1983 UTM Zone 12N** in meters, so that cells are square and
  distances, which every interpolator depends on, are in meters in every direction.

## Data

> [!IMPORTANT]
> **Set up your folder before you download anything.** On the lab machines, work on the **D:
> drive**: one folder for this class named after you, `D:\Smith\`, and one folder per lab inside
> it, `D:\Smith\Lab09\`. The **C: drive is locked**, and a **network drive** is slow enough to make
> ArcGIS Pro hang. **Never use a space** in a folder or file name you create — raster tools fail on
> them without saying why. **Back up your lab folder at the end of every session.** The full set of
> conventions is on the [ArcGIS Tips and Reminders](../../arcgis-tips.md){ target="_blank" } page.

| Layer | Where it comes from | How you get it |
| --- | --- | --- |
| `YMountain_DEM.tif` | USGS 3D Elevation Program, 1/3 arc-second DEM, tile n41w112 | Prepared extract, hosted here |
| `Lab09.gdb\Study_Area` | Drawn for this course on the 30 m grid of Step 2 | In the same zip |
| 3DEP elevation image service | USGS 3D Elevation Program, served live | A web service you add in Step 1 |

- **Download:** [`lab09-y-mountain.zip`](../../data/lab09-y-mountain.zip) (1.9 MB). Unzip it into
  your Lab09 folder — the files are in a `lab09-y-mountain` folder inside it — and read
  `READ-ME-FIRST.txt`.

> [!TIP]
> **Check the data:** `YMountain_DEM.tif` is **1,188 columns × 756 rows** of 1/3 arc-second cells,
> values **1,368.0 to 2,896.9** (meters above NAVD 88), GCS North American 1983, no NoData cells.
> `Study_Area` is one rectangle of **60.6 km²** (8.67 × 6.99 km) in NAD 1983 UTM Zone 12N.

![Infographic: the six metadata questions — What, Where, When, Why, How and Who — answered for the Y Mountain DEM: bare-earth elevation in meters above NAVD 88 on 1/3 arc-second cells, about 10.3 m north-south and 7.9 m east-west; Provo and the mountain front east of it, stored in latitude and longitude and projected in Step 2; tile n41w112 published May 20, 2026 from sources collected 1946 to 2023; the 3D Elevation Program's general-purpose seamless layer, playing the truth in this lab; a window cut from the tile with values unchanged; USGS, public domain. A footer says the DEM's own errors never show up in the RMSE.](images/lab09-dem-metadata.svg)

**Figure A.** The six metadata questions, applied to the DEM. Confirm three of the values yourself —
the publication and source dates, the vertical datum and units, and the cell size —
in `READ-ME-FIRST.txt`, in the raster's properties in ArcGIS Pro, and in the tile's
[metadata file](https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/n41w112/USGS_13_n41w112.xml){ target="_blank" }
— and say in your report what each one does to your result.

## ModelBuilder Tools

New in this lab:

| Tool | What it does |
| --- | --- |
| ![Create Thiessen Polygons icon: five points, each inside the polygon of the area nearest to it](images/icon-create-thiessen-polygons.svg){ .tool-icon }<br>**Create Thiessen Polygons** (Analysis) | Draws, around every point, the polygon of all the places nearer to it than to any other point. Given the points' values, it is nearest-neighbor interpolation. Needs an Advanced license. [Tool reference](https://pro.arcgis.com/en/pro-app/latest/tool-reference/analysis/create-thiessen-polygons.htm){ target="_blank" } |
| ![Kriging icon: a semivariogram, points rising with distance and leveling off at a sill, with the range marked](images/icon-kriging.svg){ .tool-icon }<br>**Kriging** (Spatial Analyst) | Interpolates a raster from points, weighting the neighbors by a semivariogram: a curve fitted to how much the values differ as the distance between them grows. [Tool reference](https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/kriging.htm){ target="_blank" } |
| ![Zonal Statistics as Table icon: the cells inside a zone summarized into a table row labeled MEAN](images/icon-zonal-statistics-as-table.svg){ .tool-icon }<br>**Zonal Statistics as Table** (Spatial Analyst) | Like Zonal Statistics, but writes the statistics of each zone to a table instead of a raster — here, the mean of the squared errors inside the study rectangle. [Tool reference](https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/zonal-statistics-as-table.htm){ target="_blank" } |

Tools you already know: **Project Raster** (Labs 4, 5, 7 and 8), **Extract by Mask** (Labs 4 and 8),
**Create Random Points** and **Extract Values to Points** (Lab 8), **IDW** (Lab 8), **Polygon to
Raster**, **Raster Calculator** (Labs 2 and 4–8), **Calculate Field** (Lab 6), and model parameters.
Step 10 also uses **Extract Multi Values to Points** and **Summary Statistics**.

## Example Model

![The finished ModelBuilder model, exported as a vector diagram. YMountain_DEM.tif, marked P, feeds Project Raster (DEM_UTM) and Extract by Mask with Study_Area, marked P, giving True_DEM. Number of Points and Random Seed, both marked P, feed Create Random Points (Random_Points), then Extract Values to Points with True_DEM (Sample_Points). Three branches follow: Create Thiessen Polygons and Polygon to Raster (Thiessen_Surface); IDW with IDW Power, marked P (IDW_Surface); Kriging with Semivariogram, marked P (Kriging_Surface). Each surface goes to a Raster Calculator that subtracts it from True_DEM (Error_Thiessen, Error_IDW, Error_Kriging, all marked P), a second Raster Calculator that squares it, Zonal Statistics as Table over Study_Area, and Calculate Field, ending in RMSE Thiessen, RMSE IDW and RMSE Kriging, all marked P.](images/lab09-full-model.svg)

**Figure C.** The finished model, exported from ModelBuilder — **click it to open it full size**. The
DEM is projected and cut to the rectangle (`True_DEM`); random points sample it; three branches
rebuild it (Thiessen polygons then Polygon to Raster; IDW; Kriging); each rebuild is subtracted from
`True_DEM`, squared, averaged over the rectangle and square-rooted. The twelve elements marked `P`
become the tool dialog of Step 10.

## Complete the Lab

For an advanced GIS student, the information up to this point is all you need to complete the
assignment. Feel free to try the analysis using only the information above. If you complete the lab
without the step-by-step instructions below, say so in your report.

## Step-by-Step Solution

> [!NOTE]
> **Important Note #1.** Steps 0–9 build the model and run it at the defaults with the course's
> random seed, so your numbers can be checked against this page. Step 10 re-runs the same model
> with your own seed and other settings. Build it once, and build it to be changed.

> [!NOTE]
> **Important Note #2.** Every check value on this page was measured on the files you download, with
> the steps below, in ArcGIS Pro 3.7.1. With the random seed of Step 0, your numbers should match to
> the last digit shown. The screenshots were captured in the same version, building this model, and
> their paths start with `C:\` because they were made on an instructor machine.

### Step 0 — Set Up the Project

1. Create a new project in `D:\Smith\Lab09\` with the **Map** template; if you already made the
   folder, uncheck **Create a folder for this local project**.
2. Add `YMountain_DEM.tif` (click **OK** to build pyramids and statistics) and
   `Lab09.gdb\Study_Area`.
3. Confirm Spatial Analyst is licensed and that your license level is **Advanced** (**Project** ▸
   **Licensing**); Create Thiessen Polygons needs it. <!-- VERIFY: the lab machines' license level. -->
4. On the **Analysis** tab click **ModelBuilder**. On the **ModelBuilder** tab click
   **Properties**, set **Name** to `InterpolationExplorer` and **Label** to `Interpolation Explorer`,
   and save.
5. On the **ModelBuilder** tab click **Environments** and set:
    - **Current Workspace** and **Scratch Workspace**: your project geodatabase
    - **Random Number Generator**: **Seed** `1`; leave **Generator** at ACM collected algorithm 599
    - **Cell Size**: `30`
    - **Extent**: click the second button above the boxes, which lists the map's layers, and choose
      `YMountain_DEM.tif`. The box fills with the DEM's corners in latitude and longitude.
    - after Step 2 has run once: **Snap Raster** `DEM_UTM` — type its path,
      `D:\Smith\Lab09\Lab09.gdb\DEM_UTM` (with your own folder)

    Type an environment's name in the dialog's search box to find it.

![The model's Environments dialog, two searches combined: Extent from YMountain_DEM.tif, Top 40.27, Left -111.68, Right -111.57, Bottom 40.20 in GCS North American 1983; Current Workspace Lab09.gdb; Output Coordinate System empty; Cell Size 30; Mask empty; Cell Alignment Default; Snap Raster DEM_UTM; and Random Number Generator with Seed 1 and Generator ACM collected algorithm 599.](images/lab09-environments.png)

**Figure 0.** ModelBuilder ▸ Environments, from two searches (`extent` and `random`). Leave Output
Coordinate System empty: Step 2 projects the DEM itself.

> [!WARNING]
> **Snap to `DEM_UTM`, not to `True_DEM`.** Snapping to the surface you are about to cut looks
> natural, and it works inside ModelBuilder, but the first run from the tool dialog in Step 10 stops
> with *ERROR 010654: The output True_DEM is the same as the snap raster*. `True_DEM` is cut from
> `DEM_UTM`, so the cells line up either way.

> [!NOTE]
> **Why fix the seed?** Create Random Points draws from a random number generator. With the same seed
> it draws the same points every time, so your RMSEs can be checked against this page. In Step 10 you
> switch to a seed of your own.

### Step 1 — Look at the Service

The same elevations are served live on the web. Before you use the prepared file, look at what the
service gives you.

1. On the **Map** tab, in the **Layer** group, click **Add Data From Path** (the yellow button
   beside the basemap gallery), paste
   `https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer`, and click
   **Add**. It is slow; give it a minute.
2. Right-click the new `3DEPElevation` layer ▸ **Properties** ▸ **Source**. Expand **Raster
   Information** and **Spatial Reference** and record the columns and rows, the cell size, the pixel
   type and the coordinate system. Look at the layer's legend in the Contents pane, too.
3. On the **Map** tab click **Go To XY**, enter longitude **−111.58865** and latitude **40.21415**,
   and drop a marker there. This is the highest cell of the extract. Click the marker with
   **Explore**: the pop-up reports the service. Turn the service layer off and click again to read the
   extract.
4. Remove the service layer and the marker's graphics layer. The rest of the lab runs on the extract.

![The Add Data From Path dialog: Path set to https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer and Service type An ArcGIS Server Web Service.](images/lab09-add-from-path.png)

**Figure 1a.** Add Data From Path, with the 3DEP elevation service.

![The service layer's Properties, Source page: Data Type Raster, Location the 3DEP ImageServer URL, Vertical Units Meter; Raster Information: Columns 40075015, Rows 20498394, 1 band, Cell Size X 1 and Y 1, Uncompressed Size 747.13 TB, Format Image Service, Source Type Elevation, Pixel Type unsigned char, Pixel Depth 8 Bit.](images/lab09-service-raster-info.png)

**Figure 1b.** What came back: 1 m cells covering the whole country — 747 TB if you could download it
— in **8-bit unsigned** pixels.

![The Spatial Reference section of the same page: Projected Coordinate System WGS 1984 Web Mercator (auxiliary sphere), Projection Mercator Auxiliary Sphere, WKID 3857.](images/lab09-service-spatial-reference.png)

**Figure 1c.** The service's coordinate system: Web Mercator, not the latitude and longitude of the
extract, and not UTM.

![The Explore pop-up for the service at the marker: 3DEPElevation (2), item n41w112; Service Pixel Value 154, Stretch.Pixel Value 154, Name n41w112, MinPS 0, MaxPS 27, LowPS 10.30736, HighPS 16.](images/lab09-service-popup.png)

**Figure 1d.** The service at the highest cell of the extract. The value is **154**, not an
elevation; the source item is tile `n41w112`, the same tile the extract was cut from.

> [!TIP]
> **Check the result:** the service arrives drawn as a **hillshade**, with a legend from 0 to 255.
> That is the service's default *raster function*: the server turns elevations into a picture before
> sending them, and that is why the pixel type is 8-bit and the pop-up reads **154** at the marker.
> The extract reads about **2,893 to 2,897 m** there, depending on exactly which cell your click lands
> in (the highest cell is 2,896.9 m).

> [!NOTE]
> **Why not just use the service?** A service is convenient and always current, but what comes back
> depends on the request: here a shaded picture in Web Mercator rather than elevations in meters, and
> it can change whenever the USGS updates it. An analysis that others must check needs a fixed copy
> with a known date, which is why the course hosts one. Say in your report which of the two you would
> cite in an engineering report, and why.

### Step 2 — Project the DEM

Add **Project Raster** with `YMountain_DEM.tif` as the input:

- **Output Coordinate System**: NAD 1983 UTM Zone 12N (the globe button, then search for `26912`)
- **Resampling Technique**: Bilinear interpolation
- **Output Cell Size**: 30 (X and Y)
- **Output Raster Dataset**: `DEM_UTM`

![The Project Raster dialog from ModelBuilder: Input Raster YMountain_DEM.tif, Output Raster Dataset DEM_UTM, Output Coordinate System NAD_1983_UTM_Zone_12N, Geographic Transformation empty, Resampling Technique Bilinear interpolation, Output Cell Size X 30 and Y 30, Registration Point empty.](images/lab09-project-raster.png)

**Figure 2.** Project Raster. It switches itself to Bilinear when you pick this DEM and proposes
cells of about 9.06 m; type 30 in both X and Y.

> [!TIP]
> **Check the result:** `DEM_UTM` is **314 columns × 262 rows** of 30 m cells, values **1,368.1 to
> 2,896.5** m. The thin wedges along the edges are NoData: a latitude and longitude rectangle is
> slightly tilted in UTM. That is why the study rectangle sits well inside it.

### Step 3 — Cut the True Surface

Add **Extract by Mask**: **Input raster** `DEM_UTM`, **Input raster or feature mask data**
`Study_Area`, output `True_DEM`. Type the output name last: this tool replaces a typed name when its
inputs change.

Run the model this far, then set the **Snap Raster** environment of Step 0.

![The Extract by Mask dialog from ModelBuilder: Input raster DEM_UTM, mask Study_Area, Output raster True_DEM, Extraction Area Inside, and the Analysis Extent filled in from the mask: Top 4457497.05, Left 442514.873, Right 451184.873, Bottom 4450507.05, NAD 1983 UTM Zone 12N.](images/lab09-extract-by-mask.png)

**Figure 3.** Extract by Mask. The Analysis Extent fills itself in from the rectangle; leave it.

> [!TIP]
> **Check the result:** `True_DEM` has **67,337** cells with values, from **1,368.5 to
> 2,896.5** m, mean **1,819.8** m. This is the truth every rebuilt surface is measured against.

> [!WARNING]
> **Set the Snap Raster and the Extent.** Without the Snap Raster, the interpolators place their
> cells wherever their points' extent puts them, and the subtraction in Step 8 compares cells offset
> by part of a cell. Without the Extent, IDW and Kriging fill only the box around the sample points;
> with few points that box misses strips along the edges, and those cells drop out of the RMSE. In
> neither case does anything report an error.

### Step 4 — Sample the Surface

1. Add **Create Random Points**: **Output Location** your project geodatabase, **Output Point
   Feature Class** `Random_Points`, **Constraining Feature Class** `Study_Area` — choose it under
   **Model Variables**, where it reads `Study_Area:1` — and **Number of Points [value or field]**
   `2500` (leave its type at Long).
2. Right-click the tool in the model ▸ **Create Variable** ▸ **From Parameter** ▸ **Number of
   Points [value or field]**. Right-click the new oval ▸ **Rename** it `Number of Points`, and
   right-click it ▸ **Parameter**.
3. Right-click the tool again ▸ **Create Variable** ▸ **From Environment** ▸ **Random Number
   Generator**. Rename the oval `Random Seed` and make it a parameter too. It carries the seed of
   Step 0, and in Step 10 it is how you change it.
4. Add **Extract Values to Points** with `Random_Points` and `True_DEM`, output `Sample_Points`.

> [!WARNING]
> **New ovals land on top of the tool's other inputs.** After each Create Variable, drag the new oval
> clear (click it, then drag) before you right-click it, or the menu you open belongs to the oval
> underneath.

![The Create Random Points dialog from ModelBuilder, with a banner suggesting Create Spatial Sampling Locations: Output Location Lab09.gdb, Output Point Feature Class Random_Points, Constraining Feature Class Study_Area:1, Number of Points Long 2500, Minimum Allowed Distance 0 Meters, Create Multipoint Output unchecked.](images/lab09-create-random-points.png)

**Figure 4a.** Create Random Points. Once a constraining feature class is set, the Constraining
Extent box disappears.

![The Extract Values to Points dialog from ModelBuilder: Input point features Random_Points, Input raster True_DEM, Output point features Sample_Points, both checkboxes unchecked.](images/lab09-extract-values.png)

**Figure 4b.** Extract Values to Points.

> [!TIP]
> **Check the result:** 2,500 points, `RASTERVALU` from **1,368.7 to 2,886.7** m. With seed 1, the
> first point (`OBJECTID` 1) is at about **444,603.3 E, 4,453,723.7 N**. If any `RASTERVALU` is
> empty or −9999, a point fell outside `True_DEM`: check the constraining feature class.

> [!NOTE]
> The samples never include the true highest cell (2,896.5 m): the tallest sample is 2,886.7 m. Keep
> that number in mind for the next three steps.

### Step 5 — Build the Thiessen Surface

1. Add **Create Thiessen Polygons**: **Input Features** `Sample_Points`, output
   `Thiessen_Polygons`, **Output Fields** **All fields**.
2. Add **Polygon to Raster**: **Input Features** `Thiessen_Polygons`, **Value field**
   `RASTERVALU`, **Cell assignment type** Cell center, **Cellsize** 30 (it fills in from the
   environment), output `Thiessen_Surface`.

![The Create Thiessen Polygons dialog from ModelBuilder: Input Features Sample_Points, Output Feature Class Thiessen_Polygons, Output Fields All fields.](images/lab09-thiessen-polygons.png)

**Figure 5a.** Create Thiessen Polygons, with **All fields**.

![The Polygon to Raster dialog from ModelBuilder: Input Features Thiessen_Polygons, Value field RASTERVALU, Output Raster Dataset Thiessen_Surface, Cell assignment type Cell center, Priority field NONE, Cellsize 30, Build raster attribute table checked.](images/lab09-polygon-to-raster.png)

**Figure 5b.** Polygon to Raster, with the value field changed to `RASTERVALU`.

> [!WARNING]
> **Two defaults here give a surface with no elevations in it.** Create Thiessen Polygons opens at
> **Output Fields: Only feature ID**, which leaves the polygons with no `RASTERVALU` at all. Polygon
> to Raster then fills **Value field** with `OBJECTID` by itself — a surface of polygon numbers, and
> no error. Choose **All fields** in the first, and `RASTERVALU` in the second.

> [!TIP]
> **Check the result:** **2,500** polygons, one per point. `Thiessen_Surface` runs from **1,368.7 to
> 2,886.7** m — exactly the range of the samples, because every cell simply takes the value of its
> nearest point.

### Step 6 — Build the IDW Surface

Add **IDW** (the Spatial Analyst tool; the search also offers a 3D Analyst and a Geostatistical
Analyst one): **Input point features** `Sample_Points`, **Z value field** `RASTERVALU`, **Output
cell size** `30`, **Power** 2, **Search radius** Variable with 12 points, output `IDW_Surface`. Then
right-click the tool ▸ **Create Variable** ▸ **From Parameter** ▸ **Power**, rename the oval
`IDW Power`, and make it a parameter.

![The IDW dialog from ModelBuilder: Input point features Sample_Points, Z value field RASTERVALU, Output raster IDW_Surface, Output cell size 30, Power 2, Search radius Variable with Number of points 12 and Maximum distance empty, Input barrier polyline features empty.](images/lab09-idw.png)

**Figure 6.** IDW.

> [!WARNING]
> **Z value field fills in `CID`**, a field Create Random Points adds to every point, all with the
> same value. Change it to `RASTERVALU`. Kriging in Step 7 does the same.

> [!TIP]
> **Check the result:** `IDW_Surface` runs from **1,368.7 to 2,885.5** m. IDW is a weighted average,
> so it can never go above its highest point or below its lowest: compare with Step 4.

### Step 7 — Build the Kriging Surface

Add **Kriging** (Spatial Analyst): **Input point features** `Sample_Points`, **Z value field**
`RASTERVALU`, output `Kriging_Surface`, **Kriging method** Ordinary, **Semi-variogram model**
Spherical, **Output cell size** `30`, **Search radius** Variable with 12 points. Leave **Lag size**
at the 30 it fills in, the range, sill and nugget empty, and the optional variance raster empty.
Then right-click the tool in the model ▸ **Create Variable** ▸ **From Parameter** ▸
**Semivariogram properties**, rename the oval `Semivariogram`, and make it a parameter. In the tool
dialog it shows the same controls as here: in Step 10 you pick another model from its
**Semi-variogram model** list.

![The Kriging dialog from ModelBuilder: Input point features Sample_Points, Z value field RASTERVALU, Output surface raster Kriging_Surface, Kriging method Ordinary, Semi-variogram model Spherical, Lag size 30, Major range, Partial sill and Nugget empty, Output cell size 30, Search radius Variable with Number of points 12, Output variance of prediction raster empty.](images/lab09-kriging.png)

**Figure 7.** Kriging. The range, sill and nugget stay empty: Kriging fits them to your points.

> [!TIP]
> **Check the result:** `Kriging_Surface` runs from **1,368.5 to 2,884.3** m. Unlike IDW, Kriging
> *can* go beyond its samples, and it does, just: its lowest cells, outside the rectangle where it
> extrapolates, are 0.2 m below the lowest sample. At the top it pulls the peak down a little further
> than IDW.

### Step 8 — Map the Errors

Add **Raster Calculator** (Spatial Analyst) three times, one per surface, each the truth minus the
rebuild:

| Expression | Output |
| --- | --- |
| `"%True_DEM%" - "%Thiessen_Surface%"` | `Error_Thiessen` |
| `"%True_DEM%" - "%IDW_Surface%"` | `Error_IDW` |
| `"%True_DEM%" - "%Kriging_Surface%"` | `Error_Kriging` |

The quickest way to the second and third: select the first Raster Calculator, **Ctrl+C**, click
empty canvas, **Ctrl+V**, drag the copy clear, and edit its expression and output. A positive error
means the surface came out too **low** there; a negative error, too **high**. Give all three the same
diverging color scheme with the same class breaks (the example maps use −100, −50, −20, −5, 5, 20,
50, 100 m), so that the same color means the same error on every map.

![The Raster Calculator dialog from ModelBuilder, widened: the Rasters list shows DEM_UTM, YMountain_DEM.tif, True_DEM, Number of Points and Thiessen_Surface; the expression reads "%True_DEM%" - "%Thiessen_Surface%"; Output raster Error_Thiessen.](images/lab09-rc-error.png)

**Figure 8.** The Thiessen error. Type the output name last and check it before **OK**: Raster
Calculator puts back the old name when the expression changes.

> [!TIP]
> **Check the result:**
>
> | Error raster | Minimum | Maximum | Mean |
> | --- | --- | --- | --- |
> | `Error_Thiessen` | −234.1 | 214.3 | −0.39 |
> | `Error_IDW` | −136.8 | 169.9 | −0.84 |
> | `Error_Kriging` | −104.0 | 164.4 | −0.31 |
>
> Every mean is under a meter: the errors cancel. That is why the next step squares them.

### Step 9 — Compute the RMSE

The root-mean-square error is the typical size of an error, whatever its sign: **square** every
cell's error, take the **mean** of the squares over the rectangle, and take the **square root**.
Build the chain once for Thiessen, then copy it twice:

1. **Raster Calculator**: `Square("%Error_Thiessen%")`, output `SqError_Thiessen`.
2. **Zonal Statistics as Table**: **Input raster or feature zone data** `Study_Area:1`, **Zone
   field** `OBJECTID`, **Input value raster** `SqError_Thiessen`, **Statistics type** Mean (it opens
   at All), output table `RMSE_Thiessen`.
3. **Calculate Field**: **Input Table** `RMSE_Thiessen`, **Field Name** `RMSE`, **Field Type**
   Double (it opens at Text), **Expression Type** Python, and in the box under `RMSE =`,
   `math.sqrt(!MEAN!)`. Rename its output oval `RMSE Thiessen`.

Then select the Zonal Statistics as Table and Calculate Field tools and their outputs, copy and
paste them twice, and in each copy change only the value raster and the output table (`SqError_IDW`
and `RMSE_IDW`; `SqError_Kriging` and `RMSE_Kriging`): the copied Calculate Field follows its table
by itself. Rename the outputs `RMSE IDW` and `RMSE Kriging`.

Finally make the parameters: the DEM and `Study_Area` (inputs), and as outputs the three error
rasters and the three `RMSE` ovals. With `Number of Points`, `Random Seed`, `IDW Power` and
`Semivariogram` from Steps 4, 6 and 7, that is twelve. Save, close the model, and open it from the
**Catalog** pane (**Toolboxes** ▸ `Lab09.atbx` ▸ **Interpolation Explorer**) to see its dialog.

![The Raster Calculator dialog from ModelBuilder: the expression reads Square("%Error_Thiessen%"); Output raster SqError_Thiessen.](images/lab09-rc-square.png)

**Figure 9a.** Squaring the Thiessen error.

![The Zonal Statistics as Table dialog from ModelBuilder: Input Raster or Feature Zone Data Study_Area:1, Zone Field OBJECTID, Input Value Raster SqError_Thiessen, Output Table RMSE_Thiessen, Ignore NoData in Calculations checked, Statistics Type Mean, Calculate Circular Statistics and Process as Multidimensional unchecked, Output Join Layer empty.](images/lab09-zonal-table.png)

**Figure 9b.** Zonal Statistics as Table, with **Mean**.

![The Calculate Field dialog from ModelBuilder: Input Table RMSE_Thiessen, Field Name RMSE with a warning that it is a new field, Field Type Double (64-bit floating point), Expression Type Python, Fields list OBJECTID, OBJECTID_1, COUNT, AREA, MEAN, and the expression RMSE = math.sqrt(!MEAN!).](images/lab09-calculate-field.png)

**Figure 9c.** Calculate Field. The warning beside Field Name only says the field will be added.

![The model as a tool in a floating Geoprocessing pane, titled Interpolation Explorer and set up for a Step 10 run: Number of Points Long 250; Random Seed 1 with ACM collected algorithm 599; IDW Power 2; Semivariogram Ordinary, Spherical, with Lag size empty and Major range 10950, Partial sill 513125.896396 and Nugget 0 carried over from the last run; outputs RMSE_Thiessen_n250, RMSE_Kriging_n250, RMSE_IDW_n250, Error_Thiessen_n250, Error_IDW_n250 and Error_Kriging_n250, each with a warning icon; Study_Area; YMountain_DEM.tif.](images/lab09-tool-dialog.png)

**Figure 9d.** The model as a tool, set up for the first run of Step 10. The warning icons only say
the outputs exist from an earlier run.

> [!TIP]
> **Check the result:** each table has one row (the zone field appears as `OBJECTID_1`) with
> **COUNT 67,337** and **AREA 60,603,300** (m²).
>
> | Table | MEAN (m²) | RMSE (m) |
> | --- | --- | --- |
> | `RMSE_Thiessen` | 800.3 | **28.29** |
> | `RMSE_IDW` | 428.9 | **20.71** |
> | `RMSE_Kriging` | 209.0 | **14.46** |
>
> If COUNT is smaller, an interpolator's output does not cover the whole rectangle — check the
> **Extent** environment of Step 0. At 2,500 points it can look right without it; at 250 it does not.

> [!WARNING]
> **A run from the tool dialog deletes everything that is not a parameter** (Labs 5, 7 and 8 saw
> it): `DEM_UTM`, `True_DEM`, `Sample_Points` and the three surfaces. Do Steps 2–9 from inside
> ModelBuilder first and record the check values before any dialog run. In our build a full run took
> about 1½ minutes in ModelBuilder and 2 minutes from the dialog.

### Step 10 — Test the Choices

The ranking at the defaults is *a* result, not *the* result. It came from one set of random points
and three sets of default parameters. Find out how much of it survives a change.

**First, your own points.** In ModelBuilder, double-click the `Random Seed` oval and set **Seed** to
the **last four digits of your BYU ID** as a number (`0042` is `42`; if that gives 0, use `9999`).
Save, and run the model **inside ModelBuilder** at the defaults. This is your **baseline**: Map 1 is
made from it, and it is the first row of your table. Write your seed in your report: the grader
re-runs your model with it.

**Then the checkpoints.** In real work you would not have a true DEM; you would hold back some
measured points and test against them. Do that once, on your baseline surfaces:

1. Run **Create Random Points** from the Geoprocessing pane (not in the model): constraining feature
   class `Study_Area`, **200** points, output `Checkpoints` in your project geodatabase, and on its
   **Environments** tab **Random Number Generator** seed `99`. Everyone uses the same 200
   checkpoints.
2. **Extract Multi Values to Points** on `Checkpoints` with `True_DEM` (output field name `TRUE_Z`),
   `Thiessen_Surface` (`TH_Z`), `IDW_Surface` (`IDW_Z`) and `Kriging_Surface` (`KR_Z`).
3. **Calculate Field** three times, new Double fields: `SQ_TH` = `(!TRUE_Z! - !TH_Z!) ** 2`,
   `SQ_IDW` = `(!TRUE_Z! - !IDW_Z!) ** 2`, `SQ_KR` = `(!TRUE_Z! - !KR_Z!) ** 2`.
4. **Summary Statistics** on `Checkpoints`: the **Mean** of `SQ_TH`, `SQ_IDW` and `SQ_KR`. The
   square root of each mean is that method's **checkpoint RMSE**.

> [!WARNING]
> **Finish Map 1 and the checkpoints before the first dialog run.** Map 1 draws your baseline's sample
> points, surfaces and `True_DEM`, and the checkpoints read them; none of those are parameters, so the
> first run from the tool dialog deletes them. Export Map 1 to PDF and record the checkpoint RMSEs
> first. The model rebuilds `DEM_UTM` at the start of every run, so the Snap Raster still works.

**Then four more runs**, from the model's tool dialog, with **Random Seed** still at your own seed,
giving every output a name that says what changed (`RMSE_Kriging_n250`, `Error_IDW_n250`):

1. **250 points** (everything else at the defaults).
2. **10,000 points**.
3. **IDW power 1 and Kriging exponential** (one run changes both: they are in different branches).
4. **IDW power 3 and Kriging Gaussian**.

After a run the Semivariogram boxes show the range and sill Kriging fitted last time. Each run fits
them again; to be safe when you change the model, empty **Major range**, **Partial sill** and
**Nugget** first. <!-- VERIFY: a 250-point dialog run with the fitted values left in gave Kriging RMSE 50.38, the arcpy refit value; not yet tested with the model changed to Gaussian. -->

For **the baseline and every run, in one table**, record your seed, what changed, and the RMSE of all
three methods; add the three checkpoint RMSEs to the baseline row.

Then answer, in your report:

1. **Which method wins, and does the ranking survive?** Rank the methods at each number of points,
   with your numbers. Does the winner change? How much does going from 250 to 10,000 points buy each
   method?
2. **Which parameter mattered, and which barely did?** Compare what the IDW power and the
   semivariogram model did with what the number of points did. Look at a Gaussian surface's highest
   cell before you explain it.
3. **Could you have known without the truth?** Compare each method's checkpoint RMSE with its RMSE
   over all 67,337 cells. Would 200 checkpoints have told a client the right ranking, and how far off
   would the number you quoted have been?

> [!TIP]
> Before you run the 10,000-point case, predict its RMSEs from your 250 and 2,500 results. Then look
> at where on the error maps the remaining error lives, and at the slope of the ground there.

## Deliverables

Make **two** professional map layouts (letter size, landscape is easiest):

1. **Your baseline comparison sheet** — from your personal-seed baseline: the true DEM with your
   sample points and the three surfaces in one row, **on one elevation color scale**; the three error
   rasters beneath their surfaces **on one diverging color scale** with the same breaks; each panel
   labeled with its method, its parameters and its RMSE; legends for both scales; a title, neat
   line, north arrow and scale bar; and a text box with your name, the date, the map projection, the
   DEM's source and date, and your seed.
2. **One scenario from Step 10** — whichever run most changes the picture: its three error rasters
   on Map 1's error scale with a legend, each labeled with its method, parameters and RMSE (the true
   DEM and the surfaces are optional); a title, neat line, north arrow and scale bar; and a text box
   with your name, the date, the map projection, the DEM's source and date, and your seed. Say in
   the title and the text box what changed from Map 1 and by how much.

Write a brief report (2–3 pages of text, plus your figures and maps) covering:

- a title block — assignment title, your name, the date and the course — and the name of your
  peer reviewer
- the requirements of the project and your approach to solving it
- **a description of your model** a reader could repeat from: each tool and its settings, and every
  input, intermediate and output dataset with its type
- **one** full-page figure of your model, exported from ModelBuilder (**Export ▸ Export To
  Graphic**), and **one** screen capture of its tool dialog with the number of points, the IDW power
  and the semivariogram exposed; and **upload your project's toolbox** (`Lab09.atbx`, in your project
  folder) with the report — the grader opens it and runs it at your seed
- **the three metadata values** for the DEM — its publication date and source dates, its vertical
  datum and units, and its cell size — and **what the service returned** in Step 1, what each
  means for your result, and which of the two you would cite in an engineering report
- your **check values from Steps 4 to 9** at seed 1: the first point, each surface's range, and the
  three RMSEs
- **where the methods break**: on the error map of your best method (lowest RMSE), the cell with the
  largest error in either direction — its coordinates and size — and why the ground there defeats
  the interpolators, with a cropped figure of the spot. Its value is the raster's minimum or maximum
  (**Properties** ▸ **Source** ▸ **Statistics**), whichever is farther from zero. To find it, give
  the layer a two-class symbology with the break just short of that value, so that one cell stands
  out, and click it with **Explore** to read its coordinates
- your **sensitivity table** from Step 10, with your seed, and your answers to its three questions
- **a copy of the rubric below with your self-assessment filled in** — a score in every row,
  honestly arrived at. The grader will compare it with theirs.

> [!IMPORTANT]
> **Peer review before you submit.** Have another student in the class read your report against
> the rubric and give you feedback, then act on that feedback before the deadline. Name your
> reviewer in the report and say in a sentence what you changed because of them.

**Credit line for your maps:** Elevation: USGS 3D Elevation Program, 1/3 arc-second DEM, tile
n41w112 (May 2026). Study area: drawn for CE 414.

## References

Bolstad, P. *GIS Fundamentals: A First Text on Geographic Information Systems*. Eider Press.
Chapter 12, the Week 8 reading on interpolation (any of the 5th to 7th editions).

U.S. Geological Survey, 3D Elevation Program. 1/3 arc-second DEM, tile n41w112, published May 20,
2026.

U.S. Geological Survey, 3D Elevation Program. 3DEP Elevation image service.
[elevation.nationalmap.gov](https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer){ target="_blank" }.

## Example Maps

These are examples, not templates. Your maps carry your name and your own seed's results, so your
numbers will differ a little from these.

![Example comparison sheet titled "Rebuilding Y Mountain from 2,500 Points: Kriging Comes Closest". Top row: the true DEM with 2,500 black sample points, then the Thiessen, IDW and Kriging surfaces, all on one green-to-brown-to-white elevation scale over a hillshade; the Thiessen surface is visibly faceted. Second row: the three error maps on one red-to-blue scale, labeled Thiessen error RMSE 28.29 m, IDW error RMSE 20.71 m, Kriging error RMSE 14.46 m; the valley floor is pale everywhere, and the mountain front is a mottle of red and blue, finest-grained for Thiessen and palest for Kriging. Legends, north arrow, scale bar and a text box at the bottom.](images/lab09-example-map-baseline.png)

**Figure 10.** A baseline comparison sheet at seed 1. Two things to do better than this example:
mark and label the largest error on the best method's error map, and use the empty band below the
error maps for a sentence on what the reader should notice.

![Example scenario sheet titled "The Same Surfaces from 250 Points: Every Error Grows", with the same layout and color scales: far fewer sample points; blurred, blocky surfaces; and error maps dominated by dark red and dark blue across the mountain, labeled RMSE 80.73, 69.46 and 50.38 m. The text box says the run was chosen because whole ridges are missed, not just the cliff bands.](images/lab09-example-map-scenario.png)

**Figure 11.** The kind of second map Step 10 asks for. Yours needs only the error maps, and should
be the run that most changes what a reader would conclude, which may not be this one.

## Rubric for Interpolation Explorer

Fifty points in five parts of ten. The bullets say what each part is worth, so you know exactly
what to submit.

| Item | Points |
| --- | --- |
| **Write-up** (2–3 pages)<br>• Assignment title, your name, date and course; your peer reviewer named, with a sentence on what you changed because of them (1)<br>• The requirements of the project and your approach to solving it, in your own words (1)<br>• The three metadata values for the DEM and what the service returned in Step 1, what each means for your result, and which you would cite (2)<br>• Your check values from Steps 4 to 9 at seed 1 (2)<br>• Where the methods break: the largest error on your best method's error map, its coordinates and size, with a cropped figure, and why the ground there defeats the interpolators (3)<br>• Organized writing, figures numbered and referred to, sources credited, rubric pasted with your self-assessment (1) | /10 |
| **ModelBuilder model** — correct and working<br>• The model runs end to end from its tool dialog and, at seed 1, matches the three RMSE check values (4)<br>• A full-page model figure exported from ModelBuilder, all tools and datasets readable (2)<br>• A screen capture of the tool dialog with the number of points, the IDW power and the semivariogram exposed as parameters (2)<br>• A description of the model a reader could repeat from (2) | /10 |
| **Map 1 — your baseline comparison sheet**<br>• Title, neat line, north arrow and scale bar (1)<br>• Text box with author, date, map projection, the DEM's source and date, and your seed (1)<br>• The true DEM with your sample points and the three surfaces on one elevation scale, with a legend (2)<br>• The three error maps on one diverging scale with the same breaks, with a legend (2)<br>• Every panel labeled with its method, parameters and RMSE (2)<br>• Layout, scale and legibility: a reader can compare the panels at a glance (2) | /10 |
| **Map 2 — one Step 10 scenario**<br>• Title, neat line, north arrow and scale bar (1)<br>• Text box with author, date, map projection, the DEM's source and date, and your seed (1)<br>• The scenario's three error maps on Map 1's error scale, with a legend (2)<br>• Every panel labeled with its method, parameters and RMSE (2)<br>• Title and text box say what changed from Map 1 and by how much (2)<br>• Layout, scale and legibility (2) | /10 |
| **Sensitivity** (Step 10)<br>• One table with your seed, the baseline and the four Step 10 runs, the RMSE of all three methods in every row, and the three checkpoint RMSEs on the baseline row (4)<br>• Which method wins and whether the ranking survives, with your numbers (2)<br>• Which parameter mattered and which barely did, with your numbers (2)<br>• What the checkpoints would and would not have told you (2) | /10 |
| **Total** | **/50** |

> [!NOTE]
> **Using AI on this lab.** Use AI freely to understand a tool, work out an error, or
> tighten your write-up, and add one line at the end of your report saying what you used it
> for. Do not take a field name, an expression, a coordinate system, or a number from it —
> those come from your own data, and the rubric asks you to defend every one. See the
> [AI Use Policy](../../policies/ai-policy.md) for the full policy.

<!-- Draft notes (2026-10-06).
SOURCE: "Lab 8 - Practicing with Interpolation.docx" (instructor's copy in Downloads, saved 2026-10-06), whose September 3 migration is the live docs/assignments/lab-09/README.md; rebuilt to tools/lab-conversion-guide.md per tools/labs-09-11-plan.md section 4 (accepted 2026-10-06) and tools/lab09/PARITY_PLAN.md.
ARCGIS PRO: 3.7.1, arcpy (tools/lab09/run_model.py, extra_checks.py, chain_check.py, extent_check.py) and a GUI build on 2026-10-07 at 175 % (C:\Ames\Lab09GUI\Lab09.aprx, model InterpolationExplorer, set up by tools/lab09/gui_project.py; captures in caps\). Every check value reproduced in the GUI: first point, sample range, surface ranges, error table, ZSaT COUNT/AREA/MEAN and RMSE 28.29 / 20.71 / 14.46; a tool-dialog run at 250 points gave 80.73 / 69.46 / 50.38 (the oracle values) in 1 min 54 s; a full ModelBuilder run 1 min 34 s.
GUI FACTS (2026-10-07): Snap Raster True_DEM breaks every tool-dialog run (ERROR 010654, the output True_DEM is the same as the snap raster) - environments are now Snap Raster DEM_UTM and Extent = YMountain_DEM.tif from the layer list (fills in degrees; Study_Area from the layer list also fills in degrees; browsing to True_DEM gives UTM but True_DEM is a model output); with these the surfaces cover all of DEM_UTM, so Kriging's minimum is 1,368.5 (outside the rectangle) while the RMSEs are unchanged. Create Variable > From Environment > Random Number Generator exposes the seed as a parameter (Random Seed). Semivariogram properties can be a parameter; after a run its dialog shows the fitted range/sill (10950 / 513125.9) but a 250-point dialog run still refit (50.38). Defaults that silently give wrong surfaces: Thiessen Output Fields Only feature ID; Polygon to Raster Value field OBJECTID; IDW and Kriging Z value field CID; Zonal Statistics as Table Statistics All; Calculate Field Field Type Text. Kriging writes one extra cell on each side of the extent. Project Raster proposes 9.06 m. The service arrives through its Hillshade raster function: 40,075,015 x 20,498,394 cells of 1 m, 747.13 TB, unsigned char 8 bit, WGS 1984 Web Mercator (auxiliary sphere) WKID 3857; Explore at the highest cell reads Service Pixel Value 154, item n41w112, LowPS 10.30736. Dialog runs delete DEM_UTM, True_DEM, Sample_Points and the three surfaces. Copying a Zonal Statistics + Calculate Field chain keeps the Calculate Field wired to its own table. The copied blank project pre-filled Output Coordinate System in the model environments (cleared) and carried Lab01.atbx and Lab01.gdb.
DATA: docs/data/lab09-y-mountain.zip, 1,885,312 bytes: YMountain_DEM.tif (window -111.68 -111.57 40.20 40.27 of USGS_13_n41w112, published 2026-05-20, source dates 1946-2023; 1,188 x 756 float32, 1,368.03-2,896.92 m, no NoData) and Lab09.gdb\Study_Area (442,514.873-451,184.873 E, 4,450,507.050-4,457,497.050 N, on DEM_UTM's 30 m grid). Built by tools/lab09/fetch_dem.py, run_model.py, make_extract.py.
VERIFIED NUMBERS (seed 1 ACM599): DEM_UTM 314 x 262, 1,368.1-2,896.5; True_DEM 67,337 cells, 1,368.5-2,896.5, mean 1,819.8; first point 444,603.3 E 4,453,723.7 N; samples 1,368.7-2,886.7; Thiessen 2,500 polygons, surface 1,368.7-2,886.7, error -234.1/214.3 mean -0.39, MEAN 800.3, RMSE 28.29; IDW 1,368.7-2,885.5, error -136.8/169.9 mean -0.84, MEAN 428.9, RMSE 20.71; Kriging 1,368.7-2,884.3, error -104.0/164.4 mean -0.31, MEAN 209.0, RMSE 14.46; ZSaT COUNT 67,337 AREA 60,603,300 (at seed 1 / 2,500 points also without an Extent environment, but NOT in general: the pilot found IDW and Kriging at 250 points cover only 66,297 cells without Extent = True_DEM, RMSE 69.47 / 50.24 instead of 69.46 / 50.38; Extent now set in Step 0); Calculate Field math.sqrt(!MEAN!) reproduces the RMSEs; Create Thiessen Polygons ONLY_FID leaves only Input_FID. Service: REST identify 2,896.7 at the highest cell (40.21415 N, 111.58865 W).
SENSITIVITY (do NOT publish): see tools/lab09/PARITY_PLAN.md. Points 250/1,000/2,500/10,000: Kriging 50.38/24.90/14.46/6.90; IDW power 1/2/3/5: 23.98/20.71/20.20/21.60; Kriging Gaussian 24.81, other models 14.46; checkpoints within 2-3 m of the full-grid RMSE, same ranking; seeds 2-5 never change the ranking.
GRADING ORACLE: run_model.py --seed NNNN reproduces a student's Step 10 table (all five rows plus the checkpoint RMSEs) in about two minutes.
PILOT (no-GUI, 2026-10-06, C:\Ames\Pilot09\PILOT_NOTES.md): every seed-1 number reproduced; checkpoint recipe works as written (seed 1: 30.38 / 23.16 / 17.12, deliberately not published). Fixed from its findings: Extent environment added (Step 0, Step 3 warning, Step 9 tip); Step 10 warning to finish Map 1 and the checkpoints before dialog runs; semivariogram parameter path spelled out; Map 2 deliverable matches its rubric row, true DEM optional; 'largest error' defined (best method, either direction) with a way to find it; True_DEM cell count without the wrong 289 x 233; citation question added to deliverables and rubric; Figure A names the three values; checkpoint output location; OBJECTID_1 zone field noted.
TODO(instructor): 1. Lab machines' license level (Thiessen). 2. A dialog run with Kriging Gaussian and the fitted range/sill left in (the page tells students to clear them). 3. Report template. 4. Week 9 deck alignment. 5. Learning Suite due date November 7. -->
