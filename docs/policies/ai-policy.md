# AI Use Policy

> [!IMPORTANT]
> **If you read nothing else, read this:**
>
> - **Use AI to learn.** Full, active, healthy use of AI is encouraged in this course — for
>   studying, for getting unstuck in ArcGIS Pro, and for making your writing clearer.
> - **Always disclose it.** Every time AI helps with something you turn in, say so, briefly and
>   specifically.
> - **Own your work.** You personally build the models and make the maps. Every field name, every
>   expression, every number, and every recommendation is yours to defend.
> - **AI is not permitted on the two midterms.** It is permitted on everything else, including the
>   final exam.

This course is about judgment: choosing criteria, choosing a coordinate system, deciding what a
result does and does not prove. AI is genuinely good at the parts around that judgment — recalling
a tool name, explaining why a raster came out integer, rewriting a clumsy paragraph. It is not good
at the judgment itself, and it is confidently wrong in exactly the places this course grades. So
use it, and use it openly.

## How to disclose

One line at the end of your submission is enough. For example:

> *AI disclosure: used Claude to work out why my Con expression returned all zeros, and to tighten
> the limitations paragraph.*

Specific beats long. If you did not use AI, you do not need to say anything. Disclosure is not a
penalty and it is never held against your grade. Undisclosed use of AI on work you present as your
own is an academic honesty problem under the university's
[Academic Honesty policy](university.md#academic-honesty), and it is the only part of this policy
with teeth.

## The one test that covers everything

**If you cannot explain and defend an answer as your own understanding, it is not your answer
yet.** Use AI until you pass that test, never to skip it. In this course the test is literal: your
lab report names the tools, the settings, and the datasets, and the rubric asks you to describe
your model so a reader could repeat it. A model you did not reason through is visible from the
outside.

## Two bright lines

These hold for every assignment in the course.

**Never present AI-generated output as something you produced in ArcGIS Pro.** A result, a map, a
screenshot, a table, an attribute count — if you say you made it in ArcGIS Pro, you made it in
ArcGIS Pro. Fabricated data is an integrity problem, not a style choice.

**Never take a field name, coded value, SQL expression, coordinate system, or check number from an
AI.** This is the failure mode that actually bites in this course. Ask a chatbot which attribute
holds road classification in a state roads layer and it will name one, with an example query, and
sound certain. It is guessing. Open the attribute table and look. If a lab hands you an expression
and your data does not support it, the lab is wrong and you should say so in your write-up — that
is a correct answer, not a broken one.

## By assignment category

### Labs

AI is a good assistant here. Use it to explain what a geoprocessing tool does, to debug an error
message, to work out why your output has the wrong extent or units, to talk through how to
structure a model, and to make your write-up read better.

You personally do the work in ArcGIS Pro: acquiring and inspecting the data, setting the
environments, building and running the model, and making the maps. The parts the rubric weights
most — the criteria you chose, the sensitivity analysis, and what you say the result does not
prove — should come out of your own head, and you should be able to defend them without notes.

Disclose in one line at the end of the report.

### Reading quizzes

Open book and done independently. Independently means without a classmate, not without a
reference. Use AI freely to clarify a confusing passage, to quiz yourself, or to have a concept
explained a different way. Make sure you actually understand it: the same concepts come back on the
midterms, where AI is not available.

> [!NOTE]
> The quizzes may be restructured this semester. If they change, this section changes with them and
> the change will be announced in class and on the week page.

### Midterms 1 and 2

**AI is not permitted.** These are closed-book, concept-based exams in the Testing Center. Prepare
with AI as much as you like beforehand — practice questions, concept review, having a topic
explained until it lands — but the exam itself is you.

### Final exam

**AI is permitted, and should be disclosed.** The final exam is one modeling question done in
ArcGIS Pro at a lab computer, open book and open computer. AI is a reference like any other
reference available to you there. It will not do the exam for you: the question is scored on the
model you build and the reasoning you attach to it, which is the part AI does worst. Include your
disclosure line in the PDF you upload.

### Final project

AI use is encouraged throughout — scoping the question, finding and evaluating data sources,
troubleshooting the processing, structuring the analysis, and writing the report. The project is
graded on your documented workflow and the decisions behind it, so make sure the analysis and the
reasoning are genuinely yours, and disclose how AI helped along the way.

The same rule applies to the presentation. Generated slides and generated images are fine if they
illustrate your work; a generated result is not.

### In-class activities

These are done live, on paper or in a spreadsheet, with your own numbers. The point is to compute
something by hand once so you know what the tool does when it does it for you. **Work the activity
yourself before you ask AI anything** — the numbers you upload must be numbers you produced.
Afterward, use AI freely to check your work or to understand what you just did.

### Peer review

Read your classmate's report yourself and write the feedback yourself. An AI-written review is
worse than no review: your classmate needs a reader who knows this course and did this lab. Use AI
to help you phrase a criticism kindly if you want to, but the judgment behind it must be yours.

The same goes for the notes you take on classmates' final presentations.

### Attendance and course evaluation

Not applicable.

## Tools and one caution

The free tiers of ChatGPT, Claude, and Gemini are more than enough for this course, and comparable
tools are fine. ArcGIS Pro's own AI assistant, where the lab machines have it enabled, is covered
by exactly the same rules as any other tool.

Do not paste classmates' names or personal information into an AI tool. This matters most for peer
review and for the final project, where you are working with a partner.

<!-- Drafted September 2026, adapted from the CCE 114 policy at
     https://byu-hydroinformatics.github.io/cce114-geomatics/policies/ai-policy/ and rewritten for
     CE 414: the categories are CE 414's (labs, reading quizzes, two midterms, an open-computer
     final exam in ArcGIS Pro, the final project, in-class activities, peer review), and the
     "never take a field name or expression from an AI" bright line is the CE 414 addition — it is
     the same hazard CLAUDE.md rule 3 guards against when writing the labs.

     DECIDED by the instructor, September 2026: AI is permitted on the final exam. The exam is
     open book and open computer, so a ban would be unenforceable and would only bind honest
     students; the question is scored on the model and its defense.

     TODO(instructor) before this is final:
     1. Confirm the midterm stance with the Testing Center's own rules.
     2. Decide whether any CE 414 assignment should be *designed* around AI the way CCE 114's
        Lab 3 (AI-generated error report) and Web Mapping experience are. There is no such
        assignment here yet. Lab 6 (Lake Depth Explorer) and the final project are the natural
        candidates.
     3. Settle whether ArcGIS Pro's AI assistant is actually enabled on the lab machines; the
        sentence above hedges because it has not been checked.
     4. Reconcile with the Learning Suite syllabus text. The university's Academic Honesty policy
        is now on docs/policies/university.md and is linked from the disclosure section above;
        nothing here contradicts it, but the Learning Suite syllabus does not yet carry this AI
        policy at all. -->
