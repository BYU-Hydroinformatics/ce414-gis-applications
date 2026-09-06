# Find and download a second Landsat 8/9 Collection 2 Level-2 scene (red + NIR + MTL) from the
# Microsoft Planetary Computer mirror of the USGS archive, for the second prepared extract in the
# Lab 2 draft. No key needed: the SAS token endpoint is public.
#   python fetch_second_scene.py search              -> list candidate scenes
#   python fetch_second_scene.py get <item_id> <dir> -> download red, nir08 and mtl.txt into <dir>
import sys, json, os, urllib.request, urllib.parse

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
SIGN = "https://planetarycomputer.microsoft.com/api/sas/v1/sign?href="
# Eastern Snake River Plain around Rupert / Burley / Paul, Idaho: dense center-pivot country,
# and the region the lab's Kramber reference (Idaho Dept. of Water Resources) works in.
BBOX = [-113.9, 42.5, -113.4, 42.8]


def post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def search():
    body = {"collections": ["landsat-c2-l2"], "bbox": BBOX, "datetime": "2025-06-25/2025-08-20",
            "query": {"eo:cloud_cover": {"lt": 10}, "platform": {"in": ["landsat-8", "landsat-9"]}}, "limit": 20}
    res = post(STAC, body)
    for f in res["features"]:
        p = f["properties"]
        print(f["id"], p["datetime"][:10], p.get("platform"), "cloud", p.get("eo:cloud_cover"),
              "path/row", p.get("landsat:wrs_path"), p.get("landsat:wrs_row"))


def get(item_id, outdir):
    os.makedirs(outdir, exist_ok=True)
    res = post(STAC, {"collections": ["landsat-c2-l2"], "ids": [item_id]})
    item = res["features"][0]
    for key in ("red", "nir08", "mtl.txt"):
        href = item["assets"][key]["href"]
        with urllib.request.urlopen(SIGN + urllib.parse.quote(href, safe=""), timeout=60) as r:
            url = json.load(r)["href"]
        name = os.path.basename(urllib.parse.urlparse(href).path)
        dst = os.path.join(outdir, name)
        if os.path.exists(dst):
            print("have", name); continue
        print("downloading", name)
        urllib.request.urlretrieve(url, dst)
        print("  ->", os.path.getsize(dst) // 1_000_000, "MB")
    json.dump(item, open(os.path.join(outdir, "stac_item.json"), "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "search":
        search()
    else:
        get(sys.argv[2], sys.argv[3])
