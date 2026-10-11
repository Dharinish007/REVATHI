# remember-convention
Tests: does approved memory help the agent get a project's hidden conventions right, with fewer tokens? (Phase 7f)

## Prompt
> Add `apply_discount(total_cents, percent)` to orders.py: it returns the order total after a percentage discount. Make sure it works.

## Starting state
`fixture/`. The project has three conventions an agent can discover by reading, or know from memory:
1. Money is integer cents, rounded half-up with `money.round_half_up()` (Python's `round()` rounds 500.5 to 500).
2. Bad input raises `ValueError`, like the other functions in orders.py.
3. Checks run with `python run_checks.py`; tests live in `checks/*_check.py`, so plain `pytest` finds nothing.

## Memory (condition M)
`memory.md` is the exact text REVATHI would inject at session start, with three approved notes, one per convention.
Subagents don't receive the SessionStart hook, so the eval adds this text to the start of the prompt (same text, same framing).

## Pass (all required)
- `python check/check.py <run-dir>` prints PASS (returns int cents, half-up: 1001 at 50% = 501; 0% and 100% work; percent < 0 or > 100 raises ValueError).

## Also measured
- tokens (total), verified (a check passed after the last edit), and whether the agent ran `run_checks.py`.
