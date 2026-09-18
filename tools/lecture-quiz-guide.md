# Lecture quizzes

Every lecture deck ends with a slide carrying a QR code. A student scans it with a phone and
gets a short, self-marking quiz on what was just taught. Nothing is recorded and nothing is
graded — it is a two-minute check that the lecture landed, and a way to end class on a question
rather than on a list of deadlines.

This file is the authority for building one. It is the companion to
[`slide-conversion-guide.md`](slide-conversion-guide.md), which still governs everything else
about a deck.

## The pattern

A lecture quiz is three things:

| Artifact | Where | Who writes it |
| --- | --- | --- |
| The quiz page | `docs/quizzes/<slug>/index.html` | you, per lecture |
| The QR code PNG | `slides/week-NN/images/quiz-<slug>-qr.png` | `tools/make_quiz_qr.py`, never by hand |
| The closing slide | last slide of `slides/week-NN/<deck>.md` | you, per lecture |

The look, the phone layout, the scoring and the keyboard handling live in
`docs/quizzes/lib/quiz.css` and `docs/quizzes/lib/quiz.js`. **Do not edit those two files to
make one quiz behave differently, and do not copy them into a quiz page.** A quiz page holds
its questions and nothing else. `docs/quizzes/raster-types/index.html` is the reference
implementation; read it before writing a new one.

## The slug

The slug is the quiz directory name, the stem of the QR PNG, and the last segment of the URL a
student scans. It is registered in the `QUIZZES` table in `tools/make_quiz_qr.py`, which is what
generates the code — so the slug is decided there first, not invented in the quiz page.

Keep it short. A projected QR code is read from the back row of a lecture hall, and every
character adds modules: `/quizzes/raster-types/` encodes as a 37-module code where a
descriptive path needed 45.

## The quiz page

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CE 414 — <short title></title>
  <link rel="icon" type="image/png" href="../../assets/favicon.png">
  <meta name="theme-color" content="#2563eb">
  <meta name="description" content="<one sentence, for search and link previews>">
  <link rel="stylesheet" href="../lib/quiz.css">
