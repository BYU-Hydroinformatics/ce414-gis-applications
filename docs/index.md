# CE 414 — Engineering Applications of GIS

Welcome to the course site for **Civil Engineering 414 (Engineering Applications of GIS)**,
Civil and Construction Engineering, Brigham Young University.

Dr. Dan Ames · 430N EB · [dan.ames@byu.edu](mailto:dan.ames@byu.edu) · office hours by
appointment at [calendly.com/dan-ames/office-hours](https://calendly.com/dan-ames/office-hours)

Fall 2026, Section 001: Tuesdays and Thursdays, 8:00 to 9:15 am, in 234 CB. The 2:00 to 2:50 pm
period on those days is an open lab reserved for this class, where you work on your lab assignment
individually at the lab computers. Your BYU ID card opens the lab door; if it does not, check with
the CCE office.

## Description

An applications course in geographic information systems for civil and environmental engineers.
Students build reproducible spatial models to answer siting, routing, terrain, and hydrologic
questions, and learn to state the assumptions and limitations that come with them.

CE 414 picks up where an introductory GIS course leaves off. Instead of learning what a GIS *is*,
you build and defend spatial models that answer real engineering questions: where should this
facility go, which route costs least, how much of this watershed drains to that point, and how
confident should anyone be in the answer. The course uses **ArcGIS Pro**, with **ModelBuilder** as
the backbone — every lab is a reproducible model, not a sequence of clicks.

## Prerequisites

- CCE 114 Geomatics
- CCE 270 Computational Methods

## Textbook

*GIS Fundamentals*, 7th edition, by Paul Bolstad. The access card is required: every week has an
open-book reading quiz on the assigned chapter, listed on the [Schedule](schedule/README.md) and on
each week's page.

## Software

**ArcGIS Pro** (Advanced license, with the Spatial Analyst extension) is used throughout.
It is available in the department computer lab and through BYU's Citrix virtual desktop.

> [!IMPORTANT]
> Record the ArcGIS Pro version each lab was tested against. Tool names, parameters, and default
> behaviors change between releases, and a lab that silently assumes an older version is the most
> common source of student confusion in this course.

## Learning Outcomes

The official outcomes, from the Learning Suite syllabus:

1. **Synthesis and integration.** Integrate topics from various civil engineering disciplines to solve realistic problems.
2. **Database management.** Obtain and evaluate appropriate input information from databases, handbooks, correlation, experiments, and literature.
3. **Locating geographic data.** Know where to locate, and how to prepare, geographic datasets for use in a GIS.
4. **GIS spatial analysis.** Use GIS tools and scripts for spatial analysis, understanding, and design of engineering systems.
5. **Map generation.** Produce professional maps and technical reports from geographic data for use in written and oral presentations.
6. **GIS customization.** Customize, or use customized scripts to solve engineering-specific problems with GIS.
7. **Professional communication.** Compose professional documents in a clear, concise, and effective manner.

In practice that means that by the end of the course you can frame an engineering question as a
spatial analysis with explicit criteria, find and document authoritative data, choose a coordinate
system on purpose, build a parameterized ModelBuilder workflow and rerun it somewhere new, apply
raster and vector analysis, test your result's sensitivity to its assumptions, and communicate a
recommendation through a professional map and a concise report.

## How the course runs

- Two 75-minute class meetings a week, mixing lecture, discussion, and short in-class activities
  that are uploaded to Learning Suite by 9:30 am the same day, plus an open lab period each
  afternoon of class for individual lab work.
- A **reading quiz** and a **lab** almost every week, both due **Saturday at 11:59 pm**.
- Two closed-book **midterms** in the Testing Center, a hands-on **final exam** in ArcGIS Pro, and
  a team **final project** presented in the last two weeks.
- **Peer review.** You will review and stamp at least ten classmates' lab reports over the
  semester; make your engineering stamp in the first week.

## What every lab expects

There are eleven lab assignments plus a final project. Each lab is a complete spatial analysis: you
receive an engineering question and a set of criteria, and you produce a reproducible model, a map,
and a short written defense of your recommendation. Regardless of the topic, each one is graded on
the same underlying things:

- **A reproducible model.** A fresh run from the supplied inputs should complete without you
  repairing paths, field names, SQL, or units.
- **Correct fields, units, and coordinate system.** Set a projected coordinate system before any
  tool that measures distance or area.
- **Data provenance.** Where the data came from, when, and under what license.
- **Validation.** Evidence that the answer is plausible — counts, comparisons, or a sensitivity test.
- **Cartography.** A map a client could read: legible type, sensible symbology, scale, north arrow,
  and enough context to locate the study area.
- **Honest limitations.** What the analysis does *not* prove.

The [ArcGIS Tips and Reminders](arcgis-tips.md) page collects the settings and habits that save the
most time across all of them.

## Where everything lives

Each week has its own page, and everything for that week is on it: the Tuesday and Thursday lecture
slides, the reading and quiz, the in-class activities, and the lab that is due. Start from the
[Schedule](schedule/README.md) or pick a week in the sidebar. On any deck, press <kbd>F</kbd> for
fullscreen and <kbd>P</kbd> for presenter view with speaker notes.

The lab handouts are linked from the week each lab is due. The
[Final Project](assignments/final-project.md) is linked from Weeks 12 through 15.

> [!NOTE]
> This site was built out in September 2026. The lab handouts and lecture decks are all here, each
> still carrying instructor review notes from the conversion. See the
> [roadmap](https://github.com/BYU-Hydroinformatics/ce414-gis-applications/blob/main/ROADMAP.md)
> for what has moved and what has not.
