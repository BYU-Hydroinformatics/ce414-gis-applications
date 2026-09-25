"""Fetch the Utah records of the FCC-derived "Cellular Towers in the United States (Archive)"
feature layer (HIFLD, last data update 2024-07-06) and save them as GeoJSON for make_extract.py.

Item:   https://www.arcgis.com/home/item.html?id=15dabb4108254481b591018be2598f3c
Layer:  .../Cellular_Towers_in_the_United_States_view/FeatureServer/0

Run with the ArcGIS Pro Python:
    "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" tools/lab04/fetch_towers.py
"""
import json, urllib.parse, urllib.request, pathlib, datetime

LAYER = ("https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/"
         "Cellular_Towers_in_the_United_States_view/FeatureServer/0")
OUT = pathlib.Path(r"C:\Ames\Lab04\Data\hifld_towers_UT.geojson")


def query(**kw):
    q = dict(f="geojson", outFields="*", where="LocState='UT'", outSR=4326,
             resultRecordCount=2000)
    q.update(kw)
    url = LAYER + "/query?" + urllib.parse.urlencode(q)
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.load(r)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fc = query()
    n = len(fc["features"])
    fc["retrieved"] = datetime.date.today().isoformat()
    OUT.write_text(json.dumps(fc))
    print(f"{n} Utah records -> {OUT}")


if __name__ == "__main__":
    main()
