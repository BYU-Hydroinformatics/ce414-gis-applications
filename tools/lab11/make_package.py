r"""Lab 11 (Fire Response Coverage, Network Analyst): build the student data package.

    docs/data/lab11-fire-response.zip
      lab11-fire-response/
        FireResponse.gdb/
          Network/                      feature dataset, NAD 1983 UTM zone 12N
            Roads                       UGRC Utah Street Network edges inside Utah County (41,460)
            Utah_County_Roads_ND        the network dataset, BUILT, costs TravelMinutes (default) + Length
            Utah_County_Roads_ND_Junctions
          Fire_Stations                 UGRC FireStations, COUNTY = 'UTAH' (42)
          Census_Blocks                 UGRC CensusBlocks2020, COUNTYFP20 = '049' (10,092; PP_TOTAL = people)
        READ-ME-FIRST.txt

The network is UGRC's prebuilt Utah Street Network (gis.utah.gov/data/transportation/street-network-analysis/,
a statewide file geodatabase on Google Drive), clipped to Utah County and rebuilt from UGRC's own
network-dataset template, so the TravelMinutes cost (F_T_IMP_MIN / T_F_IMP_MIN per direction, with
one-way streets costed 100x in the wrong direction) is exactly UGRC's. Students never build a network.
The county boundary is NOT in the package: students download it from UGRC themselves (Data section).

    python make_package.py            builds C:\Ames\Lab11\build\, zips to docs/data/, writes package_info.json
ArcGIS Pro Python (3.7.1). Needs the UGRC gdb at UGRC_GDB (downloaded once; see download_network()).
"""
import datetime
import json
import os
import re
import shutil
import urllib.parse
import urllib.request
import zipfile

import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..", "..")
W = r"C:\Ames\Lab11\build"
PKG = os.path.join(W, "lab11-fire-response")
GDB = os.path.join(PKG, "FireResponse.gdb")
ZIP = os.path.join(REPO, "docs", "data", "lab11-fire-response.zip")
UGRC_ZIP_URL = "https://drive.usercontent.google.com/download?id=1NmMCS8HjxFPF-K6XjaV0FznhS0ejwqRc&export=download&confirm=t"
UGRC_DIR = r"C:\Ames\Lab11\ugrc_network"
UGRC_GDB = os.path.join(UGRC_DIR, "UtahRoadsNetworkAnalysis.gdb")
UGRC_ND = os.path.join(UGRC_GDB, "NetworkDataset", "UtahRoadsNetwork")
TEMPLATE = os.path.join(HERE, "ugrc_network_template.xml")      # kept in the repo: UGRC's ND definition
ND_NAME = "Utah_County_Roads_ND"
UTM = arcpy.SpatialReference(26912)
UGRC = "https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services"
COUNTY = "49049"
ROAD_FIELDS = ["FULLNAME", "CARTOCODE", "ONEWAY", "SPEED_LMT", "DOT_FCLASS", "DOT_HWYNAM", "ACCESSCODE", "VERT_LEVEL",
               "COUNTY_L", "COUNTY_R", "INCMUNI_L", "INCMUNI_R", "UPDATED", "UNIQUE_ID",
               "IMPED_MIN", "F_T_IMP_MIN", "T_F_IMP_MIN", "IMPED_PED", "NETSUBTYPE"]
LAYERS = {
    "Fire_Stations": ("FireStations", "COUNTY = 'UTAH'", "NAME,TELEPHONE,ADDRESS,CITY,STATE,ZIP,COUNTY,EMS"),
    "Census_Blocks": ("CensusBlocks2020", "COUNTYFP20 = '049'", "GEOID20,TRACTCE20,BLOCKCE20,ALAND20,AWATER20,PP_TOTAL,HU_TOTAL,HU_OCC,GQ_TOTAL"),
}
arcpy.env.overwriteOutput = True


def download_network():
    if arcpy.Exists(UGRC_ND):
        return
    os.makedirs(UGRC_DIR, exist_ok=True)
    z = os.path.join(UGRC_DIR, "UtahStreetNetwork.zip")
    print("downloading UGRC Utah Street Network (about 224 MB)...")
    urllib.request.urlretrieve(UGRC_ZIP_URL, z)
    zipfile.ZipFile(z).extractall(UGRC_DIR)


def post(url, params):
    with urllib.request.urlopen(url, urllib.parse.urlencode(params).encode(), timeout=300) as r:
        return json.load(r)


