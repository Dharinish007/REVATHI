# house-rules
Tests: does approved memory carry the user's non-obvious past decisions into a new session? (Phase 7f, third memory eval)

**Pre-registered 2026-10-11, committed before any run.** Checks, measures and the success rule below must not change after results are seen.

## Prompt
> Add a function `slugify(title)` to text_utils.py that turns a post title into a URL slug. Make sure it works.

## Starting state
`fixture/`: `text_utils.py` with two unrelated helpers and a test file. Nothing in the files says how slugs should look.
Three earlier user decisions exist **only in memory** (all non-obvious, chosen so an agent would not guess them):
1. Slugs use underscores, not hyphens.
2. Slugs are at most 40 characters, cut at a word boundary (never mid-word, no trailing underscore).
3. Accented letters are converted to plain ASCII (é → e), never dropped.

## Memory (condition M)
`memory.md`: the exact text REVATHI would inject, with those three approved notes plus one unrelated note.

## Pass (all required): `python check/check.py <run-dir>` prints PASS
- `slugify("Hello World") == "hello_world"`
- `slugify("Café au lait!") == "cafe_au_lait"`
- `slugify("  Multiple   spaces  here ") == "multiple_spaces_here"`
- `slugify("A very long title that keeps going well past the forty character limit")` is at most 40 characters, is a prefix of the full underscore slug at a word boundary, and does not end with `_`

## Measures and success rule (fixed in advance)
- Primary: pass rate, B (no memory) vs M (memory), 3 runs each.
- Secondary: total tokens per run; whether the final message asks the user a clarifying question about the slug format.
- **Memory "helps" on this task if M passes at least 2 more runs than B (of 3) and M's mean tokens are at most 10% above B's.** Anything else is reported as "no benefit shown".
- Framing: this measures whether memory *can* carry decisions across sessions, not how often that matters in everyday work.
