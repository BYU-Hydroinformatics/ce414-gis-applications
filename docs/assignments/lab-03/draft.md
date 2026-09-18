---
search:
  exclude: true
---

# DRAFT — Lab 3: Georectifying and Digitizing Historic Maps

**Civil Engineering 414 — Engineering Applications of GIS**

Fall 2026 · Dr. Dan Ames

> [!WARNING]
> **This is a draft for review.** It is not the assigned page. The assigned page is
> [Lab 3](README.md).
>
> **Changes to what the lab asks students to do**
>
> - A **ModelBuilder model** is now required. Lab 3 was the only lab in the course with no model,
>   which is most of the reason it was easier than Lab 1. The model measures what you digitized and
>   how far off your georeferencing is, and it takes the digitized features as a parameter so that
>   the sensitivity runs cost a tool dialog rather than an afternoon.
> - The **sensitivity step now varies the control points**, not only the transformation. Changing
>   the transformation is a menu selection that costs the student nothing; choosing how many control
>   points to collect and where to put them is the actual engineering decision.
> - **At least one digitized feature must be a polygon you can measure**, and its area is reported
>   under three different georeferences. The lab now produces a number, not just a picture.
> - The **check features are drawn and measured**, not eyeballed. One line per check feature, from
>   where the scan puts it to where the basemap puts it, and the model reports the mean and the worst.
> - A new **uncertainty envelope** — your digitized features buffered by your own mean error — goes
>   on Map 1. It shows the band your feature actually lies within.
> - Steps renumbered: the old Steps 6 and 7 are now 7 and 8, and Steps 6, 9 and 10 are new.
> - New optional extra credit, up to five points: georeference a second time from the sheet's own
>   printed graticule and report the difference between the two answers.
>
> **Corrections to things that were wrong**
>
> - Nothing further. The September 17 pass corrected the deliverables list, the topoView download
>   format, and Figure 5's caption; all of that is carried forward here.
>
> **Figure provenance**
>
> - Figures 6a and 6b are new captures from ArcGIS Pro 3.7.1 at 175% display scaling, 2026-09-18.
> - Figures 1, 3 and 5 are the 2026-09-03 captures against a USGS 1893 Escondido sheet.
> - Figures 2, 4 and 12 are 2026-09-09 captures of the ribbon and the Transformation menu.
> - **Figures 7 to 11 are still the 2026-09-03 captures from an older ArcGIS Pro** and are owed.
> - **Figure C, the model diagram, does not exist yet.** The model in Step 9 has been built and run
>   with `arcpy` — every tool, parameter and output below is from a real run — but it has not been
>   assembled in ModelBuilder and exported as SVG. Marked `TODO` in place.
>
> **Site behavior**
>
> - This draft is excluded from search and is not in the site menu. Reach it by URL.

## Background

Old maps and aerial photographs are an unreasonably good source of information for civil,
environmental and construction engineers. There are thousands of filing cabinets, in government
agencies and engineering consulting firms, filled with mapping data that exists only on paper. That
data can tell you:

- how cities and landscapes have changed over time
- how growth followed, or ignored, natural and manmade features
- what a river, coastline or wetland looked like before it was engineered
- what was on a site before the building that is on it now

Libraries and agencies have scanned a great deal of it, so more of this material is online now than
ever before. A scan, though, is just a picture. It has rows and columns of pixels and no idea where
on Earth it belongs. **Georeferencing** is the act of telling it: you match points you can identify
on the scan to the same points on a map that already knows where it is, and ArcGIS Pro solves for a
transformation that moves every other pixel accordingly.

That last part is the whole lab. You do not place the image; you place a handful of points and let a
mathematical transformation place the image. How many points you give it, where you put them, and
which transformation you choose decide how much of the sheet ends up where it belongs — and the
number ArcGIS Pro reports to tell you how well it fits is measured on the very points you fitted, so
it can be made to look perfect while the map is wrong everywhere else.

Then you measure something. A historic map is only useful to an engineer when it produces a
quantity: how big the lake was, how long the rail spur ran, how much of the floodplain was built on.
The moment you report such a number you have to defend it, and the honest defense has two parts —
what the old surveyors got wrong, and what you got wrong. In Step 10 you will re-solve the same sheet
several ways, watch your own measurement move, and use what moves to decide which result you would
put your name on and what accuracy you would claim for it.

> [!IMPORTANT]
> **Your job — see the deliverables below.** Georeference one scanned historic map, digitize the
> features on it that are no longer on a modern map, build a model that measures them and measures
> your own error, test how much the answer depends on the control points you chose, and make two map
> layouts.

## Problem Statement

You need to find things that used to be somewhere and are not there now: a town that emptied out, a
rail spur that was pulled up, a street grid that was replaced, a channel that was straightened, a
lake that was larger. Nobody has this in a GIS. It exists on a sheet of paper that somebody scanned.

Your job is to turn the features on that sheet into a vector feature class, correctly located, so
they can be measured, overlaid and mapped alongside modern data. That takes three operations, in
this order:

1. **Georeference** the scan, so that its pixels sit in real-world coordinates.
2. **Digitize** the features from it, by drawing them on a new feature class while the georeferenced
   scan is underneath.
3. **Measure** what you drew, and measure how far wrong it is likely to be.

The order matters. Digitize first and every feature you draw is in the wrong place, permanently.
Measure without the third step and you have a number with no error bar, which in engineering is not
a number.

## Spatial Considerations

Every one of these is a decision you make, and every one of them changes your answer. Say in your
report what you chose and why.

- **Which sheet.** Age, scale and legibility trade against each other. An 1885 county atlas plate is
  full of vanished detail and drawn loosely; a 1950 USGS quadrangle is accurate and shows less
  change. Older is not automatically better.
- **Which basemap you georeference against.** Imagery shows what is there now; a topographic basemap
  shows named features and section lines that are easier to match on an old sheet. The basemap is
  your control, so its accuracy is a ceiling on yours.
- **How many control points, and where.** Three is the minimum for the default transformation and it
  is not enough. Points bunched in the middle of the sheet leave the corners free to wander. This is
  the parameter you will vary in Step 10, so collect generously now.
