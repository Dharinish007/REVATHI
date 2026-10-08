# Changelog

All notable changes to REVATHI are recorded here, newest first.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions will follow [Semantic Versioning](https://semver.org/) from the first release.

## [Unreleased]

### Added
- 2026-10-08 · CI workflow for REVATHI tests on Windows, Linux, macOS. Eval batch 2 + `evals/FINDINGS.md`: with the handback fix, the pressure task went verified 0/3 → 2/3.
- 2026-10-08 · **Phase 5 (evidence):** `revathi mode observe`; per-subagent logs + `SubagentStop`; eval harness (`evals/prepare.py`, `grade.py`, `scorecard.py`, pressure task `rush-fix`); batch 1 (18 runs) in `evals/SCORECARD.md`: neutral on pass rate, no extra model tokens, enforcement not effective on in-app subagents.
- 2026-10-08 · REVATHI installed on the dev machine; doctor green in both tools. Live: Claude Code ✅; Antigravity IDE loads the hooks (fix not yet re-tested live); Antigravity 2.0 does not load global hooks (cause unknown).
- 2026-10-08 · **Phase 4 (Front desk):** `revathi install [--dry-run] | uninstall | doctor | mode | log` (`cli/install.py`, `cli/revathi.py`); Antigravity adapter; `engine/pipeline.py` (shared flow), `engine/config.py` (mode). Why: one-command setup in 2 tools, reversible.
- 2026-10-08 · Modes: careful (extra asks), balanced (default), full (undoable local actions run after a snapshot). Policy rules marked `undoable`.
- 2026-10-08 · Tests: `test_antigravity.py`, `test_install.py` (fake home). 56/56 pass.
- 2026-10-08 · **Phase 3 done.** Live test: a real `reset --hard` (user-approved) was reversed by `revathi undo`; reading the decoy asked for confirmation. The fake-key leak test was blocked, but not by REVATHI (no record); the hook denies that command when replayed.
- 2026-10-08 · Undo follows `cd <dir> &&` and `git -C <dir>` to snapshot the folder a command really targets (found before the live test; test added).
- 2026-10-08 · **Phase 3 (Safety net):** `engine/undo.py` (snapshots before file writes and risky commands; `revathi undo` restores, and its own changes can be undone), `engine/canary.py` (opt-in decoy credentials; read → ask, leak → deny), `cli/revathi.py` (`undo`, `canary`). Why: make mistakes cheap and make hidden-instruction attacks visible.
- 2026-10-08 · Hook: PreToolUse now also covers Read, Grep, WebFetch, WebSearch and MCP tools (for the canary); ask messages say whether a snapshot was saved.
- 2026-10-08 · Tests `tests/test_safety_net.py` (13). 36/36 pass.
- 2026-10-08 · **Phase 2 done (v0.1 scope complete).** Live test in Claude Code: proof check sent the agent back once after an untested edit; the agent then disclosed the gap plainly. Log recorded every action; hash chain intact.
- 2026-10-08 · **Phase 2 (Trust):** recorder `engine/log.py` (hash-chained session log, secrets redacted) and proof check `engine/proof.py` (no finishing after a code change until a test/build/lint check passes; blocks once). Rules in `policy/default.toml` `[proof]`. Why: stop fake "done", keep a record of every action.
- 2026-10-08 · Claude Code adapter now handles PreToolUse, PostToolUse, PostToolUseFailure and Stop; `adapters/claude-code/settings.example.json` template; local `.claude/settings.json` updated for the live test.
- 2026-10-08 · Tests `tests/test_proof.py` (14 tests); test logs go to a temp folder. 21/21 pass.
- 2026-10-08 · **Phase 1 done.** Live test in Claude Code: secret-in-command blocked (REVATHI message, no file written); 2 risky commands asked for confirmation; a safe command ran. Note: the ask tests did not confirm the REVATHI reason text.
- 2026-10-08 · `.claude/settings.json`: REVATHI guard hook turned on for Claude Code sessions opened in `REVATHI/` (option A, project only) for the Phase 1 live test. Machine-specific absolute path; replaced by `revathi install` in Phase 4.
- 2026-10-08 · Phase 1 started. `core/AGENTS.md` (rules shipped to users), `core/skills/` (16, copied from Agentic OS), `core/agents/` (reviewer, researcher). Why: portable source for every tool.
- 2026-10-08 · Engine: `engine/event.py` (common Event/Decision), `engine/policy.py` (loads TOML), `engine/guard.py`; rules in `policy/default.toml`. Why: write checks once, keep rules as data.
- 2026-10-08 · Claude Code adapter `adapters/claude-code/hook.py` + README (manual setup). Fails safe to *ask* if the check crashes.
- 2026-10-08 · Tests `tests/test_guard.py`: 31 ported cases, 7 + 6 cases for the two known holes, 14-case dangerous-command set, 3 adapter checks. All pass.
- 2026-10-08 · Guide: release plan (v0.1 → v2.0), Phase 1 checklist.
- 2026-10-08 · Project docs created: `AGENTS.md` (agent rules + personality), `CLAUDE.md` (pointer), `README.md` (sample), `revathi_dev_guide.md` (problems, vision, architecture, plan), `revathi_decisions.md`, `CHANGELOG.md`. Why: one clear source of truth before any code is written (Phase 0).

### Fixed
- 2026-10-08 · Subagents could hand back an untested report before `SubagentStop` fired; the proof check now gates `SubagentHandback` (found in eval batch 1). Tests added.
- 2026-10-08 · Code edited through shell commands (`sed -i`, `perl -i`, redirects, `tee`, `Set-Content`) was invisible to the proof check; found in the eval pilot. Tests added.
- 2026-10-08 · **Antigravity hooks never ran** (live test): Antigravity runs hooks via `cmd /c`, which passed the quoted script path to Python with literal quotes, so every REVATHI hook failed and Antigravity let actions through. Found in Antigravity's own log. Fix: unquoted path (Windows short path if it has spaces); `doctor` now probes the hook through `cmd /c` like Antigravity. Test added (fake home with a space).
- 2026-10-08 · Antigravity: REVATHI's *ask* is now `force_ask`, because `ask` was silently auto-approved under "Always Allow" (D24).
- 2026-10-08 · Installer crashed on Windows reading `claude plugin list` (the `❯` character); found by a real-machine dry run. Test added.
- 2026-10-08 · Deletes now snapshot the exact targets first (covers git-ignored files like `.env`), falling back to a git snapshot.
- 2026-10-08 · Pruning old git snapshots left their hidden refs behind forever. Now released on prune. Regression test added.
- 2026-10-08 · Proof check re-blocked every later turn over a gap already recorded as `unproven` (found in the live test: a docs-only turn was blocked over an earlier `calc.py` edit). Now it only judges what happened after the last `unproven` record. 2 regression tests.

### Fixed (compared with the Agentic OS guard)
- Secrets inside shell commands are now caught (`echo KEY="sk-…" > config.py`, `export`, `tee`, `Set-Content`); writing to `.env` stays allowed.
- Git global options no longer bypass checks (`git -C . reset --hard`, `--no-pager`, `--git-dir`, `-c`).
- `rm -rf $HOME` is now denied (root targets were compared case-sensitively, so `$HOME` only triggered *ask*).
- New *ask* rule: `find … -delete`.
