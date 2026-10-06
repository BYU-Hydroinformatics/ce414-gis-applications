# Quiz 6 — Watershed Delineation (multiple choice)

20 items, 1 point each: 14 from class and Lab 5, 6 from the reading (Bolstad & Manson, Hydrologic Functions section; no edition-specific page, figure or equation numbers). Correct answer in **bold**.

## 1. [From class]

A neighbor asks what a watershed is. Which explanation is right?

- A. The river channel and the floodplain on either side of it
- **B. All the land that drains to one outlet: rain falling anywhere inside it ends up flowing past that point**
- C. The land within a fixed distance of a river, set by the state
- D. The reservoirs and pipes that deliver a city's drinking water

> A watershed is defined by drainage, not by distance or ownership: it is all the land whose water reaches one outlet. Move the outlet and the watershed changes. Its boundary, the divide, runs along the ridges.

> *If A:* The channel and floodplain are only the wet bottom of a watershed; the hillslopes that drain into them are part of it too.

## 2. [From class]

John Wesley Powell proposed that western states be drawn along watershed boundaries. Which problem would that most directly have reduced?

- **A. Neighboring states fighting over rivers they share, since each state would govern the water it collects**
- B. The difficulty of surveying straight-line borders across mountains
- C. Unequal state populations, since each basin holds about the same number of people
- D. The cost of building roads across state lines

> In the arid West, water is the binding limit on settlement. A river split among several states is a river they compete for: upstream diversions are downstream shortages. Basin-shaped states would have kept the people who use a stream and the land that feeds it under one government. Congress did not adopt the idea, and a century of interstate compacts and lawsuits (the Colorado River is the famous one) followed.

## 3. [From class]

Hydrologic terrain processing has two goals and one motive. Which set is right?

- A. Goals: slope and aspect rasters. Motive: shaded relief maps
- B. Goals: a filled DEM and a flow direction grid. Motive: removing errors from the DEM
- C. Goals: a stream network and watershed boundaries. Motive: replacing stream gages
- **D. Goals: a stream network (polylines) and watershed boundaries (polygons). Motive: input data for hydrologic and rainfall-runoff models**

> Starting from a DEM, the two products are a potential flow path stream network and watershed boundaries. The reason to make them is usually to feed hydrologic and watershed models, such as rainfall-runoff prediction. Fill and flow direction are intermediate steps, not goals.

> *If C:* The goals are right, but a delineated network does not measure flow; it feeds the models that predict it, and gages are how those models are checked.

## 4. [From class]

The Provo subbasin is HUC8 16020203. Which of these could be the code of a HUC10 watershed inside it?

- A. 1602030305
- B. 160202030
- **C. 1602020305**
- D. 16020203

> Each level of the Watershed Boundary Dataset adds two digits to its parent's code. A HUC10 inside 16020203 must be ten digits long and start with 16020203. 1602020305 (Outlet Provo River) is one.

> *If A:* 1602030305 is ten digits, but it starts 160203, a different basin.

> *If B:* Nine digits is not a level; codes grow two digits at a time.

> *If D:* That is the HUC8 itself.

## 5. [From class]

You skip Fill and run Flow Direction and Flow Accumulation on the raw DEM. What goes wrong?

- A. Flow Direction refuses to run on an unfilled DEM
- B. Slope values come out in percent instead of degrees
- C. Nothing, as long as the area is mountainous
- **D. Water routed into each pit stops there, so accumulation below it collapses and the stream network breaks into disconnected pieces**

> A pit has no downhill neighbor, so it is a dead end in the flow direction tree. Everything upstream of it drains into it and is never passed on, so flow accumulation downstream is too small and the network stops at every pit. Fill raises each pit to its spill level so water can continue.

> *If A:* The tools run; they just give a broken answer, which is worse.

## 6. [From class]

A single DEM cell at 40 m is surrounded by eight neighbors at 46, 44, 47, 43, 45, 48, 49 and 50 m. After Fill, what is the cell's elevation?

