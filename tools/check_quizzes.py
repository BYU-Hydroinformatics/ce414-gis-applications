#!/usr/bin/env python3
"""Check every lecture quiz and its closing slide.

Run this before committing quiz work and after any change to the quiz engine. It is the
machine-checkable half of the checklist in tools/lecture-quiz-guide.md; the half it cannot
check for you is whether the questions are true, which still needs a person and the deck.

    python3 tools/check_quizzes.py

Exits non-zero if anything fails.
"""
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SITE = "byu-hydroinformatics.github.io/ce414-gis-applications"
sys.path.insert(0, str(REPO / "tools"))
from make_quiz_qr import QUIZZES  # noqa: E402  the single source of truth for slug -> week

problems = []
notes = []


def fail(where, msg):
    problems.append(f"{where}: {msg}")


def _match_bracket(s, i):
    """Index just past the bracket pair that opens at s[i], skipping over strings."""
    open_ch = s[i]
    close_ch = {"[": "]", "{": "}"}[open_ch]
    depth = 0
    quote = None
    while i < len(s):
        c = s[i]
        if quote:
            if c == "\\":
                i += 2
                continue
            if c == quote:
                quote = None
        elif c in "\"'":
            quote = c
        elif c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1


def js_objects(script):
    """Pull the questions array out of a quiz page without executing it.

    The array is authored as JS object literals, so it is read with a small tolerant parser
    rather than json.loads: keys are bare and strings may be single- or double-quoted. The
    array and each object are found by bracket matching, so an `options:` list may be written
    on one line or across several — an earlier version of this parser stopped at the first
    `]` it saw and silently reported one question for a perfectly good eight-question quiz.
    """
    m = re.search(r"questions:\s*\[", script)
    if not m:
        return None
    start = m.end() - 1
    end = _match_bracket(script, start)
    if end < 0:
        return None
    body = script[start + 1:end - 1]

    out = []
    i = 0
    while i < len(body):
        if body[i] != "{":
            i += 1
            continue
        j = _match_bracket(body, i)
        if j < 0:
            break
        block = body[i + 1:j - 1]
        q = {}
        for key in ("prompt", "detail", "explanation"):
            km = re.search(rf'{key}:\s*"((?:[^"\\]|\\.)*)"', block)
            if km:
                q[key] = km.group(1)
        om = re.search(r"options:\s*\[", block)
        if om:
            ostart = om.end() - 1
            oend = _match_bracket(block, ostart)
            q["options"] = re.findall(r'"((?:[^"\\]|\\.)*)"', block[ostart:oend])
        am = re.search(r'answer:\s*(?:"((?:[^"\\]|\\.)*)"|(\d+))', block)
        if am:
            q["answer"] = am.group(1) if am.group(1) is not None else int(am.group(2))
        out.append(q)
        i = j
    return out


def check_quiz(slug):
    page = REPO / f"docs/quizzes/{slug}/index.html"
    where = f"docs/quizzes/{slug}/index.html"
    if not page.exists():
        fail(where, "missing")
        return 0
    html = page.read_text()

    if '"../lib/quiz.css"' not in html:
        fail(where, "does not link ../lib/quiz.css")
    if '"../lib/quiz.js"' not in html:
        fail(where, "does not load ../lib/quiz.js")
    if 'id="quizRoot"' not in html:
        fail(where, "has no #quizRoot container")
    if "<style" in html:
        fail(where, "carries its own <style> block — styling belongs in lib/quiz.css")
    if re.search(r"\bPro\b(?<!ArcGIS Pro)", html.replace("ArcGIS Pro", "")):
        fail(where, 'writes "Pro" on its own; use "ArcGIS Pro" in full')

    qs = js_objects(html)
    if qs is None:
        fail(where, "could not find a questions array")
        return 0
    if not 6 <= len(qs) <= 10:
        fail(where, f"has {len(qs)} questions; the guide asks for 6-8")

    for i, q in enumerate(qs, 1):
        at = f"{where} q{i}"
        if not q.get("prompt"):
            fail(at, "no prompt")
        opts = q.get("options") or []
        if not 2 <= len(opts) <= 4:
            fail(at, f"has {len(opts)} options; 2 to 4 allowed")
        ans = q.get("answer")
        if isinstance(ans, int):
            if not 0 <= ans < len(opts):
                fail(at, f"answer index {ans} is out of range")
        elif ans not in opts:
            fail(at, f'answer "{ans}" does not match any option {opts}')
        if not q.get("explanation"):
            fail(at, "no explanation")
        elif len(q["explanation"]) < 40:
            notes.append(f"{at}: explanation is very short")
    return len(qs)


