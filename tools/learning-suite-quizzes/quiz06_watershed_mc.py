"""Quiz 6 (Watershed Delineation) as 20 auto-graded multiple-choice items, packaged as QTI 2.2
in the same shape Learning Suite exports (see the Quiz 5 export): one Q<n>.xml per item, an
imsmanifest.xml, per-choice modal feedback, 1 point per item.

Replaces the eight open-ended Quiz 6 prompts. Every computed answer is checked by an assert below.

Run:  python tools/learning-suite-quizzes/quiz06_watershed_mc.py [out_dir]
Writes Quiz6-WatershedDelineation-MC.zip and quiz06_review.md into out_dir (default: this folder).
"""
import math
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent

# ---- checks on every computed answer ---------------------------------------------------------
# Q8: Fill raises a one-cell pit to its lowest neighbor (the spill level).
FILL_NB = [46, 44, 47, 43, 45, 48, 49, 50]
assert min(FILL_NB) == 43 and sum(FILL_NB) / 8 == 46.5
# Q10: D8 on 30 m cells; drops per unit run, diagonals over 30*sqrt(2).
c, d = 100, 30 * math.sqrt(2)
d8 = {"E (1)": (100 - 96) / 30, "SE (2)": (100 - 95) / d, "S (4)": (100 - 94) / 30, "SW (8)": (100 - 92) / d,
      "W (16)": (100 - 98) / 30, "NW (32)": (100 - 99) / d, "N (64)": (100 - 101) / 30, "NE (128)": (100 - 102) / d}
assert max(d8, key=d8.get) == "S (4)" and round(d8["S (4)"], 3) == 0.200 and round(d8["SW (8)"], 3) == 0.189
# Q13: codes 2 (SE), 4 (S), 1 (E) -> 2 east, 2 south.
step = {1: (1, 0), 2: (1, 1), 4: (0, 1), 8: (-1, 1), 16: (-1, 0), 32: (-1, -1), 64: (0, -1), 128: (1, -1)}
assert tuple(map(sum, zip(*(step[k] for k in (2, 4, 1))))) == (2, 2)
# Q14 / Q15: 5,000 cells of 10 m = 0.5 km2; the same area on 30 m cells.
assert 5000 * 10 * 10 == 500_000 and round(500_000 / 900) == 556

