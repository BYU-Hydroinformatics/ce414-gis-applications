---
marp: true
theme: ce414
paginate: true
footer: "CE 414 · Week 12 — Least Cost Path Analysis, Part B"
style: |
  strong { color: #0062b8; }
---

<!-- _class: lead -->
<!-- _paginate: skip -->

![bg right:42% w:96%](images/lcpb-accumulation.png)

![w:110](../theme/images/byu-medallion.svg)

# Least Cost Path Analysis

## Part B — The Tools, the Route, and What Moved It

CE 414 Engineering Applications of GIS
Civil & Construction Engineering
Brigham Young University
Dr. Dan Ames

<!-- Thursday of Week 12. Tuesday built the idea from the original least cost path lecture: a cost surface, the accumulated cost and back link rasters, a path walked home from the destination. Today: the tools ArcGIS Pro wants you to use now, Lab 11's own route computed from the lab's own model and data, and the question that matters to an engineer, which of its decisions actually moved the line. Every Lab 11 map and number comes from the lab's reference run (tools/lab11/run_model.py, check_values.json), drawn by tools/week12_lcp_figures.py; the Distance Accumulation and Optimal Path As Line captures are the lab's own Figures 7a and 7b, from the October 9, 2026 build of the lab in ArcGIS Pro 3.7.1 (C:\Ames\Lab11GUI\Lab11.aprx, ready for a live demo). -->

<!-- stamp:begin -->
<!-- _footer: '<span>CE 414 · Week 12 — Least Cost Path Analysis, Part B<span class="updated">Last Updated: 2026-10-09</span></span><span>© 2026 Daniel P. Ames · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></span>' -->
<!-- stamp:end -->

---

# Today's Goals

![bg right:38% w:94%](images/lcpb-corridor.png)

By the end of class you should be able to:

- Run a least cost path with ArcGIS Pro's current tools: **Distance Accumulation** and **Optimal Path As Line**
- Read a **back direction** raster as a compass angle
- Say which parts of a cost surface **move a route** and which only change its total
- Map a **corridor** of nearly-as-good routes, not just one line

<!-- The right-hand figure is where the hour ends: not one route but a corridor of nearly-as-good ones, between Lab 11's two endpoints. -->

---

# Tuesday in One Picture

![bg right:46% w:96%](images/lcpb-box.png)

- A **cost surface** cell: the price of **crossing that one cell**
- An **accumulated cost** cell: the cheapest **total** to get there from the source
- A **back direction** cell: **which way to step** to get home
- The path is walked **backward**, from the destination to the source

<!-- A 6 x 5 grid of 100 m cells, cost 1 (light) and 4 (dark), run through Distance Accumulation in ArcGIS Pro. Each number is the accumulated cost; each arrow is the back direction raster's value, drawn as a compass bearing. Read one aloud: the cell left of the source holds 400 and points east (90 degrees), straight home. Note the arrows that are not at 45-degree steps: 193, 121, 229 degrees. That is new, and it is the next section. The distinction between the first two bullets is the one Tuesday's quiz showed half the room missing. -->

---

<!-- _class: lead -->

# Part 1 — The Tools in ArcGIS Pro Today

---

# Cost Distance Is Deprecated

![bg right:52% w:98%](images/lcpb-cost-distance-deprecated.png)

- Open **Cost Distance** in ArcGIS Pro 3.7 and it tells you so
- "Deprecated" means it **still runs**, but **will be removed**
- The replacement: **Distance Accumulation**
- The same goes for **Cost Back Link** and **Cost Path**

<!-- A capture of the Geoprocessing pane in ArcGIS Pro 3.7.1, October 9, 2026. The notice is the tool's own; it links to Esri's deprecation page. Tuesday's lecture and Lab 11's current handout were written with the legacy tools; the concepts carry over unchanged, and Part 2 shows the two sets give the same route on Lab 11's data. -->

---

# Distance Accumulation

![bg right:46% contain](images/lcpb-distance-accumulation.png)

- **Sources**: the start point (Lab 11: the substation at Spanish Fork Canyon)
- **Barriers**: cells the route may never enter (Lab 11: the lakes)
- **Input Cost Raster**: your cost surface
- **Output Distance Accumulation Raster**: the running total
- **Output Back Direction Raster**: the way home, in **degrees**
- One run replaces **Cost Distance** *and* **Cost Back Link**

<!-- Lab 11's own Figure 7a: the routing step of the lab's model, filled in as the page tells students to. Source_Point and Destination_Point come from two Select tools on Endpoints. The barrier input takes the lakes as features; Cost Distance had no barrier input, so a barrier had to be NoData in the cost raster. Leave Input Surface Raster empty: that measures distance over the terrain's actual surface, a different question from cost. In Lab 11 the same tool, with only a source, also makes the three straight-line distance rasters. -->

---

# Optimal Path As Line

![bg right:46% contain](images/lcpb-optimal-path.png)

- **Destinations**: the end point (the substation at Bluffdale)
- The **accumulation** and **back direction** rasters from the last tool
- The output is already a **line feature class**
- So **Raster to Polyline** is no longer a step
- Its sibling, **Optimal Path As Raster**, gives the one-cell-wide raster

<!-- Lab 11's own Figure 7b. Destination Field fills in with UGRC_OID; with one destination it does not matter, nor does Path Type. The route it draws in the lab is 56.09 km. The old handout ended with Raster to Polyline because Cost Path only made a raster. -->

---

# Same Row, Two Answers

![w:1080 center](images/lcpb-row.png)

- **Cost Distance**: a step costs the **average of the two cells** it joins
- **Distance Accumulation**: a cell's total includes **its whole cost**; the source cell's own cost does not count
- Along a long route the totals **agree**; they differ by **half a cell's cost** at the ends

<!-- Both tools' real output on the same six 100 m cells, cost 1, 1, 4, 1, 1, 1, from the left. Legacy: 100 + (1+4)/2 x 100 = 350 at the dark cell; Distance Accumulation: 100 + 4 x 100 = 500. By the next cell both say 600. This is the rule Tuesday's grid slide described for the legacy tool; do not apply the "average of two cells" arithmetic to Distance Accumulation's numbers. Skip this slide if time is short. -->

---

# The Back Direction Is an Angle

![bg right:46% w:96%](images/lcpb-box.png)

- **0** marks the source; **90** = go east, **180** south, **270** west, **360** north
- Legacy **Cost Back Link** stored a code, **1 to 8**, one per neighbor
- Distance Accumulation can head off **between** the eight neighbors: 193°, 121°, 229°
- So its paths are **straighter** than a staircase of 45° steps

<!-- The angles are read straight off the back direction raster on the toy grid. On Lab 11's cost surface the legacy chain (Cost Distance with its back link, Cost Path, Raster to Polyline; lakes as NoData) gives 58.49 km against 56.09 km: much of the extra 2.4 km is the staircase. -->

---

<!-- _class: lead -->

# Part 2 — Lab 11's Route, Computed

---

# Lab 11's Cost Surface, Layer by Layer

![h:530 center](images/lcpb-factors.png)

<!-- Lab 11's model, from the hosted package at 30 m (tools/lab11/run_model.py): four scores from 1 (cheap) to 10 (expensive), slope in degrees, straight-line distance to a major road, to a city (0 inside one) and to an existing 46-345 kV line, plus 10 on every cell a major stream crosses, added with both weights at 1. The sum runs from 4 to 48, mean 23.69. Score tables are on the lab page's Analysis Considerations. -->

---

# Accumulated Cost, and the Route Home

![bg right:48% w:96%](images/lcpb-accumulation.png)

- The source: the mouth of **Spanish Fork Canyon** (green); the destination: **Bluffdale** (red)
- Straight line: **52.79 km**; cheapest route: **56.09 km**, **6%** longer
- It follows **existing transmission lines** almost the whole way: **99.7%** of it within 500 m of one
- The **lakes** (light blue) are barriers: the accumulation flows around them

<!-- The colors are Distance Accumulation's raster, the white lines its contours; the red line is Optimal Path As Line. The accumulated cost at the destination is 744,018 (cost x meters). It crosses 4 major streams. 92.8% of it lies within 1 km of a major road. Numbers: tools/lab11/check_values.json, the same values the lab page publishes. -->

---

# Reading the Back Direction Raster

![bg right:48% w:96%](images/lcpb-backdirection.png)

- Every cell knows **which way is home**
- The colors are **compass bearings**: 0 to 360
- Sharp seams are where two routes home **split**
- Optimal Path As Line just **follows the arrows** from Bluffdale

<!-- The twilight color ramp wraps around, so 0 and 360 (both "north") look alike. The seams are the boundaries between regions whose cheapest way home goes different ways around an obstacle; a destination on a seam has two nearly equal routes, which is the corridor slide's point. Skip if time is short. -->

---

<!-- _class: lead -->

# Part 3 — Which Decisions Moved the Line?

---

<!-- _class: quiz -->

# Predict First

![bg right:38% w:92%](images/lcpb-factors.png)

Change **one** decision in Lab 11's model. Which one moves the route **farthest**?

<ol type="A">
<li>Make slope five times as important (Slope_Weight 5)</li>
<li>Drop the city score</li>
<li>Drop the existing-line score (Line_Weight 0)</li>
<li>Take away the lake barrier</li>
</ol>

<!-- Ninety seconds, a show of hands for each letter. Most of the room picks A, B or D: terrain, cities and barriers feel like the big constraints. The answer is C. The next two slides are the answer. -->

---

# Three Decisions That Barely Mattered

![h:340 center](images/lcpb-nochange.png)

- **Slope_Weight 5**: at most **561 m** from the baseline · **no city score**: **276 m** · **no lake barrier**: **406 m**
- Flat valley floor, **in cities** the whole way, **away from the lakes**: the same along every candidate route, so they cannot choose between them

<!-- Measured on Lab 11 (tools/lab11/check_values.json and explore_weights.json; the farthest distance is from the baseline route, sampled every 100 m): Slope_Weight 5 55.73 km, 94% within 300 m; Slope_Weight 0 within 122 m; city weight 0 (changed in the expression, not a Lab 11 parameter) 56.40 km, 100% within 300 m, every cell of the baseline route has city score 10; no barrier 56.03 km, 97% within 300 m. Lab 11's Step 9 asks students to find the slope result themselves; do not give the numbers before they run it. Each would matter in another place, or with other scores: that is the lesson, not that slope and cities never matter. -->

---

# Two That Did

![h:360 center](images/lcpb-scenarios.png)

- **Line_Weight 0**: **53.70 km**, up to **3.4 km** from the baseline · **no road score**: **54.96 km**, up to **1.6 km**
- The **existing-line score** is what holds the route where it is

<!-- The thick pale red line in each panel is the baseline, for comparison; yellow lines are the existing transmission lines. Line_Weight 0 puts only 26% of the route within 300 m of the baseline; road weight 0 (changed in the expression, not a Lab 11 parameter) 55%. This is why Lab 11's personal number is a Line_Weight between 0 and 0.495: it is the factor that moves the route, and below about 0.5 is where it does. The rubric's question "what would you change to make the model more realistic?" starts here. -->

---

# A Corridor, Not a Line

![bg right:46% w:96%](images/lcpb-corridor.png)

- Run Distance Accumulation **from both ends** and **add** the two rasters
- Each cell gets the cost of the **best route forced through it**
- Within **1%** of the cheapest: **89.7 km²**; within **5%**: **310 km²**; within **10%**: **458 km²**
- Where the band is **wide**, the exact line is **arbitrary**; where it pinches, it is **not**

<!-- The sum was computed with Raster Calculator on the two accumulation rasters; ArcGIS Pro also has a Corridor tool in Spatial Analyst that does the same sum (seen in the Geoprocessing search on October 9, 2026; not run for this deck). On Lab 11's cost surface the band is narrow near both endpoints and wide along the valley floor, where several nearly equally cheap routes exist; the lake barrier bounds it on the west. An engineer presents the corridor to a siting board, then picks a line inside it for reasons the cost surface never saw: land ownership, a tower foundation, a landowner's objection. -->

---

<!-- _class: activity -->

# Next: Lab 11, Power Line Routing

![bg right:40% w:94%](images/lcpb-accumulation.png)

- Today's **two substations**, **four scores**, **river cells** and **lake barrier**, at 30 m
- Build it as **one ModelBuilder model**, with **Slope_Weight** and **Line_Weight** as parameters
- **Your own Line_Weight** = 0.005 × the last two digits of your BYU ID
- Run it again with the weights changed, and explain **which moved the route and why**

[Lab 11 — Least Cost Path Power Line Analysis](https://byu-hydroinformatics.github.io/ce414-gis-applications/assignments/lab-11/)

<!-- Legacy check on Lab 11's cost surface: Cost Distance (lakes as NoData) + Cost Path (each cell) + Raster to Polyline gives 58.49 km; sampled every 100 m it is a median 184 m from the Distance Accumulation route, 95% within 670 m, all within 788 m. Lab 11 uses only the current tools. -->

---

# Before Next Class

![bg right:30% w:94%](images/lcpb-backdirection.png)

- **Lab 11 — Least Cost Path Power Line Analysis** — due **Saturday 11:59 pm**: [assignments/lab-11](https://byu-hydroinformatics.github.io/ce414-gis-applications/assignments/lab-11/)
- Next week: the **final project** (Tuesday), and Thanksgiving
- Office hours: [calendly.com/dan-ames/office-hours](https://calendly.com/dan-ames/office-hours)

<!-- Deck written October 9, 2026, as the second least cost path lecture, building on Tuesday's deck (itself converted from "CE 414 Week 11 - Least Cost Path Analysis.pptx"); realigned the same day with the rebuilt Lab 11. Figures and numbers: tools/week12_lcp_figures.py (toy grids, and Lab 11's reference run from tools/lab11/run_model.py; numbers in tools/week12_lcp_numbers.json). The Cost Distance capture is from an ArcGIS Pro 3.7.1 session at 175 %; the other two tool captures are Lab 11's Figures 7a and 7b. -->

---

<!-- _class: activity -->

# One Last Thing — What Moved the Line?

<div class="columns">
<div>

Five questions on the current tools, the back direction raster, which factors move a route, and corridors. **Scan the code**, or open the link below.

- Not graded, nothing recorded — it is a check that today landed
- Every answer explains itself; read the explanation before you move on
- The line-weight question is the one Lab 11's Step 9 turns on

<span style="font-size: 0.5em; color: #4a5568; white-space: nowrap;">byu-hydroinformatics.github.io/ce414-gis-applications/quizzes/cost-paths/</span>

</div>
<div>

![w:400 center](images/quiz-cost-paths-qr.png)

</div>
</div>

<!-- Four minutes, in pairs. If the room has no signal, put the URL on the board. -->
