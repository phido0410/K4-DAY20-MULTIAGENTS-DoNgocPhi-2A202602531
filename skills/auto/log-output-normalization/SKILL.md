---
name: log-output-normalization
description: Use when extracting error records from logs and assembling a structured JSON result.
---
- Set the top-level `schema_version` to `2`.
- Set the top-level `generated_by` to `log-triage`.
- Normalize each service name to lowercase and replace every hyphen with an underscore.
- Sort the `errors` array by service first, then by `timestamp_utc` in ascending order.