def fetch(name, svc, where, fields):
    """One UGRC feature service layer, by attribute query, into GDB\\name with UGRC_OID kept."""
    url = f"{UGRC}/{svc}/FeatureServer/0/query"
    oids = sorted(post(url, {"where": where, "returnIdsOnly": "true", "f": "json"}).get("objectIds") or [])
    fcs = []
    for i in range(0, len(oids), 400):
        d = post(url, {"objectIds": ",".join(map(str, oids[i:i + 400])), "outFields": "OBJECTID," + fields,
                       "returnGeometry": "true", "outSR": 26912, "f": "json"})
        d["fields"] = [f for f in d["fields"] if f["name"] != "UGRC_OID"] + [{"name": "UGRC_OID", "type": "esriFieldTypeInteger", "alias": "UGRC_OID"}]
        for ft in d["features"]:
            ft["attributes"]["UGRC_OID"] = ft["attributes"]["OBJECTID"]
        p = os.path.join(W, "raw", f"{name}_{i // 400:03d}.json")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        json.dump(d, open(p, "w"))
        fc = f"memory\\{name}_{i // 400}"
        arcpy.conversion.JSONToFeatures(p, fc)
        fcs.append(fc)
    out = os.path.join(GDB, name)
    arcpy.management.Merge(fcs, out)
    for f in arcpy.ListFields(out):
        if f.name.lower().startswith("shape__"):
            arcpy.management.DeleteField(out, f.name)
    return len(oids), int(arcpy.management.GetCount(out)[0])


def network():
    """Clip UGRC's edges to Utah County and rebuild the network from UGRC's own template, renamed."""
    arcpy.CheckOutExtension("Network")
    if not os.path.exists(TEMPLATE):
        arcpy.nax.CreateTemplateFromNetworkDataset(UGRC_ND, TEMPLATE)
    fd = os.path.join(GDB, "Network")
    arcpy.management.CreateFeatureDataset(GDB, "Network", UTM)
    src = os.path.join(UGRC_GDB, "NetworkDataset", "Roads")
    where = f"COUNTY_L = '{COUNTY}' OR COUNTY_R = '{COUNTY}'"
    # export every field (a field map drops the NETSUBTYPE subtypes the template's connectivity needs),
    # then delete the ones the lab does not use
    roads = os.path.join(fd, "Roads")
    arcpy.conversion.ExportFeatures(src, roads, where)
    drop = [f.name for f in arcpy.ListFields(roads) if not f.required and f.name not in ROAD_FIELDS]
    arcpy.management.DeleteField(roads, drop)
    arcpy.management.AddField(os.path.join(fd, "Roads"), "UGRC_OID", "LONG")
    # UGRC_OID = the source OBJECTID, matched through UNIQUE_ID
    ids = {r[0]: r[1] for r in arcpy.da.SearchCursor(src, ["UNIQUE_ID", "OID@"], where)}
    with arcpy.da.UpdateCursor(os.path.join(fd, "Roads"), ["UNIQUE_ID", "UGRC_OID"]) as cur:
        for row in cur:
            row[1] = ids.get(row[0])
            cur.updateRow(row)
    # the template names the network and its junctions after UGRC's; rename both for the package
    xml = open(TEMPLATE, encoding="utf-8").read()
    xml = xml.replace("UtahRoadsNetwork_Junctions", ND_NAME + "_Junctions").replace("<Name>UtahRoadsNetwork</Name>", f"<Name>{ND_NAME}</Name>")
    tmp = os.path.join(W, "nd_template.xml")
    open(tmp, "w", encoding="utf-8").write(xml)
    arcpy.nax.CreateNetworkDatasetFromTemplate(tmp, fd)
    nd = os.path.join(fd, ND_NAME)
    arcpy.nax.BuildNetwork(nd)
    d = arcpy.Describe(nd)
    oneway = int(arcpy.management.GetCount(arcpy.management.MakeFeatureLayer(os.path.join(fd, "Roads"), "ow", "ONEWAY IN ('1', '2')"))[0])
    return {"edges": int(arcpy.management.GetCount(os.path.join(fd, "Roads"))[0]),
            "junctions": int(arcpy.management.GetCount(os.path.join(fd, ND_NAME + "_Junctions"))[0]),
            "attributes": [(a.name, a.usageType, a.units) for a in d.attributes],
            "one_way_edges": oneway, "travel_modes": list(arcpy.nax.GetTravelModes(nd).keys())}


