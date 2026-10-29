# Tool dialogs that change what you typed

Several tool dialogs quietly rewrite or clear a box after you fill it in. Nothing warns you, and
the tool still runs, so the first sign is an output with the wrong name or a result that ignored
your expression.

## Type the output name last, and read it before OK

When you type an expression in **Raster Calculator**, it replaces whatever is in **Output raster**
with a default such as `RasterC_1`. **Extract by Mask**, **Project Raster** and **Select** do the
same when you change their inputs or validate an expression. Fill in everything else first, type
the output name last, and **read the name again before you click OK**. In one test, Raster
Calculator replaced a name typed *after* the expression too, so it had to be typed twice.

*Figure placeholder: the Raster Calculator dialog with an expression typed and Output raster reset
to a default name such as RasterC_1, the output box called out.*

## Do not switch the SQL Editor off and on

Once an expression is in the SQL Editor, leave it on. In Lab 6, switching the SQL Editor off and
back on cleared the expression in **Con** without a warning. Remember also that the **OK** button
moves down when the SQL Editor is on (see
[Defaults that give a confidently wrong answer](wrong-answer-defaults.md#3-clicking-run-with-a-tool-dialog-still-open)).

## A green check means the syntax is valid, nothing more

"The SQL expression is valid" tells you ArcGIS Pro can parse the expression. It does not tell you
the field holds the codes you think it does, or that the expression selects anything. Check the
record count of the output (see [Check what a tool actually produced](check-your-output.md)).
