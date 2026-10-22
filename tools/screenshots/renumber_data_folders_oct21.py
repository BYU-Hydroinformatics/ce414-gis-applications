"""Follow-up to renumber_gui_projects_oct21.py: rename the lowercase data folders to the zip names.

copy_project replaces the project token case-sensitively, so the data folders shipped inside each GUI
project (and the arcpy reference runs) kept their old lowercase names. The student zips now unpack to
lab10-power-line, lab11-fire-response and lab12-little-cottonwood-dem, and captures that show a data
path should match. Each folder is renamed and every member of the project's .aprx/.atbx is rewritten.

    python renumber_data_folders_oct21.py          # dry run
    python renumber_data_folders_oct21.py --go
"""
import os
import shutil
import sys

from renumber_gui_projects import AMES, rewrite_zip

JOBS = [  # project folder, old data folder, new data folder
    ("Lab10GUI", "lab11-power-line", "lab10-power-line"),
    ("Lab11GUI", "lab12-fire-response", "lab11-fire-response"),
    ("Lab12GUI", "lab07-little-cottonwood-dem", "lab12-little-cottonwood-dem"),
    ("Lab10/ref", "lab11-power-line", "lab10-power-line"),
    ("Lab11/ref", "lab12-fire-response", "lab11-fire-response"),
]


def main(go):
    for proj, old, new in JOBS:
        root = f"{AMES}/{proj}"
        src, dst = f"{root}/{old}", f"{root}/{new}"
        if not os.path.exists(src):
            print("missing (skipped):", src)
            continue
        assert not os.path.exists(dst), dst
        print("rename", src, "->", dst)
        if go:
            os.rename(src, dst)
        for name in os.listdir(root):
            if name.endswith((".aprx", ".atbx")):
                path = f"{root}/{name}"
                tmp = path + ".tmp"
                if go:
                    n = rewrite_zip(path, tmp, old, new)
                    shutil.move(tmp, path)
                    print(f"  {name}: {n} replacements")
                else:
                    print("  would rewrite", name)
    if not go:
        print("\nDry run. Close ArcGIS Pro, then run again with --go.")


if __name__ == "__main__":
    main("--go" in sys.argv)
