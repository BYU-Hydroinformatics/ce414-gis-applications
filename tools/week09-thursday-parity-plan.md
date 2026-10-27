# Week 9 Thursday deck: parity with Tuesday (October 26, 2026)

On October 26 the Tuesday deck (`slides/week-09/interpolation.md`) got a round of instructor-requested
improvements. This note records how the same kinds of changes were carried over to the Thursday
deck (`slides/week-09/interpolation-explorer.md`), and the judgment calls made along the way, for
review before Thursday's class. Slide numbers are the ones printed on the slides.

## What Tuesday got, and what Thursday got to match

| Tuesday change | Thursday counterpart |
| --- | --- |
| Scanned textbook figures redrawn as our own (the IDW worked example; its printed answer of 34 was wrong, 39.5 is right) | All four Bolstad scans in the kriging part redrawn by `tools/week09_thursday_figures.py`: lag distance (4), spatial autocorrelation (5), the semivariance equation (6, now written 1/(2n) so it cannot be read as n/2) and the variogram (7). Their numbers were checked: the lag distances are measured from the drawing |
| Red arrows and short notes on ArcGIS Pro dialogs | Kriging (13), the error Raster Calculator (15), the Square Raster Calculator (17) and Zonal Statistics as Table (18), all by `tools/week09_dialog_callouts.py`; captures untouched |
| Click-in questions and answers (what happens when n gets big, or goes to 0) | Questions already sitting in the speaker notes became click-ins: "What would put a nugget here?" (8), "A cell reads +40 m. Too high or too low?" (15), "Why is the valley floor nearly white?" (16), "Why is one kriging panel flat?" (22) |
| "Try it on your worksheet" pop-ups | Slide 15: subtract each of your Provo estimates from Provo's actual temperature and read the sign, on Tuesday's worksheet |
| "Class Vote" became "Which Sampling Design Is Best and Why? / Discuss with your neighbor", with "it depends" answers animated in afterward and a note that every design uses the same points | "Class Vote: Which Interpolation Method Works Best Here?" became "Which Method Is Best and Why? / Discuss with your neighbor" (21), with four answers to click in and "Every method uses the same 150 sample points". It also moved from after the exactness slide to the start of Part 3, because by then the six-methods scores had already given the answer away |
| Removed a preview of a term not yet taught (kriging, on the exactness slide) | Dropped Natural Neighbor from the ArcGIS Pro methods table (26): the class never meets it |
| One or two bold key words on every text block | Added to the few all-plain blocks (lag distance, autocorrelation, semivariance, variogram) |
| Quiz checked against the slides | All seven RMSE-quiz items are covered. Two depend on slides the notes marked optional (19, What RMSE Hides; 24, Is 200 Checkpoints Enough?); those notes now say to keep them |
| New figures saved under new file names, so browsers cannot show a cached old picture | Every new or annotated image has a name that never existed before |

Also: "semi-variance" is now spelled "semivariance" throughout, as Esri does, except where a
slide quotes ArcGIS Pro's own "Semi-variogram model" label.

## Left alone, on purpose

- **The section-divider cartoons.** Unlike Tuesday's bedsheet, each one reads at a glance (a
  detective linking pins with yarn, a terrain being graded, a terrain lineup, a map dodging balls, an
  explorer on a mountain of points).
- **Predict It (29).** It is already a "write down your prediction" slide for Lab 8 Step 8, with no
  answers on purpose.
- **Lab 8 slides (31–35).** They mirror the lab page; changes belong there first.

## For the instructor to decide

- **Bold color.** Thursday's front matter sets `strong` to the brighter BYU blue (`#0062b8`);
  Tuesday uses the theme's navy (`#002e5d`). Pick one for both decks (and for the slide guide's
  rule 4).
- **The worksheet tie-in on slide 15** assumes students kept Tuesday's paper worksheet after
  photographing it.
