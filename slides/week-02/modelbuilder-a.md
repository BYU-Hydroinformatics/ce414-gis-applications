---
marp: true
theme: ce414
paginate: true
footer: "CE 414 · Week 2 — ModelBuilder, Part A"
---

<!-- _class: lead -->
<!-- _paginate: skip -->

![bg right:45% w:99%](images/mba-cities-rivers-map.png)

![w:130](../theme/images/byu-medallion.svg)

# Spatial Modeling and ArcGIS ModelBuilder — Part A

CE 414 Engineering Applications of GIS
Dr. Dan Ames
Civil & Construction Engineering
Brigham Young University

<!-- ModelBuilder is one of the most powerful, and most underused, tools in ArcGIS Pro. It is a way to perform analysis and to automate workflows: you build the workflow once, document it, and run it again on new data. This session and Part B together walk through creating and executing models with geoprocessing tools and data, and using the ModelBuilder environment to document and share models so other people can run them. Today is concepts and mechanics; by the end you should be able to start Lab 1 tonight. -->

---

# Today's Goals

By the end of class you should be able to:

- Say what a **model** is, and recognize models that are not computer programs
- Explain what **ModelBuilder** is and when to reach for it instead of running tools one at a time
- Create a **toolbox** and a **model** in ArcGIS Pro, set its environments, and read the canvas
- Follow the **Cities Near Rivers** model from problem to result
- Recognize the **Lab 1 model** below as the same pattern, longer

![w:1100 center](images/mba-lab1-model-overview.svg)

<!-- The picture on the right is the Lab 1 model, finished. It looks like a lot; by the end of today it should look like a chain of things you have already seen. Part B picks up the same Cities Near Rivers example and turns it into a shareable tool with parameters. -->

---

# Review: What is a Model?

<div style="background:#e8792b;color:#fff;border-radius:12px;padding:1.1em 1.5em;margin:0.8em auto;max-width:900px;text-align:center;">
<div style="font-size:1.5em;font-weight:700;line-height:1.3;">A model is an idealized and simplified<br>representation of reality</div>
<div style="margin-top:0.7em;font-size:1.05em;">Or&hellip; an <strong style="color:#fff;">"Abstraction of Reality"</strong></div>
</div>

- The word, "model", does a lot of work in engineering: it covers globes, maps, photographs, equations, and computer programs
- What every one of them has in common: they are an **intentional simplification of the real world**

<!-- Start by asking the class for examples of models before showing the definition. The next five slides are all examples; keep them moving. -->

---

# A globe is a model of the Earth

![h:440 center](images/mba-globe.gif)

<!-- Image: an antique-styled desk globe rendered from Natural Earth 1:110m land polygons (public domain) by tools/make_antique_globe_gif.py; no openly licensed animation of a real physical globe was available. -->

<!-- Round, rotates, shows continents and oceans. Leaves out everything smaller than a few hundred kilometers. Ask what a globe is good for that a flat map is not. -->

---

# A map is a graphical model of the earth's surface

![h:440 center](images/mba-old-paper-map.jpg)

<!-- Photo: "maps lying on the floor" by Andrew Neel, https://unsplash.com/photos/1-29wyvvLJA, Unsplash License. -->

<!-- A map is a graphical model. Every symbol on it is a decision about what matters. -->

---

# An aerial photo is a pictorial model of surface features

![h:430 center](images/mba-aerial-photo.jpg)

<!-- A photo is a pictorial model of the earth surface. It records reflectance, not roads or parcels; the interpretation is still up to you. Lab 2 will make this concrete: two Landsat bands are pictures, and the vegetation map you build from them is a model. -->

---

# A simple weather forecasting model

<div class="columns">
<div style="text-align:center;">

![h:360](images/mba-weather-stations.svg)

**Weather stations** — point measurements

</div>
<div style="text-align:center;">

![h:360](images/mba-thiessen-polygons.svg)

**Predicted model** — Thiessen polygons

</div>
</div>

<!-- A dozen stations measure temperature at a dozen points. Thiessen (Voronoi) polygons assign every location the value of its nearest station, which turns point measurements into a surface. It is a crude model, and it is still a model: it produces a value everywhere from data collected somewhere. -->

