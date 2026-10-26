---
marp: true
theme: ce414
paginate: true
footer: "CE 414 · Week 9 — Interpolation"
---

<!-- _class: lead -->
<!-- _paginate: skip -->

![bg right:45% w:95%](images/ip-surface-3d-kriged.png)

![w:110](../theme/images/byu-medallion.svg)

# Sampling and Interpolation

## Nearest Neighbor and IDW

CE 414 Engineering Applications of GIS
Civil & Construction Engineering
Brigham Young University
Dr. Dan Ames

<!-- Tuesday of Week 9: sampling design, then the two interpolators that weight points by a rule you choose, nearest neighbor (Thiessen) and IDW. Thursday is kriging, which lets the data choose the weights, then how to measure a surface's error, and Lab 8. Slides marked optional in these notes can be skipped as time requires. The surface on the right is where Thursday ends up: a kriged surface built from a scatter of measured points. -->

<!-- stamp:begin -->
<!-- _footer: '<span>CE 414 · Week 9 — Interpolation<span class="updated">Last Updated: 2026-10-25</span></span><span>© 2026 Daniel P. Ames · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></span>' -->
<!-- stamp:end -->

---

# Today's Goals

![bg right:30% w:90%](images/ip-linear-interpolation-equation.png)

By the end of class you should be able to:

- Explain why we **sample** instead of measuring everywhere
- Compare four **sampling designs** and say when each is appropriate
- Build a **Thiessen** (nearest neighbor) surface, by hand and in ArcGIS Pro
- Compute an **IDW** estimate and say what its **exponent** does
- Say which methods give the **measured values back**

Thursday: **kriging**, how wrong a surface is, and **Lab 8**

<!-- Everything on the right-hand figure is the whole idea in miniature: an unknown value y at position x, estimated as a weighted blend of two known values. Every method this week is a more elaborate version of that one picture. That figure comes back several times on purpose. -->

---

<!-- _class: activity -->

