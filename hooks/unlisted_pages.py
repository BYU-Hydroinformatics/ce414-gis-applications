"""Keep unlisted pages out of sitemap.xml.

A page whose front matter sets `search: exclude: true` (the lab drafts) is already left out of the
site menu and the search index. mkdocs still lists every page in sitemap.xml, which is what search
engines crawl, so without this hook a draft meant to be reached only by its link would be indexed.
Registered in mkdocs.yml under `hooks:`.
"""
import gzip
import os
import re

_unlisted = set()


def on_page_markdown(markdown, page, config, files, **kwargs):
    search = page.meta.get("search") or {}
    if isinstance(search, dict) and search.get("exclude"):
        _unlisted.add(page.url)
    return markdown


def on_post_build(config, **kwargs):
    if not _unlisted:
        return
    path = os.path.join(config["site_dir"], "sitemap.xml")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        xml = fh.read()
    for url in _unlisted:
        xml = re.sub(r"\s*<url>\s*<loc>[^<]*/" + re.escape(url) + r"</loc>.*?</url>", "", xml, flags=re.S)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(xml)
    with gzip.open(path + ".gz", "wb") as fh:
        fh.write(xml.encode("utf-8"))