- A. 40 m
- **B. 43 m**
- C. 46.5 m
- D. 50 m

> Fill raises a pit to its spill level, the elevation at which water would overflow it. For a one-cell pit that is its lowest neighbor, 43 m. Fill only raises cells, and only as far as needed; it never averages or lowers.

> *If A:* That is the pit before Fill: no neighbor is lower, so water cannot leave it.

> *If C:* 46.5 m is the average of the neighbors. Fill does not smooth; it raises to the spill level and no higher.

> *If D:* Water would spill out at the lowest point on the rim, 43 m, long before reaching 50 m.

## 7. [From the reading]

The textbook says conditioning removes pits shallower than a chosen depth and keeps deeper ones as real. Your lidar DEM's vertical errors are under 0.3 m, and every real pond in the area is at least 2 m deep. Which depth limit fits?

- A. 0.05 m
- B. 3 m
- **C. About 1 m**
- D. None: fill every pit

> The limit should be larger than the common vertical errors, so that spurious pits get removed, but smaller than any real pit, so that real ones are kept. Between 0.3 m and 2 m, about 1 m does both. In ArcGIS Pro this is the Z limit on the Fill tool.

> *If A:* Below the DEM's own errors: most spurious pits are deeper than 0.05 m and would be left in place.

> *If B:* Deeper than the real ponds: they would be filled away along with the errors.

> *If D:* Filling everything also removes the real ponds, which are part of the landscape.

## 8. [From the reading]

A highway embankment crosses a valley, and the creek passes under it through a culvert the DEM does not show. Which conditioning does the textbook prefer for this kind of pit?

- **A. Breach it: lower the cells along the steepest path through the embankment**
- B. Fill it: raise the valley behind the embankment to the top of the road
- C. Leave it, since the embankment is a real feature
- D. Raise the stream threshold until the gap disappears

> The textbook distinguishes the two cases. A small, isolated low spot from a data error is best filled. A narrow, high, linear barrier, usually a built feature with a culvert or other drain under it, is best breached: cutting a path through the barrier matches where the water really goes. Filling it instead turns the valley behind the road into a large false lake with no clear flow direction.

> *If B:* Filling would raise everything upstream of the road to the road's height: a flat false lake that does not exist.

## 9. [From the reading]

The textbook shows a stream network derived from a DEM in which a stream line stops at a sink, then starts again some distance downhill. Why does it start again?

- A. The drawing tool skips short gaps in a line
- **B. The sink keeps all the water above it, so the cells below it count only their own new contributing area and rejoin the network once that passes the threshold**
- C. The stream really does flow underground for that distance
- D. The threshold is lower below the sink

> Every cell above the sink drains into it and none drains out, so flow accumulation just below the sink starts over from the local hillslopes. A few cells farther down, enough new area drains in to pass the threshold again and a channel reappears, disconnected from the one above. The textbook's other example is a road crossing where the culvert is missing from the DEM.

> *If C:* Some streams do sink into karst, but here the gap comes from the DEM and the threshold, not from what the stream does underground.

## 10. [From class]

The center cell is 100 m on a 30 m grid. Its neighbors are: N 101, NE 102, E 96, SE 95, S 94, SW 92, W 98, NW 99. Using D8 (Esri codes: 1 E, 2 SE, 4 S, 8 SW, 16 W, 32 NW, 64 N, 128 NE), what code goes in the center cell?

- A. 8
- B. 2
- **C. 4**
- D. 64

> Compare drop per unit distance, and remember the run to a diagonal neighbor is 30√2 = 42.4 m. South: 6/30 = 0.200. Southwest: 8/42.4 = 0.189. East: 4/30 = 0.133. Southeast: 5/42.4 = 0.118. South is steepest, so the code is 4.

> *If A:* Southwest has the biggest elevation difference (8 m), but it is a diagonal: 8/42.4 = 0.189 is less steep than south's 6/30 = 0.200.

