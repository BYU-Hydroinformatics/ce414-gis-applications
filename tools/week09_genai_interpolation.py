"""Week 9 Thursday experiment: ask a generative image model to interpolate the Timpanogos samples.

The same 150 samples, 60 hold-out points and truth as tools/week09_elevation_figures.py (same DEM
request, same seed). The samples are drawn as a grayscale heightmap on a red "missing data" background
(brightness = elevation, 1,800 m black to 3,600 m white, about 7 m per gray level), and an OpenAI image
model is asked to fill in the red with realistic terrain that keeps every measured value. The picture it
returns is turned back into elevations (gray level to meters, then a straight-line rescale fitted to the
150 samples only, which is fair: it uses nothing a real project would not have) and scored exactly like
the six methods: RMSE at the 60 hold-out points and over every cell of the true DEM.

The image model is not a terrain model and returns 8-bit pixels, not elevations, so the result is a
lower bound on what a purpose-built generative model trained on DEMs could do.

    python tools/week09_genai_interpolation.py --generate                # points only (costs money)
    python tools/week09_genai_interpolation.py --generate --mode detail  # add detail to kriging
    python tools/week09_genai_interpolation.py                           # score saved outputs, draw the figure

Two tests. "points": the samples alone, as above. "detail": the fitted kriged surface as a grayscale
heightmap, with the model asked to add realistic ridge-and-gully detail while keeping the large-scale
shape, which is closer to how generative models are used on DEMs (void filling and sharpening).

--generate needs an OpenAI key in OPENAI_API_KEY or ~/.config/openai/api_key (never printed). The
input, prompt and every returned image are kept in tools/week09_genai/ so the scoring can be rerun.
Writes slides/week-09/images/ie-genai-compare.png and tools/week09_genai/numbers.json.
"""

import argparse
import base64
import io
import json
import os
import pathlib
import urllib.parse
import urllib.request
import uuid

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import tifffile
from matplotlib.colors import LightSource, LinearSegmentedColormap
from PIL import Image
from pykrige.ok import OrdinaryKriging

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "slides" / "week-09" / "images"
WORK = ROOT / "tools" / "week09_genai"
WORK.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": ["Segoe UI", "Arial", "DejaVu Sans"], "font.size": 12})
NAVY = "#002e5d"
LO, HI = 1800.0, 3600.0                      # the gray scale: LO is black, HI is white
PX = 1024                                    # input and output image size

PROMPT = (
    "This image is a top-down grayscale heightmap (digital elevation model) of a 7.2 km square of rugged "
    "mountain terrain: brighter pixels are higher ground, black is about 1,800 m and white about 3,600 m. "
    "Only the small gray squares are measured elevations. Every red pixel is missing data. Replace all of "
    "the red with the most likely, realistic, physically believable grayscale terrain: ridges, peaks, "
    "valleys and drainage that pass smoothly through every measured square and keep each square's gray "
    "value exactly. Output only the completed grayscale heightmap, same framing and scale, top-down, with "
    "no red, no shading, no labels, no border and no 3D perspective.")
PROMPT_DETAIL = (
    "This image is a top-down grayscale heightmap (digital elevation model) of a 7.2 km square of rugged "
    "mountain terrain: brighter pixels are higher ground, black is about 1,800 m and white about 3,600 m. "
    "It was interpolated from scattered measurements, so it is too smooth: the real ground has sharp "
    "ridges, peaks, gullies and branching drainage that the interpolation blurred away. Add the most "
    "likely, realistic, physically believable fine terrain detail, but keep the large-scale shape and the "
    "overall brightness of every area the same: do not move, add or remove major peaks or valleys. Output "
    "only the grayscale heightmap, same framing and scale, top-down, with no shading, no labels, no border "
    "and no 3D perspective.")
MODEL = "gpt-image-2.5-flare"

# --- truth, samples and hold-outs, exactly as in week09_elevation_figures.py ------------------------------
CX, CY, HALF, CELL = 445200, 4471300, 3600, 30
N = 2 * HALF // CELL
q = dict(bbox=f"{CX - HALF},{CY - HALF},{CX + HALF},{CY + HALF}", bboxSR=26912, imageSR=26912,
         size=f"{N},{N}", format="tiff", pixelType="F32", noDataInterpretation="esriNoDataMatchAny",
         interpolation="RSP_BilinearInterpolation", f="image")
url = ("https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage?"
       + urllib.parse.urlencode(q))
