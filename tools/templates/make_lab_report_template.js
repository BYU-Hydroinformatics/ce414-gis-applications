// Build a fillable Word lab-report template for a CE 414 lab.
//
//   node make_lab_report_template.js 03
//
// Everything lab-specific lives in the LABS block below; the builder underneath is generic.
// The rubric is read straight out of the lab page, so a template cannot drift from what is graded.
// See tools/lab-report-template-guide.md.

const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, PageBreak,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, PageOrientation,
  LevelFormat, convertInchesToTwip, HeightRule,
} = require('docx');
const fs = require('fs');
const path = require('path');

const REPO = path.resolve(__dirname, '..', '..');

// ───────────────────────────── lab-specific content ─────────────────────────────
const LABS = {

'01': {
  labTitle: 'Lab 1: Walmart Site Selection',
  labSubtitle: '',
  sections: [
    { h: 'Requirements and Approach',
      hint: 'Rubric: the requirements of the project and your approach to solving it, in your own words (2 points). Two or three paragraphs. Say what you were asked to produce and how you went about it — not a retelling of the step-by-step.' },

    { h: 'Your Walmart Point Data',
      hint: 'Rubric: how you created your Walmart point data and why you trust it — the store finder or map you used, how many stores you found, and which formats you included (1 point). "Which formats" means Supercenter, Neighborhood Market and so on: say which you counted and which you left out, and why.',
      table: { caption: 'Table 1. How the Walmart points were built.',
               head: ['Item', 'Your answer'],
               rows: [['Source (store finder or map)', ''], ['Date you collected it', ''],
                      ['Number of stores found', ''], ['Formats included, and any you excluded', ''],
                      ['Why you trust it, and where it may be wrong', '']],
               widths: [4000, 5360] } },

    { h: 'The Model',
      hint: 'Rubric: a description a reader could repeat from — each tool, its settings, and every input, intermediate and output dataset with its type and source (2 points). Fill one row per tool, in the order they run, and fill both the Type and the Source column.',
      table: { caption: 'Table 2. Model description — one row per tool.',
               head: ['Tool', 'Settings', 'Input dataset(s)', 'Output dataset', 'Type', 'Source'],
               rows: [['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', '']],
               widths: [1400, 2100, 2100, 1500, 1000, 1260] },
      figures: [
        { caption: 'Figure 1. The complete model, exported from ModelBuilder with Export ▸ Export To Graphic.',
          hint: 'Rubric: a full-page (8.5 × 11) figure of the model — every tool and dataset shown, labels informative, all text readable at 10 pt or larger (2 points).' },
        { caption: 'Figure 2. The model’s toolbox interface, with the two buffer distances exposed as parameters.', size: 'medium',
          hint: 'Rubric: a screen capture of the toolbox interface with the two buffer distances exposed as parameters, showing the input and output parameters (2 points).' },
      ] },

    { h: 'Which Criteria Actually Narrowed the Result',
      hint: 'Rubric: which of the three spatial criteria actually narrowed your result and which did not, with the counts and areas that show it (1 point). One of the three does almost nothing at its default value in Utah County. Show that with numbers, not an impression.',
      table: { caption: 'Table 3. What each criterion removed.',
               head: ['Criterion', 'Candidate polygons after', 'Total area after', 'What it removed'],
               rows: [['Density over 5,000 per sq mi', '', '', ''],
                      ['Within 2 miles of a major road', '', '', ''],
                      ['More than 2 miles from an existing Walmart', '', '', '']],
               widths: [3000, 1900, 1600, 2860] } },

    { h: 'Your Recommendation',
      hint: 'Rubric: where the best locations for a new Walmart are, which one site you recommend, and why you selected it (3 points). Name the site, say where it is, and give reasons a reader could argue with — not just that the model returned it.' },

    { h: 'Sensitivity Analysis', pageBreakBefore: true,
      hint: 'Rubric: a table of at least three additional runs, giving the parameter values, the number of candidate polygons and the total area for each (4 points). Choose your runs deliberately and say why you chose them. Change one number at a time from the baseline, so your table can show which one matters.',
      table: { caption: 'Table 4. Sensitivity — the baseline and at least three more runs.',
               head: ['Run (what changed)', 'Density threshold', 'Road buffer', 'Walmart exclusion', 'Candidate polygons', 'Total area', 'Site still suitable?'],
               rows: [['Baseline', '5,000 / sq mi', '2 miles', '2 miles', '', '', ''],
                      ['', '', '', '', '', '', ''], ['', '', '', '', '', '', ''], ['', '', '', '', '', '', '']],
               widths: [1300, 1400, 1150, 1400, 1450, 1200, 1460] },
      questions: [
        'Which parameter does your answer depend on most, and which barely matters? Support it with the numbers from your table, not an impression. (2 points)',
        'Is there a setting at which no suitable site exists at all? If so, what does that tell you about the criteria — or about Utah County? (2 points)',
        'Does your recommended site survive every scenario you ran, or only some? If only some, is it still your recommendation? Defend your answer either way. (2 points)',
      ] },

    { h: 'Maps', pageBreakBefore: true,
      hint: 'Both maps are full-page, 8.5 × 11. Put each on its own page. Symbolize the suitability layer the same way on both, so a reader can compare them.',
      figures: [
        { caption: 'Map 1. Baseline — the target zones at the criteria as given.', pageBreakAfter: true,
          hint: 'Must carry: title, neat line, north arrow and scale bar; a text box with author, date and map projection; existing Walmarts with an appropriate symbol and every existing and proposed location labeled; the final suitability layer shown so a reader can see the effect of your intersection and erase; your recommended site or sites clearly marked; close-up data frames or an inset of the spots you selected; a visible basemap at a sensible scale, all text legible in print.' },
        { caption: 'Map 2. Scenario — one run from Step 12.',
          hint: 'Everything Map 1 needs except the close-ups, plus: the title and text box say which parameters were changed, to what, and why you chose this run to show.' },
      ] },

    { h: 'References', pageBreakBefore: true,
      hint: 'Rubric: sources credited (part of the point for organized writing). Credit the census data, the roads, your Walmart source and the basemap.' },
    { h: 'AI Use Statement',
      hint: 'Course policy: one line saying what you used AI for. If you used none, say that. Field names, expressions, coordinate systems and numbers come from your own data, never from a model.' },
    { h: 'Self-Graded Rubric', pageBreakBefore: true, rubric: true,
      hint: 'Rubric: this rubric pasted in with your self-assessment in every row (part of the point for organized writing). Put a score in every row, honestly arrived at. The grader compares yours with theirs.' },
  ],
},

'02': {
  labTitle: 'Lab 2: NDVI',
  labSubtitle: 'Classifying Land Based on NDVI',
  sections: [
    { h: 'Requirements and Approach',
      hint: 'Rubric: the requirements of the project and your approach to solving it, in your own words (2 points). Two or three paragraphs. Say what you were asked to produce and how you went about it — not a retelling of the step-by-step.' },
    { h: 'Data and Scene Metadata',
      hint: 'Rubric: the three MTL values — acquisition date, cloud cover and the reflectance offset — and what each one means for your result (2 points). Fill the table, then add a sentence on anything the numbers change about how far you trust the answer.',
      table: { caption: 'Table 1. Scene metadata from the MTL file.',
               head: ['MTL value', 'What you found', 'What it means for your result'],
               rows: [['DATE_ACQUIRED', '', ''], ['CLOUD_COVER', '', ''], ['Reflectance offset', '', '']],
               widths: [2200, 2400, 4760] } },
    { h: 'The Model',
      hint: 'Rubric: a description a reader could repeat from — each tool, its settings, and every input, intermediate and output dataset with its type; for each input, the satellite and band, acquisition date, cloud cover and source (2 points). Fill one row per tool, in the order they run, and fill both the Type and the Source column.',
      table: { caption: 'Table 2. Model description — one row per tool.',
               head: ['Tool', 'Settings', 'Input dataset(s)', 'Output dataset', 'Output type'],
               rows: [['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', '']],
               widths: [1500, 2400, 2400, 1700, 1360] },
      figures: [
        { caption: 'Figure 1. The complete model, exported from ModelBuilder with Export ▸ Export To Graphic.',
          hint: 'Rubric: a full-page (8.5 × 11) figure of the model — every tool and dataset shown, labels informative, all text readable at 10 pt or larger (2 points). Export it; do not screen-capture it.' },
        { caption: 'Figure 2. The model’s toolbox interface, with the threshold exposed as a parameter.', size: 'medium',
          hint: 'Rubric: a screen capture of the toolbox interface with the threshold exposed as a parameter, showing the input and output parameters (2 points).' },
      ] },
    { h: 'Threshold Sensitivity',
      hint: 'Rubric: a table of at least three additional runs, giving the threshold, the cells in class 1 and the area for each (4 points). Report the check values at the handout’s threshold too, so a reader can see your model reproduces them.',
      table: { caption: 'Table 3. Threshold sensitivity — at least three runs beyond the baseline.',
               head: ['Threshold', 'Cells in class 1', 'Area (sq mi)', 'Percent of county', 'What the map looks like'],
               rows: [['0.4 (baseline)', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', '']],
               widths: [1300, 1700, 1500, 1600, 3260] },
      questions: [
        'Which threshold best matches the fields you can verify? Support it with NDVI values you read, not an impression. (2 points)',
        'At what threshold does the forest drop out — and what else drops out with it? (2 points)',
        'Is a single NDVI threshold enough to map irrigation in this county? If not, what would you add, and how would it help? (2 points)',
      ] },
    { h: 'Where the Classification Is Wrong',
      hint: 'Rubric: where the classification is wrong and why, and what additional data would fix it (3 points). Name the places it fails and the reason, then name the data that would fix each one.' },
    { h: 'Maps', pageBreakBefore: true,
      hint: 'Both maps are full-page, 8.5 × 11. Put each on its own page. The rubric grades every element separately — see the rubric table at the end of this report.',
      figures: [
        { caption: 'Map 1. Baseline — the classified NDVI at the threshold you chose and defended.', pageBreakAfter: true,
          hint: 'Must carry: title stating the threshold; neat line, north arrow, scale bar; a text box with author, date, map projection, and the satellite, scene and acquisition date; the classified raster symbolized with a legend; the county polygon and a few labeled cities; an inset of the center-pivot area; a visible basemap at a sensible scale, all text legible in print.' },
        { caption: 'Map 2. Scenario — the same model at a different threshold from Step 6.',
          hint: 'Everything Map 1 needs except the inset, plus: the title and text box say what the threshold was changed to and why you chose this run to show.' },
      ] },
    { h: 'References', pageBreakBefore: true,
      hint: 'Rubric: sources credited (part of the 2 points for organized writing). Credit the data, the basemap and anything you quoted or relied on.' },
    { h: 'AI Use Statement',
      hint: 'Course policy: one line saying what you used AI for. If you used none, say that. Field names, expressions, coordinate systems and numbers come from your own data, never from a model.' },
    { h: 'Extra Credit — the Magic Valley Extract (optional)', pageBreakBefore: true,
      hint: 'Optional, up to +5. Delete this whole section if you are not attempting it. Report the cells and area of class 1, the NDVI you read at a pivot and at ground you can verify is not irrigated, a map or figure, and a paragraph on whether your threshold transfers.',
      figures: [{ caption: 'Figure 3. The Magic Valley result at your chosen threshold.', size: 'medium' }] },
    { h: 'Self-Graded Rubric', pageBreakBefore: true, rubric: true,
      hint: 'Rubric: this rubric pasted in with your self-assessment in every row (part of the 2 points for organized writing). Put a score in every row, honestly arrived at. The grader compares yours with theirs.' },
  ],
},

'03': {
  labTitle: 'Lab 3: Georectifying and Digitizing Historic Maps',
  labSubtitle: '',
  sections: [
    { h: 'Requirements and Approach',
      hint: 'Rubric: the requirements of the project and your approach, in your own words (2 points). Two or three paragraphs. Say what you set out to find and how you went about it — not a retelling of the step-by-step. Say why you chose this sheet.' },

    { h: 'The Historic Sheet',
      hint: 'Rubric: the source of your sheet — repository, title, survey and publication dates, scale and URL — and the six metadata answers, with what they mean for your result (3 points). If a date is genuinely not recorded on the sheet, say so; that is a real answer, a blank is not.',
      table: { caption: 'Table 1. Source of the historic sheet.',
               head: ['Item', 'Your answer'],
               rows: [['Repository', ''], ['Sheet title', ''], ['Survey date', ''],
                      ['Publication date', ''], ['Scale', ''], ['URL', '']],
               widths: [2600, 6760] },
      table2: { caption: 'Table 2. The six metadata questions, applied to your sheet.',
                head: ['Question', 'Your answer', 'What it means for your result'],
                rows: [['What does it show, and at what scale?', '', ''],
                       ['Where does it cover, and can you match features?', '', ''],
                       ['When was it surveyed, and when published?', '', ''],
                       ['Why was it made?', '', ''],
                       ['How was it surveyed, drawn and scanned?', '', ''],
                       ['Who made it, and may you use it?', '', '']],
                widths: [2700, 3200, 3460] } },

    { h: 'Georeferencing',
      hint: 'Rubric: at least eight control points, distributed across the whole sheet rather than clustered, with the count reported (3 points); the Control Point Table read — total RMS error reported, and any outlying residual investigated and explained (2 points); which basemap you georeferenced against and why, and which coordinate system your map is in (2 points).',
      table: { caption: 'Table 3. Georeferencing summary.',
               head: ['Item', 'Your answer'],
               rows: [['Control points used', ''],
                      ['How you distributed them (and anywhere you could not)', ''],
                      ['Total RMS error (baseline transformation)', ''],
                      ['Largest residual, what you found, and what you did about it', ''],
                      ['Basemap georeferenced against, and why', ''],
                      ['Coordinate system, and why', '']],
               widths: [4200, 5160] } },

    { h: 'The Check Feature',
      hint: 'Rubric: a check made at one feature that was NOT used as a control point, with the error at that feature reported as a distance (3 points). Name the feature so a reader could re-measure it, say how you measured (which tool, from what to what), and give the distance with its unit. Pick something a good way from your control points.' },

    { h: 'Digitizing',
      hint: 'Rubric: at least six features from the historic sheet that are not on the modern basemap (3 points); a feature class in the project geodatabase, correct geometry type, in the map’s coordinate system (2 points); a Location_Name field populated and labeled on the map (2 points); a description of what each feature is, what it was called, and what is there now (3 points). Name the field Location_Name — the rubric names it.',
      table: { caption: 'Table 4. Digitized features — one row each, at least six.',
               head: ['Location_Name', 'Geometry type', 'What it was', 'What is there now'],
               rows: [['', '', '', ''], ['', '', '', ''], ['', '', '', ''],
                      ['', '', '', ''], ['', '', '', ''], ['', '', '', '']],
               widths: [2000, 1500, 2930, 2930] } },

    { h: 'Transformation Sensitivity', pageBreakBefore: true,
      hint: 'Rubric: the table, at least three transformations, with control points, total RMS error, check-feature error and a description for each (4 points). Use the same control points for every run. The check-feature column is the one that does the work — a transformation can drive RMS to zero and still be worse where it matters.',
      table: { caption: 'Table 5. Transformation sensitivity — at least three transformations, same control points.',
               head: ['Transformation', 'Control points', 'Total RMS error', 'Error at check feature', 'What the sheet looks like'],
               rows: [['1st Order Polynomial (Affine)', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', '']],
               widths: [2100, 1250, 1450, 1650, 2910] },
      questions: [
        'Which transformation gave the lowest total RMS error, and is that the one you would use? Explain the difference between the two answers if there is one. (2 points)',
        'What happened at your check feature as you changed transformations? Did it track the RMS error, or move the other way? (2 points)',
        'Which transformation would you defend to a client, and what would you tell them your georeferencing is good to? Give a distance, and say how you know. (2 points)',
      ] },

    { h: 'Where Your Result Is Wrong',
      hint: 'Rubric: where your result is wrong and why, and what data would fix it (2 points). Name where it fails and the reason — the sheet, the scan, your control points, the basemap — then name the data that would fix each one.' },

    { h: 'Maps', pageBreakBefore: true,
      hint: 'Both maps are full-page, 8.5 × 11. Put each on its own page. Map 2 is graded inside the Transformation sensitivity row: it is the run you chose to show, and its title and text box have to say what changed and why you chose it.',
      figures: [
        { caption: 'Map 1. Baseline — the transformation you would defend.', pageBreakAfter: true,
          hint: 'Must carry: title stating the transformation used; neat line, north arrow, scale bar; a text box with author, date, map projection, and the sheet’s title and date; all three layers (modern basemap, georeferenced sheet, digitized features); the digitized features symbolized and labeled, with a legend; your control points shown; an appropriate scale with all text legible in print.' },
        { caption: 'Map 2. Alternative — the same area under a different transformation from Step 8.',
          hint: 'Everything Map 1 needs, plus: the title and text box say which transformation this is and why you chose to show it.' },
      ] },

    { h: 'References', pageBreakBefore: true,
      hint: 'Rubric: sources credited (part of the 2 points for organized writing). Credit the sheet and its repository, the basemap, and anything else you relied on.' },
    { h: 'AI Use Statement',
      hint: 'Course policy: one line saying what you used AI for. If you used none, say that. Control points, coordinate systems, measured distances and RMS values come from your own work, never from a model.' },
    { h: 'Self-Graded Rubric', pageBreakBefore: true, rubric: true,
      hint: 'Rubric: this rubric pasted in with your self-assessment in every row (part of the 2 points for organized writing). Put a score in every row, honestly arrived at. The grader compares yours with theirs.' },
  ],
},

'06': {
  labTitle: 'Lab 6: Lake Depth Explorer',
  labSubtitle: 'Shorelines at Every Water Level — Looping in ModelBuilder, at Lake Powell',
  sections: [
    { h: 'Requirements and Approach',
      hint: 'Rubric: the requirements of the project and your approach to solving it, in your own words (2 points). Two or three paragraphs. Say what you set out to show and how you went about it — not a retelling of the step-by-step. If you built the model without the step-by-step instructions, say so here.' },

    { h: 'The Surface and Its Metadata',
      hint: 'Rubric: the three metadata values for the surface and what each means for your result (2 points). The vertical datum matters more than it looks — every elevation you type into the iterator is measured from it.',
      table: { caption: 'Table 1. Metadata for the surface.',
               head: ['Metadata value', 'What you found', 'What it means for your result'],
               rows: [['Survey date', '', ''], ['Vertical datum', '', ''], ['Cell size', '', '']],
               widths: [2300, 2400, 4660] } },

    { h: 'The Model',
      hint: 'Rubric: a description a reader could repeat from, including how the loop value reaches the tools inside it (2 points). Say what the iterator is, what its three values are, what happens inside the loop, and how the results are collected into one feature class.',
      table: { caption: 'Table 2. Model description — the iterator, then one row per tool inside the loop.',
               head: ['Element', 'Settings', 'Input dataset(s)', 'Output dataset', 'Type'],
               rows: [['For (iterator)', '', '', '', ''], ['Con', '', '', '', ''], ['Raster to Polygon', '', '', '', ''],
                      ['Select Layer By Location', '', '', '', ''], ['Copy Features', '', '', '', ''],
                      ['Calculate Field (Elevation)', '', '', '', ''], ['Calculate Field (AreaSqMi)', '', '', '', ''],
                      ['Collect Values', '', '', '', ''], ['Merge', '', '', '', '']],
               widths: [1700, 2200, 2200, 1700, 1560] },
      figures: [
        { caption: 'Figure 1. The complete model, exported from ModelBuilder with Export ▸ Export To Graphic.',
          hint: 'Rubric: a full-page model figure exported from ModelBuilder, with the iterator, the loop, and the collector readable (2 points).' },
        { caption: 'Figure 2. The model’s toolbox interface, showing its parameters (at least From, To and By).', size: 'medium',
          hint: 'Rubric: a screen capture of the toolbox interface with the low, high, and step parameters exposed (2 points).' },
      ] },

    { h: 'Shore Features',
      hint: 'Rubric: the shore-feature table — how you chose the features and the elevation at which each goes dry (2 points). Say in a sentence how you picked them before the table, then fill one row per feature. Its elevation is what you sampled; the goes-dry level is the pair of shorelines from your model that it falls between.',
      table: { caption: 'Table 3. Shore features, their elevations, and the water level at which each goes dry (ft NGVD29).',
               head: ['Feature', 'What it is', 'Surface sampled', 'Its elevation', 'Goes dry between', 'NPS cutoff'],
               rows: [['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', '']],
               widths: [1700, 2000, 1300, 1200, 1900, 1260] } },

    { h: 'Range and Step Sensitivity', pageBreakBefore: true,
      hint: 'Rubric: one table with the baseline and at least three additional runs, giving the range, the step, the number of shorelines, the areas at the lowest and highest elevations, and the run time for each (4 points). Choose your values deliberately and say why. The run time is the Elapsed Time in the pop-up when a run finishes.',
      table: { caption: 'Table 4. Range and step sensitivity — the baseline and at least three more runs.',
               head: ['Run (what changed)', 'Low', 'High', 'Step', 'Shorelines', 'Area at lowest', 'Area at highest', 'Run time', 'What it shows'],
               rows: [['Baseline', '', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', ''],
                      ['', '', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', '', '']],
               widths: [1200, 700, 700, 650, 1000, 1100, 1100, 960, 1950] },
      questions: [
        'Which shore features go dry, and at what elevation? Does the answer change with the step, and if so, how far? (2 points)',
        'How much does the lake’s area change per unit of elevation, and is that rate the same at the bottom of the range as at the top? What about the basin’s shape explains the difference? (2 points)',
        'What is the smallest step that still shows the shape of the basin? What did the finer runs cost? (2 points)',
      ] },

    { h: 'Where the Shorelines Are Wrong',
      hint: 'Rubric: where the shorelines are wrong and why, and what data would fix it (2 points). The seam between surveys, the 30 m cells in narrow canyons, the hollows removed in Step 4, the 2017 survey date against sediment and construction since — name each one and say what data would fix it.' },

    { h: 'Maps', pageBreakBefore: true,
      hint: 'Both maps are full-page, 8.5 × 11. Put each on its own page. Symbolize the shorelines the same way on both, so a reader can compare them.',
      figures: [
        { caption: 'Map 1. Baseline — the nested shorelines at the default range and step.', pageBreakAfter: true,
          hint: 'Must carry: title stating the elevation range and step; neat line, north arrow and scale bar; a text box with author, date, map projection, and the surface’s source, survey date and vertical datum; the nested shorelines symbolized so each elevation is readable, with a legend; your shore-feature points, labeled; an inset or close-up of one feature at the elevation it goes dry; basemap, scale and legibility appropriate to the lake.' },
        { caption: 'Map 2. Scenario — a different range or step from Step 7.',
          hint: 'Everything Map 1 needs except the inset, plus: the title and text box say what changed from Map 1 and why this run was chosen.' },
      ] },

    { h: 'References', pageBreakBefore: true,
      hint: 'Rubric: sources credited (part of the point for organized writing). Credit the surface and its survey, the basemap and anything else you relied on.' },
    { h: 'AI Use Statement',
      hint: 'Course policy: one line saying what you used AI for. If you used none, say that. Elevations, areas, datums and cell sizes come from your own data, never from a model.' },
    { h: 'Self-Graded Rubric', pageBreakBefore: true, rubric: true,
      hint: 'Rubric: this rubric pasted in with your self-assessment in every row (part of the point for organized writing). Put a score in every row, honestly arrived at. The grader compares yours with theirs.' },
  ],
},

'07': {
  labTitle: 'Lab 7: Avalanche Hazard',
  labSubtitle: 'Terrain-based avalanche hazard screening from slope, aspect, and elevation',
  sections: [
    { h: 'Requirements and Approach',
      hint: 'Rubric: the requirements of the project and your approach to solving it, in your own words (2 points). Two or three paragraphs. Say what you set out to show and how you went about it — not a retelling of the step-by-step. If you built the model without the step-by-step instructions, say so here.' },

    { h: 'The DEM and Its Metadata',
      hint: 'Rubric: the three metadata values for the DEM and what each means for your result (2 points). Confirm them yourself from READ-ME-FIRST.txt, the raster’s properties and the tile’s metadata file — do not copy them from Figure A.',
      table: { caption: 'Table 1. Metadata for the DEM.',
               head: ['Metadata value', 'What you found', 'What it means for your result'],
               rows: [['Publication date and source dates', '', ''], ['Vertical datum and units', '', ''], ['Cell size', '', '']],
               widths: [2600, 2400, 4360] } },

    { h: 'The Model',
      hint: 'Rubric: a description a reader could repeat from — each tool, its settings, and every input, intermediate and output dataset with its type (2 points). Fill one row per tool, in the order they run.',
      table: { caption: 'Table 2. Model description — one row per tool.',
               head: ['Tool', 'Settings', 'Input dataset(s)', 'Output dataset', 'Type'],
               rows: [['Project Raster', '', '', '', ''], ['Slope', '', '', '', ''], ['Aspect', '', '', '', ''],
                      ['Reclassify (slope)', '', '', '', ''], ['Reclassify (aspect)', '', '', '', ''],
                      ['Raster Calculator (altitude, with Shift)', '', '', '', ''], ['Raster Calculator (all three agree)', '', '', '', ''],
                      ['Raster Calculator (geometric mean)', '', '', '', ''], ['Cell Statistics (maximum)', '', '', '', ''],
                      ['Cell Statistics (minimum)', '', '', '', ''], ['Raster Calculator (rule spread)', '', '', '', '']],
               widths: [2300, 2100, 2000, 1700, 1260] },
      figures: [
        { caption: 'Figure 1. The complete model, exported from ModelBuilder with Export ▸ Export To Graphic.',
          hint: 'Rubric: a full-page model figure exported from ModelBuilder, all tools and datasets readable (2 points). Export it; do not screen-capture it.' },
        { caption: 'Figure 2. The model’s tool dialog, with the Shift parameter exposed.', size: 'medium',
          hint: 'Rubric: a screen capture of the toolbox interface with the shift parameter exposed (2 points).' },
      ] },

    { h: 'Snowbird by Hazard Class',
      hint: 'Rubric: the model runs end to end from its tool dialog and its Step 8 table of Snowbird’s areas at shift 0 matches the check values (part of the 4 points for a working model). Tabulate Area reports square meters; divide by 1,000,000.',
      table: { caption: 'Table 3. Snowbird’s area in each hazard class at shift 0 (km²), geometric mean.',
               head: ['Low', 'Moderate', 'Considerable', 'High', 'Extreme', 'Total'],
               rows: [['', '', '', '', '', '']],
               widths: [1560, 1560, 1560, 1560, 1560, 1560] } },

    { h: 'All Three Agree',
      hint: 'Rubric: the “all three agree” result and why it is the wrong answer (2 points). Give its check value — how much of Snowbird it leaves unclassified — and explain, with one cell as an example, what the rule throws away.' },

    { h: 'Elevation Bands and Combination Rules', pageBreakBefore: true,
      hint: 'Rubric: one table with the baseline and at least three more runs, giving the shift, the altitude-class-5 area, and the High + Extreme area of Snowbird under each of the three rules (4 points). Choose your shifts deliberately and say why.',
      table: { caption: 'Table 4. Sensitivity — the baseline and at least three more runs (km² of Snowbird).',
               head: ['Run', 'Shift (m)', 'Altitude class 5', 'High + Extreme, geometric mean', 'High + Extreme, worst factor', 'High + Extreme, best factor'],
               rows: [['Baseline', '0', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', '']],
               widths: [1200, 1000, 1500, 1900, 1880, 1880] },
      questions: [
        'How much does moving the elevation bands change the map, in each direction? Use the altitude-class column to say why. (2 points)',
        'How much does the combination rule change the map? For the same run, compare the three rules. Which would you publish, and to whom? (2 points)',
        'Where do the three rules agree, and where do they disagree most? Map Rule_Spread at shift 0 beside the imagery and say what terrain sits at 0 and at 4. (2 points)',
      ] },

    { h: 'Where the Map Is Wrong',
      hint: 'Rubric: where the map is wrong and why, and what data would fix it (2 points). What the terrain-only model leaves out (snowpack, weather, wind loading, triggering, slope shape, ground cover, terrain traps), what a bare-earth 10 m DEM cannot show, and what Table 1 assumes — name each and the data that would fix it.' },

    { h: 'Maps', pageBreakBefore: true,
      hint: 'Both maps are full-page, 8.5 × 11. Put each on its own page. Use the danger-scale colors on both, so a reader can compare them.',
      figures: [
        { caption: 'Map 1. Baseline — the geometric mean at shift 0.', pageBreakAfter: true,
          hint: 'Must carry: title stating the rule and the elevation bands; neat line, north arrow and scale bar; a text box with author, date, map projection, and the DEM’s source and date; the hazard classes in the danger-scale colors, labeled Low to Extreme in a legend; the Snowbird boundary and labeled places; an inset locating Little Cottonwood Canyon; basemap, scale and legibility appropriate to the ski area.' },
        { caption: 'Map 2. Scenario — a different shift or rule from Step 9.',
          hint: 'Everything Map 1 needs except the inset, plus: the title and text box say what changed from Map 1 and why this run was chosen.' },
      ] },

    { h: 'References', pageBreakBefore: true,
      hint: 'Rubric: sources credited (part of the point for organized writing). Credit the DEM, the ski-area layer, the advisory behind Table 1, the basemap and anything else you relied on.' },
    { h: 'AI Use Statement',
      hint: 'Course policy: one line saying what you used AI for. If you used none, say that. Expressions, class breaks, coordinate systems and areas come from your own work, never from a model.' },
    { h: 'Self-Graded Rubric', pageBreakBefore: true, rubric: true,
      hint: 'Rubric: this rubric pasted in with your self-assessment in every row (part of the point for organized writing). Put a score in every row, honestly arrived at. The grader compares yours with theirs.' },
  ],
},

'08': {
  labTitle: 'Lab 8: Big Southern Butte',
  labSubtitle: 'Measuring the volume of a volcanic dome by rebuilding the plain beneath it',
  sections: [
    { h: 'Requirements and Approach',
      hint: 'Rubric: the requirements of the project and your approach to solving it, in your own words (2 points). Two or three paragraphs. Say what you set out to measure and how you went about it — not a retelling of the step-by-step. If you built the model without the step-by-step instructions, say so here.' },

    { h: 'The DEM and Its Metadata',
      hint: 'Rubric: the three metadata values for the DEM and what each means for your result (2 points). Confirm them yourself from READ-ME-FIRST.txt, the raster’s properties and the two tiles’ metadata files — do not copy them from Figure A.',
      table: { caption: 'Table 1. Metadata for the DEM.',
               head: ['Metadata value', 'What you found', 'What it means for your result'],
               rows: [['Publication date and source dates', '', ''], ['Vertical datum and units', '', ''], ['Cell size', '', '']],
               widths: [2600, 2400, 4360] } },

    { h: 'The Model',
      hint: 'Rubric: a description a reader could repeat from — each tool, its settings, and every input, intermediate and output dataset with its type (2 points). Fill one row per tool, in the order they run.',
      table: { caption: 'Table 2. Model description — one row per tool.',
               head: ['Tool', 'Settings', 'Input dataset(s)', 'Output dataset', 'Type'],
               rows: [['Project Raster', '', '', '', ''], ['Buffer', '', '', '', ''], ['Create Random Points', '', '', '', ''],
                      ['Extract Values to Points', '', '', '', ''], ['Erase', '', '', '', ''], ['IDW', '', '', '', ''],
                      ['Extract by Mask (DEM)', '', '', '', ''], ['Extract by Mask (plain)', '', '', '', ''],
                      ['Raster Calculator (height)', '', '', '', ''], ['Raster Calculator (volume)', '', '', '', ''],
                      ['Zonal Statistics', '', '', '', '']],
               widths: [2300, 2100, 2000, 1700, 1260] },
      figures: [
        { caption: 'Figure 1. The complete model, exported from ModelBuilder with Export ▸ Export To Graphic.',
          hint: 'Rubric: a full-page model figure exported from ModelBuilder, all tools and datasets readable (2 points). Export it; do not screen-capture it.' },
        { caption: 'Figure 2. The model’s tool dialog, with the outline and the number of points exposed.', size: 'medium',
          hint: 'Rubric: a screen capture of the tool dialog with the outline and the number of points exposed as parameters (2 points).' },
      ] },

    { h: 'Check Values',
      hint: 'Rubric: your check values from Steps 4 to 8 (2 points), and the model’s baseline volume matching the check value (part of the 4 points for a working model). Use the random seed of Step 0.',
      table: { caption: 'Table 3. Baseline check values (IDW, 1,000 points, seed 1, reference outline).',
               head: ['Points kept after Erase', 'Tallest cell (m)', 'Mean height (m)', 'Volume (km³)'],
               rows: [['', '', '', '']],
               widths: [2340, 2340, 2340, 2340] } },

    { h: 'Testing the Assumptions', pageBreakBefore: true,
      hint: 'Rubric: one table with the baseline and the four Step 9 runs, with the points kept, the outline area, the volume, the tallest cell and the cells below the plain (4 points). Step 9 says where to read each value.',
      table: { caption: 'Table 4. Sensitivity — the baseline and the four Step 9 runs.',
               head: ['Run', 'What changed', 'Points kept', 'Outline area (km²)', 'Volume (km³)', 'Tallest cell (m)', 'Cells below the plain'],
               rows: [['Baseline', 'Nothing', '', '', '', '', ''], ['250 points', '', '', '', '', '', ''], ['4,000 points', '', '', '', '', '', ''],
                      ['Your own outline', '', '', '', '', '', ''], ['Spline', '', '', '', '', '', '']],
               widths: [1250, 1600, 1100, 1350, 1250, 1300, 1510] },
      questions: [
        'Which choice moves the volume most, and which least? Rank them with your numbers. (3 points)',
        'What did the spline do that IDW cannot? Map its cells below the plain and explain them with what you learned about the methods in Week 8. (3 points)',
      ] },

    { h: 'What the Volume Measures',
      hint: 'Rubric: what the volume measures and what the model cannot see (2 points). Step 9, question 3: is it the volume of the lava dome? Say what part of the dome the model cannot see, and what data would let you measure it.' },

    { h: 'Maps', pageBreakBefore: true,
      hint: 'Both maps are full-page, 8.5 × 11. Put each on its own page. Use the same color scale for height on both, so a reader can compare them.',
      figures: [
        { caption: 'Map 1. Baseline — height above the plain, IDW, reference outline.', pageBreakAfter: true,
          hint: 'Must carry: title with the volume in it or in a text box; neat line, north arrow and scale bar; a text box with author, date, map projection, and the DEM’s source and date; height above the plain in a clear color scale with a legend in meters; the outline over a hillshade or imagery; an inset locating the butte in Idaho; scale and legibility appropriate to the butte.' },
        { caption: 'Map 2. Scenario — your own outline or the spline, from Step 9.',
          hint: 'Everything Map 1 needs except the inset, with the same color scale, plus: the title and text box say what changed from Map 1 and by how much.' },
      ] },

    { h: 'References', pageBreakBefore: true,
      hint: 'Rubric: sources credited (part of the point for organized writing). Credit the DEM (both tiles), the reference outline, the USGS article, the basemap and anything else you relied on.' },
    { h: 'AI Use Statement',
      hint: 'Course policy: one line saying what you used AI for. If you used none, say that. Expressions, coordinate systems, volumes and counts come from your own work, never from a model.' },
    { h: 'Self-Graded Rubric', pageBreakBefore: true, rubric: true,
      hint: 'Rubric: this rubric pasted in with your self-assessment in every row (part of the point for organized writing). Put a score in every row, honestly arrived at. The grader compares yours with theirs.' },
  ],
},

'09': {
  labTitle: 'Lab 9: Interpolation Explorer',
  labSubtitle: 'Rebuilding a mountain from samples, three ways, and measuring how wrong each one is',
  sections: [
    { h: 'Requirements and Approach',
      hint: 'Rubric: the requirements of the project and your approach to solving it, in your own words (1 point). One or two paragraphs. Say what you set out to measure and how you went about it — not a retelling of the step-by-step. If you built the model without the step-by-step instructions, say so here.' },

    { h: 'The DEM, the Service and Their Metadata',
      hint: 'Rubric: the three metadata values for the DEM and what the service returned in Step 1, and what each means for your result (2 points). Confirm the values yourself from READ-ME-FIRST.txt, the raster’s properties and the tile’s metadata file — do not copy them from Figure A.',
      table: { caption: 'Table 1. Metadata for the DEM, and what the 3DEP image service returned.',
               head: ['Value', 'What you found', 'What it means for your result'],
               rows: [['Publication date and source dates', '', ''], ['Vertical datum and units', '', ''], ['Cell size', '', ''],
                      ['Service: spatial reference and cell size', '', ''], ['Service vs extract at the highest cell (m)', '', '']],
               widths: [2600, 2400, 4360] } },

    { h: 'The Model',
      hint: 'Rubric: a description a reader could repeat from — each tool, its settings, and every input, intermediate and output dataset with its type (2 points). Fill one row per tool, in the order they run; one row can cover a tool used once per method if the settings are the same.',
      table: { caption: 'Table 2. Model description — one row per tool.',
               head: ['Tool', 'Settings', 'Input dataset(s)', 'Output dataset', 'Type'],
               rows: [['Project Raster', '', '', '', ''], ['Extract by Mask', '', '', '', ''], ['Create Random Points', '', '', '', ''],
                      ['Extract Values to Points', '', '', '', ''], ['Create Thiessen Polygons', '', '', '', ''], ['Polygon to Raster', '', '', '', ''],
                      ['IDW', '', '', '', ''], ['Kriging', '', '', '', ''], ['Raster Calculator (error, ×3)', '', '', '', ''],
                      ['Raster Calculator (square, ×3)', '', '', '', ''], ['Zonal Statistics as Table (×3)', '', '', '', ''],
                      ['Calculate Field (×3)', '', '', '', '']],
               widths: [2300, 2100, 2000, 1700, 1260] },
      figures: [
        { caption: 'Figure 1. The complete model, exported from ModelBuilder with Export ▸ Export To Graphic.', size: 'landscape',
          hint: 'Rubric: a full-page model figure exported from ModelBuilder, all tools and datasets readable (2 points). Export it; do not screen-capture it. Upload your project’s toolbox (.atbx) with the report as well.' },
        { caption: 'Figure 2. The model’s tool dialog, with the number of points, the IDW power and the semivariogram exposed.', size: 'medium',
          hint: 'Rubric: a screen capture of the tool dialog with the number of points, the IDW power and the semivariogram exposed as parameters (2 points).' },
      ] },

    { h: 'Check Values',
      hint: 'Rubric: your check values from Steps 4 to 9 at seed 1 (2 points), and the three RMSEs matching the check values (part of the 4 points for a working model). These come from the course seed, 1, not your own.',
      table: { caption: 'Table 3. Check values at seed 1, 2,500 points, default parameters.',
               head: ['Value', 'Thiessen', 'IDW', 'Kriging'],
               rows: [['First point (E, N)', '', '', ''], ['Surface minimum and maximum (m)', '', '', ''],
                      ['Error minimum and maximum (m)', '', '', ''], ['Mean of squared error (m²)', '', '', ''], ['RMSE (m)', '', '', '']],
               widths: [3360, 2000, 2000, 2000] } },

    { h: 'Where the Methods Break',
      hint: 'Rubric: the largest error on your own baseline error maps, its coordinates and size, and why the ground there defeats the interpolators (3 points). Read the location and value from your own raster and include a cropped figure of that spot. A general paragraph about interpolation earns nothing here.',
      figures: [
        { caption: 'Figure 3. The largest error on my baseline error maps, close up.', size: 'medium',
          hint: 'A crop of your error map around the largest error, with its coordinates and value labeled.' },
      ] },

    { h: 'Testing the Choices', pageBreakBefore: true,
      hint: 'Rubric: one table with your seed, the baseline and the four Step 10 runs, the RMSE of all three methods in every row, and the three checkpoint RMSEs on the baseline row (4 points).',
      table: { caption: 'Table 4. Sensitivity at my seed: ______ (the last four digits of my BYU ID).',
               head: ['Run', 'What changed', 'Thiessen RMSE (m)', 'IDW RMSE (m)', 'Kriging RMSE (m)'],
               rows: [['Baseline', 'Nothing (2,500 points, power 2, spherical)', '', '', ''], ['Baseline, 200 checkpoints', 'RMSE at the checkpoints', '', '', ''],
                      ['250 points', '', '', '', ''], ['10,000 points', '', '', '', ''],
                      ['IDW power 1, Kriging exponential', '', '', '', ''], ['IDW power 3, Kriging Gaussian', '', '', '', '']],
               widths: [2200, 2560, 1540, 1500, 1560] },
      questions: [
        'Which method wins, and does the ranking survive? Rank the methods at each number of points, with your numbers. (2 points)',
        'Which parameter mattered, and which barely did? Compare the IDW power and the semivariogram model with the number of points. (2 points)',
        'Could you have known without the truth? Compare each checkpoint RMSE with the RMSE over all 67,337 cells. (2 points)',
      ] },

    { h: 'Maps', pageBreakBefore: true,
      hint: 'Both maps are full sheets; landscape is easiest. Use the same elevation scale and the same error scale and breaks on both, so a reader can compare them.',
      figures: [
        { caption: 'Map 1. Baseline comparison sheet at my seed — the true DEM, three surfaces and three error maps.', size: 'landscape', pageBreakAfter: true,
          hint: 'Must carry: title, neat line, north arrow and scale bar; a text box with author, date, map projection, the DEM’s source and date, and your seed; the true DEM with your sample points and the three surfaces on one elevation scale with a legend; the three error maps on one diverging scale with the same breaks, with a legend; every panel labeled with method, parameters and RMSE.' },
        { caption: 'Map 2. One Step 10 scenario — its three error maps on Map 1’s error scale.', size: 'landscape',
          hint: 'Must carry: the scenario’s three error maps on Map 1’s error scale with a legend and the true DEM for reference; every panel labeled with method, parameters and RMSE; title and text box saying what changed from Map 1 and by how much; plus the title, neat line, north arrow, scale bar and text box items of Map 1.' },
      ] },

    { h: 'References', pageBreakBefore: true,
      hint: 'Rubric: sources credited (part of the point for organized writing). Credit the DEM tile, the 3DEP image service, the textbook chapter and anything else you relied on.' },
    { h: 'AI Use Statement',
      hint: 'Course policy: one line saying what you used AI for. If you used none, say that. Expressions, coordinate systems, RMSEs and coordinates come from your own work, never from a model.' },
    { h: 'Self-Graded Rubric', pageBreakBefore: true, rubric: true,
      hint: 'Rubric: this rubric pasted in with your self-assessment in every row (part of the point for organized writing). Put a score in every row, honestly arrived at. The grader compares yours with theirs.' },
  ],
},

'04': {
  labTitle: 'Lab 4: Cell Phone Tower Placement',
  labSubtitle: '',
  sections: [
    { h: 'Requirements and Approach',
      hint: 'Rubric: the requirements of the project and your approach to solving it, in your own words (2 points). Two or three paragraphs. Say what you were asked to produce and how you went about it — not a retelling of the step-by-step.' },

    { h: 'Data and Metadata',
      hint: 'Rubric: the three metadata values from Figure A and what each one means for your result (2 points). Confirm these yourself from READ-ME-FIRST.txt and the source item’s page — do not copy them from the figure.',
      table: { caption: 'Table 1. Metadata for the tower layer.',
               head: ['Metadata value', 'What you found', 'What it means for your result'],
               rows: [['Last update date', '', ''],
                      ['Licensing service the layer covers', '', ''],
                      ['Records sharing a location', '', '']],
               widths: [2700, 2400, 4260] } },

    { h: 'The Model',
      hint: 'Rubric: a description a reader could repeat from — each tool, its settings, and every input, intermediate and output dataset with its type (point, line, polygon, raster) and source (2 points). Fill one row per tool, in the order they run, and fill both the Type and the Source column.',
      table: { caption: 'Table 2. Model description — one row per tool.',
               head: ['Tool', 'Settings', 'Input dataset(s)', 'Output dataset', 'Type', 'Source'],
               rows: [['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', ''], ['', '', '', '', '', '']],
               widths: [1400, 2100, 2100, 1500, 1000, 1260] },
      figures: [
        { caption: 'Figure 1. The complete model, exported from ModelBuilder with Export ▸ Export To Graphic.',
          hint: 'Rubric: a full-page (8.5 × 11) figure of the model, exported from ModelBuilder — every tool and dataset shown, labels informative, all text readable at 10 pt or larger (2 points). Export it; do not screen-capture it.' },
        { caption: 'Figure 2. The model’s tool dialog, with the four parameters exposed.', size: 'medium',
          hint: 'Rubric: a screen capture of the tool dialog with the four parameters exposed (2 points) — road distance, search radius, maximum slope and maximum density.' },
      ] },

    { h: 'Your Recommended Site',
      hint: 'Rubric: your recommended site and why you chose it (2 points). Say where it is, and give the reasons in terms a carrier would care about — not just that the model returned it.' },

    { h: 'Candidate Zones You Do Not Believe',
      hint: 'Rubric: the candidate zones you do not believe, why, and what data would fix each problem (Step 13) (2 points). One row per zone. "The tower layer has no license site recorded nearby" is a data problem, not a terrain one — say which it is.',
      table: { caption: 'Table 3. Candidate zones you do not believe.',
               head: ['Zone (where it is)', 'Why you do not believe it', 'What data would fix it'],
               rows: [['', '', ''], ['', '', ''], ['', '', '']],
               widths: [2600, 3400, 3360] } },

    { h: 'Sensitivity Analysis', pageBreakBefore: true,
      hint: 'Rubric: one table with the baseline and at least three more runs, giving for each the four parameter values, the cells and area in km², the percentage of the county, and whether your recommended site is still suitable (4 points). Area is cells × 900 ÷ 1,000,000; the county is 5,545 km². The baseline row is part of the table. Change one number at a time from the baseline, so your table can answer the first question below.',
      table: { caption: 'Table 4. Sensitivity — the baseline and at least three more runs.',
               head: ['Run (what changed)', 'Slope (°)', 'Road (km)', 'Density', 'Radius (m)', 'Cells', 'Area (km²)', '% of county', 'Site still suitable?'],
               rows: [['Baseline', '5', '1', '20', '20000', '', '', '', ''],
                      ['', '', '', '', '', '', '', '', ''],
                      ['', '', '', '', '', '', '', '', ''],
                      ['', '', '', '', '', '', '', '', '']],
               widths: [1400, 700, 750, 800, 900, 1000, 1000, 950, 1860] },
      questions: [
        'Which number does your answer depend on most, and which least? Support it with your table, not an impression. (2 points)',
        'Does your recommended site survive every run? If not, which change removed it, and is it still your recommendation? (2 points)',
        'How much of what you see is the tower data rather than the terrain or the roads? What would a complete tower layer change, and what data would you want before a carrier spent money on your site? (2 points)',
      ] },

    { h: 'Maps', pageBreakBefore: true,
      hint: 'Both maps are full-page, 8.5 × 11. Put each on its own page. Symbolize the suitable areas the same way on both, so a reader can compare them.',
      figures: [
        { caption: 'Map 1. Baseline — Suitable_Sites at the criteria given.', pageBreakAfter: true,
          hint: 'Must carry: title, neat line, north arrow and scale bar; a text box with author, date, map projection and data sources; the suitable areas symbolized with a legend; the existing towers and the highways shown and symbolized; your recommended site marked and labeled, with an inset of it on imagery; a visible basemap at a sensible scale, all text legible in print.' },
        { caption: 'Map 2. Scenario — one run from Step 14.',
          hint: 'Everything Map 1 needs except the inset, plus: the title and text box say which number was changed, to what, and why you chose this run to show.' },
      ] },

    { h: 'References', pageBreakBefore: true,
      hint: 'Rubric: sources credited (part of the point for organized writing). Credit the tower layer, the elevation and road data, the basemap and anything else you relied on.' },
    { h: 'AI Use Statement',
      hint: 'Course policy: one line saying what you used AI for. If you used none, say that. Field names, expressions, coordinate systems and numbers come from your own data, never from a model.' },
    { h: 'Self-Graded Rubric', pageBreakBefore: true, rubric: true,
      hint: 'Rubric: this rubric pasted in with your self-assessment in every row (part of the point for organized writing). Put a score in every row, honestly arrived at. The grader compares yours with theirs.' },
  ],
},

'05': {
  labTitle: 'Lab 5: Watershed Delineation',
  labSubtitle: 'Extracting streams and watersheds from a DEM',
  sections: [
    { h: 'Requirements and Approach',
      hint: 'Rubric: the requirements of the project and your approach to solving it, in your own words (2 points). Two or three paragraphs. Say what you were asked to produce and how you went about it — not a retelling of the step-by-step.' },

    { h: 'Data and Metadata',
      hint: 'Rubric: the four metadata values from Figure A and what each one means for your result (2 points). Confirm the first three from READ-ME-FIRST.txt and the tile’s metadata file, and the fourth from UGRC’s page for the NHD layer — do not copy them from the figure.',
      table: { caption: 'Table 1. Metadata for the DEM and the NHD.',
               head: ['Metadata value', 'What you found', 'What it means for your result'],
               rows: [['DEM publication date', '', ''],
                      ['Range of source dates in the DEM', '', ''],
                      ['DEM vertical datum', '', ''],
                      ['NHD last update', '', '']],
               widths: [2700, 2400, 4260] } },

    { h: 'The Model',
      hint: 'Rubric: a description a reader could repeat from — each tool, its settings, and every input, intermediate and output dataset with its type (point, line, polygon, raster) and source (2 points). One row per tool, in the order they run; the tool names are filled in for you, starting with Project Raster (run once, outside the model). Fill both the Type and the Source column.',
      table: { caption: 'Table 2. Model description — one row per tool.',
               head: ['Tool', 'Settings', 'Input dataset(s)', 'Output dataset', 'Type', 'Source'],
               rows: [['Project Raster (once, outside the model)', '', '', '', '', ''],
                      ['Fill', '', '', '', '', ''],
                      ['Flow Direction', '', '', '', '', ''],
                      ['Flow Accumulation', '', '', '', '', ''],
                      ['Snap Pour Point', '', '', '', '', ''],
                      ['Watershed', '', '', '', '', ''],
                      ['Raster to Polygon', '', '', '', '', ''],
                      ['Raster Calculator', '', '', '', '', ''],
                      ['Stream Link', '', '', '', '', ''],
                      ['Stream to Feature', '', '', '', '', ''],
                      ['Watershed (2)', '', '', '', '', ''],
                      ['Raster to Polygon (2)', '', '', '', '', '']],
               widths: [1400, 2100, 2100, 1500, 1000, 1260] },
      figures: [
        { caption: 'Figure 1. The complete model, exported from ModelBuilder with Export ▸ Export To Graphic.',
          hint: 'Rubric: a full-page (8.5 × 11) figure of the model, exported from ModelBuilder and laid out so it reads in rows as Figure C does — every tool and dataset shown, labels informative, all text readable at 10 pt or larger (2 points). Export it; do not screen-capture it.' },
        { caption: 'Figure 2. The model’s tool dialog, with the threshold and the three outputs exposed as parameters.', size: 'medium',
          hint: 'Rubric: a screen capture of the tool dialog with the threshold and the three outputs exposed as parameters, like Figure 12b (2 points). Open it from the Catalog pane after you save the model.' },
      ] },

    { h: 'Checking the Result',
      hint: 'Rubric: the two checks from Step 13 — your basin area against StreamStats and your stream length against the NHD, with the numbers (2 points). Give both in the same units. Measure the NHD in UTM meters, not Web Mercator.',
      table: { caption: 'Table 3. Your model against two independent sources.',
               head: ['Check', 'Your model', 'Independent source', 'Difference'],
               rows: [['Basin area (km²)', '', 'StreamStats:', ''],
                      ['Total stream length (km)', '', 'NHD, all lines:', ''],
                      ['Perennial + intermittent length (km)', '—', 'NHD, FCode 46006 + 46003:', '—']],
               widths: [2800, 1800, 3000, 1760] } },

    { h: 'Where the Model Is Wrong',
      hint: 'Rubric: where the model is wrong, why, and what data would fix each problem (Step 13) (2 points). One row per problem. Start from the three places Step 13 names — the Provo bench, the NHD’s ephemeral lines, and culverts — or find your own.',
      table: { caption: 'Table 4. Where the model is wrong.',
               head: ['Where', 'Why it is wrong', 'What data would fix it'],
               rows: [['', '', ''], ['', '', ''], ['', '', '']],
               widths: [2600, 3400, 3360] } },

    { h: 'Sensitivity Analysis', pageBreakBefore: true,
      hint: 'Rubric: one table with the baseline and at least three more thresholds, giving for each the threshold in cells and km², the basin area, the segments, the subwatersheds, the stream length, the mean subwatershed area and the drainage density, with the NHD as a reference row (4 points). Contributing area is threshold × 100 ÷ 1,000,000 km². The baseline row is part of the table.',
      table: { caption: 'Table 5. Sensitivity — the baseline, at least three more thresholds, and the NHD.',
               head: ['Threshold (cells)', 'Contributing area (km²)', 'Basin area (km²)', 'Segments', 'Subwatersheds', 'Stream length (km)', 'Mean subwatershed (km²)', 'Drainage density (km/km²)'],
               rows: [['5,000 (baseline)', '0.5', '', '', '', '', '', ''],
                      ['', '', '', '', '', '', '', ''],
                      ['', '', '', '', '', '', '', ''],
                      ['', '', '', '', '', '', '', ''],
                      ['NHD (reference)', '—', '—', '—', '—', '', '—', '']],
               widths: [1400, 1150, 1050, 1000, 1150, 1150, 1260, 1200] },
      questions: [
        'How do the segment and subwatershed counts depend on the threshold? What happens to them when the threshold doubles, which range of thresholds gives 20–40 subwatersheds, and why are two of your columns always equal? (2 points)',
        'Which threshold reproduces the NHD’s total length, and which its perennial and intermittent length? What does that say about what the NHD’s lines represent, and about which network a runoff model should use? (2 points)',
        'What did the threshold not change, and which network would you defend to the engineer who asked for 20–40 subwatersheds? (2 points)',
      ] },

    { h: 'Maps', pageBreakBefore: true,
      hint: 'Both maps are full-page, 8.5 × 11. Put each on its own page. Symbolize the subwatersheds, your streams and the NHD the same way on both, so a reader can compare them.',
      figures: [
        { caption: 'Map 1. Baseline — subwatersheds and streams at 5,000 cells.', pageBreakAfter: true,
          hint: 'Must carry: title, neat line, north arrow and scale bar; a text box with author, date, map projection and data sources; subwatersheds and the basin boundary symbolized with a legend; your streams and the NHD streams, told apart; the outlet marked and a locator map; imagery or hillshade visible, zoomed to the basin, all text legible in print.' },
        { caption: 'Map 2. Scenario — one threshold from Step 14.',
          hint: 'The same as Map 1 (the locator is optional), plus: the title and text box say what threshold was used, what it replaced, and why you chose this run to show.' },
      ] },

    { h: 'References', pageBreakBefore: true,
      hint: 'Rubric: sources credited (part of the point for organized writing). Credit the DEM, the NHD, StreamStats, the basemap and anything else you relied on.' },
    { h: 'AI Use Statement',
      hint: 'Course policy: one line saying what you used AI for. If you used none, say that. Field names, expressions, coordinate systems and numbers come from your own data, never from a model.' },
    { h: 'Self-Graded Rubric', pageBreakBefore: true, rubric: true,
      hint: 'Rubric: this rubric pasted in with your self-assessment in every row (part of the point for organized writing). Put a score in every row, honestly arrived at. The grader compares yours with theirs.' },
  ],
},

};
// ─────────────────────────── end lab-specific content ───────────────────────────

const COURSE = 'CE 414 — Engineering Applications of GIS';
const TERM = 'Fall 2026 · Dr. Dan Ames';

const key = process.argv[2];
if (!LABS[key]) {
  console.error(`usage: node make_lab_report_template.js <lab>   (one of ${Object.keys(LABS).join(', ')})`);
  process.exit(1);
}
const LAB = LABS[key];
const README = path.join(REPO, 'docs', 'assignments', `lab-${key}`, 'README.md');
const OUTFILE = path.join(REPO, 'docs', 'assignments', `lab-${key}`, `lab${key}-report-template.docx`);

// Read the rubric straight out of the lab page so it cannot drift from what is graded.
function extractRubric(mdPath) {
  const src = fs.readFileSync(mdPath, 'utf8');
  const re = /^\| (\*\*.+?)\s*\|\s*(\/10|\*\*\/50\*\*|up to \+5)\s*\|$/gm;
  const out = [];
  let m;
  while ((m = re.exec(src)) !== null) {
    const body = m[1].replace(/^\*\*(.+?)\*\*/, (_, t) => `\u0000${t}\u0000`);
    const title = body.split('\u0000')[1];
    const rest = body.split('\u0000').slice(2).join('');
    const parts = rest.split('<br>').map((p) => p.trim()).filter(Boolean);
    out.push({
      title,
      lead: parts.length && !parts[0].startsWith('•') ? parts[0] : '',
      points: m[2].replace(/\*/g, ''),
      bullets: parts.filter((p) => p.startsWith('•')).map((p) => p.replace(/^•\s*/, '')),
    });
  }
  if (!out.length) throw new Error(`no rubric rows found in ${mdPath}`);
  return out;
}
const rubric = extractRubric(README);

const INK = '1F3864', GRAY = '767171', RULE = 'BFBFBF', HEADFILL = 'D9E2F3', ZEBRA = 'F2F2F2';
const CONTENT_W = 9360; // 6.5in at 1440 DXA/in
const LAND_W = 12960;   // 9in: the content width of a landscape Letter page with 1in margins

const clean = (s) => s.replace(/`/g, '').replace(/\*\*/g, '').replace(/\*/g, '');

const hint = (t) => new Paragraph({
  spacing: { before: 60, after: 160 },
  children: [new TextRun({ text: t, italics: true, color: GRAY, size: 19 })],
});

// Placeholders are highlighted yellow so one left behind is obvious on the page, to the student
// before they submit and to the grader after. (Lab 4, Fall 2026: a third of the reports kept one.)
const MARK = 'yellow';
const placeholder = (t = '[Add your content here.]') => new Paragraph({
  spacing: { before: 0, after: 260 },
  children: [new TextRun({ text: t, italics: true, color: GRAY, highlight: MARK })],
});

const caption = (t) => new Paragraph({
  style: 'Caption', spacing: { before: 100, after: 240 },
  children: [new TextRun({ text: t, bold: true, size: 19, color: INK })],
});

const DASH = { style: BorderStyle.DASHED, size: 6, color: RULE };
// tall = full portrait page; medium = screen capture; landscape = full page on a landscape page
// (9 in wide), used for the model figure so a wide model is not squeezed into an unreadable strip.
const DROP = { tall: [CONTENT_W, 8640], medium: [CONTENT_W, 4320], landscape: [LAND_W, 7500] };
const imageDrop = (size = 'tall') => {
  const [w, h] = DROP[size];
  return new Table({
    columnWidths: [w],
    width: { size: w, type: WidthType.DXA },
    borders: { top: DASH, bottom: DASH, left: DASH, right: DASH,
               insideHorizontal: DASH, insideVertical: DASH },
    rows: [new TableRow({
      cantSplit: true,
      height: { value: h, rule: HeightRule.ATLEAST },
      children: [new TableCell({
        width: { size: w, type: WidthType.DXA },
        verticalAlign: 'center',
        children: [new Paragraph({
          alignment: AlignmentType.CENTER, keepNext: true,
          children: [new TextRun({ text: '[ Insert image here — delete this box ]', italics: true, color: GRAY, size: 19, highlight: MARK })],
        })],
      })],
    })],
  });
};

function cell(children, { width, head = false, shade = null }) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: (head || shade) ? { type: ShadingType.CLEAR, fill: head ? HEADFILL : shade, color: 'auto' } : undefined,
    margins: { top: 90, bottom: 90, left: 120, right: 120 },
    children,
  });
}

function simpleTable({ head, rows, widths }) {
  const sum = widths.reduce((a, b) => a + b, 0);
  if (sum !== CONTENT_W) throw new Error(`column widths sum to ${sum}, must be ${CONTENT_W}`);
  const sz = head.length >= 8 ? 15 : 19;
  const headRow = new TableRow({
    tableHeader: true, cantSplit: true,
    children: head.map((h, i) => cell(
      [new Paragraph({ children: [new TextRun({ text: h, bold: true, size: sz, color: INK })] })],
      { width: widths[i], head: true })),
  });
  const bodyRows = rows.map((r, ri) => new TableRow({
    cantSplit: true,
    children: r.map((c, i) => cell(
      [new Paragraph({ children: [new TextRun({ text: c || ' ', size: sz, color: c ? '000000' : GRAY })] })],
      { width: widths[i], shade: ri % 2 ? ZEBRA : null })),
  }));
  return new Table({ columnWidths: widths, width: { size: CONTENT_W, type: WidthType.DXA }, rows: [headRow, ...bodyRows] });
}

function rubricTable() {
  const W = [7200, 900, 1260]; // = 9360
  // "Max" rather than "Points", and a printed "___ / 10" in the score cell: with "/10" in a column
  // headed Points, students wrote their score there or left Your score blank (Lab 4, Fall 2026).
  const rows = [new TableRow({
    tableHeader: true, cantSplit: true,
    children: ['Item', 'Max', 'Your score'].map((h, i) => cell(
      [new Paragraph({ children: [new TextRun({ text: h, bold: true, size: 19, color: INK })] })],
      { width: W[i], head: true })),
  })];

  for (const r of rubric) {
    const isTotal = r.title === 'Total';
    const itemParas = [new Paragraph({
      spacing: { after: r.bullets.length ? 60 : 0 },
      children: [new TextRun({ text: clean(r.title + (r.lead ? ' ' + r.lead : '')), bold: true, size: 19 })],
    })];
    for (const b of r.bullets) {
      itemParas.push(new Paragraph({
        numbering: { reference: 'rubric-bullets', level: 0 },
        spacing: { after: 40 },
        children: [new TextRun({ text: clean(b), size: 17 })],
      }));
    }
    const max = r.points.replace(/^\//, '');                       // "/10" -> "10", "up to +5" kept
    const blank = r.points.startsWith('/') ? `___ / ${max}` : '___';
    rows.push(new TableRow({
      cantSplit: true,
      children: [
        cell(itemParas, { width: W[0], shade: isTotal ? HEADFILL : null }),
        cell([new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: max, bold: isTotal, size: 19 })] })],
          { width: W[1], shade: isTotal ? HEADFILL : null }),
        cell([new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: blank, bold: isTotal, size: 19, highlight: MARK })] })],
          { width: W[2], shade: isTotal ? HEADFILL : null }),
      ],
    }));
  }
  return new Table({ columnWidths: W, width: { size: CONTENT_W, type: WidthType.DXA }, rows });
}

// ── title page ──
const titleLine = (t, run, spacing = {}) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing,
  children: [new TextRun({ text: t, ...run })],
});

const fillIn = (label, hintText) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 0, after: 120 },
  children: [
    new TextRun({ text: label + '  ', bold: true, size: 21, color: INK }),
    new TextRun({ text: hintText, italics: true, color: GRAY, size: 21, highlight: MARK }),
  ],
});

// Does this lab have a ModelBuilder figure? (Lab 3 is digitized by hand and has none.)
const hasModel = LAB.sections.some((s) => (s.figures || []).some((f) => /ModelBuilder/.test(f.caption)));

// A checklist at the very top, in its own yellow box the student deletes. Each line is a miss that
// cost points across Labs 1 to 4; none is a new requirement — they are rubric items and cleanup.
function checklistBox() {
  const items = [
    'Delete every yellow placeholder and every gray instruction line, and this box.',
    'Name your reviewer, add the sentence on what you changed, and paste their stamp image below.',
    ...(hasModel ? ['Figure 1 is the model exported from ModelBuilder (Export ▸ Export To Graphic, as PNG) — not a screen capture, and not redrawn or “enhanced” by AI.'] : []),
    'Every number in your tables and text comes from your own work in ArcGIS Pro.',
    'Put a score in every row of the Self-Graded Rubric, and the total.',
    'Save as PDF, then open the PDF and check that every figure and map came through readable.',
  ];
  const BOX = { style: BorderStyle.SINGLE, size: 8, color: 'BF9000' };
  const paras = [new Paragraph({
    spacing: { after: 80 },
    children: [new TextRun({ text: 'Before you submit — then delete this box', bold: true, size: 20, color: INK })],
  })];
  for (const t of items) {
    paras.push(new Paragraph({
      numbering: { reference: 'checklist', level: 0 }, spacing: { after: 40 },
      children: [new TextRun({ text: t, size: 19 })],
    }));
  }
  return new Table({
    columnWidths: [CONTENT_W], width: { size: CONTENT_W, type: WidthType.DXA },
    borders: { top: BOX, bottom: BOX, left: BOX, right: BOX, insideHorizontal: BOX, insideVertical: BOX },
    rows: [new TableRow({ cantSplit: true, children: [new TableCell({
      width: { size: CONTENT_W, type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: 'FFF2CC', color: 'auto' },
      margins: { top: 120, bottom: 120, left: 160, right: 160 },
      children: paras,
    })] })],
  });
}

// The document is a list of sections so the model figure can sit on its own landscape page.
const sections = [];
let body = [];
const newSection = (landscape = false) => {
  body = [];
  sections.push({ landscape, children: body });
};
newSection();

body.push(checklistBox());
body.push(new Paragraph({ spacing: { before: 900 } }));
body.push(titleLine(LAB.labTitle, { bold: true, size: 48, color: INK }, { after: LAB.labSubtitle ? 100 : 420 }));
if (LAB.labSubtitle) body.push(titleLine(LAB.labSubtitle, { size: 32, color: INK }, { after: 420 }));
body.push(titleLine(COURSE, { size: 24 }, { after: 60 }));
body.push(titleLine(TERM, { size: 24, color: GRAY }, { after: 600 }));
body.push(fillIn('Your name:', '[your name]'));
body.push(fillIn('Date submitted:', '[date]'));
body.push(fillIn('Peer reviewer:', '[reviewer’s name]'));
body.push(new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 60, after: 400 },
  children: [new TextRun({ text: '[One sentence on what you changed because of your reviewer’s feedback.]', italics: true, color: GRAY, size: 21, highlight: MARK })],
}));
body.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: '[ Paste your reviewer’s stamp image here ]', italics: true, color: GRAY, size: 19, highlight: MARK })],
}));
body.push(new Paragraph({ children: [new PageBreak()] }));

// Generic advice appended to every lab's hints, so it does not have to be repeated in LABS.
const MODEL_FIG_ADVICE = ' Insert the exported PNG file itself. Do not screen-capture it, redraw it, or run it through an AI “enhancer” — that changes what the figure shows. This page is landscape so a wide model stays readable.';
const AI_ADVICE = ' You do the work in ArcGIS Pro yourself: AI may not run it for you, put facts in your report you did not find, or redraw or “enhance” your figures (see the course AI policy).';

// ── sections ──
let sectionNo = 0;
for (const s of LAB.sections) {
  sectionNo += 1;
  if (s.pageBreakBefore && sectionNo > 1 && body.length) body.push(new Paragraph({ children: [new PageBreak()] }));
  body.push(new Paragraph({
    heading: HeadingLevel.HEADING_1, spacing: { before: 280, after: 80 },
    children: [new TextRun({ text: `${sectionNo}.  ${s.h}`, bold: true, size: 28, color: INK })],
  }));
  if (s.hint) body.push(hint(s.h === 'AI Use Statement' ? s.hint + AI_ADVICE : s.hint));
  if (s.rubric) { body.push(rubricTable()); continue; }
  if (!s.table && !s.figures && !s.questions) body.push(placeholder());
  for (const t of [s.table, s.table2].filter(Boolean)) {
    if (t === s.table) body.push(placeholder());
    body.push(simpleTable(t));
    body.push(caption(t.caption));
  }
  if (s.figures) {
    for (const f of s.figures) {
      const isModel = /ModelBuilder/.test(f.caption);
      if (isModel) newSection(true);                 // the model figure gets a landscape page
      const fh = isModel ? (f.hint || '').replace(/ Export it; do not screen-capture it\./, '') + MODEL_FIG_ADVICE : f.hint;
      if (fh) body.push(hint(fh));
      body.push(imageDrop(isModel ? 'landscape' : (f.size || 'tall')));
      body.push(caption(f.caption));
      if (isModel) newSection(false);               // and the report goes back to portrait
      else if (f.pageBreakAfter) body.push(new Paragraph({ children: [new PageBreak()] }));
    }
  }
  if (s.questions) {
    for (const q of s.questions) {
      body.push(new Paragraph({
        heading: HeadingLevel.HEADING_2, spacing: { before: 220, after: 60 },
        children: [new TextRun({ text: q, bold: true, size: 22, color: INK })],
      }));
      body.push(placeholder('[Your answer here.]'));
    }
  }
}

const doc = new Document({
  creator: COURSE,
  title: `${LAB.labTitle} report template`,
  description: 'Fillable lab report template. Replace every yellow placeholder and delete the gray instructions.',
  styles: {
    default: {
      document: { run: { font: 'Calibri', size: 22, color: '000000' }, paragraph: { spacing: { line: 276, after: 140 } } },
      heading1: { run: { font: 'Calibri', bold: true, size: 28, color: INK }, paragraph: { spacing: { before: 280, after: 80 } } },
      heading2: { run: { font: 'Calibri', bold: true, size: 22, color: INK }, paragraph: { spacing: { before: 220, after: 60 } } },
    },
    paragraphStyles: [
      { id: 'Caption', name: 'Caption', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: 'Calibri', size: 19, color: INK, bold: true },
        paragraph: { spacing: { before: 100, after: 240 }, alignment: AlignmentType.LEFT } },
    ],
  },
  numbering: {
    config: [{
      reference: 'rubric-bullets',
      levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
                 style: { paragraph: { indent: { left: 240, hanging: 160 } } } }],
    }, {
      reference: 'checklist',
      levels: [{ level: 0, format: LevelFormat.BULLET, text: '☐', alignment: AlignmentType.LEFT,
                 style: { paragraph: { indent: { left: 360, hanging: 280 } } } }],
    }],
  },
  sections: sections.filter((sec) => sec.children.length).map((sec) => ({
    properties: {
      page: {
        size: { width: 12240, height: 15840,
                orientation: sec.landscape ? PageOrientation.LANDSCAPE : PageOrientation.PORTRAIT },
        margin: { top: convertInchesToTwip(1), bottom: convertInchesToTwip(1),
                  left: convertInchesToTwip(1), right: convertInchesToTwip(1) },
      },
    },
    children: sec.children,
  })),
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUTFILE, buf);
  console.log(`wrote ${OUTFILE} (${buf.length} bytes, ${rubric.length} rubric rows)`);
});
