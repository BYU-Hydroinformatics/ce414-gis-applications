# Lab report template guide

What a CE 414 lab report template is, why each piece is there, and how to build the next one.

[`tools/lab-conversion-guide.md`](lab-conversion-guide.md) is the authority for the **lab page**.
This file is the authority for the **Word template students write into**. The two have to agree:
the template's sections are the lab page's Deliverables, in the order the rubric grades them.

Build them with [`tools/templates/make_lab_report_template.js`](templates/make_lab_report_template.js).

## 1. What the template is for

Students were pasting the rubric out of the web page into Word and Google Docs and losing the
table — merged cells, lost bullets, a wall of unformatted text. That is the surface problem. The
template fixes two deeper ones:

- **The rubric stops being something you paste at the end.** It becomes the shape of the document.
  A student who fills in every section has, by construction, submitted every graded item.
- **It removes the excuse for the recurring misses.** Across Labs 2 and 3 the same bullets went
  missing in report after report — the six metadata questions answered as prose instead of six
  answers, the accuracy claim with no distance, the check-feature column absent from the
  sensitivity table, no "where is my result wrong" section at all. Every one of those is a heading
  or a table column in the template now. You can still leave it blank, but you cannot not notice it.

It is a floor, not a ceiling. The best reports have always added things the template does not ask
for, and they should keep doing that.

## 2. Anatomy

In order. Anything marked *(generic)* is the same in every lab; the rest comes from the lab page.

### Title page *(generic)*

Lab title, subtitle, course line, term and instructor line. Then, centered and labeled:

- **Your name:** `[your name]`
- **Date submitted:** `[date]`
- **Peer reviewer:** `[reviewer's name]`
- one italic line: `[One sentence on what you changed because of your reviewer's feedback.]`
- `[ Peer-review stamp here ]`

That last pair exists because the peer-review bullet is worth a point in every lab and is the most
commonly half-done item in the set — students name a reviewer and never say what changed. Putting
the sentence on the title page as its own line makes the omission visible.

Then a page break. Nothing else shares the title page.

### Body sections

One `Heading 1` per deliverable, numbered `1.`, `2.`, `3.` … **in the order the rubric grades
them.** That ordering is the whole trick: the write-up row's bullets come first, then the model
row, then the maps, then sensitivity.

Each section carries, in this order:

1. **The rubric line, verbatim, with its point value**, as a gray italic hint under the heading.
   Not a paraphrase — the words the grader will read. Add one sentence of plain advice after it
   when there is a common way to get it wrong ("Export it; do not screen-capture it").
2. **A seeded structure** where the rubric asks for one — a table with the right column headings,
   a figure drop zone, or bold sub-headings for the numbered questions.
3. **`[Add your content here.]`** in gray italic, so an unfilled section is obvious at a glance.

### Tables

Seed the table, with the columns the rubric names, and leave the rows empty. This is where most of
the value is. Lab 2's sensitivity table exists because "threshold, cells in class 1, area" is a
three-point bullet and reports kept arriving with two of the three. Lab 3's would seed
`Transformation | Control points | Total RMS error | Error at check feature | What the sheet looks like`
for the same reason — the check-feature column was the single most-missed item in the set.

Give every table a bold `Caption`-styled line under it, numbered: `Table 1. …`. Numbered captions
are themselves a rubric bullet ("figures numbered and referred to in the text").

### Figure drop zones

A single-cell table with dashed borders and a real height, captioned. Two sizes:

- **tall** (8640 DXA ≈ 6 in) for full-page items — model figures, map layouts
- **medium** (4320 DXA ≈ 3 in) for screen captures and supporting figures

The box has a height so students paste into a space that is already the right shape, rather than
dropping a 2-inch thumbnail of a model diagram and calling it a full-page figure. The placeholder
text says `[ Insert image here — delete this box ]` because otherwise the box survives into the
submission.

Maps get `pageBreakAfter` so each lands on its own page.

### Self-graded rubric — always last

A three-column Word table:

| Column | Width (DXA) | Why |
| --- | ---: | --- |
| Item | 7200 | Row title in bold, then every bullet with its point value |
| Points | 900 | `/10`, `/50`, `up to +5` |
| Your score | 1260 | Empty. The student fills it |

Keep it to these three. An "evidence" or "where is this in your report" column is tempting — the
strongest self-assessments have volunteered one — but it is not a graded item, and section 3 says
not to invent requirements the rubric does not grade. A student who wants to cite a section number
in the score cell is free to.

