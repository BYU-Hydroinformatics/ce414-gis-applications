# Lab 8 (Big Southern Butte) — parity plan

Written October 5, 2026, to bring Lab 8 to the standard of Labs 1–7 (`tools/lab-conversion-guide.md`).
The live page `docs/assignments/lab-08/README.md` is untouched; the rebuild is
`docs/assignments/lab-08/draft.md` (search-excluded, not linked). **Nothing here is promoted until
Dan decides the items marked DECISION.** Lab 8 is due Saturday of Week 9 (October 31).

## Gap table

| Element (Labs 1–7) | Lab 8 now | Draft |
| --- | --- | --- |
| One study area | Big Southern Butte **plus a second feature in a DEM of the student's choosing** (15 points) | Big Southern Butte only (DECISION 1) |
| Two maps, baseline + one scenario | Two maps, but the second is the second DEM | Baseline + one Step 9 scenario (DECISION 1) |
| Hosted data with READ-ME and metadata questions | "Download from The National Map or Inside Idaho" (no URL) | `docs/data/lab08-big-southern-butte.zip` (10.4 MB): 1/3″ DEM cut from tiles n44w114 + n44w113 (the butte straddles 113° W), and a reference `Butte_Boundary`; Figure A owed |
| Reproducible check values | "between 3.0 and 6.0 km³ depending on your polygon" | A hosted outline (DECISION 2) and a fixed random seed (DECISION 3) make every step checkable |
| Projected coordinate system named | NAD 1983 UTM 12N at 30 m | UTM 12N at **10 m**, bilinear (DECISION 5) |
| A parameter and a sensitivity step | None (a TODO asks for one) | Number of points and the outline as parameters, plus one interpolation swap (DECISION 4) |
| Rubric five parts of ten | 5 + 10 + 5 + 15 + 15, with an SQL-threshold item from another lab | Five parts of ten (DECISION 6) |
| Report template | None | To build with `make_lab_report_template.js 08` after the decisions |
| GUI build and captures | Word-era captures, a pre-renumbering geodatabase name, an illegible model overview | Owed (Step figures marked TODO(capture)) |

## Decisions for Dan

1. **Drop Part 2** (the second DEM of the student's choosing). The conversion guide says no
   required second study area, and Part 2 is unbounded (any DEM, any feature, any volume) and
   ungradable against a check value. The sensitivity step replaces it; the "reuse the tool" idea
   survives as the student-drawn outline run, which goes through the same tool dialog.
2. **Host a reference outline.** `Butte_Boundary` (28.03 km²) is derived from the DEM, not
   digitized: a least-squares plane fitted to the plain 4.5–8 km from the summit (it falls 5.4 m per
   km to the north, which is what the old Figure 2 caption says), cells more than 10 m above it,
   connected to the summit, holes filled, smoothed (`make_outline.py`; the READ-ME explains it).
   Students still digitize their own outline in Step 9 and compare — the handout's own Spatial
   Considerations say the outline is the biggest source of difference, and now they measure it.
   Alternative: no hosted outline (every volume different, no check values past Step 1).
3. **Fix the random seed.** Create Random Points honors the Random number generator environment (listed in its tool reference). With seed 1
   (ACM599) the reference run's points are identical run to run (`run_model.py` tests it), so the
   page can quote 560 points kept and 5.145 km³. **Verify in the GUI** that the model-level
   environment gives the same first point (337,632.6 E, 4,806,349.7 N).
4. **Sensitivity design.** Parameters: the number of points and the outline. Runs: 250 and 4,000
   points, the student's own outline, and one copy of the model with **Spline** in place of IDW
   (ties to the Week 8 interpolation deck, and Spline overshoots: 11,963 cells come out below the
   plain). Measured spread (km³): method 4.48–5.31; outline ±200 m 4.85–5.32; points 250–4,000
   5.06–5.23; seed (1,000 points, six seeds) 5.145–5.161. The TIP hints that the random part matters
   least.
5. **10 m cells**, not 30 m: the DEM is 1/3″ (about 10 m north–south), the Lab 5 and Lab 7 pattern,
   and the 30 × 30 in the old expression becomes 10 × 10. Run time is a few seconds per tool.
6. **Rubric**: five parts of ten as Lab 7. The SQL-threshold sub-item (from another lab) becomes
   "the number of points and the outline exposed as parameters".
7. **Background**: the uncited "one of the largest volcanic domes on Earth (U.S. Department of the
   Interior, 2012)" and the dead BLM flyer are replaced by the USGS Yellowstone Volcano Observatory
   article "The Big Buttes of the Eastern Snake River Plain" (December 4, 2023): two coalesced
   rhyolite lobes, about 300,000 years old, about 760 m tall, among the largest rhyolite domes in the
   world. Godchaux et al. (1992) is about the *western* plain's phreatomagmatic volcanoes and is
   dropped; Greeley (1982) and Hughes et al. (1999) stay.
