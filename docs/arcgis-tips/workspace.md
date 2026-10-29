# Set up your workspace and project

On the lab machines, work on the **D: drive**. Not the C: drive, not the desktop, not a network
drive — and there are specific reasons for each:

- **C: is locked.** The lab administrators block writes to it because it holds the software
  installations and the system files. Anything you try to save there will fail, or vanish.
- **Network drives make ArcGIS Pro hang.** Your CAEDM home directory and similar network shares are
  writable, but ArcGIS Pro reads and writes very large files constantly, and doing that across a
  network connection is slow and will sometimes hang or crash ArcGIS Pro outright. Use them for backups,
  never as the place you work.
- **D: is local, fast and writable** — but it is shared with everyone who logs into that machine,
  and it may be wiped between semesters.

So:

1. **Make one folder for this class**, named after you, at the root of D:. For example
   `D:\Smith\`. Use your own name, not your instructor's.
2. **Make one folder per lab inside it**: `D:\Smith\Lab01\`, `D:\Smith\Lab02\`, and so on.
   Put the ArcGIS Pro project *and* the downloaded data for that lab in it.
3. **Back it up every time you leave the lab.** Copy your lab folder to the network or cloud
   storage of your choice — CAEDM, Google Drive, OneDrive or Box. Work that exists in only one
   place on a shared computer is work you are choosing to risk.

If you want your work to be portable between machines, a **high-speed USB 3.0 external drive** is
a legitimate alternative to D:. You can work directly off it — it is local to the machine while it
is plugged in — and take it with you. Still back it up.

> [!WARNING]
> **Never put a space in any folder or file name you create.** Use `D:\Smith\Lab01`, never
> `D:\John Smith\Lab 01`. Several geoprocessing tools — the raster analysis tools especially —
> fail or behave strangely on paths containing spaces, and the error message rarely tells you that
> the space is the problem. The same goes for the names you give output datasets: use
> `HighDensity_Tracts`, not `High Density Tracts`.


## Creating the project in the right place

In **New Project**, two things trip up almost everyone:

- **The Location box does not accept a typed path.** Click the folder button to its right and use
  the browse dialog. In that dialog, the *Name* box at the bottom *does* accept a full typed path,
  so you can paste `D:\Smith\Lab01` there and click OK.
- **Uncheck "Create a folder for this local project"** if you have already made your `Lab01`
  folder. Leaving it checked gives you `D:\Smith\Lab01\Lab01`, which is not what you want.
