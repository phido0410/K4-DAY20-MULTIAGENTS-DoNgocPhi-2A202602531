---
name: structured-data-deliverables
description: Use when analyzing tabular data and producing machine-readable results or cleaned data files.
---
- Translate every requested output into a checklist of files, fields, formats, and metadata before calculating.
- Inspect headers, row counts, duplicates, missing-value conventions, and representative records.
- Deduplicate according to the task’s entity definition before computing distinct-entity metrics.
- Track input-row counts separately from counts of usable distinct entities.
- Represent currency in the required exact unit; use integer minor units or decimal arithmetic rather than binary floats.
- Normalize timestamps to the required timezone and format, and map labels to the specified canonical values.
- Exclude unknown values only where required, and apply that rule consistently to metrics and cleaned outputs.
- Write every requested artifact, then validate its schema, field order, row count, types, and formatting.