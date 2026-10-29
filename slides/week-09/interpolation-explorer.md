---
marp: true
theme: ce414
paginate: true
footer: "CE 414 · Week 9 — Kriging and Interpolation Error"
style: |
  strong { color: #0062b8; }
---

<!-- _class: lead -->
<!-- _paginate: skip -->

![bg right:45% w:96%](images/ie-example-baseline.png)

![w:110](../theme/images/byu-medallion.svg)

# Kriging and Interpolation Error

## Which Surface to Trust — and Lab 8

CE 414 Engineering Applications of GIS
Civil & Construction Engineering
Brigham Young University
Dr. Dan Ames

<!-- Thursday of Week 9. Tuesday built surfaces with weights from a rule you choose: Thiessen and IDW. Today starts with kriging, which takes its weights from the data, then asks how wrong each surface is and which one to trust. Then Lab 8, which does exactly this on Y Mountain with all three methods. The title image is the Lab 8 example baseline sheet: the true DEM and three rebuilds from the same 2,500 points, with their error maps underneath. -->

<!-- stamp:begin -->
<!-- _footer: '<span>CE 414 · Week 9 — Kriging and Interpolation Error<span class="updated">Last Updated: 2026-10-28</span></span><span>© 2026 Daniel P. Ames · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></span>' -->
<!-- stamp:end -->

---

# Today's Goals

![bg right:42% w:96%](images/ie-profile.svg)

By the end of class you should be able to:

- Say why **closer** points count more, and what the **nugget**, **range** and **sill** do to a kriged surface
- Compute an **error raster** and say what its **sign** means
- Reduce the error to one number, the **RMSE**, and compute it in ArcGIS Pro
- Say which surface to **trust**, and why the answer **depends**
- Say what **Lab 8** asks for, and how you will know you are right

<!-- The profile on the right is one row of cells across the Lab 8 study area: the truth and the three rebuilds from 250 points. Thiessen steps, IDW sags, kriging smooths the peak off. The second half of today is a way of putting a number on the gaps between those lines. Testing whether a ranking survives a change is Lab 8 Step 8; Part 4 previews it. -->

---
<!-- _class: lead -->

![bg right:55%](images/ip-divider-kriging.jpg)

# Part 1 — Kriging

## Closer in space, closer in value

<!-- Tuesday's methods weight points by a rule you choose: nearest only, or 1/d^n. Kriging first measures how similarity fades with distance, from the samples themselves, and takes its weights from that. Part 1 was rebuilt October 26, 2026 for students who will run the tool rather than compute kriging by hand: Tuesday's Provo worksheet, a neighbor test, the curve in plain words, then what each setting does. The lag-distance, autocorrelation, semivariance-equation and decomposition slides were cut. October 28, 2026: two more neighbor tests (no pattern, a regional trend), a slide that builds the semivariogram one bin at a time with its equation, and the fit split onto its own slide. -->

---

# Remember Provo?

<style scoped>
section > h1 { position: absolute; top: 52px; left: 70px; right: 70px; margin: 0; }
.rp-text { position: absolute; left: 70px; top: 130px; width: 620px; font-size: 0.86em; }
.rp-map { position: absolute; right: 70px; top: 40px; width: 520px; }
.rp-big { position: absolute; left: 70px; top: 520px; width: 600px; }
.rp ul { list-style: none; margin: 0; padding: 0; }
li[data-bespoke-marp-fragment="active"] .pop { display: inline-block; animation: tryit-pop 0.45s ease-out both; }
</style>

<div class="rp-text">

- On Tuesday you trusted **American Fork** most: it is 19 km from Provo, and Moab and Cedar City are over 250 km away
- **IDW** turned that instinct into a fixed rule: weight = 1/d²
- **Kriging** asks the data instead: *how much* more alike are closer places?

</div>

<img class="rp-map" src="images/ip-utah-activity-map.png" alt="Utah with Provo and the three known cities">
<img class="rp-map" src="images/ip-utah-activity-map-distances.png" alt="Straight-line distances from Provo: 19 km to American Fork, 259 km to Moab, 311 km to Cedar City">

<div class="rp">

* <span class="infobox rp-big pop">Closer in space, closer in value: kriging measures how much</span>

</div>

<!-- Start from what every student did on Tuesday's worksheet. Ask who weighted American Fork most and why. That instinct, nearby places are more alike, is the whole idea of kriging; the only new question is how much more alike, and kriging answers it from the data rather than from a rule like 1/d^2. One click brings up the one-line summary. The map and distances are Tuesday's (tools/week09_tuesday_figures.py). -->

---

# The Neighbor Test

<style scoped>
section > h1 { position: absolute; top: 52px; left: 70px; right: 70px; margin: 0; }
.nt-lead { position: absolute; left: 70px; top: 118px; width: 1140px; font-size: 0.8em; }
.nt-img { position: absolute; left: 70px; top: 175px; width: 1140px; }
.nt ul { list-style: none; margin: 0; padding: 0; }
li[data-bespoke-marp-fragment="active"] .pop { display: inline-block; animation: tryit-pop 0.45s ease-out both; }
</style>

<div class="nt-lead">Every <strong>pair</strong> of stations we already know is a test: how <strong>far apart</strong> are they, and how <strong>different</strong>?</div>

<img class="nt-img" src="images/ie-neighbor-base.png" alt="Sixty weather stations on a made-up temperature map, beside empty axes of distance against temperature difference">

<div class="nt">

* <img class="nt-img pop" src="images/ie-neighbor-pairs.png" alt="A close pair, 15 km apart and 1 degree different, and a far pair, 240 km apart and 14 degrees different">
* <img class="nt-img pop" src="images/ie-neighbor-cloud.png" alt="All 1,770 pairs: close pairs sit low, far pairs scatter high">

</div>

<!-- Two clicks. First one close pair and one far pair, on the map and as two dots: 15 km apart and about 1 degree different; 240 km apart and about 14 degrees. Second click: every pair of the 60 stations, 1,770 of them. Close pairs sit near the bottom (alike); far pairs scatter high (anything goes). That pattern is what kriging measures. The temperatures are made up: a smooth afternoon field plus a little instrument noise (tools/week09_kriging_story_figures.py). -->

---

# The Neighbor Test: No Pattern

<style scoped>
section > h1 { position: absolute; top: 52px; left: 70px; right: 70px; margin: 0; }
.nt-lead { position: absolute; left: 70px; top: 118px; width: 1140px; font-size: 0.8em; }
.nt-img { position: absolute; left: 110px; top: 160px; width: 1040px; }
.nt ul { list-style: none; margin: 0; padding: 0; }
.nt-take { position: absolute; left: 70px; right: 70px; top: 598px; font-size: 0.68em; }
li[data-bespoke-marp-fragment="active"] .pop { display: inline-block; animation: tryit-pop 0.45s ease-out both; }
</style>

<div class="nt-lead">The same 60 stations, but now every reading is <strong>independent</strong> of its neighbors: no pattern at all</div>

<img class="nt-img" src="images/ie-neighbor-random-base.png" alt="The same sixty stations on a speckled map with no pattern, beside empty axes of distance against temperature difference">

<div class="nt">

* <img class="nt-img pop" src="images/ie-neighbor-random-cloud.png" alt="All 1,770 pairs: close pairs scatter just as high as far pairs">
* <span class="infobox nt-take pop">Close pairs differ as much as far pairs: a neighbor tells you <strong>nothing</strong>, and kriging can do no better than the <strong>average</strong></span>

</div>

<!-- Two clicks: the cloud, then the takeaway. Same station locations as the last slide, but each reading is drawn independently (white noise plus the same small instrument error), so a station 15 km away is no more like Provo than one 250 km away. Ask before the first click what the cloud will look like. The cloud is flat: no bottom-left corner of alike close pairs. A semivariogram of this would be all nugget, and kriging with it puts the average everywhere; Part 3 shows a real mountain that the automatic fit mistook for exactly this. Note the y axis here runs to 40, not 30, so all the points fit. Made up; tools/week09_kriging_story_figures.py. -->

---

# The Neighbor Test: A Regional Trend

<style scoped>
section > h1 { position: absolute; top: 52px; left: 70px; right: 70px; margin: 0; }
.nt-lead { position: absolute; left: 70px; top: 118px; width: 1140px; font-size: 0.8em; }
.nt-img { position: absolute; left: 110px; top: 160px; width: 1040px; }
.nt ul { list-style: none; margin: 0; padding: 0; }
.nt-take { position: absolute; left: 70px; right: 70px; top: 598px; font-size: 0.68em; }
li[data-bespoke-marp-fragment="active"] .pop { display: inline-block; animation: tryit-pop 0.45s ease-out both; }
</style>

<div class="nt-lead">The same stations again, now on a <strong>regional trend</strong>: warm in the west, cooler to the east</div>

<img class="nt-img" src="images/ie-neighbor-trend-base.png" alt="The same sixty stations on a map that grades from warm in the west to cool in the east, beside empty axes">

<div class="nt">

* <img class="nt-img pop" src="images/ie-neighbor-trend-cloud.png" alt="All 1,770 pairs: the difference keeps growing with distance and never levels off">
* <span class="infobox nt-take pop">The difference keeps <strong>growing</strong> with distance and never levels off: no sill. Fit the <strong>trend</strong> first (Tuesday's trend surface), or use kriging that includes one</span>

</div>

<!-- Two clicks again. A steady west-to-east drop of about 0.09 degrees F per km plus a little smooth wiggle. Close pairs are alike, as in the first test, but far pairs never stop getting more different, so the cloud is a wedge rather than a curve that levels off. Pairs lined up north-south stay alike even when far apart, which is why the bottom of the wedge stays near zero. Kriging assumes the differences level off at a sill; a trend like this breaks that, so either take the trend out first with Tuesday's trend surface and krige what is left, or use Universal kriging, which fits the trend inside kriging. Three clouds, three stories: smooth field (levels off), no pattern (flat), trend (keeps rising). Made up; tools/week09_kriging_story_figures.py. -->

---

# Build the Semivariogram, One Bin at a Time

<style scoped>
section > h1 { position: absolute; top: 52px; left: 70px; right: 70px; margin: 0; }
.bd-eq { position: absolute; left: 70px; top: 112px; width: 560px; font-size: 0.78em; }
.bd-eq p { margin: 0; }
.bd-words { position: absolute; left: 650px; top: 128px; width: 560px; font-size: 0.66em; line-height: 1.35; }
.bd-img { position: absolute; left: 90px; top: 200px; width: 1100px; }
.bd ul { list-style: none; margin: 0; padding: 0; }
li[data-bespoke-marp-fragment="active"] .pop { display: inline-block; animation: tryit-pop 0.45s ease-out both; }
</style>

<div class="bd-eq">

$$
\gamma(h) = \frac{1}{2\,N(h)} \sum_{N(h)\ \text{pairs}} \left(z_i - z_j\right)^2
$$

</div>

<div class="bd-words">Take every <strong>pair</strong> about <em>h</em> apart, square each pair's difference, average them, and halve it: one dot on the graph per <strong>20 km bin</strong></div>

<img class="bd-img" src="images/ie-semivariogram-build-0.png" alt="The station map beside empty semivariogram axes">

<div class="bd">

* <img class="bd-img pop" src="images/ie-semivariogram-build-1.png" alt="The pairs 0 to 20 km apart drawn on the map, and their average as the first dot">
* <img class="bd-img pop" src="images/ie-semivariogram-build-2.png" alt="The pairs 20 to 40 km apart drawn on the map, and their average as the second dot">
* <img class="bd-img pop" src="images/ie-semivariogram-build-3.png" alt="The pairs 40 to 60 km apart drawn on the map, and their average as the third dot">
* <img class="bd-img pop" src="images/ie-semivariogram-build-4.png" alt="Every 20 km bin averaged: fourteen dots that rise and then level off">

</div>

<!-- Four clicks, one bin at a time, then the rest. Click 1: every pair of stations less than 20 km apart is drawn on the map (only a few dozen; they are the close neighbors), and their average half-squared difference becomes the first dot. Click 2: the pairs 20 to 40 km apart, a longer web of lines, and a dot a little higher. Click 3: 40 to 60 km. Click 4: the same thing done for every 20 km bin out to 280 km: the dots rise and level off. N(h) is the number of pairs in the bin, z_i and z_j the two stations' readings. The one-half is why it is called the semi-variance; it makes the far-apart level (the sill) equal the variance of the readings. The bin width is ArcGIS Pro's Lag size. 20 km bins rather than 10 km because 60 stations give too few pairs closer than 10 km for a steady average. Students never compute this by hand; the tool does it. Same made-up stations as the neighbor test (tools/week09_kriging_story_figures.py). -->

---

# Fit a Model to the Dots

<style scoped>
section > h1 { position: absolute; top: 52px; left: 70px; right: 70px; margin: 0; }
.sv-img { position: absolute; right: 50px; top: 120px; width: 640px; }
.sv-lead { position: absolute; left: 70px; top: 125px; width: 500px; font-size: 0.72em; }
.svfit ul, .sv ul { list-style: none; margin: 0; padding: 0; }
.sv-fit { position: absolute; left: 70px; top: 262px; width: 500px; font-size: 0.68em; line-height: 1.3; }
.sv li { position: absolute; left: 70px; width: 500px; margin: 0; font-size: 0.68em; line-height: 1.3; }
.sv li:nth-child(1) { top: 345px; } .sv li:nth-child(2) { top: 400px; } .sv li:nth-child(3) { top: 455px; }
.sv li:nth-child(4) { top: 530px; } .sv li:nth-child(5) { top: 570px; }
.sv .q { color: #e8792b; font-weight: 700; }
.svmod ul { list-style: none; margin: 0; padding: 0; }
.sv-mod { background: #fff; }
.lab8-big { position: absolute; right: 50px; top: 592px; width: 640px; box-sizing: border-box; background: #e8792b; color: #fff; border-radius: 12px; padding: 0.35em 0.8em; font-size: 0.82em; font-weight: 800; line-height: 1.25; text-align: center; }
.lab8-big strong { color: #ffd21f; }
li[data-bespoke-marp-fragment="active"] .pop { display: inline-block; animation: tryit-pop 0.45s ease-out both; }
</style>

<div class="sv-lead">

Now we have the dots. Many **kriging models** have been developed; pick one and **fit** it to the dots, and the tool reads three numbers off the curve. The last click shows three of the shapes.

</div>

<img class="sv-img" src="images/ie-semivariogram-dots.png" alt="Semivariance against distance: the pairs averaged every 20 km, as dots">

<div class="svfit">

* <img class="sv-img pop" src="images/ie-semivariogram-plain.png" alt="The same dots with a fitted spherical curve in orange, and the nugget, range and sill marked"><span class="pop sv-fit">The fitted model, in <strong style="color:#e07a1f">orange</strong>: here a spherical one</span>

</div>

<div class="sv">

* <span class="pop"><strong>Nugget:</strong> two thermometers a step apart still disagree a little</span>
* <span class="pop"><strong>Range:</strong> how far away a station still tells you something</span>
* <span class="pop"><strong>Sill:</strong> how different far-apart places typically get</span>
* <span class="pop q">Past the range, what does Moab tell you about Provo?</span>
* <span class="pop">No more than the state's average does</span>

</div>

<div class="svmod">

* <img class="sv-img sv-mod pop" src="images/ie-semivariogram-models.png" alt="Three semivariogram models with the same nugget, sill and range: spherical rises steadily, exponential is steepest at first, Gaussian is flat at first"><span class="pop lab8-big">Lab 8 runs <strong>all three</strong> models on Y Mountain</span>

</div>

<!-- Seven clicks: the fitted model, then nugget, range, sill, a question and its answer, and last the three model shapes Lab 8 offers with the Lab 8 banner. No need to go into how the fit is done: there are many model shapes, the tool fits one to the dots, and it appears in orange. The tool never asks students to compute this; it fits the curve and reports these three numbers, and they are exactly the Major range, Partial sill (sill minus nugget) and Nugget boxes in the Kriging dialog, which Lab 8 leaves empty so the tool fits them. Nugget: instrument error or variation closer than any two stations. Range: past it, a station is no more use for Provo than the regional average. Sill: the typical difference between far-apart places. Here the made-up stations give a nugget of 9 degrees F squared (the noise put into the readings), a sill of about 83 and a range of about 170 km. Last click, the three models (merged here October 28, 2026 from their own slide): same nugget, sill and range, different shape near zero. Spherical rises steadily and is flat past the range; exponential is steepest at first, so neighbors lose their likeness fastest; Gaussian is flat at first and assumes a very smooth surface. Drawn from the formulas ArcGIS Pro's Kriging documents (tools/week09_semivariogram_models.py); the exponential and Gaussian only approach the sill, so their range is the distance where they reach 95 % of it. The shape near zero matters most, because the nearest samples carry most of the weight. Do not give the class Lab 8's results; the Gaussian run's error map is one of the lab's questions. -->

---

# Under the Hood: How Kriging Gets Its Weights

<style scoped>
section > h1 { position: absolute; top: 46px; left: 70px; right: 70px; margin: 0; font-size: 1.6em; }
.kw-map { position: absolute; left: 50px; top: 112px; width: 500px; }
.kw-var { position: absolute; left: 50px; top: 410px; width: 500px; }
.kw-list { position: absolute; left: 600px; top: 112px; width: 620px; font-size: 0.6em; line-height: 1.32; }
.kw-list ul { margin: 0; padding-left: 1.1em; }
.kw-list li { margin: 0 0 0.35em 0; }
.kw-list .b { color: #0062b8; font-weight: 700; } .kw-list .g { color: #6b7684; font-weight: 700; } .kw-list .o { color: #c9620f; font-weight: 700; }
.kw-mx { position: absolute; left: 610px; top: 395px; border-collapse: separate; border-spacing: 3px; font-family: "JetBrains Mono", Menlo, Consolas, monospace; font-size: 0.5em; }
.kw-mx td { padding: 3px 7px; text-align: center; border-radius: 4px; border: none; background: none; }
.kw-mx td.gij { background: #eef0f3; } .kw-mx td.d0 { background: #eef0f3; color: #8a94a0; }
.kw-mx td.one { background: #f2f5e6; } .kw-mx td.v { background: #e3eefa; color: #0062b8; font-weight: 700; }
.kw-mx td.lam { background: #fbeedd; color: #c9620f; font-weight: 700; } .kw-mx td.br { color: #8a94a0; font-size: 1.9em; padding: 0; }
.kw-mx td.op { color: #4a5568; }
.kw-z { position: absolute; left: 618px; top: 590px; width: 600px; font-size: 0.6em; line-height: 1.35; }
.kw-z p { margin: 0 0 0.2em 0; }
.kw-z .o { color: #c9620f; font-weight: 700; }
</style>

<img class="kw-map" src="images/ie-kw-map.png" alt="An unknown point Z0 with four measured temperatures around it: blue dashed lines D1 to D4 from Z0 to each, and gray lines between every pair of measurements">
<img class="kw-var" src="images/ie-kw-vario.png" alt="The semivariogram with the four target readings V1 to V4 in blue and the six pair readings in gray">

<div class="kw-list">

- The weights are **not read straight off the curve**. Read it at two kinds of distance:
  - <span class="b">Z₀ to each sample</span>: how far off each sample is likely to be (V₁…V₄)
  - <span class="g">sample to sample</span>: how much the samples **repeat** each other (V₁₂…V₃₄)
- Put them in one small **system of equations** and solve for the <span class="o">weights λ</span>, which add up to 1
- Then Z₀ is a **weighted average**, just like IDW. Clustered samples share their weight; IDW never sees that
- ArcGIS Pro does this for **every cell**, with its 12 nearest points
- **Read more:** [How Kriging Gets Its Weights](https://byu-hydroinformatics.github.io/ce414-gis-applications/explainers/kriging-weights/), the full example worked by hand

</div>

<table class="kw-mx" aria-label="The kriging system">
<tr><td class="br" rowspan="5">[</td><td class="d0">0</td><td class="gij">V₁₂</td><td class="gij">V₁₃</td><td class="gij">V₁₄</td><td class="one">1</td><td class="br" rowspan="5">]</td><td class="br" rowspan="5">[</td><td class="lam">λ₁</td><td class="br" rowspan="5">]</td><td class="op" rowspan="5">=</td><td class="br" rowspan="5">[</td><td class="v">V₁</td><td class="br" rowspan="5">]</td></tr>
<tr><td class="gij">V₁₂</td><td class="d0">0</td><td class="gij">V₂₃</td><td class="gij">V₂₄</td><td class="one">1</td><td class="lam">λ₂</td><td class="v">V₂</td></tr>
<tr><td class="gij">V₁₃</td><td class="gij">V₂₃</td><td class="d0">0</td><td class="gij">V₃₄</td><td class="one">1</td><td class="lam">λ₃</td><td class="v">V₃</td></tr>
<tr><td class="gij">V₁₄</td><td class="gij">V₂₄</td><td class="gij">V₃₄</td><td class="d0">0</td><td class="one">1</td><td class="lam">λ₄</td><td class="v">V₄</td></tr>
<tr><td class="one">1</td><td class="one">1</td><td class="one">1</td><td class="one">1</td><td class="one">0</td><td class="lam">m</td><td class="v">1</td></tr>
</table>

<div class="kw-z">

<span class="o">Z₀ = λ₁Z₁ + λ₂Z₂ + λ₃Z₃ + λ₄Z₄</span>

Here: λ = 0.63, 0.16, 0.10, 0.12, so Z₀ = **61.5 °F**

</div>

<!-- A one-slide primer on what the Kriging tool does with the fitted curve, added October 28, 2026 in place of the separate three-models slide (those models are now the last click of Fit a Model to the Dots). Students often assume the weights are read straight off the semivariogram. They are not: the curve is read at two kinds of distance, from the unknown point to each sample (blue, V1 to V4: how far off each sample is likely to be) and between every pair of samples (gray, the six Vij: how much the samples repeat each other). Those ten numbers fill a 5 x 5 system: the gray block is sample-to-sample, the blue column is target-to-sample, and the last row forces the weights to add to 1; m is a Lagrange multiplier that makes that rule fit. Solve it and you have the weights; Z0 is then the same weighted average as IDW. The example is made up (spherical model, nugget 2, sill 20, range 50 km): weights 0.625, 0.157, 0.095 and 0.122, Z0 = 61.49 F, and an expected error of about 3.3 F. Z3 and Z4 are the same distance from Z0 but get different weights because Z3 is closer to Z2 and repeats some of what Z2 says; IDW gives them the same weight. Students do not need to solve this by hand; the link goes to the full worked page (docs/explainers/kriging-weights/index.html), and the figures are from tools/week09_kriging_weights_figures.py. -->
---

# Same Points, Different Settings

<style scoped>
section > h1 { position: absolute; top: 52px; left: 70px; right: 70px; margin: 0; }
.ks-img { position: absolute; left: 50%; transform: translateX(-50%); top: 152px; height: 522px; }
.ks-inset { position: absolute; right: 60px; top: 22px; width: 270px; border: 1px solid #c3ccd6; }
.ks-cap { position: absolute; right: 345px; top: 40px; width: 270px; font-size: 0.52em; line-height: 1.3; color: #4a5568; text-align: right; }
</style>

<img class="ks-inset" src="images/ie-kriging-settings-truth.png" alt="The true temperature map with a straight 100 km line across it, eight measured points on the line and 22 more scattered around it">
<span class="ks-cap">The truth (right) and <strong>30 thermometers</strong>. Each line graph is a <strong>cross section</strong> of the kriged map beside it, along the <strong>100 km line</strong></span>

<img class="ks-img" src="images/ie-kriging-settings-2d.png" alt="The same 30 points kriged four ways, each shown as a cross section along the line and as a small kriged map: fitted model, big nugget, short range, long range">

<!-- The inset at upper right is the made-up truth: a temperature map, a straight 100 km line across it with 8 thermometers on it (blue), and 22 more scattered off the line (black). Every panel krigs all 30 points in two dimensions; the line graph is that kriged map read along the line (a cross section) and the small map beside it is the whole surface, so each setting shows both ways. Point at the maps after each line graph: fitted model, a believable heat map; big nugget, nearly one flat color; short range, a yellow sheet with a small bull's-eye on each thermometer; long range, broad smooth blobs. Redrawn October 28, 2026 with the maps; before that the panels were one-dimensional kriging of the 8 points alone. Fitted model: each point's influence reaches out to the range and fades. Big nugget: the model says even neighbors barely agree, so the surface smooths toward the average and misses the points (Thursday's flat kriging panel later is the extreme case). Short range: the points are farther apart than the range, so between them the estimate falls back to the average. Long range: every point reaches far, so the curve runs straight between points and never returns to the average. Ask before revealing each caption which panel is which. Made-up values; ordinary kriging of the smooth signal (tools/week09_kriging_story_figures.py). -->

---

# Kriged Result

<style scoped>
section > h1 { position: absolute; top: 52px; left: 70px; right: 70px; margin: 0; }
.kr-lead { position: absolute; left: 70px; top: 122px; width: 1140px; font-size: 0.8em; }
.kr-img { position: absolute; left: 50px; top: 215px; height: 420px; }
.kr ul { list-style: none; margin: 0; padding: 0; }
.kr li { position: absolute; left: 870px; width: 360px; margin: 0; font-size: 0.58em; line-height: 1.3; }
.kr li:nth-child(1) { top: 210px; } .kr li:nth-child(2) { top: 345px; } .kr li:nth-child(3) { top: 462px; }
.kr .tryit, .kr .infobox { font-size: 1em; }
li[data-bespoke-marp-fragment="active"] .pop { display: block; animation: tryit-pop 0.45s ease-out both; }
</style>

<div class="kr-lead">Like IDW, a <strong>weighted average</strong> of nearby points, but the <strong>variogram</strong> sets the weights, not a fixed 1/d<sup>n</sup></div>

<img class="kr-img" src="images/ip-tp-kriging-result.png" alt="The true DEM beside the kriged surface from 150 samples">

<div class="kr">

* <span class="tryit pop">This looks better than Tuesday's methods. Why doesn't it give back the <strong>full terrain</strong> of the mountain?</span>
* <span class="infobox pop">Because you can't <strong>fabricate data</strong>. Between the samples, kriging only has a weighted average of the points it was given.</span>
* <span class="infobox pop">A <strong>generative AI</strong> model could invent ridges and canyons that look more real, but it still could not give back <em>this</em> mountain without many more points.</span>

</div>

<!-- Three clicks: the question (let the room answer before the next click), the answer, then the generative-AI point. Every method today only rearranges the 150 measured elevations; none of them can know about a canyon that no sample fell in, so the ridges and gullies between samples are gone. A generative model trained on many DEMs could fill in plausible-looking terrain texture, but it would be invented texture, not Mount Timpanogos's actual ridges; only more measurements bring those back. The true DEM on the left, the kriged surface from Tuesday's 150 samples on the right (ordinary kriging, the spherical model on the previous slides). Compare it against Tuesday's IDW panels: the bull's-eyes are gone, because the weights now reflect how quickly elevation actually decorrelates with distance instead of a fixed 1/d^n rule. Against the whole DEM it scores 86 m RMSE, IDW 110 m. The line above the figure is the sentence the quiz asks about; it came from the "From Variogram to Surface" slide, merged here October 26, 2026 along with the variogram and 3D kriging slides. -->

---

# Kriging in ArcGIS Pro

<style scoped>
section > h1 { position: absolute; top: 52px; left: 70px; right: 70px; margin: 0; }
.pro-text { position: absolute; left: 70px; top: 130px; width: 470px; font-size: 0.8em; }
.pro-img { position: absolute; right: 50px; top: 40px; height: 640px; }
</style>

<div class="pro-text">

- **Spatial Analyst ▸ Kriging**, method **Ordinary**
- Leave the model's numbers empty and the tool **fits** them to your points
- A default is not always right: Part 3 shows one that fails

</div>

<img class="pro-img" src="images/ie-kriging-callouts.png" alt="The Kriging tool dialog with red callouts on Semi-variogram model, Lag size, the range, sill and nugget boxes, and Output cell size">

<!-- The capture is the Kriging tool inside the Lab 8 model, ArcGIS Pro 3.7.1, with Lag size 30 filled in from the 30 m cell size. Ordinary kriging assumes an unknown but constant mean; Universal adds a trend, Tuesday's trend surface inside kriging. In Lab 8 the default lag works: 2,500 points over 60 km2 give many close pairs. In an earlier ArcGIS Pro test on Little Cottonwood Canyon (150 points over a canyon) the same kind of default fitted a model that was almost all nugget and lost to every method but the trend; a 300 m lag won. Today's six-methods slide shows the same failure on the Timpanogos samples with an automatic fit. After a run the dialog can show the fitted range and sill, which is why the lab says to empty them before the next run. -->

---

<!-- _class: lead -->

![bg right:55%](images/ip-divider-how-wrong.jpg)

# Part 2 — How Wrong Is the Surface?

## When you have the truth

---

# Error = Truth − Surface

![bg right:50% w:97%](images/ie-rc-error-callouts.png)

<style scoped>
section > h1 { position: absolute; top: 52px; left: 70px; width: 560px; margin: 0; }
.et-list { position: absolute; left: 70px; top: 122px; width: 560px; font-size: 0.66em; line-height: 1.3; }
.et-list ul { margin: 0; }
.et-img { position: absolute; left: 80px; top: 252px; height: 335px; }
.qa ul { list-style: none; margin: 0; padding: 0; }
.qa li { position: absolute; left: 70px; width: 540px; margin: 0; font-size: 0.6em; line-height: 1.3; }
.qa li:nth-child(1) { top: 598px; } .qa li:nth-child(2) { top: 630px; }
.qa strong { color: #e8792b; }
li[data-bespoke-marp-fragment="active"] .pop { display: inline-block; animation: tryit-pop 0.45s ease-out both; }
</style>

<div class="et-list">

- Subtract, cell by cell, in **Raster Calculator**: the **map algebra** of Week 3
- **Positive:** the surface is too **low**; **negative:** too **high**
- In **meters**; map it on a **diverging** scale centered on zero

</div>

<img class="et-img" src="images/ie-map-algebra-error.png" alt="Three tilted rasters stacked: True_DEM minus Surface equals Error; one cell reads 2,450 minus 2,410 equals +40 m">

<div class="qa">

* <span class="pop"><strong>A cell reads +40 m. Too high or too low?</strong></span>
* <span class="pop">Too <strong>low</strong>: the truth is 40 m above the surface there</span>

</div>

<!-- The diagram is the whole idea: two rasters on the same grid, one above the other, and subtraction one cell at a time, exactly the local map algebra from the Week 3 raster-analysis decks (NDVI was the same kind of cell-by-cell arithmetic). The picked cell reads 2,450 m in the truth and 2,410 m in the surface, so its error is +40 m: blue, too low (made-up values, tools/week09_map_algebra_figure.py). The capture is the Lab 8 Step 6 Raster Calculator, inside ModelBuilder: "%True_DEM%" - "%Thiessen_Surface%". The order matters only for the sign, but say it out loud and keep it fixed: if one student subtracts the other way, every color on their map flips and their "too high" ridges become "too low". Lab 8 uses truth minus surface throughout. Two clicks: the +40 question and its answer. The worksheet callout was dropped October 28, 2026: there is no worksheet on Thursday. -->

---

# Where the Error Lives

![w:1180 center](images/ie-error-row.png)

* **Why is the valley floor nearly white?**
* It is flat: any nearby sample is close when the ground does not change. The error is on the **mountain front**
* Thiessen's error is **finest-grained**: every polygon edge is a step
* <span class="tryit">Which of these maps has the <strong>least error</strong>, and how can we <strong>calculate</strong> it?</span>

<style scoped>
section > ul { font-size: 0.8em; }
</style>

<!-- The three error maps from the Lab 8 example baseline (2,500 points, default parameters). Red is where the surface is too high, blue too low. Four clicks: the question (ask the room before the next click), the answer, the Thiessen point, then the lead-in to RMSE: let them guess which map is best by eye, then say that eyeballing three maps of 67,337 cells is not a measurement, and the next slide turns each map into one number. The valley floor is within 5 m for every method because it is flat: any method that returns a nearby sample's value is close when the ground does not change. The error is a map of where the ground changes faster than the samples are spaced. Lab 8 asks each student to find their best method's single worst cell and explain the ground there. -->

---

# One Number: Root Mean Squared Error (RMSE)

<style scoped>
section > h1 { position: absolute; top: 52px; left: 70px; right: 70px; margin: 0; }
.rm-eq { position: absolute; left: 70px; top: 125px; width: 500px; font-size: 1.05em; }
.rm-list { position: absolute; left: 70px; top: 290px; width: 500px; font-size: 0.82em; line-height: 1.35; }
.rm-list ul { margin: 0; }
.rm-img { position: absolute; right: 40px; top: 122px; width: 660px; }
.rm-cap { position: absolute; right: 40px; top: 428px; width: 660px; font-size: 0.56em; color: #4a5568; text-align: center; }
.rm-ans ul { list-style: none; margin: 0; padding: 0; }
.rm-ans li { position: absolute; left: 70px; right: 70px; top: 530px; margin: 0; display: flex; align-items: stretch; gap: 16px; }
.rm-ans .lead { flex: 0 0 300px; display: flex; align-items: center; font-size: 0.66em; line-height: 1.25; color: #002e5d; font-weight: 700; }
.rm-ans .r { flex: 1; border-radius: 12px; padding: 0.3em 0.5em; text-align: center; color: #fff; font-size: 0.66em; line-height: 1.2; }
.rm-ans .r b { display: block; font-size: 1.6em; }
.rm-ans .t { background: #e8792b; } .rm-ans .i { background: #0062b8; } .rm-ans .k { background: #2e8b57; }
li[data-bespoke-marp-fragment="active"] .pop { display: inline-block; animation: tryit-pop 0.45s ease-out both; }
</style>

<div class="rm-eq">

$$
\text{RMSE} = \sqrt{\frac{1}{n}\sum_{i=1}^{n}\left(z_i - \hat{z}_i\right)^2}
$$

</div>

<div class="rm-list">

- **Square** each error, so highs and lows both count
- Take the **mean** over every cell
- Take the **square root**, so the answer is back in **meters**

</div>

<img class="rm-img" src="images/ie-profile.svg" alt="One row of cells across the Lab 8 study area: the true DEM and the Thiessen, IDW and kriging rebuilds from 250 points">

<span class="rm-cap">Every <strong>gap</strong> between the black truth and a colored rebuild is one cell's error; RMSE is the typical size of those gaps, in meters</span>

<div class="rm-ans">

* <span class="lead">The three error maps from the last slide, each as one number:</span><span class="r t pop">Thiessen<b>28.29 m</b></span><span class="r i pop">IDW, power 2<b>20.71 m</b></span><span class="r k pop">Kriging<b>14.46 m</b></span>

</div>

<!-- One click: the answer to the last slide's question, the three error maps as one number each (the Lab 8 example baseline, 2,500 points, default parameters; the lab's check values). Kriging wins here, and the next slide shows how the number is computed in ArcGIS Pro. z is the truth, z-hat the surface, n the number of cells. Squaring does two things: it stops positive and negative errors canceling, and it weights big errors heavily, so a surface with a few 100 m misses scores worse than one with many 5 m misses. The profile is one row of cells across the Lab 8 study area (the same one as on Today's Goals): every vertical gap between the black truth and one of the colored rebuilds is one cell's error, and RMSE rolls all 67,337 of those gaps into one number per method. Common slip: the root of the mean, not the mean of the roots, and not the root of the sum. The "What RMSE Hides" slide that followed was cut October 28, 2026 to keep RMSE something students want to use; its profile figure moved here. -->

---

# RMSE in ArcGIS Pro: Four Steps

<style scoped>
section > h1 { position: absolute; top: 52px; left: 70px; right: 70px; margin: 0; }
.fl-lead { position: absolute; left: 70px; top: 118px; width: 1140px; font-size: 0.7em; }
.flow { position: absolute; left: 70px; top: 170px; width: 350px; display: flex; flex-direction: column; gap: 8px; }
.flow .box { background: #eef4fb; border: 2px solid #0062b8; border-radius: 12px; padding: 0.3em 0.55em; font-size: 0.56em; line-height: 1.3; }
.flow .box b { display: block; font-size: 1.25em; color: #002e5d; }
.flow .box .tool { color: #0062b8; font-weight: 700; }
.flow .box code { font-size: 0.92em; }
.fl-list { position: absolute; left: 70px; top: 505px; width: 350px; font-size: 0.56em; line-height: 1.3; }
.fl-list ul { margin: 0; padding-left: 1.1em; }
.caps-base { position: absolute; left: 450px; top: 170px; width: 760px; height: 490px; object-fit: contain; object-position: left top; }
.caps ul { list-style: none; margin: 0; padding: 0; }
.caps li { position: absolute; left: 450px; top: 170px; width: 760px; height: 490px; margin: 0; background: #fff; }
.caps li img { width: 100%; height: 100%; object-fit: contain; object-position: left top; }
.caps li[data-bespoke-marp-fragment="inactive"] { display: none; }
.flow .box.on { background: #fff3e8; border-color: #e8792b; }
section:not(:has(.caps li[data-bespoke-marp-fragment="active"])) .flow .box:nth-child(1) { background: #fff3e8; border-color: #e8792b; }
section:has(.caps li:nth-child(1)[data-bespoke-marp-fragment="active"]):not(:has(.caps li:nth-child(2)[data-bespoke-marp-fragment="active"])) .flow .box:nth-child(2) { background: #fff3e8; border-color: #e8792b; }
section:has(.caps li:nth-child(2)[data-bespoke-marp-fragment="active"]):not(:has(.caps li:nth-child(3)[data-bespoke-marp-fragment="active"])) .flow .box:nth-child(3) { background: #fff3e8; border-color: #e8792b; }
section:has(.caps li:nth-child(3)[data-bespoke-marp-fragment="active"]) .flow .box:nth-child(4) { background: #fff3e8; border-color: #e8792b; }
</style>

<div class="fl-lead">ArcGIS Pro has <strong>no single RMSE tool</strong>. Chain four steps, each one a tool you already know (click through the dialogs):</div>

<div class="flow">
<div class="box"><b>1 · Error</b><span class="tool">Raster Calculator</span> · <code>True_DEM − Surface</code></div>
<div class="box"><b>2 · Square</b><span class="tool">Raster Calculator</span> · <code>Square(Error)</code></div>
<div class="box"><b>3 · Mean</b><span class="tool">Zonal Statistics as Table</span> · one zone, statistic <strong>Mean</strong></div>
<div class="box"><b>4 · Square root</b><span class="tool">Calculate Field</span> · <code>math.sqrt(!MEAN!)</code></div>
</div>

<div class="fl-list">

- The formula read **inside out**
- Lab 8's model chains all four for **each method**
- **COUNT** in the table is the cells averaged: **67,337**

</div>

<img class="caps-base" src="images/ie-rc-error-callouts.png" alt="Step 1: the Raster Calculator dialog with callouts, truth minus surface, one error raster per method">

<div class="caps">

* <img src="images/ie-rc-square-callouts.png" alt="Step 2: the Raster Calculator dialog squaring the error raster">
* <img src="images/ie-zonal-callouts.png" alt="Step 3: the Zonal Statistics as Table dialog with callouts: the study area as the one zone, the squared error raster, and statistic Mean">
* <img src="images/ie-calc-field-callouts.png" alt="Step 4: the Calculate Field dialog writing RMSE as the square root of MEAN">

</div>

<!-- Three clicks: the dialog for step 1 is up when the slide opens, and each click replaces it with the next step's dialog and moves the highlight down the flow (all four are Lab 8 Step 6 and 7 captures). There is no RMSE tool in ArcGIS Pro, so the four boxes are the whole recipe, and each one is a tool students have already run: Raster Calculator twice (Week 3's map algebra), Zonal Statistics as Table, and Calculate Field. Read the formula on the last slide from the inside out and it is the same four steps: the difference, the square, the mean, the root. The table is Lab 8 Step 7's output for one method: COUNT 67,337 cells and AREA 60,603,300 square meters, both on the lab page as check values. If COUNT comes out smaller, the surfaces did not cover the whole study area (the Extent environment is the usual cause), and the RMSE is quietly computed on fewer cells. Zonal Statistics as Table opens with the statistic set to All; Mean is the one the RMSE needs. The step-2 capture (ie-rc-square-callouts.png) was on the RMSE slide until October 28, 2026. -->

---

<!-- _class: lead -->

![bg right:55%](images/ip-divider-which-trust.jpg)

# Part 3 — Which One to Trust?

## Same points, different surfaces

---

<!-- _class: quiz -->

<style scoped>
section > h1 { position: absolute; top: 40px; left: 70px; width: 600px; margin: 0; line-height: 1.2; }
.sd-sub { position: absolute; top: 148px; left: 70px; font-size: 0.85em; font-weight: 700; color: #e8792b; }
.sd-truth { position: absolute; left: 70px; top: 205px; height: 250px; }
.sd-truth-cap { position: absolute; left: 340px; top: 215px; width: 300px; font-size: 0.6em; line-height: 1.35; }
.sd-compare { position: absolute; right: 70px; top: 24px; height: 628px; }
.sd-note { position: absolute; right: 70px; top: 658px; width: 431px; text-align: center; font-size: 0.5em; color: #4a5568; }
.sd-ans ul { list-style: none; margin: 0; padding: 0; }
.sd-ans li { position: absolute; left: 70px; width: 640px; margin: 0; font-size: 0.6em; line-height: 1.3; }
.sd-ans li:nth-child(1) { top: 478px; } .sd-ans li:nth-child(2) { top: 520px; }
.sd-ans li:nth-child(3) { top: 558px; } .sd-ans li:nth-child(4) { top: 596px; }
li[data-bespoke-marp-fragment="active"] .sd-pop { display: inline-block; animation: tryit-pop 0.45s ease-out both; }
</style>

# Which Method Is Best and Why?

<span class="sd-sub">Discuss with your neighbor</span>

<img class="sd-truth" src="images/ip-tp-dem-2d.png" alt="The true surface: Mount Timpanogos DEM">
<span class="sd-truth-cap"><strong>The truth</strong>, which a real project never gets to see</span>

<img class="sd-compare" src="images/ip-tp-compare-methods.png" alt="Six surfaces from the same samples: Thiessen, IDW, spline, kriging fitted, kriging automatic, trend">
<span class="sd-note">Every method uses the same <strong>150</strong> sample points</span>

<div class="sd-ans">

* <span class="sd-pop"><strong>It depends</strong> on the ground, the purpose, and the settings:</span>
* <span class="sd-pop">Closest to this mountain? → <strong>spline</strong> or <strong>kriging</strong> with a fitted model</span>
* <span class="sd-pop">The flat panel? → kriging with a <strong>careless setting</strong></span>
* <span class="sd-pop">A regional trend, or a category like soil? → <strong>trend</strong> or <strong>Thiessen</strong></span>

</div>

<!-- Give pairs two or three minutes, then take answers and the reasons for them. Click the four answers in only after the discussion; the next slides then put numbers on it. Push the class past "which is prettiest" to "which one reproduces the ridges and canyons of the truth." Honest answer: it depends. On this mountain the spline and the fitted kriging come closest (69 and 73 m at the hold-out points, next slide); IDW and Thiessen follow; the trend surface only has the regional tilt. The flat panel is the same kriging with an automatic variogram fit that came out almost all nugget, so every cell gets the mean: worth asking what went wrong before the third click. Trend is right when only the regional pattern matters, and Thiessen when the variable is a category such as soil type. Every panel uses the same 150 Timpanogos samples, so the differences are the methods, not the data. And in a real project you cannot run this comparison, because you never have the truth panel, which is why the next slide scores each method at points held back from it. Moved October 26, 2026 from after the exactness slide, where the scores had already given the answer away; formerly a class vote. -->

---

# Same Points, Six Methods

![h:520 center](images/ip-tp-six-methods.png)

<p class="six-cap">Each method is scored at <strong>60 points held back</strong> from it: the honest test when there is no true surface</p>

<style scoped>
.qa ul { list-style: none; margin: 0; padding: 0; }
.qa li { position: absolute; left: 640px; width: 590px; margin: 0; font-size: 0.56em; line-height: 1.3; }
.qa li:nth-child(1) { top: 46px; } .qa li:nth-child(2) { top: 74px; }
.six-cap { position: absolute; left: 70px; right: 70px; top: 650px; margin: 0; font-size: 0.58em; text-align: center; }
.qa strong { color: #e8792b; }
li[data-bespoke-marp-fragment="active"] .pop { display: inline-block; animation: tryit-pop 0.45s ease-out both; }
</style>

<div class="qa">

* <span class="pop"><strong>Why is one kriging panel flat?</strong></span>
* <span class="pop">Its automatic fit decided no sample tells you anything about its neighbors, so every cell gets the <strong>mean</strong>. Next slide: why</span>

</div>

<!-- It answers "how would you judge which one to trust" with a test students can run. the same 150 Mount Timpanogos samples as Tuesday (USGS 3DEP, 30 m, 7.2 km square; tools/week09_elevation_figures.py, numbers in tools/week09_elevation_numbers.json; computed with numpy, scipy and pykrige rather than ArcGIS Pro, so the figures are figures, not tool captures). Each surface is checked at 60 hold-out points the methods never saw (red circles, first panel). Root-mean-square error at the hold-out points: spline 69 m, kriging with a fitted spherical model 73, IDW 100, Thiessen 113, 2nd-order trend 241, and kriging with pykrige's automatic variogram fit 372 - exactly what you get by ignoring location and guessing the mean of the samples (372 m), because that fit came out almost all nugget with a range of a few meters, so every cell gets the mean. Two lessons: hold out some points and measure, don't eyeball; and the same method with a careless setting can do far worse than a much simpler one. Natural neighbor, in the earlier version of this test, has no scipy equivalent and was dropped. Now that RMSE is defined, the numbers can be read off directly. Exactness, if anyone asks: Thiessen, IDW, the spline and the fitted kriging (nugget 0) return every sample value; the trend misses by 163 m on average and the automatic kriging, with its huge nugget, by 96 m, so kriging is exact only when the nugget is zero. The hold-out, checkpoint-spread, exactness and methods-table slides were cut October 26, 2026 once Lab 8 dropped checkpoints. -->

---

# Why the Automatic Fit Came Out Flat

<style scoped>
section > h1 { position: absolute; top: 52px; left: 70px; right: 70px; margin: 0; }
.af-img { position: absolute; left: 50%; transform: translateX(-50%); top: 118px; width: 1080px; }
.af ul { list-style: none; margin: 0; padding: 0; }
.af li { position: absolute; left: 70px; width: 1140px; margin: 0; font-size: 0.6em; line-height: 1.3; }
.af li:nth-child(1) { top: 555px; } .af li:nth-child(2) { top: 590px; } .af li:nth-child(3) { top: 625px; }
li[data-bespoke-marp-fragment="active"] .pop { display: inline-block; animation: tryit-pop 0.45s ease-out both; }
</style>

<img class="af-img" src="images/ie-autofit-flat.png" alt="Two semivariograms of the same 150 samples: binned every 300 m the dots rise to a 4.6 km range; in six wide bins out to 8 km they rise and then fall, and the fitted line is flat">

<div class="af">

* <span class="pop">The automatic fit used **6 wide bins** out to 8 km. The far bins are pairs on opposite **low flanks**: alike again, so the dots rise, then **fall**</span>
* <span class="pop">A spherical curve can only rise and level off, so the best fit was a **flat line** with a range of 0.3 m: no sample helps its neighbors</span>
* <span class="pop">To that model the mountain looks like the **no-pattern** test from Part 1, so every cell gets the mean. Lab 8's 2,500 points and 30 m **lag** fit fine</span>

</div>

<!-- Three clicks. Same 150 Timpanogos samples, binned two ways (tools/week09_autofit_figure.py, which repeats the elevation script's DEM request and sample draw). Left: the careful fit behind the good kriging panel, pairs grouped every 300 m and only out to 4.5 km; the dots rise steadily and the spherical model reaches its sill at about 4.6 km. Right: pykrige's defaults, the automatic fit: 6 bins spread across every distance in the 7.2 km square, out to about 8 km. Past about 4 km the pairs are increasingly corner to corner, one low flank against the other, and those are similar heights again, so the dots come back down. No spherical curve rises and falls, so the least-squares fit settles on the average level everywhere: nugget 33,339 and partial sill 72,238 m^2 with a range of 0.29 m. A range shorter than the closest pair of samples means no sample carries any weight for its neighbor, so ordinary kriging returns the sample mean everywhere, the flat panel, and with that big nugget it does not even return the samples. The lessons for Lab 8: the lag (bin width) and how far out you look matter, and a fitted model is worth a glance before you trust it. In Lab 8 (2,500 points over 60 km2, Lag size 30 from the 30 m cell size) the fit works, as the Kriging in ArcGIS Pro notes say. Added October 28, 2026, replacing the one-line "almost all nugget" answer. -->

---

<!-- _class: lead -->

![bg right:55%](images/ip-divider-explorer.jpg)

# Part 4 — Lab 8, Interpolation Explorer

<!-- NOTE FOR FALL 2027 (Dan, October 28, 2026): present this Lab 8 introduction, or at least part of it (Lab 8 at a Glance and Your Own IDW Power), in Tuesday's deck instead of here. Doing some theory and some hands-on lab demonstration on Tuesday, then more theory and more lab demonstration on Thursday, has worked well this year; this week put all of the lab on Thursday. Also recorded in tools/NEXT_STEPS.md, section 7. -->

---

# Lab 8 at a Glance

![bg right:58% w:99%](images/ie-full-model.svg)

- **Ground:** Y Mountain, a **30 m** DEM, `True_DEM`
- **Points:** **250**, **2,500**, **10,000**
- **Model:** points → Thiessen, IDW, kriging → error → **RMSE**
- **Then:** five dialog runs, one at **your own** IDW power

[Lab 8 — Interpolation Explorer](https://byu-hydroinformatics.github.io/ce414-gis-applications/assignments/lab-08/)

<!-- The figure is the finished Lab 8 model, exported from ModelBuilder. Sample Points, IDW Power and the Semivariogram are its input parameters; the three error rasters and three RMSE tables are its outputs. Two things to warn about: set the Extent environment to True_DEM in Step 0, or IDW and kriging cover less ground at 250 points; and finish Map 1 before the first run from the tool dialog, because a dialog run deletes everything that is not a parameter, including the surfaces. -->

---

# Your Own IDW Power

![bg right:36% h:80%](images/ie-tool-dialog.png)

> **Power = 1 + (last two digits of your BYU ID) ÷ 40**

- BYU ID `123456789` → **89** → 1 + 89 ÷ 40 = **3.225**
- The **nine-digit number on your BYU ID card** — not your NetID
- Run 5 uses it; the grader checks your RMSE against your digits

<!-- The capture is the model as a tool, set up for run 5 with the example ID ending in 89. Everyone's other runs use the same hosted points and will match a classmate's to the centimeter; run 5 will not. The lab page gives the example's answer (IDW RMSE 20.29 m at power 3.225) so students can check their setup before they use their own digits. Every power falls between 1 and 3.475. -->

---

<!-- _class: quiz -->

# Lab 8 Step 8: Predict It

<style scoped>
section { font-size: 23px; }
</style>

![bg right:45% w:96%](images/ie-error-row.png)

Three knobs: **points** (250, 2,500, 10,000), **IDW power** (1, 2, 3, yours), **semivariogram model** (spherical, exponential, Gaussian). Change **one**, rerun, and ask: **does the winner change?**

At **2,500** points: Thiessen **28.29 m**, IDW **20.71 m**, kriging **14.46 m**

- Go to **10,000** points. Which method **gains the most**, and which the least?
- Raise IDW's power from 2 to **3**. Better, worse, or about the same?
- Where on the error map will the error that remains be?

<!-- Votes only; no answers today. These are the Lab 8 Step 8 questions in advance, so each student goes in with a prediction to test, which is the habit the lab is built around. Write the predictions on the board: if 2,500 points gives these RMSEs, what will 10,000 give? Ten times fewer? Half? Does every method gain the same amount? Come back to the board when the labs are in. The three baseline RMSEs are on the lab page as check values, so it is fine to show them. Merged October 26, 2026 with the "Three Knobs" slide, and the Part 4 divider folded into Part 5. -->

---

# How You Will Know You Are Right

![bg right:42% h:84%](images/ie-zonal-table.png)

- `True_DEM`: **67,337** cells, **1,368.5 to 2,896.5 m**
- Every RMSE table: **COUNT 67,337**
- 2,500 points, defaults: **28.29 / 20.71 / 14.46 m**
- Run 5 at the example power **3.225**: IDW **20.29 m**

<!-- All four are TIP boxes on the lab page. A COUNT below 67,337 means a surface does not cover the study area; an RMSE that matches to the meter but not the centimeter usually means a different neighbor count or a missed environment setting. -->

---

# Make It Yours

![bg right:45% w:96%](images/ie-example-scenario.png)

- The **numbers** will match your classmates'; the **choices** should not
- Your own **layout**, **color ramps**, **model labels**, and **words**
- Upload your **toolbox** (`Lab08.atbx`) — the grader runs it at your power
- **Peer review** before you submit, and name your reviewer

<!-- The figure is the lab page's example scenario sheet. It is one way to do Map 2, not a template to copy: submissions whose layouts, model labels or symbology match another student's too closely are flagged for follow-up. Say it plainly once, here. -->

---

<!-- _class: activity -->

# Final Thoughts

<div class="columns" style="grid-template-columns: 1.7fr 1fr; font-size: 0.82em;">
<div>

**Quiz: How Wrong Is the Surface?** Eight questions on kriging, error rasters, RMSE and where the error lives. **Scan the code**, or open the link under it.

- A quick check that today's material made sense
- Note the sign question: a wrong sign flips the whole map in Lab 8

**Before next class**

- **Quiz 7** — open book, Chapter 12, due **Saturday 11:59 pm**
- **Lab 8 — Interpolation Explorer** — due **Saturday 11:59 pm** — [Lab 8](https://byu-hydroinformatics.github.io/ce414-gis-applications/assignments/lab-08/)
- Next week: **no class meetings**; study the **cut, fill, and raster volumes** decks on your own, and **Lab 9 — Big Southern Butte**
- Office hours: [calendly.com/dan-ames/office-hours](https://calendly.com/dan-ames/office-hours)

</div>
<div>

![w:300 center](images/quiz-rmse-qr.png)

<span style="font-size: 0.45em; color: #4a5568;">byu-hydroinformatics.github.io/ce414-gis-applications/quizzes/rmse/</span>

</div>
</div>

<!-- Five minutes, in pairs, then a show of hands on the Gaussian item: it is the run Lab 8 Step 8 asks them to explain. If the room has no signal, put the URL on the board; the items read aloud just as well. -->

<!-- Week 9 due items from the DUE table in tools/build_schedule.py: Lab 8, Quiz 7 and Chapter 12 this Saturday. Deck written October 8, 2026; the kriging part, the six-methods test, the exactness slide and the tool table moved here from the Tuesday deck on October 20, 2026; the checkpoint, exactness, tool-table, variogram, 3D-kriging and service slides were cut October 26, 2026 to match the simplified Lab 8. October 28, 2026: neighbor-test variants and the bin-by-bin semivariogram added, pop-up questions on the kriged result and the error maps, the map-algebra diagram on the error slide, the four-step RMSE flow, What RMSE Hides cut, and the automatic-fit explanation added. Figures: tools/week09_interpolation_figures.py (error-row crop and the checkpoint test); the ArcGIS Pro captures are from the Lab 8 GUI build (docs/assignments/lab-08/images), copied into this folder. -->