# ---- the items --------------------------------------------------------------------------------
# (tag, prompt, [choices], index of correct choice, explanation, {choice index: extra note when picked})
Q = [
    ("From class",
     "A neighbor asks what a <em>watershed</em> is. Which explanation is right?",
     ["The river channel and the floodplain on either side of it",
      "All the land that drains to one outlet: rain falling anywhere inside it ends up flowing past that point",
      "The land within a fixed distance of a river, set by the state",
      "The reservoirs and pipes that deliver a city's drinking water"],
     1,
     "A watershed is defined by drainage, not by distance or ownership: it is all the land whose water reaches one outlet. "
     "Move the outlet and the watershed changes. Its boundary, the divide, runs along the ridges.",
     {0: "The channel and floodplain are only the wet bottom of a watershed; the hillslopes that drain into them are part of it too."}),
    ("From class",
     "John Wesley Powell proposed that western states be drawn along watershed boundaries. Which problem would that most directly have reduced?",
     ["Neighboring states fighting over rivers they share, since each state would govern the water it collects",
      "The difficulty of surveying straight-line borders across mountains",
      "Unequal state populations, since each basin holds about the same number of people",
      "The cost of building roads across state lines"],
     0,
     "In the arid West, water is the binding limit on settlement. A river split among several states is a river they compete for: "
     "upstream diversions are downstream shortages. Basin-shaped states would have kept the people who use a stream and the land that feeds it "
     "under one government. Congress did not adopt the idea, and a century of interstate compacts and lawsuits (the Colorado River is the famous one) followed.",
     {}),
    ("From class",
     "Hydrologic terrain processing has two goals and one motive. Which set is right?",
     ["Goals: slope and aspect rasters. Motive: shaded relief maps",
      "Goals: a filled DEM and a flow direction grid. Motive: removing errors from the DEM",
      "Goals: a stream network (polylines) and watershed boundaries (polygons). Motive: input data for hydrologic and rainfall-runoff models",
      "Goals: a stream network and watershed boundaries. Motive: replacing stream gages"],
     2,
     "Starting from a DEM, the two products are a <em>potential flow path</em> stream network and watershed boundaries. The reason to make them is "
     "usually to feed hydrologic and watershed models, such as rainfall-runoff prediction. Fill and flow direction are intermediate steps, not goals.",
     {3: "The goals are right, but a delineated network does not measure flow; it feeds the models that predict it, and gages are how those models are checked."}),
    ("From class",
     "The Provo subbasin is HUC8 <strong>16020203</strong>. Which of these could be the code of a HUC10 watershed inside it?",
     ["1602030305", "160202030", "16020203", "1602020305"],
     3,
     "Each level of the Watershed Boundary Dataset adds two digits to its parent's code. A HUC10 inside 16020203 must be ten digits long and start with "
     "16020203. 1602020305 (Outlet Provo River) is one.",
     {0: "1602030305 is ten digits, but it starts 160203, a different basin.",
      1: "Nine digits is not a level; codes grow two digits at a time.",
      2: "That is the HUC8 itself."}),
    ("From class",
     "Two HUC12 subwatersheds have codes that share the same first ten digits. What does that tell you?",
     ["They have the same area",
      "They lie in the same HUC10 watershed",
      "One drains directly into the other",
      "They are in the same state"],
     1,
     "The code is read like an address: each pair of digits narrows it one level. Two HUC12s that share their first ten digits share a parent HUC10. "
     "The code says nothing about their size, and units in the same parent are not necessarily upstream and downstream of each other.",
     {}),
    ("From class",
     "An engineer has only a 1 m DEM of a hillside building site. Which question can the DEM answer by itself?",
     ["How much of the rain on the site will evaporate",
      "How much of the rain will soak in and recharge groundwater",
      "Which side of the ridge the site's runoff will flow toward",
      "How much snow the site stores each winter"],
     2,
     "Of the water-balance terms, a DEM speaks only to where the water that runs off will go: flow paths, divides and outlets. "
     "Evapotranspiration, infiltration and snow storage need other data, such as weather stations, soil surveys and snow surveys.",
     {}),
    ("From class",
     "You skip Fill and run Flow Direction and Flow Accumulation on the raw DEM. What goes wrong?",
     ["Flow Direction refuses to run on an unfilled DEM",
      "Water routed into each pit stops there, so accumulation below it collapses and the stream network breaks into disconnected pieces",
      "Slope values come out in percent instead of degrees",
      "Nothing, as long as the area is mountainous"],
     1,
     "A pit has no downhill neighbor, so it is a dead end in the flow direction tree. Everything upstream of it drains into it and is never passed on, "
     "so flow accumulation downstream is too small and the network stops at every pit. Fill raises each pit to its spill level so water can continue.",
     {0: "The tools run; they just give a broken answer, which is worse."}),
    ("From class",
     "A single DEM cell at 40 m is surrounded by eight neighbors at 46, 44, 47, 43, 45, 48, 49 and 50 m. After Fill, what is the cell's elevation?",
     ["40 m", "43 m", "46.5 m", "50 m"],
     1,
     "Fill raises a pit to its spill level, the elevation at which water would overflow it. For a one-cell pit that is its lowest neighbor, 43 m. "
     "Fill only raises cells, and only as far as needed; it never averages or lowers.",
     {0: "That is the pit before Fill: no neighbor is lower, so water cannot leave it.",
      2: "46.5 m is the average of the neighbors. Fill does not smooth; it raises to the spill level and no higher.",
      3: "Water would spill out at the lowest point on the rim, 43 m, long before reaching 50 m."}),
    ("From class",
     "Some pits are real and some are artifacts of how the DEM was made. Which of these is most likely an artifact?",
     ["The Great Salt Lake, which has no outlet",
      "A sinkhole in limestone terrain",
      "A closed playa basin in western Utah",
      "A low spot upstream of a road embankment where the DEM does not show the culvert under the road"],
     3,
     "A DEM records the top of the road fill, not the culvert through it, so the embankment looks like a dam and the creek above it becomes a pit. "
     "Terminal lakes, sinkholes and playas are real closed basins. Fill treats both kinds the same, which is why it has an optional Z limit.",
     {}),
    ("From class",
     "The center cell is 100 m on a 30 m grid. Its neighbors are: N 101, NE 102, E 96, SE 95, S 94, SW 92, W 98, NW 99. "
     "Using D8 (Esri codes: 1 E, 2 SE, 4 S, 8 SW, 16 W, 32 NW, 64 N, 128 NE), what code goes in the center cell?",
     ["8", "4", "2", "64"],
     1,
     "Compare drop per unit distance, and remember the run to a diagonal neighbor is 30&#x221A;2 = 42.4 m. "
     "South: 6/30 = 0.200. Southwest: 8/42.4 = 0.189. East: 4/30 = 0.133. Southeast: 5/42.4 = 0.118. South is steepest, so the code is 4.",
     {0: "Southwest has the biggest elevation difference (8 m), but it is a diagonal: 8/42.4 = 0.189 is less steep than south's 6/30 = 0.200.",
      3: "64 is north, which is uphill (101 m). The code names where the water goes, not where it comes from."}),
    ("From class",
     "Which statement correctly contrasts terrain <em>aspect</em> with <em>D8 flow direction</em> for one cell?",
     ["Aspect fits a plane to the eight neighbors and can point any of 360 degrees, never using the center cell; D8 keeps the single steepest drop from the center cell, so it can point only eight ways",
      "D8 fits a plane to the eight neighbors; aspect keeps the single steepest drop from the center cell",
      "They are the same calculation reported in different units",
      "Aspect uses only the four cardinal neighbors; D8 uses only the four diagonal neighbors"],
     0,
     "Aspect is the direction of the plane fitted to the 3 &#xD7; 3 window (the same partial derivatives as slope), so it is a continuous compass bearing "
     "and the center elevation does not enter it. D8 asks a simpler question: from the center cell, which one of the eight neighbors has the steepest drop? "
     "On the same cell they can disagree; the Rock Canyon example in class had an aspect of 250 degrees and a D8 direction of southwest.",
     {}),
    ("From class",
     "Aspect can point in any of 360 directions; D8 only eight. Why do hydrology tools route water with D8 anyway?",
     ["D8 is more accurate than aspect on every slope",
      "Aspect cannot be computed on a filled DEM",
      "To accumulate flow, each cell's water must be handed to one specific neighbor; a D8 code names that cell, and a bearing like 250 degrees does not",
      "Aspect is reported in percent, which the routing tools cannot read"],
     2,
     "Routing means building the tree of which cell drains into which, so that flow accumulation can count what passes through each cell. "
     "D8 gives every cell exactly one downstream cell. A bearing of 250 degrees falls between two neighbors and does not say which one receives the water. "
     "The price is that D8 can only point eight ways, which is why D8 flow paths look blocky on smooth hillslopes.",
     {0: "Not on every slope: on a smooth hillside facing 250 degrees, D8 must choose 225 or 270, so it is less exact about direction. Its advantage is that it routes."}),
    ("From class",
     "Water leaves a cell whose D8 code is 2. The cell it enters holds 4, and the next one holds 1. Where is the water now, relative to where it started?",
     ["One cell east and two cells south",
      "Two cells east and two cells south",
      "Two cells west and two cells south",
      "Seven cells east, the sum of the codes"],
     1,
     "2 is southeast (one east, one south), 4 is south (one south), 1 is east (one east). Together: two east and two south. "
     "The codes are labels for directions, not distances, so they are never added.",
     {}),
    ("From class",
     "On a 10 m DEM, a cell's Esri flow accumulation value is 5,000. What does that tell you?",
     ["5,000 cubic meters of water flow through it each year",
      "5,000 upstream cells drain through it, a contributing area of 0.5 km&#xB2;",
      "5,000 upstream cells drain through it, a contributing area of 50,000 m&#xB2;",
      "The cell is 5,000 m from the watershed divide"],
     1,
     "Flow accumulation counts cells, not water: it is the number of upstream cells whose flow path passes through this one (in Esri's convention the cell itself is not counted, "
     "so ridge cells are 0). Multiply by the area of one cell to get contributing area: 5,000 &#xD7; (10 m &#xD7; 10 m) = 500,000 m&#xB2; = 0.5 km&#xB2;.",
     {2: "Each cell is 10 m &#xD7; 10 m = 100 m&#xB2;, not 10 m&#xB2;: 5,000 &#xD7; 100 = 500,000 m&#xB2;."}),
    ("From Lab 5",
     "Lab 5 uses a stream threshold of 5,000 cells on a 10 m DEM. You rerun the model on a 30 m DEM of the same area and want streams to start at the same contributing area. "
     "About what threshold should you use?",
     ["5,000 cells", "15,000 cells", "1,667 cells", "556 cells"],
     3,
     "A threshold in cells is really a threshold in area. 5,000 cells &#xD7; 100 m&#xB2; = 500,000 m&#xB2;. A 30 m cell covers 900 m&#xB2;, so the same area is "
     "500,000 / 900 = about 556 cells. When cell size changes, convert the threshold through area.",
     {0: "Keeping 5,000 cells on 30 m cells means 4.5 km&#xB2;, nine times the area, and a much sparser network.",
      1: "Larger cells need fewer of them to cover the same area, not more.",
      2: "Cell area grows with the square of the cell size: 30 m cells are 9 times the area of 10 m cells, not 3 times."}),
    ("From class",
     "How could you tell whether your stream threshold is realistic for your study area?",
     ["Use the lowest threshold the computer can handle so no stream is missed",
      "Use the tool's default value, since it is calibrated for the United States",
      "Rerun Fill until the stream network stops changing",
      "Overlay the network on mapped streams (the NHD) and imagery or topography, and adjust until channels begin about where real channels begin"],
     3,
     "The threshold is a judgment call, so it has to be checked against something independent of the DEM: the National Hydrography Dataset, aerial imagery, "
     "contour crenulations on a topographic map, or field observation. If the generated channels start far above where real channels start, the threshold is too low; "
     "if real channels are missing, it is too high.",
     {0: "A very low threshold draws a channel down nearly every hillslope hollow, most of which never carry a stream."}),
    ("From class",
     "Pour point A is on one tributary and pour point B is on another, both above the junction where they meet. Point C is below the junction. Which is true?",
     ["The watersheds of A and B overlap where the tributaries meet",
      "The watersheds of A and B do not overlap, and the watershed of C contains both of them",
      "The watershed of C is smaller than A's, because C is lower",
      "A, B and C all have the same watershed, since they are on the same river system"],
     1,
     "Each cell drains along one path, so it belongs to the watershed of A or of B, never both. Everything that reaches A or B keeps flowing past the junction to C, "
     "so C's watershed contains both, plus whatever drains in between. That nesting is why subwatersheds tile a basin with no gaps and no overlaps.",
     {}),
    ("From Lab 5",
     "In Lab 5, Snap Pour Point moves your outlet up to 50 m. Where does it move it?",
     ["To the cell with the highest flow accumulation within 50 m",
      "To the nearest point on the NHD stream line",
      "To the lowest-elevation cell within 50 m",
      "To the center of the nearest cell"],
     0,
     "Snap Pour Point searches the snap distance for the cell with the largest flow accumulation, which is the channel. "
     "An outlet left one cell off the channel would return the watershed of a few hillslope cells instead of the basin.",
     {1: "The tool works on the flow accumulation raster, not on any vector stream layer."}),
    ("From Lab 5",
     "Lab 5 makes one subwatershed per stream link with a second run of the Watershed tool. What is its pour point input?",
     ["The snapped outlet point",
      "The flow accumulation raster",
      "The Stream Link raster, so each link acts as the outlet of its own subwatershed and passes on its ID",
      "The basin polygon"],
     2,
     "Stream Link gives every segment its own number. Used as the pour points for Watershed, each link collects the cells that drain to it, "
     "and the resulting subwatershed carries that link's number, which is how the subwatersheds and the streams join.",
     {}),
    ("From class",
     "StreamStats asks you to choose a state before you can delineate a basin. Why?",
     ["Its preprocessed terrain data and its regression equations for streamflow are organized by state",
      "Watersheds stop at state lines",
      "Each state uses a different flow direction encoding",
      "State law requires the user to identify their location"],
     0,
     "StreamStats runs the same delineation steps on terrain data prepared ahead of time, then applies regression equations for flows such as peak discharge, "
     "and both are built state by state. The basin it returns can still cross a state line; watersheds do not stop there.",
     {}),
]
assert len(Q) == 20

