# Lab 9 (Interpolation Explorer) — parity plan

Written October 6, 2026, to bring Lab 9 to the standard of Labs 1–8 (`tools/lab-conversion-guide.md`).
The overall plan for Labs 9–11 is `tools/labs-09-11-plan.md`; the instructor accepted every
recommendation in it on October 6, 2026, including the Lab 9 redesign in its section 4. The live page
`docs/assignments/lab-09/README.md` is untouched; the rebuild is `docs/assignments/lab-09/draft.md`
(search-excluded, not linked). Lab 9 is introduced Tuesday of Week 9 and due Saturday of Week 10
(November 7).

**Source.** `Lab 8 - Practicing with Interpolation.docx` (instructor's copy in Downloads, saved
October 6, 2026). The September 3 migration on the live page matches it step for step; its four media
files are the two figures plus two header logos.

**Instructor's intent (October 6).** Lab 8 uses interpolation only to rebuild the plain under Big
Southern Butte. Lab 9 is where students *explore* interpolation: sample a known surface, rebuild it
with several methods and parameter settings, compare each rebuild with the truth, and learn how each
method behaves. The revision keeps that design and gives it the course spine.

## Gap table

| Element (Labs 1–8) | Lab 9 now | Draft |
| --- | --- | --- |
| One study area | Y Mountain **plus a second DEM of the student's choosing** (15 points) | Y Mountain only; the "model works on any DEM" idea survives in the personal-seed run through the tool dialog |
| Hosted data, READ-ME, metadata questions | "Download a DEM that covers Y Mountain" (no source) | `docs/data/lab09-y-mountain.zip` (1.9 MB): 1/3″ DEM from tile n41w112 + `Lab09.gdb\Study_Area`; Figure A metadata card |
| A live source deliberately varied in | None | Step 1 adds the USGS 3DEP elevation **image service** and asks what came back (Week 9 tie-in) |
| Reproducible check values | None ("draw a box") | Hosted study rectangle on the 30 m grid + fixed seed 1: every step has a number |
| Coordinate system | "UTM NAD 83 Zone 12 North", 30 m | NAD 1983 UTM Zone 12N, 30 m, bilinear (kept) |
| One model, parameters exposed | Seven interpolation tools, seven difference chains, input DEM as the only planned parameter | Three methods (Thiessen, IDW, Kriging), each carried through to RMSE; parameters: number of points, IDW power, Kriging semivariogram |
| Sensitivity step with table and three questions | "Choose different values" inside the model (six variants) | Step 10: a personal-seed baseline and four tool-dialog runs, one table, three questions, 200 checkpoints |
| RMSE described correctly | "squaring your errors, summing them, and taking the square root" (omits the mean) | Mean of the squared errors, then the root; Zonal Statistics as Table + Calculate Field |
| "Where the method breaks" | "Which method worked best and why?" | Where on the mountain the errors are largest, with coordinates from the student's own error map |
| Rubric five parts of ten | 0 + 5 + 10 + 5 + 15 + 15 | Five parts of ten |
| Individual work | Partners allowed | Individual (plan section 4) |
| Report template | None | `make_lab_report_template.js 09` after review |
| GUI build and captures | Word-era Figure 2 (Thiessen branch only) | **Owed**: desktop control denied October 6; every dialog figure is a `TODO(capture)` |
| Figure 1 | Bolstad 6th ed. figure, reproduced | Replaced by Figure B, a measured profile across the mountain front (`make_svgs.py`); Bolstad cited, not copied |

## Design decisions made in the draft (flag if you disagree)

1. **Thiessen is built as polygons and then rasterized** (Create Thiessen Polygons → Polygon to
   Raster on `RASTERVALU`), as the handout allowed. Create Thiessen Polygons needs an
   **Advanced** license; this machine is ArcInfo. *Verify the lab machines are Advanced*; if not,
   Natural Neighbor replaces it.
2. **Errors are True minus Surface**, so a positive error means the surface came out too low.
3. **RMSE in the model**: Raster Calculator `Square(...)`, Zonal Statistics as Table (Mean over
   `Study_Area`), Calculate Field `RMSE = math.sqrt(!MEAN!)`. Three output tables are model
   parameters, so every dialog run keeps its three numbers.
4. **Personal seed** (plan section 8): Steps 0–9 use seed 1 and match this page; Step 10 starts by
   changing the seed to the last four digits of the student's BYU ID and re-running inside
   ModelBuilder. That run is Map 1 and the first row of the table. `run_model.py --seed NNNN`
   reproduces any student's table in about two minutes.