def check_slide(slug, week):
    decks = sorted(REPO.glob(f"slides/week-{week:02d}/*.md"))
    hits = [d for d in decks if f"images/quiz-{slug}-qr.png" in d.read_text()]
    where = f"slides/week-{week:02d}"
    if not hits:
        fail(where, f"no deck carries images/quiz-{slug}-qr.png")
        return
    if len(hits) > 1:
        fail(where, f"{len(hits)} decks carry the {slug} code: {[h.name for h in hits]}")
    deck = hits[0]
    text = deck.read_text()
    where = str(deck.relative_to(REPO))

    png = REPO / f"slides/week-{week:02d}/images/quiz-{slug}-qr.png"
    if not png.exists():
        fail(where, f"QR image {png.name} does not exist")

    url = f"{SITE}/quizzes/{slug}/"
    if url not in text:
        fail(where, f"does not print the quiz URL {url} as a scan fallback")

    # The quiz slide must be the last one. Slides are separated by a --- on its own line.
    # A deck often ends with an authoring-notes HTML comment, which is not a slide, so walk
    # back from the end and skip any chunk that is nothing but comments and whitespace.
    # (Stripping those notes with a regex instead is what broke an earlier version of this
    # check: a notes block sitting mid-deck swallowed everything after it.)
    chunks = text.split("\n---\n")
    last = ""
    for chunk in reversed(chunks):
        if re.sub(r"<!--.*?-->", "", chunk, flags=re.S).strip():
            last = chunk
            break
    if f"images/quiz-{slug}-qr.png" not in last:
        fail(where, "the quiz slide is not the last slide of the deck")
    if "_class: activity" not in last:
        notes.append(f"{where}: quiz slide is not marked <!-- _class: activity -->")


def check_practice():
    """Every quiz must be listed on its week page, under the title the page itself uses.

    The two drift apart easily: the quiz page is written by one hand and the schedule table by
    another, and a student who scans the code gets one title while the week page promises a
    different one.
    """
    from build_schedule import PRACTICE
    listed = {}
    for week, items in PRACTICE.items():
        for slug, title, _desc in items:
            listed[slug] = (week, title)
    for slug, week in QUIZZES.items():
        if slug not in listed:
            fail("tools/build_schedule.py", f"PRACTICE does not list the {slug} quiz")
            continue
        lweek, ltitle = listed[slug]
        if lweek != week:
            fail("tools/build_schedule.py", f"PRACTICE files {slug} under week {lweek}, not {week}")
        page = REPO / f"docs/quizzes/{slug}/index.html"
        if not page.exists():
            continue
        m = re.search(r'title:\s*"([^"]*)"', page.read_text())
        if m and m.group(1) != ltitle:
            fail("tools/build_schedule.py",
                 f'PRACTICE calls {slug} "{ltitle}"; the page calls itself "{m.group(1)}"')
    for slug in listed:
        if slug not in QUIZZES:
            fail("tools/build_schedule.py", f"PRACTICE lists {slug}, which make_quiz_qr.py does not know")


def main():
    total = 0
    for slug, week in sorted(QUIZZES.items()):
        total += check_quiz(slug)
        check_slide(slug, week)
    check_practice()

    print(f"{len(QUIZZES)} quizzes, {total} questions")
    for n in notes:
        print(f"  note  {n}")
    for p in problems:
        print(f"  FAIL  {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