# ---- items from the reading: Bolstad & Manson, GIS Fundamentals, "Hydrologic Functions" (read in the 7th ed.) ----
# Paraphrased, not quoted. No page, figure or equation numbers in the prompts: students own the 6th or 7th edition,
# and the numbering differs. Every item carries what it needs in the prompt itself. Checks on the computed ones:
# D-infinity: azimuth 105 is 15 deg from east (90) and 30 deg from southeast (135); each neighbor gets
# (angle to the OTHER neighbor) / 45, so east gets 30/45 and southeast 15/45.
assert (135 - 105) / 45 == 2 / 3 and (105 - 90) / 45 == 1 / 3
# Wetness index w = ln(SCA / tan b), SCA = AREA / C.
assert round(math.log((50_000 / 10) / 0.10), 1) == 10.8 and round(math.log(5_000), 1) == 8.5
assert round(math.log(50_000 / 0.10), 1) == 13.1 and round(math.log(5_000 * 0.10), 1) == 6.2
READ = {
    "aspect": ("From the reading",
     "The textbook notes that flow direction is often set equal to the local aspect, but that this can be wrong in some places. "
     "In which setting does it say aspect is a <em>reasonable</em> approximation of flow direction?",
     ["Nearly flat farmland", "A city drained by ditches, culverts and storm sewers",
      "Steep, undeveloped terrain", "Flat ground over soils of very different permeability"],
     2,
     "In steep, undeveloped terrain the downslope pull of gravity dominates, and surface and subsurface flow tend to go the same way, so aspect is a fair "
     "approximation. It breaks down on nearly flat ground, where soil permeability can steer water below the surface somewhere else, and in built areas, "
     "where ditches, culverts and storm sewers move water in ways the terrain does not show.",
     {}),
    "dinf": ("From the reading",
     "The textbook contrasts D8 with the D-infinity method, which splits a cell's flow between the two neighbors on either side of its steepest downhill direction, "
     "giving the larger share to the neighbor closer to that direction. A cell's steepest downhill direction is an azimuth of 105&#xB0;, "
     "between its east neighbor (90&#xB0;) and its southeast neighbor (135&#xB0;). How does D-infinity divide the cell's flow?",
     ["All of it to the east neighbor",
      "Two-thirds to the east neighbor and one-third to the southeast neighbor",
      "One-third to the east neighbor and two-thirds to the southeast neighbor",
      "Half to each"],
     1,
     "D-infinity splits the flow between the two neighbors on either side of the steepest direction, in proportion to how close the direction is to each. "
     "105&#xB0; is 15&#xB0; from east and 30&#xB0; from southeast, so east, the closer one, gets 30/45 = 2/3 and southeast gets 15/45 = 1/3. "
     "D8 would send all of it east. Splitting is how D-infinity represents divergent flow, which D8 cannot.",
     {0: "That is the D8 answer: all flow to the single neighbor closest to the steepest direction.",
      2: "That gives the larger share to the farther neighbor. The closer direction (east, 15&#xB0; away) gets the larger share."}),
    "restart": ("From the reading",
     "The textbook shows a stream network derived from a DEM in which a stream line stops at a sink, then starts again some distance downhill. Why does it start again?",
     ["The drawing tool skips short gaps in a line",
      "The sink keeps all the water above it, so the cells below it count only their own new contributing area and rejoin the network once that passes the threshold",
      "The stream really does flow underground for that distance",
      "The threshold is lower below the sink"],
     1,
     "Every cell above the sink drains into it and none drains out, so flow accumulation just below the sink starts over from the local hillslopes. "
     "A few cells farther down, enough new area drains in to pass the threshold again and a channel reappears, disconnected from the one above. "
     "The textbook's other example is a road crossing where the culvert is missing from the DEM.",
     {2: "Some streams do sink into karst, but here the gap comes from the DEM and the threshold, not from what the stream does underground."}),
    "zlimit": ("From the reading",
     "The textbook says conditioning removes pits shallower than a chosen depth and keeps deeper ones as real. "
     "Your lidar DEM's vertical errors are under 0.3 m, and every real pond in the area is at least 2 m deep. Which depth limit fits?",
     ["0.05 m", "About 1 m", "3 m", "None: fill every pit"],
     1,
     "The limit should be larger than the common vertical errors, so that spurious pits get removed, but smaller than any real pit, so that real ones are kept. "
     "Between 0.3 m and 2 m, about 1 m does both. In ArcGIS Pro this is the Z limit on the Fill tool.",
     {0: "Below the DEM's own errors: most spurious pits are deeper than 0.05 m and would be left in place.",
      2: "Deeper than the real ponds: they would be filled away along with the errors.",
      3: "Filling everything also removes the real ponds, which are part of the landscape."}),
    "breach": ("From the reading",
     "A highway embankment crosses a valley, and the creek passes under it through a culvert the DEM does not show. "
     "Which conditioning does the textbook prefer for this kind of pit?",
     ["Breach it: lower the cells along the steepest path through the embankment",
      "Fill it: raise the valley behind the embankment to the top of the road",
      "Leave it, since the embankment is a real feature",
      "Raise the stream threshold until the gap disappears"],
     0,
     "The textbook distinguishes the two cases. A small, isolated low spot from a data error is best filled. A narrow, high, linear barrier, usually a built feature "
     "with a culvert or other drain under it, is best breached: cutting a path through the barrier matches where the water really goes. "
     "Filling it instead turns the valley behind the road into a large false lake with no clear flow direction.",
     {1: "Filling would raise everything upstream of the road to the road's height: a flat false lake that does not exist."}),
    "wetness": ("From the reading",
     "The textbook's wetness index is w = ln(SCA / tan&#x3B2;), where the specific catchment area SCA = AREA / C, AREA is the accumulated area upstream and C is the cell size. "
     "A cell on a 10 m grid has 50,000 m&#xB2; of accumulated area upstream and a slope with tan&#x3B2; = 0.10. What is w?",
     ["6.2", "8.5", "10.8", "13.1"],
     2,
     "SCA = 50,000 m&#xB2; / 10 m = 5,000 m. Then SCA / tan&#x3B2; = 5,000 / 0.10 = 50,000, and ln(50,000) = 10.8. "
     "The index is high where a lot of area drains in and the slope is gentle, which is where soils stay wet.",
     {0: "6.2 is ln(5,000 &#xD7; 0.10): that multiplies by the slope, which is the stream power index (SPI = SCA &#xD7; tan&#x3B2;), not the wetness index.",
      1: "8.5 is ln(5,000): the slope was left out.",
      3: "13.1 is ln(500,000): the area was not divided by the cell size C first."}),
}

