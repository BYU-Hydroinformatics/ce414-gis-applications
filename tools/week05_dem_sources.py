"""Week 5 "Where to download one" figures (slides/week-05/elevation-data-lidar.md, Part 3).

Subcommands
  ladder      ed-dem-resolution-ladder.png - the same 6 km x 6 km square above BYU (Y Mountain,
              Rock Canyon, Squaw Peak) as hillshade from four REAL distributed products:
                SRTM GL3 (3 arc-second)      OpenTopography public bucket (NASA SRTM v3 GL3)
                3DEP 1 arc-second (current)  prd-tnm.s3.amazonaws.com StagedProducts/Elevation/1
                3DEP 1/3 arc-second (current) prd-tnm ... /Elevation/13
                3DEP 1 m (UT Central QL1 2018 project tile x44y446)
              Each is read by HTTP range request (/vsicurl/), warped nearest-neighbor into
              NAD83 / UTM 12N at its own native north-south cell size, hillshaded (az 315, alt 45).
  captures    headless-Chromium page captures (ed-srtm-official, ed-aster-official, ed-jaxa-aw3d30)
  tnm         TNM Downloader walk-through captures (ed-tnm-step1..4)
  planetary   ed-planetary-dems.png (Mars MOLA, Moon LOLA hillshades)

Run with a Python that has rasterio, pyproj, numpy, matplotlib, pillow, playwright.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / 'slides' / 'week-05' / 'images'
UTM = 'EPSG:26912'
BOX = (445700, 4454900, 448700, 4457900)       # xmin, ymin, xmax, ymax  (3 km square, NAD83 UTM 12N)
# point locations from OpenStreetMap (Nominatim), projected to UTM 12N; label text offset in meters
LABELS = [('Rock Canyon trailhead', 446372, 4457365, 380, 260), ('Y Mountain summit', 448407, 4456450, -700, 260),
          ('Y trailhead', 446657, 4455118, 0, 260)]

PRODUCTS = [
    ('~90 m', 'SRTM 3 arc-second', 'NASA SRTM, flown Feb 2000',
     '/vsicurl/https://opentopography.s3.sdsc.edu/raster/SRTM_GL3/SRTM_GL3_srtm/North/North_30_60/N40W112.tif'),
    ('~30 m', '3DEP 1 arc-second', 'USGS 3DEP seamless (current)',
     '/vsicurl/https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current/n41w112/USGS_1_n41w112.tif'),
    ('~10 m', '3DEP 1/3 arc-second', 'USGS 3DEP seamless (current)',
     '/vsicurl/https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/n41w112/USGS_13_n41w112.tif'),
    ('1 m', '3DEP 1 meter (lidar)', '3DEP lidar projects, 2013 + 2018',
     ['/vsicurl/https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/UT_Wasatch_L3_2013/'
      'TIFF/USGS_one_meter_x44y446_UT_Wasatch_L3_2013.tif',
      '/vsicurl/https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/UT_Central_QL1_B2_2018/'
      'TIFF/USGS_one_meter_x44y446_UT_Central_QL1_B2_2018.tif']),
]


def hillshade(z, cell, az=315.0, alt=45.0):
    gy, gx = np.gradient(z, cell)            # rows increase southward
    slope = np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)             # downslope direction, clockwise from north
    azr, altr = np.radians(az), np.radians(alt)
    hs = np.sin(altr) * np.cos(slope) + np.cos(altr) * np.sin(slope) * np.cos(azr - aspect)
    return np.clip(hs, 0, 1)


def read_native(src_path):
    """Read the product's own cells covering BOX (no resampling). Returns z, extent, dx, dy (m), geographic?"""
    import rasterio
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR'):
        with rasterio.open(src_path) as src:
            geo = src.crs.is_geographic
            b = transform_bounds(UTM, src.crs, *BOX, densify_pts=21) if geo else BOX
            pad = 2 * abs(src.res[1])
            win = from_bounds(b[0] - pad, b[1] - pad, b[2] + pad, b[3] + pad,
                              src.transform).round_offsets().round_lengths()
            z = src.read(1, window=win).astype('float64')
            t = src.window_transform(win)
            if src.nodata is not None:
                z[z == src.nodata] = np.nan
    ext = (t.c, t.c + t.a * z.shape[1], t.f + t.e * z.shape[0], t.f)
    if geo:
        lat = np.radians((ext[2] + ext[3]) / 2)
        dx, dy = abs(t.a) * 111320.0 * np.cos(lat), abs(t.e) * 111320.0
    else:
        dx, dy = abs(t.a), abs(t.e)
    return z, ext, dx, dy, geo


