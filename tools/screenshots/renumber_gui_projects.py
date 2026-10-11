"""Make renumbered copies of three ArcGIS Pro GUI projects so their captures show the current lab numbers.

  old C:/Ames/Lab08GUI  (Big Southern Butte, old Lab 8)  -> C:/Ames/Lab09GUI   Lab08.* -> Lab09.*
  old C:/Ames/Lab09GUI2 (Y Mountain interp, old Lab 9)   -> C:/Ames/Lab08GUI   Lab09.* -> Lab08.*
  old C:/Ames/Lab07GUI  (Avalanche, old Lab 7)           -> C:/Ames/Lab10GUI   Lab07.* -> Lab10.*

The existing C:/Ames/Lab09GUI (a first Y Mountain attempt) and C:/Ames/Lab08GUI (the Butte original)
are moved to C:/Ames/_old first. The .aprx and .atbx archives are zips of JSON/XML; every member is
rewritten with the project token replaced (case-sensitive: the data folders are lowercase and keep
their names). Nothing is run; ArcGIS Pro opens the copies afterwards.
"""
import os
import shutil
import sys
import zipfile

AMES = "C:/Ames"
OLD = AMES + "/_old"
SKIP_DIRS = {"GpMessages", "Index", "ImportLog", "caps", "__pycache__"}
SKIP_EXT = {".lock", ".ipynb"}


def rewrite_zip(src, dst, old, new):
    zin = zipfile.ZipFile(src)
    zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    n = 0
    for info in zin.infolist():
        data = zin.read(info.filename)
        if old.encode() in data:
            n += data.count(old.encode())
            data = data.replace(old.encode(), new.encode())
        name = info.filename.replace(old, new)
        zout.writestr(name, data, zipfile.ZIP_DEFLATED if info.compress_type else zipfile.ZIP_STORED)
    zin.close()
    zout.close()
    return n


def copy_project(src_dir, dst_dir, old, new):
    assert not os.path.exists(dst_dir), dst_dir
    os.makedirs(dst_dir)
    report = []
    for name in sorted(os.listdir(src_dir)):
        s = os.path.join(src_dir, name)
        if name in SKIP_DIRS or os.path.splitext(name)[1] in SKIP_EXT:
            continue
        d = os.path.join(dst_dir, name.replace(old, new))
        if os.path.isdir(s):
            shutil.copytree(s, d, ignore=shutil.ignore_patterns("*.lock"))
            report.append(f"  dir  {name} -> {os.path.basename(d)}")
        elif name.endswith((".aprx", ".atbx")):
            n = rewrite_zip(s, d, old, new)
            report.append(f"  zip  {name} -> {os.path.basename(d)}  ({n} replacements)")
        else:
            shutil.copy2(s, d)
            report.append(f"  file {name} -> {os.path.basename(d)}")
    return report


def main():
    os.makedirs(OLD, exist_ok=True)
    moves = [(AMES + "/Lab09GUI", OLD + "/Lab09GUI-ymountain-try1"), (AMES + "/Lab08GUI", OLD + "/Lab08GUI-butte")]
    for s, d in moves:
        if os.path.exists(s):
            assert not os.path.exists(d), d
            shutil.move(s, d)
            print("moved", s, "->", d)
    jobs = [
        (OLD + "/Lab08GUI-butte", AMES + "/Lab09GUI", "Lab08", "Lab09"),
        (AMES + "/Lab09GUI2", AMES + "/Lab08GUI", "Lab09", "Lab08"),
        (AMES + "/Lab07GUI", AMES + "/Lab10GUI", "Lab07", "Lab10"),
    ]
    for src, dst, old, new in jobs:
        print(f"{src} -> {dst}  ({old} -> {new})")
        for line in copy_project(src, dst, old, new):
            print(line)
    # leftover token check inside the new archives
    for dst, old in [(AMES + "/Lab09GUI/Lab09.aprx", "Lab08"), (AMES + "/Lab09GUI/Lab09.atbx", "Lab08"),
                     (AMES + "/Lab08GUI/Lab08.aprx", "Lab09"), (AMES + "/Lab08GUI/Lab08.atbx", "Lab09"),
                     (AMES + "/Lab10GUI/Lab10.aprx", "Lab07"), (AMES + "/Lab10GUI/Lab10.atbx", "Lab07")]:
        z = zipfile.ZipFile(dst)
        left = sum(z.read(i.filename).count(old.encode()) for i in z.infolist())
        print("leftover", old, "in", dst, ":", left)


if __name__ == "__main__":
    main()
