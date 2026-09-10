#!/usr/bin/env python3
"""Stamp every deck's title slide with its last-updated date and the copyright line.

    python3 tools/stamp_decks.py            # rewrite the stamps
    python3 tools/stamp_decks.py --check    # exit 1 if any stamp is out of date

The date is not typed by hand: it is the commit date of the most recent commit that touched the
deck's own markdown or any image the deck references. That is the honest answer to "when was this
deck last changed", and it cannot drift the way a hand-edited date does. Uncommitted changes to a
deck are reported and the deck is stamped with today's date, since the working tree is newer than
anything git knows about.

The stamp replaces Marp's footer on the title slide only, so the three pieces can be placed
deliberately: the course line where the footer would have been, the last-updated line directly
under it in a dimmer gray, and the copyright opposite on the right. `section.lead .titlestamp` in
slides/theme/ce414.css does the placing. Every other slide keeps the ordinary Marp footer.

Re-run this before publishing a deck; the date is only as fresh as the last run. It is idempotent:
running it twice in a row changes nothing.
"""
import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CC_URL = "https://creativecommons.org/licenses/by/4.0/"
# Creative Commons' recommended marking: the rights holder, then the licence, linked to its deed.
# Copyright and CC BY coexist — the author keeps copyright and grants the licence on top of it.
COPYRIGHT = f'© 2026 Daniel P. Ames · <a href="{CC_URL}">CC BY 4.0</a>'
# Not a deck: a planning document that happens to live in a week folder.
SKIP = {"LECTURE_PLAN.md"}

BEGIN = "<!-- stamp:begin -->"
END = "<!-- stamp:end -->"
STAMP_RE = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", re.DOTALL)


def unstamped(text):
    """The deck with its stamp and the blank line the stamp introduced removed, so two versions
    can be compared on their real content. Collapsing runs of blank lines is safe here — Markdown
    treats one blank line and three the same — and it is what makes stamping idempotent."""
    return re.sub(r"\n{3,}", "\n\n", STAMP_RE.sub("", text)).strip()


def git_last_date(paths):
    """Commit date (YYYY-MM-DD) of the most recent commit touching any of `paths`."""
    out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", *paths],
                         cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
    return out.stdout.strip()


def is_dirty(deck, text, image_paths):
    """Has anything about this deck changed since the last commit, ignoring the stamp itself?

    The stamp must not count. Writing a stamp modifies the deck, which would make the next run see
    a dirty file and stamp it with today's date, which modifies it again — the date would creep
    forward every run and never reflect a real edit. So the deck is compared against its committed
    version with the stamp stripped from both sides. Images are compared normally."""
    if image_paths:
        out = subprocess.run(["git", "status", "--porcelain", "--", *image_paths],
                             cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        if out.stdout.strip():
            return True
    rel = deck.relative_to(ROOT).as_posix()
    committed = subprocess.run(["git", "show", f"HEAD:{rel}"],
                               cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if committed.returncode != 0:          # never committed
        return True
    return unstamped(committed.stdout) != unstamped(text)


def local_images(deck, text):
    """Every image the deck references from disk, as repo-relative paths that exist."""
    found = []
    for m in re.finditer(r"!\[[^\]]*\]\(([^)\s]+)", text):
        url = m.group(1)
        if url.startswith(("http:", "https:", "data:", "#")):
            continue
        p = (deck.parent / url).resolve()
        if p.exists():
            found.append(str(p.relative_to(ROOT)))
    return sorted(set(found))


def footer_text(text):
    """The deck's front-matter footer, which the title slide reproduces before dropping it."""
    m = re.search(r"^footer:\s*(.+?)\s*$", text, re.MULTILINE)
    if not m:
        return None
    return m.group(1).strip().strip('"').strip("'")


def stamp_block(footer, date):
    """The title slide's own footer, overriding the front matter's for this one slide.

    Marp's footer is the only element rendered across the full slide width: a slide with a split
    background puts its content in a narrower column, so anything placed in the body cannot reach
    the right edge. The directive value must stay on one line, hence single quotes outside and
    double inside."""
    left = f'<span>{footer}<span class="updated">Last Updated: {date}</span></span>'
    right = f"<span>{COPYRIGHT}</span>"
    return f"{BEGIN}\n<!-- _footer: '{left}{right}' -->\n{END}\n"


def title_slide_end(text):
    """Index of the separator that closes slide 1, i.e. the first '---' line after the front
    matter. Returns None if the deck has only a title slide."""
    fm = re.match(r"---\n.*?\n---\n", text, re.DOTALL)
    if not fm:
        raise SystemExit("deck has no Marp front matter")
    m = re.search(r"^---\s*$", text[fm.end():], re.MULTILINE)
    return None if m is None else fm.end() + m.start()


def process(deck, check):
    text = deck.read_text(encoding="utf-8")
    footer = footer_text(text)
    if footer is None:
        return f"SKIP  {deck.relative_to(ROOT).as_posix()} — no footer in front matter", False

    images = local_images(deck, text)
    if is_dirty(deck, text, images):
        date = dt.date.today().isoformat()
        note = " (uncommitted changes, stamped today)"
    else:
        date = git_last_date([str(deck.relative_to(ROOT)), *images])
        note = ""

    body = STAMP_RE.sub("", text)
    cut = title_slide_end(body)
    block = stamp_block(footer, date)
    if cut is None:
        new = body.rstrip("\n") + "\n\n" + block
    else:
        new = body[:cut].rstrip("\n") + "\n\n" + block + "\n" + body[cut:]

    changed = new != text
    if changed and not check:
        deck.write_bytes(new.encode("utf-8"))
    verb = ("would update" if check else "updated") if changed else "unchanged"
    return f"{verb:<13} {deck.relative_to(ROOT).as_posix():<48} {date}{note}", changed


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="report what would change and exit 1 if anything would")
    args = ap.parse_args()

    stale = 0
    for deck in sorted(ROOT.glob("slides/week-*/*.md")):
        if deck.name in SKIP:
            continue
        line, changed = process(deck, args.check)
        print(line)
        stale += bool(changed)

    if args.check and stale:
        print(f"\n{stale} deck(s) carry a stale stamp — run tools/stamp_decks.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