---

# A Digital Elevation Model is a model of the earth's terrain

<div class="columns" style="grid-template-columns: 0.9fr 1.15fr 1.25fr; gap: 20px; align-items: end;">
<div style="text-align:center;">

![h:270](images/mba-dem-grid.svg)

<small>One number per cell</small>

</div>
<div style="text-align:center;">

![h:270](images/mba-dem-columns.svg)

<small>The same numbers as columns</small>

</div>
<div style="text-align:center;">

![h:270](images/mba-dem-terrain.jpg)

<small>The terrain they describe</small>

</div>
</div>

A DEM is two models at once: a **raster data model** (a regularly spaced grid of numeric values — discussed last week) holding one number per cell, and a **model or representation of the terrain (elevations)** built from those numbers.

<!-- This is the one-line bridge from last week's data models. The word "model" is in the name. A DEM is a raster, one elevation per cell, and it is also a simplified representation of the ground. Every raster analysis later in the course starts from this double meaning. -->

---

# There are many types of models

<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin:0.6em 0 0.4em 0;">
<div style="background:#eef3f9;border-top:8px solid #002e5d;border-radius:8px;padding:0.7em 0.6em;text-align:center;"><div style="font-size:2.2em;color:#002e5d;font-weight:800;">T</div><div style="font-weight:700;">Theory</div><div style="font-size:0.7em;color:#5a6472;margin-top:0.4em;">Bernoulli's energy principle</div></div>
<div style="background:#eef3f9;border-top:8px solid #002e5d;border-radius:8px;padding:0.7em 0.6em;text-align:center;"><div style="font-size:2.2em;color:#002e5d;font-weight:800;">L</div><div style="font-weight:700;">Law</div><div style="font-size:0.7em;color:#5a6472;margin-top:0.4em;">Conservation of mass</div></div>
<div style="background:#eef3f9;border-top:8px solid #002e5d;border-radius:8px;padding:0.7em 0.6em;text-align:center;"><div style="font-size:2.2em;color:#002e5d;font-weight:800;">H</div><div style="font-weight:700;">Hypothesis</div><div style="font-size:0.7em;color:#5a6472;margin-top:0.4em;">"Cities cluster near rivers"</div></div>
<div style="background:#eef3f9;border-top:8px solid #e8792b;border-radius:8px;padding:0.7em 0.6em;text-align:center;"><div style="font-size:2.2em;color:#e8792b;font-weight:800;">E</div><div style="font-weight:700;">Equation</div><div style="font-size:0.7em;color:#5a6472;margin-top:0.4em;">Manning's equation, NDVI</div></div>
<div style="background:#eef3f9;border-top:8px solid #e8792b;border-radius:8px;padding:0.7em 0.6em;text-align:center;"><div style="font-size:2.2em;color:#e8792b;font-weight:800;">S</div><div style="font-weight:700;">Structured idea</div><div style="font-size:0.7em;color:#5a6472;margin-top:0.4em;">A site-selection workflow</div></div>
</div>

<div style="background:#fff;border-left:8px solid #002e5d;border-radius:8px;padding:0.7em 1.2em;margin:0.6em auto;max-width:900px;font-size:1.05em;">
A model could be a <strong>theory</strong>, a <strong>law</strong>, a <strong>hypothesis</strong>, an <strong>equation</strong>, or even a <strong>structured idea</strong>
</div>

<p style="font-size:0.7em;color:#5a6472;">From Haggett and Chorley, 1967</p>

