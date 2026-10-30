# Creating a point feature class

Several labs ask you to place your own points — candidate sites, existing stores, sample locations.

1. In the **Catalog** pane, expand **Databases**, right-click your project geodatabase
   (`Lab01.gdb`), and choose **New ▸ Feature Class**.

    ![The right-click menu of a project geodatabase in the Catalog pane: New is highlighted (outlined in red) and its submenu lists Feature Dataset, Feature Class (outlined in red, with a tooltip reading Create a new feature class in the geodatabase), Table, View, Relationship Class, Raster Dataset, Mosaic Dataset, Trajectory Dataset, Catalog Dataset, Oriented Imagery Dataset and Toolbox.](images/points-new-fc-menu.png)

    **Figure 1.** Right-click the geodatabase ▸ **New** ▸ **Feature Class**.

2. Give it a name with no spaces, set **Feature Class Type** to **Point**, and click Next. The type
   opens at **Polygon**, so change it.

    ![The Create Feature Class pane, Define page: Name Candidate_Sites, Alias empty, Feature Class Type Point (outlined in red), M Values unchecked, Z Values checked, Add output dataset to current map checked, and Previous, Next and Finish buttons.](images/points-define.png)

    **Figure 2.** Page 1 of the wizard. Leave the M and Z check boxes as they are.

3. Add any fields you want to record — a `NAME` text field is usually enough. Click **Click here to
   add a new field**, type the name, then set its **Data Type**: a new field comes in as **Long**,
   a whole number, which cannot hold a name.

    ![The Fields page: OBJECTID, SHAPE, and a new field NAME whose Data Type reads Long, outlined in red.](images/points-fields-long.png)

    **Figure 3.** A new field arrives as **Long**.

    ![The same page with the Data Type list open under Long: Long, Big Integer, Float, Double, Text (outlined in red), Date, Date (high precision), Date Only, Time Only.](images/points-fields-type-list.png)

    **Figure 4.** Click the Data Type cell twice to open the list, and choose **Text**.

    ![The Fields page with NAME as Text, outlined in red.](images/points-fields-text.png)

    **Figure 5.** `NAME` is now a text field.

4. On the next page, check the coordinate system. It should be the one you are using for analysis
   (NAD 1983 UTM zone 12N). The wizard proposes the coordinate system of the layers in your map,
   so if the map is in something else, search for UTM zone 12N here. Then click **Finish**.

    ![The Spatial Reference page: Selected Coordinate Systems, Horizontal NAD 1983 UTM zone 12N (outlined in red), Vertical None, and below it the Available Coordinate Systems tree open at Layers with NAD 1983 UTM zone 12N highlighted.](images/points-crs.png)

    **Figure 6.** Page 3: read the **Horizontal** line before you click Finish.

5. The empty layer is added to your map. On the **Edit** ribbon tab click **Create**, pick your new
   layer in the Create Features pane, and click on the map to place each point.

    ![The Edit tab of the ribbon: Paste, Save (outlined in red), Discard, No Topology, Error Inspector, Manage Templates, Snapping, and in the Features group Create (outlined in red), Modify and Delete.](images/points-edit-ribbon.png)

    **Figure 7.** **Create** opens the Create Features pane; **Save** writes your edits.

    ![The ArcGIS Pro window: the Contents pane lists Candidate_Sites with a yellow point symbol; the map shows three yellow points placed over imagery of Provo; the Create Features pane on the right reads Create Candidate_Sites completed and lists the Candidate_Sites template, outlined in red.](images/points-placed.png)

    **Figure 8.** Three points placed over imagery, with the Candidate_Sites template selected.

6. Click **Save** on the Edit tab when you are done. Edits are not written until you save.

Use a basemap or imagery to place points accurately, and zoom in — a point placed at the wrong
scale can be a quarter mile off.