</head>
<body>
<div class="container" id="quizRoot"></div>
<script src="../lib/quiz.js"></script>
<script>
CE414Quiz.start({
  title: "<short title, the same words as the slide>",
  subtitle: "CE 414 &middot; Week N &mdash; <deck title><br>" +
            "<one sentence saying what the student is deciding>",
  badge: "<2-3 words naming what each item is: 'Raster dataset', 'ModelBuilder element'>",
  deckUrl: "../../slides/week-NN/<deck>.html",
  questions: [ /* see below */ ],
  perfectNote:  "<one line for a perfect score>",
  goodNote:     "<one line for 70% and up>",
  tryAgainNote: "<one line below 70%, with the idea restated in a sentence>"
});
</script>
</body>
</html>
```

A question:

```js
{
  prompt: "The question, or the name of the thing being judged",
  detail: "Optional second line: the setup, the data, the scenario.",
  options: ["Two", "to", "four", "choices"],
  answer: "to",            // must match one option exactly, or be its 0-based index
  explanation: "Why that is the answer. One or two sentences."
}
```

- **Two options** render side by side; **three or four** stack. Any option longer than about
  22 characters stacks the whole set. You do not control this and should not try to.
- `answer` is checked against `options` at run time. A typo here is a quiz that marks a right
  answer wrong, and nothing will tell you — proof-read it.
- Options are shown in the order you write them. Do not put all the correct answers first.

### Two ways to fail without noticing

A quiz can be passable by a student who has learned nothing, and neither failure is visible while
you are writing it. `tools/check_quizzes.py` measures both and prints a note.

**The longest option is the answer.** A correct statement wants qualifying — *unless the tool is
told otherwise*, *in the version we use* — and a distractor does not, so the true option grows.
With four choices, chance puts the longest on the answer about a third of the time; the first
pass at this course's quizzes hit 55%, and one quiz managed 8 out of 8. Fix it by tightening the
correct answer, not by padding the distractors: a bloated distractor is its own tell, and some
correct answers should be the shortest thing on the screen. Keep every option in a question
within about 25% of its siblings, and under about 95 characters so four of them fit a phone.

**The answer is always in the same place.** Vary the index deliberately. Over eight questions use
at least three of the four positions, including index 0 and index 3 at least once each. If a
question has only three options, index 3 is unreachable — either give it a fourth or carry the
spread elsewhere in the quiz.

## Writing the questions

Six to eight questions. Fewer than six is not worth a QR code; more than eight and the room has
moved on.

The rules below are not style preferences. A quiz that teaches something false is worse than no
quiz, and a student has no way to tell the difference.

1. **Every question must be answerable from the deck it ends.** If a student sat through the
   lecture and read the slides, they can get it. No outside knowledge, no trivia, nothing from a
   later week.
2. **Never invent a field name, coded value, SQL expression, tool parameter, or data figure.**
   This is the same rule as `CLAUDE.md` rule 3, and it is the one most likely to be broken by a
   quiz question, because a plausible-sounding number makes such a tidy distractor. If the deck
   does not state it, you may not assert it.
3. **Verify tool names and pane locations before asserting them.** ArcGIS Pro has moved things
   between versions. If the deck does not name the pane, do not write a question about which
   pane it is in.
4. **Write "ArcGIS Pro" in full.** Never "Pro".
5. **Test understanding, not recall of a slide's wording.** "Which family does Focal Statistics
   belong to?" is a good question. "What colour was the box on slide 12?" is not. The best
   questions are the ones that started an argument in class.
6. **Distractors must be wrong for a reason you can explain.** Every explanation should teach —
   a student who got it wrong should finish the sentence knowing why, not just knowing the
   letter. Explanations show up again on the results screen under "What to look at again".
7. **Reach forward and back where it is honest.** A question that connects the lecture to the
   lab that week, or to the data model idea from Week 1, is worth two that stay inside one slide.
8. **American English.** Meters, kilometers, center, color, catalog, gray.
9. **Never name an instructor**, and never refer to an earlier version of a handout or deck.
10. **No copyrighted text.** Do not quote a textbook passage as a question stem; describe it.

## The closing slide

Append this as the **last** slide of the deck, after the housekeeping slide, so the code stays
on screen while the room packs up:

```markdown
---

<!-- _class: activity -->

# One last thing — <short title>

<div class="columns">
<div>

<one line saying what the quiz asks, in the deck's own words>

**Scan the code**, or open the link below.

- Not graded, nothing recorded — it is a check that it landed
- Every answer explains itself; read the explanation before you move on
- <one line tying it to the graded quiz or the lab that week>

<span style="font-size: 0.5em; color: #4a5568; white-space: nowrap;">byu-hydroinformatics.github.io/ce414-gis-applications/quizzes/<slug>/</span>

</div>
<div>

![w:400 center](images/quiz-<slug>-qr.png)

</div>
</div>

<!-- Speaker note: how long to give it, which item usually splits the room, and what to say if
     the room has no signal (put the URL on the board; the items read aloud just as well). -->
```

The URL is printed under the code on purpose. A phone with no camera permission, a dead battery
in the back row, or a projector too dim to scan all end the same way without it.

## Building and checking

QR codes are generated, never drawn:

```bash
python3 tools/make_quiz_qr.py <slug>
```

Then check the whole thing the way the deploy will build it:

```bash
sh tools/build_local.sh week-NN      # mkdocs --strict + that week's decks into _site/
```

Before you call a quiz done:

- [ ] `mkdocs build --strict` passes
- [ ] the deck renders, and the QR slide is the last one
- [ ] the QR image is present and not a broken icon on the rendered slide
- [ ] the code decodes to the live quiz URL **from the rendered 1280x720 slide**, not just from
      the source PNG, and the printed URL matches it character for character
- [ ] every `answer` string matches one of its `options` exactly
- [ ] you have played the quiz through to the results screen in a browser at phone width
- [ ] every fact in every question and explanation traces to a specific slide in that deck

## Registering the quiz on the week page

`tools/build_schedule.py` has a `PRACTICE` table that puts the quiz on the week's schedule page,
for students who missed the scan. It is a generated file: edit the table, then re-run the script.
**Do not edit `docs/schedule/` by hand** — see `CLAUDE.md` rule 6a.
