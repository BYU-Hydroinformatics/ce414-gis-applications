"""Lab 7 (HAND flood mapping): flood-frequency flows -> stage -> HAND threshold.

Builds tools/lab07/stage_table.csv for USGS 10163000 PROVO RIVER AT PROVO, UT.

Sources (downloaded to C:/Ames/HAND/raw/ and cached; delete a file to refresh it):
  peaks.rdb   https://nwis.waterdata.usgs.gov/nwis/peak?site_no=10163000&agency_cd=USGS&format=rdb
  rating.rdb  https://waterdata.usgs.gov/nwisweb/get_ratings?site_no=10163000&file_type=exsa
  site.rdb    https://waterservices.usgs.gov/nwis/site/?format=rdb&sites=10163000&siteOutput=expanded

Method (a teaching approximation, NOT a published USGS estimate; StreamStats/GageStats
publishes no peak-flow statistics for this regulated gage):
  * Log-Pearson Type III, Bulletin 17B-style method of moments on log10 annual peaks, station
    skew only (no generalized-skew weighting, no low-outlier or historic adjustment).
  * Three record periods are computed (all systematic, post-Deer Creek, post-Jordanelle). They are
    NOT the lab's design flows: the lab uses FEMA's published FIS flows (period fema_fis_2026,
    design = True); the LP3 rows serve the "why do two 100-year floods differ?" question.
  * Flow -> gage height by the current USGS rating (exsa, rating 30.0): the first table row
    (0.01 ft steps) whose discharge is >= the flow, the rule students apply by hand. Above the rating's top (8.00 ft, 2,150 ft3/s) the
    top segment's power law Q = C (GH - 3.20)^b is extrapolated (flagged EXTRAPOLATED).
  * Elevation = gage datum (4,493.22 ft NAVD 88) + gage height.
  * HAND threshold h = gage height - 3.20 ft (the rating offset, about the gage height of zero
    flow), in meters; h_cm = h rounded to whole centimeters, the value the model iterates over.

Run with any Python 3 that has numpy + scipy (the ArcGIS Pro python does):
  "C:/Program Files/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe" tools/lab07/stage_table.py
"""
import csv
import json
import math
import os
import urllib.request

import numpy as np
from scipy import stats

RAW = r"C:\Ames\HAND\raw"
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "10163000"
URLS = {
    "peaks.rdb": f"https://nwis.waterdata.usgs.gov/nwis/peak?site_no={SITE}&agency_cd=USGS&format=rdb",
    "rating.rdb": f"https://waterdata.usgs.gov/nwisweb/get_ratings?site_no={SITE}&file_type=exsa",
    "site.rdb": f"https://waterservices.usgs.gov/nwis/site/?format=rdb&sites={SITE}&siteOutput=expanded",
}
RETURN_PERIODS = [2, 5, 10, 25, 50, 100]
FT = 0.3048
PERIODS = {
    "all_systematic": (1934, 2100, "WY 1934 on (all systematic peaks; every peak is coded 6, regulated)"),
    "post_deer_creek": (1942, 2100, "WY 1942 on (after Deer Creek Dam began storing, 1941)"),
    "post_jordanelle": (1993, 2100, "WY 1993 on (after Jordanelle Dam began storing, 1992-93)"),
}
DESIGN = "fema_fis_2026"  # instructor decision, Oct 9, 2026: the lab uses FEMA's published flows
# FEMA Flood Insurance Study, Utah County (49049CV001B, revised June 23, 2026), Table 9 Summary of
# Discharges, Provo River "3 miles above tie-in to Utah Lake", drainage area 673 mi2. Read from the
# PDF page image (page 53) on Oct 9, 2026. No 2- or 5-yr values are published; 500-yr = 0.2 %.
FEMA_FIS = {10: 1475, 25: 1810, 50: 2065, 100: 2325, 500: 2935}


def fetch(name):
    path = os.path.join(RAW, name)
    if not os.path.exists(path):
        os.makedirs(RAW, exist_ok=True)
        urllib.request.urlretrieve(URLS[name], path)
    return path


def rdb_rows(path):
    lines = [l.rstrip("\n") for l in open(path, encoding="utf-8", errors="ignore") if not l.startswith("#")]
    head = lines[0].split("\t")
    return [dict(zip(head, l.split("\t"))) for l in lines[2:] if l.strip()]


