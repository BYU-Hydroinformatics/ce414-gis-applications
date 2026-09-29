// Build a fillable Word lab-report template for a CE 414 lab.
// Everything lab-specific lives in the LAB block below; the builder underneath is generic.
// Usage:  node make_lab_report_template.js  (writes the .docx named in LAB.outfile)

const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, PageBreak,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, PageOrientation,
  LevelFormat, convertInchesToTwip, HeightRule,
} = require('docx');
const fs = require('fs');

// ───────────────────────────── lab-specific content ─────────────────────────────
const LAB = {
  outfile: '/Users/dan/Code/ce414-gis-applications/docs/assignments/lab-02/lab02-report-template.docx',
  labTitle: 'Lab 2: NDVI',
  labSubtitle: 'Classifying Land Based on NDVI',
  course: 'CE 414 — Engineering Applications of GIS',
  term: 'Fall 2026 · Dr. Dan Ames',

  // Sections, in the order the rubric grades them. `hint` is the rubric line for that section.
  // `tables` and `figures` seed the structures the strongest reports all had.
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
        { caption: 'Figure 2. The model’s toolbox interface, with the threshold exposed as a parameter.',
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
        { caption: 'Map 1. Baseline — the classified NDVI at the threshold you chose and defended.',
          hint: 'Must carry: title stating the threshold; neat line, north arrow, scale bar; a text box with author, date, map projection, and the satellite, scene and acquisition date; the classified raster symbolized with a legend; the county polygon and a few labeled cities; an inset of the center-pivot area; a visible basemap at a sensible scale, all text legible in print.',
          pageBreakAfter: true },
        { caption: 'Map 2. Scenario — the same model at a different threshold from Step 6.',
          hint: 'Everything Map 1 needs except the inset, plus: the title and text box say what the threshold was changed to and why you chose this run to show.' },
      ] },

    { h: 'References', pageBreakBefore: true,
      hint: 'Rubric: sources credited (part of the 2 points for organized writing). Credit the data, the basemap and anything you quoted or relied on.' },

    { h: 'AI Use Statement',
      hint: 'Course policy: one line saying what you used AI for. If you used none, say that. Field names, expressions, coordinate systems and numbers come from your own data, never from a model.' },

    { h: 'Extra Credit \u2014 the Magic Valley Extract (optional)', pageBreakBefore: true,
      hint: 'Optional, up to +5. Delete this whole section if you are not attempting it. See Going further in the Data section of the lab: report the cells and area of class 1, the NDVI you read at a pivot and at ground you can verify is not irrigated, a map or figure, and a paragraph on whether your threshold transfers.',
      figures: [{ caption: 'Figure 3. The Magic Valley result at your chosen threshold.', size: 'medium' }] },

    { h: 'Self-Graded Rubric', pageBreakBefore: true,
      hint: 'Rubric: this rubric pasted in with your self-assessment in every row (part of the 2 points for organized writing). Put a score in every row and a short note saying where in your report the evidence is. Honest beats optimistic — the grader compares.',
      rubric: true },
  ],

};
// ─────────────────────────── end lab-specific content ───────────────────────────

const rubric = JSON.parse(fs.readFileSync('/tmp/lab02_rubric.json', 'utf8'));

const INK = '1F3864', GRAY = '767171', RULE = 'BFBFBF', HEADFILL = 'D9E2F3', ZEBRA = 'F2F2F2';
const CONTENT_W = 9360; // 6.5in at 1440 DXA/in

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
        children: [new TextRun({ text: '[ Insert image here \u2014 delete this box ]', italics: true, color: GRAY, size: 19 })],
      })],
    })],
  })],
});

function cell(children, { width, head = false, shade = null, span = 1 }) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    columnSpan: span,
    shading: (head || shade) ? { type: ShadingType.CLEAR, fill: head ? HEADFILL : shade, color: 'auto' } : undefined,
    margins: { top: 90, bottom: 90, left: 120, right: 120 },
    children,
  });
}

function simpleTable({ head, rows, widths }) {
  const headRow = new TableRow({
    tableHeader: true, cantSplit: true,
    children: head.map((h, i) => cell(
      [new Paragraph({ children: [new TextRun({ text: h, bold: true, size: 19, color: INK })] })],
      { width: widths[i], head: true })),
  });
  const bodyRows = rows.map((r, ri) => new TableRow({
    cantSplit: true,
    children: r.map((c, i) => cell(
      [new Paragraph({ children: [new TextRun({ text: c || ' ', size: 19, color: c ? '000000' : GRAY })] })],
      { width: widths[i], shade: ri % 2 ? ZEBRA : null })),
  }));
  return new Table({
    columnWidths: widths,
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    rows: [headRow, ...bodyRows],
  });
}

