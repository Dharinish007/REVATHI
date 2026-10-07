---
name: debugging
description: Find and fix the root cause of a bug, crash, failing test, or unexpected behavior. Use when something "doesn't work", "breaks after X", "stopped working", throws an error, or behaves differently than expected.
---

# Debugging

Goal: a confirmed root cause and a fix that addresses it, not a patch that hides the symptom.

## Inputs
- The symptom: exact error, observed vs. expected behavior, where it happens.
- How to trigger it. If missing and not derivable, ask once.

## Procedure
1. **Reproduce.** Trigger the failure yourself (run the test, request, command, or page). If you can't reproduce, say so and work from logs/evidence instead of guessing.
2. **Localize.** Trace the path from input to wrong output. Narrow with evidence: logs, a debugger, targeted prints, `git log`/`git bisect` for regressions, comparing a working vs. broken case.
3. **Form one hypothesis at a time** and test it with the cheapest experiment that could disprove it. Record what each experiment ruled out.
4. **Confirm the root cause** before editing: you can explain why the bug happens and why it didn't happen in the working case.
5. **Fix at the root.** Find every caller of the code you change; fix once where they all route through.
6. **Prove it.** Re-run the reproduction (now passes), add a regression test when the project has tests, run the surrounding suite.
7. Remove temporary debug output.

## Failure handling
- Three hypotheses disproven: stop, summarize evidence and what's ruled out, and ask or widen scope instead of trying random changes.
- Can't reproduce: report the conditions tried and what extra info (logs, env, data) would unblock it.
- Fix works but cause is unclear: say so explicitly; don't present it as a root-cause fix.

## Output
Root cause (1–2 lines) · fix (files changed) · evidence it works (repro before/after, tests run) · anything unverified.
