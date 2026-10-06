"""Remove HTML comments from every page before it is rendered.

The lab pages carry instructor-facing HTML comments (revision notes, migration notes, measured
sensitivity tables, TODOs). Python-Markdown passes comments through to the HTML, so without this
hook they sit in the page source of the public site. Comments inside fenced code blocks are left
alone. Registered in mkdocs.yml under `hooks:`.

This only cleans the rendered site; the Markdown is still readable on the public GitHub repo.
"""
import re

_FENCE = re.compile(r"^( {0,3})(`{3,}|~{3,})", re.M)
_COMMENT = re.compile(r"<!--.*?-->", re.S)


def _strip(text):
    # A comment that is the whole of its line(s) leaves no blank-line debris.
    text = re.sub(r"^[ \t]*<!--.*?-->[ \t]*\n", "", text, flags=re.S | re.M)
    return _COMMENT.sub("", text)


def on_page_markdown(markdown, page, config, files, **kwargs):
    out, pos, fence = [], 0, None
    for m in _FENCE.finditer(markdown):
        marker = m.group(2)
        if fence is None:
            out.append(_strip(markdown[pos:m.start()]))
            pos, fence = m.start(), marker
        elif marker[0] == fence[0] and len(marker) >= len(fence):
            end = markdown.find("\n", m.end())
            end = len(markdown) if end == -1 else end + 1
            out.append(markdown[pos:end])
            pos, fence = end, None
    rest = markdown[pos:]
    out.append(rest if fence else _strip(rest))
    return "".join(out)
