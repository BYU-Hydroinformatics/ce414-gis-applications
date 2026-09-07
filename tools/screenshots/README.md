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