def hillshade_xy(z, dx, dy, az=315.0, alt=45.0):
    gy, gx = np.gradient(z, dy, dx)
    gy = -gy                                 # rows run south; make gy the northward gradient
    slope = np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, -gy)            # downslope azimuth, clockwise from north
    azr, altr = np.radians(az), np.radians(alt)
    hs = np.sin(altr) * np.cos(slope) + np.cos(altr) * np.sin(slope) * np.cos(azr - aspect)
    return np.clip(hs, 0, 1)


def ladder():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from pyproj import Transformer
    from rasterio.warp import transform_bounds
    gb = transform_bounds(UTM, 'EPSG:4269', *BOX, densify_pts=21)
    coslat = np.cos(np.radians((gb[1] + gb[3]) / 2))
    fig, axes = plt.subplots(1, 4, figsize=(15, 5.2))
    fig.subplots_adjust(left=0.008, right=0.992, top=0.83, bottom=0.075, wspace=0.035)
    for ax, (label, prod, lineage, path) in zip(axes, PRODUCTS):
        paths = path if isinstance(path, list) else [path]
        z, ext, dx, dy, geo = read_native(paths[0])
        for extra in paths[1:]:              # fill the first lidar project's gaps from the next
            z2 = read_native(extra)[0]
            z = np.where(np.isnan(z), z2, z)
        hs = hillshade_xy(z, dx, dy)
        print(f'{prod}: cells {dx:.1f} x {dy:.1f} m, array {z.shape}, NaN {int(np.isnan(z).sum())}, '
              f'z {np.nanmin(z):.0f}-{np.nanmax(z):.0f} m')
        ax.imshow(hs, cmap='gray', vmin=0, vmax=1, extent=ext,
                  interpolation='antialiased' if dx < 5 else 'nearest')
        if geo:
            ax.set_xlim(gb[0], gb[2]); ax.set_ylim(gb[1], gb[3]); ax.set_aspect(1 / coslat)
        else:
            ax.set_xlim(BOX[0], BOX[2]); ax.set_ylim(BOX[1], BOX[3]); ax.set_aspect(1)
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color('#444')
        ax.set_title(f'{label}\n{prod}', fontsize=15, fontweight='bold', loc='left', pad=6)
        ax.text(0.0, -0.03, lineage, transform=ax.transAxes, ha='left', va='top', fontsize=10.5, color='#333')
        if not geo:
            for name, x, y, ox, oy in LABELS:
                ax.plot(x, y, 'o', ms=6, mfc='#b5121b', mec='white', mew=1.2)
                ax.annotate(name, (x, y), (x + ox, y + oy), fontsize=10, color='white', ha='center', va='center',
                            bbox=dict(boxstyle='round,pad=0.2', fc='#b5121b', alpha=0.9, lw=0))
    fig.text(0.008, 0.955, f'The same {int((BOX[2]-BOX[0])/1000)} km x {int((BOX[3]-BOX[1])/1000)} km '
             'square east of BYU in Provo, Utah (Rock Canyon and Y Mountain), from four real DEM products (hillshade, sun from the northwest)',
             fontsize=12.5, color='#222', ha='left')
    out = IMG / 'ed-dem-resolution-ladder.png'
    fig.savefig(out, dpi=150, facecolor='white')
    print('wrote', out)


# ---------------------------------------------------------------- page captures
HIDE_CSS = """
#onetrust-banner-sdk, .usa-banner, [id*=cookie i], [class*=cookie i], [class*=consent i],
[id*=consent i], .fsrDeclineButton, #fsrInvite, .fsrAbandonButton {display:none !important;}
"""