# Final selection and order: 14 class/lab items and 6 from the reading, grouped by topic.
# Dropped from the first draft: HUC12 shared digits, DEM water-balance term, artifact pit (the reading
# items cover pits more deeply), "why route with D8" (the reading's aspect item answers old Q5 better),
# D8 path tracing, and the StreamStats state question.
ORDER = [0, 1, 2, 3, 6, 7, "zlimit", "breach", "restart", 9, 10, "aspect", "dinf", 13, 14, 15, "wetness", 16, 17, 18]
Q = [READ[k] if isinstance(k, str) else Q[k] for k in ORDER]
assert len(Q) == 20

# Spread the correct answers evenly over A-D (five each) without editing the items above.
TARGET = "BADCDBCABCDACBDABDCA"


def place(q, k):
    tag, prompt, choices, ans, expl, notes = q
    order = [i for i in range(len(choices)) if i != ans]
    order.insert(k, ans)
    return tag, prompt, [choices[i] for i in order], k, expl, {order.index(i): t for i, t in notes.items()}


Q = [place(q, "ABCD".index(t)) for q, t in zip(Q, TARGET)]
assert all(TARGET.count(c) == 5 for c in "ABCD")

# ---- QTI writer -------------------------------------------------------------------------------
NS = ('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.imsglobal.org/xsd/imsqti_v2p2" '
      'xsi:schemaLocation="http://www.imsglobal.org/xsd/imsqti_v2p2 http://www.imsglobal.org/xsd/qti/qtiv2p2/imsqti_v2p2.xsd"')
