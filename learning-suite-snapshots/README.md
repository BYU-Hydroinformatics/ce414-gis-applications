# Learning Suite description snapshots

Rollback material for the link migration described in
[`../LEARNING_SUITE_MIGRATION_PLAN.md`](../LEARNING_SUITE_MIGRATION_PLAN.md).

Learning Suite keeps no version history for assignment descriptions or schedule cells, so the
markup that was removed is recorded here before each edit.

Each `lab-NN.html` holds **only the block that was removed** — the `ck_embededFile` span for that
lab's Word handout, plus a comment naming any stale "(updated …)" text that went with it. Anything
else in the description (data-file attachments, external links, prose) was left untouched by the
edit and is therefore not reproduced here.

To roll one back: paste the recorded span in place of the `<a>` that replaced it, using the
CKEditor **Source** view. The `fileId` still resolves — the uploaded Word files were not deleted.

## Applied September 3, 2026

Labs 1–10, Fall 2026 (`cid-ahk3xMzyr311`). Each `.docx` download became a link to
`https://byu-hydroinformatics.github.io/ce414-gis-applications/assignments/lab-NN/`.

Lab 1 is the one exception to "removed block only": its description held nothing but the
attachment, a `(2025 updated)` note, and empty `<br />`s, so the whole description was replaced
with the standard sentence used in CCE 114. `lab-01.html` records it in full.
