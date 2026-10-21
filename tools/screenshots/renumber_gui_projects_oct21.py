"""Second lab renumbering (October 21, 2026): rename the Windows working folders to the new numbers.

  Least Cost Path   old Lab 11 -> Lab 10    C:/Ames/Lab11GUI -> Lab10GUI   Lab11.* -> Lab10.*
  Network Analysis  old Lab 12 -> Lab 11    C:/Ames/Lab12GUI -> Lab11GUI   Lab12.* -> Lab11.*
  Avalanche Hazard  old Lab 10 -> Lab 12    C:/Ames/Lab10GUI -> Lab12GUI   Lab10.* -> Lab12.*

The three numbers rotate, so every source is first moved to C:/Ames/_old/<name>-oct21 and the
renamed copies are made from there (copy_project rewrites the token inside the .aprx and .atbx
archives, as the October 10 script did). The arcpy reference-run folders C:/Ames/Lab10, Lab11 and
Lab12 hold no project token, so they are only renamed. Nothing is run; open each copy in ArcGIS Pro
afterwards, then re-shoot the captures marked TODO(recapture) in docs/assignments/lab-1[012]/.

    python renumber_gui_projects_oct21.py          # dry run: print what would move
    python renumber_gui_projects_oct21.py --go
"""
import os
import shutil
import sys

from renumber_gui_projects import AMES, OLD, copy_project

ROTATE = {"10": "12", "11": "10", "12": "11"}


def main(go):
    os.makedirs(OLD, exist_ok=True)
    # 1. move every source aside, so no destination exists yet
    staged = {}
    for old in ROTATE:
        for kind in ("GUI", ""):
            src = f"{AMES}/Lab{old}{kind}"
            if not os.path.exists(src):
                print("missing (skipped):", src)
                continue
            dst = f"{OLD}/Lab{old}{kind}-oct21"
            assert not os.path.exists(dst), dst
            print("move", src, "->", dst)
            if go:
                shutil.move(src, dst)
            staged[(old, kind)] = dst
    # 2. renamed copies (GUI projects) and plain renames (reference runs)
    for (old, kind), src in staged.items():
        new = ROTATE[old]
        dst = f"{AMES}/Lab{new}{kind}"
        if kind == "GUI":
            print(f"copy {src} -> {dst}  (Lab{old} -> Lab{new})")
            if go:
                for line in copy_project(src, dst, f"Lab{old}", f"Lab{new}"):
                    print(line)
        else:
            print("rename", src, "->", dst)
            if go:
                shutil.move(src, dst)
    if not go:
        print("\nDry run. Close ArcGIS Pro, then run again with --go.")


if __name__ == "__main__":
    main("--go" in sys.argv)
