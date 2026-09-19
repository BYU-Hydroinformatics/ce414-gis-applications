# Lab 3, expansion proposal

> **DECIDED 2026-09-18 by the instructor.** Lab 3 stays a manual, one-week lab: **no ModelBuilder**
> (Proposal 3 rejected), no five-run sensitivity with re-tracing. Kept, in manual form: drawn check
> features, one measured polygon (Calculate Geometry by hand, uncertainty by perimeter × error rather
> than a Buffer envelope), control points varied alongside the transformation in three runs, the
> Stansbury sheet as worked example, the graticule extra credit. New: attributes on every digitized
> feature. The round-2 draft (`docs/assignments/lab-03/draft.md`) implements this. What follows is
> the proposal as written, kept for the record.

Instructor-facing. Written 2026-09-18 in response to three observations from the instructor: that
the sensitivity step amounts to doing the same thing two or three times, that Lab 3 is materially
easier than Lab 1, and that georeferencing and digitizing ought to lead to *measuring* something.
Nothing here is built yet. Decisions are marked **DECISION**.

## What is actually wrong with the lab

Lab 3 is easier than Lab 1 for a reason that is structural, not cosmetic. Section 1 of
`tools/lab-conversion-guide.md` says every lab in this course has the same spine, and the first item
is "one model, built once, built to be changed." Lab 3 says, in its own Analysis Tools section,
"There is no ModelBuilder model in this lab." It is the only lab that opts out of the spine, and
that is most of the difficulty gap. Lab 1 makes a student chain seven tools and then re-run the
chain; Lab 3 asks for a sequence of interactive clicks that produce a picture.

The second problem is that Step 8's sensitivity axis is **cheap**. Changing the transformation is a
menu selection. The student re-solves with the same points, looks at a different number, and writes
a sentence. Nothing they did is at stake, so nothing is learned about their own judgment. Compare
Lab 1, where changing the distance threshold changes which site you recommend.

The third problem is that the lab produces no quantity. A student finishes with a map and an RMS
value that the lab has just told them not to trust. There is no engineering result.

## Proposal 1 — vary the control points, not only the transformation

The real decision in georeferencing is not which equation to pick. It is **how many points to
collect and where to put them**. That is the choice that costs the student something, and it is free
to vary once the points exist: delete some, re-solve.

Replace the single-axis Step 8 table with runs over two axes:

| Run | Control points | Transformation |
| --- | --- | --- |
| A | 3, clustered near the middle of the sheet | 1st order (affine) |
| B | 4, at the corners only | 1st order (affine) |
| C | all 8 or more, spread | 1st order (affine) |
| D | all 8 or more, spread | 2nd order polynomial |
| E | all 8 or more, spread | Spline |

Recorded for each: total RMS error, and the error at **two or three held-out check features**, one
of them deliberately near a corner.

The finding the student should reach on their own: **RMS falls as the points cluster and rises as
they spread, while the error at the check features does the opposite.** The number the software
reports and the accuracy the student actually has move in opposite directions. Run A will look the
best and be the worst. That inversion is the lesson, it is measurable, and no amount of
transformation shopping demonstrates it.

The existing TIP hint would become something like "one of these runs will give you the best number
you see all lab, and it is the one you should trust least."

## Proposal 2 — measure what you digitized

This is the instructor's idea and it is the one that turns the lab into engineering. Once features
are digitized, measure them, and measure them **under more than one georeference**.

Add to Step 6 a requirement that at least one digitized feature be *measurable and comparable*:
a closed polygon (a lake, a town site, a parcel block) or a line with a modern counterpart (a rail
grade, a road, a channel). Then **Calculate Geometry** for its length or area, in stated units, and
compare against the modern equivalent.

The point is not the measurement. The point is that **the measurement moves when the georeference
moves**, and the student can put a percentage on it:

> Under run C my 1852 shoreline encloses 4,900 square kilometers. Under run A it encloses 5,400.
> The difference is 10 percent and none of it is the lake changing — it is my control points.

That sentence is worth more than the whole current Step 8.

### Why the Stansbury sheet is the right vehicle

Digitize the 1852 Great Salt Lake shoreline and measure the area it encloses. The lake today is
dramatically smaller. The student is then holding two numbers and one genuinely hard question:

**Is the lake smaller, or is my map wrong? How much of each?**

That is a real civil and environmental engineering question with current relevance, it has no clean
answer, two defensible students can disagree, and answering it *requires* the error analysis the lab
has been teaching. It is the "where the method breaks" item of the spine, arriving with a number
attached instead of a paragraph.

### The effect is big enough to carry a lab — worked from this sheet

The size of the effect does not have to be taken on faith. The Stansbury sheet has already been
georeferenced two ways, and the areas they imply differ substantially.

The area a digitized polygon encloses scales with the product of the two axis scales, so the ratio
between the two georeferences follows directly from them, whatever the polygon is — the shoreline's
own accuracy cancels out:

