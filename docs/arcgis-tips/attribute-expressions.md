# Writing attribute expressions

The expression box has two modes, and the handouts sometimes mix up their wording:

- **Clause mode** (the default) builds `Where [field] [operator] [value]` from dropdowns. This is
  where a phrase like "NAME is Equal to UTAH" comes from.
- **SQL mode** — toggle **SQL Editor** — is where you type real SQL: `NAME = 'UTAH'`.

Things to know:

- **Text values need single quotes and are case sensitive.** `NAME = 'UTAH'` works;
  `NAME = 'Utah'` returns nothing. Numbers take no quotes: `DENSITY > 5000`.
- **A coded field may be text even though its values look like numbers.** UGRC's road
  classification field stores `'1'`, `'2'`, `'3'` as *strings*. `CARTOCODE = 1` fails;
  `CARTOCODE IN ('1','2','3')` works. Check the field type before you write the expression.
- **In ModelBuilder the value box will not list a field's unique values.** In a standalone tool it
  offers a pick list; on a model variable it cannot, because the tool has not run yet. You have to
  type the value, so a typo or wrong capitalisation silently returns zero features.
- **A field created by an upstream tool will not appear in a downstream tool's field list** until
  that upstream tool has actually run. Type the field name in by hand.
