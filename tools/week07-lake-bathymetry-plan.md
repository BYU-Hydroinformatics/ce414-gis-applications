# Week 7 — Lake Bathymetry: plan for the slides, Lab 6 and the quizzes

First cut, October 1, 2026. Nothing here is built yet. The Week 7 schedule page now says "Lake
Bathymetry" and that the slides are being prepared; `docs/assignments/lab-06/README.md` is still the
September 8 placeholder (written around a reservoir with a dam) and carries its WARNING box.

The thread from Week 6: Thursday's deck ends on the nested hydrologic units from Rock Canyon up to the
**Great Salt Lake subregion (HUC4 1602)** and a "Next Week — Where Rock Canyon's Water Ends Up" slide.
Week 7 picks that up: a terminal lake, whose **water level is its water balance**.

## 1. What already exists (found October 1)

| Item | Where | State |
| --- | --- | --- |
| Lab 6 placeholder page and report template | `docs/assignments/lab-06/` | Question, tools, step titles, deliverables and rubric settled; lake, data, check values, figures all TODO. Written for a dammed reservoir ("region connected to the dam", "Bureau of Reclamation elevation record") — needs rewriting for GSL |
| **A Lab 6 draft for GSL**, "Mapping Lake Shorelines from a Topobathymetric DEM", dated 2026-07-30, with real Step 11 validation numbers | Your teaching folder (per `lake-notes/gsl.md` in hydromap-app) — **not on this Windows machine** | **Please send it.** It probably saves most of §3 |
| hydromap-app (https://github.com/danames/hydromap-app, HEAD `70c0d84`) | GitHub | Has the *baked outputs* for GSL (45 shoreline polygons, 4,170–4,214 ft NGVD29, 1 ft step; a causeway cross-section) and the band-baking spec, but **not the DEM and not the GSL processing script** (only Lake Mead's survives, `scratch/lakemead/build_extent_bands.py`) |
| Learning Suite | Week 7 Tuesday activities "Practicing Hydrology Tools" and "Where is my watershed?"; Lab 6 due date | The activities belong to the old Week 7 and need replacing; ROADMAP item 4 says the Lab 6 due date reads Oct 10 and should be Oct 17 |

## 2. Data

**Recommended source: USGS topobathymetric DEM and its elevation–area–volume tables.**
Root, J.C., 2023, *Half-meter topobathymetric elevation model and elevation-area-volume tables for
Great Salt Lake, Utah, 2002-2016*: U.S. Geological Survey data release,
https://doi.org/10.5066/P9DGG75W (ScienceBase item 64595c00d34ec179a8368788).

- The DEM is 0.5 m, NAD83 UTM 12N, **about 34 GB** (plus a 9.8 GB `.ovr`), one file, no range requests.
  Bathymetry from Baskin's contour surveys (south arm 2002–04, north arm 2006) interpolated with Topo to
  Raster **in ArcGIS Pro**, mosaicked with UGRC 2016 lidar. The metadata says NAVD88 meters in one field
  and feet in another; the hydromap docs say the raster is actually feet. **Verify before building.**
- The EAV tables (5 CSVs: total, north arm, south arm, Farmington Bay, Bear River Bay) run 4,170.00–
  4,215.00 ft NAVD88 in 0.01 ft steps, with `elev_ft_NGVD29`, area and volume columns. NGVD29 =
  NAVD88 − 3.48 ft, constant (checked across the table). These are the lab's **answer key**: an area
  at any level, computed by USGS from the same DEM (Storage Capacity tool on a 5 m resample; they report
  agreement with 0.5 m within 0.003 %). hydromap's baked shorelines match the total table to 0.04 %
  (median), 4,171–4,211 ft.
- Alternative: Tarboton & Merck, *Great Salt Lake Bathymetry*, HydroShare
  (https://www.hydroshare.org/resource/582060f00f6b443bb26e896426d9f62a/), `GSLDEM.tif` about 509 MB,
  CC BY 4.0, NGVD29. Much easier to get, but a different, older product that the USGS EAV tables were
  not computed from. **Do not mix the two.**

**Student extract.** Resample the USGS DEM once (outside class) to **30 m**, clip to the lake plus a
margin, convert to **feet NGVD29** so the levels match the gage record and the numbers students see in
the news, and ship it as `docs/data/lab06-gsl-surface.zip` (target under 30 MB) with a READ-ME-FIRST,
built by a `tools/lab06/` script — the Lab 5 pattern. At 30 m the lake is roughly 4,000 × 3,500 cells.
**Question for you:** do you already have the 34 GB TBDEM on the Mac (hydromap was baked from it)? If
so, the extract can be built there, or the file copied once; otherwise budget the download.

**Levels to use** (all ft NGVD29; sources as recorded in hydromap-app, re-verify before publishing):

- Record low about **4,188.5 ft, November 2022** (`gsl.json`; the EAV table gives 894 sq mi and
  7.08 million acre-ft there)
- "Healthy" range **4,198–4,205 ft**, from Utah FFSL's 2013 Great Salt Lake Comprehensive Management
  Plan elevation matrix
- The EAV table stops at 4,211.52 ft NGVD29; above about 4,211 the lake spills onto the playa and is
  unvalidated. Default range for the lab: **4,190 to 4,210 ft by 2 ft** (11 runs of the loop)
- Current level: read it live from USGS gage 10010000 (south arm, Saltair) the week of the lab

## 3. Lab 6 — Lake Depth Explorer (first-cut design)

**Question.** If the Great Salt Lake's water surface stands at a given elevation, where is the
shoreline, how big is the lake, and which places along it are wet or dry? Build one model that answers
that for a whole list of elevations at once.

**Model** (one loop; every tool except the iterator is one students have already used):

1. **For** iterator (ModelBuilder ▸ Iterators ▸ For): from, to, by → `%Value%`
2. **Raster Calculator**: `Con("%GSL_Surface%" <= %Value%, 1)` — 1 where the surface is below the water
   level, NoData elsewhere (the Lab 5 lesson about the third argument carries over)
3. **Raster to Polygon** (multipart on) → `Lake_%Value%`
4. **Add Field / Calculate Field**: `Level_ft = %Value%`, and the area in km² and mi²
5. **Collect Values** → **Merge** into one feature class `Shorelines`, one polygon per level

Counting every cell below the level is what the USGS EAV table does, so the student's area at each
level has a published check value (tolerance to set from the 30 m build; expect well under 1 %). The
placeholder's "keep the main pool" step (Region Group, seeded) becomes an **extension question**, not a
core step: at low levels Farmington and Bear River bays disconnect, and the arms behave differently
across the railroad causeway.

**Steps** (keeping the placeholder's titles where they fit): 0 Set Up the Project · 1 Read the Surface
(metadata, datum, the 3.48 ft offset) · 2 Add the Loop · 3 Flood the Surface · 4 Draw the Shoreline ·
5 Collect and Merge · 6 Check Against the USGS Table · 7 Shore Features (at what level does each go dry:
e.g. the Great Salt Lake Marina at Saltair, Bridger Bay on Antelope Island, the Spiral Jetty — their
elevations to be **measured from the DEM**, not asserted) · 8 Test the Range and Step (the sensitivity
step, Lab 3–5 pattern: change the step from 2 ft to 0.5 ft and the range; what does the step hide?).

**Deliverables** stay as the placeholder sets them (two maps — nested shorelines, and one level of
your choice — a 2–3 page report, the model export and the tool dialog, the metadata values, the
shore-feature table, the range-and-step table, the self-assessed rubric). Add one table: the student's
area at each level beside the USGS EAV area, with the percent difference.

**To verify in ArcGIS Pro 3.7 before writing the steps as fact:** the For iterator's parameters and
where it sits on the ribbon; `%Value%` inline in a Raster Calculator expression *and* in an output
name; Collect Values feeding Merge; run time for 11 iterations on a 30 m GSL surface on a lab machine.
Then the usual: arcpy verification run (`tools/lab06/run_model.py`), GUI build and captures, no-GUI
pilot, then promote.

## 4. Week 7 slides — two decks, five-question quiz each

**Tuesday — "Lake Bathymetry"** (`slides/week-07/lake-bathymetry.md`)

1. Where Rock Canyon's water ends up: the HUC4 map from Week 6, the Great Salt Lake as a terminal lake
2. What bathymetry is, and how it is measured: lead line, single- and multibeam sonar, airborne lidar
   (topobathymetric), satellite-derived — each with its depth limit and resolution
3. The GSL surface itself: how the USGS 2023 model was built (contours + lidar, Topo to Raster in
   ArcGIS Pro) — a nice "a real agency did this in the software you use" moment
4. Datums: NGVD29 vs NAVD88, the 3.48 ft offset, and why a level without a datum is not a number
5. Elevation–area–volume curves (hypsometry): read the USGS EAV table; what the shape of the curve says
   about a shallow, flat-bottomed lake. The table's own rows (as quoted in hydromap's `gsl.json`) give about 35 sq mi of lake per foot of level near 4,190 ft but about 85 sq mi per foot near 4,200 ft — re-derive from the CSV before putting numbers on a slide
6. The 2022 record low on the curve: area and volume at 4,188.5 vs the healthy range
7. Activity (Excel, replaces "Practicing Hydrology Tools"): plot area and volume against elevation from
   the EAV CSV; how much lakebed is exposed between 4,200 and 4,188.5 ft?
8. Close: QR quiz (5)

**Thursday — "Looping in ModelBuilder: Lake Depth Explorer"** (`slides/week-07/lake-depth-explorer.md`)

1. Running a model once per level vs once for all levels: what an iterator is
2. The For iterator, `%Value%` substitution in expressions and output names, and why iterators only
   work in ModelBuilder (and run the whole model once per value)
3. Collect Values and Merge: getting one dataset back out of a loop
4. Live demo on the 30 m surface: three levels, then eleven
5. Lab 6 walkthrough: the question, the data package, the check against the USGS table, the shore
   features, the range-and-step test, the report template
6. Activity (replaces "Where is my watershed?"): run the model for three levels, map them nested
7. Close: QR quiz (5)

**Graphics:** all maps rendered in ArcGIS Pro from the student extract (the Week 6
`tools/week06_figures.py` pattern): nested shorelines at 4,190/4,200/4,210; the EAV curve as an SVG
from the USGS CSV; the causeway cross-section from hydromap's `gsl-causeway.json` (note it comes from
the HydroShare DEM, not the USGS one — label it so); bathymetry-method sketches generated only where no
real figure exists.

## 5. Quiz plan (five each, high-level)

Tuesday (slug `bathymetry`): what bathymetry measures; why a terminal lake's level is its water
balance; why a level needs a datum (NGVD29 vs NAVD88); what an EAV curve's shape tells you about a
shallow lake; why a 1 ft drop exposes different areas at different levels.

Thursday (slug `iterators`): what an iterator does that running the tool twice does not; what
`%Value%` means; why each iteration needs its own output name; what Collect Values is for; why the
step size can hide a threshold you care about.

## 6. Open decisions for you

1. **Send the 2026-07-30 Lab 6 draft**, and say whether you have the 34 GB TBDEM locally.
2. Datum and units for students: feet NGVD29 (matches gages and news) — recommended — or NAVD88.
3. Whole lake only (matches the EAV total table), or also the south arm on its own (USGS publishes it)?
4. Main-pool connectivity: extension question (recommended) or a core step?
5. Learning Suite: replace the two Week 7 Tuesday activities; fix the Lab 6 due date (Oct 17).
6. Lab 6 is introduced Thursday and due Saturday of the same week — keep, or due the following week?
