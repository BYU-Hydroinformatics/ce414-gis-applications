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
      hint: 'Rubric: a description a reader could repeat from — each tool, its settings, and every input, intermediate and output dataset with its type; for each input, the satellite and band, acquisition date, cloud cover and source (2 points). Fill one row per tool, in the order they run.',
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
      hint: 'Rubric: a description a reader could repeat from — each tool, its settings, and every input, intermediate and output dataset with its type (point, line, polygon, raster) and source (2 points). Fill one row per tool, in the order they run.',
      table: { caption: 'Table 2. Model description — one row per tool.',
               head: ['Tool', 'Settings', 'Input dataset(s)', 'Output dataset', 'Type and source'],
               rows: [['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', '']],
               widths: [1500, 2300, 2300, 1700, 1560] },
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
      hint: 'Rubric: one table with the baseline and at least three more runs, giving for each the four parameter values, the cells and area in km², the percentage of the county, and whether your recommended site is still suitable (4 points). Area is cells × 900 ÷ 1,000,000; the county is 5,545 km². The baseline row is part of the table.',
      table: { caption: 'Table 4. Sensitivity — the baseline and at least three more runs.',
               head: ['Run name', 'Slope (°)', 'Road (km)', 'Density', 'Radius (m)', 'Cells', 'Area (km²)', '% of county', 'Site still suitable?'],
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

const clean = (s) => s.replace(/`/g, '').replace(/\*\*/g, '').replace(/\*/g, '');

const hint = (t) => new Paragraph({
  spacing: { before: 60, after: 160 },
  children: [new TextRun({ text: t, italics: true, color: GRAY, size: 19 })],
});

const placeholder = (t = '[Add your content here.]') => new Paragraph({
  spacing: { before: 0, after: 260 },
  children: [new TextRun({ text: t, italics: true, color: GRAY })],
});

const caption = (t) => new Paragraph({
  style: 'Caption', spacing: { before: 100, after: 240 },
  children: [new TextRun({ text: t, bold: true, size: 19, color: INK })],
});

const DASH = { style: BorderStyle.DASHED, size: 6, color: RULE };
const imageDrop = (size = 'tall') => new Table({
  columnWidths: [CONTENT_W],
  width: { size: CONTENT_W, type: WidthType.DXA },
  borders: { top: DASH, bottom: DASH, left: DASH, right: DASH,
             insideHorizontal: DASH, insideVertical: DASH },
  rows: [new TableRow({
    cantSplit: true,
    height: { value: size === 'tall' ? 8640 : 4320, rule: HeightRule.ATLEAST },
    children: [new TableCell({
      width: { size: CONTENT_W, type: WidthType.DXA },
      verticalAlign: 'center',
      children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: '[ Insert image here — delete this box ]', italics: true, color: GRAY, size: 19 })],
      })],
    })],
  })],
});

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
  const rows = [new TableRow({
    tableHeader: true, cantSplit: true,
    children: ['Item', 'Points', 'Your score'].map((h, i) => cell(
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
    rows.push(new TableRow({
      cantSplit: true,
      children: [
        cell(itemParas, { width: W[0], shade: isTotal ? HEADFILL : null }),
        cell([new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: r.points, bold: isTotal, size: 19 })] })],
          { width: W[1], shade: isTotal ? HEADFILL : null }),
        cell([new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: ' ', size: 19 })] })],
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
    new TextRun({ text: hintText, italics: true, color: GRAY, size: 21 }),
  ],
});

const body = [];
body.push(new Paragraph({ spacing: { before: 2200 } }));
body.push(titleLine(LAB.labTitle, { bold: true, size: 48, color: INK }, { after: LAB.labSubtitle ? 100 : 420 }));
if (LAB.labSubtitle) body.push(titleLine(LAB.labSubtitle, { size: 32, color: INK }, { after: 420 }));
body.push(titleLine(COURSE, { size: 24 }, { after: 60 }));
body.push(titleLine(TERM, { size: 24, color: GRAY }, { after: 700 }));
body.push(fillIn('Your name:', '[your name]'));
body.push(fillIn('Date submitted:', '[date]'));
body.push(fillIn('Peer reviewer:', '[reviewer’s name]'));
body.push(new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 60, after: 500 },
  children: [new TextRun({ text: '[One sentence on what you changed because of your reviewer’s feedback.]', italics: true, color: GRAY, size: 21 })],
}));
body.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: '[ Peer-review stamp here ]', italics: true, color: GRAY, size: 19 })],
}));
body.push(new Paragraph({ children: [new PageBreak()] }));

// ── sections ──
let sectionNo = 0;
for (const s of LAB.sections) {
  sectionNo += 1;
  if (s.pageBreakBefore && sectionNo > 1) body.push(new Paragraph({ children: [new PageBreak()] }));
  body.push(new Paragraph({
    heading: HeadingLevel.HEADING_1, spacing: { before: 280, after: 80 },
    children: [new TextRun({ text: `${sectionNo}.  ${s.h}`, bold: true, size: 28, color: INK })],
  }));
  if (s.hint) body.push(hint(s.hint));
  if (s.rubric) { body.push(rubricTable()); continue; }
  if (!s.table && !s.figures && !s.questions) body.push(placeholder());
  for (const t of [s.table, s.table2].filter(Boolean)) {
    if (t === s.table) body.push(placeholder());
    body.push(simpleTable(t));
    body.push(caption(t.caption));
  }
  if (s.figures) {
    for (const f of s.figures) {
      if (f.hint) body.push(hint(f.hint));
      body.push(imageDrop(f.size || 'tall'));
      body.push(caption(f.caption));
      if (f.pageBreakAfter) body.push(new Paragraph({ children: [new PageBreak()] }));
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
  description: 'Fillable lab report template. Replace every gray italic prompt.',
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
    }],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840, orientation: PageOrientation.PORTRAIT },
        margin: { top: convertInchesToTwip(1), bottom: convertInchesToTwip(1),
                  left: convertInchesToTwip(1), right: convertInchesToTwip(1) },
      },
    },
    children: body,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUTFILE, buf);
  console.log(`wrote ${OUTFILE} (${buf.length} bytes, ${rubric.length} rubric rows)`);
});
