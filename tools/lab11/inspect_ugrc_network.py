import arcpy, os, json
gdb = r"C:/Ames/Lab11/ugrc_network/UtahRoadsNetworkAnalysis.gdb"
arcpy.env.workspace = gdb
print("FDS:", arcpy.ListDatasets("*", "Feature"))
print("FCs root:", arcpy.ListFeatureClasses())
print("Tables:", arcpy.ListTables())
for fd in arcpy.ListDatasets("*", "Feature") or []:
    print("== FD", fd, arcpy.Describe(os.path.join(gdb, fd)).spatialReference.name)
    print("  FCs:", arcpy.ListFeatureClasses(feature_dataset=fd))
    print("  NDs:", arcpy.ListDatasets("*", "Network") )
    for c in arcpy.Describe(os.path.join(gdb, fd)).children:
        print("  child", c.name, c.dataType)
        if c.dataType == "NetworkDataset":
            nd = c
            print("   buildTime/state:", getattr(nd, "isBuildable", None), nd.networkType, "edges", nd.edgeSources and [e.name for e in nd.edgeSources], "junctions", [j.name for j in nd.junctionSources], "turns", [t.name for t in nd.turnSources])
            pass
            print("   elevation model:", nd.elevationModel)
            for a in nd.attributes:
                print("   attr:", a.name, a.usageType, a.units, a.dataType, "useByDefault", a.useByDefault)
            try:
                tms = arcpy.nax.GetTravelModes(os.path.join(gdb, fd, nd.name))
                for k, tm in tms.items(): print("   travel mode:", k, "| impedance", tm.impedance, "| timeAttr", tm.timeAttributeName, "| distAttr", tm.distanceAttributeName, "| restrictions", list(tm.restrictions))
            except Exception as e: print("   travel modes ERR", e)
        elif c.dataType == "FeatureClass":
            print("   count", arcpy.management.GetCount(os.path.join(gdb, fd, c.name))[0], "fields", [f.name for f in c.fields][60:])
roads = os.path.join(gdb, "NetworkDataset", "Roads")
fl = [f.name for f in arcpy.ListFields(roads)]
print("IMP fields:", [f for f in fl if "IMP" in f or "MIN" in f or "LEN" in f.upper()])
with arcpy.da.SearchCursor(roads, ["UPDATED"], "COUNTY_L = '49049'", sql_clause=(None, "ORDER BY UPDATED DESC")) as cur:
    print("latest UPDATED in Utah County:", next(cur))
print("Utah County roads in ND:", arcpy.management.GetCount(arcpy.management.MakeFeatureLayer(roads, "r", "COUNTY_L = '49049' OR COUNTY_R = '49049'"))[0])
with arcpy.da.SearchCursor(roads, ["F_T_IMP_MIN","T_F_IMP_MIN","SPEED_LMT","CARTOCODE","Shape_Length"], "COUNTY_L = '49049'") as cur:
    rows = [r for r in cur]
import statistics
ft = [r[0] for r in rows if r[0] is not None]
print("rows", len(rows), "F_T_IMP_MIN none:", sum(1 for r in rows if r[0] is None), "min/med/max", min(ft), statistics.median(ft), max(ft))
print("sample:", rows[:5])
