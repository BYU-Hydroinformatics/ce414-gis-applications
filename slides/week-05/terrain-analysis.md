---
marp: true
theme: ce414
paginate: true
footer: "CE 414 · Week 5 — Terrain Analysis"
---

<!-- _class: lead -->
<!-- _paginate: skip -->

![bg right:45%](images/ta-shaded-relief.jpg)

# Terrain Analysis

CE 414 Engineering Applications of GIS
Dr. Dan Ames

<!-- Week 5 concepts lecture. Everything in this deck is a raster surface operation: the input is a DEM and the output is another raster that answers an engineering question. The lab this week applies it. -->

---

# Today's Goals

![bg right:34% w:90%](images/ta-elevation-surface.png)

By the end of class you should be able to:

- Define an **elevation surface** and name the ways a **DEM** can represent one
- Say where U.S. and global DEMs come from, and at what **cell size**
- Explain what **slope**, **aspect**, **curvature**, and **hillshade** measure, and how each is computed from a 3 × 3 window
- Compute slope at a cell by hand, two different ways, and get the same answer the software would
- Explain what a **viewshed** is and name three engineering uses for one

<!-- Frame the hour. The first third is where elevation data comes from; the middle is what you derive from it; the last is visibility. Each derived surface is a raster in, raster out. -->

---

<!-- _class: lead -->

# Part 1
## Elevation surfaces and where DEMs come from

<!-- Divider. Move quickly through the data-source slides; the students mostly need to know which portal to open and what cell size to expect. -->

---

# Elevation surface and DEM

![bg right:42% w:88%](images/ta-elevation-surface.png)

- **Elevation surface** — the ground surface elevation at each point
- **Digital Elevation Model (DEM)** — a digital representation of an elevation surface

Examples of a DEM include a (square) digital elevation grid, a triangular irregular network, a set of digital line graph contours, or random points.

<!-- The distinction that matters: the surface is the real thing, the DEM is a model of it. A grid is only one way to model a surface; a TIN, contours and a point cloud are others. Everything else today assumes the square grid case. -->

---

# Digital elevation grid

**Digital elevation grid** — a grid of cells (square or rectangular) in some coordinate system, having land surface elevation as the value stored in each cell. A **square digital elevation grid** is the common special case.

![h:370 center](images/ta-elevation-grid-anatomy.jpg)

<!-- Walk the anatomy: number of rows, number of columns, cell size, an (X,Y) origin, and NODATA cells where there is no value. The number in the cell is an elevation; the color is only symbology applied to that number. -->

---

# DEM data sources

- **3″** (3 arc seconds ≈ 90 m) DEMs from **SRTM** (space shuttle global scan)
- **30 m** DEMs derived from 1:24,000 scale maps, available for the full U.S.
- **10 m** DEM for the U.S., resampled and downscaled from 30 m for most of the U.S.
- **1 m** DEM for parts of the earth, derived from lidar

<!-- TODO(graphic): this source slide was text only; a four-tier resolution-ladder figure would carry it. None was generated for this pass. -->

<!-- These four tiers are the mental model students should leave with: coarse global, medium national, fine national, very fine and patchy. The specific dataset names below the tiers have moved on since this slide was written. -->

<!-- VERIFY: "3″ (3 arc seconds ≈ 90 m) DEMs from SRTM" — SRTM is distributed at 1 arc-second and 3 arc-second; confirm which product and which resolution is meant. -->
<!-- VERIFY: "30 m DEMs derived from 1:24,000 scale maps available for the full U.S." — this describes the legacy NED / USGS DEM lineage; confirm against what USGS actually distributes now. -->
<!-- VERIFY: "10 m DEM for the US resampled and downscaled from 30 m for most of the U.S." — check whether the 1/3 arc-second product is natively 10 m or derived from 30 m, and note that going 30 m to 10 m is upsampling, not downscaling. -->
<!-- VERIFY: "1 m DEM for parts of the earth derived from LiDAR" — confirm current coverage and the correct product name. -->
<!-- TODO(instructor): restate this slide in current USGS 3DEP terminology (3DEP product tiers and their arc-second/meter designations), and decide whether "NED" should still be named at all or only mentioned as the historical predecessor. -->