<style scoped>
section ul { list-style: none; margin: 0; padding: 0; }
section li[data-marpit-fragment] { position: absolute; left: 0; top: 0; width: 100%; height: 100%; margin: 0; pointer-events: none; }
.mb-ring { position: absolute; left: 958px; top: 135px; width: 286px; height: 330px; overflow: visible; }
.mb-ring ellipse { fill: none; stroke: #e8792b; stroke-width: 6; stroke-linecap: round; stroke-dasharray: 900; stroke-dashoffset: 0; }
li[data-bespoke-marp-fragment="active"] .mb-ring ellipse { animation: mb-draw 0.9s ease-out forwards; }
@keyframes mb-draw { from { stroke-dashoffset: 900; } to { stroke-dashoffset: 0; } }
.mb-call { position: absolute; left: 780px; top: 88px; width: 430px; text-align: right; font-size: 0.74em; font-weight: 700; color: #e8792b; line-height: 1.25; }
li[data-bespoke-marp-fragment="active"] .mb-call { animation: mb-fade 0.6s ease-out both; }
@keyframes mb-fade { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
</style>

* <svg class="mb-ring" viewBox="0 0 286 330"><ellipse cx="143" cy="165" rx="130" ry="152" transform="rotate(-7 143 165)"/></svg><span class="mb-call">Enabled by ModelBuilder — Core Modeling Environment for this Class</span>

<!-- Nothing on this list is a computer program. Ask the class for an engineering example of each: Manning's equation, the rational method, a free-body diagram. The two orange tiles are the ones this course builds in ModelBuilder: equations (Lab 2's NDVI) and structured ideas (Lab 1's site-selection chain). We model constantly and only sometimes write code. -->

---

# A recipe is a model

![h:350 center](images/mba-pie-recipe.svg)

- **Blue ovals are inputs, yellow boxes are tools, green ovals are derived data** — exactly ModelBuilder's vocabulary
- "a pattern of something to be made" — *Merriam-Webster*

<p style="font-size:0.62em;color:#5a6472;">(Adapted from Merrilee Torres, Burlington County, NJ, GIS Users Group)</p>

<!-- Ovals are data, boxes are processes, and the arrows carry one into the next. That is exactly the vocabulary of ModelBuilder: data element, tool, derived data. If you can write a recipe you can build a model. On Thursday everyone brings a sketch of a cookie recipe drawn this way; say so now. -->

---

# What is ModelBuilder?

![w:1100 center](images/mba-lab2-model-overview.svg)

A GIS-integrated system for:

- **Automating workflow** by stringing processes together, saved so it can be run again
- **Designing** and **implementing** models, and **sharing** them with other people
- **Showing the process** used to create an output, as a flow diagram — one analysis, written down

<!-- The diagram is the Lab 2 model, exported straight from ModelBuilder: two satellite bands in, a vegetation classification out, nine steps in between. The share-and-document points are the ones students undervalue. A model is a picture of your analysis that a reviewer can read, which is worth as much as the automation. -->

---

# Example geoprocessing tasks

![h:450 center](images/mba-geoprocessing-tasks.png)

<p style="font-size:0.62em;color:#5a6472;">(Adapted from Brett Rose, Esri DC Technology Center)</p>

<!-- Four familiar questions: site selection from weighted layers, least-cost route over terrain, nearest facility, and population inside a zone. Every one of them is several tools in a row, which is precisely when a model pays for itself. Site selection is Lab 1; least-cost path is its own lecture later in the semester. -->

---

# Four ways to run the same tool

![h:430 center](images/mba-four-ways-pro.png)

One Buffer, four front ends. What changes between them is repeatability, not the result.

<!-- All four panels are ArcGIS Pro 3.7, and all four run the same Buffer. The dialog is what you have used so far. The Python window runs one line at a time. The model is today's subject: a picture of the whole chain that can be run again. The script is the same chain as arcpy code, which you will meet later in the course. Every one of them calls the identical geoprocessing tool underneath. -->

---

<!-- _class: lead -->

# Building a model in ArcGIS Pro

## Toolbox → model → environments → ribbon

---

# How to start a new model

<div class="columns" style="grid-template-columns: 1fr 1fr;">
<div>

- Open your project in ArcGIS Pro and show the **Catalog pane** (View ▸ Catalog Pane)
- Right-click **Toolboxes ▸ New Toolbox (.atbx)**, or press **Ctrl+Shift+B**
- Give it a meaningful name — it is saved as a `.atbx` file in your project folder
- Every new project already has a default toolbox named after the project; Lab 1 uses that one

</div>
<div>

![w:520](images/mba-catalog-new-toolbox.png)

</div>
</div>

<!-- You can do plenty of non-ModelBuilder work with a new toolbox, such as collecting the tools you use every week in one place. In the labs you do not even need a new toolbox: the project's default toolbox, Lab01.atbx, is where the Analysis ribbon's ModelBuilder button puts the model. -->

---

# Add a model to your toolbox

<div class="columns" style="grid-template-columns: 1fr 1fr;">
<div style="font-size:0.9em;">

- Right-click your toolbox ▸ **New ▸ Model**, or click **ModelBuilder** on the **Analysis** ribbon — the ModelBuilder view opens
- A model has a **Name** and a **Label**. Renaming it in the Catalog pane changes only the *Label*; set the *Name* in **Properties ▸ General**
- A model cannot be renamed while it is open in ModelBuilder: close the view first
- Save with **Ctrl+S**, or ModelBuilder ▸ **Save**

</div>
<div>

![w:245](images/mba-new-model-menu.png)

![w:470](images/mba-tool-properties-general-lab2.png)

</div>
</div>

<!-- Name is the internal name with no spaces, used by arcpy; Label is what people see in the Catalog pane. The screenshot shows the trap: this model was renamed NDVI in the Catalog pane, and its Name is still Model, which is why the dialog title says so. Set both now, because renaming later breaks anything that calls the model by name. Both facts were checked in Pro 3.7.1 on September 6. -->

---

# Set the model's environments

<div class="columns" style="grid-template-columns: 1fr 1fr;">
<div style="font-size:0.9em;">

- Set environments for the whole model with **Environments** on the ModelBuilder ribbon
- **Current workspace** — the geodatabase used for inputs and outputs
- **Output Coordinate System** — empty means *Same as Input*. Leave it empty on purpose, or set it on purpose; never inherit it by accident
- **Scratch workspace** — where intermediate results you do not need to keep are written
- These apply to every tool in the model unless a tool overrides them

</div>
<div>

![w:430](images/mba-environments-dialog.png)

</div>
</div>

<!-- The output coordinate system is the one that bites people. A buffer distance in miles means nothing until the data are in a projected coordinate system with sensible linear units. The Cities Near Rivers example later projects both inputs before buffering for exactly this reason. In Lab 2 the opposite lesson applies: an inherited coordinate system silently reprojects every output. -->

---

# The ModelBuilder ribbon

![w:1050 center](images/mba-modelbuilder-ribbon.png)

<div style="font-size:0.78em;">

- **Model** — New, Save, Properties, Environments, Export, Report
- **View** — Find and Replace, Auto Layout, Fit to Window
- **Mode** — Select, Select All, Pan
- **Run** — Validate, Run, Intermediate
- **Insert** — Variable, Create Label, Tools, Iterators, Utilities, Logical

</div>

**Validate** checks every tool's parameters at once, which is the fastest way to find out why a model will not run. **Auto Layout** and **Fit to Window** are worth pressing often.

<!-- The ribbon tab is contextual: it only appears while a ModelBuilder view is the active view. Auto Layout arranges elements into a readable left-to-right chain. Fit to Window is how you find an element you dragged off the canvas. Run executes the processes that have not run yet; to re-run a model that has already completed, press Validate first. To run one tool in isolation, right-click that element and choose Run. -->

---

# Model elements have three states

<div style="font-size:0.82em;">

**1) Not ready to run** — gray: a required parameter is still empty

![h:100](images/mba-state-notready.png)

**2) Ready to run** — every element is colored: blue inputs, yellow tools, green outputs

![w:880](images/mba-state-ready.png)

**3) Already run** — colored, with a **green check** on everything that has executed

