"""Remove section-divider (lead) slides from a Marp deck, keeping the title slide.

A lead slide is one whose body starts with `<!-- _class: lead -->`; the title slide also carries
`<!-- _paginate: skip -->` and is kept. Any speaker-note comment on a removed divider is appended
to the following slide's notes so nothing the instructor wrote is lost.

    python tools/drop_lead_slides.py slides/week-07/lake-bathymetry.md [more decks]
"""
import re
import sys

for path in sys.argv[1:]:
    text = open(path, encoding="utf-8").read()
    parts = text.split("\n---\n")          # parts[0] is the front matter
    out, carry, dropped = [parts[0]], [], 0
    for body in parts[1:]:
        if "<!-- _class: lead -->" in body and "_paginate: skip" not in body:
            carry += [c.strip() for c in re.findall(r"<!--(?!\s*_)(.*?)-->", body, flags=re.S) if c.strip()]
            dropped += 1
            continue
        if carry:
            body = body.rstrip("\n") + "\n\n" + "\n\n".join(f"<!-- {c} -->" for c in carry) + "\n"
            carry = []
        out.append(body)
    open(path, "w", encoding="utf-8").write("\n---\n".join(out))
    print(f"{path}: dropped {dropped} divider slide(s)")