8. **The old 3.0–6.0 km³ range** is replaced by the check value. Wikipedia quotes about 8 km³ for the
   combined domes, unsourced; the draft does not cite it, but Step 9's third question asks what the
   model's number measures (volume above an interpolated plain, not the volume of the dome).

## Measured (ArcGIS Pro 3.7.1 arcpy, October 5, 2026)

`run_model.py` → `check_values.json`; `step_checks.py` → `step_checks.json`.

- Extract: 3,024 × 1,836 cells of 1/3″, 1,499.8–2,307.1 m, no NoData.
- Project Raster (UTM 12N, bilinear, 10 m): 2,314 × 1,944 cells, 1,499.8–2,306.8 m.
- Butte_Boundary 28.030 km²; Points_Boundary (Buffer 1,500 m) 65.411 km².
- Create Random Points, 1,000, seed 1: RASTERVALU 1,531.2–2,277.2 m; Erase leaves **560**
  (1,531.2–1,597.0 m, mean 1,559.4).
- IDW (power 2, variable 12, 10 m): inside the outline the plain runs 1,547.1–1,585.9 m.
- Extract by Mask: 280,311 cells (= 28.03 km²). DEM inside 1,554.8–2,306.8 m.
- Height above the plain: −0.5 to 729.1 m, mean 183.5 m; 53 cells below zero.
- Zonal Statistics SUM: **5.145 km³** (same with the default processing extent).

| Run | Volume (km³) | Cells below the plain |
| --- | --- | --- |
| Baseline (IDW, 1,000 points, seed 1) | 5.145 | 53 |
| Natural Neighbor | 5.029 | 0 |
| Spline (regularized, 0.1, 12) | 4.481 | 11,963 |
| Kriging (ordinary, spherical) | 4.988 | 210 |
| Trend (first-order plane) | 5.312 | 0 |
| 250 points (146 kept) | 5.229 | 0 |
| 500 points (274 kept) | 5.199 | 13 |
| 2,000 points (1,136 kept) | 5.103 | 91 |
| 4,000 points (2,302 kept) | 5.062 | 18 |
| Seeds 2–6 (1,000 points) | 5.146–5.161 | 0–83 |
| Outline −200 / −100 / +100 / +200 m | 4.846 / 5.008 / 5.236 / 5.322 | |

**Extent caveat.** All runs use the default processing extent, as a student's will. IDW gives the
same answer with the extent set to `Points_Boundary`, but Spline does not (4.428 km³, 12,449 cells
below the plain): it partitions its extent into regions, so its result depends on the extent. The
spline numbers a student gets will only match if they leave Processing Extent at its default.

## Still owed

1. Dan's decisions above.
2. GUI build in ArcGIS Pro 3.7.1 at 175 %: captures for every step, Figure C (Export To Graphic),
   confirm the seed environment and the tool-dialog run.
3. Figure A (metadata infographic) and tool icons (`make_svgs.py`, the Lab 7 pattern); example
   maps (`build_figures.py`).
4. No-GUI pilot by a subagent.
5. Report template (`make_lab_report_template.js 08`), then promote.