![w:880](images/mba-state-run.png)

</div>

<!-- Reading the canvas is the whole debugging skill. Blue oval = input data, yellow box = tool, green oval = derived output. Gray means a required parameter is still empty, and it propagates downstream, so fix the leftmost gray element first. The green check means that step has already executed and its output exists on disk. All three strips are the same Cities Near Rivers model, exported from ArcGIS Pro 3.7 at three moments. -->

---

# Start building your model

![bg right:38% w:95%](images/mba-connect-menu.png)

- First, plan what you want to do: what data, and what process on each dataset
- If the model is not open, right-click it in the **Catalog pane** and choose **Edit**
- Drag data onto the canvas from the **Catalog** or **Contents** pane
- Add tools from the **Geoprocessing pane**, or click an empty spot on the canvas and **start typing the tool's name**
- To connect two elements, **drag from one onto the other**; a menu asks which parameter the connection feeds

<!-- The connection step is the one that changed from ArcMap. There is no connect tool: you hover the edge of an element, drag onto the target, release, and choose the parameter, as in the menu on the right, captured from the Lab 2 model. Typing on the canvas to add a tool is the fastest route and is what the labs use. -->

---

<!-- _class: lead -->

# Example: Cities Near Rivers

## One problem, start to finish

---

# The problem

