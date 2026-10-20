"""Week 8 Tuesday: bathtub versus HAND along the Provo River's long profile, plus single-panel
crops of fl-bathtub-vs-hand.png. Reads tools/lab07/profile.json (profile.py, Oct 9 2026).

    propy.bat tools/week08_profile_figure.py      (any Python with matplotlib + Pillow works)

Writes slides/week-08/images/fl-river-profile.png, fl-bathtub-map.png, fl-hand-map-panel.png.
"""
import json, os, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
IMG = HERE.parent / "slides" / "week-08" / "images"
d = json.load(open(HERE / "lab07" / "profile.json"))
km = [p[0] for p in d["long"]]; z = [p[1] for p in d["long"]]
h = d["h100_m"]; bath = d["elev100_m"]; gage_km = d["gage_km"]
EX = 8  # the water surface is drawn EX times the real depth so that it can be seen at this scale

plt.rcParams.update({"font.family": "Segoe UI", "font.size": 12})
fig, ax = plt.subplots(figsize=(9, 4.2), dpi=150)
ax.fill_between(km, 1360, z, color="#d9c7a3", lw=0)
ax.plot(km, z, color="#8b5e34", lw=1.8, label="river bed, mouth of Provo Canyon to Utah Lake")
zs = [v + h * EX for v in z]
ax.fill_between(km, z, zs, color="#63b3ed", alpha=0.85, lw=0)
ax.plot(km, zs, color="#2b6cb0", lw=1.8, label=f"HAND: the whole surface rises by h = {h:.2f} m (drawn {EX}x)")
ax.axhline(bath, color="#dd6b20", ls="--", lw=2, label=f"bathtub: one elevation, {bath:,.2f} m")
# bathtub pool: where the bed is below the bathtub line
below = [v <= bath for v in z]
ax.fill_between(km, z, bath, where=below, color="#dd6b20", alpha=0.35, lw=0)
ax.axvline(gage_km, color="#4a5568", ls=":", lw=1.2)
ax.text(gage_km + 0.15, 1363.5, "gage", ha="left", va="bottom", fontsize=11, color="#4a5568")
ax.annotate(f"the bathtub reaches only the lowest {d['long_summary']['km_below_bathtub']:.1f} km",
            xy=(km[-1] - 2.4, bath + 2), xytext=(9.2, 1400), fontsize=11, color="#9c4221",
            arrowprops=dict(arrowstyle="->", color="#9c4221"))
ax.annotate("HAND floods the river all the way up", xy=(3.5, zs[int(len(z) * 3.5 / km[-1])] + 1),
            xytext=(4.2, 1455), fontsize=11, color="#1a365d", arrowprops=dict(arrowstyle="->", color="#1a365d"))
ax.set_xlim(0, km[-1]); ax.set_ylim(1362, 1480)
ax.set_xlabel("distance downstream (km)"); ax.set_ylabel("elevation (m, NAVD 88)")
ax.set_title("The same 1 % flood, two ways, along the river", loc="left", fontsize=13, color="#1a365d")
ax.legend(loc="upper right", fontsize=9.5, frameon=False)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(IMG / "fl-river-profile.png"); plt.close(fig)
print("fl-river-profile.png")

im = Image.open(IMG / "fl-bathtub-vs-hand.png"); w, hh = im.size
# the two map panels sit left and right of center; keep each panel with its two-line caption
im.crop((int(w * 0.05), int(hh * 0.065), int(w * 0.46), int(hh * 0.98))).save(IMG / "fl-bathtub-map.png", optimize=True)
im.crop((int(w * 0.54), int(hh * 0.065), int(w * 0.95), int(hh * 0.98))).save(IMG / "fl-hand-map-panel.png", optimize=True)
print("fl-bathtub-map.png fl-hand-map-panel.png", w, hh)