| | Longitude scale | Latitude scale |
| --- | ---: | ---: |
| Fitted to the printed graticule | 2.428e-4 deg/px | 1.820e-4 deg/px |
| Fitted to three ground features | about 2.05e-4 deg/px | about 1.90e-4 deg/px |

That puts the same digitized shoreline at roughly **10 to 20 percent** more enclosed area under the
graticule georeference than under the ground-feature one. The range is wide because the ground fit
rests on three hand-measured positions; a student collecting proper control points would pin it
tighter, which is the exercise.

Ten to twenty percent is far larger than any plausible digitizing sloppiness, and it is produced
entirely by a choice the student made about control points. It is also the right order to be
genuinely confusable with real hydrological change, which is what makes the question honest rather
than rhetorical.

## Proposal 3 — restore the model spine with a measurement model

Georeferencing cannot be a model; it is interactive by nature, and the lab is right about that. But
**the measurement half can be**, and that is what puts Lab 3 back on the course spine and closes most
of the difficulty gap with Lab 1.

A small ModelBuilder model, with the digitized feature class as an exposed **parameter**:

- digitized features (P) into Calculate Geometry, then Summary Statistics, giving area or length
- the same features into Symmetrical Difference against the modern layer, giving area gained and lost

The student builds it once and runs it once per georeference from its tool dialog. That is exactly
the "built once, built to be changed" argument the other labs make, and it makes the sensitivity
runs cheap, which is the stated reason to bother with parameters at all.

It also gives the rubric back its "ModelBuilder model — correct and working" row, the full-page model
figure and the toolbox interface capture, none of which Lab 3 has an equivalent of today.

**DECISION:** whether to require the model or offer it. A lighter version — Calculate Geometry by
hand, once per run, no model — gets most of Proposal 2's value at perhaps a third of the work. If
the concern is that the lab is too easy, the model is the answer; if the concern is the calendar,
the light version is.

## Proposal 4 — the anchoring problem, as the capstone

See `GEOREF_FINDINGS.md`. Georeferencing the Stansbury sheet from its own printed graticule produced
latitudes accurate to 60 meters and longitudes out by 10 to 19 kilometers, growing steadily westward
— the sheet carries both a longitude shift and a longitude scale error, while its latitudes and its
internal geometry are sound. A least-squares fit to that graticule would report an RMS error near
zero throughout, because the graticule itself is drawn very regularly.

**Near-zero RMS, and the map is kilometers out of place.** That is the lab's Step 5 warning
happening for real, on a sheet the students can download.

This is worth a slide in the Week 4 Tuesday deck at minimum. It may be worth an optional
extra-credit part: georeference from the graticule, georeference from ground features, and report
the difference between the two — which *is* the sheet's survey error, separated out. That is a
genuinely advanced idea and it is the sanctioned five-point optional extra, not a required part.

## Proposal 5 — the counter-example, in class

The 1891 Wellge bird's-eye of Salt Lake City is downloaded and ready. Five minutes in class: add
control points to it, watch the RMS climb, watch the sheet tear, and ask why. The street grid
visibly converges to a vanishing point, so scale varies continuously across the image and no
transformation in the menu can fit it. It makes the Data section's warning something students have
seen fail rather than been told about.

## What this would do to the page

Sketch, not a commitment:

- Steps 0 to 5 unchanged (find, add, fit to display, control points, residuals)
- Step 6 digitize — adds the requirement that one feature be measurable
- Step 7 name and label — unchanged
- **Step 8 new** — build the measurement model, expose the input as a parameter
- **Step 9 new sensitivity** — the five runs of Proposal 1, the model run on each, one table carrying
  RMS, check-feature errors *and* the measured quantity
- Step 10 — which run you defend, what accuracy you claim, and the lake question

Rubric stays five rows of ten. Suggested rebalance: Write-up / Georeferencing / Digitizing and
measurement / Map 1 / Sensitivity. The measurement model's figure and toolbox capture move into row
three, which currently grades digitizing alone and is the lightest row on the page.

**DECISION — the real risk is size.** This turns a one-week lab into something closer to Lab 1,
which is what was asked for, but Lab 3 is due in Week 4 and shares that week with the remote sensing
deck. Options: keep the expansion and move some of it to extra credit; keep it and accept Lab 3 as a
two-week lab; or adopt Proposals 1 and 2 now, which need no model and little new page, and hold
Proposal 3 for the next offering.

## Open questions for the instructor

1. Model or no model — Proposal 3's DECISION above. This is the one that decides the lab's size.
2. Is the Great Salt Lake shrinkage question the right spine for the lab, or too close to a
   politically warm topic for a required deliverable?
3. Should the prepared Stansbury sheet be hosted in `docs/data/` so every student works the same
   sheet, or does the lab keep its "you find the data and you defend it" character? Hosting it makes
   check values possible for the first time in this lab — there are none today.
4. Is five sensitivity runs too many? Three would still show the inversion if they are A, C and E.
