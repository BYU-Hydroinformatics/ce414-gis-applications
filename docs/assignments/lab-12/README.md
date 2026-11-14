# Lab 12: Choose Your Own Adventure

**Civil Engineering 414 — Engineering Applications of GIS**

Fall 2026 · Dr. Dan Ames

*Your question, your data, your model: a GIS analysis you design yourself, taught back as a
five-minute training video.*

<!-- **Revision notes.** New lab, drafted and promoted 2026-11-14. It replaces both the Avalanche
Hazard lab (Lab 12, 50 points; archived complete in docs/assignments/avalanche-backup/ for Fall 2027)
and the final project (proposal meeting, team presentation, lab-style write-up and presentation notes,
110 points). Lab 12 is now 100 points, individual: a five-minute ArcGIS Pro training video posted
unlisted on YouTube, a project report (text plus a full-page model and a full-page map) and a project
package, due Thursday of Week 15; a 30-90 s vertical reel is extra credit, up to 10 points. Course
total 1,295 -> 1,235 (Learning Suite, Nov 14), then 1,240 with a Week 12 in-class activity added the same day. Open: the Learning Suite upload limit for a .ppkx (the page allows a link), and
whether Snipping Tool on the lab machines records the microphone. The 18 example write-ups (Drive
folder 1FUjsLXI28kuB1JUgkKIa7G_A3HTa6gc6) carry student names and are not linked. -->

<!-- Drafted 2026-11-14 from the instructor's decisions of November 13-14, 2026 (one chat session): drop the
proposal meeting and the peer review of presentations; individual, not team, projects (an individual project
measures each student's own work); call it Lab 12, Choose Your Own Adventure, worth 100 points, a
stretch beyond Labs 1-11; ideas from past students; raster and vector analysis, ModelBuilder and map
making required; submit a five-minute voiceover screen capture of ArcGIS Pro made as a training video, a
short written piece and the ArcGIS Pro project package; an optional vertical reel for extra credit that
the instructor may post. The written piece is a short project report, not full step-by-step
instructions (the video is the training; the report carries what a video cannot: URLs, dates, settings),
with the model figure and the map each on a full page. Later the same day: video on YouTube, unlisted,
required for everyone (one place, less confusion); past decks linked here (moving off Learning Suite;
all eight decks are Drive "anyone with the link", checked 2026-11-14); rubric bullets labeled with what
they are graded from.
Due date: Thursday of Week 15 (December 10, 2026), the date the Learning Suite syllabus already gives
the final project write-up. The instructor is away December 6-10, 2026, so Week 15 questions go by email.
PROJECT PACKAGE (Esri help, "Share a project package", read 2026-11-14): Share tab > Package group >
Project opens the Package Project pane; "Share outside of organization" copies feature-service data into
file geodatabases; for toolboxes, "Input, output, and intermediate data is not copied. Model project data
is copied, but input data is not"; maps' layer data and geoprocessing history (with the data needed to
rerun) are copied. Hence Step 7's two rules: every input stays a layer in a map, and run the model once
from its tool dialog before packaging.
LINK CHECK (curl -L, 2026-11-14): 200 gis.utah.gov/products/sgid/, apps.nationalmap.gov/downloader/,
livingatlas.arcgis.com, pro.arcgis.com project-package help, support.microsoft.com Snipping Tool,
instagram.com/dr.danames. opendata.utah.gov returned 400 to curl and is not linked. -->

> [!NOTE]
> **This is a two-and-a-half-week lab**, introduced Tuesday of Week 13 and due **Thursday of
> Week 15 at 11:59 pm**, the last day of classes. It is worth **100 points**, twice a regular lab,
> and you do it **on your own**. Week 14 has Midterm 2 and no new lecture; its class time is open
> lab for this project. There is no class in Week 15, and I am away that week: send questions by
> email, and expect an answer in the evening.

## Background

Labs 1 to 11 handed you a question, the data and a recipe. Working GIS analysts get none of the
three. Someone brings them a problem — where should the new trailhead go, which culverts flood
first, how far is every school from a fire station — and the analyst decides what the question
really is, finds data that can answer it, builds a model, and shows the answer on a map.

This lab is that job. You choose the problem, find the data, build the model in ModelBuilder and
make the map. Then you do the part that turns an analysis into something other people can use:
you **teach it**. Your main deliverable is a five-minute training video, recorded on your own
ArcGIS Pro screen, for someone who wants to do this kind of analysis next. If you can explain
every dataset, every tool and every intermediate result in your model to that person, you
understand your analysis.

## Find a Project

Start from a problem you care about — a place you know, a question from an internship or another
class, a hobby. The best projects are specific: not "flooding in Utah", but "which of Provo's
storm drain inlets sit in the lowest tenth of the city's terrain".

**Past students' presentations.** Each year's class built one shared slide deck, every project
in turn, from the problem statement through the data and the model to the final maps. Page
through a few before you choose:

[2018](https://docs.google.com/presentation/d/186eEk6id3Yc58J9YTJWFDH6NePLCjJ8ecvAKh2EGCpw){ target="_blank" } ·
[2019](https://docs.google.com/presentation/d/1fzcs7eHolBGCwRPeRqWdLSj420-rjPFnD1WnDx3wYtk){ target="_blank" } ·
[2020](https://docs.google.com/presentation/d/11EMv0J_lutW4YcdxgzhxKtnUhK2Z0Rpzg_eeNNpGz2E){ target="_blank" } ·
[2021](https://docs.google.com/presentation/d/14FsmzOX8VPRn-17VNuEBk6xTO1rCqWlLJ8fdkeaL-6M){ target="_blank" } ·
[2022](https://docs.google.com/presentation/d/1lEwkMtb0CnLa9_GOO94AjqjVKL9NwHVRvEcfXHd3NLw){ target="_blank" } ·
[2023](https://docs.google.com/presentation/d/1IwyEidFPxk7ilbfqsJu3T8YrRrkTJ5ONstAjhoAhmS8){ target="_blank" } ·
[2024](https://docs.google.com/presentation/d/1UvupCj2YvOtAfjrG_IBvvLNr058GeybBoqi-l8yFi2g){ target="_blank" } ·
[2025](https://docs.google.com/presentation/d/1njvHMGkIwe3eJDbopwYC9fmZsBCHOs85BHV_x_JxJh8){ target="_blank" }

The decks are large and can take a minute to open. Take an idea and make it yours — a different
place, a different question, a better model — rather than repeat one. Pick something other than
Labs 1 to 11: this lab is a stretch past them, not a rerun.

**Ideas from past CE 414 projects.** Each row is a question a student or team answered in an
earlier year, with what they built it from; the year links to that year's deck. Most of these
deserve a better model than the one that answered them first.

| Theme | Question | Built with | Year |
| --- | --- | --- | --- |
| Water | Which homes near Utah Lake take flood damage at a given lake level, and what does it cost? | DEM, NHD lakes, parcels with market values | [2023](https://docs.google.com/presentation/d/1IwyEidFPxk7ilbfqsJu3T8YrRrkTJ5ONstAjhoAhmS8){ target="_blank" } |
| Water | How much runoff does each parcel send off in a 100-year storm, by the rational method? | Imagery classified with Segment Mean Shift, NOAA Atlas 14 rainfall, parcels, Tabulate Area | [2021](https://docs.google.com/presentation/d/14FsmzOX8VPRn-17VNuEBk6xTO1rCqWlLJ8fdkeaL-6M){ target="_blank" } |
| Water | What peak flow must each culvert under a new rural road carry? | DEM, NHD streams, rain-gauge records, Watershed, the rational method | [2021](https://docs.google.com/presentation/d/14FsmzOX8VPRn-17VNuEBk6xTO1rCqWlLJ8fdkeaL-6M){ target="_blank" } |
| Water | Where could a new reservoir go, and how much would it hold? | DEMs, streams, land ownership, floodplains, Zonal Statistics | [2020](https://docs.google.com/presentation/d/11EMv0J_lutW4YcdxgzhxKtnUhK2Z0Rpzg_eeNNpGz2E){ target="_blank" } |
| Water | Where could a dam go to serve a valley's farms, and how much would it store? | DEM, land use, Fill, Flow Accumulation, Zonal Statistics | [2022](https://docs.google.com/presentation/d/1lEwkMtb0CnLa9_GOO94AjqjVKL9NwHVRvEcfXHd3NLw){ target="_blank" } |
| Water | Where should rain gardens and detention basins go in a county? | DEM, soils, curvature, Flow Distance | [2025](https://docs.google.com/presentation/d/1njvHMGkIwe3eJDbopwYC9fmZsBCHOs85BHV_x_JxJh8){ target="_blank" } |
| Water | Which beaches are most exposed to stormwater runoff? | DEM, storm drains, beach polygons, Flow Accumulation | [2025](https://docs.google.com/presentation/d/1njvHMGkIwe3eJDbopwYC9fmZsBCHOs85BHV_x_JxJh8){ target="_blank" } |
| Water | Which parts of a watershed could pollute a lake the most? | Point pollution sources, DEM, watersheds, Near | [2022](https://docs.google.com/presentation/d/1lEwkMtb0CnLa9_GOO94AjqjVKL9NwHVRvEcfXHd3NLw){ target="_blank" } |
| Water | How deep was a flood, estimated from a flood-extent map and a DEM? | Satellite or FEMA flood extent, DEM | [2023](https://docs.google.com/presentation/d/1IwyEidFPxk7ilbfqsJu3T8YrRrkTJ5ONstAjhoAhmS8){ target="_blank" } |
| Water | Which buildings, and how many people, does a river flood reach? | DEM, NHD, OpenStreetMap buildings, a population raster | [2025](https://docs.google.com/presentation/d/1njvHMGkIwe3eJDbopwYC9fmZsBCHOs85BHV_x_JxJh8){ target="_blank" } |
| Water | Which low-head dams are the most dangerous, by stream type and size? | Fatality records, NHD flowlines, Snap, joins | [2022](https://docs.google.com/presentation/d/1lEwkMtb0CnLa9_GOO94AjqjVKL9NwHVRvEcfXHd3NLw){ target="_blank" } |
| Water | Where could a whitewater park go? | Flow accumulation, rivers, low-head dams, parks | [2023](https://docs.google.com/presentation/d/1IwyEidFPxk7ilbfqsJu3T8YrRrkTJ5ONstAjhoAhmS8){ target="_blank" } |
| Hazards | Which trails in a national park face the worst flash-flood hazard? | DEM, soils, rainfall, trails, Flow Accumulation | [2025](https://docs.google.com/presentation/d/1njvHMGkIwe3eJDbopwYC9fmZsBCHOs85BHV_x_JxJh8){ target="_blank" } |
| Hazards | Where can landslides start, and how far would they run? | DEM, soils, precipitation, slope, curvature, Path Distance | [2025](https://docs.google.com/presentation/d/1njvHMGkIwe3eJDbopwYC9fmZsBCHOs85BHV_x_JxJh8){ target="_blank" } |
| Hazards | Which burned areas threaten roads and buildings with mudslides after a wildfire? | Fire perimeters, slope, flow accumulation, infrastructure | [2018](https://docs.google.com/presentation/d/186eEk6id3Yc58J9YTJWFDH6NePLCjJ8ecvAKh2EGCpw){ target="_blank" } |
| Hazards | Which way is a wildfire most likely to spread, given terrain, fuel and wind? | DEM, vegetation, wind direction, Cost Path As Polyline | [2019](https://docs.google.com/presentation/d/1fzcs7eHolBGCwRPeRqWdLSj420-rjPFnD1WnDx3wYtk){ target="_blank" } |
| Hazards | Which water utilities' service areas face the most wildfire risk? | Service-area boundaries, FEMA National Risk Index, Zonal Statistics | [2025](https://docs.google.com/presentation/d/1njvHMGkIwe3eJDbopwYC9fmZsBCHOs85BHV_x_JxJh8){ target="_blank" } |
| Hazards | Which schools, hospitals and dams sit in the highest earthquake hazard along the Wasatch Fault? | Ground shaking, liquefaction, landslides, facility points | [2023](https://docs.google.com/presentation/d/1IwyEidFPxk7ilbfqsJu3T8YrRrkTJ5ONstAjhoAhmS8){ target="_blank" } |
| Hazards | Does an earthquake risk score from liquefaction, slope and emergency services beat distance to the fault? | Faults, liquefaction potential, emergency services, slope | [2018](https://docs.google.com/presentation/d/186eEk6id3Yc58J9YTJWFDH6NePLCjJ8ecvAKh2EGCpw){ target="_blank" } |
| Hazards | Where in the United States is combined natural-hazard risk lowest? | NOAA hazard points, digitized hazard zones, Cell Statistics | [2019](https://docs.google.com/presentation/d/1fzcs7eHolBGCwRPeRqWdLSj420-rjPFnD1WnDx3wYtk){ target="_blank" } |
| Hazards | What are the best tsunami evacuation routes for a coastal town? | Inundation zones, elevation, roads, Cost Path As Polyline | [2019](https://docs.google.com/presentation/d/1fzcs7eHolBGCwRPeRqWdLSj420-rjPFnD1WnDx3wYtk){ target="_blank" } |
| Hazards | Where would lava flow in a hypothetical eruption on a Hawaiian island? | Contours to TIN, Fill, Flow Accumulation | [2025](https://docs.google.com/presentation/d/1njvHMGkIwe3eJDbopwYC9fmZsBCHOs85BHV_x_JxJh8){ target="_blank" } |
| Hazards | Which areas are likely dust sources, from soil, vegetation and slope? | Soils, DEM, Landsat NDVI, Weighted Sum | [2022](https://docs.google.com/presentation/d/1lEwkMtb0CnLa9_GOO94AjqjVKL9NwHVRvEcfXHd3NLw){ target="_blank" } |
| Terrain and recreation | Where are the safe sledding hills, and how thrilling is each one? | Lidar DEM, tree canopy, roads, railroads, Surface Parameters | [2021](https://docs.google.com/presentation/d/14FsmzOX8VPRn-17VNuEBk6xTO1rCqWlLJ8fdkeaL-6M){ target="_blank" } |
| Terrain and recreation | How hard is each trail, from slope and length? | DEM, trails, Interpolate Shape, Add Surface Information | [2020](https://docs.google.com/presentation/d/11EMv0J_lutW4YcdxgzhxKtnUhK2Z0Rpzg_eeNNpGz2E){ target="_blank" } |
| Terrain and recreation | Which hiking trails have broad views that include water? | DEM, trails, lakes, streams, Viewshed | [2025](https://docs.google.com/presentation/d/1njvHMGkIwe3eJDbopwYC9fmZsBCHOs85BHV_x_JxJh8){ target="_blank" } |
| Terrain and recreation | From which spot in a national park can you see the most landmarks? | DEM, trails, points of interest, Geodesic Viewshed | [2024](https://docs.google.com/presentation/d/1UvupCj2YvOtAfjrG_IBvvLNr058GeybBoqi-l8yFi2g){ target="_blank" } |
| Terrain and recreation | Where should a fire lookout tower go to see the most terrain? | DEM, NDVI, trails, Viewshed | [2021](https://docs.google.com/presentation/d/14FsmzOX8VPRn-17VNuEBk6xTO1rCqWlLJ8fdkeaL-6M){ target="_blank" } |
| Terrain and recreation | Where could new climbing routes go: steep, near trails, away from existing climbs? | DEM, trails, existing routes, Slope, Con | [2020](https://docs.google.com/presentation/d/11EMv0J_lutW4YcdxgzhxKtnUhK2Z0Rpzg_eeNNpGz2E){ target="_blank" } |
| Terrain and recreation | Where could ski runs go on a mountain? | DEM, Slope, Flow Accumulation | [2018](https://docs.google.com/presentation/d/186eEk6id3Yc58J9YTJWFDH6NePLCjJ8ecvAKh2EGCpw){ target="_blank" } |
| Terrain and recreation | Where are safe, reachable bonfire sites in the mountains? | DEM, fire history, parks, campsites, Buffer, Erase | [2020](https://docs.google.com/presentation/d/11EMv0J_lutW4YcdxgzhxKtnUhK2Z0Rpzg_eeNNpGz2E){ target="_blank" } |
| Terrain and recreation | How can you generate a running route of a chosen length from your door? | Road network, Service Area, Route | [2025](https://docs.google.com/presentation/d/1njvHMGkIwe3eJDbopwYC9fmZsBCHOs85BHV_x_JxJh8){ target="_blank" } |
| Terrain and recreation | Where are elk most likely to drop their antlers? | DEM, elk habitat, water, known finds | [2019](https://docs.google.com/presentation/d/1fzcs7eHolBGCwRPeRqWdLSj420-rjPFnD1WnDx3wYtk){ target="_blank" } |
| Terrain and recreation | Where are the pits on a lava field, and how much does each hold? | Lidar DEM, Fill, Cut Fill, Zonal Statistics | [2021](https://docs.google.com/presentation/d/14FsmzOX8VPRn-17VNuEBk6xTO1rCqWlLJ8fdkeaL-6M){ target="_blank" } |
| Terrain and recreation | How much rock was dug out to make the Kennecott mine? | DEM, Raster to TIN, Surface Volume | [2023](https://docs.google.com/presentation/d/1IwyEidFPxk7ilbfqsJu3T8YrRrkTJ5ONstAjhoAhmS8){ target="_blank" } |
| Ecology | Where could Utah prairie dogs be reintroduced? | Species range, soil drainage, vegetation, roads, DEM, Slice | [2021](https://docs.google.com/presentation/d/14FsmzOX8VPRn-17VNuEBk6xTO1rCqWlLJ8fdkeaL-6M){ target="_blank" } |
| Ecology | How much cool, high pika habitat was lost between 1981 and 2020? | PRISM temperature rasters, DEM, water | [2021](https://docs.google.com/presentation/d/14FsmzOX8VPRn-17VNuEBk6xTO1rCqWlLJ8fdkeaL-6M){ target="_blank" } |
| Ecology | Where is the cheapest corridor for wildlife between two habitat patches, and where does it cross roads? | Land cover, roads, streams, Cost Distance | [2025](https://docs.google.com/presentation/d/1njvHMGkIwe3eJDbopwYC9fmZsBCHOs85BHV_x_JxJh8){ target="_blank" } |
| Ecology | Where should milkweed be planted along the monarch migration? | Migration path, temperature, land cover | [2018](https://docs.google.com/presentation/d/186eEk6id3Yc58J9YTJWFDH6NePLCjJ8ecvAKh2EGCpw){ target="_blank" } |
| Ecology | Did farmland protection zones slow the loss of farms to houses? | USDA cropland rasters, protection zones, Compute Change Raster | [2023](https://docs.google.com/presentation/d/1IwyEidFPxk7ilbfqsJu3T8YrRrkTJ5ONstAjhoAhmS8){ target="_blank" } |
| Ecology | Did lawns get greener or browner after smart water meters went in? | Meter points, imagery from two years, Zonal Histogram | [2018](https://docs.google.com/presentation/d/186eEk6id3Yc58J9YTJWFDH6NePLCjJ8ecvAKh2EGCpw){ target="_blank" } |
| Ecology | Does snow cover differ between a burned watershed and an unburned one? | Snow-cover rasters, Zonal Statistics | [2018](https://docs.google.com/presentation/d/186eEk6id3Yc58J9YTJWFDH6NePLCjJ8ecvAKh2EGCpw){ target="_blank" } |
| Ecology | How well does NASA's snow product match snow cover computed from Landsat? | Landsat, NDSI, the NASA snow product | [2018](https://docs.google.com/presentation/d/186eEk6id3Yc58J9YTJWFDH6NePLCjJ8ecvAKh2EGCpw){ target="_blank" } |
| Ecology | How did fine-particle air pollution change across Utah over twenty years? | EPA monitor points, Spline, Raster Calculator | [2024](https://docs.google.com/presentation/d/1UvupCj2YvOtAfjrG_IBvvLNr058GeybBoqi-l8yFi2g){ target="_blank" } |
| Ecology | Which communities are most vulnerable to drought? | Precipitation, soil moisture and NDVI rasters, FEMA risk index | [2024](https://docs.google.com/presentation/d/1UvupCj2YvOtAfjrG_IBvvLNr058GeybBoqi-l8yFi2g){ target="_blank" } |
| Ecology | Which countries got brighter or dimmer at night? | Night-light rasters from two years, Zonal Statistics | [2018](https://docs.google.com/presentation/d/186eEk6id3Yc58J9YTJWFDH6NePLCjJ8ecvAKh2EGCpw){ target="_blank" } |
| Energy and infrastructure | Where are the best sites for a solar farm? | Solar radiation, slope, transmission lines, protected lands | [2024](https://docs.google.com/presentation/d/1UvupCj2YvOtAfjrG_IBvvLNr058GeybBoqi-l8yFi2g){ target="_blank" } |
| Energy and infrastructure | Where can a wind farm meet wind, road, town and spacing limits? | Wind, roads, towns, rivers, Weighted Sum | [2021](https://docs.google.com/presentation/d/14FsmzOX8VPRn-17VNuEBk6xTO1rCqWlLJ8fdkeaL-6M){ target="_blank" } |
| Energy and infrastructure | Where are the longest gaps between electric-vehicle fast chargers on a road trip? | Charger points, roads, Cost Distance, Cost Path As Polyline | [2023](https://docs.google.com/presentation/d/1IwyEidFPxk7ilbfqsJu3T8YrRrkTJ5ONstAjhoAhmS8){ target="_blank" } |
| Energy and infrastructure | What route should a railroad take from a coal seam to a power plant? | DEM, streams, land ownership, Distance Accumulation | [2023](https://docs.google.com/presentation/d/1IwyEidFPxk7ilbfqsJu3T8YrRrkTJ5ONstAjhoAhmS8){ target="_blank" } |
| Energy and infrastructure | Where should a passenger railroad from Provo to St. George run? | DEM, water, roads, land ownership, a cost surface | [2024](https://docs.google.com/presentation/d/1UvupCj2YvOtAfjrG_IBvvLNr058GeybBoqi-l8yFi2g){ target="_blank" } |
| Energy and infrastructure | Where can tilt-up concrete buildings go on vacant industrial land? | Zoning, parcels, roads, suppliers, DEM, Near | [2019](https://docs.google.com/presentation/d/1fzcs7eHolBGCwRPeRqWdLSj420-rjPFnD1WnDx3wYtk){ target="_blank" } |
| Energy and infrastructure | Where can a sign beside the highway be seen and read from the road? | Imagery, visibility analysis | [2022](https://docs.google.com/presentation/d/1lEwkMtb0CnLa9_GOO94AjqjVKL9NwHVRvEcfXHd3NLw){ target="_blank" } |
| Getting around | Where should a new public park go? | DEM, transit stops, roads, parks, census blocks | [2021](https://docs.google.com/presentation/d/14FsmzOX8VPRn-17VNuEBk6xTO1rCqWlLJ8fdkeaL-6M){ target="_blank" } |
| Getting around | Where should a new bus line run to serve the most people and places? | Roads, transit stops, census blocks, Distance Accumulation | [2023](https://docs.google.com/presentation/d/1IwyEidFPxk7ilbfqsJu3T8YrRrkTJ5ONstAjhoAhmS8){ target="_blank" } |
| Getting around | Where should new bus stops go to raise ridership? | Transit stops and routes, populated blocks, Union, Dissolve | [2020](https://docs.google.com/presentation/d/11EMv0J_lutW4YcdxgzhxKtnUhK2Z0Rpzg_eeNNpGz2E){ target="_blank" } |
| Getting around | Do bus stops raise the risk of pedestrian crashes? | Crash points, bus stops, census blocks, Kernel Density | [2024](https://docs.google.com/presentation/d/1UvupCj2YvOtAfjrG_IBvvLNr058GeybBoqi-l8yFi2g){ target="_blank" } |
| Getting around | What is the safest bike route between two campuses? | Roads, bike routes, crash points, Kernel Density, an optimal path | [2024](https://docs.google.com/presentation/d/1UvupCj2YvOtAfjrG_IBvvLNr058GeybBoqi-l8yFi2g){ target="_blank" } |
| Getting around | Where are the dark spots in a city's streetlight coverage? | Streetlight points, roads, a lighting model | [2025](https://docs.google.com/presentation/d/1njvHMGkIwe3eJDbopwYC9fmZsBCHOs85BHV_x_JxJh8){ target="_blank" } |
| Getting around | Where should a new hospital go? | Collisions, earthquakes, hospitals, highways, Combine | [2019](https://docs.google.com/presentation/d/1fzcs7eHolBGCwRPeRqWdLSj420-rjPFnD1WnDx3wYtk){ target="_blank" } |
| Getting around | Which state parks with the features you want are within reach of a city? | State parks, cities, a ModelBuilder iterator | [2021](https://docs.google.com/presentation/d/14FsmzOX8VPRn-17VNuEBk6xTO1rCqWlLJ8fdkeaL-6M){ target="_blank" } |
| Getting around | What route visits eight national parks in winter and avoids the coldest roads? | Winter temperature raster, parks, hotels, Find Routes | [2021](https://docs.google.com/presentation/d/14FsmzOX8VPRn-17VNuEBk6xTO1rCqWlLJ8fdkeaL-6M){ target="_blank" } |
| Getting around | Where in a city might a rental property pay off best? | Rent and price points, schools, stores, Kriging | [2022](https://docs.google.com/presentation/d/1lEwkMtb0CnLa9_GOO94AjqjVKL9NwHVRvEcfXHd3NLw){ target="_blank" } |
| Further afield | How many craters, and how much crater area, does a Martian volcano have? | Mars DEM and infrared mosaic, Mars geologic map, Fill, Minus | [2021](https://docs.google.com/presentation/d/14FsmzOX8VPRn-17VNuEBk6xTO1rCqWlLJ8fdkeaL-6M){ target="_blank" } |
| Further afield | Where in Utah should you look for new dinosaur fossils? | Geologic map, Paleobiology Database finds, Point Density | [2020](https://docs.google.com/presentation/d/11EMv0J_lutW4YcdxgzhxKtnUhK2Z0Rpzg_eeNNpGz2E){ target="_blank" } |
| Further afield | Where are gold, silver and copper most concentrated in a mining district's soils? | Geologic units, soil-sample geochemistry | [2019](https://docs.google.com/presentation/d/1fzcs7eHolBGCwRPeRqWdLSj420-rjPFnD1WnDx3wYtk){ target="_blank" } |
| Further afield | What would the states look like if their borders followed watersheds? | Watershed boundaries, Dissolve, Eliminate | [2019](https://docs.google.com/presentation/d/1fzcs7eHolBGCwRPeRqWdLSj420-rjPFnD1WnDx3wYtk){ target="_blank" } |
| Further afield | How would state borders change if everyone belonged to the nearest NFL team? | Population raster, team points, Near | [2020](https://docs.google.com/presentation/d/11EMv0J_lutW4YcdxgzhxKtnUhK2Z0Rpzg_eeNNpGz2E){ target="_blank" } |
| Further afield | Where could a new national park go in a state that has none? | Federal lands, roads, campgrounds, forest cover | [2025](https://docs.google.com/presentation/d/1njvHMGkIwe3eJDbopwYC9fmZsBCHOs85BHV_x_JxJh8){ target="_blank" } |
| Further afield | Where could an amusement park go, near airports and families? | Counties, temperature, airports, Polygon to Raster, Raster Calculator | [2025](https://docs.google.com/presentation/d/1njvHMGkIwe3eJDbopwYC9fmZsBCHOs85BHV_x_JxJh8){ target="_blank" } |

<!-- Source: the eight class decks (2018: 18 projects, 2019: 17, 2020: 14, 2021: 20, 2022: 9, 2023: 13,
2024: 12, 2025: 23; 126 in all) and the 18 "Example Final Project" write-ups in the instructor's Drive,
read 2026-11-14 through the Drive connector; paraphrased, student names omitted. Left out: duplicates
(solar siting appears in 2018, 2021, 2024 and 2025; one row kept), straight repeats of a current lab
(HAND flooding in Logan, a cell-tower adaptation), and projects built on sensitive data (offender
registries, crime and child-safety risk, a "concealment site" scenario, coca and violence). -->

**Where to find data.** Most Utah projects can be built from these:

- [UGRC's State Geographic Information Database](https://gis.utah.gov/products/sgid/){ target="_blank" }:
  roads, parcels, boundaries, water, utilities, land cover and imagery for Utah.
- [The National Map Downloader](https://apps.nationalmap.gov/downloader/){ target="_blank" } (USGS):
  elevation (3DEP), hydrography (NHD) and more for the whole country.
- [ArcGIS Living Atlas of the World](https://livingatlas.arcgis.com/){ target="_blank" }: Esri's
  curated layers, from land cover to census data, ready to add to a map in ArcGIS Pro.

Check the data before you commit to a question: download it, add it to a map, and make sure it
covers your area and holds the fields you need. A good question with no data is not a project yet.

## Requirements

Your project must have all four:

1. **Raster and vector data, both analyzed.** At least one raster layer (elevation, land cover,
   imagery, a surface you interpolate) and at least one vector layer (points, lines or polygons)
   must go *into* the analysis, not only sit under it as a backdrop.
2. **A ModelBuilder model** that runs from its tool dialog and produces your result. Aim for
   roughly six to twelve tools; a model of two tools is a lab exercise, and a model of thirty is
   a semester.
3. **A finished map** that answers your question.
4. **Your own work**, done individually. Classmates can help you find data or fix an error, as in
   any lab; the question, the model, the map and the video are yours.

## Complete the Lab

### Step 1 — Choose the Question

Write your question in one sentence, and say who would act on the answer. "Where in Utah County
could a 2 MW solar farm go within 1 km of a substation, on land under 5 degrees of slope and not
in a floodplain?" is a project. "Solar energy in Utah" is a topic.

### Step 2 — Gather the Data

Set up your folder as for every lab: on the lab machines, `D:\Smith\Lab12\`, never a space in a
name. Download each layer, read its metadata, and record in your project report (Step 6) where it
came from, its URL, the date you downloaded it, and its coordinate system. Pick one projected
coordinate system for the whole project (NAD 1983 UTM Zone 12N for most of Utah) and set it, with
the cell size and extent, in the environments as in earlier labs.

### Step 3 — Build the Model

Build the analysis in ModelBuilder in your project's toolbox. Give your intermediate datasets
names a stranger could read (`Slope_Under_5`, not `Reclass_Slop1`), expose the inputs, the key
thresholds and the result as parameters, and run it from its tool dialog until it runs end to end
without a hand repair.

### Step 4 — Make the Map

One professional map layout (letter size) that answers your question: the result clearly
symbolized, the layers that explain it, a legend, title, neat line, north arrow and scale bar, and
a text box with your name, the date, the map projection, and the sources and dates of the data.

### Step 5 — Record the Video

Your video is a **training video**: a voiceover on your ArcGIS Pro screen, made for someone who
wants to do this kind of analysis. Record the screen and your voice with the **Snipping Tool**
built into Windows (open it, choose the video camera, click **New**, drag a box around the ArcGIS
Pro window, and turn the microphone on before you start). Microsoft's
[Snipping Tool help](https://support.microsoft.com/en-us/windows/use-snipping-tool-to-capture-screenshots-00246869-1843-655f-f220-97299b865f6b){ target="_blank" }
shows the controls. **[To do: confirm that Snipping Tool on the lab machines shows the microphone
button, and that the machines take a headset.]**

Show, in this order, in **five minutes** (no more than five and a half):

| About | What you show |
| --- | --- |
| 30 s | The question, and who would use the answer |
| 1 min | Each dataset: what it is, raster or vector, where it came from |
| 2½ min | The model, tool by tool: open each tool, say what it does and why, then show the dataset it made |
| 1 min | The final map, the answer, and one thing the analysis cannot tell you |

Three things make it work:

- **Show results; do not wait for them.** Run the model before you record. On camera, open each
  tool from the model to show its settings, then switch to the layer it produced. Nobody wants to
  watch a progress bar.
- **Record in pieces.** Record the data, the model and the map as separate clips and retake any
  piece you stumble on. Submit the pieces in order, or join them in any video editor you like.
- **Make it readable.** Zoom in on dialogs and tables so a viewer can read them, and record
  somewhere quiet, with a headset if you can.

**Post it on YouTube as an unlisted video.** Everyone uses YouTube, so every video plays the same
way. Sign in at [YouTube](https://www.youtube.com/){ target="_blank" } with any Google account,
click **Create ▸ Upload video**, and under **Visibility** choose **Unlisted**: anyone with the link
can watch it, and nobody can find it by searching. Title it `CE 414 Lab 12 — ` and your project's
title. Open the link in a private browser window before you submit it, to be sure it plays.

### Step 6 — Write the Project Report

A short report that a future student could start from: a page or two of text, then the model and
the map, each on its own full page. Four or five pages in all is typical.

- **Title block:** your name, the date, your project's title, and the link to your video
- **The question** in one sentence, and who would act on the answer
- **A data table**, one row per layer: name, raster or vector, source and URL, the date you
  downloaded it, and its coordinate system
- **The tools in the order your model runs them**, each with its key settings, as a numbered list
- **The answer** in two or three sentences, with the numbers that support it, and its main
  limitation
- one line saying what you used AI for, if anything
- **Your model, full page:** exported from ModelBuilder (**Export ▸ Export To Graphic**), every tool and dataset readable
- **Your map, full page:** the layout from Step 4, exported as a PDF page

### Step 7 — Package the Project

A project package (`.ppkx`) bundles your maps, layouts, toolbox and data into one file that anyone
with ArcGIS Pro can open, so the grader can open your project and rerun your model. A package
copies the data in your **map layers** and in your **geoprocessing history**, but it does **not**
copy a model's input data on its own, so first:

1. Make sure **every input dataset is a layer in a map** in your project (a map named `Data` is
   fine).
2. **Run your model once from its tool dialog**, so the run is in the geoprocessing history.

Then, on the **Share** tab, in the **Package** group, click **Project**. In the **Package Project**
pane, save it as a file in your Lab12 folder, check **Share outside of organization**, leave
**Include Toolboxes** and **Include History Items** checked, and run it. Open the `.ppkx` once
yourself (double-click it) to check that the maps draw and the model is there.
**[To do: confirm the Package Project pane's labels and options in ArcGIS Pro 3.7.]**

If the package is too large for Learning Suite, put it in Google Drive or BYU Box with link
sharing on and submit the link. **[To do: confirm Learning Suite's upload limit.]**

### Extra Credit — Make a Reel

For **up to 10 extra-credit points**, cut a **30 to 90 second vertical video** (phone shape, 9:16)
from your footage: the question, one striking intermediate result, the final map, and the answer,
with captions, for someone scrolling a phone rather than learning the tools. Submit it as a video
file on Learning Suite.

A reel that simply shows the project earns a few points; a really good one earns all ten. What
makes it really good: it hooks a viewer in the first three seconds, tells the story without the
sound on, gets the answer across clearly, and looks like something people would want to share.

With your permission, I may post it on my professional GIS Instagram account,
[@dr.danames](https://www.instagram.com/dr.danames/){ target="_blank" }, so you do not have to
post it on your own. In your submission, say whether I may post it, and whether to credit you by
name. Posting is never required for the extra credit, and you are free to post it on your own
account instead.

## Deliverables

Submit on Learning Suite by **Thursday of Week 15, 11:59 pm**:

| What | Form |
| --- | --- |
| Training video, about five minutes | The **unlisted YouTube link** |
| Project report: a page or two of text, the model on a full page, the map on a full page | PDF |
| Project package | `.ppkx` file, or a link if it is too large |
| Extra credit: vertical reel, 30 to 90 seconds | Video file, with your posting permission |

> [!NOTE]
> **Make it yours.** No two students should turn in the same project. Your question, your data,
> your model, your map and your voice are your own work. Projects whose models, maps or videos
> match another student's too closely are flagged for follow-up.

## Rubric for Choose Your Own Adventure

One hundred points in five parts. The bullets say what each part is worth, so you know exactly
what to submit, and each bullet says **where it is graded from**: the **video**, the **report**, or
the **package** (opened and run in ArcGIS Pro). In all, about 30 points come from the video, 40
from the report and 30 from the package.

| Item | Points |
| --- | --- |
| **Question and data**<br>• *Video and report:* the question in one sentence, specific to a place, and who would act on the answer (4)<br>• *Package:* at least one raster and one vector layer, both used in the analysis (6)<br>• *Report:* every layer in the data table, with raster or vector, source and URL, download date and coordinate system (6)<br>• *Package:* one projected coordinate system for the project, set on purpose (4) | /20 |
| **ModelBuilder model** — correct and working<br>• *Package:* the model opens from the package and runs from its tool dialog without a hand repair (8)<br>• *Package:* it does the analysis, with raster and vector tools both inside the model, and the result comes out of it, not from hand edits afterward (6)<br>• *Report:* the full-page model figure, every tool and dataset readable, with informative names for intermediate data and the inputs, key thresholds and result exposed as parameters (6) | /20 |
| **Map** — graded from the full-page map in the report<br>• Title, neat line, north arrow and scale bar (4)<br>• Text box with your name, the date, the map projection, and the sources and dates of the data (4)<br>• The result clearly symbolized with a legend, so the map answers the question at a glance (6)<br>• The layers that explain the result, a suitable basemap, and scale and legibility appropriate to the area (6) | /20 |
| **Training video** — graded from the video<br>• About five minutes, no more than five and a half, unlisted on YouTube and playing from the link (4)<br>• Each dataset shown, with what it is and where it came from (5)<br>• The model walked tool by tool: each tool's settings shown and explained, and the dataset it made shown (10)<br>• The final map, the answer, and one thing the analysis cannot tell you (5)<br>• Clear audio, readable screen, and a pace a newcomer could follow (6) | /30 |
| **Report and package**<br>• *Report:* complete, with the title block and video link, the tools in order with their settings, the answer with its numbers and its limitation, and the AI line (6)<br>• *Package:* the `.ppkx` submitted, and it opens with its maps and data (4) | /10 |
| **Total** | **/100** |
| **Extra credit:** a 30 to 90 second vertical reel cut from your footage, with captions, the question, the result and the map; a really good one, which hooks a viewer in the first seconds, reads without sound and gets the answer across, earns the most | **up to +10** |

> [!NOTE]
> **Using AI on this lab.** Use AI freely to find data, understand a tool, work out an error, plan
> your video or tighten your report, and add one line to the report saying what you used it
> for. Do not take a field name, an expression, a coordinate system, or a number from it — those
> come from your own data — and do not present generated output as a result you produced in
> ArcGIS Pro. See the [AI Use Policy](../../policies/ai-policy.md) for the full policy.