def rdb_comment(path, key):
    for l in open(path, encoding="utf-8", errors="ignore"):
        if key in l:
            return l.strip()
    return ""


def water_year(date):
    y, m = int(date[:4]), int(date[5:7] or 0)
    return y + 1 if m >= 10 else y


def lp3(q):
    x = np.log10(np.asarray(q, float))
    n = len(x)
    mean, sd = x.mean(), x.std(ddof=1)
    g = n * np.sum((x - mean) ** 3) / ((n - 1) * (n - 2) * sd ** 3)
    out = {}
    for t in RETURN_PERIODS:
        p = 1 - 1 / t  # non-exceedance
        k = stats.pearson3.ppf(p, g)  # standardized frequency factor for skew g
        out[t] = 10 ** (mean + k * sd)
    return {"n": n, "mean_log": mean, "sd_log": sd, "skew": g, "q": out}


def main():
    peaks = rdb_rows(fetch("peaks.rdb"))
    rating = rdb_rows(fetch("rating.rdb"))
    site = rdb_rows(fetch("site.rdb"))[0]
    datum_ft = float(site["alt_va"])
    offset_line = rdb_comment(os.path.join(RAW, "rating.rdb"), "RATING OFFSET1")
    offset = float(offset_line.split("=")[1])
    rating_id = rdb_comment(os.path.join(RAW, "rating.rdb"), "RATING ID")

    series = {}
    for r in peaks:
        if not r.get("peak_va"):
            continue
        wy = water_year(r["peak_dt"])
        series[wy] = float(r["peak_va"])
    gh = np.array([float(r["INDEP"]) for r in rating])
    q = np.array([float(r["DEP"]) for r in rating])
    # top-segment power law for extrapolation: fit on the top 0.5 ft of the table
    top = gh >= gh.max() - 0.5
    b, logc = np.polyfit(np.log(gh[top] - offset), np.log(q[top]), 1)

    def stage(flow):
        if flow <= q.max():
            # the rule students use: the first rating row whose discharge is >= the flow
            return float(gh[np.argmax(q >= flow)]), False
        return math.exp((math.log(flow) - logc) / b) + offset, True

    results = {}
    for key, (y0, y1, label) in PERIODS.items():
        vals = [v for wy, v in sorted(series.items()) if y0 <= wy <= y1]
        results[key] = lp3(vals) | {"label": label, "first_wy": min(w for w in series if w >= y0),
                                     "last_wy": max(series), "max_peak": max(vals)}

    results["fema_fis_2026"] = {"label": "FEMA FIS Utah County 2026, Table 9 (published, regulated)",
                                "q": FEMA_FIS}
    rows = []
    for key, res in results.items():
        for t in res["q"]:
            flow = res["q"][t]
            g, extrap = stage(flow)
            h_ft = g - offset
            rows.append({
                "period": key, "design": key == DESIGN, "return_period_yr": t, "aep_pct": round(100 / t, 1),
                "q_cfs": round(flow), "q_m3s": round(float(flow) * FT ** 3, 1),
                "gage_height_ft": round(g, 2), "elev_ft_navd88": round(datum_ft + g, 2),
                "elev_m_navd88": round((datum_ft + g) * FT, 3),
                "hand_h_ft": round(h_ft, 2), "hand_h_m": round(h_ft * FT, 3), "h_cm": int(round(h_ft * FT * 100)),
                "rating": "EXTRAPOLATED" if extrap else "within table",
                "source": "FEMA FIS 2026" if key == "fema_fis_2026" else "LP3 (this script)",
            })
    out = os.path.join(HERE, "stage_table.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    meta = {
        "site": SITE, "gage_datum_ft_navd88": datum_ft, "rating": rating_id, "rating_offset_ft": offset,
        "rating_top": {"gh_ft": float(gh.max()), "q_cfs": float(q.max())},
        "extrapolation": {"b": b, "C": math.exp(logc)},
        "n_peaks": len(series), "wy_range": [min(series), max(series)],
        "lp3": {k: {kk: (vv if kk != "q" else {str(t): round(x) for t, x in vv.items()})
                    for kk, vv in v.items()} for k, v in results.items()},
    }
    json.dump(meta, open(os.path.join(HERE, "stage_table_meta.json"), "w"), indent=2, default=float)
    print(json.dumps(meta, indent=1, default=float))
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
