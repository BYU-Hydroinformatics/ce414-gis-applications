"""Add a content hash to the site's own CSS and JavaScript links.

GitHub Pages lets browsers cache files for ten minutes, and a browser can keep a stylesheet longer
than that, so after a push a student could see new page markup styled by an old extra.css. Each
link to a file listed under extra_css or extra_javascript gets "?v=<hash of the file>", so the URL
changes exactly when the file does. Registered in mkdocs.yml under `hooks:`.
"""
import hashlib
import os
import re

_versions = {}


def on_config(config, **kwargs):
    _versions.clear()
    for entry in list(config["extra_css"]) + list(config["extra_javascript"]):
        path = str(getattr(entry, "path", entry))
        src = os.path.join(config["docs_dir"], path)
        if os.path.isfile(src):
            with open(src, "rb") as f:
                _versions[path] = hashlib.sha1(f.read()).hexdigest()[:10]
    return config


def on_post_page(output, page, config, **kwargs):
    for path, version in _versions.items():
        output = re.sub(r'((?:href|src)="[^"]*?' + re.escape(path) + r')"', r'\1?v=' + version + '"', output)
    return output
