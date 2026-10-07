---
name: code-review
description: Review a diff, PR, branch, or file for correctness bugs, security issues, and unnecessary complexity. Use when asked to review, audit, or check code, or before merging significant changes.
---

# Code review

Goal: a short list of real, verified problems ranked by severity - not a style essay.

## Inputs
- The target (diff, PR, branch, files) and the intent of the change (PR description, ticket, or ask).

## Procedure
1. **Understand intent first**, then read the full diff and enough surrounding code (callers, callees, tests) to judge it.
2. **Hunt in priority order:**
   1. Correctness: logic errors, edge cases (empty, null, boundaries, concurrency), broken callers, error paths.
   2. Security: untrusted input reaching queries/shell/HTML/paths, authz gaps, secrets, unsafe deserialization.
   3. Data safety: migrations, destructive operations, lost writes.
   4. Tests: does anything verify the new behavior?
   5. Simplicity: reinvented helpers/stdlib, dead code, speculative abstraction.
3. **Verify each finding** before reporting: trace the actual path or construct the concrete input that fails. Drop anything you can't substantiate, or label it as a question.
4. Skip pure style nits unless the repo's conventions are violated.

## Failure handling
- Can't see enough context to judge: say which part is unreviewed and why.

## Output
Findings, most severe first: `file:line` · problem · concrete failure scenario · suggested fix. End with an overall verdict. If nothing survives verification, say so.
