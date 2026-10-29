# Midterm 2 Study Guide

**Midterm 2** is a closed-book, concept-based exam in the Testing Center, 100 points. It opens
**Tuesday of Week 14 at 8:00 am** and closes **Thursday at 9:00 pm**; the Testing Center charges a
late fee from 2:00 pm Thursday, so go earlier. It covers **Weeks 8–13**.

**Conditions.** Paper and pencil, closed book and closed notes, with no computer, phone or other
device. **Bring a calculator**: any calculator is allowed, as long as it is not a phone. You have
**3 hours**, which is plenty: most students should finish in about half that.

**What the exam looks like.** **100 multiple-choice questions, 1 point each.** Every question has
four options and exactly one best answer. The questions are grouped by week, Week 8 through Week 13.
Some are built on ArcGIS Pro screenshots from the labs and lectures; one asks you to compare four
figures and pick the right one; and some are short hand calculations of the kind worked in class.
You mark your answers on the **Testing Center's answer sheet**, and only the answer sheet is scored.
Circle answers and do scratch work in the booklet as you go, but leave time at the end to copy every
letter onto the sheet.

**What is not on this exam.** **Coordinate systems, projections, datums and GPS** are not on
Midterm 2; those lectures were retired from this semester's schedule. **Lab 12 (Avalanche Hazard)**
is due the same week as the exam, so it is not on Midterm 2 either.

## How to study for this exam

- **Take your Learning Suite reading quizzes again**, especially Quiz 7 (Chapter 12) and Quiz 11
  (Chapter 14). A few questions come from the reading. Quiz 8 was built from the Week 10
  slides, and Quizzes 9 and 10 cover the Week 11 and 12 topics, so they are good practice too.
- **Retake the self-check quizzes** linked under each week below. Many exam questions test the same
  ideas, in different words.
- **Reread each lab's warnings and "Check the result" boxes.** Several questions are about the
  mistakes those boxes warn about: the setting that changes the answer without an error message, the
  default you were told to change, the step that, skipped, makes a number wildly wrong. For each lab,
  be able to say what the model does, why each tool is there, and what the sensitivity step showed.
- **Practice the hand calculations.** Work an IDW estimate with two different exponents, an RMSE
  from a handful of errors, the cut, fill and balance grade of a small level pad, an average end
  area, an accumulated cost along a row of cells and the cheapest path across a small grid, a HAND
  value and a flood depth from a gage height, and a skill score from three areas. Bring your
  calculator.
- **Read all four options before you choose.** The wrong options are mostly the mistakes students
  really make, so an option that looks right at first glance may be one of them.
- **Pace yourself.** 100 questions in 3 hours is almost two minutes each, with time left over to
  fill in the answer sheet.

**How to use the weekly lists.** Each week lists what you should be able to do. Turn every line into
a question and answer it out loud without notes. If you cannot, open that week's slides (press
<kbd>P</kbd> for the speaker notes, which carry the explanations) and the self-check quiz.

## Week 8 — Flood Mapping and HAND

*Slides:* [Part A](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-08/flood-models.html), [Part B](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-08/hand.html). *Self-check:* [Height Above What?](../quizzes/hand/index.html), [How Big, How High?](../quizzes/floods/index.html). *Lab:* [Lab 7](../assignments/lab-07/README.md).

- Say what a **100-year flood** is, as a probability, and what that means over a run of years
- Say what a stream gage measures, what a **rating curve** does, and why a flood flow above the top of the rating is the least certain number in the model
- Turn a flow into a gage height and a gage height into a flood **depth h**, as Lab 7 Step 1 does
- Say why a river is **not a bathtub**, and when a bathtub is the right model
- Define **HAND**, compute it for a cell from the river cell it drains to, and say which cells flood at a depth h
- Say how HAND is built from Lab 5's chain plus **Flow Distance**, and why the **stream definition** and the **filled** surface matter
- Score one flood map against another: **hit rate**, **false-alarm ratio** and **CSI**; say where HAND breaks and what 1-D and 2-D hydraulic models add
- For Lab 7: why it is **two models**, what passes between them, why the loop runs in centimeters, what the **Extent** environment, **Raster to Polygon**'s settings, **Collect Values** and **Spatial Join** each do

## Week 9 — Interpolation, Kriging and Error

*Reading:* Bolstad, Chapter 12. *Slides:* [Sampling, Nearest Neighbor, and IDW](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-09/interpolation.html), [Kriging and Interpolation Error](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-09/interpolation-explorer.html). *Self-check:* [Points Into Surfaces](../quizzes/interpolation/index.html), [How Wrong Is the Surface?](../quizzes/rmse/index.html). *Lab:* [Lab 8](../assignments/lab-08/README.md).

