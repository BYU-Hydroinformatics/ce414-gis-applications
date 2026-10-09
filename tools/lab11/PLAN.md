# Lab 11 (Least Cost Path Power Line) — rebuild plan

Written October 9, 2026. Design source: `tools/labs-09-11-plan.md` section 6, whose recommendations
the instructor accepted on October 6, 2026. This file records how they were applied, the two choices
that plan left open, and everything measured. Authority for "done": `tools/lab-conversion-guide.md`.

## Accepted decisions (labs-09-11-plan.md, section 6 and section 8)

1. **Distance Accumulation + Optimal Path As Line** replace Cost Distance / Cost Back Link / Cost Path /
   Raster to Polyline. (Verified in ArcGIS Pro 3.7.1, October 9: Cost Distance shows its own
   deprecation notice naming Distance Accumulation.)
2. **Slope, not raw elevation**, as the terrain cost. ("Lower is cheaper" is not a defensible
   engineering cost; steepness is. The Week 12 Part B deck measured the old elevation multiplier:
   on its own it gives nearly the straight line.)
3. **Personal numbers from the BYU ID** (section 8, item 1). Applied as a personal **line weight**,
   `0.005 × last two digits` (0 to 0.495); `run_model.py personal` writes the lookup. (First set at
   0.20 + 0.01 × digits; the no-GUI pilot of Oct 9 found any weight above about 0.6 stays within 300 m of
   the baseline, so about 60 of 100 students would have had the baseline route.)
4. **Upload the toolbox (`Lab11.atbx`)** with the report (section 8, item 2), as in Labs 7 and 10.
5. **Judgment tied to their own map** (section 8, item 4): "where the route is unrealistic" must name
   a place on their route with coordinates and a cropped figure.

## The two choices the plan left open (made here; the instructor may override)

- **Hard barriers: open water only.** Lakes over 1 km² (Utah Lake, Deer Creek Reservoir and five
  unnamed waterbodies in the box) go in Distance Accumulation's barrier input. City cores stay a cost,
  because the endpoints themselves are in cities and Utah County's valley is nearly all municipal.
- **Scenario wording.** Kept: a line from the mouth of Spanish Fork Canyon (the wind park) to
  Bluffdale (the data center), but the endpoints are now **two existing substations** read from the
  UGRC TransmissionLines layer (OBJECTID 2185, 428 m from the handout's source coordinate, and 1350,
  1,095 m from its destination coordinate), not typed coordinates. "New NSA data center" becomes
  "the data center at Bluffdale". (`probe_endpoints.py`, `endpoint_chips.py`.)

## The model

Cost = Slope_Weight × Slope_Score + Road_Score + City_Score + Line_Weight × Line_Score + Crossing, where

| Score | From | Classes |
| --- | --- | --- |
| Slope_Score | Slope (degrees) of the 30 m DEM | 0–5: 1, 5–10: 2, 10–15: 4, 15–20: 6, 20–30: 8, > 30: 10 |
| Road_Score | distance to a major road (Interstate, Other Freeway, Principal Arterial) | ≤ 1 km: 1, 1–2 km: 3, 2–5 km: 6, > 5 km: 10 |
| City_Score | distance to a city boundary (0 inside) | ≤ 1 km: 10, then 8, 6, 4, 2 by kilometer to 5 km, beyond: 1 |
| Line_Score | distance to an existing kV line | ≤ 500 m: 1, 0.5–2 km: 5, > 2 km: 10 |
| Crossing | a major stream cell (IsMajor = 1, Polyline to Raster) | 10, else 0 |

Distances are straight-line, made with Distance Accumulation with no cost raster (the same tool the
route uses). Parameters: **Slope_Weight** (1) and **Line_Weight** (1), plus the barrier input,
which a student can clear in the tool dialog to test "barrier versus cost".

**Why these two parameters (measured, October 9).** The first design exposed Slope_Weight and a
river Crossing_Cost. Neither moved the route: slope weight 0 to 2, crossing cost 0 to 20 and removing
the lake barrier all kept it within a few hundred meters of the baseline (`check_values.json` of
that run, superseded). 99.7 % of the route lies within 500 m of an existing kV line, so the
co-location score dominates. `explore_weights.py` (`explore_weights.json`): Line_Weight 0 puts only
26 % of the route within 300 m of the baseline (53.7 km); 0.5 keeps 74 %; road weight 0 keeps 55 %;
slope weight 5 keeps 94 %; city weight 0 keeps 100 %. So the student varies Line_Weight (which moves
the route kilometers) and Slope_Weight (which, in a flat valley, barely does); the contrast is the
lesson, and the personal number is a Line_Weight in the range where the route responds.

Data: `docs/data/lab11-power-line.zip` (`make_package.py`): 3DEP at 30 m in UTM 12N, UGRC roads with a
UDOT functional class, all NHD lakes and streams in the box, municipalities, transmission lines and
substations, and the two endpoint substations. Students do the four Selects themselves.

## Measured

See `check_values.json` (`run_model.py`) and `personal_lookup.csv` (`run_model.py personal`).
