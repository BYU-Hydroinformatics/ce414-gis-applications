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

## Later the same day: cuts to match the simplified Lab 8

Slide numbers above are from before this round. Once Lab 8 dropped its checkpoint test (October
23), the deck went from 36 numbered slides to 26: cut the Variogram, From Variogram to Surface (its
"like IDW, but the data set the weights" line moved to Kriged Result), Kriging Surface (3D), Hold
Points Back, Is 200 Checkpoints Enough?, Exact and Non-exact Methods, The Methods in ArcGIS Pro, the
Part 4 divider and Step 1 (the service). Three Knobs merged into "Lab 8 Step 8: Predict It", which
moved into the Lab 8 part (now Part 4). The six-methods slide gained a one-line caption on held-back
points. The RMSE quiz's two checkpoint items were replaced (where the error lives; what a Gaussian
model assumes), and the Lab 8 page's note, the Week 9 schedule blurbs and the Midterm 2 study guide
were updated to match.

## Part 1 rebuilt for tool users (October 26, 2026)

Students will run Kriging, not compute it, so Part 1 now walks from Tuesday's Provo worksheet to the
tool's settings: "Remember Provo?" (you trusted American Fork; IDW made that a fixed rule; kriging
asks the data how much), "The Neighbor Test" (one close pair, one far pair, then all 1,770 pairs of 60
made-up stations), "Average the Pairs: the Semivariogram" (nugget, range and sill in plain words,
with a click-in question), the three model shapes, and "Same Points, Different Settings" (one
dimension, kriged with the fitted model, a big nugget, a short range and a long range). Kriged
Result and the annotated Kriging dialog follow. Cut: the trend/autocorrelation/random
decomposition, Lag Distance, Spatial Autocorrelation, Semivariance (the equation) and the old
Nugget, Sill, and Range slide. Figures: tools/week09_kriging_story_figures.py, all made-up values.
