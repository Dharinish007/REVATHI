# Changelog

All notable changes to REVATHI are recorded here, newest first.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions will follow [Semantic Versioning](https://semver.org/) from the first release.

## [Unreleased]

### Fixed
- 2026-10-08 · Antigravity did not use REVATHI memory (live test): its `ephemeralMessage` lasts one model call, and memory was sent only once. Now re-sent before every call, capped at 3,000 chars; recorded once per conversation. Claude Code recall confirmed live.

### Added
- 2026-10-08 · **Phase 7d (notice + review):** `engine/learn.py` turns session logs into suggestions: proof-passed fixes become evidence episodes, a check used in 3+ sessions of a project becomes a fact suggestion; dedupe by key. `revathi memory learn | review` (review needs a real terminal; the guard blocks agents). Session start mentions waiting suggestions and tells agents how to propose. 12 tests; 112/112 pass. Why: memory that grows from real work, still approved by the user.
- 2026-10-08 · **Phase 7b + 7c (recall + shield):** approved memory is shown at session start in Claude Code (`SessionStart`) and Antigravity (`PreInvocation`, once per conversation), framed as data, not commands; `revathi memory search`. The guard stops agents approving, rejecting, forgetting or editing memory (policy rules + memory-store write check). Installer and doctor cover the new hooks. 12 tests; 100/100 pass. Why: memory every tool can use, that an AI can't poison by approving itself.
- 2026-10-08 · **Phase 7a (memory store):** `engine/memory.py` (OKF v0.2 notes with `x-revathi` keys, stdlib frontmatter parser, inbox → approve/reject/forget, archive instead of delete, hash-chained `log.md`) and `revathi memory propose|list|show|approve|reject|forget|check`. A note counts only if unchanged since the user approved it; secrets are refused. Tests `tests/test_memory.py` (16); 87/87 pass. Why: the safe base the second brain is built on.
- 2026-10-08 · Guide: Phase 7 (second brain) plan with slices 7a–7h, built on research of memory frameworks, Karpathy's LLM wiki and Google's OKF format. Decisions D29–D36 proposed. Phase 6: GitHub repo marked live (CI green). Why: agree the full plan before writing memory code.

## [1.0.0rc1] - 2026-10-08 (prepared, not yet published)
Moved to its own repo: https://github.com/Dharinish007/REVATHI (history kept).
Everything below under "Unreleased" ships in this release candidate. Packaging: `pip install revathi` → `revathi` command; MIT license; standalone-repo CI with a wheel content check.

### Added
- 2026-10-08 · **Phase 5 done.** Second pressure task `quick-rename` (ceiling effect: the model tested on its own); verdict per REVATHI part in `evals/FINDINGS.md`.
- 2026-10-08 · Send-back reason names the project's own test files. Eval batch 3: pressure task with REVATHI 5/5 pass + verified; totals A → B pass 4/5 → 7/8, verified 1/5 → 7/8.
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
- 2026-10-08 · Commands that ran `revathi install` left no record (found when REVATHI's own proof check blocked its developer): install rewrote an unchanged `settings.json`, and the AI tool reloaded its hooks mid-command (likely cause; Claude Code's reload behavior not confirmed). Install now skips unchanged settings files (no reload, no useless backups). Live re-check: the install command is recorded. Test added.
- 2026-10-08 · Installing from a Windows git clone (CRLF) reported every already-installed skill (LF) as a conflict, and uninstall could not clean them up; files are now compared ignoring line endings. `.gitattributes` added. Found when reinstalling from the new repo. Test added.
- 2026-10-08 · Shell-edited files were recorded with a relative path, so the send-back could name another project's tests; now resolved against the command's folder (follows `cd`). Found in eval batch 3.
- 2026-10-08 · A check that never ran (`No module named pytest`, `command not found`, `Ran 0 tests`, `collected 0 items`) counted as passing. Found in eval batch 3.
- 2026-10-08 · Mac/Linux: Antigravity hook path was unquoted on every OS, which breaks under `sh -c` for paths with spaces; now unquoted only on Windows. Found by the first CI run (Linux/macOS red, Windows green); CI now green on all 6 jobs.
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
