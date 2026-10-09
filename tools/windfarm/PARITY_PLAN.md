# Lab 10 (Wind Farm Site Selection) — parity plan

Written October 8, 2026, to bring Lab 10 to the standard of Labs 1–9 (`tools/lab-conversion-guide.md`).
The overall plan for Labs 9–11 is `tools/labs-09-11-plan.md`; the instructor accepted every
recommendation in it on October 6, 2026, including the Lab 10 design in its section 5 and the
integrity measures in its section 8. The live page `docs/assignments/lab-10/README.md` is untouched;
the rebuild will be `docs/assignments/lab-10/draft.md` (search-excluded, not linked). **Nothing below
the decisions list gets built until the instructor answers it.**

**Calendar.** Lab 10 is introduced **Tuesday, November 3 (Week 10)** and due **Saturday, November 14**.
Target: promoted, GUI-built and templated by **Tuesday, October 27**.

**Source.** `Lab 9 - Wind Farm Site Selection.docx` (Word-era numbering), migrated September 3, 2026;
the live page matches it step for step and uses all 28 of its figures. Created by three students as a
Fall 2021 CE 414 final project (credit kept).

**What the current page is.** A faithful, unverified migration: 537 lines, 20 TODO/VERIFY comments, 28
captures from an unidentified ArcGIS Pro version, a 2021 student example map, and a rubric of
10 + 10 + 15 + 15. Its model is five Select/Intersect → Buffer → Polygon to Raster → Reclassify (0/1)
chains, a Weighted Sum with raw weights 7/6/4/3/2, and Get Raster Properties → Equal To → Raster to
Point for the single best cell. It asks for the analysis twice ("then for a collection of counties
you select").

## Gap table

| Element (Labs 4–9) | Lab 10 now | Plan |
| --- | --- | --- |
| One study area | Six southeastern counties, then "western South Dakota" in the next section, then "counties you select" | The six counties only: Minnehaha, Moody, Lake, McCook, Turner, Lincoln (9,535.5 km², measured) |
| Hosted data, READ-ME, metadata questions | Five gis.sd.gov searches, an NHD "data downloader", a wind source that is a JPG to georeference and digitize | `docs/data/lab10-southeast-sd.zip` (estimated under 10 MB) with every layer the model needs; Figure A metadata card for the turbine database |
| A live source varied deliberately | None | Step 1 opens the live USGS wind turbine database (download or viewer) and compares it with the frozen extract |
| Coordinate system and raster environments | None stated; "Cell Size 1" with no units; snap, extent and mask never set | NAD 1983 UTM Zone 14N (WKID 26914), 100 m cells, snap raster = the hosted wind raster, extent = study area, **mask left empty for the distance tools** (measured trap, below) |
| Check values in every step | None | Measured below: cell counts, distance maxima, cells excluded per criterion, open area, top score and its location |
| One model, parameters exposed | 25 tools in five parallel chains; nothing exposed | About 16 tools: Select ×2, Distance Accumulation ×4, Raster Calculator (mask), Rescale by Function ×3, Weighted Sum, Set Null, Zonal Statistics + Equal To + Raster to Point. Parameters: three exclusion values and the weight table |
| Exclusions vs preferences | All five criteria flattened to 0/1 and weighted, so an excluded cell can still score high | Exclusions → one 0/1 mask applied once; preferences → common 1–10 scores combined with weights summing to 1 |
| Sensitivity step with table and three questions | None ("do it again for other counties") | Step 10: course weights, own weights, wind-first, infrastructure-first, the AI's weights, 10-mile spacing, and a personal weight run |
| "Where the method breaks" | "Do you agree with the results of the model?" | The top site as measured is 54 m from a town boundary (below); students must find and explain what the score does not measure |
| Defaults traps as WARNING boxes | None | Five measured or known (below) |
| Rubric five parts of ten | 10 + 10 + 15 + 15, "two maps" for two county sets, no row for the raster work | Five parts of ten; sensitivity row carries the AI-weights bullet |
| Deliverables list, peer review, `.atbx` | None | As Lab 9: two maps, report list matching the rubric item for item, peer-review box, toolbox upload |
| Icons, Figure C, example maps | None | Icons for Distance Accumulation, Rescale by Function, Weighted Sum; Figure C SVG; two `arcpy.mp` layouts |
| Report template | None | `LABS['10']` in `tools/templates/make_lab_report_template.js` |
| GUI build and captures | 28 Word-era captures with stale labels (Cities 20mi, Roads 2km, Rivers 2mi), one with a student's path | All replaced by a GUI build at 175 % |
| Individual work | "one student team's judgment" | Individual |
| Extra credit for skipping the steps | Promised in Complete the Lab | Removed (guide section 2) |

## Decisions for the instructor (short)

Already accepted on October 6 and not reopened: six counties with "western SD" deleted; exclusion
mask + normalized weighted preferences; Weighted Sum in ModelBuilder (Suitability Modeler mentioned
in the deck); river exclusion 1 mile; personal parameters, `.atbx`, spot-check vivas, the AI-weights
bullet. What is still open:

1. **Distance tool: Distance Accumulation**, not Euclidean Distance. *Recommend: yes.* The Euclidean
   Distance reference page now says it "is deprecated and will be removed in a future release" and
   names Distance Accumulation as the replacement. Both give identical distances here (measured).
   Same tool Lab 11 will use, so students meet it once before the cost version.
2. **Wind data: Global Wind Atlas mean wind speed at 100 m**, clipped and hosted. *Recommend: yes.*
   It is the only numeric raster found that needs no login or API key (CC BY 4.0, DTU with the World
   Bank). NREL is now the National Laboratory of the Rockies: `nrel.gov` no longer resolves, so the
   page's `wrdb.nrel.gov` link is dead; `wrdb.nlr.gov` loads but is a JavaScript app (download path
   VERIFY in a browser). 100 m rather than 80 m because South Dakota turbines built since 2015 have
   hub heights of 80–110 m, median 89 m (USWTDB, 1,004 turbines). The DOE's 2025 South Dakota 100 m
   map (JPG) is linked for comparison, not digitized.
