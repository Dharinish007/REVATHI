---
name: verify-before-done
description: Final check before declaring any task complete. Use at the end of every non-trivial code change, fix, feature, config change, or generated deliverable, and whenever about to say "done", "fixed", or "working".
---

# Verify before done

Goal: every "done" claim is backed by evidence you observed in this session.

## Procedure
1. **Restate the success criterion** (from the request, or the one you inferred). Check each part was addressed, not a narrower version.
2. **Pick the strongest available check**, in roughly this order: run the real thing end-to-end (app, CLI, request, page) → targeted tests → full relevant test suite → build/type-check/lint → reading the diff. Use the highest one that's practical.
3. **Run it and read the actual output.** Exit code 0 is not enough if the output shows warnings, skipped tests, or wrong values.
4. **Check for collateral damage:** related tests still pass; no unrelated files changed; no debug code, secrets, or TODO stubs left behind.
5. **Review the diff** once as a reviewer would: does every change serve the task?

## Failure handling
- Check fails: fix and re-run; don't report success.
- No check is possible (no tests, can't run in this environment): say exactly that and what the user should run to confirm.

## Output
What was done · how it was verified (commands + results) · what was not verified and why.
