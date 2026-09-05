# Lab 1 figure pipeline

Scripts that regenerate the Lab 1 draft graphics. Run with the ArcGIS Pro Python:
`"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"`.

- `make_svgs.py` — writes the six tool icons (`icon-*.svg`) and the two infographics
  (`lab01-metadata-questions.svg`, `lab01-data-sources.svg`) into `docs/assignments/lab-01/images/`.
  Hand-authored SVG with real text; edit the card text in the script and re-run.
- `scenario.py` — builds the Step 12 scenario output (3-mile Walmart exclusion) in
  `C:\Ames\Lab01\Lab01.gdb` and lists candidate polygons for the recommended site.
- `build_layouts.py X Y` — copies `Lab01.aprx` to `Lab01_Layouts.aprx`, builds the baseline and
  scenario layouts with arcpy.mp (basemaps need Pro signed in) and exports them to
  `C:\Ames\Lab01\Exports\`; copy the PNGs into the images folder. `X Y` is the recommended site
  in UTM 12N (426450 4475078 = the vacant field in north Lehi used in the published figures).

Lesson learned: the legend only renders correctly with the title shown, `fittingStrategy =
"AdjustFontSize"` and a frame about 1.8 in tall; `AdjustFrame` or CIM font overrides blow the
patches up to page size. Headless Chrome renders HTML pages blank here with `--disable-gpu`;
omit that flag (it is fine for bare SVG files).
