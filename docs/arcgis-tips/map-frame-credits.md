# Basemap credits cover a small map frame

## The problem

When a layout has several small map frames — the panels of a comparison sheet, an inset or a
locator map — the **service layer credits** in the corner of each frame can cover a large part of
it. These are the source credits ArcGIS Pro adds automatically for every web service in the map:
basemaps, imagery, and image services such as the elevation service in Lab 8. The text is the same
length whatever the size of the frame, so on a small frame it sits on top of the data, and on a
sheet of six frames the same line appears six times.

*Figure placeholder: a layout with three or more small map frames (a Lab 8 comparison sheet works),
each with the automatic service layer credits drawn across the bottom of the frame and covering the
data.*

## The fix: move the credits out of the map frames

You cannot click the automatic credits and edit them, but you can replace them with one text
element that you control:

1. Open your layout.
2. On the **Insert** tab, in the **Graphics and Text** group, click **New Dynamic Text**.
3. Scroll down to the **Layout** section and choose **Service Layer Credits**.
4. Click on the layout to place it.

*Figure placeholder: the Insert tab's New Dynamic Text menu, scrolled to the Layout section, with
Service Layer Credits highlighted.*

Once that element exists, the credits stop drawing inside the map frames. **[To do: confirm in
ArcGIS Pro 3.7 that placing the element removes the automatic credits from every map frame on the
page, not only from the frame it is nearest.]** The element lists the credits for every map frame on
the page, so one copy covers the whole sheet. Drag it to the margin or next to your text box, and
make the font small (6 to 7 points is fine) in the **Element** pane.

*Figure placeholder: the same layout as the first figure after the fix, with the map frames clear
and one small Service Layer Credits element in the margin beside the text box.*

Leave the element on the layout. If you delete it, the automatic credits come back inside every
map frame. **[To do: confirm that deleting the element restores the automatic credits in the map
frames. Esri's support article 000042063 confirms steps 1 to 4 and moving the element; this
behavior comes from an emailed write-up, not from Esri documentation.]**

## Hiding the credits, and when you may

If you would rather write the sources yourself, you can hide the element: find **Service Layer
Credits** in the layout's **Contents** pane and uncheck it. Do this **only if the same sources
appear somewhere else on the layout**, typed into your text box. **[To do: confirm that
unchecking the element in the Contents pane hides it without the automatic credits coming back in
the map frames, and that it stays hidden in an exported PDF.]**

*Figure placeholder: the layout's Contents pane with the Service Layer Credits element listed and
its check box cleared.*

Esri's guidance is that the credits must appear **on or near the map** in anything printed, including
class work and research papers, not only in commercial products
([Esri: citing an ArcGIS Online basemap](https://support.esri.com/en-us/knowledge-base/what-is-the-correct-way-to-cite-an-arcgis-online-basema-000012040){ target="_blank" }).
Moving or consolidating the credits is fine. Removing them from the sheet is not, and the lab
rubrics ask for the data's source on the map in any case.

For example, a Lab 8 sheet can hide the dynamic credits and carry this line in its text box instead:

> Elevation: USGS 3D Elevation Program, 1/3 arc-second DEM, tile n41w112 (May 2026). Study area:
> drawn for CE 414.

If you also used a basemap, add its sources to that line — the **Credits** on the basemap's item
page give the wording, and so does the dynamic text element before you hide it.