<style scoped>
.ip-kicker { display: block; font-size: 0.7em; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: #e8792b; margin-bottom: -0.3em; }
.ip-text { padding-right: 530px; font-size: 0.9em; }
.ip-stack { position: absolute; right: 50px; top: 40px; width: 551px; height: 640px; }
.ip-stack img { position: absolute; left: 0; top: 0; width: 551px; height: 640px; }
.ip-stack ul { list-style: none; margin: 0; padding: 0; }
.ip-stack li { margin: 0; }
li[data-bespoke-marp-fragment="active"] .ip-hint { animation: tryit-pop 0.45s ease-out both; }
</style>

<div class="ip-text">

<span class="ip-kicker">Work with a neighbor</span>

# In Class Activity: What Is the Temperature in Provo?

- Let's assume you only know the air temperature in three Utah cities: **Moab**, **American Fork**, and **Cedar City**
- Look up the current air temperature in each on weather.com or an equivalent site
- From those three, **estimate the current temperature in Provo**
- Write down your answer and the method you used to get it
- Upload your answer and your method to Learning Suite

</div>

<div class="ip-stack">

![](images/ip-utah-activity-map.png)

* <img class="ip-hint" src="images/ip-utah-activity-map-distances.png" alt="Straight-line distances from Provo: 19 km to American Fork, 259 km to Moab, 311 km to Cedar City">

</div>

<!-- The click is a hint for anyone stuck: straight-line (great-circle) distances from Provo, as the crow flies rather than by road, between the UGRC municipal-boundary centroids: American Fork 19 km, Moab 259 km, Cedar City 311 km (tools/week09_tuesday_figures.py). -->

<!-- Give them three or four minutes. Collect several answers and, more importantly, several rules: nearest city, plain average, distance-weighted average, adjust for elevation. Those four answers are Thiessen, a global mean, IDW, and a trend surface. Name them now, then spend the rest of the session making each one precise. -->

<!-- Map: Utah from UGRC's state boundary, cities at the centroids of their UGRC municipal boundaries (tools/week08_interpolation_figures.py). Point out before anyone answers: American Fork is about 20 km from Provo, while Moab and Cedar City are each more than 250 km away. The map is why nearest-city and distance-weighted answers win. -->

---

# Interpolation

<img class="ip-geo" src="images/ip-soil-cross-section-cartoon.jpg" alt="Cartoon geologist standing on a cross-section of soil layers">

**Interpolation** is a procedure to predict values of an attribute at unsampled points within the region that was sampled.

<div class="columns">
<div>

**Why?** You cannot measure every location:

- Time
- Money
- Physically or legally impossible

</div>
<div>

**Examples:**

- Temperature
- Acid rain deposition
- Soil characteristics
- Mining: gold deposits

</div>
</div>

Also used when **changing cell size**, when data are **missing or unsuitable**, or for a **past date** (for example, temperature).

<style scoped>
section { padding-right: 440px; }
.ip-geo { position: absolute; right: 50px; top: 70px; width: 370px; }
.ip-joke ul { list-style: none; margin: 0; padding: 0; }
.ip-joke li { position: absolute; left: 860px; width: 370px; margin: 0; font-size: 0.72em; line-height: 1.3; text-align: center; }
.ip-joke li:nth-child(1) { top: 470px; font-weight: 700; color: #002e5d; }
.ip-joke li:nth-child(2) { top: 512px; color: #e8792b; font-weight: 700; }
li[data-bespoke-marp-fragment="active"] .ip-pop { display: inline-block; animation: tryit-pop 0.45s ease-out both; }
</style>

<div class="ip-joke">

* <span class="ip-pop">Why is the geologist sad?</span>
* <span class="ip-pop">To measure every spot, he'd have to dig up the whole site, and then there'd be nothing left to measure.</span>

</div>

<!-- Two clicks: the question, then the punch line. It is the definition's "why" in one line: measuring everywhere is not just slow and expensive, it can destroy the thing being measured (a soil core, a gold deposit). -->

<!-- Note the phrase "within the region sampled." Predicting outside that region is extrapolation, and every method here degrades badly when you ask it to extrapolate. Fixed the source's "Can not" to "cannot." -->

---

# Sampling and Interpolation: Growing Up

<style scoped>
section > h1 { position: absolute; top: 52px; left: 70px; right: 70px; margin: 0; }
.gr ul { list-style: none; margin: 0; padding: 0; }
.gr li { margin: 0; }
.gr-cartoon { position: absolute; left: 70px; top: 118px; width: 300px; height: 300px; border-radius: 10px; }
.gr-layer { position: absolute; left: 440px; top: 112px; width: 790px; height: 489px; }
.gr-say { position: absolute; left: 70px; width: 350px; font-size: 0.6em; line-height: 1.3; }
.gr-say strong { color: #002e5d; }
.s0 { top: 432px; } .s1 { top: 490px; } .s2 { top: 548px; } .s3 { top: 628px; }
.s1 strong, .s2 strong { color: #e8792b; }
li[data-bespoke-marp-fragment="active"] .gr-pop { animation: tryit-pop 0.45s ease-out both; }
</style>

<img class="gr-cartoon" src="images/ip-growth-wall-cartoon.jpg" alt="Cartoon of a mom marking her daughter's height on a door frame">

<img class="gr-layer" src="images/ip-growth-points.png" alt="Her height on each birthday from 1 to 18">

<span class="gr-say s0"><strong>Sampling:</strong> Mom marks her height on the wall every birthday, ages 1 to 18.</span>

<div class="gr">

* <img class="gr-layer gr-pop" src="images/ip-growth-question.png" alt=""><span class="gr-say s1 gr-pop"><strong>How tall was she at 12½?</strong> Nobody marked the wall that day.</span>
* <img class="gr-layer gr-pop" src="images/ip-growth-answer.png" alt=""><span class="gr-say s2 gr-pop"><strong>Interpolate</strong> between her 12th and 13th birthdays: 63 + (65½ − 63) × (12½ − 12) ⁄ (13 − 12) ≈ 64¼ in</span>
* <img class="gr-layer gr-pop" src="images/ip-growth-line.png" alt=""><span class="gr-say s3 gr-pop"><strong>Every month?</strong> Interpolate each one and connect them: the whole growth line.</span>

</div>

<!-- Three clicks. A girl measured on every birthday is a sample; the wall marks are her data. Click 1: nobody measured her at 12 and a half, so we need an estimate. Click 2: the two-point equation from Today's Goals, with her 12th (5 ft 3 in) and 13th (5 ft 5.5 in) birthday heights: 63 + 2.5 x 0.5 = 64.25 in, about 5 ft 4 in. Click 3: do that for every month and join the dots and you have the whole curve. That is the entire week in one dimension: the birthdays are the sampling design, the line is the interpolated surface. Ask whether a straight line between birthdays is right during her growth spurt (11 to 13), which is the question every method today answers differently. The girl is made up: her heights follow the shape of the CDC (2000) stature-for-age median for girls, scaled to finish at 5 ft 8 in and rounded to the half inch (tools/week09_tuesday_figures.py). The cartoon was generated with OpenAI gpt-image-2, October 25, 2026. -->

---

# From a Line to a Surface

<style scoped>
section > h1 { position: absolute; top: 52px; left: 70px; right: 70px; margin: 0; }
.ls ul { list-style: none; margin: 0; padding: 0; }
.ls li { margin: 0; }
.ls-small { position: absolute; left: 60px; top: 130px; width: 440px; height: 305px; }
.ls-map { position: absolute; left: 530px; top: 112px; width: 700px; height: 414px; }
.ls-cap { position: absolute; font-size: 0.6em; line-height: 1.3; }
.ls-cap strong { color: #002e5d; }
.c1 { left: 70px; top: 445px; width: 420px; }
.c2 { left: 545px; top: 532px; width: 680px; }
.c2b { left: 545px; top: 561px; width: 680px; color: #e8792b; font-weight: 700; }
.d1 { left: 70px; top: 600px; width: 1140px; } .d2 { left: 70px; top: 636px; width: 1140px; }
.ls-ask { position: absolute; left: 70px; top: 505px; width: 430px; font-size: 0.66em; }
.ls-card { position: absolute; left: 560px; top: 130px; width: 640px; display: block; background: #fff; border: 3px solid #1f4e8c; border-radius: 12px; box-shadow: 0 6px 18px rgba(0,0,0,0.18); padding: 0.5em 0.9em; font-size: 0.66em; line-height: 1.4; }
.ls-card strong { color: #1f4e8c; }
li[data-bespoke-marp-fragment="active"] .ls-pop { animation: tryit-pop 0.45s ease-out both; }
</style>

<img class="ls-small" src="images/ip-growth-small.png" alt="Her heights on each birthday joined into a growth line">
<img class="ls-map" src="images/ip-temp-stations.png" alt="Sixteen temperature stations on an empty grid">

<span class="ls-cap c1"><strong>1-D:</strong> her height on every birthday → the whole growth line</span>
<span class="ls-cap c2"><strong>2-D:</strong> the temperature at a few stations →</span>

<div class="ls">

* <img class="ls-map ls-pop" src="images/ip-temp-surface.png" alt="The same stations on a fully interpolated temperature grid"><span class="ls-cap c2b ls-pop">the whole grid, every cell interpolated</span>
* <span class="ls-cap d1 ls-pop"><strong>Spatial sampling:</strong> gather observations that represent the spatial distribution of a variable of interest</span>
* <span class="ls-cap d2 ls-pop"><strong>Interpolation:</strong> use those samples to predict that variable at every unsampled location</span>
* <span class="infobox ls-ask ls-pop">What other classes have you had where you had to <strong>interpolate</strong> a value?</span>
* <span class="ls-card ls-pop"><strong>Thermodynamics:</strong> a property between two rows of the steam tables<br><strong>Fluids:</strong> a friction factor read between curves on the Moody diagram<br><strong>Hydrology:</strong> a rainfall depth between durations on an IDF curve<br><strong>Geomatics:</strong> an elevation between two contour lines<br><strong>Geotechnical:</strong> the soil layers between two borings<br><strong>Structures:</strong> a design value between rows of a code table</span>

</div>

<!-- The map starts empty except for the stations: a thermometer reading at each is the birthday mark on the wall. Click 1 fills every cell, which is the growth line in two dimensions. Clicks 2 and 3 are the two definitions the rest of the session hangs on. The two halves are inseparable: a brilliant interpolator cannot rescue a bad sample, and a beautiful sample is useless until you interpolate it. Click 4 asks the class, and click 5 shows answers once they have had a go. Most examples on the card are one-dimensional, like the growth chart; two are already spatial: an elevation between contours and the ground between borings. The temperatures are made up (16 stations, filled by IDW with power 2, tools/week09_tuesday_figures.py); IDW itself comes later today. -->

---

<!-- _class: lead -->

![bg right:55%](images/ip-divider-gold.jpg)

# Scenario: Distribution of a Mineral Deposit

## Gold nuggets under a landscape

<!-- The next four slides all use the same made-up scenario: gold is distributed through the subsurface, you cannot dig everywhere, so you choose where to dig. Keep the scenario fixed and change only the sampling design so the comparison is fair. -->

---

# The Scenario

The map on the left is the real, fully known gold grade. In practice you never see it — you only get the handful of points you choose to sample.

<div class="columns">
<div>

![h:420 center](images/ip-gold-grade.png)

</div>
<div>

![w:290 center](images/ip-gold-deposit-cartoon.jpg)

**Gold nuggets…**

</div>
</div>

<!-- Left: the true gold grade in grams per tonne, made up for this scenario (tools/week09_tuesday_figures.py): a northeast-trending vein, a dozen ore pods of different sizes, and background variation. Right: the cartoon reason we care. The next four slides sample this same map. The whole point of the next four slides is that you must commit to a sampling design before you know what the surface looks like. -->

---

# Systematic Sampling Pattern

![bg right:38% w:80%](images/ip-gold-systematic.png)

- Samples spaced uniformly at fixed X, Y intervals
- Parallel lines

**Advantages**

- Easy to understand and to plan

**Disadvantages**

- All areas receive the same attention
- Difficult to stay on the lines in the field
- May be **biased** if the landscape has a matching pattern

<!-- Systematic is the default people reach for. The bias failure mode is worth naming: if the terrain has ridges at roughly your sample spacing, a grid can land on ridge tops every time and you will never see the valleys. -->

---

# Random Sampling

![bg right:38% w:80%](images/ip-gold-random.png)

- Select random points

**Advantages**

- Less biased — unlikely to match a pattern in the landscape

**Disadvantages**

- Does nothing to distribute samples toward areas of high variation
- Difficult to explain; the locations of points may themselves be a problem

<!-- "The location of points may be a problem" is a field-work concern: random points land in rivers, on private land, and halfway up cliffs. Ask the class what they would do with a point they cannot reach — moving it quietly destroys the randomness that justified the design. -->

---

# Cluster Sampling

![bg right:38% w:80%](images/ip-gold-cluster.png)

- Cluster centers are established, either randomly or systematically
- Samples are arranged around each center

**Advantages**

- Reduced travel time
- Less costly

**Disadvantages**

- Less representative sampling

<!-- Cluster sampling is the design that budgets produce. It buys many observations cheaply, but the observations are not independent: points inside one cluster tell you nearly the same thing. -->

<!-- Optional: skip if time is short. Systematic and random carry the main contrast. -->

---

# Adaptive Sampling

![bg right:38% w:80%](images/ip-gold-adaptive.png)

- Higher sampling density where the feature of interest is more variable
- Requires some method of estimating feature variation

**Advantages**

- Often efficient: large homogeneous areas need few samples, reserving effort for areas of higher spatial variation

**Disadvantages**

- Without a way to identify where the feature varies most, you need several visits; sample density cannot be changed on the spot

<!-- Adaptive is the best design and the hardest to execute, because it needs prior knowledge of the thing you are going out to measure. In practice it means a coarse first pass followed by targeted infill. Fixed the source's "can not" to "cannot." -->

<!-- TODO(instructor): decide how much of sampling design belongs in CE 414 versus the statistics prerequisite, and whether to add a slide on sample size and spacing. -->

<!-- Optional: skip if time is short. -->

---

<!-- _class: quiz -->

# Class Vote: Which Sampling Design Works Best Here?

![bg right:52% h:95%](images/ip-gold-compare.png)

**The true gold grade:**

![h:360 center](images/ip-gold-grade.png)

<!-- Vote now, while the four designs are fresh, and before discussing any of them. Each design has the same 96 points on the same map. The interesting argument is between adaptive and random: adaptive (a coarse first pass, then infill where the grade changes fastest) puts points where the surface changes fastest, which is where interpolation errors are largest, but it needs prior knowledge that a real project usually does not have. There is no answer key here on purpose. -->

---

<!-- _class: lead -->

![bg right:55%](images/ip-divider-surface.jpg)

# From Samples to a Surface

## Gather observations that represent the spatial distribution of a variable — then predict that variable everywhere else

<!-- This repeats the framing from earlier in the session, which is exactly what the source deck did: it restated the sampling/interpolation definition slide as the transition out of sampling designs and into interpolation methods. Everything from here on is the second half. -->

---

# Interpolation: Many Methods

![bg right:28% w:90%](images/ip-linear-interpolation-equation.png)

- There are **many different methods**
- All of them use the **location** and the **value** at sampling locations to estimate the variable of interest at unmeasured locations
- Methods differ in **weighting** and in the **number of observations** used
- Each method produces **different results**, even with the same data
- There is **no best method** for every application
- Accuracy is often judged by **withheld sample points** — the difference between the measured and the interpolated values

<!-- The last bullet is the honest one and it is where the rest of a career in this material lives: hold points back, interpolate without them, and compare. Everything else on this slide is bookkeeping. -->

<!-- Thursday makes the last bullet concrete: a six-methods test with 60 points held back, RMSE, and checkpoints. -->

---

# Interpolation: Rasters and Contours

![bg right:28% w:90%](images/ip-linear-interpolation-equation.png)

Usually used for **point-to-raster** data. Some methods instead produce **contour lines** — vector lines of uniform value.

**Raster surface**

- Values are measured at a set of sample points
- Raster layer boundaries and cell dimensions are established
- The interpolation method estimates the value for the center of each unmeasured grid cell

**Contour lines: an iterative process**

- Estimate points of a given value (say 10 °C) and connect them into a line, then estimate the next value (say 20 °C) — lines of different values may not cross

<!-- Point out that the raster path and the contour path are two renderings of the same estimated surface, not two different analyses. In practice you interpolate to a raster and derive contours from it. -->

<!-- Optional: skip if time is short. Lab 8 works only in rasters. -->

---

# Example Base

<div class="columns" style="align-items:start">
<div>

![h:430 center](images/ip-contour-map-base.png)

**Elevation contours** — the true surface

</div>
<div>

![h:430 center](images/ip-sample-points-values.png)

**Sampled locations and values**

</div>
</div>

<!-- This pair is the reference for the rest of the session and for kriging on Thursday. Left is the truth, which in a real project you never have. Right is everything the interpolator gets to see. Every method that follows is judged by how close it comes to the left panel using only the right panel. -->

---

# Thiessen Polygons: The Method

<div class="columns" style="grid-template-columns: 1fr 1.15fr; align-items:start">
<div>

- Each cell takes the value at the **nearest sample location**
- Only **one point** is used; also called **nearest sample** or **nearest neighbor**
- The conceptually simplest method

**Building one by hand**

1. Connect each point to its nearest neighbors
2. Draw the **perpendicular bisector** of each line
3. Join the bisectors; the polygon takes the value of its center point

</div>
<div>

![w:600 center](images/ip-thiessen-construction.png)

</div>
</div>

<!-- Thiessen is the zero-weighting case: the nearest point gets a weight of one and everything else gets zero. Worth saying out loud, because it makes the later methods feel like refinements rather than unrelated tricks. Walk the four panels in order. The key geometric fact: every location inside a polygon is closer to that polygon's sample point than to any other. In ArcGIS Pro this is a single tool (two slides on); students should still be able to draw it by hand on an exam. -->

---

# Thiessen Polygons: The Result

<div class="columns" style="grid-template-columns: 1fr 1fr 1.25fr; align-items:start; font-size: 0.8em;">
<div>

![h:390 center](images/ip-sample-points-values.png)

**Sampled locations and values**

</div>
<div>

![h:390 center](images/ip-thiessen-polygons-map.png)

**Thiessen polygons**

</div>
<div>

![w:100%](images/ip-surface-3d-thiessen.png)

**The surface:** flat inside each polygon, a jump at every edge

</div>
</div>

<!-- Same points, now partitioned, then shown in 3D. Note the dense cluster on the right of the map: where samples crowd together the polygons become tiny slivers, and where samples are sparse a single polygon can cover a large area with one measured value. The 3D view makes the defining property obvious: the surface is flat inside each polygon and jumps discontinuously at every boundary. That is fine for a categorical variable such as soil type, and wrong for elevation or temperature. Merged October 25, 2026 from four slides (concept, construction, points to polygons, 3D surface). -->

---

# Thiessen: Trade-offs

![bg right:28% w:90%](images/ip-linear-interpolation-equation.png)

**Advantages**

- Ease of application
- Appropriate for **discrete** (categorical) variables

**Disadvantages**

- Accuracy depends largely on **sampling density**
- Boundaries are often odd-shaped at transitions
- **Continuous** variables are often not well represented

<!-- Tie the disadvantages back to the 3D view they just saw. The odd-shaped boundaries and the step discontinuities are the same fact seen twice. -->

---

# Thiessen Polygons in ArcGIS Pro

<div class="columns" style="align-items:start">
<div>

![w:470 center](images/ip-pro-thiessen.png)

**Create Thiessen Polygons**: Output Fields **All fields**

</div>
<div>

![h:390 center](images/ip-pro-polygon-to-raster.png)

**Polygon to Raster**: Value field = the **sampled value**

</div>
</div>

<!-- Both captures are from the Lab 8 model in ArcGIS Pro 3.7.1, where RASTERVALU is the field holding each sample's elevation. Two defaults give a surface with no elevations in it and no error: Create Thiessen Polygons opens at Output Fields "Only feature ID", which drops the sampled value, and Polygon to Raster fills Value field with OBJECTID, which makes a surface of polygon numbers. Create Thiessen Polygons needs an Advanced license; the lab machines have it. -->

---

# Inverse Distance Weighted (IDW): The Method

<div class="columns" style="grid-template-columns: 1.2fr 1fr; align-items:start">
<div>

- Estimates an unknown point from the **values of** and **distances to** nearby known points
- Each known point's weight is **inverse to its distance**: the farther away, the less it counts
- $Z_i$ is a known value, $d_{ij}$ the distance to it, $Z_j$ the unknown point
- $n$ is a user-selected **exponent**, often 1, 2, or 3
- Any number of points may be used, up to all of them; typically 3 or more

</div>
<div>

![w:440 center](images/ip-idw-equation.png)

</div>
</div>

<!-- IDW is the first method that uses more than one point and treats them unequally. The weights follow a rule you choose; on Thursday kriging takes them from the data. Read the equation as a weighted average whose weights are 1/d^n, normalized by their own sum so they add to one. That normalization is the denominator. If n = 0 every weight is equal and IDW collapses to a plain local mean. Merged October 25, 2026 from the concept and equation slides. -->

---

# IDW: A Worked Example

![h:500 center](images/ip-idw-worked-example.png)

<!-- Walk the arithmetic on the figure: three known points at distances 4, 2 and 6 with values 50, 30 and 52, weights of 1/4, 1/2 and 1/6, and an estimate of 34. This is a linear IDW, exponent one. Have the class redo it with the exponent squared and watch the answer move toward the nearest point. -->

---

# IDW: The Results

<div class="columns" style="grid-template-columns: 1.35fr 1fr; align-items:start; font-size: 0.78em;">
<div>

![w:100%](images/ip-idw-squared-6-vs-12.png)

Exponent 2: **6** nearest points (left) vs **12** (right)

</div>
<div>

![w:80% center](images/ip-surface-3d-idw.png)

- A larger exponent **n** gives the **closer points** more influence
- **More sample points** give a **smoother** surface
- Continuous, but with **bull's-eyes** around isolated points

</div>
</div>

<!-- These are two of the choices Lab 8 varies: the power (2, then 1, 3 and each student's own) and the number of sample points (250, 2,500, 10,000). The lab holds the neighbor count at 12. Left figure: both panels use exponent two; more neighbors smooths the surface without removing the bull's-eyes, because the exponent, not the neighbor count, is what concentrates weight on the nearest point. As n grows without bound, IDW converges on the Thiessen result: the nearest point takes all the weight. Right: compare against the Thiessen surface and keep both in mind for Thursday's kriged surface. IDW is continuous (no cliffs at polygon edges) but not smooth: the surface has a kink at every sample point, and each sample sits at a local peak or pit. Merged October 25, 2026 from "What Changes the IDW Surface", the two IDW comparison figures (the linear 6-point one was dropped) and the 3D surface. -->

---

# IDW in ArcGIS Pro

![bg right:42% h:84%](images/ie-idw.png)

- **Spatial Analyst ▸ IDW** (3D Analyst and Geostatistical Analyst have their own)
- **Z value field**: the sampled value
- **Power**: the exponent *n*; 2 by default
- **Search radius**: **Variable**, the **12** nearest points by default
- **Output cell size**: set it, or IDW picks one from the points

<!-- The capture is the IDW tool inside the Lab 8 model, with Power exposed as a model parameter (the IDW Power oval). Lab 8 also sets Cell Size, Snap Raster and Extent as environments so every surface lands on the same 30 m cells as the true DEM; without them nothing reports an error, but Thursday's subtraction compares cells that do not line up. -->

---

# Trend Surfaces and Splines

<div class="columns" style="grid-template-columns: 1fr 1fr; align-items:start; font-size: 0.8em;">
<div>

**Trend surface:** one polynomial fit through **all** the points by regression

![w:380](images/ip-trend-surface-equation.png)

![h:300 center](images/ip-trend-surface-result.png)

The regional slope, with the local detail gone

</div>
<div>

**Spline:** joined polynomial pieces, bent to pass **through** the points, like a drafter's flexible ruler

![h:300 center](images/ip-spline-result.png)

The smoothest-looking result, but it can **overshoot** between distant points

</div>
</div>

<!-- Both fit polynomials; the difference is reach. In the trend equation the a terms are regression coefficients and the equation is second order. Trend surface is regression, not local interpolation: every sample point influences every part of the surface, which is why its result looks nothing like the original (the figure is a third-order surface). A spline is built from local polynomial pieces joined smoothly, and is forced through the measured points; it gives the smoothest-looking result in this deck, which is not the same as the most accurate: the surface can overshoot well past the range of the measured values between widely spaced points. Trend surfaces are not in Lab 8; Lab 9 next week uses a spline in one run. Merged October 25, 2026 from two slides. -->

---

# Does the Surface Give the Points Back?

![bg right:28% w:90%](images/ip-linear-interpolation-equation.png)

Interpolate, then read the surface **at the sample points**:

- **Thiessen**: yes — the nearest point *is* the sample
- **IDW**: yes — at distance 0 the sample takes all the weight
- **Spline**: yes, or very nearly — it is built to pass through the points
- **Trend surface**: **no** — one polynomial cannot pass through every point

A method that returns the samples is **exact**. Thursday: is **kriging**?

<!-- The self-check quiz has an item on exactly this, and it splits the room: IDW surfaces look averaged, so people expect IDW to be the non-exact one. At a sample location the distance is zero, the weight 1/d^n is unbounded, and the sample's own value comes back. In the six-methods test Thursday shows (ArcGIS Pro, 150 samples, tools/week08_interpolation_figures.py): Thiessen and IDW give the sample values back exactly, the regularized spline is off by 0.01 m on average, and the 2nd-order trend misses by 166 m on average. Fixed-radius averaging was removed from this deck October 25, 2026 (not used in practice or in Lab 8). -->

---

# Thursday: Kriging

![bg right:45% w:96%](images/ip-surface-3d-kriged.png)

- Thiessen and IDW weight the points by a **rule you choose**
- **Kriging** measures how fast similarity fades with distance, then sets the weights **from the data**
- Then: **how wrong** is each surface, in meters?
- And **Lab 8**: rebuild Y Mountain three ways and measure the error

<!-- The surface is the kriged version of the same example points, also the title image. Set it beside the Thiessen and IDW surfaces: stepped, kinked, smooth. -->

---

<!-- _class: activity -->

# Final Thoughts

<div class="columns" style="grid-template-columns: 1.7fr 1fr; font-size: 0.74em;">
<div>

**Quiz: Points Into Surfaces.** Seven items, one or more on each of today's goals: why we sample, the four designs, Thiessen, the IDW exponent, and which methods give the points back. **Scan the code**, or open the link under it.

- Not graded, nothing recorded: a quick check that today's material made sense
- The **exponent** and the **number of points** are two of the choices you test in Lab 8

**Before next class**

- **Reading:** Chapter 12 of *GIS Fundamentals* (Sampling and Interpolation)
- **Quiz 7**, open book, on Learning Suite, due **Saturday 11:59 pm**
- [Lab 8 — Interpolation Explorer](https://byu-hydroinformatics.github.io/ce414-gis-applications/assignments/lab-08/) is introduced Thursday and due **Saturday 11:59 pm**
- Office hours: [calendly.com/dan-ames/office-hours](https://calendly.com/dan-ames/office-hours)

</div>
<div>

![w:300 center](images/quiz-interpolation-qr.png)

<span style="font-size: 0.45em; color: #4a5568;">byu-hydroinformatics.github.io/ce414-gis-applications/quizzes/interpolation/</span>

</div>
</div>

<!-- The seven items follow Today's Goals in order (the first two, on why we sample and on adaptive sampling, were added October 25, 2026 so every goal is tested). Five minutes, in pairs, then a show of hands on the one that splits the room: the item asking which method cannot return the measured values unchanged. Most of the room expects IDW to be the non-exact one because its surfaces look averaged, but at a sample location the nearest point is that sample itself, so IDW gives the measurement back; the trend surface is the one that misses, because one polynomial cannot pass through every point. If the room has no signal, put the URL on the board; the items read aloud just as well. -->

<!-- Conversion notes: source "CE 414 Week 8 - Interpolation.pptx" (48 slides), converted September 3, 2026; the spelling fixes are in git history. Split October 20, 2026: kriging, the six-methods comparison, the exactness test, the method vote and the ArcGIS Pro tool table moved to Thursday (interpolation-explorer.md); sampling, Thiessen and IDW stay here, with new ArcGIS Pro slides from the Lab 8 captures. Figures: tools/week08_interpolation_figures.py. -->
