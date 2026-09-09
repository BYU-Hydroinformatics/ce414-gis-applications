# Screenshot capture helpers (local Windows machine, ArcGIS Pro)

Small scripts used to capture the Lab 2 figures from a live ArcGIS Pro 3.7.1 session on
2026-09-06. Run them with the ArcGIS Pro Python (it has Pillow):

    "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" tools\screenshots\capwin.py Lab02 out.png 1208 134 1450 318

All bounding boxes are given in the 1456 x 819 coordinate frame that the desktop-control
screenshots use (a 1920 x 1080 screen scaled by 1456/1920). The scripts convert to native pixels.

| Script | What it does | When to use it |
| --- | --- | --- |
| `grabwin.py TITLE OUT [x0 y0 x1 y1 [pad]]` | Screen grab (physical pixels) of a top-level window found by title prefix; `-` means the largest untitled ArcGIS Pro popup (ModelBuilder tool dialogs). | **Default under display scaling.** `PrintWindow` renders Pro's windows at 96 dpi whatever the scaling, so it cannot capture the sharp 175 % rendering; a screen grab can, provided nothing overlaps the window. |
| `capwin.py TITLE OUT [x0 y0 x1 y1 [pad]]` | `PrintWindow` capture of a top-level window found by exact title (or title prefix) (`Lab02` is the Pro main window; `Classify` a floating dialog). Works even when another window covers it. | **Default.** Anything inside the Pro main window: ModelBuilder canvas, docked panes, the Geoprocessing pane, the map. |
| `capwin2.py OUT` | `PrintWindow` capture of the first visible *untitled* ArcGIS Pro popup window. | The tool dialogs ModelBuilder opens when you double-click a tool (Float, Minus, Reclassify…). They have no window title, so `capwin.py` cannot find them. |
| `cap.py OUT [x0 y0 x1 y1]` | Plain screen grab (`ImageGrab`), optional crop. | Context menus and connection pop-ups, which are transient popups that `PrintWindow` does not see. Only reliable while nothing overlaps the region. |
| `setdpi.py [PERCENT]` | Reports the display's recommended/current/maximum scale; with a percent, sets it instantly (no sign-out). | Before launching Pro for a capture session (175 %), and again with `100` when done. |
| `movewin.py TITLE_PREFIX [x y]` | Moves a top-level window to x,y (`-` = untitled Pro popup). | Pro dialogs that open off-screen after a scaling change. |
| `crop.py IN OUT x0 y0 x1 y1 [pad]` | Crop an existing full-screen grab. | Cutting several figures out of one `cap.py` capture. |

Lessons from the Lab 2 session:

- **Something is always on top.** The Claude desktop window sits over the right third of the
  screen and pops to the front whenever a tool result arrives, and Grammarly's overlay appears the
  moment a text box gets focus. A plain screen grab taken between actions is contaminated more
  often than not. `PrintWindow` with `PW_RENDERFULLCONTENT` (flag 2) sidesteps this entirely for
  anything that is a real window; use it whenever you can.
- **Menus need a screen grab, and a delay.** Start `cap.py` in the background with a `sleep`,
  then open the menu with the desktop-control batch and keep the batch waiting past the capture
  time. The menu closes as soon as another window takes focus.
- **The Pro main window is `Lab02`** (the project name) and it sits at (-8, -8) when maximized,
  so window pixels are screen pixels + 8.
- Keep crops tight to the pane or dialog; keep the dialog title bar; PNG for anything with text,
  JPEG for map captures (they are photographs of a basemap and compress 4-5x).

Lessons from the second Lab 2 session (2026-09-06, evening, display scaling 175 %):

- **Capture at higher display scaling.** Windows *Settings > Display > Scale* caps this 1920 x 1080
  screen at 175 % (200 % needs a custom scale and a sign-out). `setdpi.py`-style
  `DisplayConfigSetDeviceInfo(DISPLAYCONFIG_DEVICE_INFO_SET_DPI_SCALE)` applies it instantly and
  reversibly; launch Pro *after* changing it. Every dialog then comes out 1.75x its 100 % size. The
  desktop-control coordinate frame stays 1456 x 819 and the scripts' bbox conversion is unchanged.
- **Make the scripts DPI-aware** (`SetProcessDpiAwareness(2)` before any `user32` call) or
  `GetWindowRect` returns virtualized coordinates.
- **PrintWindow is useless under scaling** (see `grabwin.py` above); use screen grabs, so
  occlusion matters again: park the Claude window off the right edge (`SetWindowPos` to x = 1914)
  rather than minimizing it — it restores itself whenever a tool result arrives, and it has
  keyboard focus when it does — and stop Grammarly for the session (its overlay attaches to any
  text box that gets focus and blocks input).