- Explain why we **sample** instead of measuring everywhere, and compare the four **sampling designs**
- Build a **Thiessen** surface and say what its shape looks like; compute an **IDW** estimate by hand and say what the **exponent** does
- Recognize the profile each method draws through the same points, and say which methods can go above the highest sample
- Say which methods give the **measured values back** (exact) and which do not
- Read a **semivariogram**: **nugget**, **sill**, **range**; say how **kriging** sets its weights, and what a large nugget does
- Compute an **error raster**, say what its **sign** means, and compute an **RMSE** by hand; say what the RMSE hides
- Say which surface to **trust**, and why holding points back is the honest test without the truth
- For Lab 8: the two Thiessen defaults that ruin the surface, why the IDW surface stays inside the samples' range, what the empty kriging boxes mean, why Zonal Statistics as Table uses **Mean**, what a short **COUNT** means, and what the elevation service sent in Step 1
- From the reading: tell **spatial interpolation** from **spatial prediction**; name a sampling design from a description; say why a sum of errors is a poor accuracy measure

## Week 10 — Cut, Fill and Raster Volumes

*Self-study week. Slides:* [Cut and Fill](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-10/cut-and-fill.html), [Volumes with Rasters](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-10/raster-volumes.html). *Self-check:* [Cut or Fill?](../quizzes/earthwork/index.html), [The Base Is the Answer](../quizzes/volumes/index.html). *Lab:* [Lab 9](../assignments/lab-09/README.md).

- Compute **cut** and **fill** from an existing and a design surface, cell by cell, and say whether soil is hauled on or off
- Find the **balance grade** of a level pad, and say why it is the mean and not the midpoint
- Read the sign of **Cut Fill**'s VOLUME
- Estimate road earthwork by **average end area**
- Say what a grid volume **leaves out**
- Write any raster volume as **height × cell area, summed**, and say why the DEM must be **projected** first
- Say when **Surface Volume** is enough, and why Lab 9 uses Raster Calculator and **Zonal Statistics** instead
- Explain why the **base surface** is the biggest choice in a mountain's volume, and what part of the butte the volume cannot see
- For Lab 9: the units of each Raster Calculator output, what Zonal Statistics with **Sum** writes, why the points on the butte are erased, and why a wider outline changes the volume; from the Thursday deck, what a spline base can do that an IDW base cannot

## Week 11 — Least Cost Paths

*Slides:* [Part A](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-11/least-cost-path.html), [Part B](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-11/least-cost-path-b.html). *Self-check:* [Cheapest or Shortest?](../quizzes/least-cost-path/index.html), [What Moved the Line?](../quizzes/cost-paths/index.html). *Lab:* [Lab 10](../assignments/lab-10/README.md).

- Say what a **cost surface** is, and why it is not a map of distance; build one by reclassifying and combining rasters, with **high = undesirable**
- Explain what the **accumulated cost** and **back direction** rasters each store, and read a back direction as a **compass angle**
- Compute an accumulated cost by hand, and trace the cheapest path from a destination back to its source
- Name ArcGIS Pro's current tools, **Distance Accumulation** and **Optimal Path As Line**, the legacy ones they replace, and how the two charge a step
- Tell a **barrier** from a **cost**
- Say which parts of a cost surface **move a route** and which only change its total, and why
- Map a **corridor** of nearly-as-good routes, and say what a wide or narrow corridor means
- For Lab 10: why the terrain enters as slope, what each score table says, what Distance Accumulation gives with no cost raster, how the river term in the cost expression works, how the weights enter, and which weight moved the route

## Week 12 — Network Analysis

*Slides:* [Part A](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-12/network-analysis-a.html), [Part B](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-12/network-analysis-b.html). *Self-check:* [Along the Roads](../quizzes/networks/index.html), [Four Minutes Away](../quizzes/service-areas/index.html). *Lab:* [Lab 11](../assignments/lab-11/README.md).

- Say what a **network dataset** is made of: **edges**, **junctions**, **connectivity**; say what a missing junction does
- Explain what an **impedance** is, and why minutes and meters give **different routes**
- Describe how **one-way streets** and **turns** enter a network, as costs or as walls
- Place network distance beside **straight-line** and **cost distance**, and say which fits a fire engine
- Say what the network does **not** know, and which way each gap moves an answer
- Run a **service area** in ArcGIS Pro: the analysis layer, **Add Locations**, **Solve**
- Say which solver answers which question: **Service Area**, **Closest Facility**, **Location-Allocation**, Route
- Explain why a **buffer** and a **service area** disagree about the same minutes, and turn minutes at a speed into a buffer distance
- For Lab 11: what the network's two costs and their evaluators show, what **Dissolve** and **Rings** do, what **Select Data** does, why each branch gets its own **Make Feature Layer**, what **Have their center in** and **invert** select, and what the cutoff runs show

## Week 13 — The Final Project

*Reading:* Bolstad, Chapter 14. *Slides:* [The Final Project](https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-13/final-project-introduction.html). *Self-check:* [Ready to Pitch?](../quizzes/final-project/index.html). *Project:* [Final Project](../assignments/final-project.md).

- Judge whether an idea is the right **scope** for the project, and say why displaying data is not analysis
- List the requirements every project must meet, including **raster and vector** data
- Say what to bring to the **proposal meeting**, including the **data-feasibility table**
- Say how you would show a result is right: a **validation** or **sensitivity** check
- From the reading: tell **precision** from **accuracy**; name the kinds of data error (**positional** and **attribute accuracy**, **completeness**, **logical consistency**); say what the OGC web services (**WMS**, **WFS**, **WPS**) each deliver