T = tifffile.imread(io.BytesIO(urllib.request.urlopen(url, timeout=120).read())).astype(float)
assert T.shape == (N, N) and not np.isnan(T).any()
x = (np.arange(N) + 0.5) * CELL / 1000
y = (np.arange(N) + 0.5) * CELL / 1000
rng = np.random.default_rng(414)
idx = rng.choice((N - 8) ** 2, 150, replace=False)
r, c = idx // (N - 8) + 4, idx % (N - 8) + 4
P = np.c_[x[c], y[r]]
V = T[r, c]
rest = np.setdiff1d(np.arange((N - 8) ** 2), idx)
hidx = rng.choice(rest, 60, replace=False)
hr, hc = hidx // (N - 8) + 4, hidx % (N - 8) + 4


def rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def draw_input(path):
    """Samples as gray squares (about 2 cells wide) on red."""
    im = np.zeros((PX, PX, 3), np.uint8); im[..., 0] = 255
    s = PX / N
    for rr, cc, v in zip(r, c, V):
        g = int(round(np.clip((v - LO) / (HI - LO), 0, 1) * 255))
        y0, x0 = int((rr - 0.5) * s), int((cc - 0.5) * s)
        im[y0:y0 + 9, x0:x0 + 9] = g
    Image.fromarray(im).save(path)


def resolve_key():
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        return key
    f = pathlib.Path.home() / ".config" / "openai" / "api_key"
    if f.exists() and f.read_text().strip():
        return f.read_text().strip().splitlines()[0].strip()
    raise SystemExit("No OpenAI key: set OPENAI_API_KEY or write it to ~/.config/openai/api_key")


def call_edit(key, image_path, prompt, out_path, quality="medium"):
    """POST /v1/images/edits as multipart form data, standard library only."""
    bnd = uuid.uuid4().hex
    parts = []
    for name, val in [("model", MODEL), ("prompt", prompt), ("size", f"{PX}x{PX}"), ("quality", quality), ("n", "1")]:
        parts.append(f'--{bnd}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{val}\r\n'.encode())
    parts.append(f'--{bnd}\r\nContent-Disposition: form-data; name="image"; filename="input.png"\r\n'
                 f'Content-Type: image/png\r\n\r\n'.encode() + pathlib.Path(image_path).read_bytes() + b"\r\n")
    parts.append(f"--{bnd}--\r\n".encode())
    req = urllib.request.Request("https://api.openai.com/v1/images/edits", data=b"".join(parts), method="POST",
                                 headers={"Authorization": f"Bearer {key}",
                                          "Content-Type": f"multipart/form-data; boundary={bnd}"})
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            payload = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"API error {e.code}: {e.read().decode(errors='replace')[:400]}")
    pathlib.Path(out_path).write_bytes(base64.b64decode(payload["data"][0]["b64_json"]))
    return payload.get("usage")


ap = argparse.ArgumentParser()
ap.add_argument("--generate", action="store_true", help="call the API for a new output (costs money)")
ap.add_argument("--mode", choices=["points", "detail"], default="points",
                help="points: fill in from the samples alone; detail: add detail to the kriged surface")
ap.add_argument("--quality", default="medium")
args = ap.parse_args()

ok = OrdinaryKriging(P[:, 0], P[:, 1], V, variogram_model="spherical",
                     variogram_parameters=[183646.654, 4.559, 0.0], exact_values=False)
kr = ok.execute("grid", x, y)[0].data


def draw_kriged(path):
    g = np.clip((kr - LO) / (HI - LO), 0, 1) * 255
    Image.fromarray(g.astype(np.uint8)).resize((PX, PX), Image.BICUBIC).convert("RGB").save(path)


if args.generate:
    m = args.mode
    inp = WORK / f"{m}-input.png"
    (draw_input if m == "points" else draw_kriged)(inp)
    prompt = PROMPT if m == "points" else PROMPT_DETAIL
    (WORK / f"{m}-prompt.txt").write_text(prompt + "\n")
    k = len(list(WORK.glob(f"{m}-[0-9]*.png"))) + 1
    usage = call_edit(resolve_key(), inp, prompt, WORK / f"{m}-{k}.png", args.quality)
    print(f"wrote {m}-{k}.png; usage {usage}")


def latest(m):
    outs = sorted(WORK.glob(f"{m}-[0-9]*.png"), key=lambda p: int(p.stem.split("-")[1]))
    return outs[-1] if outs else None


