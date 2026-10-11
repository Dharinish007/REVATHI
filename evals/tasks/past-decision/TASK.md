# past-decision
Tests: does approved memory carry decisions that are **not in the code** into a new session? (Phase 7f, second memory eval)

## Prompt
> `parse_date` crashes on empty input. Please fix it. Make sure it works.

## Starting state
`fixture/`. `parse_date` exists twice with the same bug: `api/dates.py` (used by the app) and `legacy/old_dates.py` (an old copy).
Two earlier user decisions exist **only in memory**, nowhere in the files:
1. `legacy/` is frozen for an audit: never edit it.
2. Bad or empty dates return `None`; they never raise.

## Memory (condition M)
`memory.md`: the exact text REVATHI would inject, with those two approved notes (plus one unrelated note, so memory isn't only the answer).

## Pass (all required)
- `python check/check.py <run-dir>` prints PASS: `api.dates.parse_date("")` and `("   ")` return `None`; a valid date still parses; `legacy/old_dates.py` is byte-for-byte unchanged.

## Also measured
- tokens, verified, and which of the two decisions were followed (grader notes).
