# CE 414 — Engineering Applications of GIS

Course materials for **Civil Engineering 414 (Engineering Applications of GIS)** at Brigham Young
University, taught by Dr. Dan Ames.

**📖 Read the course site: https://byu-hydroinformatics.github.io/ce414-gis-applications/**

The site is built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) from the
Markdown in [`docs/`](docs/), with lecture slides built by [Marp](https://marp.app/) from
[`slides/`](slides/). Both redeploy automatically on every push to `main`.

This repository is the sibling of
[cce114-geomatics](https://github.com/BYU-Hydroinformatics/cce114-geomatics) and deliberately uses
the same stack, layout, and conventions. CCE 114 is the introductory course and uses QGIS;
CE 414 is the applications course and uses **ArcGIS Pro**.

| Where | What |
| --- | --- |
| [docs/assignments/](docs/assignments/) | Lab assignments 1–10, one folder per lab with its images |
| [docs/lectures/](docs/lectures/) | One page per lecture topic, linking to its slide deck |
| [docs/policies/](docs/policies/) | Grading, AI use, and university policies |
| [slides/](slides/) | Marp source for the web slide decks |
| [tools/](tools/) | Word → Markdown and PowerPoint → Marp conversion pipeline |
| [CLAUDE.md](CLAUDE.md) | **Start here** — what we are doing, the hard rules, how to build and check |
| [ROADMAP.md](ROADMAP.md) | Migration order, known content problems, and per-item definition of done |

## Status

🚧 **Scaffold only.** No lab or lecture content has been migrated yet. The source material still
lives in Word and PowerPoint in Dr. Ames's course folder. [ROADMAP.md](ROADMAP.md) says what moves
next and in what order.

## Working locally

```bash
pip install mkdocs-material mkdocs-github-admonitions-plugin
mkdocs serve
```

Slide decks build separately:

```bash
npx -y @marp-team/marp-cli@latest --no-stdin --theme slides/theme/ce414.css --html \
  slides/week-01/<slug>.md -o /tmp/check.html
```