def decode(out):
    """Gray level to meters, then a straight-line rescale fitted to the 150 samples only."""
    rgb = np.asarray(Image.open(out).convert("RGB").resize((N, N), Image.BOX), float)
    raw = LO + rgb.mean(axis=2) / 255 * (HI - LO)
    a1, a0 = np.polyfit(raw[r, c], V, 1)
    z = a0 + a1 * raw
    return z, {"output": out.name, "rescale_slope": round(float(a1), 4), "rescale_intercept_m": round(float(a0), 1),
               "rmse_holdout_m": round(rmse(z[hr, hc], T[hr, hc]), 1), "rmse_m": round(rmse(z, T), 1),
               "rmse_at_samples_m": round(rmse(z[r, c], V), 1),
               "rmse_holdout_raw_m": round(rmse(raw[hr, hc], T[hr, hc]), 1)}


nums = {"model": MODEL, "prompt_points": PROMPT, "prompt_detail": PROMPT_DETAIL,
        "kriging_fitted": {"rmse_holdout_m": round(rmse(kr[hr, hc], T[hr, hc]), 1), "rmse_m": round(rmse(kr, T), 1),
                           "rmse_at_samples_m": round(rmse(kr[r, c], V), 1)},
        "mean_only_rmse_holdout_m": round(rmse(np.full(60, V.mean()), T[hr, hc]), 1)}
surf = {}
for m in ["points", "detail"]:
    if latest(m):
        surf[m], nums[f"genai_{m}"] = decode(latest(m))
if "points" not in surf:
    raise SystemExit("no points output yet: run with --generate")
(WORK / "numbers.json").write_text(json.dumps(nums, indent=2) + "\n")
print(json.dumps({k: v for k, v in nums.items() if not k.startswith("prompt")}, indent=1))

# --- figure: input, truth, kriging, generative AI ------------------------------------------------------------
TERRAIN = LinearSegmentedColormap.from_list(
    "terr", ["#3f7f3a", "#8fb35a", "#d9c98a", "#b88a5a", "#8a6a55", "#c9c2bb", "#ffffff"])
ls = LightSource(azdeg=315, altdeg=40)
XX, YY = np.meshgrid(x, y)


def panel(ax, Z, title, sub=None, points=True):
    ax.imshow(ls.shade(Z, cmap=TERRAIN, vert_exag=1, dx=CELL, dy=CELL, blend_mode="soft", vmin=LO, vmax=HI),
              extent=(0, 7.2, 7.2, 0))
    ax.contour(XX, YY, Z, levels=np.arange(1800, 3700, 100), colors="k", linewidths=0.3, alpha=0.5)
    if points:
        ax.plot(P[:, 0], P[:, 1], "o", ms=2.2, color="black", mec="white", mew=0.4)
    ax.set_xlim(0, 7.2); ax.set_ylim(7.2, 0); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontsize=13, color=NAVY, loc="left", weight="bold")
    if sub:
        ax.text(0, -0.03, sub, transform=ax.transAxes, fontsize=10.5, color="#4a5568", va="top")


cols = 5 if "detail" in surf else 4
fig, axs = plt.subplots(1, cols, figsize=(3.25 * cols, 3.9), dpi=170)
axs[0].imshow(np.asarray(Image.open(WORK / "points-input.png")), extent=(0, 7.2, 7.2, 0))
axs[0].set_xticks([]); axs[0].set_yticks([])
axs[0].set_title("What the AI was given", fontsize=13, color=NAVY, loc="left", weight="bold")
axs[0].text(0, -0.03, "150 samples as gray; red = missing", transform=axs[0].transAxes, fontsize=10.5,
            color="#4a5568", va="top")
panel(axs[1], T, "The truth", "30 m DEM", points=False)
panel(axs[2], kr, "Kriging (fitted)", f"error {nums['kriging_fitted']['rmse_holdout_m']:.0f} m at the hold-outs")
panel(axs[3], surf["points"], "AI from the points", f"error {nums['genai_points']['rmse_holdout_m']:.0f} m at the hold-outs")
if "detail" in surf:
    panel(axs[4], surf["detail"], "AI detail on kriging", f"error {nums['genai_detail']['rmse_holdout_m']:.0f} m at the hold-outs")
fig.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.1, wspace=0.05)
fig.savefig(IMG / "ie-genai-compare.png", facecolor="white"); plt.close(fig)
