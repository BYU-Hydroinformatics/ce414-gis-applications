# Lab 7 (Flood Mapping with HAND) — feasibility and build plan

Written October 8–9, 2026. Lab 7 is new: it follows Lab 5 (Rock Canyon watersheds) and Lab 6 (Lake
Depth Explorer), so the water labs run watersheds → bathymetry → flooding. **Calendar (instructor,
October 9):** introduced Tuesday October 20 and **due Saturday October 24, Week 8** — the same week
as Midterm 1. It is therefore a **one-week lab with Lab 6's workload**: every prepared input is
hosted (including the stage table), and the hydrology is explanation in the page plus **one row the
student verifies**. Working data are in `C:\Ames\HAND\`.

## 0. Status after the instructor's decisions (October 9, 2026) — read this first

Sections 1–15 below are the feasibility record of October 8–9. The instructor then decided (section
14's eight questions): Provo River 10163000; **FEMA's published FIS flows** (10/25/50/100/500-yr:
1,475 / 1,810 / 2,065 / 2,325 / 2,935 ft³/s; the 500-yr is FEMA's 0.2 % column, read from the
page image) as the design table, with the LP3 fit kept only for a "why do two 100-year floods
differ?" question; **h = gage height − 3.20 ft, uncorrected** (the 0.47 m lidar-channel offset is a
"where it breaks" item); 5 m lidar; personal flow Q = 900 + 12 × last two digits of the nine-digit
BYU ID; sensitivity = stream threshold; buildings only; Iterate Field Values over the hosted table
(Lab 6's For as the fallback). **Where sections 2, 5–11 disagree with this section, this section
wins.**

**Built:** `docs/assignments/lab-07/README.md` (full page, Steps 0–7, rubric 5 × 10),
`docs/assignments/lab-07/images/` (four icons; Figure A metadata card; Figure B measured long
profile + FEMA section C; Figure 1 rating; Figure C a *drawn* model diagram — all from
`make_svgs.py`, data from `profile.py`), `docs/data/lab07-provo-river-hand.zip` (12,411,788 bytes,
`make_extract.py`), `docs/assignments/lab-07/lab07-report-template.docx`
(`LABS['07']` in `tools/templates/make_lab_report_template.js`).

**Student path, as measured** (`verify_package.py` from the zip alone → `package_checks.json`;
`probe_student_path.py` → `probe_student_path.json`):

- Two models: **HAND Builder** (Fill → Flow Direction D8 → Flow Accumulation → Raster Calculator
  `Con("%Flow_Accumulation%" > %Threshold%, 1)` → Buffer `Provo_River` 30 m → Extract by Mask →
  Flow Distance VERTICAL/D8/MINIMUM) and **Flood Loop** (Iterate Field Values on `Stage_Table.H_CM`
  → Raster Calculator `Con("%HAND%" <= %Value% / 100, 1)` → Raster to Polygon no-simplify multipart
  → Calculate Field H_CM → Collect Values → Merge). Two models because an iterator reruns every tool.
- Environments: Extent, Snap Raster, Cell Size = `Provo_DEM`. **Without Extent, HAND covers 695,974
  cells, not 697,608** (Flow Distance takes the stream raster's extent).
- A Con **where clause** `Value * 100 <= 153` fails (ERROR 010416), hence Raster Calculator with
  `%Value% / 100` (arcpy `Con(hand <= 153 / 100, 1)` = 62,693 cells). VERIFY in the GUI.
- `H_CM` = threshold in whole centimeters (gdb names cannot hold "1.53"): 119, 134, 143, 153, 173.

| Check | Value |
| --- | --- |
| DEM | 1,718 × 2,124 × 5 m, 1,366.78–1,645.53 m |
| Fill | 1,366.92–1,645.53; raised 489,125 cells (12.228 km²), max 8.47 m |
| Flow accumulation max; Stream_Cells; River_Cells | 1,050,227; 74,866; 3,191 |
| HAND | 697,608 cells, 0–197.95 m, mean 23.54 |
| Verify row (25-yr) | 1,810 → 7.58 ft (7.57 ft = 1,809.84) → 1,371.844 m, h 1.335 m, H_CM 134 |
| Floods (H_CM: cells, km², buildings) | 119: 51,474, 1.2869, 319 · 134: 56,420, 1.4105, 356 · 143: 59,332, 1.4833, 388 · 153: 62,693, 1.5673, 413 · 173: 68,538, 1.7135, 451 |
| FEMA, 100-yr | FEMA 1.3429 km², HAND in comparison area 1.2801, overlap 0.7361; hit 0.548, FAR 0.425, **CSI 0.390** |
| Threshold 400 / 1,000 / 4,000 / 8,000 | River_Cells 3,513 / 3,307 / 3,110 / 2,912; 100-yr km² 1.8591 / 1.7326 / 1.4389 / 0.9739; buildings 497 / 474 / 397 / 257; CSI 0.377 / 0.387 / 0.394 / 0.325 |
| Personal (`personal.py`, h to the mm) | 100 distinct h and areas, 74 distinct building counts; 89 → 1,968 ft³/s, 7.78 ft, 1.396 m, 1.4548 km², 376; 02 → 924, 6.24, 0.927, 1.0799 km², 258 |
| Traps | no corridor: 47.94 km² at h 1.53; raw DEM surface: 6,141 negative cells (min −1.92 m) |

Also measured for the page and decks (`profile.py` → `profile.json`): river long profile
1,476.98 → 1,367.05 m over 17.57 km; the 100-yr stage elevation (1,372.04 m) lies above only the
lowest 4.8 km; at FEMA section C HAND floods 95 m of 123 m and FEMA 105 m; the D8 path from the
highest river cell **leaves the river at 40.23923 N, 111.68941 W** and exits the box's south edge
(a lecture/"where it breaks" fact — the bare-earth DEM routes the river south through the city).

**Pilot (no-GUI, October 9):** `C:\Ames\Pilot07\PILOT_NOTES.md` — all ~40 check values reproduced from the zip; its text findings are fixed on the page (list in the page's migration notes), and the hosted geodatabase is now `ProvoData.gdb` (the project's own is `Lab07.gdb`).

**Still owed:** the GUI build at 175 % (`C:\Ames\Lab07GUI\`) with every `TODO(capture)` on the
page (Figures 0, 2, 3a, 3b, 4, 5a–5d, 6a, 6b, Figure C export) and the VERIFY items (Iterate Field
Values menu and output name; inline `%Value%` arithmetic in Raster Calculator; Flow Distance dialog
labels; Extract by Mask analysis extent; Jordanelle dates; a NOAA HAND/FIM link); example maps
(`build_figures.py`, arcpy.mp); lab-machine run time; the two Week 8 decks (section 12, with the
LP3/FEMA numbers updated to the FEMA design flows: 100-yr h = 1.527 m); Learning Suite due date;
nav/schedule entries belong to the renumbering work (`build_schedule.py`, not touched here).

**Lineage.** Three student final projects did this: 2021 (one stage, Logan, Flow Distance for HAND,
Con for depth, clipped by private property), 2024 (Utah County flood-prone dense areas), 2025
("Mapping Flood Intervals with HAND": gage → peak-flow statistics → rating curve → stage per return
period → HAND extent per return period → parcels at risk, in an iterating model). Their lessons are
built in: the stage table is **hosted** (it "requires a bit of prep work"), the hydrology is
**taught in the page** (the 2021 team's barrier), and the result is **validated** against FEMA (the
2025 author could not tell whether the maps were right).

## 1. Site: keep USGS 10163000 Provo River at Provo

**Recommendation: keep it.** Evaluated honestly:

| | Finding (measured or read, October 8–9) |
| --- | --- |
| Regulation | **Every one of the 90 annual peaks is coded 6** (regulated or diverted). Deer Creek (1941) and Jordanelle (1992–93) reservoirs upstream (VERIFY dates against Reclamation; the usbr.gov pages timed out). Peaks are small for 673 mi²: record 2,520 ft³/s (1952); post-Jordanelle maximum 1,990 ft³/s (2017). |
| Is that disqualifying? | No — it is a teaching point (Bulletin 17 assumes unregulated peaks; FEMA and the USGS still publish regulated-flow frequencies here). The flows are modest, so floods are shallow (1.5–2 m), which is exactly where a 5 m HAND map is informative. |
| Channel | Urban, partly confined. FEMA's 2026 model keeps the 1% flood mostly **in the channel above the gage** and spreads it **below** it (toward Utah Lake). HAND cannot see levees or bridges → a real "where the method is wrong" item. |
| Validation data | Exceptional: Utah County's **new FIRM (effective June 23, 2026)** includes a Provo River restudy (the FIS lists HEC-RAS 6.3 and AECOM analyses dated 2021 and 2023; VERIFY the row alignment in its Table 12) with **43 cross-sections** carrying the 1% water surface (`WSEL_REG`) and streambed (`STRMBED_EL`) in NAVD 88. |
| Published flows | FEMA FIS Table 9 gives Provo River flows (below); StreamStats/GageStats publishes **no** peak-flow statistics for this gage (only duration and mean-flow statistics, OFR 2017-1108). |
| Continuity | Same city as Lab 5's Rock Canyon; the same FIS maps Rock Canyon Creek down to its confluence with the Provo River. |

Alternatives checked through GageStats (preferred AEP flows): **Spanish Fork at Castilla 10150500**
(published 1% = 2,630 ft³/s, but the gage is at the canyon mouth, the town reach below it is
diverted, and FEMA's Spanish Fork study is older); **Weber near Oakley 10128500** (1% = 3,780, natural
snowmelt, but rural, few structures, outside Utah County); **Logan above State Dam 10109000** (no
peak statistics). None beats Provo's 2026 FEMA restudy as a validation set.

## 2. Hydrology (`stage_table.py` → `stage_table.csv`, `stage_table_meta.json`)

**Sources (all curl 200 on October 9):** NWIS peaks (`nwis/peak … format=rdb`), the current rating
(`get_ratings … file_type=exsa`), the NWIS site file (`waterservices … siteOutput=expanded`).

- **Gage datum 4,493.22 ft NAVD 88** (accuracy ±0.16 ft); gage at 40.23926 N, 111.71119 W.
- **Rating 30.0**, in force since April 26, 2023 (provisional): 459 rows, 3.42–**8.00 ft**,
  6.83–**2,150 ft³/s**; logarithmic expansion, **offset 3.20 ft** (≈ gage height of zero flow).
  Above 8.00 ft the top segment is extrapolated: Q = 120.85 (GH − 3.20)^1.835.
- **90 peaks**, WY 1903 and 1934–2024 (WY 2025 not yet in the file).
- **Flood frequency: no published USGS estimate exists for this gage**, so `stage_table.py` fits a
  **Log-Pearson III by method of moments with station skew** (Bulletin 17B-style teaching
  approximation; no EMA, no regional skew, no low-outlier test — *not* Bulletin 17C). Three periods:

| Period | n | skew | Q2 | Q5 | Q10 | Q25 | Q50 | Q100 (ft³/s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| All systematic, WY 1934 on | 89 | −0.37 | 859 | 1,381 | 1,734 | 2,179 | 2,506 | 2,827 |
| Post–Deer Creek, WY 1942 on | 83 | −0.38 | 874 | 1,394 | 1,743 | 2,179 | 2,498 | 2,809 |
| **Post-Jordanelle, WY 1993 on (design)** | **32** | **+0.03** | **842** | **1,346** | **1,722** | **2,244** | **2,665** | **3,111** |
| FEMA FIS 2026, Table 9 (published) | | | — | — | 1,475 | 1,810 | 2,065 | 2,325 (500-yr 2,935) |

FEMA values: *Flood Insurance Study, Utah County*, volume 49049CV001B (revised June 23, 2026),
Table 9, "Provo River, 3 miles above tie-in to Utah Lake", 673 mi² — read from the rendered page
image (PDF page 53), including a "1% future" column of 2,925.

- **Flow → stage → HAND threshold.** Gage height = the first rating row whose discharge ≥ Q (the rule
  a student can apply); elevation = datum + GH; **h = GH − 3.20 ft**, in meters. Design rows (hosted
  as `Stage_Table`):

| Return period | Q (ft³/s) | GH (ft) | Elev (m NAVD 88) | **h (m)** | Rating |
| --- | --- | --- | --- | --- | --- |
| 2 | 842 | 6.09 | 1,371.390 | 0.881 | table |
| 5 | 1,346 | 6.92 | 1,371.643 | 1.134 | table |
| 10 | 1,722 | 7.46 | 1,371.807 | 1.298 | table |
| 25 | 2,244 | 8.11 | 1,372.006 | 1.498 | extrapolated |
| 50 | 2,665 | 8.60 | 1,372.153 | 1.644 | extrapolated |
| 100 | 3,111 | 9.07 | 1,372.298 | 1.789 | extrapolated |

**The row students verify: the 10-year.** 1,722 ft³/s → first row ≥ is 7.46 ft (1,727.09 ft³/s) →
4,500.68 ft = 1,371.807 m → h = 4.26 ft = **1.298 m**. It is inside the rating, unlike the 25–100-yr rows.

### Checks on the convention (`xs_check.py` → `xs_check.json`)

- **FEMA's 1% depth above its streambed** at the 42 sections with a riverine WSEL: median **1.80 m**
  (1.49–2.07). Our 100-yr h is **1.789 m**. The convention "h = depth above zero flow" lands on FEMA's
  depth almost exactly.
- But the **DEM channel is not the bed**: the 3DEP lidar is hydro-flattened, so the lowest DEM cell
  at each section is the water surface on the flight day, median **0.47 m above FEMA's bed**
  (0.10–1.44). The HAND threshold that would reproduce FEMA's water surface relative to the DEM is
  median **1.28 m** (0.60–1.88).
- **Vertical mismatch at the gage (VERIFY):** FEMA's 1% WSEL interpolated to the gage is 1,372.94 m
  and its bed 1,371.12 m; the gage's zero-flow elevation is 1,370.51 m and our 100-yr stage 1,372.30 m.
  Both are about 0.6 m lower than FEMA's, so the *depths* agree but the *elevations* do not. Also, peak
  gage heights in WY 2013–2019 run ~2 ft higher than for the same flows before and after (2015: 709
  ft³/s at 8.33 ft; 2020: 702 ft³/s at 5.93 ft) — a gage move, datum change or control change.
  This is why the lab uses **depth (GH − 3.20 ft)**, which does not depend on the datum.

## 3. Terrain (`fetch_dem.py`)

- **3DEP elevation image service**, best-available lidar, exported at 2 m in NAD 1983 UTM 12N
  (EPSG 26912) over the box 111.750–111.650 W, 40.225–40.320 N → UTM 436,190–444,780 E,
  4,452,930–4,463,550 N (8.59 × 10.62 km), 30 tiles of 1,000 px (one 4,295 × 5,310 request gave
  HTTP 504). Elevations 1,366.76–1,645.65 m. Sources under the gage (service identify): Wasatch L3
  2013, Wasatch L5 2014, Great Salt Lake QL1 2016 (which one wins the mosaic: VERIFY).
- **USGS 1/3″ tile n41w112 (published May 20, 2026)**, the Lab 5 product, clipped and projected at
  10 m for the resolution test.
- **Student DEM (recommended): 5 m**, bilinear from the 2 m export: 1,718 × 2,124 cells, the whole
  arcpy chain in **16 s**. 2 m takes 93–108 s and makes a 50+ MB package; 10 m runs in 13 s and scores
  the same against FEMA (table in §6), so 5 m is chosen for map legibility (streets and banks show).

## 4. Tools, verified in arcpy (ArcGIS Pro 3.7.1, Advanced, Spatial Analyst)

**Flow Distance** — `FlowDistance(in_stream_raster, in_surface_raster, {in_flow_direction_raster},
{distance_type}, {flow_direction_type}, {statistics_type})`; `distance_type` VERTICAL (**default**) |
HORIZONTAL; `flow_direction_type` D8 (default) | MFD | DINF; `statistics_type` MINIMUM (default) |
WEIGHTED_MEAN | MAXIMUM. VERTICAL along D8 to the stream **is HAND**. Measured traps (`gotchas.py` →
`gotchas.json`, 5 m package):

| Case | HAND cells | 100-yr wet (km²) | Note |
| --- | --- | --- | --- |
| Reference (Fill, D8 FDR, NoData off-stream, corridor mask) | 697,608 | 1.751 | |
| Stream raster with **0** off-stream (inside the corridor) | 697,608 | 1.751 | 0 is treated as not-stream: no trap |
| **Raw DEM** as the surface | 697,608 | 1.724 | 6,141 **negative** cells, min −1.92 m |
| **No flow-direction raster** | 697,608 | 1.751 | the tool derives D8 itself; identical |
| **No corridor mask** (every Con stream is a drainage) | 3,370,573 | **51.96** | the big trap: every gutter becomes a river |

Newer Hydrology tools exist (`DeriveStreamAsRaster`, `DeriveStreamAsLine`, `DeriveContinuousFlow`:
no fill needed, depressions as input). Recommend **not** using them: the Lab 5 chain is the point of
reuse, and Flow Distance needs a flow-direction raster consistent with its surface.

**Fill matters here:** it raises 11.0 km² of the box (urban depressions, up to 8.47 m); on the 3,191
river cells, 45 are raised > 0.5 m (max 2.10 m) — places where a bridge or culvert fill dams the
bare-earth channel. HAND is measured from the filled surface.

## 5. Reference model and check values (`run_model.py`, `verify_package.py` → `package_checks.json`)

Model in words (two parts, one model):

1. *HAND:* `Provo_DEM` → **Fill** → **Flow Direction** (D8) → **Flow Accumulation** →
   **Con** (`acc > 2000`, i.e. 0.05 km² at 5 m; NoData elsewhere) → **Extract by Mask** (mask =
   **Buffer** of `Provo_River`, 30 m) → **Flow Distance** (VERTICAL) = `HAND`.
2. *Floods:* **Iterate Field Values** over `Stage_Table.H_CM` → **Con** (`HAND <= %Value% / 100`) →
   **Raster to Polygon** → **Calculate Field** (return period) → **Select Layer By Location**
   (`Buildings` INTERSECT) → **Collect Values** → **Merge** → one feature class of nested floods
   (Lab 6's pattern). *VERIFY in the GUI:* Iterate Field Values' output name (`Value`) and whether
   inline `%Value% / 100` works in Con's expression; fallback: iterate `H_M` and name outputs by `H_CM`
   through a second Get Field Value, or use the For iterator over h like Lab 6.

Check values **from the hosted zip alone** (`verify_package.py`, the canonical numbers):

- DEM 1,718 × 2,124 at 5 m, 1,366.78–1,645.53 m; Fill 1,366.92–1,645.53 m; max accumulation
  1,050,227 cells.
- River cells after the mask **3,191**; HAND on **697,608** cells, 0–197.95 m, mean 23.54 m
  (17.6 km of NHD river).

| Return period | h (m) | Wet cells | Area (km²) | Polygons | Buildings (intersect) | Hit rate | **CSI** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 0.881 | 41,794 | 1.044 | 81 | 244 | 0.458 | 0.383 |
| 5 | 1.134 | 49,296 | 1.233 | 78 | 299 | 0.501 | 0.398 |
| 10 | 1.298 | 55,018 | 1.377 | 91 | 341 | 0.526 | 0.399 |
| 25 | 1.498 | 61,722 | 1.544 | 97 | 395 | 0.548 | 0.394 |
| 50 | 1.644 | 66,106 | 1.654 | 71 | 434 | 0.565 | 0.391 |
| **100** | **1.789** | **70,050** | **1.754** | **71** | **454** | **0.578** | **0.386** |

Buildings: 11,122 footprints within 1 km of the river are hosted; "centroid inside" counts are lower
(390 at 100-yr). Raster CSI (`run_model.py`) and polygon CSI (Pairwise Intersect + areas) agree.

## 6. Validation against FEMA (the 100-yr row)

FEMA riverine 1% zones (A, AE incl. floodway, AH; not Utah Lake's coastal AE/VE) inside the
**comparison area** (500 m of the river minus the coastal zones): **1.343 km²** (AE 0.62, floodway
0.28, AH 0.31, A 0.06, riverine floodway in the coastal zone 0.08). HAND 100-yr inside it 1.444 km²;
overlap 0.776 km². **Hit rate 0.578, false-alarm ratio 0.462, CSI 0.386.**

- CSI is flat between h = 1.0 and 1.75 m (0.39–0.40), so the hydrology choice is *not* what limits
  agreement. With FEMA's own 1% flow (2,325 ft³/s → h 1.527 m) CSI is 0.394.
- **Where it differs:** north of 4,455,500 N (upper reach) FEMA keeps the flood almost in the channel
  (0.32 km²); HAND adds 0.33 km² of false alarm beside it (CSI 0.34). South of that line HAND misses
  0.47 km², mostly FEMA's **AH overflow zone** that leaves the river southward (a split flow HAND
  cannot represent), CSI 0.41.
- **Bathtub contrast** (2 m DEM, `bathtub.py`): one flat water surface at the 100-yr stage elevation
  (1,372.30 m) floods 15.4 km² of low ground by Utah Lake, 9.2 km² of it north of the gage, and
  never reaches the river upstream of the gage's neighborhood (northmost cell 4,459,398 N); HAND at the
  same stage follows the river to the top of the box (4,463,413 N) and floods 1.75 km².

## 7. Personal parameter (`personal.py` → `ce414-private/grading-oracles/lab07_personal_lookup.csv`; `package_checks.json['personal']`)

**Personal design flow Q = 900 + 12 × (last two digits of the nine-digit BYU ID) ft³/s**: 900 to
2,088 ft³/s (just above the 2-year to between the 10- and 25-year), always **inside the rating table**.
The student converts it exactly like the verified row (first rating row ≥ Q → GH → h), floods it
from the model's dialog, and says which return periods it falls between. Measured on the package:
**100 different h, 100 different areas, 62 different building counts**; e.g. 00 → 900 ft³/s, 6.19 ft,
h 0.911 m, 1.067 km²; 50 → 1,500, 7.15 ft, 1.204 m, 1.298 km²; 99 → 2,088, 7.93 ft, 1.442 m, 1.495 km².

## 8. Sensitivity (`sensitivity_5m_base.json`; 2 m base in `sensitivity_2m_base.json`)

Do not publish; for setting expectations. 100-yr row, buildings counted by centroid.

| Run (5 m unless noted) | River cells | 2-yr km² | 100-yr km² | Hit | FAR | CSI | Bldg |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Base: T 0.05 km², corridor 30 m** | 3,191 | 1.043 | 1.751 | 0.577 | 0.462 | 0.386 | 381 |
| T 0.01 km² | 3,513 | 1.239 | 2.070 | 0.616 | 0.517 | 0.371 | 448 |
| T 0.02 km² | 3,340 | 1.152 | 1.950 | 0.610 | 0.501 | 0.378 | 433 |
| T 0.1 km² | 3,110 | 0.954 | 1.615 | 0.575 | 0.452 | 0.390 | 373 |
| T 0.2 km² | 2,912 | 0.613 | 1.213 | 0.508 | 0.418 | 0.372 | 235 |
| T 0.5 km² | 2,640 | 0.560 | 1.101 | 0.480 | 0.392 | 0.366 | 226 |
| Corridor 15 m | 2,680 | 0.697 | 1.332 | 0.455 | 0.403 | 0.348 | 213 |
| Corridor 60 m | 3,936 | 1.552 | 2.474 | 0.669 | 0.584 | 0.345 | 584 |
| 2 m lidar | 8,447 | 1.034 | 1.744 | 0.610 | 0.453 | 0.405 | 306 |
| 3 m lidar | 5,572 | 1.028 | 1.756 | 0.608 | 0.442 | 0.411 | 293 |
| 10 m lidar | 1,547 | 0.755 | 1.642 | 0.596 | 0.421 | 0.416 | 274 |
| 10 m USGS 1/3″ | 1,540 | 0.964 | 1.887 | 0.618 | 0.463 | 0.403 | 286 |

**Recommended sensitivity step: the stream threshold** (T = 0.01, 0.2 km² plus one of the
student's choosing, i.e. 400 and 8,000 cells): it moves the 100-yr area by −31 % to +18 % while CSI
barely moves — the lesson is that the *map* changes more than its *agreement*. The threshold is
Lab 5's parameter, so it costs no new skill. The **corridor width** is as strong (15 m → 1.33 km², 60 m → 2.47 km²) and could replace it. DEM resolution is weak
(1.64–1.89 km², CSI 0.40–0.42) — a good lecture fact, a poor student experiment. On the 2 m DEM a
100 m corridor gave CSI 0.29 and T = 1 km² lost the upper river (CSI 0.27): both now WARNING boxes.

## 9. Data package (`make_extract.py` → `C:\Ames\HAND\pkg\lab07-provo-river-hand.zip`, **12.4 MB**)

To become `docs/data/lab07-provo-river-hand.zip` after approval (the maintainer copies it).

| Item | Size / count | Source |
| --- | --- | --- |
| `Provo_DEM.tif` | 10.9 MB, 1,718 × 2,124 × 5 m, float32 LZW | 3DEP lidar via image service |
| `Lab07.gdb` (3.3 MB): `Provo_River` | 1 line, 17.6 km | UGRC UtahStreamsNHD |
| `Gage` | 1 point | NWIS site file |
| `Buildings` | 11,122 within 1 km | UGRC Buildings (Microsoft footprints) |
| `FEMA_Floodplain_1pct` | 111 polygons, zones kept | NFHL layer 28, DFIRM 49049C |
| `Comparison_Area` | 1 polygon | 500 m buffer minus FEMA coastal zones |
| `FEMA_Cross_Sections` | 43 lines | NFHL layer 14 |
| `Stage_Table` | 6 rows (RETURN_YR, AEP_PCT, Q_CFS, GAGE_HT_FT, ELEV_M, H_M, H_CM) | `stage_table.py` |
| `rating_10163000.csv` | 459 rows | NWIS exsa rating 30.0 |
| `peaks_10163000.csv` | 90 peaks | NWIS |
| `READ-ME-FIRST.txt` | | draft text in `make_extract.py` |

**Live source for the metadata questions:** the FEMA NFHL map service (layer 28) added by URL —
draws fine, but its *query* with a spatial filter returned HTTP 400 on October 8, so the comparison
uses the hosted copy. Parcels (`Parcels_Utah_LIR`, 57,910 in the box, value and class fields, no
owner names) were fetched but are **not** recommended for a one-week lab.

## 10. Step outline (one week, Lab 6-sized)

- **Step 0 — Set Up the Project**: folder, `.aprx`, environments Snap Raster / Extent / Cell Size =
  `Provo_DEM`; check: 1,718 × 2,124 cells, 1,366.78–1,645.53 m.
- **Step 1 — Read the Gage**: metadata questions (gage datum, rating date and top, peak codes 6);
  verify the 10-year row by hand (h = 1.298 m).
- **Step 2 — Condition the Surface**: Fill, Flow Direction (Lab 5 reuse); check Fill max, the 11 km²
  raised.
- **Step 3 — Find the River**: Flow Accumulation, Con > 2000, Buffer 30 m, Extract by Mask; check 3,191 cells.
- **Step 4 — Height Above Drainage**: Flow Distance VERTICAL; check 697,608 cells, max 197.95 m.
- **Step 5 — Flood Every Return Period**: Iterate Field Values → Con → Raster to Polygon → Select
  Layer By Location → Collect Values → Merge; check the six areas and building counts above.
- **Step 6 — Check Against FEMA**: Pairwise Intersect with `FEMA_Floodplain_1pct`, Pairwise Clip to
  `Comparison_Area`, three areas, CSI 0.386; name the place where HAND is most wrong, with
  coordinates (the AH overflow south of the lower river, or a false-alarm block in the upper reach).
- **Step 7 — Test the Threshold** (sensitivity + personal flow): the personal design-flow run and two
  threshold runs from the model dialog, one table, three questions.

Model diagram, in words: *DEM → Fill → Flow Direction → Flow Accumulation → Con → Extract by Mask
(Buffer of Provo_River) → Flow Distance → [iterator: Stage_Table H_CM] → Con → Raster to Polygon →
Calculate Field → Select Layer By Location (Buildings) → Collect Values → Merge.* Parameters: DEM,
threshold, corridor width, stage table, output floods.

## 11. Deliverables and rubric sketch (five rows of ten)

| Row | Items |
| --- | --- |
| Write-up | title block, peer reviewer (1); requirements and approach (2); the verified 10-yr row and the personal-flow row shown step by step (2); FEMA comparison with hit rate and CSI and where HAND is wrong, with coordinates (2); metadata values and regulation caveat (1); organization, figures, rubric pasted (2) |
| Model | runs end to end and matches the check values (4); full-page model figure (2); dialog with parameters (2); description (2) |
| Map 1 — floods by return period | nested 2–100-yr extents with a legend, buildings at risk, FEMA outline (the Lab 6/Lab 5 map items) |
| Map 2 — your design flow | same, plus what changed and why (2) |
| Sensitivity | the table (4); three questions (2 each) |

`.atbx` with the submission; spot-check vivas (plan section 8).

## 12. What Week 8's two lectures must establish

**Lecture 1 — bathtub models vs flood-inundation modeling (Tuesday, Oct 20).**

1. Flow is not stage: discharge, stage, gage datum, the rating curve (Provo's real table: 3.42 → 8.00 ft,
   6.8 → 2,150 ft³/s, offset 3.20 ft) and why extrapolating above the top row is a guess.
2. Return period and AEP: the 2- to 100-year as "1 % chance every year"; a peak series and a
   Log-Pearson III fit, explained, not derived; regulation (all 90 Provo peaks coded 6).
3. Bathtub: one water surface, every cell below it is wet. Figure from our data: the 100-yr stage
   elevation (1,372.30 m) floods 15.4 km² of Utah Lake lowland and not one meter of river above the
   gage's neighborhood. Bathtubs suit lakes and coasts (Lab 6, Utah Lake's coastal zones), not rivers.
4. What FEMA does instead: 1-D hydraulics (HEC-RAS) on cross-sections; figure: three of the 43 Provo
   sections with WSEL and bed (median depth 1.80 m).

**Lecture 2 — HAND (Thursday, Oct 22).**

1. The idea: elevation relative to the stream cell each cell drains to, not to sea level; one
   threshold h floods a whole river. Figure: HAND map of the reach (0–198 m, most of the floodplain < 3 m).
2. How: Fill → D8 → accumulation → streams → Flow Distance VERTICAL (Lab 5's chain plus one tool);
   the stream definition is the critical choice — figure: no corridor mask (52 km² wet) vs mask (1.75 km²).
3. Stage to h: depth above zero flow; the hydro-flattened DEM channel sits ~0.47 m above FEMA's bed.
4. Figure pair at the same stage: bathtub vs HAND (numbers in §6).
5. Validation: hit rate, false-alarm ratio, CSI; the Provo answer (CSI ≈ 0.39) and where it fails
   (levee-confined upper reach, AH split flow) — what HAND cannot know (levees, bridges, conveyance).
   NOAA's National Water Model flood maps use HAND at continental scale (cite; link VERIFY — the
   water.noaa.gov page tried returned 404).

## 13. Risks

1. **Extrapolated rating** for the 25–100-yr rows (above 8.00 ft / 2,150 ft³/s). Mitigated: the
   verified and personal rows are inside the table; say so in the page.
2. **Gage datum / stage history** (2013–2019 gage heights ~2 ft high; 0.6 m elevation offset vs
   FEMA at the gage). Mitigated by using depth; VERIFY with the USGS Utah Water Science Center.
3. **LP3 is not Bulletin 17C** and regulated peaks violate its assumptions; our 1% (3,111) is 34 %
   above FEMA's published 2,325. Label it a teaching approximation; ask students to compare.
4. **The 2-yr floods 1.04 km² and 244 buildings**, which is surely too much (a 2-yr flow stays in
   the channel) — the hydro-flattened channel offset. Use it as the "where it's wrong" lesson or adopt
   the corrected convention (decision 3).
5. GUI unknowns: Iterate Field Values + inline arithmetic in Con; Raster to Polygon inside an
   iterator; Merge executing every pass (Lab 6). The arcpy oracle does not prove the GUI path.
6. 3DEP image service flakiness (HTTP 504 on a big request; 502 on October 9 during the link check);
   the hosted DEM removes the dependency. Building footprints are 2018-era ML footprints (UGRC page).
7. Midterm week: any GUI surprise costs students more than usual — the GUI build must happen by
   ~October 17.

## 14. Decisions for the instructor

1. Site: Provo River at Provo, 10163000? (Recommend yes.)
2. Design flows: our post-Jordanelle LP3 (2–100-yr, complete) with FEMA's FIS flows as a comparison
   question, or FEMA's published flows (10–500-yr, no 2/5)? (Recommend LP3 + FEMA question.)
3. Threshold convention: h = GH − 3.20 ft (simple; overpredicts small floods) or h − 0.47 m (FEMA-
   calibrated channel offset)? (Recommend the simple one, with the offset as a written question.)
4. DEM: 5 m from lidar (recommend) or the 10 m USGS 1/3″ product of Lab 5?
5. Personal flow Q = 900 + 12 × last two ID digits? (Recommend yes.)
6. Sensitivity variable: stream threshold (recommend) or corridor width?
7. Buildings only (recommend), or parcels and market value too?
8. Iterator: Iterate Field Values on the hosted table (new tool) or Lab 6's For over h (reuse)?

## 15. Still owed

Decisions → `docs/assignments/lab-07/` draft (the renumbering agent owns that folder; coordinate) →
icons and Figures A/B (metadata card; stage–discharge and HAND schematic from these numbers) → no-GUI
pilot → promote → **GUI build** at 175 % (`C:\Ames\Lab07GUI\`), every dialog captured, Figure C →
example maps (`arcpy.mp`) → report template → the two Week 8 decks (§12) → Learning Suite due date.

## Links checked (curl, October 9, 2026)

| Status | URL |
| --- | --- |
| 200 | https://waterdata.usgs.gov/monitoring-location/10163000/ |
| 200 | https://nwis.waterdata.usgs.gov/nwis/peak?site_no=10163000&agency_cd=USGS&format=rdb |
| 200 | https://waterdata.usgs.gov/nwisweb/get_ratings?site_no=10163000&file_type=exsa |
| 200 | https://waterservices.usgs.gov/nwis/site/?format=rdb&sites=10163000&siteOutput=expanded |
| 200 | https://streamstats.usgs.gov/gagestatsservices/stations/10163000 |
| 404 | https://streamstats.usgs.gov/gagepages/html/10163000.htm (no gage page) |
| 200 | https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28 |
| 200 | https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/14 |
| 200 | https://msc.fema.gov/portal/downloadProduct?productTypeID=FINAL_PRODUCT&productSubTypeID=FIS_REPORT&productID=49049CV001B |
| 200 | https://msc.fema.gov/portal/home |
| 502* | https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer (*worked hours earlier) |
| 200 | https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/historical/n41w112/USGS_13_n41w112_20260519.tif |
| 200 | https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services/Buildings/FeatureServer/0 |
| 200 | https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services/Parcels_Utah_LIR/FeatureServer/0 |
| 200 | https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services/UtahStreamsNHD/FeatureServer/0 |
| 200 | https://gis.utah.gov/products/sgid/location/building-footprints/ |
| 200 | https://gis.utah.gov/products/sgid/water/nhd-streams/ |
| 200 | https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/flow-distance.htm |
| 200 | https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/derive-stream-as-raster.htm |
| 200 | https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/fill.htm |
| 200 | https://pro.arcgis.com/en/pro-app/latest/tool-reference/modelbuilder-toolbox/iterate-field-value.htm |
| 200 | https://pro.arcgis.com/en/pro-app/latest/tool-reference/modelbuilder-toolbox/iterate-row-selection.htm |
| 200 | https://pro.arcgis.com/en/pro-app/latest/tool-reference/modelbuilder-toolbox/collect-values.htm |
| 200 | https://pro.arcgis.com/en/pro-app/latest/tool-reference/modelbuilder-toolbox/for.htm |
| 200 | https://pro.arcgis.com/en/pro-app/latest/tool-reference/analysis/spatial-join.htm |
| 200 | https://doi.org/10.3133/tm4B5 (Bulletin 17C) |
| 200 | https://pubs.usgs.gov/of/2017/1108/ofr20171108.pdf |
| 404 | https://water.noaa.gov/about/owp-hand-fim (find a working NOAA HAND reference) |
| timeout | https://www.usbr.gov/projects/index.php?id=471 (Provo River Project; VERIFY dam dates) |

## Files

`tools/lab07/`: `stage_table.py` (+ `.csv`, `_meta.json`), `fetch_dem.py`, `fetch_vectors.py`,
`run_model.py` (+ `check_values.json` 5 m default with log-interpolated h, `sensitivity_*.json`),
`xs_check.py` (+ `.json`), `h_sweep.py` (+ json), `bathtub.py` (+ json), `student_chain.py`
(+ json), `gotchas.py` (+ json), `personal.py` (+ the private `lab07_personal_lookup.csv`), `make_extract.py`,
`verify_package.py` (+ **`package_checks.json`, the canonical check values**).
`C:\Ames\HAND\`: `raw\` (NWIS, FIS PDFs, REST JSON), `dem\`, `HAND.gdb`, `work\`, `pkg\`, `PkgCheck\`.
