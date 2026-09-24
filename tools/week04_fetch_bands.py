# Download the blue and green bands (B2, B3) of the Lab 2 Utah County Landsat 8 scene from the
# Microsoft Planetary Computer mirror of the USGS archive, for the Week 4 band-by-band slides.
# Red (B4) and NIR (B5) come from the Lab 2 download; this adds the two bands Lab 2 did not need.
# No key needed: the SAS token endpoint is public (same method as tools/lab02/fetch_second_scene.py).
#   python week04_fetch_bands.py <dir>
import sys, json, os, urllib.request, urllib.parse

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
SIGN = "https://planetarycomputer.microsoft.com/api/sas/v1/sign?href="
ITEM = "LC08_L2SP_038032_20250712_02_T1"


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    req = urllib.request.Request(STAC, data=json.dumps({"collections": ["landsat-c2-l2"], "ids": [ITEM]}).encode(),
                                 headers={"Content-Type": "application/json"})
    item = json.load(urllib.request.urlopen(req, timeout=120))["features"][0]
    for key in ("blue", "green", "red", "nir08"):
        href = item["assets"][key]["href"]
        name = os.path.basename(urllib.parse.urlparse(href).path)
        dst = os.path.join(outdir, name)
        if os.path.exists(dst):
            print("have", name); continue
        with urllib.request.urlopen(SIGN + urllib.parse.quote(href, safe=""), timeout=60) as r:
            url = json.load(r)["href"]
        print("downloading", name, flush=True)
        urllib.request.urlretrieve(url, dst)
        print("  ->", os.path.getsize(dst) // 1_000_000, "MB", flush=True)
    json.dump(item, open(os.path.join(outdir, "stac_item.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
