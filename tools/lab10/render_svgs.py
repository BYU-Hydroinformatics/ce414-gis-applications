"""Render Lab 10's SVG figures to PNG previews with headless Chrome so they can be looked at.
(Do not pass --disable-gpu: it renders blank on this machine. Playwright timed out here.)
    python render_svgs.py OUTDIR"""
import pathlib
import subprocess
import sys

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
IMG = pathlib.Path(__file__).resolve().parents[2] / "docs" / "assignments" / "lab-10" / "images"
out = pathlib.Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
for f in sorted(IMG.glob("*.svg")):
    w, h = (1000, 500) if f.name.startswith("lab10-") else (120, 90)
    png = out / (f.stem + ".png")
    subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", "--force-device-scale-factor=2",
                    f"--window-size={w},{h}", f"--screenshot={png}", f.as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
    print(png)
