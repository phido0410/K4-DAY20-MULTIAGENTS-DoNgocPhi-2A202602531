---
name: machine-readable-output-contracts
description: Use when transforming logs or other records into JSON or another schema-constrained output.
---
- Treat the requested schema and naming rules as mandatory, not cosmetic.
- Include all required top-level fields and use the exact specified values and types.
- Normalize identifiers and labels before aggregation or serialization.
- Convert timestamps consistently before ordering records.
- Sort output using the complete requested key sequence and direction.
- Preserve required record details, counts, and null values during transformation.
- Parse the generated output and validate its structure, field values, normalization, and ordering.
- Ensure the final response describes only artifacts that were actually created and checked.