> *If D:* 64 is north, which is uphill (101 m). The code names where the water goes, not where it comes from.

## 11. [From class]

Which statement correctly contrasts terrain aspect with D8 flow direction for one cell?

- A. D8 fits a plane to the eight neighbors; aspect keeps the single steepest drop from the center cell
- B. They are the same calculation reported in different units
- C. Aspect uses only the four cardinal neighbors; D8 uses only the four diagonal neighbors
- **D. Aspect fits a plane to the eight neighbors and can point any of 360 degrees, never using the center cell; D8 keeps the single steepest drop from the center cell, so it can point only eight ways**

> Aspect is the direction of the plane fitted to the 3 × 3 window (the same partial derivatives as slope), so it is a continuous compass bearing and the center elevation does not enter it. D8 asks a simpler question: from the center cell, which one of the eight neighbors has the steepest drop? On the same cell they can disagree; the Rock Canyon example in class had an aspect of 250 degrees and a D8 direction of southwest.

## 12. [From the reading]

The textbook notes that flow direction is often set equal to the local aspect, but that this can be wrong in some places. In which setting does it say aspect is a reasonable approximation of flow direction?

- **A. Steep, undeveloped terrain**
- B. Nearly flat farmland
- C. A city drained by ditches, culverts and storm sewers
- D. Flat ground over soils of very different permeability

> In steep, undeveloped terrain the downslope pull of gravity dominates, and surface and subsurface flow tend to go the same way, so aspect is a fair approximation. It breaks down on nearly flat ground, where soil permeability can steer water below the surface somewhere else, and in built areas, where ditches, culverts and storm sewers move water in ways the terrain does not show.

## 13. [From the reading]

The textbook contrasts D8 with the D-infinity method, which splits a cell's flow between the two neighbors on either side of its steepest downhill direction, giving the larger share to the neighbor closer to that direction. A cell's steepest downhill direction is an azimuth of 105°, between its east neighbor (90°) and its southeast neighbor (135°). How does D-infinity divide the cell's flow?

- A. All of it to the east neighbor
- B. One-third to the east neighbor and two-thirds to the southeast neighbor
- **C. Two-thirds to the east neighbor and one-third to the southeast neighbor**
- D. Half to each

> D-infinity splits the flow between the two neighbors on either side of the steepest direction, in proportion to how close the direction is to each. 105° is 15° from east and 30° from southeast, so east, the closer one, gets 30/45 = 2/3 and southeast gets 15/45 = 1/3. D8 would send all of it east. Splitting is how D-infinity represents divergent flow, which D8 cannot.

> *If A:* That is the D8 answer: all flow to the single neighbor closest to the steepest direction.

> *If B:* That gives the larger share to the farther neighbor. The closer direction (east, 15° away) gets the larger share.

## 14. [From class]

On a 10 m DEM, a cell's Esri flow accumulation value is 5,000. What does that tell you?

- A. 5,000 cubic meters of water flow through it each year
- **B. 5,000 upstream cells drain through it, a contributing area of 0.5 km²**
- C. 5,000 upstream cells drain through it, a contributing area of 50,000 m²
- D. The cell is 5,000 m from the watershed divide

