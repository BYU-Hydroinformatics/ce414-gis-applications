# Lab 7 (Avalanche Hazard) — parity plan

Written October 2, 2026, while Dan was away, to bring Lab 7 to the standard of Labs 1–6
(`tools/lab-conversion-guide.md`). The live page `docs/assignments/lab-07/README.md` is untouched;
the rebuild is `docs/assignments/lab-07/draft.md` (search-excluded, not linked). **Nothing here is
promoted until Dan decides the items marked DECISION.** Lab 7 is due Saturday of Week 8
(October 24); the draft is meant to be reviewed before Tuesday, October 20.

## Gap table

| Element (Labs 1–6) | Lab 7 now | Draft |
| --- | --- | --- |
| One study area | Snowbird **plus a second resort of the student's choosing** (required) | Snowbird only (DECISION 1) |
| Two maps, baseline + one scenario | Three maps (Con method, multiply method, second resort) | Two maps (DECISION 2) |
| Hosted data with READ-ME and metadata questions | Students download NED from a dead UGRC page | `docs/data/lab07-little-cottonwood-dem.zip` (2.4 MB, USGS 1/3″ tile n41w112) + UGRC ski-area boundaries as a live layer; Figure A owed |
| Projected coordinate system named | "Project Raster to the NAD 1983 projection" (a datum, not a projection) | NAD 1983 UTM zone 12N, 10 m, bilinear (as Lab 5) |
| Check values in every step | None | Every step (below) |
| A parameter and a sensitivity step | None; "divide 0–125 into five categories" with no breaks | Elevation-band shift as a model parameter + three combination rules (DECISION 3, 4) |
| Where the method breaks | A hint question | Its own deliverable: snowpack, weather, wind loading, triggering; vegetation and terrain traps; the DEM's ground surface |
| Rubric five parts of ten | 5 + 10 + 5 + 30, plus a "/50 self-assessment" row | Five parts of ten (DECISION 5) |
| Report template | None | To build with `tools/templates/make_lab_report_template.js` after the decisions |
| GUI build and captures | Word-era screenshots from two model versions | Owed (Step figures marked TODO(capture)) |

## Decisions for Dan

1. **Drop the second ski area** (the conversion guide says no required second study area). The
   draft drops it; the sensitivity step replaces it.
2. **Two maps.** The "all three agree" Con method becomes a step with a check value and a report
   question (it leaves 96 % of Snowbird unclassified), not a map.
3. **How to turn the 1–125 product into five classes.** The handout says only "divide the ranges
   0–125 into five categories". The draft takes the **cube root of the product** (the geometric
   mean of the three classes) and rounds it: products 1–3 Low, 4–15 Moderate, 16–42 Considerable,
   43–91 High, 92–125 Extreme. It keeps the handout's point (5, 5, 4 → 100 → Extreme) and is one
   Raster Calculator expression. Alternatives: equal intervals of 25 (puts 5,5,4 in Extreme too, but
   5,5,1 = 25 in Low); natural breaks (not checkable).
4. **The sensitivity design.** Two things move: (a) a model parameter, **Elevation shift**, that
   moves all four altitude breaks (an advisory's bands change with the storm and the season), and
   (b) two more combination rules computed in the same run with **Cell Statistics** — the worst
   factor (maximum) and the best factor (minimum). Finding: at Snowbird the altitude bands barely
   matter (69 % of the area is above 2,800 m) while the combination rule changes Extreme from 3 % to
   76 % of the area. The TIP hints at the first without giving away the second.
5. **Wording.** The draft calls the output **terrain-based avalanche hazard screening** and says
   in Background what it is not (no snowpack, weather, wind or trigger). The title stays "Lab 7:
   Avalanche Hazard" so the schedule and Learning Suite links still read right. Rename if you want.
6. **Table 1 stays as the handout has it** (from a Sawtooth Avalanche Center advisory), with one
   correction: slope's Low band starts at 0, not −1 (−1 is the Aspect tool's flat code). The aspect
   row keeps −1 in Extreme as written, and the draft points out what that does to flat cells
   (nothing much: flat cells are slope class 1).
7. **References**: the uncited "150 deaths a year (National Geographic)" and "Clark et al. 2002"
   are replaced by sources checked October 2, 2026: CAIC (27 US avalanche deaths per winter over
   the last 10 winters) and avalanche.org's encyclopedia (slope angle; aspect). Dead Sawtooth link
   replaced by the site root.

## Measured (ArcGIS Pro 3.7.1 arcpy, `run_model.py` and `tool_checks.py`, October 2, 2026)

- Extract: 1,296 × 864 cells of 1/3″, 2,176.4–3,500.5 m, no NoData.
- Project Raster (UTM 12N, bilinear, 10 m): 1,023 × 896 cells, 2,178.0–3,499.4 m.
- Slope max 77.8°. Aspect flat cells (−1): 480 in the whole extent.
- Snowbird (UGRC SkiAreaBoundaries, OBJECTID 13): 10.781 km² by Tabulate Area at 10 m.
  (UGRC's Shape__Area, 18.7 km², is Web Mercator: divide by about 1.73 at this latitude.)
- Snowbird by class (km²), shift 0, measured as students will (Tabulate Area against the live
  Web Mercator layer; `student_route_checks.json` — the page uses these):

| Classes | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- |
| Altitude | 0 | 0.172 | 1.638 | 1.527 | 7.445 |
| Slope | 4.986 | 1.667 | 0.794 | 1.289 | 2.047 |
| Aspect | 0.571 | 2.054 | 2.768 | 3.493 | 1.896 |
| All three agree (0 = not classified: 10.346) | 0 | 0 | 0.010 | 0.090 | 0.336 |
| Geometric mean (baseline) | 0.168 | 3.162 | 3.691 | 2.673 | 1.087 |
| Worst factor (maximum) | 0 | 0.082 | 0.758 | 1.738 | 8.203 |
| Best factor (minimum) | 5.116 | 2.363 | 1.663 | 1.303 | 0.336 |

  Rule_Spread (worst − best) 0–4: 0.436 / 1.559 / 2.547 / 2.931 / 3.309. (`check_values.json`
  and `tool_checks.json` used the boundary projected first and differ in the third decimal.)

- Sensitivity, geometric mean, High + Extreme (km²): −400 m 3.976; −200 m 3.936; 0 3.760;
  +200 m 3.316; +400 m 2.465. Maximum rule Extreme: 10.613, 9.152, 8.205, 6.415, 4.289.
  Minimum rule Extreme: 0.415, 0.406, 0.336, 0.258, 0.126. (Do not publish; the TIP hints.)
- Run time of the whole reference run: 51 s.
