---
name: git-safety
description: Safe procedure for git operations - committing, branching, merging, rebasing, resolving conflicts, undoing changes, pushing, and PRs. Use for any git action beyond read-only status/log/diff.
---

# Git safety

Goal: git work that never loses someone's changes or rewrites shared history by accident.

## Before acting
- Run `git status` and check the current branch. Uncommitted work you didn't create is the user's: don't discard it.
- Commit or push only when asked. On the default branch, create a branch first unless told otherwise.

## Rules of the procedure
- **Stage deliberately:** add specific files, not `git add -A`, and check the staged diff for secrets, large binaries, and unrelated changes.
- **Commit messages:** follow the repo's existing style (`git log --oneline -10`); explain why, not just what.
- **Never skip hooks or signing** (`--no-verify`, `--no-gpg-sign`). If a hook fails, fix the cause.
- **Prefer new commits over amending** once anything is pushed.
- **Destructive commands need explicit confirmation** and a look at what they'll destroy first: `reset --hard`, `checkout -- .`, `clean -fd`, `branch -D`, `push --force` (use `--force-with-lease` if force is approved), `rebase` of pushed branches, `stash drop`.
- **Before any risky operation**, note the current commit SHA (or create a backup branch) so it can be undone.
- **Conflicts:** understand both sides before resolving; never resolve by blindly taking one side. Re-run tests after.
- No interactive commands (`rebase -i`, `add -i`) in non-interactive environments.

## Failure handling
- Unexpected state (detached HEAD, mid-rebase, unknown stash): stop and report state before changing anything.
- Push rejected: fetch and inspect; don't force.

## Output
Commands run · resulting state (branch, commit SHA, pushed or not) · anything requiring the user's decision.