3. **Wind threshold.** At 100 m, 7 m/s excludes **0.2 %** of the area (1,990 of 953,568 cells); the
   study area runs 6.57–8.94 m/s, mean 7.97. *Recommend: keep 7 m/s as the default* and let the
   sensitivity TIP say "one exclusion does almost nothing at its default" (the guide's pattern);
   7.5 m/s would exclude 8.3 % and 8.0 m/s 50.6 %. Alternative: default 7.5.
4. **Town and road criteria become preferences only.** "Within 30 miles of a town" excludes **0 %**
   (no cell is more than 13.8 miles from an incorporated South Dakota place); "within 2 miles of a
   main road" would exclude **38.9 %**. *Recommend: both are 1–10 scores (closer is better), no
   exclusion.* Town = incorporated places (TIGER `CLASSFP = 'C5'`); road = TIGER primary and
   secondary roads (`MTFCC` S1100, S1200), which is what "main road" means — the page's "Local
   Roads" layer contradicts its own criterion.
5. **"River" = a named NHD stream/river whose name contains "River"**: `ftype = 460 AND gnis_name
   LIKE '%River%'`, eight rivers (Big Sioux, James, Vermillion and its East, West and Little forks,
   Rock, East Branch Rock). *Recommend: yes.* 1 mile excludes 8.3 %; every *named* stream at 1 mile
   would exclude 43.5 %.
6. **No town setback.** The course run's best cell is **54 m from Humboldt's boundary**, because the
   town score rewards closeness and nothing penalizes it. *Recommend: leave it in* as the built-in
   "where the method breaks" discovery, and ask for a setback distance in the report. Alternative: add
   a fourth exclusion (for example 1 mile from incorporated places) to the mask.
7. **Personal parameter: a personal weight run.** Run 7 uses *wind weight = 0.30 + (last two digits
   of the nine-digit BYU ID) ÷ 200* (0.300–0.795), with town and road splitting the rest equally.
   *Recommend: this* over a personal turbine spacing (10 + digits ÷ 10 miles). Both give a different
   graded area for every ID; only the weight version ever moves the site (it moves between digits 66
   and 77), so it also teaches the lesson. Grading lookup for all 100 values precomputed by
   `run_model.py --personal`.
8. **Best site = one cell, or a block?** The one-cell maximum is 1 ha, not a wind farm. *Recommend:
   keep the single cell* (Zonal Statistics MAXIMUM → Equal To → Raster to Point, which avoids wiring
   Get Raster Properties' string output into Equal To) and ask in question 3 what a minimum farm
   area would change. Alternative: Focal Statistics (mean over a 2 km circle) before the maximum.
9. **Neighbor-state towns and roads.** Turbines come from every state (all 888 within 20 miles are in
   Minnesota or South Dakota; none inside the six counties), but the probe used South Dakota places
   and roads only. *Recommend: include Minnesota and Iowa TIGER places and roads within 20 miles* so
   distances near the border are right (effect not yet measured).

## Data sources (checked October 8, 2026; curl with a browser user agent)

| Layer | Source | Status | Use |
| --- | --- | --- | --- |
| Counties | Census TIGER/Line 2025 counties, `www2.census.gov/geo/tiger/TIGER2025/COUNTY/tl_2025_us_county.zip` | 200, 84.0 MB (national) | Hosted extract; fields `STATEFP`, `NAME`, `NAMELSAD` verified; the six `NAME` values are exactly Minnehaha, Moody, Lake, McCook, Turner, Lincoln (`STATEFP = '46'`) |
| Towns | TIGER/Line 2025 places, South Dakota `tl_2025_46_place.zip` | 200, 0.8 MB | 485 places: `CLASSFP` C5 = incorporated (LSAD 25 city 157, 43 town 152, 47 village 1), U1/U2 = census-designated (175). 45 incorporated places in the counties, 85 within 20 mi |
| Roads | TIGER/Line 2025 primary and secondary roads, `tl_2025_46_prisecroads.zip` | 200, 3.2 MB | `MTFCC` S1100 (92) and S1200 (2,016) statewide; fields `LINEARID`, `FULLNAME`, `RTTYP`, `MTFCC` |
| Rivers | USGS NHD High Resolution HU4 1016 (James) and 1017 (Big Sioux, Vermillion) file geodatabases on `prd-tnm.s3.amazonaws.com` | 200, 58.7 MB and 43.6 MB | Field names are **lowercase** (`ftype`, `gnis_name`); `NHDFlowline` is in a network, so **Project fails with ERROR 001489** — use Export Features with the output coordinate system set. State GDB (368 MB) and state shapefile (790 MB) also 200, too big |
| Existing turbines | USGS/ACP/LBNL U.S. Wind Turbine Database: `energy.usgs.gov/uswtdb/data/`, `eerscmap.usgs.gov/uswtdb/assets/data/uswtdbSHP.zip`, viewer, REST API `energy.usgs.gov/api/uswtdb/v1/turbines` | All 200; SHP zip 3.9 MB, CSV 1.7 MB, GeoJSON 1.4 MB; DOI 10.5066/F7TX3DN0 resolves | 77,379 turbines (SD 1,503, MN 2,726, IA 6,515). **Metadata catch:** the data page cites **V9.1 (September 28, 2026)**, but the zip downloaded today holds `uswtdb_V9_0_20260626.shp`. Updated quarterly, so the model uses a frozen hosted extract and Step 1 compares it with the live release |
| Wind speed | Global Wind Atlas, `globalwindatlas.info/api/gis/country/USA/wind-speed/100` → `gwa.cdn.nazkamapps.com/country_tifs_v4/USA_wind-speed_100m.tif` | 200, 751 MB (Last-Modified June 12, 2025) | 0.0025° WGS 1984 cells; clip hosted. License CC BY 4.0 (search result; the site's terms page is a JavaScript app, VERIFY in a browser). Version: the path says `v4`, the attribution text found says 3.0 — VERIFY |
| Wind (NREL/NLR) | `wrdb.nrel.gov` (on the page) | **Dead**: `nrel.gov` has no address | Replace; `wrdb.nlr.gov`, `maps.nlr.gov/wind-prospector`, `developer.nlr.gov/docs/wind/wind-toolkit/`, `data.nlr.gov` all 200 (WIND Toolkit needs an API key) |
| Wind map | DOE WINDExchange, `windexchange.energy.gov/maps-data/` → `energy.gov/cmei/systems/windexchange/maps-and-data`; South Dakota 100 m JPG (`/sites/default/files/2025-10/South_Dakota_Land-Based_Wind_Speed_at_100_Meters.jpg`) | 200; JPG 4.8 MB | Link only, as a comparison in the metadata step |
| SD state portal | `gis.sd.gov` → `opendata2017-09-18t192802468z-sdbit.opendata.arcgis.com` | 200 | Not needed; drop |
| The National Map | `nationalmap.gov` → usgs.gov page; `apps.nationalmap.gov/downloader/` | 200 | Keep the downloader link for NHD provenance |
| Not used | PAD-US (usgs.gov download page 200), NLCD (`mrlc.gov/data` 200), 3DEP image service (200) | — | Candidates for "what the score does not measure" (question 3), not for the model |

Side finding: `pro.arcgis.com/.../tool-reference/...` now answers **301 → `doc.esri.com/en/arcgis-pro/latest/...`**.
Links on Labs 1–9 still work through the redirect; new pages should use the `doc.esri.com` form.

## Measured (ArcGIS Pro 3.7.1 arcpy, October 8, 2026) — probe, not yet the oracle

`inventory.py` → `inventory.json`; `probe_model.py 100` → `probe_checks_100m.json`; `extent_trap.py` →
`extent_trap.json`. Data in `C:\Ames\Lab10\` (raw downloads, `src\`, `probe_100m.gdb`). UTM 14N, 100 m,
grid snapped to whole hundreds of meters, extent = study area.

- Study area: six counties dissolved, **9,535.5 km²** (3,681.7 mi²); **953,568 cells** at 100 m.
  Counties (km²): Minnehaha 2,107.9, Turner 1,599.4, Lincoln 1,496.4, McCook 1,493.5, Lake 1,489.3,
  Moody 1,349.0.
- Wind at 100 m (bilinear to 100 m): **6.569–8.944 m/s, mean 7.965**, no NoData. Cells below 7.0:
  1,990; below 7.5: 79,302; below 8.0: 482,969.
- Turbines: **none inside the six counties.** Within 10 / 20 / 30 miles of them: 339 / 888 / 1,515,
  nearly all on the Buffalo Ridge in Minnesota (Lake Benton, Prairie Rose, Stoneray, Rock Aetna…).
  The nearest is 447 m outside the boundary.
- Distance maxima inside the area: turbines 102.5 km, rivers 49.0 km, towns 22.1 km, roads 16.9 km.
- Excluded share of the area: wind < 7 m/s **0.2 %**; within 20 mi of a turbine **37.0 %** (10 mi:
  9.7 %); within 1 mi of a river **8.3 %** (2 mi: 16.5 %). Not used as exclusions: more than 30 mi
  from a town 0 %; more than 2 mi from a main road 38.9 %.
- Mask (wind ≥ 7, turbines > 20 mi, rivers > 1 mi): **552,371 cells open, 5,523.7 km²** (57.9 %).
  Variants (km² open): spacing 10 mi 7,834.8; 30 mi 2,479.9; rivers 2 mi 5,092.7; wind 7.5 5,184.1;
  wind 8.0 3,034.6.
- Scores (Rescale by Function, Linear, 1–10; town 0–30 mi and road 0–10 mi reversed 10→1 — the
  reversed scale worked in arcpy, VERIFY in the dialog): wind 1–10, town 1.93–10, road 2.84–10.
- Course weights wind 0.5 / town 0.25 / road 0.25: maximum **9.3143**, one cell at **656,450 E,
  4,834,550 N** (43.6475 N, 97.0601 W), western Minnehaha County, **54 m from Humboldt**; 3,208.5
  km² score ≥ 7.

### Sensitivity (for setting expectations; do NOT publish)

| Run | Weights (wind/town/road) | Max | km² ≥ 7 | Top site |
| --- | --- | --- | --- | --- |
| Course | 0.5 / 0.25 / 0.25 | 9.3143 | 3,208.5 | 656,450 E 4,834,550 N (Humboldt) |
| Wind-first | 0.7 / 0.15 / 0.15 | 9.1257 | 2,675.1 | 653,250 E 4,843,650 N, 7.1 km from Montrose — **moves 9.6 km** |
| Infrastructure-first | 0.2 / 0.4 / 0.4 | 9.6967 | 4,278.9 | Humboldt cell |
| Equal | ⅓ / ⅓ / ⅓ | 9.5267 | 3,983.2 | Humboldt cell |
| Course, spacing 10 mi | 0.5 / 0.25 / 0.25 | 9.3143 | 4,653.0 | Humboldt cell |

- Personal weight (0.30 + d/200, d = 0, 11, …, 99): area 4,083.3 → 2,434.1 km², changing at every
  step; the site moves from the Humboldt cell to the Montrose-area cell between d = 66 and 77.
- Personal spacing (10 + d/10 mi): area 4,653.0 → 3,228.6 km²; the site never moves.
- Lesson the TIP can hint at: the exclusions decide *how much* land is open; the weights decide
  *where* the best cell is, and only a strong tilt toward wind moves it.

### Traps found (each becomes a WARNING box)

1. **Mask environment + sources outside it.** With Mask = study area, Distance Accumulation and
   Euclidean Distance to the turbines (all outside the counties) returned all NoData in one run and
   `ERROR 160333: The table was not found` in another. With extent = study area and no mask, both
   give 447.2–91,609.0 m over all 953,568 cells. Set the mask only after the distances, or apply it
   with Set Null at the end.
2. **Clipping inputs to the counties first** (the current Step 2 Intersect) leaves zero turbines, so
   the 20-mile exclusion silently vanishes. Clip to a 20-mile buffer, or not at all.
3. **Extent environment on vector tools.** In the probe, with an Extent environment set (in UTM
   coordinates, inputs in geographic coordinates), Project and Copy Features wrote empty feature
   classes (0 features, no error). The cause is not pinned down (arcpy only); verify in the GUI
   whether a model-level Extent does the same to the Select steps.
4. **Raster Clip with an output coordinate system set** resampled the wind raster to two 163 km cells.
   The hosted wind raster comes already projected, so students never clip it.
5. **NHD `Project` → ERROR 001489** (network feature class); the hosted extract avoids it.

## Sensitivity design (Step 10, proposed)

Parameters exposed: minimum wind speed, turbine spacing (miles), river setback (miles), and the
Weighted Sum table. Runs from the tool dialog after Map 1 is made:

| Run | What changes |
| --- | --- |
| Baseline | Course weights 0.5 / 0.25 / 0.25, 7 m/s, 20 mi, 1 mi — the published check values |
| 1 | **Your own weights**, justified in the report before running (the Lab 1 "layer you create and defend") |
| 2 | Wind-first 0.7 / 0.15 / 0.15 |
| 3 | Infrastructure-first 0.2 / 0.4 / 0.4 |
| 4 | **The AI's weights**: before any run, the student asks an AI tool for a weight set and its justification for this site, pastes the prompt and answer, and runs it |
| 5 | Course weights, turbine spacing 10 mi |
| 6 | Personal weight from the BYU ID digits (decision 7) |

Record for each: weights and exclusion values, open area (km²), area scoring ≥ 7 (km²), maximum
score, and the top cell's coordinates and distance from the baseline site. Questions:
1. What moves the answer most — the exclusions or the weights — with your numbers?
2. Is the top site robust? Across how many runs does it stay put, and what did the AI's weights do
   to it? Where was the AI right, and what could only the data answer?
3. What does the score not measure? Use the top site's surroundings (the town next to it) and name
   the data that would fix it: setbacks, land ownership, transmission capacity, wildlife (PAD-US),
   land cover (NLCD), minimum farm area.

## Pilot plan

As Lab 9: after the draft, a fresh subagent in `C:\Ames\Pilot10\` reads the draft as a first-time
student, downloads the hosted zip from the built site, reproduces every published check value with
the ArcGIS Pro Python, runs the personal-weight oracle for two invented IDs, and writes
`PILOT_NOTES.md` (ranked findings and a stated/measured/match table). Specific things to try: the
model with and without the Mask environment; a reversed Rescale by Function; the Weighted Sum table
as a model parameter; the Zonal Statistics → Equal To wiring. Then the GUI build at 175 %
(`C:\Ames\Lab10GUI\Lab10.aprx`), which is where the dialog questions get settled.

## Still owed (in order)

1. Instructor answers to decisions 1–9.
2. `tools/lab10/run_model.py` (the oracle, with `--personal` for the 100-value lookup) and
   `step_checks.json`; `fetch_data.py` + `make_extract.py` for `docs/data/lab10-southeast-sd.zip` with
   `READ-ME-FIRST.txt` (provenance, USWTDB version, GWA credit line, processing). Include MN/IA towns
   and roads if decision 9 is accepted, and re-measure.
3. `docs/assignments/lab-10/draft.md` in the guide's anatomy: Background rewritten around the
   exclusion/preference distinction; Step 0 with environments and the 953,568-cell check; Step 1 the
   live turbine database; Steps 2–9 as in the gap table; Step 10 the sensitivity; Deliverables, rubric
   (five × ten, AI-weights bullet in Sensitivity), "Make it yours" and peer-review boxes, `.atbx`
   upload, BYU-ID box copied from Lab 9.
4. `make_svgs.py` (three icons, Figure A turbine-database metadata card, Figure B exclusions vs
   preferences diagram with measured percentages).
5. No-GUI pilot; fixes.
6. Promotion (old page to `lab10-backup/`), GUI build and captures, Figure C, snippets,
   `build_figures.py` example maps (baseline and wind-first), report template `LABS['10']`.
7. Week 10 deck: `slides/week-10/raster-spatial-analysis.md` is a single 14-slide deck with an open
   `TODO(instructor)` saying it stops at "combine the layers"; it needs exclusion vs preference,
   Distance Accumulation, Rescale by Function, weights summing to 1, and a Lab 10 preview figure.
8. Learning Suite due date (November 14) and template link.