Give the Item column most of the width. The bullets are long, and a narrow Item column wraps them
into a column of two- and three-word lines that is hard to read down.

Widths must sum to 9360 (6.5 in of content between 1-inch margins) and be set in `WidthType.DXA` on
both the table and every cell. Percentages break in Google Docs.

## 3. Rules that are easy to get wrong

- **The hints quote the rubric, including the point values in parentheses.** A student should be
  able to grade themselves from the template alone.
- **Never invent a requirement the rubric does not grade.** If a section would be nice but is worth
  nothing, leave it out; the template is a contract.
- **Bullets come from a `numbering` config**, never a literal `•`.
- **`cantSplit: true` on every table row**, and `tableHeader: true` on header rows so the header
  repeats when a long rubric table runs over a page.
- **`ShadingType.CLEAR`**, never `SOLID` — `SOLID` renders black.
- **US Letter:** `size: { width: 12240, height: 15840 }`. The docx default is A4.
- **Real Word styles.** `HeadingLevel.HEADING_1` / `HEADING_2` and a `Caption` paragraph style, so
  the Navigation pane, a table of contents and the Google Docs importer all work. Direct formatting
  on top of a real style is fine; a custom style with no `outlineLevel` is not.
- **American English, and "ArcGIS Pro" in full** — the same rules as the lab pages.
- **No `\n`.** Separate `Paragraph` elements.

## 4. Building the next one

The builder script keeps everything lab-specific in one `LAB` block at the top; the machinery below
it is generic. To make Lab 3's template:

1. Extract the rubric from the lab page rather than retyping it, so the template cannot drift from
   what is graded:

   ```bash
   python3 - <<'PY'
   import re, json
   src = open('docs/assignments/lab-03/README.md').read()
   rows = re.findall(r'^\| (\*\*.+?)\s*\|\s*(/10|\*\*/50\*\*|up to \+5)\s*\|$', src, re.M)
   out = []
   for item, pts in rows:
       m = re.match(r'\*\*(.+?)\*\*(.*)$', item, re.S)
       parts = [p.strip() for p in m.group(2).split('<br>') if p.strip()]
       out.append({'title': m.group(1),
                   'lead': parts[0] if parts and not parts[0].startswith('•') else '',
                   'points': pts,
                   'bullets': [re.sub(r'^•\s*', '', p) for p in parts if p.startswith('•')]})
   json.dump(out, open('/tmp/lab03_rubric.json', 'w'), indent=1)
   PY
   ```

2. Edit the `LAB` block: `outfile`, `labTitle`, `labSubtitle`, and the `sections` array. Point the
   script's `readFileSync` at the new rubric JSON.
3. Walk the lab page's **Deliverables** list top to bottom and make sure every bullet has a home in
   `sections`. That list and the template are the same document in two formats.
4. Build, render, and **look at it**:

   ```bash
   node tools/templates/make_lab_report_template.js
   soffice --headless --convert-to pdf docs/assignments/lab-NN/labNN-report-template.docx --outdir /tmp/tpl
   ```

   Then read the pages. Most template defects are visual — a rubric row split across a page break,
   a drop zone too short for what goes in it, a table whose columns do not sum.

5. Validate: the docx skill's `scripts/office/validate.py` should report `All validations PASSED!`.

## 5. Definition of done

- [ ] Every bullet in the lab page's Deliverables has a section, a table column, or a question
      sub-heading in the template
- [ ] Every rubric row's point values appear in the hint text of the section that earns them
- [ ] The rubric table's bullets are byte-identical to the lab page's — extracted, not retyped
- [ ] Column widths sum to 9360 and are set in DXA on both table and cells
- [ ] No rubric row splits across a page; the header row repeats
- [ ] Renders correctly through LibreOffice **and** imports into Google Docs with the rubric table
      intact
- [ ] `validate.py` passes
- [ ] The lab page links it from the Deliverables section
- [ ] The file lives at `docs/assignments/lab-NN/labNN-report-template.docx` so MkDocs serves it

## 6. Where things live

```
tools/lab-report-template-guide.md              this file
tools/templates/make_lab_report_template.js     the builder (LAB block at top, generic below)
docs/assignments/lab-NN/labNN-report-template.docx   the artifact MkDocs serves
```

`node_modules/` is git-ignored; run `npm install docx` inside `tools/templates/` once.

The `.docx` **is** committed. It is a source artifact students download, not built output like
`site/` or a deck's `.html`.