function rubricTable() {
  const W = [7200, 900, 1260]; // = 9360
  const head = new TableRow({
    tableHeader: true, cantSplit: true,
    children: ['Item', 'Points', 'Your score']
      .map((h, i) => cell([new Paragraph({ children: [new TextRun({ text: h, bold: true, size: 19, color: INK })] })],
        { width: W[i], head: true })),
  });

  const rows = [head];
  for (const r of rubric) {
    const isTotal = r.title === 'Total';
    const itemParas = [new Paragraph({
      spacing: { after: r.bullets.length ? 60 : 0 },
      children: [new TextRun({ text: r.title + (r.lead ? ' ' + r.lead.replace(/\*/g, '') : ''), bold: true, size: 19 })],
    })];
    for (const b of r.bullets) {
      itemParas.push(new Paragraph({
        numbering: { reference: 'rubric-bullets', level: 0 },
        spacing: { after: 40 },
        children: [new TextRun({ text: b.replace(/\*/g, ''), size: 17 })],
      }));
    }
    const pts = r.points.replace(/\*/g, '');
    rows.push(new TableRow({
      cantSplit: true,
      children: [
        cell(itemParas, { width: W[0], shade: isTotal ? HEADFILL : null }),
        cell([new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: pts, bold: isTotal, size: 19 })] })],
          { width: W[1], shade: isTotal ? HEADFILL : null }),
        cell([new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: ' ', size: 19 })] })],
          { width: W[2], shade: isTotal ? HEADFILL : null }),
      ],
    }));
  }
  return new Table({ columnWidths: W, width: { size: CONTENT_W, type: WidthType.DXA }, rows });
}

// ── title page ──
const titleLine = (t, opts) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: opts.spacing || {},
  children: [new TextRun({ text: t, ...opts.run })],
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
body.push(titleLine(LAB.labTitle, { run: { bold: true, size: 52, color: INK }, spacing: { after: 100 } }));
body.push(titleLine(LAB.labSubtitle, { run: { size: 32, color: INK }, spacing: { after: 420 } }));
body.push(titleLine(LAB.course, { run: { size: 24 }, spacing: { after: 60 } }));
body.push(titleLine(LAB.term, { run: { size: 24, color: GRAY }, spacing: { after: 700 } }));

body.push(fillIn('Your name:', '[your name]'));
body.push(fillIn('Date submitted:', '[date]'));
body.push(fillIn('Peer reviewer:', '[reviewer’s name]'));
body.push(new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 60, after: 500 },
  children: [new TextRun({
    text: '[One sentence on what you changed because of your reviewer’s feedback.]',
    italics: true, color: GRAY, size: 21 })],
}));
body.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: '[ Peer-review stamp here ]', italics: true, color: GRAY, size: 19 })],
}));
body.push(new Paragraph({ children: [new PageBreak()] }));

// ── sections ──
let sectionNo = 0;
function emitSection(s) {
  sectionNo += 1;
  if (s.pageBreakBefore && sectionNo > 1) body.push(new Paragraph({ children: [new PageBreak()] }));
  body.push(new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 280, after: 80 },
    children: [new TextRun({ text: `${sectionNo}.  ${s.h}`, bold: true, size: 28, color: INK })],
  }));
  if (s.hint) body.push(hint(s.hint));
  if (s.rubric) { body.push(rubricTable()); return; }
  if (!s.table && !s.figures && !s.questions) body.push(placeholder());
  if (s.table) {
    body.push(placeholder());
    body.push(simpleTable(s.table));
    body.push(caption(s.table.caption));
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
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 220, after: 60 },
        children: [new TextRun({ text: q, bold: true, size: 22, color: INK })],
      }));
      body.push(placeholder('[Your answer here.]'));
    }
  }
}

LAB.sections.forEach(emitSection);

const doc = new Document({
  creator: 'CE 414 — Engineering Applications of GIS',
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
  fs.writeFileSync(LAB.outfile, buf);
  console.log('wrote', LAB.outfile, buf.length, 'bytes');
});
