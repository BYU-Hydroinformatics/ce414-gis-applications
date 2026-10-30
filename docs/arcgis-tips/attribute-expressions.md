# Writing attribute expressions

The expression box has two modes, and the handouts sometimes mix up their wording:

- **Clause mode** (the default) builds `Where [field] [operator] [value]` from dropdowns. This is
  where a phrase like "NAME is Equal to UTAH" comes from.
- **SQL mode** — toggle **SQL Editor** — is where you type real SQL: `NAME = 'UTAH'`.

![The Select tool from ModelBuilder with the SQL Editor off: Input Features UtahCounty, Output Feature Class UtahCounty_Select, and one clause, outlined in red, reading Where NAME is equal to UTAH, with Add Clause below.](images/expressions-clause-mode.png)

**Figure 1.** Clause mode: a field, an operator and a value, each picked from a list.

![The same Select dialog with the SQL Editor switch on (outlined in red) and the expression NAME = 'UTAH' typed in the box.](images/expressions-sql-mode.png)

**Figure 2.** The same expression in SQL mode. Text values go in single quotes.

Things to know:

- **Text values need single quotes and are case sensitive.** `NAME = 'UTAH'` works;
  `NAME = 'Utah'` returns nothing. Numbers take no quotes: `DENSITY > 5000`.
- **A coded field may be text even though its values look like numbers.** UGRC's road
  classification field stores `'1'`, `'2'`, `'3'` as *strings*. `CARTOCODE = 1` fails;
  `CARTOCODE IN ('1','2','3')` works. Check the field type before you write the expression.
- **The value box lists a field's values only for data that already exists.** When the input is a
  layer or dataset, the box offers a pick list, in ModelBuilder too (Figure 3). When the input is a
  model variable that an earlier tool creates, it cannot, because that tool has not run yet. You
  have to type the value, so a typo or wrong capitalization silently returns zero features.

  ![The Select clause with NAME and is equal to chosen and the value list open below the value box, outlined in red: UTAH, with Values selected and Fields as the other option.](images/expressions-pick-list.png)

  **Figure 3.** The pick list for an existing layer. Choosing from it avoids typos.
- **A field created by an upstream tool will not appear in a downstream tool's field list** until
  that upstream tool has actually run. Type the field name in by hand.