L = "ABCD"


def item(n, tag, prompt, choices, ans, expl, notes):
    ident = f"MultipleChoice{n}"
    ids = [f"Choice{L[i]}" for i in range(len(choices))]
    x = [f'<?xml version="1.0"?>\n<assessmentItem {NS} identifier="{ident}" title="Question {n}" adaptive="false" timeDependent="false">',
         f'<responseDeclaration identifier="RESPONSE" cardinality="single" baseType="identifier"><correctResponse><value>{ids[ans]}</value></correctResponse>'
         f'<mapping defaultValue="0" lowerBound="0" upperBound="1"><mapEntry mapKey="{ids[ans]}" mappedValue="1"/></mapping></responseDeclaration>',
         '<outcomeDeclaration identifier="SCORE" cardinality="single" baseType="float"><defaultValue><value>0</value></defaultValue></outcomeDeclaration>',
         '<outcomeDeclaration identifier="FEEDBACK" baseType="identifier" cardinality="multiple"/>',
         f'<itemBody><div><choiceInteraction responseIdentifier="RESPONSE" maxChoices="1" data-type-hint="MultipleChoice">'
         f'<prompt><div><div><strong>[{tag}]</strong> {prompt}</div> </div> </prompt>']
    x += [f'<simpleChoice identifier="{i}">{ch}</simpleChoice>' for i, ch in zip(ids, choices)]
    x.append('</choiceInteraction></div></itemBody><responseProcessing><responseCondition><responseIf><setOutcomeValue identifier="SCORE">'
             '<baseValue baseType="float">0</baseValue></setOutcomeValue><isNull><variable identifier="RESPONSE"/></isNull></responseIf>'
             '<responseElse><setOutcomeValue identifier="SCORE"><mapResponse identifier="RESPONSE"/></setOutcomeValue></responseElse></responseCondition>')
    for i in ids:
        x.append(f'<responseCondition><responseIf><member><baseValue baseType="identifier">{i}</baseValue><variable identifier="RESPONSE"/></member>'
                 f'<setOutcomeValue identifier="FEEDBACK"><multiple><baseValue baseType="identifier">{i}_feedback</baseValue></multiple>'
                 f'</setOutcomeValue></responseIf></responseCondition>')
    x.append('</responseProcessing>')
    for k, i in enumerate(ids):
        lead = "Correct." if k == ans else "Incorrect."
        extra = f" {notes[k]}" if k in notes else ""
        x.append(f'<modalFeedback outcomeIdentifier="FEEDBACK" showHide="show" identifier="{i}_feedback">{lead}{extra} {expl}</modalFeedback>')
    x.append('</assessmentItem>')
    return "".join(x)