![bg right:52% w:96%](images/mba-cities-rivers-map.png)

Find all **U.S. cities within 10 miles of a major river**.

- Two inputs: a **cities** point layer and a **rivers** line layer
- One question that takes several tools in sequence
- Exactly the kind of job you do not want to repeat by hand

<!-- Ask the class how they would do it with tool dialogs before showing the model. They will get close: project, buffer, intersect. Then show them the model and point out that the model is the same answer, written down. -->

---

# The model

![w:1100 center](images/mba-cities-rivers-model-pro.png)

`us_rivers` → **Project** → **Buffer** (10 miles) → areas near rivers; `us_cities` → **Project**; then **Intersect** the two.

<!-- Read the diagram out loud, following the arrows. Both inputs are projected first so that "10 miles" means something, then the rivers are buffered, then Intersect keeps the cities that fall inside the buffer. The intermediate datasets, the green ovals in the middle, are things nobody wants to keep; that is what the Intermediate setting is for. This is the model as built in ArcGIS Pro 3.7 on September 7, 2026, ready to run and not yet run. -->

---

# Two dialogs that decide the answer

<div class="columns" style="grid-template-columns: 1fr 1fr;">
<div style="text-align:center;">

![h:400](images/mba-project-tool-dialog.png)

**Project** — an equidistant projection, and the geographic transformation ArcGIS Pro proposes

</div>
<div style="text-align:center;">

![h:400](images/mba-buffer-tool-dialog.png)

**Buffer** — 10 *Statute Miles*, not 10 *Unknown*; dissolve everything into one feature

</div>
</div>

<!-- Two dialogs, two decisions. Project: the inputs are in WGS 1984 latitude and longitude, where a "mile" has no meaning, so both are projected to USA Contiguous Equidistant Conic; because the datum changes, Pro asks for a geographic transformation and proposes one. Buffer: the unit box reads Unknown until you set it, and it defaults to meters if you only type a number. Dissolving the buffers into one feature keeps Intersect from producing a city twice where two river buffers overlap. Lab 1 has the same Buffer trap. -->

---

# The result

![bg right:52% w:96%](images/mba-cities-rivers-result-pro.png)

**256 of 678 cities** — about **38 percent** — are within 10 miles of a major river.

- Red dots are the cities the model kept
- Dataset: Natural Earth 1:10m populated places and rivers, conterminous U.S. (the download on the next slide)
- Note where they cluster, and where they do not

<!-- The number depends entirely on which cities and rivers you use, so it is quoted with its dataset. This is the same Natural Earth extract students download. The distribution is the interesting part: the Mississippi and Ohio corridors, the Northeast, California's Central Valley. Ask why, and you get a short conversation about where American cities were founded. -->

---

<!-- _class: activity -->

# You try it

![bg right:45% w:96%](images/mba-you-try-it-start.png)

**What percentage of U.S. cities are within 10 miles of a major river?**

