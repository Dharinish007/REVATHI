# Changelog

All notable changes to REVATHI are recorded here, newest first.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions will follow [Semantic Versioning](https://semver.org/) from the first release.

## [Unreleased]

### Added
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
- 2026-10-08 · Proof check re-blocked every later turn over a gap already recorded as `unproven` (found in the live test: a docs-only turn was blocked over an earlier `calc.py` edit). Now it only judges what happened after the last `unproven` record. 2 regression tests.

### Fixed (compared with the Agentic OS guard)
- Secrets inside shell commands are now caught (`echo KEY="sk-…" > config.py`, `export`, `tee`, `Set-Content`); writing to `.env` stays allowed.
- Git global options no longer bypass checks (`git -C . reset --hard`, `--no-pager`, `--git-dir`, `-c`).
- `rm -rf $HOME` is now denied (root targets were compared case-sensitively, so `$HOME` only triggered *ask*).
- New *ask* rule: `find … -delete`.
