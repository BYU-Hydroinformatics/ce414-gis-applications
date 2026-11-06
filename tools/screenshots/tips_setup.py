"""Build D:\\Smith\\Tips\\Tips.aprx, the project the ArcGIS Tips dialog captures are taken in.

Copies the inputs the captures need from the GUI-build geodatabases into Tips.gdb and makes one
map per theme, so every dialog in tools/screenshots/arcgis-tips-shot-list.md (Session A) has its
input already in the Contents pane. D: is a `subst` of C:\\Ames\\TipsD for the session.

    propy.bat tools\\screenshots\\tips_setup.py
"""
import os
import arcpy

HOME = r"D:\Smith\Tips"
GDB = os.path.join(HOME, "Tips.gdb")
SRC_APRX = r"D:\Smith\Lab02\Lab02.aprx"

COPIES = [  # (source, name in Tips.gdb, map)
    (r"C:\Ames\Lab01\Lab01.gdb\Counties_Select", "UtahCounty", "Vector"),
    (r"C:\Ames\Lab01\Lab01.gdb\Tracts_UtahCounty", "Tracts_UtahCounty", "Vector"),
    (r"C:\Ames\Lab01\Lab01.gdb\MajorRoads_UtahCounty", "MajorRoads_UtahCounty", "Vector"),
    (r"C:\Ames\Lab01\Lab01.gdb\Walmarts_UtahCounty", "Walmarts_UtahCounty", "Vector"),
    (r"C:\Ames\Lab01\Lab01.gdb\Roads_UtahCounty", "Roads_UtahCounty", "Vector"),
    (r"C:\Ames\Lab05GUI\Lab05.gdb\DEM_UTM", "RockCanyon_DEM", "Watershed"),
    (r"C:\Ames\Lab05GUI\Lab05.gdb\Flow_Directiond8", "Flow_Direction", "Watershed"),
    (r"C:\Ames\Lab05GUI\Lab05.gdb\Outlet", "Outlet", "Watershed"),
    (r"C:\Ames\Lab08GUI\lab09-y-mountain\Lab08.gdb\Sample_Points_250", "Sample_Points_250", "Interpolation"),
    (r"C:\Ames\Lab08GUI\lab09-y-mountain\Lab08.gdb\Study_Area", "Study_Area", "Interpolation"),
    (r"C:\Ames\Lab08GUI\lab09-y-mountain\Lab08.gdb\True_DEM", "True_DEM", "Interpolation"),
]
FILES = [  # raw files added to a map straight from disk
    (r"C:\Ames\Lab04GUI\Data\DEM\USGS_1_n40w112.tif", "DEM"),
    (r"C:\Ames\Lab04GUI\Data\DEM\USGS_1_n40w113.tif", "DEM"),
    (r"D:\Smith\Lab02\Data\UtahCounty_NIR_B5_SR_x10000.tif", "Rasters"),
    (r"D:\Smith\Lab02\Data\UtahCounty_Red_B4_SR_x10000.tif", "Rasters"),
]


def main():
    os.makedirs(HOME, exist_ok=True)
    if not arcpy.Exists(GDB):
        arcpy.management.CreateFileGDB(HOME, "Tips.gdb")
    for src, name, _ in COPIES:
        out = os.path.join(GDB, name)
        if arcpy.Exists(out):
            continue
        if not arcpy.Exists(src):
            print("MISSING", src)
            continue
        print("copy", name)
        arcpy.management.Copy(src, out)

    aprx_path = os.path.join(HOME, "Tips.aprx")
    arcpy.mp.ArcGISProject(SRC_APRX).saveACopy(aprx_path)
    aprx = arcpy.mp.ArcGISProject(aprx_path)
    aprx.homeFolder = HOME
    aprx.defaultGeodatabase = GDB
    for lay in aprx.listLayouts():
        aprx.deleteItem(lay)
    for m in aprx.listMaps():
        aprx.deleteItem(m)

    maps = {}
    for _, _, mname in COPIES:
        maps.setdefault(mname, None)
    for _, mname in FILES:
        maps.setdefault(mname, None)
    for mname in maps:
        m = aprx.createMap(mname)
        for lyr in m.listLayers():  # createMap adds a basemap
            m.removeLayer(lyr)
        maps[mname] = m
    for _, name, mname in COPIES:
        path = os.path.join(GDB, name)
        if arcpy.Exists(path):
            maps[mname].addDataFromPath(path)
    for path, mname in FILES:
        maps[mname].addDataFromPath(path)
    aprx.save()
    print("saved", aprx_path, [m.name for m in aprx.listMaps()])


if __name__ == "__main__":
    main()