- Download [week02-cities-rivers.zip](https://byu-hydroinformatics.github.io/ce414-gis-applications/data/week02-cities-rivers.zip) (under 1 MB) and add `us_cities` and `us_rivers` to a new map
- Build the model: **Project → Buffer → Intersect**
- Project to **USA Contiguous Equidistant Conic** before you buffer, and accept the geographic transformation
- Compare your count with **256 of 678**, and be ready to explain a difference

<!-- Use the hosted download; it is three shapefiles from Natural Earth, public domain, clipped to the lower 48. Buffer and Intersect are in the Analysis toolbox, Project is in Data Management. If someone gets 257 instead of 256, they probably used a geodesic distance instead of a projected one; that difference is a Thursday discussion. -->

---

# Read a model out loud

![w:1100 center](images/mba-state-run.png)

1. **Rivers** are *projected* into a map projection with real distance units
2. The projected rivers are *buffered* 10 miles → **areas near rivers**
3. **Cities** are *projected* the same way
4. Projected cities are *intersected* with the areas → **cities near rivers**

Every green check is a dataset on disk that you can open and inspect.

<!-- This is the skill Lab 1's rubric rewards under "a description of the model a reader could repeat from": say the chain as a sentence, input to output, naming each tool and each intermediate dataset. Practice on this one before you build your own. -->

---

# Lab 1 is the same pattern, longer

![w:1120 center](images/mba-lab1-model-overview.svg)

Select ▸ Intersect ▸ Add Field ▸ Calculate Field ▸ Select ▸ Select ▸ Buffer ▸ Intersect ▸ Buffer ▸ Erase — ten tools, one chain.

<!-- Do not teach the steps here; the lab page does that. The point is recognition: blue inputs, yellow tools, green outputs, connectors, and P markers on the things the user gets to change. Two buffers, two intersects, one erase. Every element on this canvas is something you have now seen. -->

---

# Where the lab's data comes from

![w:1000 center](images/mba-lab1-data-sources.svg)

<!-- This is the data-sources figure from the Lab 1 page. Three of the four layers are downloads from the Utah Geospatial Resource Center; one, the Walmart locations, you make yourself, because the public dataset that used to exist has been taken down. Modeling starts with knowing where every input came from and how far to trust it. -->

---

# Judge the data before you model it

![w:1000 center](images/mba-lab1-metadata-questions.svg)

<!-- Six questions from CCE 114's metadata lecture, each answered for a Lab 1 layer. What, where, when, why, how, who, and the license question underneath. A model built on a layer you cannot answer these questions for is a model with an unknown error in it. The lab's write-up asks for these answers. -->

---

# The tools you will use in Lab 1

<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:12px;text-align:center;font-size:0.72em;margin-top:0.4em;">
<div><img src="images/mba-icon-select.svg" style="width:120px;"><br><strong>Select</strong><br>rows that match an expression</div>
<div><img src="images/mba-icon-intersect.svg" style="width:120px;"><br><strong>Intersect</strong><br>keep where two layers overlap</div>
<div><img src="images/mba-icon-add-field.svg" style="width:120px;"><br><strong>Add Field</strong><br>a new attribute column</div>
<div><img src="images/mba-icon-calculate-field.svg" style="width:120px;"><br><strong>Calculate Field</strong><br>fill it with an expression</div>
<div><img src="images/mba-icon-buffer.svg" style="width:120px;"><br><strong>Buffer</strong><br>a zone at a distance</div>
<div><img src="images/mba-icon-erase.svg" style="width:120px;"><br><strong>Erase</strong><br>remove where another layer is</div>
</div>

Every one is a **Spatial Analysis** or **Data Management** tool you can find by typing its name on the canvas.

<!-- These are the six icons from the Lab 1 page's tool table, so the lab and the lecture use the same vocabulary. Select and Intersect narrow the data; Add Field and Calculate Field compute the density; Buffer draws the distance criteria; Erase removes the areas already served. -->

---

# Two traps, shown once

<div class="columns" style="grid-template-columns: 1fr 1fr;">
<div style="text-align:center;">

![h:380](images/mba-lab1-add-field-dialog.png)

**Add Field** — the type must be **Double**. The default, *Long*, silently drops every decimal.

</div>
<div style="text-align:center;">

![h:380](images/mba-lab1-buffer-dialog.png)

**Buffer** — the unit box reads *Unknown* until you set it, then defaults to **Meters**. Choose *Statute Miles*.

</div>
</div>

<!-- These are the two most expensive mistakes in Lab 1, and both are silent: nothing warns you. A Long density field gives every tract a density of 0, 1 or 2, so nothing passes the 5,000 test; a two-meter buffer selects almost nothing. Both dialogs are captured from the Lab 1 run, and the lab page shows them again where they occur. -->

---

# Things to remember

![bg right:34% w:92%](images/mba-output-context-menu.png)

- To re-open a model for editing, right-click it in the **Catalog pane** and choose **Edit**; double-click runs it as a tool instead
- To make an output appear in the map, right-click that output and check **Add To Display**
- If elements stay gray, a required parameter is missing — open the tool, or press **Validate**
- Right-click a working dataset you do not need to keep and check **Intermediate Data**
- To test one step, right-click that tool element and choose **Run**

<!-- These are the ones students email about. The menu on the right is an output element's right-click menu in Pro 3.7.1: Add To Display is exactly that label. Validate is the single biggest time-saver. The Run group on the ribbon also has an Intermediate button that toggles the same flag on a selected element. -->

---

# Coming up: ModelBuilder, Part B

![bg right:34% w:92%](images/mba-tool-dialog-threshold.png)

- We keep the **Cities Near Rivers** model and make it useful to somebody else
- Turning inputs and distances into **parameters**, so the model becomes a tool with its own dialog, like the one on the right
- **Renaming** elements and documenting a model so a reviewer can read it
- Then a **Lab 1 clinic**: the rubric, a complete submission, checking your answer, peer review

<!-- Part B is the payoff: today's model is hard-wired to one buffer distance and one pair of layers, and by the end of Part B it is a general tool. The dialog on the right is the Lab 2 model as a tool, with the classification threshold exposed; Lab 1 does the same with its two buffer distances. -->

---

# Before Next Class

![bg right:30% w:90%](images/mba-pumpkin-pie.jpg)

- **Sketch a model of baking a cookie** on paper — ovals for ingredients, boxes for steps — and bring it. Thursday starts with it
- Start [Lab 1](https://byu-hydroinformatics.github.io/ce414-gis-applications/assignments/lab-01/): Steps 0 to 4 are within reach tonight
- Read the assigned textbook chapter <!-- TODO(instructor): reading chapter -->
- Take the **open-book quiz** on Learning Suite
- Bring a laptop with ArcGIS Pro, and have a project open before class
- Questions? Office hours: [calendly.com/dan-ames/office-hours](https://calendly.com/dan-ames/office-hours)

<!-- Fill in the reading chapter and the quiz due date before class. The cookie sketch is the prep for Thursday's exercise; a photo of a napkin is fine. -->

<!--
Revision notes (2026-09-07): Part A revised against slides/week-02/LECTURE_PLAN.md. 28 slides -> 35.
- Dropped: the ArcGIS 9 "geoprocessing options" composite, the ArcMap Cities Near Rivers window, the
  drawn element-state diagrams, the monitor clip art, and the unverified "898 of 3,128" figure.
- New ArcGIS Pro 3.7.1 captures (Sept 7, 175 % display scaling, project C:\Ames\Week02\CitiesRivers.aprx):
  four-ways composite (Geoprocessing pane, Python window, canvas, notebook), the three element states
  (SVG exports of the same model), the Project and Buffer dialogs, the ready model, the result map, and
  the You-try-it starting map. Data: docs/data/week02-cities-rivers.zip (Natural Earth 1:10m, public
  domain, conterminous U.S.); the answer 256 of 678 was verified by the model in Pro and by arcpy.
- Reused from the labs (copied into images/ with mba- prefixes): Lab 1 model overview, data-sources and
  metadata infographics, six tool icons, Add Field and Buffer dialogs; Lab 2 model overview, Tool
  Properties General, Environments dialog, connect menu, output context menu, threshold tool dialog.
- Text corrections from the Sept 6 Lab 2 GUI run: Catalog rename sets the Label not the Name; a model
  cannot be renamed while open in ModelBuilder; a run element carries a green check, not a shadow;
  connect-by-drag wording verified; "Add To Display" and "Intermediate Data" labels verified.
- The five-kinds-of-model slide is an HTML tile strip (no AI image; two generated attempts garbled).
- Still open: the reading chapter and quiz date on the last slide.
-->