> Flow accumulation counts cells, not water: it is the number of upstream cells whose flow path passes through this one (in Esri's convention the cell itself is not counted, so ridge cells are 0). Multiply by the area of one cell to get contributing area: 5,000 × (10 m × 10 m) = 500,000 m² = 0.5 km².

> *If C:* Each cell is 10 m × 10 m = 100 m², not 10 m²: 5,000 × 100 = 500,000 m².

## 15. [From Lab 5]

Lab 5 uses a stream threshold of 5,000 cells on a 10 m DEM. You rerun the model on a 30 m DEM of the same area and want streams to start at the same contributing area. About what threshold should you use?

- A. 5,000 cells
- B. 15,000 cells
- C. 1,667 cells
- **D. 556 cells**

> A threshold in cells is really a threshold in area. 5,000 cells × 100 m² = 500,000 m². A 30 m cell covers 900 m², so the same area is 500,000 / 900 = about 556 cells. When cell size changes, convert the threshold through area.

> *If A:* Keeping 5,000 cells on 30 m cells means 4.5 km², nine times the area, and a much sparser network.

> *If B:* Larger cells need fewer of them to cover the same area, not more.

> *If C:* Cell area grows with the square of the cell size: 30 m cells are 9 times the area of 10 m cells, not 3 times.

## 16. [From class]

How could you tell whether your stream threshold is realistic for your study area?

- **A. Overlay the network on mapped streams (the NHD) and imagery or topography, and adjust until channels begin about where real channels begin**
- B. Use the lowest threshold the computer can handle so no stream is missed
- C. Use the tool's default value, since it is calibrated for the United States
- D. Rerun Fill until the stream network stops changing

> The threshold is a judgment call, so it has to be checked against something independent of the DEM: the National Hydrography Dataset, aerial imagery, contour crenulations on a topographic map, or field observation. If the generated channels start far above where real channels start, the threshold is too low; if real channels are missing, it is too high.

> *If B:* A very low threshold draws a channel down nearly every hillslope hollow, most of which never carry a stream.

## 17. [From the reading]

The textbook's wetness index is w = ln(SCA / tanβ), where the specific catchment area SCA = AREA / C, AREA is the accumulated area upstream and C is the cell size. A cell on a 10 m grid has 50,000 m² of accumulated area upstream and a slope with tanβ = 0.10. What is w?

- A. 6.2
- **B. 10.8**
- C. 8.5
- D. 13.1

> SCA = 50,000 m² / 10 m = 5,000 m. Then SCA / tanβ = 5,000 / 0.10 = 50,000, and ln(50,000) = 10.8. The index is high where a lot of area drains in and the slope is gentle, which is where soils stay wet.

> *If A:* 6.2 is ln(5,000 × 0.10): that multiplies by the slope, which is the stream power index (SPI = SCA × tanβ), not the wetness index.

> *If C:* 8.5 is ln(5,000): the slope was left out.

> *If D:* 13.1 is ln(500,000): the area was not divided by the cell size C first.

## 18. [From class]

Pour point A is on one tributary and pour point B is on another, both above the junction where they meet. Point C is below the junction. Which is true?

- A. The watersheds of A and B overlap where the tributaries meet
- B. The watershed of C is smaller than A's, because C is lower
- C. A, B and C all have the same watershed, since they are on the same river system
- **D. The watersheds of A and B do not overlap, and the watershed of C contains both of them**

> Each cell drains along one path, so it belongs to the watershed of A or of B, never both. Everything that reaches A or B keeps flowing past the junction to C, so C's watershed contains both, plus whatever drains in between. That nesting is why subwatersheds tile a basin with no gaps and no overlaps.

## 19. [From Lab 5]

In Lab 5, Snap Pour Point moves your outlet up to 50 m. Where does it move it?

- A. To the nearest point on the NHD stream line
- B. To the lowest-elevation cell within 50 m
- **C. To the cell with the highest flow accumulation within 50 m**
- D. To the center of the nearest cell

> Snap Pour Point searches the snap distance for the cell with the largest flow accumulation, which is the channel. An outlet left one cell off the channel would return the watershed of a few hillslope cells instead of the basin.

> *If A:* The tool works on the flow accumulation raster, not on any vector stream layer.

## 20. [From Lab 5]

Lab 5 makes one subwatershed per stream link with a second run of the Watershed tool. What is its pour point input?

- **A. The Stream Link raster, so each link acts as the outlet of its own subwatershed and passes on its ID**
- B. The snapped outlet point
- C. The flow accumulation raster
- D. The basin polygon

> Stream Link gives every segment its own number. Used as the pour points for Watershed, each link collects the cells that drain to it, and the resulting subwatershed carries that link's number, which is how the subwatersheds and the streams join.