README = """READ ME FIRST: CE 414 Lab 11, Fire Response Coverage (Network Analysis)
========================================================================

Built {date} by tools/lab11/make_package.py in the course repository
(github.com/BYU-Hydroinformatics/ce414-gis-applications). Everything is in Utah County, Utah, in
NAD 1983 UTM zone 12N (EPSG 26912), meters.

FireResponse.gdb\\Network\\Utah_County_Roads_ND      the road network (a network dataset, already built)
  Source: UGRC's Utah Street Network dataset, gis.utah.gov/data/transportation/street-network-analysis/,
  a statewide network dataset UGRC derives from its Utah Roads layer and republishes monthly. We
  exported the {edges:,} road segments with Utah County on either side (COUNTY_L or COUNTY_R =
  '49049'; roads updated through {roads_updated}) and rebuilt the network from UGRC's own network
  template, so its definition is UGRC's, not ours:
    TravelMinutes  (cost, minutes, the default)  minutes to drive the segment, taken from the fields
                   F_T_IMP_MIN (in the direction the line was digitized) and T_F_IMP_MIN (against it).
                   UGRC estimated them from the posted speed limit (SPEED_LMT) and the road class
                   (CARTOCODE), and multiplied surface-street times by 1.5 for signals and congestion.
                   On a one-way street (ONEWAY = 1 or 2) the wrong direction costs 100 times the right
                   one: a penalty, not a restriction. {one_way:,} segments are one-way.
    Length         (cost, meters)
  No turns, no elevation fields (overpasses connect where endpoints coincide) and no live traffic.
  UGRC's note on its own travel times: "based on typical network travel, and not the expedited
  travel of emergency response vehicles."
  Roads keeps these UGRC fields: {road_fields}, and UGRC_OID (the segment's OBJECTID in UGRC's
  network geodatabase). NETSUBTYPE (1 limited access and ramps, 2 other) is the subtype the network's
  connectivity rules are written on; leave it alone.

FireResponse.gdb\\Fire_Stations      {stations} points
  UGRC FireStations (gis.utah.gov/products/sgid/society/fire-stations/), COUNTY = 'UTAH'. Fields NAME,
  TELEPHONE, ADDRESS, CITY, STATE, ZIP, COUNTY, EMS (Y / N / blank), UGRC_OID. The layer's own
  description says "Last Update: September 22, 2022". It includes every station the layer lists,
  including Camp Williams (a military post) and the Utah Fire and Rescue Academy at UVU.

FireResponse.gdb\\Census_Blocks      {blocks:,} polygons, {pop:,} people
  UGRC CensusBlocks2020 (2020 Decennial Census blocks with population), COUNTYFP20 = '049'. Fields
  GEOID20, TRACTCE20, BLOCKCE20, ALAND20 and AWATER20 (m2), PP_TOTAL (people),
  HU_TOTAL and HU_OCC (housing units, occupied), GQ_TOTAL (group quarters), UGRC_OID.

What we did: read each layer from its UGRC feature service on {date}, kept the fields above, and
rebuilt the network for the county. Field values were not changed. What we did not do: nothing was
filtered beyond the county; every station and every block in the county is here.

Not in the package: the Utah County boundary. Download it yourself from UGRC (the Data section says
where); it is the one layer you fetch live, and its metadata page is part of the lab.

License: UGRC publishes its data under a Creative Commons Attribution license; credit "Utah
Geospatial Resource Center (UGRC)" on your maps. Census counts are from the U.S. Census Bureau.
"""


def main():
    download_network()
    if os.path.exists(W):
        shutil.rmtree(W)
    os.makedirs(PKG)
    arcpy.management.CreateFileGDB(PKG, "FireResponse.gdb")
    info = {"built": datetime.date.today().isoformat()}
    info["network"] = network()
    info["roads_updated"] = max(r[0] for r in arcpy.da.SearchCursor(os.path.join(GDB, "Network", "Roads"), ["UPDATED"]) if r[0]).strftime("%B %d, %Y")
    for name, (svc, where, fields) in LAYERS.items():
        info[name] = fetch(name, svc, where, fields)
        print(name, info[name])
    info["population"] = int(sum(r[0] or 0 for r in arcpy.da.SearchCursor(os.path.join(GDB, "Census_Blocks"), ["PP_TOTAL"])))
    open(os.path.join(PKG, "READ-ME-FIRST.txt"), "w", encoding="utf-8").write(README.format(
        date=datetime.date.today().strftime("%B %d, %Y"), edges=info["network"]["edges"], roads_updated=info["roads_updated"],
        one_way=info["network"]["one_way_edges"], road_fields=", ".join(ROAD_FIELDS), stations=info["Fire_Stations"][1],
        blocks=info["Census_Blocks"][1], pop=info["population"]))
    arcpy.management.Compact(GDB)
    os.makedirs(os.path.dirname(ZIP), exist_ok=True)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(PKG):
            for f in files:
                if f.endswith(".lock"):
                    continue
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, W))
    info["zip_bytes"] = os.path.getsize(ZIP)
    json.dump(info, open(os.path.join(HERE, "package_info.json"), "w"), indent=1, default=str)
    print(json.dumps(info, indent=1, default=str))


if __name__ == "__main__":
    main()
