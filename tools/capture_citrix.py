#!/usr/bin/env python3
"""Capture a region of the Citrix/ArcGIS Pro session from the Mac side.

Why this exists: nothing can be saved *out* of the BYU Citrix HTML5 session
(Snipping Tool, PowerPoint Save and the image clipboard all fail — see
ROADMAP.md, "How to capture new ArcGIS Pro screenshots"). What does work is
capturing the Chrome window on the Mac with `screencapture`, at full Retina
resolution, and cropping the region we want with Pillow.

Usage
-----
    # 1. Read the Chrome viewport offsets once per session (Claude in Chrome
    #    javascript_tool, on the Citrix tab):
    #      ({sx: window.screenX, sy: window.screenY,
    #        top: window.outerHeight - window.innerHeight,
    #        dpr: window.devicePixelRatio})
    #
    # 2. Capture a region given in *viewport* CSS pixels:
    python3 tools/capture_citrix.py --sx 0 --sy 25 --top 87 \
        --region 330,320,1060,790 \
        --out docs/assignments/lab-05/images/lab05-fill-model.png

    # A full-screen grab with no crop, for inspection:
    python3 tools/capture_citrix.py --sx 0 --sy 25 --top 87 --out /tmp/full.png

Notes
-----
- Brings Chrome to the front first (the Claude desktop window otherwise
  occludes it) and waits a moment for the compositor.
- The Chrome window must be fully on screen; captures clip at the right edge
  otherwise.
- Physical pixels = (screenX + x) * dpr, (screenY + top + y) * dpr.
- Output is written at native (2x) resolution. Pass --downscale 2 for 1x.
"""
import argparse
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from PIL import Image


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--sx", type=int, required=True, help="window.screenX of the Chrome window")
    p.add_argument("--sy", type=int, required=True, help="window.screenY of the Chrome window")
    p.add_argument("--top", type=int, required=True, help="outerHeight - innerHeight (tab strip + toolbar)")
    p.add_argument("--dpr", type=float, default=2.0, help="devicePixelRatio (default 2)")
    p.add_argument("--region", help="x0,y0,x1,y1 in viewport CSS pixels; omit for the whole screen")
    p.add_argument("--downscale", type=float, default=1.0, help="divide output size by this factor")
    p.add_argument("--out", required=True, help="output PNG path")
    p.add_argument("--no-activate", action="store_true", help="do not bring Chrome to the front first")
    a = p.parse_args()

    if not a.no_activate:
        subprocess.run(["osascript", "-e", 'tell application "Google Chrome" to activate'], check=False)
        time.sleep(1.5)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
    subprocess.run(["screencapture", "-x", tmp_path], check=True)
    im = Image.open(tmp_path)

    if a.region:
        x0, y0, x1, y1 = (int(v) for v in a.region.split(","))
        box = (
            int((a.sx + x0) * a.dpr),
            int((a.sy + a.top + y0) * a.dpr),
            int((a.sx + x1) * a.dpr),
            int((a.sy + a.top + y1) * a.dpr),
        )
        im = im.crop(box)

    if a.downscale and a.downscale != 1.0:
        im = im.resize((int(im.width / a.downscale), int(im.height / a.downscale)), Image.LANCZOS)

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, optimize=True)
    Path(tmp_path).unlink(missing_ok=True)
    print(f"wrote {out} ({im.width}x{im.height})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
