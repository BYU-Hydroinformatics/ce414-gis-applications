# Running a model from its tool dialog

From Lab 2 on, you build a model in ModelBuilder and then run it again as a tool, from the dialog
the Catalog pane opens. The two kinds of run behave differently, and most lost work in this course
comes from not knowing how.

## A dialog run deletes intermediate data

Everything in a model that is **not a parameter or an input** is *intermediate*. When the model
finishes running from its tool dialog, ArcGIS Pro deletes every intermediate dataset from your
geodatabase, and the layers vanish from your map. Clicking **Run** inside ModelBuilder keeps all of
it. The dialog run also deletes the copies an earlier run inside ModelBuilder made.

Ways to keep what you need:

- **Make it a parameter.** Right-click the oval ▸ **Parameter**. Parameters are never deleted. This
  is the dependable route, and it is why the labs make their key outputs parameters.
- **Finish anything that needs intermediates first.** Make your checks and your first map from the
  run inside ModelBuilder, before the first dialog run. If you need the layers again, run the model
  inside ModelBuilder once more.
- **Map from the downloaded data where you can.** Downloaded inputs are never deleted. A
  definition query holding the same expression as a Select tool gives you the same features without
  depending on the model's output.

> [!WARNING]
> **Do not click the ✗ Intermediate button** on the ModelBuilder canvas toolbar. It is *Delete
> Intermediate Data*, and it deletes them immediately. ArcGIS Pro also has a per-dataset
> **Intermediate Data** flag (select the oval and press `Ctrl+I`), but we could not confirm that it
> keeps the data through a dialog run. You may have to save the model and reopen the tool before
> it takes effect. Make the oval a parameter instead. **[To do: confirm whether `Ctrl+I`, then
> saving the model, closing it and reopening the tool from the Catalog pane, keeps the flagged
> dataset through a dialog run. One test without reopening the tool did not keep it.]**

*Figure placeholder: the ModelBuilder canvas toolbar with the ✗ Intermediate button called out and
labeled "Delete Intermediate Data — do not click".*

## Close the model's tab, then open the tool

Save the model and close its ModelBuilder tab. Then, in the **Catalog** pane, open your toolbox
(`LabNN.atbx`) and double-click the model: it opens as a tool in the Geoprocessing pane. With the
model's tab still open, the tool dialog can show an empty parameter list.

In the Catalog pane, right-click the model ▸ **Edit** to reopen it in ModelBuilder. **Open** runs it
as a tool instead.

*Figure placeholder: the Catalog pane with a lab toolbox expanded and a model's right-click menu
open, Edit and Open both visible.*

## Give every run its own output names

A run that reuses an output name **overwrites** the dataset from the earlier run, including the
baseline you already mapped. Give each run's outputs a name that says which run it is, such as
`RMSE_IDW_n250` or `Route_Steep`.

- **Type the numbers into the name yourself.** In Lab 6, a name built from `%From Value%` and the
  model's other parameters wrote the right dataset but added the *previous* run's layer to the map.
- **A warning icon on an output only means the dataset already exists** from an earlier run. It is
  not an error, but it is your cue to rename. (Lab 5's Figure 12b and Lab 9's Figure 8b show
  these icons.)

## Check that the dialog run matches

At its default values, a dialog run should reproduce your last run inside ModelBuilder exactly. The
labs give check values for this. If yours do not match, a parameter was left at a value from
testing.

Leave **Close on completion** unchecked the first time, so you can read the run's messages.
