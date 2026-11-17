---
marp: true
theme: ce414
paginate: true
footer: "CE 414 · Week 12 — Network Analysis, Part A"
style: |
  strong { color: #0062b8; }
---

<!-- _class: lead -->
<!-- _paginate: skip -->

![bg right:42% w:96%](images/nab-one-station-rings.png)

![w:110](../theme/images/byu-medallion.svg)

# Network Analysis

## Part A — Distance Along the Roads, and the Service Area

CE 414 Engineering Applications of GIS
Civil & Construction Engineering
Brigham Young University
Dr. Dan Ames

<!-- Tuesday of Week 12, the last new topic of the course, two weeks before Midterm 2. The course has measured distance twice: as a buffer in Lab 1 and as accumulated cost across a raster in Lab 10. Today is the third way, along a road network: what a network is made of, how its costs work, and the first solver, the service area, with its three tools. Thursday adds closest facility and location-allocation and then builds Lab 11's model. Every map and number here comes from Lab 11's own data (UGRC's prebuilt Utah Street Network clipped to Utah County, the 42 fire stations, the 2020 Census blocks) and reference run, drawn by tools/week12_network_figures.py; the numbers are in tools/week12_network_numbers.json. Redivided November 16, 2026: service areas and their tools moved here from Thursday, and "What This Network Does Not Know" moved to Thursday. -->

<!-- stamp:begin -->
<!-- _footer: '<span>CE 414 · Week 12 — Network Analysis, Part A<span class="updated">Last Updated: 2026-10-28</span></span><span>© 2026 Daniel P. Ames · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></span>' -->
<!-- stamp:end -->

---

# One More Lab After This One

![bg right:42% w:94%](images/na-cyoa-question-data-recipe.svg)

- **Lab 11** this week is the **last lab with a recipe**: the question, the data and the steps are handed to you
- After it, one more: **Lab 12, Choose Your Own Adventure**
- **Your** question, **your** data, **your** ModelBuilder model, and a five-minute **training video** that teaches it
- Due **Thursday of Week 15**, the last day of classes
- Full details **next Tuesday, November 24**. Until then, notice the questions you would like a map to answer

<!-- Set the stage for the finish line: one lab with a recipe, then one where the students write the recipe. The figure is the Week 13 deck's own: every lab so far handed over the question, the data and the recipe, and Lab 12 takes all three away. Keep it short; the Week 13 deck carries the requirements and the scoring (individual, 100 points, an unlisted YouTube video, a PDF report and an ArcGIS Pro project package). The lab page is live now for anyone who wants to read ahead: assignments/lab-12. Thursday of Week 13 is Thanksgiving. -->

---

# This Week's Lab Goal

![bg right:42% w:96%](images/nab-lab11-map1.png)

**Lab 11, Fire Response Coverage:** *who in Utah County lives more than **four minutes' drive** from a fire station?*

- Build **one ModelBuilder model**: a **service area** around all 42 stations, then a **count of the people** outside it
- Measure the same four minutes as a **buffer**, and compare the two answers
- Run it again at **your own cutoff** and at 2, 6 and 8 minutes
- Due **Saturday**: two maps, a table, the report and `Lab11.atbx` · [the lab page](https://byu-hydroinformatics.github.io/ce414-gis-applications/assignments/lab-11/)

<!-- Say the goal before any of the theory, so every slide today has somewhere to land. The map is the lab's own Figure 9. Everything today is a piece of this model: the network (Part 1), its costs (Part 2), and the service area and its three tools (Part 3). Thursday finishes the model: from polygons to people, the buffer comparison, and the cutoff. Each student's cutoff is 4 + 0.04 x the last two digits of their BYU ID. -->

---

# Today's Goals

![bg right:40% w:96%](images/na-edges-junctions.png)

By the end of class you should be able to:

- Say what a **network dataset** is made of: **edges**, **junctions**, **connectivity**
- Explain what an **impedance** is, and why minutes and meters give **different routes**
- Describe how **one-way streets** and **turns** enter a network, as costs or as walls
- Run a **service area** in ArcGIS Pro: the analysis layer, **Add Locations**, **Solve**

<!-- The right-hand figure is 840 m of Provo as the network sees it: every edge labeled with its minutes, every junction a circle, the one-way edges in orange. By the end of the hour every element of it should mean something, and the last part of the hour spreads four minutes outward through it from a station. -->

---

# Three Ways to Measure Distance

![bg right:42% w:96%](images/na-four-minutes-two-ways.png)

| Lab | Distance | Moves |
| --- | --- | --- |
| **1** | **Straight-line** | any direction, all at once |
| **10** | **Cost distance** | cell to cell, at a price |
| **11** | **Network distance** | along the roads only |

- The **same four minutes** from one Provo station: a 3.75 km circle covers **44 km²**; the roads reach **4.9 km²**
- Each fits its mover: a power line crosses country, an engine does not

<!-- The circle is four minutes at 35 mph in every direction, which is what a Lab 1 buffer would say. The blue shape is four minutes of driving along UGRC's network, at its typical-traffic minutes, from Provo Fire and Rescue Station 21. Nine times the area. Thursday puts a number on that for the whole county. The point to make now: none of the three is "the" distance; each models a different way of moving, and the question picks the model. -->

---

<!-- _class: lead -->

![bg right:55%](images/na-divider-network.jpg)

# Part 1 — What a Network Dataset Is Made Of

---

# Edges and Junctions

![bg right:50% w:98%](images/na-edges-junctions.png)

- An **edge** is a road segment with a **cost** to travel it
- A **junction** is where edges **meet**; a route can only turn at a junction
- The edge's cost here is **minutes**: 0.10 for a short block, 0.55 for a long one
- A network is a **graph**: the geometry draws the map, the graph does the routing

<!-- Lab 11's network, zoomed to about 840 m of Provo streets. Each label is the segment's TravelMinutes (the cheaper direction where they differ). The white circles are the junctions ArcGIS Pro built where segment endpoints coincide. The orange edges are one-way; the arrow shows the direction that costs the normal minutes. Ask: how many ways can you leave the junction in the middle? As many as it has edges, and only those. -->

---

# Connectivity Lives in the Junctions

![bg right:50% w:98%](images/na-overpass.png)

- Two lines **cross on the map**: an interstate over a street
- No **junction** where they cross, so the network **does not connect them**
- Right for an overpass; a disaster at a real intersection that was digitized without a junction
- UGRC's rule: freeways and ramps connect only at their **endpoints**; other streets connect at **any vertex** they share, in one group

<!-- The red X is a place west of Provo where I-15 crosses a surface street; the nearest junction is 88 m away, at the ramp. Connectivity is set per subtype of the Roads class in UGRC's template: subtype 1 (limited access and ramps) end-vertex, subtype 2 (everything else) any-vertex, both in one connectivity group (ConnPolicy 1 and 0 in tools/lab11/ugrc_network_template.xml; Esri's enum is 0 = any vertex, 1 = end vertex). There is no elevation field in this network, so I-15 stays off the street below only because a freeway segment connects at its own ends, and it has no end there. The lesson for any network you build: the junctions are the model; a segment that stops 2 m short of the one it should meet is a wall. -->

---

# Impedance: the Cost of an Edge

![bg right:52% w:98%](images/na-impedance.png)

- An **impedance** is whatever you choose to **minimize**: meters, minutes, dollars, calories
- UGRC's **TravelMinutes**: the segment's length over its posted speed, with surface streets **× 1.5** for signals and congestion
- A local street at a posted 25 mph comes out at **17 mph**; an interstate posted 65 at **54**
- The network carries a second cost, **Length**, in meters

<!-- Medians of TravelMinutes per kilometer by CARTOCODE class over Utah County's 41,460 edges (tools/week12_network_numbers.json, "impedance"). Local and neighborhood streets: 2.24 min/km, which is 27 km/h or 17 mph, against a posted 25: the 1.5 factor. Interstates: 0.69 min/km, 54 mph against 65. UGRC's page calls the method "relatively crude, though effective." That is the right spirit: an impedance is a model, and it is only as good as the decision behind it. The 1.5 factor is the thing to argue about on Thursday, when a fire engine's own speed comes up. -->

---

<!-- _class: quiz -->

# Talk to Your Neighbor

![bg right:40% w:94%](images/na-overpass.png)

A street segment on 300 North stops **2 m short** of the 500 West segment it should meet. Nothing else touches it there. What does the network do at that corner?

<ol type="A">
<li>Snaps the two together, since 2 m is close enough</li>
<li class="correct">Treats it as a dead end: no route can turn from one street onto the other there</li>
<li>Lets routes cross, but charges a turn delay</li>
<li>Connects them, because they look connected on the map</li>
</ol>

* <span class="reveal"></span>

<!-- Two minutes: talk to your neighbor, then a show of hands, then one key press circles the answer. B. Connectivity lives in the junctions, and a junction exists only where the geometry actually meets (an endpoint, or a shared vertex for UGRC's surface streets). A gap of 2 m is a gap; the map draws the corner, the graph does not have it. A and D are the map-reader's intuition; C confuses turns with connectivity. The streets are made up for the question. -->

---

<!-- _class: lead -->

![bg right:55%](images/na-divider-source.jpg)

# Part 2 — Direction, Turns, and Lab 11's Network

---

# One-Way Streets: a Wall or a Price

![bg right:46% w:96%](images/na-edges-junctions.png)

- Every edge has a cost **in each direction**: `F_T_IMP_MIN` along the way it was digitized, `T_F_IMP_MIN` against
- A **restriction** attribute makes the wrong direction **impassable**
- UGRC chose a **cost** instead: the wrong direction is **100 times** the right one
- On Lab 11's longest one-way I-15 segment: **3.04** minutes northbound, **304** the other way

<!-- The two directional fields are the evaluators of TravelMinutes in UGRC's template. 590 of Utah County's edges are one-way (ONEWAY = 1 or 2). A hundredfold cost means a solver goes the wrong way only when nothing else reaches at all, which is a defensible model of an engine with its lights on. A restriction would make it impossible. Both are modeling decisions, and Lab 11's Step 1 has students read the two numbers off I-15 themselves. -->

---

# Turns Cost Time Too

![h:430 center](images/na-turn-delays.png)

<!-- UGRC's network has no turn features, but it carries global turn delays, read from the network template: a left turn from a local street onto a local street adds 30 seconds, a right turn nothing, crossing a major road straight ahead 15 seconds. This is why a fastest route avoids left turns across arterials, and it is one more reason the network's four minutes reach less than a circle's. A network built from raw roads without these has every turn free. Skip if time is short. -->

---

<!-- _class: quiz -->

# Predict First

![bg right:40% w:94%](images/na-impedance.png)

Lab 11's network carries two costs, **TravelMinutes** and **Length**. You route an engine from a Provo station to a Census block **8 km** away, once minimizing each. What happens?

<ol type="A">
<li>The two routes are the same roads, since the roads are the roads</li>
<li class="correct">The fewest-meters route is shorter and slower; the fewest-minutes route is longer and faster</li>
<li>The fewest-minutes route is also the shortest, since fast roads are straight</li>
<li>Neither can be solved: a network has one cost</li>
</ol>

* <span class="reveal"></span>

<!-- Ninety seconds in pairs, a show of hands, then the key press circles the answer. A is the common answer: people picture one road to a place. The answer is B, and the next slide is the measurement. D is the misconception that a network dataset carries one cost; this one carries two, and a travel mode picks which one the solver minimizes. -->

---

# Shortest Is Not Fastest

![bg right:50% w:98%](images/na-shortest-vs-fastest.png)

- Same two points, same network, two impedances
- **Fewest meters**: **9.9 km** through the city grid, **23.4 minutes** at local speeds and turns
- **Fewest minutes**: **15.3 km** down I-15, **15.1 minutes**
- The fast route is **55 % longer** and **8 minutes quicker**
- A fire engine's standard is written in **minutes**, so Lab 11 minimizes minutes

<!-- Solved with Make Route Analysis Layer on Lab 11's network (tools/week12_network_numbers.json, "route"): from Provo Fire and Rescue Station 21 to a populated block 8.1 km away in a straight line. The green route minimizes Length: 9,878 m, and at TravelMinutes it would take 23.37 minutes. The orange route minimizes TravelMinutes: 15,315 m in 15.14 minutes. Nothing about the roads changed; only the question. This is the whole idea of an impedance in one picture. -->

---

# How UGRC Built It

![bg right:40% w:94%](images/na-overpass.png)

1. **Sources**: Roads, one subtype for freeways and ramps, one for the rest
2. **Connectivity**: end-vertex for freeways and ramps, any-vertex for other streets, one group
3. **Elevation**: none, so overpasses rely on freeway endpoints not touching
4. **Attributes**: `TravelMinutes` (default) and `Length`, each with an **evaluator** per direction reading a field
5. **Turns**: global delays by turn type, road class
6. **Build**: ArcGIS Pro walks every segment and writes the junctions

<!-- This is the Catalog pane's network dataset wizard, as UGRC filled it in; it is why Lab 11 ships the network already built. Lab 11's package was made by exporting UGRC's definition as a template, clipping the roads to Utah County, creating the network from the template and building it, so the costs are UGRC's, unchanged. Students see the result in Network Dataset Properties in Step 1. If a student asks "could I build one from a shapefile of roads": yes, and the deck's six steps are the six decisions they would have to make. -->

---

# What Lab 11 Hands You

![h:400](images/na-network-properties.png)

- **Network Dataset Properties** ▸ **Travel Attributes** ▸ **Costs**: `TravelMinutes` in minutes, `Length` in meters
- Each cost is read from a field **along** and **against** the digitized direction

<!-- Lab 11's Figure 1b, from the GUI build (ArcGIS Pro 3.7.1): the clipped network's properties, which Step 1 of the lab has students open. Two costs, no travel modes, no hierarchy (hence the yellow note about turn categories). The evaluators are the point: a one-way street costs its normal minutes along and 100 times that against, which is how UGRC encodes one-way without a restriction. Skippable if time is short; it is on the lab page. -->

---

<!-- _class: quiz -->

# Talk to Your Neighbor

![bg right:40% w:94%](images/na-edges-junctions.png)

A one-way block costs **0.2 minutes** the legal way. The fastest way to a fire is down it the **wrong way**. On Lab 11's network, what does the solver do?

<ol type="A">
<li>Drives the wrong way, because it is the shortest</li>
<li>Never uses that block in that direction</li>
<li class="correct">Goes around, unless every way around takes more than 20 minutes</li>
<li>Adds 100 meters to the route</li>
</ol>

* <span class="reveal"></span>

<!-- Two minutes in pairs, then the key press. C. UGRC encodes one-way as a price, not a wall: the wrong direction costs 100 times the right one, here 0.2 x 100 = 20 minutes, so the solver goes around the block whenever any detour is cheaper than 20 minutes, which in a city is nearly always. B is what a restriction would do, the other choice UGRC could have made. D mixes up the two costs: the hundredfold factor is on TravelMinutes, not on Length. -->

---

<!-- _class: lead -->

![bg right:55%](images/na-divider-service-area.jpg)

# Part 3 — The First Solver: Service Areas

---

# Service Area: What One Station Can Reach

![bg right:50% w:98%](images/nab-one-station-rings.png)

- Spread minutes outward from a **facility** along the edges; stop at the **cutoff**
- Draw a polygon around the reached edges, one per cutoff: **rings**
- From Provo Station 21: **1.5 km²** inside two minutes, **4.9 km²** inside four, **15 km²** inside six
- It is not a circle, because the roads are not

<!-- Solved with Make Service Area Analysis Layer on Lab 11's network from one station, cutoffs 2, 4, 6, 8, rings (tools/week12_network_numbers.json, "one_station"). Within six minutes is the sum of the first three rings, 1.5 + 4.9 + 8.7. Point at the shape: it reaches far along the arterials and barely at all into the neighborhoods with one way in. -->

---

# Service Areas from All 42 Stations

![bg right:50% w:98%](images/nab-service-areas.png)

- Load all **42 stations** as facilities and solve once
- **Dissolve** the overlaps so a block near two stations is counted once
- Within two minutes: **52 km²**; four: **195 km²**; six: **380 km²**; eight: **557 km²**
- The four-minute area is a **string of small shapes** around the stations, which are in the cities

<!-- Lab 11's reference run, cutoffs 2, 4, 6 and 8 solved separately, each dissolved (tools/lab11/check_values.json, "sensitivity"). The areas are what students get in Step 4 for four minutes, and in Step 9 for the others; the deck gives the areas but not the populations outside each, which is what Step 9 asks them to find. Utah Lake in the middle is the gap. -->

---

# The Tools in ArcGIS Pro

<div class="columns">
<div>

<div class="imggrid" style="grid-template-columns: repeat(3, 1fr);">

![h:120](images/nab-icon-make-service-area-analysis-layer.svg)

![h:120](images/nab-icon-add-locations.svg)

![h:120](images/nab-icon-solve.svg)

</div>

1. **Make Service Area Analysis Layer**: the network, the **cutoffs**, the travel direction, how the polygons are drawn. It computes **nothing**
2. **Add Locations**: the stations into the **Facilities** sublayer, each snapped to the nearest edge within the search tolerance
3. **Solve**: fills in the **Polygons** sublayer

</div>
<div>

- The result is an **analysis layer** in the map, not a feature class
- In a model, **Select Data** pulls the Polygons out and **Copy Features** keeps them
- The same three steps run every solver: a Closest Facility or Location-Allocation layer has its own sublayers

</div>
</div>

<!-- The icons are Lab 11's own. The one mistake everyone makes once: run the first two and look for polygons. Nothing exists until Solve. In ArcGIS Pro 3.7.1 the first tool's parameters are Network Data Source and Layer Name; the network ships without named travel modes, so Travel Mode shows Custom and the layer uses TravelMinutes, the default cost. -->

---

# Make Service Area Analysis Layer

![bg right:60% w:96%](images/nab-dlg-make-service-area-callouts.png)

- Sets up the question: **which network**, **which way**, **how many minutes**
- How the answer is **drawn**: polygons, dissolved, in rings
- It computes **nothing** yet

<!-- The red callouts are drawn beside the untouched capture by tools/week12_dialog_callouts.py. Lab 11's own Figure 2 from the GUI build (ArcGIS Pro 3.7.1), filled in as Step 2 of the lab says. Travel Mode is empty because the network ships without named travel modes, so the layer uses the default cost, TravelMinutes. Cutoffs is a list, one value per row: add a row with 8 and you get two rings. Dissolve matters for counting: without it, overlapping station areas stack and a block near two stations sits inside two polygons. -->

---

# Add Locations

![bg right:58% w:96%](images/nab-dlg-add-locations-callouts.png)

- Loads points into **one sublayer** of the analysis layer
- For a service area, the stations are the **Facilities**
- Each station is **snapped** to the nearest street within the search tolerance
- Then **Solve**, and the Polygons sublayer fills in

<!-- The red callouts are drawn beside the untouched capture by tools/week12_dialog_callouts.py. Lab 11's own Figure 3. The search tolerance (5000 m, the default) is under Advanced. The check in the lab: the Facilities table has 42 rows, every Status OK. Solve has almost no parameters (the analysis layer in, the same layer out, solved), so it has no dialog slide of its own. -->

---

<!-- _class: quiz -->

# Talk to Your Neighbor

![bg right:40% w:94%](images/nab-one-station-rings.png)

You run **Make Service Area Analysis Layer** and **Add Locations**. All 42 stations are located. The **Polygons** sublayer is **empty**. Why?

<ol type="A">
<li>A cutoff of 4 minutes is too small to draw</li>
<li>Travel Mode was left empty</li>
<li class="correct">Solve has not run yet</li>
<li>The stations had to go into Barriers, not Facilities</li>
</ol>

* <span class="reveal"></span>

<!-- Two minutes in pairs, then the key press. C: the first two tools set up the question and load the stations; nothing is computed until Solve. Everyone makes this mistake once. B is a fair worry, but an empty Travel Mode on this network just means the default cost, TravelMinutes, runs. D is backwards: barriers are places a route may not go. -->

---

<!-- _class: activity -->

# Final Thoughts

<div class="columns" style="grid-template-columns: 1.7fr 1fr; font-size: 0.74em;">
<div>

**Quiz: Along the Roads.** Five questions on junctions and connectivity, one-way streets as a cost, two impedances, UGRC's 1.5 factor, and which distance belongs to a fire engine. **Scan the code**, or open the link under it.

- A quick check that today's material made sense
- Thursday builds on the two-impedance question

**Before next class**

- **Lab 11 — Fire Response Coverage** — due **Saturday 11:59 pm**: [assignments/lab-11](https://byu-hydroinformatics.github.io/ce414-gis-applications/assignments/lab-11/)
- Thursday: closest facility, location-allocation, and the rest of Lab 11's model in ArcGIS Pro
- Office hours: [calendly.com/dan-ames/office-hours](https://calendly.com/dan-ames/office-hours)

</div>
<div>

![w:300 center](images/quiz-networks-qr.png)

<span style="font-size: 0.45em; color: #4a5568;">byu-hydroinformatics.github.io/ce414-gis-applications/quizzes/networks/</span>

</div>
</div>

<!-- Four minutes, in pairs. If the room has no signal, put the URL on the board. -->

<!-- Deck written October 10, 2026, new for the course (no source PowerPoint). Figures and numbers: tools/week12_network_figures.py from Lab 11's package and reference run (tools/lab11/). Network facts (connectivity by subtype, evaluators, global turn delays, no elevation model) are read from UGRC's network template, tools/lab11/ugrc_network_template.xml. Owed: a real capture of Network Dataset Properties from the Lab 11 GUI build. -->
