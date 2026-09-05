---
search:
  exclude: true
---

# DRAFT — ArcGIS Tips, Tricks, and Important Reminders

> [!WARNING]
> **This is a draft for review, not yet part of the course site.** It is deliberately not linked
> from the site navigation, and no assigned lab currently points at it. It exists to support the
> [draft revision of Lab 1](assignments/lab-01/draft.md). If you want it live, it should go in the
> nav and the short "before you start" reminder should be added to the top of each lab.

Read this before Lab 1, and come back to it whenever a tool "works" but the answer looks wrong.

Everything on this page was checked in **ArcGIS Pro 3.7** during a full run of Lab 1. Where a
setting has moved or been renamed since older versions of these handouts, the current wording is
given.

## Set up your workspace before you start

On the lab machines you only have write access to the **D: drive**, and anyone who logs into that
computer can edit it. So:

1. **Make one folder for this class**, named after you, at the root of D:. For example
   `D:\Smith\`. Use your own name, not your instructor's.
2. **Make one folder per lab inside it**: `D:\Smith\Lab01\`, `D:\Smith\Lab02\`, and so on.
   Put the ArcGIS Pro project *and* the downloaded data for that lab in it.
3. **Back it up every time you leave the lab.** Copy your lab folder to a USB drive, your BYU
   network drive, or cloud storage. These are public machines. Work that exists in only one place
   on a shared computer is work you are choosing to risk.

> [!WARNING]
> **Never put a space in any folder or file name you create.** Use `D:\Smith\Lab01`, never
> `D:\John Smith\Lab 01`. Several geoprocessing tools — the raster analysis tools especially —
> fail or behave strangely on paths containing spaces, and the error message rarely tells you that
> the space is the problem. The same goes for the names you give output datasets: use
> `HighDensity_Tracts`, not `High Density Tracts`.

Do not save projects or data to the C: drive, the desktop, or a network drive. C: and the desktop
may be wiped between sessions, and analysis run across a network connection is slow and prone to
locking errors.

## Creating the project in the right place

In **New Project**, two things trip up almost everyone:

- **The Location box does not accept a typed path.** Click the folder button to its right and use
  the browse dialog. In that dialog, the *Name* box at the bottom *does* accept a full typed path,
  so you can paste `D:\Smith\Lab01` there and click OK.
- **Uncheck "Create a folder for this local project"** if you have already made your `Lab01`
  folder. Leaving it checked gives you `D:\Smith\Lab01\Lab01`, which is not what you want.

## Set the coordinate system before you measure anything

Any tool that measures distance or area — Buffer, and anything that reports area — gives wrong
answers if the data is still in geographic (latitude/longitude) coordinates. Degrees are not miles.

In ModelBuilder, click **Environments** on the **ModelBuilder** ribbon tab (in the *Model* group)
and set **Output Coordinate System**. For anywhere in Utah, use **NAD 1983 UTM zone 12N** — search
for it in the picker; note Pro spells "zone" with a lowercase z. All of Utah falls in UTM zone 12.

Sanity check: after you run a tool, Utah County should come out to about **2,141 square miles**.
Two ways it goes wrong, and they look different:

- **About 0.59** — your data is still in geographic coordinates and that is square *degrees*.
  Obviously wrong, easy to spot.
- **About 3,668** — your data is in **Web Mercator**, which is what several web downloads hand you
  by default. This is the dangerous one: it is in real units, it looks like a plausible county
  area, and it is 71% too big. Web Mercator distorts badly at Utah's latitude and must never be
  used for measurement.

If you get either number, the Output Coordinate System is not set. Do not carry on.

## Four ways to get a confidently wrong answer

These four all produce output, report success, and show no error. They are the most common causes
of a lab that "ran fine" and still earns a poor grade.

### 1. Buffer distances default to meters

The Buffer tool's Distance row has **two** boxes: a number and a unit. The unit reads *Unknown*
until you type a number, and then it silently sets itself to **Meters**. Type `2`, click OK, and
you have made a **two-metre** buffer instead of a two-mile one. Your radius is **1,609 times too
small** — that is just the number of metres in a mile. For a circular buffer the area comes out
about 2.6 million times too small; for a buffer around a long road it is nearer 1,600 times, since
a thin ribbon's area scales with the radius rather than its square.

Always set the unit box yourself. There is no plain "Miles" option in Pro 3.7; choose
**Statute Miles**.

### 2. Add Field defaults to Long (32-bit integer)

If you are creating a field that will hold a calculated value with a decimal part — a density, a
ratio, an average — set **Field Type** to **Double (64-bit floating point)**. The default is Long,
which silently **rounds every value to a whole number** — a density of 8,539.51 is stored as 8,540.
(It rounds rather than truncating, so the loss is easy to miss when you skim the table.)

If you let Calculate Field create the field instead of using Add Field first, you get a **Text**
field, and every later comparison against it breaks.

### 3. Clicking Run with a tool dialog still open

If a tool's dialog is open and you click **Run**, the model runs with whatever was last *committed*
— not what is on screen. A Select tool whose expression has not been committed selects *everything*
and reports success in about a second.

Click **OK** on the tool dialog first, every time. Watch out: the OK button **moves down** when you
switch on the SQL Editor, which is exactly when people miss it.

### 4. Buffer's Dissolve Type defaults to No Dissolve

Buffering 1,500 road segments with "No Dissolve" gives you 1,500 overlapping polygons, and anything
you intersect with them afterwards comes out as a mess of slivers. When you want a single zone,
set **Dissolve Type** to *Dissolve all output features into a single feature*.

## Writing attribute expressions

The expression box has two modes, and the handouts sometimes mix up their wording:

- **Clause mode** (the default) builds `Where [field] [operator] [value]` from dropdowns. This is
  where a phrase like "NAME is Equal to UTAH" comes from.
- **SQL mode** — toggle **SQL Editor** — is where you type real SQL: `NAME = 'UTAH'`.

Things to know:

- **Text values need single quotes and are case sensitive.** `NAME = 'UTAH'` works;
  `NAME = 'Utah'` returns nothing. Numbers take no quotes: `DENSITY > 5000`.
- **A coded field may be text even though its values look like numbers.** UGRC's road
  classification field stores `'1'`, `'2'`, `'3'` as *strings*. `CARTOCODE = 1` fails;
  `CARTOCODE IN ('1','2','3')` works. Check the field type before you write the expression.
- **In ModelBuilder the value box will not list a field's unique values.** In a standalone tool it
  offers a pick list; on a model variable it cannot, because the tool has not run yet. You have to
  type the value, so a typo or wrong capitalisation silently returns zero features.
- **A field created by an upstream tool will not appear in a downstream tool's field list** until
  that upstream tool has actually run. Type the field name in by hand.

## Check what a tool actually produced

Never move to the next step on the strength of a green check mark.

- **Open the attribute table and read the record count.** Does it make sense? If you selected one
  county and got 29, the expression did not take.
- **Watch the count across a step.** Intersecting a layer with a county boundary can return *more*
  features than you started with, because polygons that straddle the line get split, and because
  the two layers' boundaries never line up exactly. Those extra fragments carry the attributes of
  their parent feature, which can be misleading.
- **Look at the map.** Turn the layer on and see where it is. Most mistakes in this course are
  obvious the moment you look at the result instead of the message window.
- **Ask whether each criterion changed anything.** If applying a filter leaves the count and the
  area exactly as they were, that constraint did not bind. That is a legitimate and interesting
  result — say so in your report, and say how you know.

## Creating a point feature class

Several labs ask you to place your own points — candidate sites, existing stores, sample locations.

1. In the **Catalog** pane, expand **Databases**, right-click your project geodatabase
   (`Lab01.gdb`), and choose **New ▸ Feature Class**.
2. Give it a name with no spaces, set **Feature Class Type** to **Point**, and click Next.
3. Add any fields you want to record — a `NAME` text field is usually enough — then set the
   coordinate system to the same one you are using for analysis (NAD 1983 UTM zone 12N), and Finish.
4. The empty layer is added to your map. On the **Edit** ribbon tab click **Create**, pick your new
   layer in the Create Features pane, and click on the map to place each point.
5. Click **Save** on the Edit tab when you are done. Edits are not written until you save.

Use a basemap or imagery to place points accurately, and zoom in — a point placed at the wrong
scale can be a quarter mile off.

## Housekeeping

- **Do not rename or move files outside ArcGIS Pro.** A shapefile is five or more files that must
  stay together, and a project stores paths to its data. Use the Catalog pane to rename or move.
- **Give outputs descriptive names.** `HighDensity_Tracts` tells a grader what it is;
  `Select_Output_3` does not. The same goes for the labels on tools in ModelBuilder — this is
  explicitly part of the rubric in several labs.
- **Statewide downloads are large.** Utah's statewide roads layer is over 400,000 features: about
  140 MB zipped and 600 MB unzipped. Download it once, keep it, and do not re-download it for each
  lab.