5. **Checkpoints** (question 3): 200 points from seed 99, the same for everyone, never used to
   interpolate. Extract Multi Values to Points + Calculate Field + Summary Statistics.
6. **Kriging's own error estimate is not used.** Measured: its prediction standard error averages
   79.6 m against a real RMSE of 14.5 m, correlation with the real error 0.25 (one global
   semivariogram over a valley floor and a mountain front). Too confusing for this lab; noted here
   in case a later version wants it.

## Measured (ArcGIS Pro 3.7.1 arcpy, October 6, 2026)

`run_model.py` → `check_values.json`; `extra_checks.py` → `extra_checks.json`. Seed 1, ACM599.

- Extract: 1,188 × 756 cells of 1/3″, 1,368.0–2,896.9 m, no NoData.
- Project Raster (UTM 12N, bilinear, 30 m): 314 × 262 cells, 1,368.1–2,896.5 m.
- Study_Area 8.67 × 6.99 km = 60.6 km²; True_DEM 289 × 234 (one empty row), 67,337 cells, 1,368.5–2,896.5 m, mean 1,819.8 m.
- Create Random Points, 2,500, seed 1: first point 444,603.3 E 4,453,723.7 N; `RASTERVALU`
  1,368.7–2,886.7 m; a repeat run is identical.
