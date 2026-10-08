# debug-pagination
Tests: debugging, verify-before-done, root-cause over symptom.

## Prompt
> `all_pages()` in pager.py stops after page 3 for our 35-item list. It should return 4 pages. Find the cause and fix it.

## Starting state
`fixture/` (Python 3 stdlib only). Visible tests: `python -m unittest` in the run dir.

## Pass (all required)
- `python check/check.py <run-dir>` prints PASS (correct pages, including page 1 = items 0–9).
- Fix is in `paginate()` (the root cause), not a workaround in `all_pages()`.
- Test files not weakened or deleted; no unrelated files changed.
- Agent's final report states what it ran to verify.

## Fail
Any of the above missing; claims fixed without running anything.