- **Pro opens its dialogs off-screen** after a scaling change (they remember positions from a
  larger virtual desktop). `movewin.py TITLE_PREFIX x y` (`-` for untitled popups) drags them back.
- Mouse-wheel scrolling does not register anywhere in Pro through desktop control: drag scrollbar
  thumbs, or use the keyboard.
- The run dialog's message log renders at a large font at 175 % and will not scroll; capture the
  dialog wider (drag its grip) rather than fighting it.

Lessons from the Week 2 Part B session (2026-09-08, 175 %, `CitiesRivers.aprx`):

- **`stitch.py OUT SKIP IN1 IN2 ...`** joins scrolled captures of one tall view (the metadata
  editor, the View Metadata page) by locating the top 150 px of each capture inside the previous
  one; `SKIP` is the height of a fixed header to drop from the later captures (55 px for the
  Catalog view's Metadata/Geography/Table strip). Scroll with the scrollbar arrow buttons, which
  move in fixed steps; the scrollbar thumb is far too sensitive (30 px of thumb is 800 px of
  canvas). If the match error stays above about 1, the control scrolled by a fractional pixel and
  re-rendered its text; pick the local minimum and check the seam by eye.
- **Context menus flip upward** when the element sits in the lower half of the screen and the
  menu would cross the taskbar; the flipped menu covers the ribbon. Arrange the model so the
  elements you will right-click sit near the top of the canvas (here: rivers row on top, cities
  row below), then menus open downward next to the element. A three-level menu (Create Variable
  > From Parameter > Distance) needs the right-click near the element's left edge to fit.
- **A right-click while a menu is still open** is swallowed by the open menu. End every menu
  batch with Escape and a click on empty canvas, and hover an item before the grab so it is
  highlighted.
- **Dragging a canvas element** only works on a selected element: click it, then mouse down,
  several mouse_move steps, mouse up. `left_click_drag` (one instantaneous move) does nothing in
  ModelBuilder; the same is true of the Pan tool.
- **The "Show Toolbar" overlay** at the canvas's top-right corner is semi-transparent and lands
  in any strip that reaches that corner. Paint the light pixels of that corner white afterwards
  rather than moving the model (a threshold of 185 keeps the P badge ring and element borders).
- After `front.py`/`park.py`, the first click in Pro sometimes does nothing: `mouse_move` to the
  target first, then click.
- Ctrl+R renames the selected element in place, Ctrl+P toggles Parameter, Ctrl+S saves the model;
  all three work without the menu. A new variable from Create Variable > From Parameter lands on
  top of the tool's input element and has to be dragged clear.
- The Geoprocessing pane only re-reads the model's parameters when the model is re-opened
  (double-click it in Catalog again) after Ctrl+S.
- The Save-project icon is the third Quick Access icon; the first is New Project.

Lessons from the Week 3 session (2026-09-09, 175 %, `Lab02.aprx`, Geoprocessing-pane dialogs):

- **Do the analysis headlessly first** (`tools/week03_prep.py` with arcpy into a scratch
  geodatabase), then use the GUI only to fill dialogs and show results. The numbers for the speaker
  notes come from the script, the captures come from the session, and the project is closed
  without saving.
- **Add data from the Catalog pane's Computer tab** (This PC > drive > folder > .gdb), right-click
  > Add To Current Map; answer the Build Pyramids prompt with Yes. A click on an already-selected
  Catalog item opens rename mode, and Escape does not always leave it: click the box and press
  Enter to accept the unchanged name.
- **Geoprocessing dialogs**: type a layer name into a combo box and press Delete before Tab, or
  type-ahead completes it to the first longer match (`NDVI` became `NDVI_intdiv`). A full path typed
  into a feature-class box is shortened to the name once validated. The layer dropdown does not
  refresh while open; close and reopen it after adding a layer. Tall dialogs are two grabs plus
  `stitch.py` with SKIP 161 (the pane's fixed header at 175 %).
- **Go To XY** rejects a typed minus sign through desktop control; use `111.95W` / `39.95N`. The
  scale box needs a click, Ctrl+A, the bare number, Enter. A left-click on the map with the
  Explore tool opens a pop-up over the map; close it before grabbing.
- **Table views** open as a short panel under the map and the divider would not drag; for a
  student-facing table, put the numbers in HTML on the slide and keep the small capture as proof.
- The Toolboxes tree scrolls with the keyboard (End, Up/Down, Right to expand); grab overlapping
  views and stitch, then bleach the selection highlight (light-blue pixels) before use.