def manifest(n):
    res = "".join(f'<resource type="imsqti_item_xmlv2p2" identifier="MultipleChoice{i}" href="Q{i}.xml"><file href="Q{i}.xml"/></resource>' for i in range(n))
    return ('<?xml version="1.0"?>\n<manifest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.imsglobal.org/xsd/imscp_v1p1" '
            'identifier="Quiz6:WatershedDelineation" xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1 http://www.imsglobal.org/xsd/qti/qtiv2p2/qtiv2p2_imscpv1p2_v1p0.xsd '
            'http://ltsc.ieee.org/xsd/LOM http://www.imsglobal.org/xsd/imsmd_loose_v1p3p2.xsd http://www.imsglobal.org/xsd/imsqti_metadata_v2p2 '
            'http://www.imsglobal.org/xsd/qti/qtiv2p2/imsqti_metadata_v2p2.xsd"><metadata><schema>QTIv2.2 Package</schema><schemaversion>1.0.0</schemaversion>'
            f'</metadata><resources>{res}</resources></manifest>')


def plain(s):
    import html, re
    return html.unescape(re.sub("<[^>]+>", "", s))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    z = OUT / "Quiz6-WatershedDelineation-MC.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
        f.writestr("imsmanifest.xml", manifest(len(Q)))
        for n, q in enumerate(Q):
            f.writestr(f"Q{n}.xml", item(n, *q))
    md = ["# Quiz 6 — Watershed Delineation (multiple choice)\n", "20 items, 1 point each: 14 from class and Lab 5, 6 from the reading (Bolstad & Manson, Hydrologic Functions section; no edition-specific page, figure or equation numbers). Correct answer in **bold**.\n"]
    for n, (tag, prompt, choices, ans, expl, notes) in enumerate(Q, 1):
        md.append(f"## {n}. [{tag}]\n\n{plain(prompt)}\n")
        md += [f"- {'**' if i == ans else ''}{L[i]}. {plain(ch)}{'**' if i == ans else ''}" for i, ch in enumerate(choices)]
        md.append(f"\n> {plain(expl)}\n")
        for i, t in notes.items():
            md.append(f"> *If {L[i]}:* {plain(t)}\n")
    (OUT / "quiz06_review.md").write_text("\n".join(md), encoding="utf-8")
    print("answer letters:", "".join(L[q[3]] for q in Q))
    print("wrote", z)


if __name__ == "__main__":
    main()
