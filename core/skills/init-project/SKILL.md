---
name: init-project
description: Create or refresh a repository's own AGENTS.md (plus a CLAUDE.md pointer) with the project-specific facts an agent needs - commands, structure, conventions, gotchas. Use when starting work in a repo that has no AGENTS.md/CLAUDE.md, when asked to "init", "set up this project for agents", or when the existing project file is stale or wrong.
---

# Init project

Goal: a short, verified project file that saves every future session from re-discovering the same facts. Project facts only; universal rules already live in the global rules file.

## Procedure
1. **Check what exists.** Read any existing `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`, `GEMINI.md`, `README`, `CONTRIBUTING`. Refresh rather than replace; keep human-written content unless it is wrong.
2. **Discover the facts** (see `codebase-analysis`): manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Makefile`, CI config), entry points, test layout, lint/format config, env var names (from `.env.example`, never `.env` values).
3. **Verify every command** you will list (install, build, test, single test, lint, run) by running it, or mark it `unverified`. A wrong command is worse than none.
4. **Write `AGENTS.md`** at the repo root, under ~60 lines, with only what an agent can't guess quickly:
   - **Overview:** one or two lines on what this is and who uses it.
   - **Commands:** exact, verified commands, including how to run one test.
   - **Structure:** the few directories that matter and what lives there.
   - **Conventions:** naming, patterns, error handling, testing style actually used here.
   - **Gotchas:** non-obvious traps (generated files not to edit, required services, slow tests, platform quirks).
   - **Boundaries:** files or areas agents must not touch without asking.
5. **Add `CLAUDE.md`** containing `@AGENTS.md` if it doesn't exist (Claude Code reads CLAUDE.md; Codex, Cursor and others read AGENTS.md). If CLAUDE.md exists, add the import line and move duplicated facts into AGENTS.md, with approval if the file is user-written.
6. **Leave out:** generic advice ("write clean code"), anything in the global rules, secrets, long architecture essays (link to docs instead), facts that change weekly.

## Failure handling
- A command fails: fix the documented command if the correct one is clear; otherwise list it as broken under Gotchas.
- Huge monorepo: write the root file for shared facts and suggest per-package AGENTS.md files instead of one giant file.
- Not allowed to run commands: write the file with every command marked `unverified`.

## Output
Files created or updated · commands verified vs unverified · anything left for the user to confirm.