- **Which transformation.** A first-order (affine) transformation can shift, scale, rotate and skew
  the whole sheet but keeps straight lines straight. Higher orders bend it. A spline forces the
  control points to match exactly and rubber-sheets everything between them.
- **The coordinate system of your map.** Set it before you digitize. Your new feature class inherits
  it, and every length and area you measure later depends on it.
- **What counts as "gone".** A road that moved fifty meters, a town that shrank, a lake that is
  smaller: you decide what qualifies, and you defend it.
- **Which feature you choose to measure.** A polygon with sharp, identifiable corners can be
  re-traced the same way twice. A soft, vague boundary cannot, and the difference between your two
  tracings will swamp the effect you are trying to measure.

## Data

> [!IMPORTANT]
> **Set up your folder before you download anything.** On the lab machines, work on the
> **D: drive**, in a folder named after you with one folder per lab inside it — `D:\Smith\Lab03\`.
> Put the project, the scan and everything you make there. The C: drive is locked, network drives
> make ArcGIS Pro slow on large scans, and a USB 3.0 external drive is a legitimate alternative.
> **Never use a space in a folder or file name.** The full set of workspace conventions is on the
> [ArcGIS Tips and Reminders](../../arcgis-tips.md) page.

Unlike Labs 1 and 2, nothing here is prepared for you. **You find the data, and you defend it.**
That is the point: the judgment you exercised in Lab 1 choosing which Walmart stores counted, you
exercise here choosing a sheet and a basemap.

| Layer | Where it comes from | What you must record |
| --- | --- | --- |
| Historic map scan | You find and download it | Repository, title, date, scale, and the URL you got it from |
| Modern basemap | ArcGIS Pro basemap gallery | Which basemap, and why that one |
| Digitized features | You create it | Coordinate system, geometry type, and what you chose to include |
| Error lines | You create it | One line per check feature, and what feature each one represents |

### Judging the source

Apply the six metadata questions from the introductory course to your sheet before you use it —
**what, where, when, why, how, who** — and put the answers in your report:

- **What** does the sheet show, and at what scale? A scale printed on the sheet tells you how much
  detail to trust.
- **Where** does it cover, and does its coverage actually contain features you can match?
- **When** was it surveyed, which is often years before it was published? Both dates matter, and
  they are not the same date.
- **Why** was it made? A railroad promotional map, a fire insurance plan and a topographic survey
  are drawn to different standards and lie in different directions.
- **How** was it surveyed and drawn, and how was it scanned? A folded sheet flattened on a scanner
  bed has distortion no transformation will fully remove.
- **Who** made it, and are you allowed to use it? Anything published in the United States before
  1930 is in the public domain; a library's scan of it may still carry the library's own terms.

> [!WARNING]
> A pictorial or "bird's eye" view is not a map. Panoramic city views, common in the 1880s, are
> drawn in perspective from an imagined viewpoint, so scale changes continuously across the image
> and no transformation will make it fit. They are wonderful documents and they will waste your
> afternoon. Use a plan view, drawn looking straight down.

### Where to find a sheet

Your sheet should be **older than 1900** if you can find one that covers ground you can match. The
further back it goes, the more change there is to find.

| Source | What is there |
| --- | --- |
| [USGS topoView](https://ngmdb.usgs.gov/topoview/) | Every USGS topographic sheet ever published, back to 1884, free. The most reliable starting point. **Take the JPEG download, not the GeoTIFF** — see the warning below |
| [USGS Historical Topographic Map Collection](https://www.usgs.gov/programs/national-geospatial-program/historical-topographic-maps-preserving-past) | The program behind topoView, with an explanation of what was scanned and how |
| [David Rumsey Map Collection](https://www.davidrumsey.com/) | Over 100,000 scanned historic maps, strong on the nineteenth century and on city plans |
| [Library of Congress map collections](https://www.loc.gov/maps/collections/) | Fire insurance plans, city plans, railroad maps. May show a bot check before it loads |
| [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:Old_maps_by_country) | Public-domain scans, many of them Library of Congress copies, organized by country and state. Check the license box on the file page |

> [!WARNING]
> **Take the plain image, not the georeferenced one.** Where a repository offers a choice of
> formats, some of them already carry a spatial reference: USGS describes its GeoTIFF download as
> having "embedded georeferencing information so that the map can be used directly in a GIS", and a
> GeoPDF carries one too. Download one of those and ArcGIS Pro drops the sheet straight onto the
> basemap, correctly placed, with nothing for you to solve — somebody else did this lab for you.
> Take the **JPEG**, or any plain image format, so that the placement is yours.

> [!TIP]
> **Check the result.** Before you commit to a sheet, ask yourself two questions. Can you name at
> least **six** features on it that you could also point to on a modern basemap? And can you find
> **one closed shape** on it — a lake, a pond, a town boundary, a field, a quarry — that you could
> trace twice and get nearly the same outline both times? If the answer to either is no, find
> another sheet. The second question matters as much as the first: Step 7 asks you to measure that
> shape, and Step 10 asks you to measure it again.

### A worked example

The instructor's worked example for this lab is the **1852 Stansbury survey of the Great Salt Lake**
(Library of Congress item 2018588045, public domain, available through Wikimedia Commons). It is a
good sheet to look at before you choose your own, for three reasons: it is a real survey rather than
a compilation, it is visibly folded so its distortion is the kind no transformation removes, and it
carries a printed graticule, which makes the optional extra credit at the end of this lab possible.

You are not required to use it, and if you do, be aware that its latitudes are excellent and its
longitudes are not — which is exactly the sort of thing this lab is meant to teach you to find out
for yourself rather than be told.

### If your download is a PDF

Many scans, including USGS GeoPDFs, arrive as PDF. ArcGIS Pro will not add a PDF to a map directly.
Convert it:

- **In ArcGIS Pro**, search the Geoprocessing pane for **PDF To TIFF** (Conversion Tools ▸ To
  Raster). Set the input PDF, an output `.tif` in your lab folder, and a resolution — 250 to 300 dpi
  is enough for a topographic sheet and keeps the file manageable.
- **Or take a screen capture** of the PDF opened at full size and save it as a `.jpg` or `.png`.
  This is fine and it is what most people do; you lose whatever resolution the screen does not show.

Do not upload the file to a third-party conversion website. You have the tool on your desk.

## ModelBuilder Tools

Georeferencing itself is interactive by nature — you are looking at two images and deciding that
this corner is that corner, which is not something a model can do for you. Everything that happens
*after* the georeferencing is a model, and you build it in Step 9.

These are the tools you will use for the first time in this course.

<!-- TODO(instructor): this table needs the generated SVG icons that Labs 1 and 2 have
(tools/lab01/make_svgs.py, tools/lab02/make_svgs.py). Until tools/lab03/make_svgs.py exists the
table is text only, which is a visible difference from the reference labs. -->

| Tool | What it does |
| --- | --- |
| **Georeference** (Imagery tab, Alignment group) | Opens the Georeference tab for the selected raster layer. Everything in Steps 3 to 5 lives on that tab |
| **Fit to Display** (Prepare group) | Drops the scan into the current map view at roughly the right size and place, so you have something to drag points from. A first guess, not a result |
| **Add Control Points** (Adjust group) | The core tool. Click a point on the scan, then the same point on the basemap. Each pair is one link |
| **Transformation** (Adjust group) | Chooses the equation fitted to your control points. The menu states the minimum number of points each one needs |
| **Control Point Table** (Review group) | Lists every link with its residual, and the total RMS error. Where you find out what your points are actually doing |
| **Create Feature Class** (Catalog pane, right-click a geodatabase ▸ New) | Makes the empty point, line or polygon layer you are about to draw into |
| **Create Features** (Edit tab, Features group) | The editing pane you draw in |
| **Add** (attribute table, Field group) | Adds a field, so your features can carry a name |
| **Label** (Labeling tab) | Draws the values of a field on the map |
| **Calculate Geometry Attributes** (Data Management ▸ Features) | Writes a geometric property — area, perimeter, length — into a field you name. Use the **geodesic** options; they are measured on the ellipsoid rather than in the projected plane, so they do not inherit your projection's distortion |
| **Summary Statistics** (Analysis ▸ Statistics) | Reads a field across every row and writes one output row holding the total, mean, maximum or minimum. This is how the model turns a table of features into the single number you report |
| **Buffer** (Analysis ▸ Proximity) | Builds a polygon covering everything within a set distance of a feature. In Step 9 the distance is your own measured error, so the buffer is the band your digitized feature actually lies within |

## Example Model

<!-- TODO(instructor): Figure C is owed. The model below has been built and run end to end with
arcpy on 2026-09-18 -- every tool name, parameter and output in Step 9 is from that run -- but it
has not been assembled in ModelBuilder and exported as SVG (Export > Export To Graphic, nothing
selected). Until it is, students have a description and no diagram, which is a real gap: the
reference labs both open with the finished model. -->

The finished model has five tools and three parameters. It takes the features you digitized and the
error lines you drew, and it returns four things: the total area of what you captured, its
perimeter, your mean and worst georeferencing error, and an uncertainty envelope you can put on a
map.

Everything marked `P` in the model appears in the tool dialog you build in Step 9, which is what
makes Step 10 cheap: you re-run the model from its dialog once per georeference instead of
re-building anything.

## Complete the Lab

If you would rather work it out than be walked through it, everything you need is above: find a
plan-view sheet older than 1900, georeference it against a basemap you choose, digitize what is gone
including one measurable polygon, build the measurement model, and do the Step 10 comparison. The
step-by-step solution below is there when you want it.

> [!TIP]
> If you complete the lab without the step-by-step solution, say so in your report. There is no
> extra credit for it; it is worth knowing about yourself.

## Step-by-Step Solution

> [!NOTE]
> **Important Note #1.** These steps walk through one sheet with one set of control points. Step 10
> re-solves *the same sheet* with different subsets of those control points, so collect them
> carefully and generously the first time — you will use them several times. Build the model once
> and build it to be changed.

> [!NOTE]
> **Important Note #2.** The figures were captured in ArcGIS Pro 3.7.1 against a different sheet
> than yours, so your screen will not match exactly; the ribbon, the panes and the button names are
> what to follow. Paths in the figures start with `C:\` because they were captured on an instructor
> machine. Yours should be on `D:\`.

### Step 0 — Set Up the Project

1. Start ArcGIS Pro and create a new project using the **Map** template. Name it `Lab03`.
   In the *Location* box, browse to your lab folder; the box does not take a typed path.
2. Confirm that the project geodatabase is `Lab03.gdb`, in your lab folder. Everything you create
   goes in it.
3. On the **Map** tab, in the **Layer** group, click **Basemap** and choose one. Start with
   **Imagery Hybrid**: it shows what is on the ground now and labels the roads, which is what you
   need to match against.
4. Decide your coordinate system now, before you digitize anything. On the **View** tab, open **Map
   Properties ▸ Coordinate Systems** and set a projected system appropriate to your area — a UTM
   zone or a State Plane zone, in meters or feet. Record what you chose; it goes on your maps.

> [!WARNING]
> If you leave the map in the basemap's Web Mercator, every distance and area you measure later is
> wrong by a factor that grows with latitude. Lab 1 made this mistake deliberately so you would
> recognize it. Set a projected coordinate system. This lab measures areas, so it matters more here
> than it did there.

> [!TIP]
> **Check the result.** After you set the coordinate system, hover the pointer over the middle of
> your study area and read the coordinate pair at the bottom of the map view. In a UTM zone the
> easting should be a six-digit number between about 160,000 and 830,000 and the northing a
> seven-digit number. If you see numbers in the millions with a minus sign, or a pair that looks
> like degrees, the map is still in Web Mercator or still in geographic coordinates and step 4 did
> not take.

### Step 1 — Find a Historic Map

Work through *Where to find a sheet* above and download one. Save it in your lab folder, as an
image, with no spaces in the file name. Convert it from PDF first if you need to.

Record the repository, the sheet title, the survey date, the publication date, the scale and the
URL. You need all six in your report.

### Step 2 — Add the Scan

1. In the **Catalog** pane, right-click **Folders** and add a folder connection to your lab folder.
2. Find your image and drag it into the map.
3. If ArcGIS Pro offers to build pyramids or calculate statistics, let it.
4. Right-click the layer in the **Contents** pane and choose **Zoom To Layer**.

The scan will be somewhere absurd — a speck in the Gulf of Guinea off West Africa is the classic,
because an image with no spatial reference is placed at coordinates near zero, and zero longitude
and zero latitude is in the ocean south of Ghana.

![Map view zoomed to an ungeoreferenced historic map layer, which lands as a tiny speck in the Gulf of Guinea off the coast of West Africa](images/lab03-random-location.png)

**Figure 1.** An image with no spatial reference, drawn at the origin of the coordinate system.

> [!TIP]
> **Check the result.** If your scan appears in roughly the right place without any work from you,
> it already carries spatial reference information — a GeoTIFF or GeoPDF often does. That is not a
> problem, but it means the software has already made the choices this lab is about. Say so in your
> report, and georeference it anyway to see how your solution compares.

> [!NOTE]
> A scan can land at the origin even when it *does* carry a correct georeference, if it has a world
> file but no coordinate system — the numbers are right and the software does not know what they
> mean, so it reads degrees as meters and puts the sheet a hundred metres from the origin. If you
> suspect this, run **Define Projection** on the image and add it again.

### Step 3 — Fit to Display

1. Navigate the map to the area your sheet covers, at a scale where you can see the whole of it.
2. Select the scan in the **Contents** pane.
3. On the **Imagery** tab, in the **Alignment** group, click **Georeference**. The **Georeference**
   tab opens.

![ArcGIS Pro Imagery ribbon tab with the Georeference button highlighted in the Alignment group, and the Contents pane showing a historic map raster above the World Imagery basemap](images/lab03-georeference-button.png)

**Figure 2.** Where to find the Georeference button.

4. In the **Prepare** group, click **Fit to Display**. The scan jumps into the current view.
5. Make it semi-transparent so you can see the basemap through it. With the layer selected, go to
   the contextual **Raster Layer** tab, **Effects** group, and set **Transparency** to about 50 %.

![Map view after Fit to Display: a semi-transparent historic topographic sheet sits roughly over the modern imagery basemap](images/lab03-fit-to-display.jpg)

**Figure 3.** After Fit to Display, with transparency turned up.

![The ArcGIS Pro Georeference ribbon tab showing the Prepare, Adjust, Review, Save and Close groups](images/lab03-georeference-tab.png)

**Figure 4.** The Georeference tab in ArcGIS Pro 3.7.1. Everything in Steps 3 to 5 is on it: **Fit to
Display** in Prepare, **Add Control Points** and **Transformation** in Adjust, **Control Point
Table** in Review, and **Save** — which you must click before you close.

### Step 4 — Add Control Points

In the **Adjust** group, click **Add Control Points**. Then, for each point:

1. Click a feature on the **scan**.
2. Click the **same feature** on the basemap.

The scan moves as soon as you have enough points for the current transformation. It will keep
moving, and settling, as you add more.

![An 1893 USGS Escondido sheet displayed semi-transparently over modern imagery, with a single control point marker near the center of the sheet and a georeferencing status panel in the top right reading Transformation 1st Order Polynomial (Affine), Controls Points 1 / 1, Total RMS Errors Forward, Inverse and Forward-Inverse all 0.000000](images/lab03-control-point-example.jpg)

**Figure 5.** The very first control point, matched from the scan to the basemap. Read the status
panel in the top right: one point, and a total RMS error of 0.000000. The sheet is plainly still in
the wrong place, so that zero is telling you nothing — which is the whole point of the TIP below.
This is where you start, not where you stop; keep going until you have twelve, spread to the corners.

**How many, and where.** Collect **at least twelve**, and spread them out:

- Put points near all four **corners** of the sheet, not only in the middle. A transformation is
  only constrained where you constrain it; corners left free will wander.
- Use features that have not moved: **road intersections, section corners, rail crossings, river
  confluences, building corners on old buildings**. Do not use a river bank, a shoreline, a field
  edge or a tree.
- Avoid clusters. Four points within one town tell the transformation almost as little as one point.

> [!NOTE]
> Twelve is more than the old minimum of eight because Step 10 asks you to re-solve with subsets —
> three clustered, four at the corners, and all of them. You cannot take points away later if you
> did not collect them now, and re-collecting them means starting the sheet over.

**The minimum is not the target.** Each transformation needs a minimum number of points, and if you
give it exactly that many it fits them perfectly and tells you nothing:

| Transformation | Minimum control points |
| --- | --- |
| Zero Order Polynomial (Only Shift) | 1 |
| Similarity Polynomial | 3 |
| 1st Order Polynomial (Affine) | 3 |
| 2nd Order Polynomial | 6 |
| 3rd Order Polynomial | 10 |
| Adjust | 3 |
| Projective | 4 |
| Spline | 10 |

> [!WARNING]
> Do not click **Save** and close the Georeference tab until you have finished Step 10. Saving writes
> the transformation to the image and you want to try several first. If you must stop, either leave
> ArcGIS Pro open, or save and be prepared to re-collect your points.

> [!TIP]
> **Check the result.** With the default 1st Order Polynomial and exactly three points, your total
> RMS error will be 0.000000. That is not a good fit; it is an exact fit of three points by a
> transformation with exactly enough freedom to pass through three points. When the number stops
> being zero, you have started to learn something.

### Step 5 — Read the Residuals

In the **Review** group, click **Control Point Table**. Each row is one link, with its **residual**:
how far that point ended up from where you put it, in map units.

The table also reports a **total RMS error**, the root-mean-square of those residuals. Read it, and
then be careful with it.

> [!WARNING]
> **The RMS error is measured on the points you fitted.** Every control point in the table
> contributed to solving the transformation, so the residuals describe how well the equation
> reproduces its own inputs. It says nothing about the rest of the sheet. A high-order polynomial or
> a spline can drive the total RMS to zero and distort the map badly everywhere in between. A small
> number here is not a good result. It is a small number.

Work through the table once:

- If one point has a residual several times larger than the rest, look at it. You have probably
  matched the wrong intersection, or clicked a feature that moved. Delete it and re-collect it.
- If the residuals are all about the same size, that size is roughly the accuracy of your
  georeferencing at the points, which is the best case for the sheet as a whole.
- Record the total RMS error and the number of points. Both go in your report and in Step 10's table.

### Step 6 — Draw Your Error

The RMS error cannot tell you how good your georeferencing is, because it only knows about points
you already fitted. So measure it somewhere you did not fit — and rather than eyeball the gap,
**draw it**, so the model can measure it in Step 9.

Pick **three check features** that you did *not* use as control points and that still exist: a road
intersection on the far side of the sheet, a bridge, a section corner, a canal junction. At least
one of them should be near a corner of the sheet, where the transformation is least constrained.

1. In the **Catalog** pane, under **Databases**, right-click `Lab03.gdb`, then **New ▸ Feature
   Class**. Name it `ErrorLines`, choose **Line**, and give it the coordinate system of your map.
2. On the **Edit** tab, click **Create**, pick `ErrorLines` in the **Create Features** pane, and for
   each check feature draw a **two-point line**: start where the *scan* puts the feature, end where
   the *basemap* puts it. Double-click to finish each line.
3. Click **Save** in the **Manage Edits** group.

Each line is one measurement of how wrong your georeferencing is, at a place that had no say in the
answer. Step 9's model turns the three of them into a mean and a worst case.

> [!TIP]
> **Check the result.** All three lines should point in roughly the same direction. A systematic
> offset — every line pointing the same way — means the whole sheet is shifted, which is usually the
> old survey's error rather than yours. Lines pointing in different directions mean the sheet is
> being stretched or bent, which usually is yours. Say in your report which of the two you have.

> [!WARNING]
> Draw each line in the same order every time: scan position first, basemap position second. The
> length is the same either way, but in Step 10 you will re-draw these lines under each georeference,
> and a consistent direction is what lets you compare the *direction* of the error between runs.

### Step 7 — Digitize the Features

Now find what is gone. Turn the transparency up and down, switch basemaps, and look for features on
the scan with nothing under them: a town site, a road that stops, a rail grade, a channel that has
moved, a lake that has shrunk.

1. In the **Catalog** pane, under **Databases**, right-click `Lab03.gdb`, then **New ▸ Feature
   Class**.

![ArcGIS Pro Catalog pane, Project tab, with the Databases entry expanded to show a single project geodatabase named Lab03.gdb, selected](images/lab03-catalog-project-gdb.png)

**Figure 6a.** The project geodatabase in the Catalog pane. There is one, it is named for the lab,
and everything you create in this lab goes in it.

![The ArcGIS Pro context menu for a geodatabase with New highlighted and its submenu open, listing Feature Dataset, Feature Class, Table, View, Relationship Class and Raster Dataset](images/lab03-new-feature-class.png)

**Figure 6b.** Right-click the geodatabase and choose **New ▸ Feature Class**.

2. Name it, choose the geometry type, and give it the coordinate system of your map.
3. Select the new layer in the **Contents** pane, open the **Edit** tab, and click **Create** in the
   **Features** group.
4. In the **Create Features** pane, click your feature class and draw. Click once for a point; click
   along a line and double-click to finish it; click around a shape and double-click to close a
   polygon.
5. Click **Save** in the **Manage Edits** group when you are done. Edits are not saved until you say so.

![ArcGIS Pro Edit ribbon tab with the Create button highlighted in the Features group](images/lab03-edit-create-features.png)

**Figure 7.** Starting an edit session.

Capture **at least six** features. Six is enough to say something; two is an anecdote.

**One of them must be a polygon you can measure.** A lake, a pond, a town boundary, a field, a
quarry, a millpond, the footprint of a vanished building complex — anything with a closed outline
that has corners or headlands you could find again. This is the feature Step 9 measures and Step 10
re-measures, so put it in its own polygon feature class, named something you will recognize.

> [!TIP]
> **Check the result.** Turn the historic scan off. Your digitized features should still be in
> sensible places relative to the modern basemap — a vanished road should still connect to roads that
> exist. If a feature lands in the middle of a lake, either you drew it wrong or your georeferencing
> is worse than the RMS error suggested.

> [!NOTE]
> Trace your measurable polygon deliberately, not quickly. In Step 10 you will trace it again under a
> different georeference and compare the two areas, and any sloppiness in your tracing shows up in
> that comparison as though it were a georeferencing effect. Pick identifiable points on the outline
> — a headland, a corner, a river mouth — and put a vertex on each of them, so that your second
> tracing follows the same decisions as your first.

### Step 8 — Name and Label

1. Right-click your feature layer and open the **Attribute Table**.
2. In the **Field** group, click **Add**. Add a field named `Location_Name`, data type **Text**.
   Save the field definition.

![Attribute table toolbar in ArcGIS Pro with the Add button in the Field group](images/lab03-add-field-button.png)

**Figure 8.** Adding a field from the attribute table.

![The Fields view for a feature class showing OBJECTID, Shape, and a new Location_Name field with its data type set to Text](images/lab03-fields-view.png)

**Figure 9.** The new field in the Fields view.

3. Back in the attribute table, type a name for each feature. Use the name from the historic sheet
   where it has one; that name is part of what you found.

![Attribute table for a feature class with four named point records in the Location_Name field](images/lab03-attribute-table-filled.png)

**Figure 10.** Naming the digitized features.

4. With the layer selected, open the **Labeling** tab, check **Label Features In This Class**, and
   set the **Field** to `Location_Name`.

![ArcGIS Pro Labeling ribbon tab with Label Features In This Class checked and Location_Name chosen in the Field drop-down](images/lab03-labeling.png)

**Figure 11.** Labeling the features.

### Step 9 — Build the Measurement Model

You now have a polygon you want the area of, and three lines that say how wrong your georeferencing
is. Both of those are about to be measured several times, so build the measuring once, as a model.

1. On the **Analysis** tab, click **ModelBuilder**. A blank model canvas opens on the contextual
   **ModelBuilder** tab. Press **Ctrl+R** to rename it `Measure Digitized Features`.
2. Add the five tools below from the **Geoprocessing** pane, connecting each output to the next
   input by dragging.

| # | Tool | What to set |
| --- | --- | --- |
| 1 | **Calculate Geometry Attributes** | Input: your measurable polygon feature class. Add two fields: `Area_km2` = **Area (geodesic)**, area unit **Square kilometers**; and `Perim_km` = **Perimeter length (geodesic)**, length unit **Kilometers** |
| 2 | **Summary Statistics** | Input: the output of tool 1. Statistics: `Area_km2` **SUM**, `Perim_km` **SUM**. Output table `Area_Summary` |
| 3 | **Calculate Geometry Attributes** | Input: `ErrorLines`. Add one field: `Error_m` = **Length (geodesic)**, length unit **Meters** |
| 4 | **Summary Statistics** | Input: the output of tool 3. Statistics: `Error_m` **MEAN**, `Error_m` **MAX**, `Error_m` **MIN**. Output table `Error_Summary` |
| 5 | **Buffer** | Input: the output of tool 1. Distance: a **linear unit** in meters, which you will make a parameter. Output `Uncertainty_Envelope` |

3. Rename every intermediate dataset to something a reader can follow. A model whose boxes say
   `Output Feature Class` and `Output Feature Class (2)` is not a description of anything.
4. **Expose the parameters.** Right-click each of these and choose **Parameter**, or select it and
   press **Ctrl+P**:
   - the **measurable polygon** input on tool 1
   - the **`ErrorLines`** input on tool 3
   - the **Buffer distance** on tool 5
   - the two **output tables** and the **uncertainty envelope**
5. Press **Ctrl+S** to save the model.

> [!NOTE]
> **Why bother with parameters.** Step 10 runs this model at least three times. With parameters you
> open the tool dialog, change two boxes and click Run. Without them you open the model, edit tool
> dialogs inside it, and save, three times over, and any mistake is invisible. The reason to build a
> model is never the first run; it is the fourth.

> [!WARNING]
> Use the **geodesic** area and length options, not the planar ones. Planar measurements are made in
> your projection's flat plane and carry its distortion; geodesic measurements are made on the
> ellipsoid. On a sheet the size of a county the difference is small, on a sheet the size of a state
> it is not, and the geodesic number is the one you can defend.

6. Run the model from its dialog. In the **Catalog** pane, under **Toolboxes ▸ Lab03.atbx**,
   double-click `Measure Digitized Features`, fill in the three inputs, and click **Run**. For the
   buffer distance on this first run, use the **mean error** the model is about to report — so run it
   once with any value, read `Error_Summary`, then run it again with the real number.

> [!TIP]
> **Check the result.** Open `Area_Summary` and `Error_Summary` from **Standalone Tables** in the
> Contents pane. `Area_Summary` should have exactly **one row**, with `FREQUENCY` equal to the number
> of polygons you digitized. `Error_Summary` should have one row with `FREQUENCY` = 3, one per check
> line. If `FREQUENCY` is 0 the model ran on an empty feature class — you drew into the wrong layer,
> or you did not click Save in the Manage Edits group. If `SUM_Area_km2` is a number in the millions,
> your area unit is square meters rather than square kilometers.

> [!NOTE]
> The uncertainty envelope is worth looking at before you go on. It is your digitized feature grown
> by your own mean error, and on many sheets it is dramatically bigger than the feature itself. That
> is not a mistake in the model. It is the honest picture of what you know.

### Step 10 — Test the Georeference

Your georeferenced sheet is *an* answer. It is the answer that one transformation gives for the
points you happened to collect. Before you put your name on it, find out how much of it is the sheet
and how much of it is your choice.

**First, the georeference.** Using the control points you already have, re-solve five ways. To drop
points from the solve, delete rows in the **Control Point Table**; to change the equation, use the
**Transformation** menu in the Adjust group.

![The Transformation menu in ArcGIS Pro 3.7.1, listing Zero Order Polynomial, Similarity Polynomial, 1st Order Polynomial (Affine), 2nd Order Polynomial, 3rd Order Polynomial, Adjust, Projective and Spline, each with the minimum number of control points it requires](images/lab03-transformation-list.png)

**Figure 12.** The Transformation menu, with the minimum control points each one needs.

For each run, re-draw your three error lines — the check features have not moved, but the scan has —
and run the model. Record:

| Run | Control points | Transformation | Total RMS error | Mean check error (m) | Worst check error (m) |
| --- | ---: | --- | ---: | ---: | ---: |
| A — clustered | 3, all near the middle | 1st Order (Affine) | | | |
| B — corners only | 4, one near each corner | 1st Order (Affine) | | | |
| C — all of them | all 12 or more, spread | 1st Order (Affine) | | | |
| D — higher order | all 12 or more, spread | 2nd Order Polynomial | | | |
| E — spline | all 12 or more, spread | Spline | | | |

**Then, what it does to a measurement.** For **three** of those runs — A, C and E — re-trace your
measurable polygon into a new feature class and run the model on it. This is the expensive part of
the lab and it is the part that matters, so trace carefully and put your vertices on the same
identifiable points each time.

| Run | Area (km²) | Perimeter (km) | Difference from run C |
| --- | ---: | ---: | ---: |
| A — clustered | | | |
| C — all of them | | | — |
| E — spline | | | |

Then answer these three questions in your report, in bold, in this order:

1. **Which run gave the lowest total RMS error, and is that the one you would use?** Explain the
   difference between the two answers if there is one.
2. **What happened to your mean check error as you changed the control points?** Did it track the
   total RMS error, or move against it? Say what that means about what RMS can and cannot tell you.
3. **How much did your measured area change across the three runs, and how much of that change is
   your tracing rather than your georeferencing?** Give a percentage, say how you would separate the
   two, and state what accuracy you would claim if a client asked for the area of this feature.

Finally, pick one run other than your baseline for **Map 2**, and say on the map what you changed and
why you chose that run to show.

> [!TIP]
> One of these runs will give you the best number you see all lab. It is the one you should trust
> least. Watch what the spline does, and watch what run A does.

### Going further: the graticule (optional, up to five points)

Many nineteenth-century survey sheets carry a printed **graticule** — a grid of latitude and
longitude lines, with the degrees labeled around the border. If your sheet has one, you can
georeference it a second way, from the sheet's own coordinates: put control points on the graticule
intersections and give each one the latitude and longitude printed beside it, rather than matching it
to a feature on the basemap.

You then have two georeferences of the same sheet: one fitted to the ground, and one fitted to what
the surveyors believed the ground's coordinates were. **The difference between them is the survey's
own error**, separated out from yours.

Do this and report, for at least three features: how far apart the two georeferences put them, in
which direction, and whether the difference is a constant shift or grows across the sheet. Say what
that implies about how the original survey was made — and note whether the error is the same in
latitude and in longitude, because on many sheets of this period it is not.

> [!WARNING]
> A graticule fit will give you a beautiful RMS error, because a printed graticule is drawn very
> regularly and your points will sit on it almost perfectly. That number tells you nothing at all
> about whether the sheet is in the right place. Check it against a ground feature before you believe
> it.

## Deliverables

Make **two** professional map layouts, each a full page (8.5 × 11):

1. **Map 1 — your baseline.** The transformation you would defend. Show four things: the modern
   basemap, the georeferenced historic sheet, your digitized features, labeled, and the
   **uncertainty envelope** from the model. Show your control points as well.
2. **Map 2 — one alternative run.** The same area under a different run from Step 10, with the title
   and text box saying which one and why you chose to show it.

Write a brief report (2–3 pages of text, plus your figures and maps) covering:

- your name, the date, the course, and the name of your peer reviewer, with a sentence on what you
  changed because of them
- the requirements of the project and your approach, in your own words
- **the source of your historic map**: repository, title, survey date, publication date, scale and URL
- the six metadata answers from *Judging the source*, and what they mean for your result
- which basemap you georeferenced against and why, and the coordinate system your map is in
- **how many control points you used, how you distributed them, and which transformation you chose**
- your **total RMS error**, and what you did about any point whose residual stood out from the rest
- **your three check features and the error at each**, as distances on the ground, with a sentence on
  whether the three lines pointed the same way or different ways, and what that told you
- **a description of your model**: what each of the five tools does, which inputs you exposed as
  parameters and why, and a full-page figure of the model exported from ModelBuilder, plus one
  capture of the tool dialog showing the parameters exposed
- **the area and perimeter of your measurable polygon**, in stated units, with what it is and what is
  there now
- your Step 10 tables and the answers to their three questions
- a description of your other digitized features: what they are, what they were called, and what is
  there now
- where your result is wrong and why, and what data would fix it
- this rubric pasted in, with your self-assessment in every row
- the optional graticule comparison, if you did it

> [!IMPORTANT]
> **Peer review before you submit.** Have another student in the class read your report against
> the rubric and give you feedback, then act on that feedback before the deadline. Name your
> reviewer in the report and say in a sentence what you changed because of them. A report nobody
> else has read is a draft, not a submission.

## References

Esri. *Overview of georeferencing.* ArcGIS Pro documentation.
<https://pro.arcgis.com/en/pro-app/latest/help/data/imagery/overview-of-georeferencing.htm>

Esri. *PDF To TIFF.* ArcGIS Pro tool reference.
<https://pro.arcgis.com/en/pro-app/latest/tool-reference/conversion/pdf-to-tiff.htm>

Esri. *Calculate Geometry Attributes.* ArcGIS Pro tool reference.
<https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/calculate-geometry-attributes.htm>

Esri. *Summary Statistics.* ArcGIS Pro tool reference.
<https://pro.arcgis.com/en/pro-app/latest/tool-reference/analysis/summary-statistics.htm>

U.S. Geological Survey. *Historical Topographic Map Collection.*
<https://www.usgs.gov/programs/national-geospatial-program/historical-topographic-maps-preserving-past>

## Example Maps

<!-- TODO(instructor): these two are finished layouts from earlier offerings, kept because they show
what a good result looks like. They are not a baseline/scenario pair, neither shows an uncertainty
envelope, and neither has a usable source citation any more. Building a real pair the way
tools/lab01/build_layouts.py and tools/lab02/build_layout.py do is owed, and is now possible: a
georeferenced sheet exists at C:\Ames\Lab03\Data. -->

![Student example layout: a georeferenced historic railroad map of the American West over a modern basemap, with missing cities and newer cities symbolized separately, control points shown as pins, plus title, legend, north arrow and scale bar](images/lab03-example-state-map.jpg)

**Figure 13.** A finished layout showing towns on an 1876 sheet that are no longer populated places.
Note that the control points are on the map, the digitized features are labeled, and the historic
sheet is transparent enough to see the basemap through it.

![Student example layout: a georeferenced historic pictorial map of Luxembourg over a modern basemap, with four missing roads and a rotary digitized and labeled, control points shown as pins, plus title, legend, north arrow and scale bar](images/lab03-example-city-map.jpg)

**Figure 14.** A second finished layout, this one digitizing streets rather than places.

> [!NOTE]
> These are examples, not templates. Your maps should be better than these: your name must be on
> them, your symbology should suit the features you actually digitized, and Map 1 must show the
> uncertainty envelope, which neither of these has.

## Rubric for Georectifying and Digitizing Historic Maps

Fifty points in five parts of ten. The bullets say what each part is worth, so you know exactly what
to submit.

| Item | Points |
| --- | --- |
| **Write-up** (2–3 pages)<br>• Assignment title, your name, date and course; your peer reviewer named, with a sentence on what you changed because of them (1)<br>• The requirements of the project and your approach, in your own words (2)<br>• The source of your sheet — repository, title, survey and publication dates, scale and URL — and the six metadata answers, with what they mean for your result (3)<br>• Where your result is wrong and why, and what data would fix it (2)<br>• Clear, organized writing: figures numbered and referred to in the text, sources credited, and this rubric pasted in with your self-assessment in every row (2) | /10 |
| **Georeferencing** — correct and defensible<br>• At least twelve control points, distributed across the whole sheet rather than clustered, with the count reported (2)<br>• The Control Point Table read: total RMS error reported, and any outlying residual investigated and explained (2)<br>• Three check features that were **not** used as control points, drawn as error lines and reported as distances on the ground (3)<br>• Whether the three error lines pointed the same way or different ways, and what you concluded from that (1)<br>• Which basemap you georeferenced against and why, and which coordinate system your map is in (2) | /10 |
| **Digitizing and the measurement model**<br>• At least six features digitized from the historic sheet that are not on the modern basemap, including one measurable polygon, in feature classes of the correct geometry type in the project geodatabase and in the map's coordinate system (3)<br>• A `Location_Name` field populated and labeled on the map (1)<br>• The model runs end to end from its own dialog and returns the four outputs (3)<br>• Full-page model figure exported from ModelBuilder, and a capture of the tool dialog with the parameters exposed (2)<br>• A description of the model a reader could rebuild from, saying which inputs you made parameters and why (1) | /10 |
| **Map 1 — your baseline** (full page, 8.5 × 11)<br>• Title stating the transformation and the number of control points used (1)<br>• Neat line, north arrow and scale bar (1)<br>• Text box with author, date, map projection, and the sheet's title and date (1)<br>• All four layers shown: basemap, georeferenced sheet, digitized features, uncertainty envelope (2)<br>• Digitized features clearly symbolized and labeled, with a legend that explains what the envelope is (2)<br>• Control points shown (1)<br>• Zoomed to an appropriate scale, and all text legible when printed (2) | /10 |
| **Sensitivity** (Step 10)<br>• The five-run georeference table, with control points, transformation, total RMS error, and mean and worst check error for each (3)<br>• The three-run measurement table, with area, perimeter and difference from baseline (2)<br>• Which run gave the lowest RMS and whether that is the one you would use (1)<br>• What happened to the check error as the control points changed, and what that says about RMS (2)<br>• How much the measured area moved, how much of that is tracing rather than georeferencing, and what accuracy you would claim to a client (2) | /10 |
| **Total** | **/50** |
| **Extra credit — the graticule comparison**<br>• A second georeference solved from the sheet's printed graticule (2)<br>• The difference between the two answers at three or more features, with direction, and whether it is a constant shift or grows across the sheet (2)<br>• What that implies about how the original survey was made, including whether latitude and longitude are equally wrong (1) | up to +5 |

Map 2 is graded inside the sensitivity row: the run you chose to show, and the title and text box
saying what changed and why.

> [!NOTE]
> **Using AI on this lab.** Use AI freely to understand a tool, work out an error, or
> tighten your write-up, and add one line at the end of your report saying what you used it
> for. Do not take a field name, an expression, a coordinate system, or a number from it —
> those come from your own data, and the rubric asks you to defend every one. See the
> [AI Use Policy](../../policies/ai-policy.md) for the full policy.

<!--
DRAFT migration notes. This draft expands the assigned page of 2026-09-17. See the review box at the
top for what changed and why.

VERIFIED 2026-09-18 with arcpy on the local ArcGIS Pro 3.7.1 install (license ArcInfo/Advanced), in
C:\Ames\Lab03\ModelTest.gdb, on stand-in geometry:
- arcpy.management.CalculateGeometryAttributes with AREA_GEODESIC + SQUARE_KILOMETERS and
  PERIMETER_LENGTH_GEODESIC + KILOMETERS runs and writes both fields.
- arcpy.analysis.Statistics with SUM returns one row carrying FREQUENCY, SUM_Area_km2, SUM_Perim_km.
- CalculateGeometryAttributes with LENGTH_GEODESIC + METERS on a line feature class writes Error_m.
- arcpy.analysis.Statistics with MEAN/MAX/MIN on that returns one row of three statistics.
- arcpy.analysis.Buffer with a linear unit in meters runs on the polygon output.
That is the five-tool chain in Step 9, in order, with the parameter shapes the step describes.

LICENSE NOTE: an earlier design used arcpy.analysis.Near to pair scan points with truth points
automatically. Near ran here at Advanced, but it is not available at every license level, so the
design was changed to student-drawn error lines measured with Calculate Geometry Attributes. That is
core functionality at any license, and it is better teaching: the student draws the error rather than
having the software find it. Do not reintroduce Near without checking the student license level.

SCALE OF THE EFFECT: buffering a 1460.6 km2 stand-in polygon by its own 8,290 m mean error produced a
2,954.0 km2 envelope -- more than double. Student numbers will be far smaller, but the shape of the
result is the point, and it is why the envelope is on Map 1.

DESIGN NOTE, why the polygon is re-traced rather than re-projected: digitized features are stored in
map coordinates, so changing the transformation moves the scan and leaves the features where they
were. There is no way to make a measurement respond to the georeference without re-tracing. This is
stated plainly to students in Step 7's NOTE and Step 10's question 3 asks them to separate their
tracing error from the georeferencing effect, which is the honest treatment and is itself worth
teaching. It is also why the measurement table is three runs and the georeference table is five: the
cheap axis gets more runs than the expensive one.

CONTROL POINT COUNT raised from eight to twelve, because Step 10's run C needs "all of them" to be
meaningfully more than run B's four, and because 3rd Order Polynomial and Spline both need ten.

STILL OWED, in priority order:
1. Figure C, the model diagram: build the Step 9 model in ModelBuilder and export it as SVG, then cut
   the per-step snippets from that same export the way tools/lab02/cut_model_snippets.py does.
2. tools/lab03/make_svgs.py and the tool-table icons, which Labs 1 and 2 both have.
3. Figures 7 to 11, still the 2026-09-03 captures from an older ArcGIS Pro.
4. Example maps as a real baseline/scenario pair, now possible: a georeferenced sheet is on disk at
   C:\Ames\Lab03\Data (see tools/lab03/GEOREF_FINDINGS.md).
5. A metadata infographic, lettered Figure A or B, which both reference labs have and this page has
   none of.
6. Pilot: no pilot has been run on this draft. Per section 6 of the lab guide it must not be promoted
   without at least the no-GUI pilot.

TODO(instructor) decisions still open, from tools/lab03/EXPANSION_PROPOSAL.md:
- Whether to host the 1852 Stansbury sheet in docs/data/ so every student works one sheet and the lab
  can publish real check values for the first time. This draft names it as a worked example only.
- Whether Lab 3 becomes a two-week lab. This draft is materially longer than the assigned page and
  shares Week 4 with the remote sensing deck.
- Whether the page title's "Historic Maps" should propagate to the LABS table in
  tools/build_schedule.py and to Learning Suite, which still say "Images".
-->