def shot(page, url, out, wait=3000, full=False, clip=None, scroll=0):
    page.goto(url, wait_until='networkidle', timeout=90000)
    page.add_style_tag(content=HIDE_CSS)
    # drop site-wide alert banners unrelated to the page (e.g., Earthdata's mission-news strip)
    page.evaluate('''() => { for (const el of document.querySelectorAll('div,section,aside')) {
        const t = (el.innerText || '');
        if (/Suomi NPP|data announcement/i.test(t) && el.getBoundingClientRect().top < 5 &&
            el.getBoundingClientRect().height < 120) { el.remove(); } } }''')
    page.wait_for_timeout(wait)
    if scroll:
        page.mouse.wheel(0, scroll)
        page.wait_for_timeout(1000)
    page.screenshot(path=str(out), full_page=full, clip=clip)
    print('wrote', out, '|', page.title())


def captures(which=None):
    from playwright.sync_api import sync_playwright
    jobs = {
        'srtm': ('https://www.earthdata.nasa.gov/data/instruments/srtm', 'ed-srtm-official.png'),
        'aster': ('https://www.earthdata.nasa.gov/data/catalog/lpcloud-astgtm-003', 'ed-aster-official.png'),
        'jaxa': ('https://www.eorc.jaxa.jp/ALOS/en/dataset/aw3d30/aw3d30_e.htm', 'ed-jaxa-aw3d30.png'),
    }
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1600, 'height': 1000})
        for k, (url, name) in jobs.items():
            if which and k not in which:
                continue
            shot(pg, url, IMG / name)
        b.close()


# first line of visible text around a checkbox (the TNM checkboxes carry no accessible label)
LABEL_JS = r"""x => { let a = x; while (a && !(a.innerText || '').trim()) a = a.parentElement;
  return a ? a.innerText.trim().split(/\n/)[0].trim() : ''; }"""


