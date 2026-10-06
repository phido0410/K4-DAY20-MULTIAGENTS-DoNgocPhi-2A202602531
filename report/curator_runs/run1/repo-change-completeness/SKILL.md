---
name: repo-change-completeness
description: Use when fixing bugs or making changes in a code package with explicit quality or documentation checks.
---
- Read the full affected modules and the repository’s existing test, typing, and changelog conventions.
- Annotate every public function’s parameters and return value, including functions not directly changed.
- Add a regression test for each fixed bug; keep tests focused and independent.
- Record each fix in the required changelog section and format.
- Run the regression tests and the relevant full test suite.
- Check each explicit acceptance rule against the final repository state before reporting completion.