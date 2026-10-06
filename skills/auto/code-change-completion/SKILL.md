---
name: code-change-completion
description: Use when fixing bugs in a Python package and preparing the change for review.
---
- Add type annotations to every parameter and return value of every public package function; treat names beginning with `_` as private.
- Create `tests/test_regressions.py` with one test function for each bug fixed, and include at least three test functions.
- Run the regression test file and confirm it passes.
- Record every fix in `CHANGELOG.md` under the exact heading `## Unreleased`.
- Format each changelog entry exactly as `- fix(<function name>): <short description>`.
- Include at least three fix bullets.