---

# Where to get global DEMs

![bg right:40% w:92%](images/ta-global-dem-3d.jpg)

- A maintained roundup of free global elevation data:
  [gisgeography.com/free-global-dem-data-sources](https://gisgeography.com/free-global-dem-data-sources/)
- Read the entry for each dataset before you download: **coverage**, **cell size**, **vertical datum**, and **license**
- The next four slides are the sources you will actually use in this course

<!-- Have the page open. The point of the list is that "a DEM" is never just "a DEM" — you pick one, and the choice shows up in every derived surface afterward. -->

---

# USGS — The National Map

![bg right:52% w:96%](images/ta-usgs-national-map.jpg)

- Clearinghouse for many U.S. DEM and other datasets
- [nationalmap.gov](https://www.nationalmap.gov/)
- Select an area, filter to **Elevation Products (3DEP)**, then pick a resolution and a file format

<!-- This is the portal students use for the lab. Show the subcategory tree on the left: they check the elevation product they want, draw an extent, and the download list appears. -->

<!-- TODO(screenshot): The National Map download interface has been redesigned since this capture; re-shoot the current page. -->

---

# NASA SRTM

![bg right:52% w:96%](images/ta-nasa-srtm-page.jpg)

- During its 11-day mission, the Space Shuttle *Endeavour*, carrying SRTM, orbited the Earth 16 times
- As part of this mission, it captured Earth's topography at **1 arc-second (30 meters)** for over 80% of the Earth's surface

<!-- The Shuttle Radar Topography Mission flew in February 2000. Radar interferometry from a fixed mast: two antennas, one baseline, one pass. It is still the reference global DEM for a lot of hydrology work. -->

<!-- VERIFY: "orbited the Earth 16 times" — 16 is the number of orbits per day, so the mission total is much larger. Check the figure before presenting. -->
<!-- VERIFY: "over 80% of the Earth's surface" — SRTM coverage is usually quoted as a fraction of the *land* surface between about 60° N and 56° S. Confirm the wording. -->
<!-- TODO(screenshot): this is a capture of a third-party web page, complete with an advertisement. Replace with a NASA/USGS source page or a plain SRTM coverage figure. -->

---

# NASA ASTER

![bg right:52% w:96%](images/ta-aster-gdem-earthdata.jpg)

- ASTER GDEM has a global resolution of 90 meters, with a resolution of 30 meters in the United States
- Search and download through NASA **Earthdata Search**

<!-- ASTER GDEM is built from stereo optical imagery rather than radar, so it fills in where SRTM has voids, but it is noisier over low-contrast surfaces such as snow, sand and water. -->

<!-- VERIFY: the "90 m global / 30 m U.S." resolution claim. ASTER GDEM is generally distributed at 1 arc-second globally; confirm which product version this describes. -->
<!-- Note: the source slide repeated this sentence twice, once beginning "ASTER GDEM has..." and once "ASTER GDEM boasted..."; the duplicate was removed. -->
<!-- TODO(screenshot): Earthdata Search interface capture is stale; re-shoot. -->

---

# JAXA — Japan's space agency

![bg right:52% w:96%](images/ta-jaxa-alos-portal.jpg)

- JAXA distributes the **ALOS** global elevation and land-observation products
- Another independent global DEM to cross-check SRTM and ASTER against

<!-- Worth naming so students know there is more than one global option. The useful habit is comparing two DEMs over the same area and seeing where they disagree — usually steep terrain, forest canopy and water. -->

<!-- VERIFY: the source slide had no text at all here beyond the title; the two bullets describe what the captured page shows. Confirm which ALOS product is meant (and its cell size) before presenting. -->
<!-- TODO(screenshot): JAXA portal capture is stale; re-shoot. -->

---

# Mars DEMs!

![bg right:52% w:96%](images/ta-mars-dem-quadrangles.jpg)

- Elevation surfaces are not a terrestrial idea: Mars is mapped, quadrangle by quadrangle, the same way
- Same data model, same derived surfaces, no field survey

<!-- A one-slide aside, but it makes the point that everything in this lecture is arithmetic on a grid of numbers. Nothing in the slope or viewshed math cares which planet the numbers came from. -->

---

# Coverage of 30 m and 3″ DEMs

![h:470 center](images/ta-dem-coverage-extents.png)

<!-- Two different things are being compared: cell size and tile extent. The 3-arc-second DEM covers a 1-degree tile; the 30 m DEM covers a 7.5-minute quadrangle, which is a small square inside it. Finer cells mean smaller tiles and more files for the same study area. -->

---

# Cell size changes what you can see

<div class="columns">
<div>

**30 m cells**

![w:420 center](images/ta-cellsize-30m.png)

</div>
<div>

**100 m cells**

![w:420 center](images/ta-cellsize-100m.png)

</div>
</div>

<!-- Same terrain, same symbology, two cell sizes. The red outline is the same parcel in both. At 100 m the small drainages disappear and the parcel spans only a handful of cells; any slope you compute for it is an average over a much larger footprint. -->

<!-- TODO(instructor): add the native-versus-resampled distinction here — a 10 m grid resampled from 30 m source data has 10 m cells but 30 m information, and every derived surface inherits the coarser one. Decide how to state it and whether to demonstrate it with a resampled raster. -->

---

<!-- _class: lead -->

# Part 2
## Describing the surface

<!-- Divider. From here on, every slide is a raster derived from the DEM by looking at a moving 3 x 3 window. -->

---

# Some common terrain analyses

<style scoped>
table { font-size: 19px; width: 100%; }
th, td { padding: 3px 9px; }
</style>

| Variable | Description | Importance |
| --- | --- | --- |
| Height | Elevation above base | Temperature, vegetation, visibility |
| Slope | Rise relative to horizontal distance | Water flow, flooding, erosion, travel cost |
| Aspect | Downhill direction of steepest slope | Temperature, vegetation, soil moisture |
| Upslope area | Watershed area above a point | Soil moisture, runoff volume and timing, erosion |
| Flow length | Mean upstream flow path length to a point | Sediment and erosion rates |
| Profile curvature | Curvature parallel to slope direction | Erosion, water flow acceleration |
| Plan curvature | Curvature perpendicular to slope direction | Water flow convergence, soil water, erosion |
| Visibility | Site obstruction from given viewpoints | Utility location, viewshed preservation |

<!-- The "Importance" column is the reason any of this is in a civil engineering course. Each row is one raster tool: the input is the DEM, the output is another raster in the units named. -->

<!-- TODO(graphic): a small figure pairing each variable with a one-glance thumbnail (slope, aspect, curvature, visibility) would carry this slide; none was generated for this pass. -->
<!-- TODO(instructor): this table is the natural place to separate susceptibility, hazard, risk and exposure — slope and curvature feed a susceptibility surface, not a risk map. Decide whether to define the four terms here or in a later week. -->

---

# Shaded relief

![bg right:46% w:94%](images/ta-shaded-relief.jpg)

- Shaded relief maps are a **visualization** or symbology effect in which shadowing is applied to highlight the terrain
- **Why?**

<!-- Ask it as a real question before answering. A hillshade is not a measurement; it is a rendering of one, computed by illuminating the surface from an assumed sun azimuth and altitude. It reads as three-dimensional because the eye is good at shape from shading. In ArcGIS Pro this is the Hillshade tool in Spatial Analyst. -->

<!-- VERIFY: ArcGIS Pro tool names named in the speaker notes of this deck (Hillshade, Slope, Aspect, Curvature, Contour, Viewshed) against the Pro version the course is taught on. -->
<!-- TODO(instructor): connect the hillshade to scale and uncertainty — the illumination azimuth is a choice, and it decides which landforms appear and which vanish. Decide how much of that to say here. -->

---

# Contours

![bg right:46% w:94%](images/ta-contours-3d-terrain.jpg)

- "Connected lines of uniform elevation that run at right angles to local slope"
- Why not just use a continuous color ramp?
- What types of maps benefit from the use of contour lines?

<!-- Contours give you readable numbers off a paper or PDF map, which a color ramp cannot. They also carry slope information in their spacing. Ask the class where they have actually used contours: grading plans, site drainage, trail maps. -->

---

<!-- _class: quiz -->

# What does the terrain look like at A, B, C and D?

![bg right:44% w:92%](images/ta-contour-reading-quiz.png)

- **A?**
- **B?**
- **C?**
- **D?**
- The photo is the same terrain, from the camera position marked on the map

<!-- Let them argue before you show the photo connection. Close contours mean steep, wide spacing means flat; contours that point upstream mark a valley, contours that bulge downhill mark a ridge. Match each letter to a feature in the photograph. -->

---

<!-- _class: quiz -->

# What are the steps to convert the DEM to the contour lines?

![bg right:40% w:92%](images/ta-dem-to-contours.jpg)

- Top: the DEM, symbolized as a gray ramp
- Bottom: contour lines derived from it
- What happens, cell by cell, in between?

<!-- Answer sketch: pick a contour interval, then for every pair of adjacent cells find where the chosen elevation falls between them and interpolate the crossing point; connect crossings into lines; smooth. The tool is Contour in Spatial Analyst. Ask what happens to the output if the interval is too small for the cell size. -->

---

# Slope

![bg right:34% w:88%](images/ta-slope-rise-run.png)

- "Slope is defined as the change in elevation (**rise**) with a change in horizontal position (**run**)"
- Often reported in **degrees** between zero (flat) and 90 (vertical). At rise/run = 1, the slope is 45 degrees
- Can also be expressed as a **percent** = (rise/run) × 100

<!-- Both units are in use and they are not interchangeable: 100 percent is 45 degrees, not 90. The worked example on the figure converts 3 percent to 1.72 degrees. Make the class do one conversion out loud. -->

---

# Slope in three dimensions

![bg right:48% w:94%](images/ta-slope-3d-surface.png)

- "Slope calculations in three dimensions require the consideration of **ALL** values surrounding a cell"
- On a real surface, the steepest direction at a point is rarely aligned with a row or a column

<!-- The arrows on the figure are the direction of steepest descent at each location. Slope has a magnitude and a direction; the magnitude is the slope raster, the direction is the aspect raster. -->

---

# Slope on a grid

![bg right:38% w:88%](images/ta-slope-center-cell.png)

- When computing slope on a grid, we have a problem: the slope direction is seldom exactly between the centers of two cells
- So we need methods that look at **several** surrounding cells

<!-- This is why there is more than one slope algorithm. Each one is a different weighting of the eight neighbors, and they give different answers on the same DEM. -->

<!-- TODO(instructor): tie slope to scale and uncertainty here — slope computed on a 10 m grid and slope computed on a 30 m grid over the same hillside are different numbers, and neither is wrong. Decide how to frame the dependence on cell size and on DEM vertical error. -->

---

<!-- _class: quiz -->

# How would you do it?

![bg right:40% w:70%](images/ta-slope-center-cell.png)

- **What is the slope at the center cell?**
- The cell size is 10 m; the nine elevations are on the figure
- Work in pairs. Write down the method you used, not just the number

<!-- Take two or three methods from the room before showing the next slides. Common answers: steepest neighbor, average of the four cardinal neighbors, fit a plane through all nine. All three are real algorithms. -->

---

# Slope: four nearest cells

![w:730 center](images/ta-slope-four-nearest-cells.png)

<p style="font-size:20px; background:#fff6d6; border-left:6px solid #d9a400; padding:8px 14px; margin-top:12px;">
<strong>Typo in the original figure:</strong> <code>dZ/dy = (Z2 − Z1)/2C</code> should read <code>dZ/dy = (Z2 − Z7)/2C</code>. The kernel and the arithmetic, (45 − 48)/20, are both correct.
</p>

<!-- Only the four cardinal neighbors are used; the diagonals get weight zero. Two central differences give dZ/dx and dZ/dy, and the slope is the arctangent of the magnitude of that gradient: 25.3 degrees here. -->

---

<!-- _class: activity -->

# Slope: 3rd-order finite difference — try it

![h:475 center](images/ta-slope-third-order.png)

<!-- This is the method ArcGIS Pro's Slope tool uses. All eight neighbors contribute, with the cardinal ones weighted double. Same nine elevations as the previous slide, and the answer comes out 22.9 degrees instead of 25.3 — a 2.4 degree spread from the choice of algorithm alone. Have them reproduce both numbers before moving on. -->

<!-- TODO(instructor): the plan calls for a validation exercise here — students compute slope by hand and compare against the Slope tool's output for the same cell. Decide whether it belongs in this lecture, in the lab, or on the quiz, and what counts as agreement. -->

---

# Aspect

![bg right:30% w:85%](images/ta-aspect-azimuth.png)

- **Aspect** is the downhill direction of the steepest slope, reported as an **azimuth** clockwise from north

$$
\text{Aspect} = 180 - \arctan\!\left(\frac{dz/dy}{dz/dx}\right) + 90\left(\frac{dz/dx}{|dz/dx|}\right)
$$

- Same partial derivatives as slope; a different thing done with them

<!-- TODO(instructor): aspect has its own scale-and-uncertainty story — on gentle slopes the direction of steepest descent is almost arbitrary, so aspect is noisiest exactly where slope is smallest, and it changes with cell size. Decide whether to make that point here or alongside the slope slide. -->

<!-- Aspect is circular data: 359 degrees and 1 degree are two degrees apart, not 358. That breaks averaging, and it is why aspect is usually reclassified into compass sectors before it is used. Flat cells have no aspect at all and are coded separately. -->

---

# Plan and profile curvature

![bg right:52% w:96%](images/ta-curvature-formulas.png)

- **Profile curvature** — curvature *parallel* to the slope direction
- **Plan curvature** — curvature *perpendicular* to the slope direction
- Can you calculate curvature?
- Name some applications or uses for curvature

<!-- Curvature is the second derivative of the surface, fitted from the same 3 x 3 window. Profile curvature controls whether flow accelerates or decelerates downslope; plan curvature controls whether it converges into a hollow or spreads over a nose. Together they predict where water and sediment collect. -->

<!-- TODO(instructor): curvature is the most scale-sensitive of these surfaces — the second derivative amplifies DEM noise, so a 1 m lidar DEM and a 30 m DEM give qualitatively different curvature maps. Decide how to make that point, and whether to require smoothing before curvature in the lab. -->

---

<!-- _class: lead -->

# Part 3
## Viewsheds

<!-- Divider. Visibility is the last of the standard terrain surfaces and the one with the most direct engineering uses. -->

---

# What is a viewshed?

![h:420 center](images/ta-viewshed-sign.jpg)

<!-- Opening gag before the definition. Ask the room for a one-sentence definition first; the wrong answers are useful. -->

---

# Not this

![h:440 center](images/ta-viewshed-not-a-shed.jpg)

<!-- The second half of the joke: a viewshed is not a shed with a view. Then move straight to the real definition on the next slide. -->

---

# A viewshed is a rotating searchlight

![bg right:52% w:96%](images/ta-viewshed-searchlight.png)

- In other words: **what could you see in all directions from the given point?**
- Sweep a beam from the viewer, mark every cell the beam reaches, and skip everything in shadow
- The output is a raster: **seen** or **not seen**, cell by cell

<!-- The profile at the top of the figure is the whole algorithm in one dimension: from the viewer, a line of sight rises at some angle, and any cell below the running maximum angle is hidden. The 3D block is the same test run outward in every direction. -->

<!-- TODO(instructor): viewshed results depend on choices the tool makes you name — observer and target offsets, earth curvature and refraction correction, the analysis radius, and the DEM's cell size. Decide how to present that as an uncertainty story rather than a parameter list. -->

---

# How to use a viewshed

<div class="columns">
<div>

- Search and rescue
- Land development and conservation
- Park management
- Solar energy potential
- Other?

The battles of Saratoga:

</div>
<div>

![w:420 center](images/ta-saratoga-cannon.jpg)

![w:420 center](images/ta-saratoga-battlefield.jpg)

</div>
</div>

<!-- Saratoga is the worked example: the artillery positions on the bluff control the river road because of what they can see, not because of what they can reach. Collect a few more uses from the room — cell towers, wind turbines, billboards, scenic easements, sniper and security siting. -->

---

<!-- _class: activity -->

# Where this shows up in lab

- **Lab 4 — Cell Phone Tower Placement** puts today's material to work: a DEM in, a viewshed out, and a siting decision that has to be defended
- What this lecture gives you for it: what a DEM cell size means, how a derived surface is computed from a 3 × 3 window, and what a viewshed does and does not tell you
- Bring a candidate site and a reason for it

<!-- Preview slide. Point at the lab page and let them read the deliverables before they start. In ArcGIS Pro the relevant tools are Slope, Aspect, Hillshade, Contour and Viewshed, all in the Spatial Analyst toolbox. -->

<!-- TODO(graphic): a supporting figure for this slide — ideally a Pro screenshot of the Viewshed tool run over a candidate tower site — was not available for this pass. -->

---

# Before Next Class

- **Reading:** <!-- TODO(instructor): reading chapter --> assigned chapter on terrain and surface analysis
- **Open-book quiz** on Learning Suite
- **Lab 3** is due this week — see the [Lab 3 page](https://byu-hydroinformatics.github.io/ce414-gis-applications/assignments/lab-03/)
- **Lab 4 — Cell Phone Tower Placement** starts next week — see the [Lab 4 page](https://byu-hydroinformatics.github.io/ce414-gis-applications/assignments/lab-04/)
- Questions? Office hours: [calendly.com/dan-ames/office-hours](https://calendly.com/dan-ames/office-hours)

<!-- Confirm the quiz due date and the reading before class. -->

<!-- VERIFY: schedule reconstructed from filenames — Lab 3 shown as due in Week 5 and Lab 4 starting in Week 6. Confirm against the semester schedule. -->
<!-- TODO(graphic): no graphic on this slide; a small course-schedule or lab-thumbnail figure would carry it. -->

<!-- Conversion notes (2026-09-03): CROP (2026-09-03): the five browser captures (National Map, SRTM/GISGeography, Earthdata, JAXA ALOS, Mars DEMs) had the Chrome tab strip and address bar removed because they showed the capturing user's other open tabs and profile avatar; page content unchanged. source "CE 414 Week 5 - Terrain Analysis.pptx", 28 slides, no hidden slides and no speaker notes in the source — every note in this deck is new. 28 source slides became 35: added a title byline slide, Today's Goals, three section dividers, a Lab 4 preview, and Before Next Class; source slide 22 was split into two slides (four nearest cells / 3rd-order finite difference) because its figure is unreadable at 16:9 on one slide. No slides were dropped. The duplicated sentence on the ASTER slide was removed. Source media1 (a stock tomato photo, unused by any slide) was not carried over. Slides 2, 3, 11 and 26 were built from PowerPoint shapes and are 200 dpi renders of the PDF page, cropped. Stale non-ArcGIS screenshots kept and flagged: The National Map, the SRTM page (a third-party page with an advertisement in the capture), Earthdata Search, and the JAXA portal. There are no ArcMap-era ArcGIS captures in this deck and no ArcGIS UI at all — ArcGIS Pro tool names appear only in speaker notes and carry a VERIFY. Open items: DEM resolution and dataset claims (four VERIFY flags plus a 3DEP terminology TODO; ten VERIFY flags in the deck overall), native-vs-resampled resolution, scale/uncertainty for hillshade, slope, curvature and viewshed, a hand-versus-tool validation exercise, the susceptibility/hazard/risk/exposure distinction, the reading chapter, the Week 5/6 lab schedule, and three TODO(graphic) slides. -->