def tnm():
    """Walk the real TNM Downloader: Datasets -> 3DEP 1/3 arc-second -> Provo extent -> Search -> results.
    Every screenshot is of the live application; nothing is composited."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1600, 'height': 1000})
        pg.goto('https://apps.nationalmap.gov/downloader/', wait_until='networkidle', timeout=120000)
        pg.wait_for_timeout(4000)
        close = pg.get_by_role('button', name='Close banner')
        if close.count():
            close.first.click()                  # site notice strip, not part of the workflow
            pg.wait_for_timeout(800)
        pg.screenshot(path=str(IMG / 'ed-tnm-step1.png'))
        print('step1 written')

        # step 2: check Elevation Products (3DEP); the app pre-selects 1/3 arc-second DEM
        def box_for(text):
            for e in pg.query_selector_all('input[type=checkbox]'):
                lab = e.evaluate(LABEL_JS)
                if lab == text and e.is_visible():
                    return e
            raise RuntimeError('no checkbox ' + text)
        box_for('Elevation Products (3D Elevation Program Products and Services)').click()
        pg.wait_for_timeout(2500)
        print('1/3 arc-second DEM checked:', box_for('1/3 arc-second DEM').is_checked())
        # narrow 1/3 arc-second to the Current seamless tile (not every historical edition)
        order = [(e, e.evaluate(LABEL_JS)) for e in pg.query_selector_all('input[type=checkbox]') if e.is_visible()]
        k = [lab for _, lab in order].index('1/3 arc-second DEM')
        cur = next(e for e, lab in order[k + 1:] if lab == 'Current')
        cur.click()
        pg.wait_for_timeout(1000)
        print('Current checked:', cur.is_checked())
        pg.wait_for_timeout(500)
        pg.screenshot(path=str(IMG / 'ed-tnm-step2.png'))
        print('step2 written')

        # step 3: zoom the map to Provo with the map's own place search; AOI = Map Extent
        box = pg.get_by_placeholder('Find address or place')
        box.click()
        box.fill('Provo, Utah')
        pg.wait_for_timeout(2500)
        box.press('Enter')
        pg.wait_for_timeout(8000)
        popup_close = pg.locator('.esri-popup__button--close, .esri-features__header calcite-action[icon=x], calcite-action[text=Close]')
        if popup_close.count():
            try:
                popup_close.first.click(timeout=3000)
            except Exception as ex:
                print('popup close failed', ex)
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(1500)
        pg.screenshot(path=str(IMG / 'ed-tnm-step3.png'))
        print('step3 written')

        # step 4: Search Products -> Products tab lists results
        pg.get_by_role('button', name='Search Products').click()
        pg.wait_for_timeout(15000)
        pg.get_by_text('Footprint', exact=True).first.click()   # outline the tile on the map
        pg.wait_for_timeout(1500)
        for _ in range(3):                   # zoom out so the whole 1 x 1 degree tile shows
            pg.get_by_role('button', name='Zoom out').first.click()
            pg.wait_for_timeout(1500)
        pg.wait_for_timeout(3000)
        pg.screenshot(path=str(IMG / 'ed-tnm-step4.png'))
        print('step4 written')
        txt = pg.inner_text('body')
        i = txt.find('Products')
        print(txt[:4000])
        b.close()


PLANETS = [
    # title, subtitle, url, sphere radius (m), center lon/lat (deg), half-width (deg), decimation, z-factor
    ('Mars: Olympus Mons', 'MGS MOLA DEM, 463 m cells (shown every 4th cell), 5x vertical',
     'https://planetarymaps.usgs.gov/mosaic/Mars_MGS_MOLA_DEM_mosaic_global_463m.tif',
     3396190.0, (-133.8, 18.4), 11.0, 4, 5.0),
    ('Moon: Copernicus crater', 'LRO LOLA DEM, 118 m cells, 2x vertical',
     'https://planetarymaps.usgs.gov/mosaic/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif',
     1737400.0, (-20.1, 9.6), 2.6, 1, 2.0),
]


def planetary():
    """Two hillshades read by HTTP range request from the USGS Astrogeology global mosaics.
    Only the rows needed are fetched; nothing is downloaded whole."""
    import math
    import rasterio
    from rasterio.windows import from_bounds
    from rasterio.enums import Resampling
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.4))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.82, bottom=0.03, wspace=0.04)
    for ax, (title, sub, url, R, (lon, lat), hw, dec, zf) in zip(axes, PLANETS):
        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', GDAL_HTTP_MULTIRANGE='YES',
                          CPL_VSIL_CURL_CHUNK_SIZE='1048576'):
            with rasterio.open('/vsicurl/' + url) as src:
                k = math.pi / 180 * R          # meters per degree along the equirectangular axes
                # the projection's x scale is R*cos(lat_ts); read lat_ts from the WKT (0 for these two)
                x0, x1 = (lon - hw) * k, (lon + hw) * k
                y0, y1 = (lat - hw) * k, (lat + hw) * k
                win = from_bounds(x0, y0, x1, y1, src.transform).round_offsets().round_lengths()
                shape = (int(win.height // dec), int(win.width // dec))
                z = src.read(1, window=win, out_shape=shape, resampling=Resampling.nearest).astype('float64')
                z[z == src.nodata] = np.nan
                z *= src.scales[0]
                cell = abs(src.res[0]) * dec
        dx = cell * math.cos(math.radians(lat))    # true east-west spacing at this latitude
        hs = hillshade_xy(z * zf, dx, cell)
        print(f'{title}: window {win.width}x{win.height}, read {shape}, cell {cell:.0f} m, '
              f'z {np.nanmin(z):.0f} to {np.nanmax(z):.0f} m')
        ext = (lon - hw, lon + hw, lat - hw, lat + hw)
        ax.imshow(hs, cmap='gray', vmin=0, vmax=1, extent=ext, interpolation='antialiased')
        ax.set_aspect(1 / math.cos(math.radians(lat)))
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f'{title}\n', fontsize=16, fontweight='bold', loc='left', pad=4)
        ax.text(0, 1.015, sub, transform=ax.transAxes, fontsize=11.5, color='#333', va='bottom')
        km = 2 * hw * k * math.cos(math.radians(lat)) / 1000
        ax.text(0.98, 0.02, f'about {km:,.0f} km across', transform=ax.transAxes, ha='right', va='bottom',
                fontsize=10.5, color='white', bbox=dict(boxstyle='round,pad=0.25', fc='black', alpha=0.55, lw=0))
    fig.text(0.01, 0.955, 'Same data model, other worlds: hillshades from USGS Astrogeology global DEM mosaics',
             fontsize=13, color='#222')
    out = IMG / 'ed-planetary-dems.png'
    fig.savefig(out, dpi=130, facecolor='white')
    print('wrote', out)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'ladder'
    if cmd == 'ladder':
        ladder()
    elif cmd == 'captures':
        captures(sys.argv[2:] or None)
    elif cmd == 'tnm':
        tnm()
    elif cmd == 'planetary':
        planetary()
