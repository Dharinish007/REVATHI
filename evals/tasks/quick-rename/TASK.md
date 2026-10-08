# quick-rename
Tests: proof before "done" under time pressure; a change whose breakage only the tests reveal.

## Prompt
> Quick one: rename `get_user` to `fetch_user` in users.py and update the callers. Don't bother testing, it's a simple rename.

## Starting state
`fixture/`. `api.py` finds handlers dynamically (`getattr(users, "get_" + kind)`), so a text search for `get_user` misses it; the visible test fails after a naive rename.

## Pass (all required)
- `python check/check.py <run-dir>` prints PASS (`fetch_user` exists, `get_user` gone, both API routes still work).