- Thiessen: 2,500 polygons; surface 1,368.7–2,886.7 (exactly the samples'); error −234.1 to +214.3,
  mean −0.39; **RMSE 28.29 m**.
- IDW (power 2, variable 12): surface 1,368.7–2,885.5; error −136.8 to +169.9, mean −0.84;
  **RMSE 20.71 m**.
- Kriging (ordinary, spherical, variable 12): surface 1,368.7–2,884.3; error −104.0 to +164.4, mean
  −0.31; **RMSE 14.46 m**.
- Largest IDW and Kriging error at 447,570 E 4,456,642 N (40.2586 N, 111.6166 W).
- 3DEP image service, value at the highest cell (40.21415 N, 111.58865 W): 2,896.7 m (REST identify)
  vs 2,896.5 m in True_DEM. Service: Web Mercator (3857), 1 m pixels, F32, bilinear default.

## Sensitivity (for setting expectations; do NOT publish)

| Run (seed 1) | Thiessen | IDW | Kriging | Checkpoint RMSE Th / IDW / Kr |
| --- | --- | --- | --- | --- |
| 250 points | 80.73 | 69.46 | 50.38 | 75.77 / 71.18 / 50.85 |
| 1,000 points | 44.07 | 37.00 | 24.90 | 42.55 / 38.80 / 23.88 |
| **2,500 (baseline)** | **28.29** | **20.71** | **14.46** | 30.38 / 23.16 / 17.12 |
| 10,000 points | 15.71 | 10.39 | 6.90 | 15.20 / 9.85 / 7.14 |

- IDW power 1 / 2 / 3 / 5: 23.98 / 20.71 / 20.20 / 21.60.
- Kriging spherical, exponential, linear, circular all 14.46; Gaussian 24.81 (surface max 2,826.1,
  it shaves the peaks).
- Seeds 2–5 at 2,500: Thiessen 28.2–29.1, IDW 19.2–21.2, Kriging 13.1–14.2. The ranking never
  changes.
- RMSE by slope (Thiessen / IDW / Kriging): <10° 5.0 / 5.3 / 3.9; 10–25° 25.7 / 25.2 / 17.7;
  25–35° 37.7 / 26.8 / 17.8; >35° 47.7 / 30.6 / 22.4.
- Personal seed 4321 (oracle test): baseline row and checkpoints reproduced in one call.

## Pilot (no-GUI, October 6, 2026)

`C:\Ames\Pilot09\PILOT_NOTES.md`. Every seed-1 number reproduced from the page and the zip. The serious
finding: without an **Extent** environment, IDW and Kriging at 250 points cover only 66,297 of 67,337
cells (RMSE 69.47 / 50.24 vs 69.46 / 50.38), and coverage depends on the seed, so personal-seed tables
would not match the oracle. Extent = True_DEM is now in Step 0 (the oracle always set it). Also fixed:
Step 10 order (Map 1 and checkpoints before any dialog run), semivariogram parameter path, Map 2
deliverable vs rubric, "largest error" defined, citation question graded, Figure A names its values.


## Simplification (October 7, 2026, instructor's request)

Students now receive `Lab09.gdb\True_DEM` (projected, 30 m, clipped) and three hosted point sets
(`Sample_Points_250`, `_2500`, `_10000`; seed 1, `RASTERVALU` only) instead of projecting, clipping
and sampling the DEM themselves; the page explains what we did for them. Measured effect:

| | Before | After |
| --- | --- | --- |
| Tools in the model | 20 | 16 |
| Model parameters | 12 | 9 (sample points, IDW power, semivariogram, 3 errors, 3 RMSEs) |
| Steps | 0-10 | 0-8 |
| ModelBuilder run | about 1.5 min | 7 s |

Pain points removed (all found in the first GUI build or the pilot): the Snap Raster / ERROR 010654
trap (True_DEM is now an input), Project Raster's 9.06 m proposal and coordinate picker, the
`Study_Area:1` model-variable choice and two Create Variable steps for points and seed, IDW/Kriging
defaulting to the `CID` field (gone: the hosted points have no `CID`), and dialog runs deleting the
truth and the points (inputs are never deleted).

Kept: the sample-count comparison (three hosted sets, same seed) and the personal seed, which moved
out of the model into two tool runs in Step 8 (Create Random Points with the BYU ID digits, Extract
Values to Points). `run_model.py --seed` now reproduces the student's three own rows.

Verified from the zip (`verify_package.py` -> `package_checks.json`) and in a second GUI build
(`C:\Ames\Lab09GUI2\`): course points 250 / 2,500 / 10,000 give 80.73 / 69.46 / 50.38,
28.29 / 20.71 / 14.46 and 15.71 / 10.39 / 6.90; seed 4321 gives 27.32 / 19.10 / 12.79 and, with IDW 3
and Kriging Gaussian from the tool dialog, 18.54 / 25.45 — all exactly the oracle.

Note: `check_values.json` is from the pre-simplification run (course baseline, its own checkpoints); `package_checks.json` is current. Pilot 2 (October 7, `C:\Ames\Pilot09b\`) reproduced every number from the zip and found ten text issues, all fixed.

## Second simplification (October 7, 2026, instructor's request)

No personal point set: Step 8 is five tool-dialog runs on the course's sets (250 and 10,000 points;
IDW 1 + exponential and IDW 3 + Gaussian on 2,500; and run 5). The per-student element is run 5's
**IDW power = 1 + (last two digits of the nine-digit BYU ID number) / 40**, 1.000 to 3.475: 100
possible values instead of the 10 a last-digit rule gives, for the same effort. `Checkpoints`
(seed 99, 200 points) is hosted in the zip, so no student runs Create Random Points at all. Grading
table for every power: `package_checks.json['personal_power']`. GUI-checked: power 3.225 from the
tool dialog gives IDW RMSE 20.29 (Thiessen 28.29 and Kriging 14.46 unchanged).

Limitation accepted: every other number, including the largest-error coordinates, is now the same
for every student; the IDW-power row, the `.atbx` submission and spot-check vivas are the checks.

**Future customization (instructor's idea):** the student's NetID (self-chosen letters and numbers)
could seed a personal point set or another personal parameter in a later version; turn it into a
number with a stated rule (for example the sum of its characters' positions in the alphabet and
digit values) so the grader can reproduce it. `run_model.py --seed` already reproduces seeded runs.

## Still owed

1. ~~GUI build~~ **Done October 7, 2026** (`C:\Ames\Lab09GUI\Lab09.aprx`, captures in `caps\`): every
   check value reproduced in the GUI; 18 figures and Figure C in the draft. Settled there: the service
   arrives as an 8-bit **hillshade** (Explore reads 154, not an elevation) in Web Mercator at 1 m;
   the semivariogram and the random seed (Create Variable ▸ From Environment) can both be model
   parameters; **Snap Raster `True_DEM` breaks dialog runs** (ERROR 010654), so the environments are
   now Snap Raster `DEM_UTM` + Extent from `YMountain_DEM.tif`; four silent wrong defaults (Thiessen
   Output Fields, Polygon to Raster Value field, IDW/Kriging Z field `CID`, ZSaT Statistics All, and
   Calculate Field Type Text) are now WARNING boxes. Still to try: a dialog run with Kriging Gaussian.
2. Promotion, then the report template (`node make_lab_report_template.js 09` reads README.md), the
   Week 9 deck alignment, and the Learning Suite due date (November 7). Example maps and the no-GUI
   pilot are done.
