# 🌸 REVATHI

**The trust layer for AI agents.** REVATHI sits between your AI coding agent and your computer. It stops dangerous actions, won't let the agent say "done" without proof, records what happened, and can undo mistakes.

Works with **Claude Code** and **Antigravity**. Local and private: no network calls, no telemetry.

> Status: **1.0.0 release candidate.** Tested on Windows, Linux and macOS (CI) and live in Claude Code. Antigravity: see [Known limits](#known-limits).

## Why
AI agents are smart, but you can't fully trust them yet. They say "done" without testing, run destructive commands, leak keys into files, and leave no record. Instructions in a rules file are only advice; an agent can skip them. REVATHI enforces the important parts with hooks the agent can't skip.

## What it does
| | Feature | What you get |
|---|---|---|
| 🛡️ | **Guard** | Blocks catastrophic actions (`rm -rf /`, force-push to main, secrets written into files) and asks before risky ones (`reset --hard`, `DROP TABLE`, publishing) |
| 🧾 | **Proof before "done"** | After a code change, the agent is sent back once until the project's tests pass, or it must say plainly that it didn't verify |
| ↩️ | **Undo** | A snapshot before risky actions; `revathi undo` restores your work (local files only) |
| 📼 | **Recorder** | A tamper-evident log of every action; `revathi log` shows it in plain words |
| 🪤 | **Canary** | Optional decoy credentials that reveal hidden-instruction (prompt injection) attacks |
| 🔍 | **Modes** | `observe` (record only) · `careful` · `balanced` (default) · `full` (local actions run after a snapshot) |
| 🧰 | **Skills** | 16 step-by-step skills (debugging, code review, planning…) and 2 subagents |

## Evidence
From REVATHI's own evals (same model, same prompt, with and without REVATHI): on a task where the user says *"no need to test"* and the obvious fix crashes, correct fixes went **4/5 → 7/8** and actually-tested fixes **1/5 → 7/8**, at about **+2% tokens**. Where the model already tests, REVATHI changes nothing and costs nothing. Small samples, one model: see [evals/FINDINGS.md](evals/FINDINGS.md).

## Install
Needs Python 3.11+.
```bash
pip install revathi
revathi install --dry-run   # see exactly what will change
revathi install             # connect Claude Code and Antigravity
revathi doctor              # check everything is green
```
Restart your AI tools. Then use them as usual: REVATHI works in the background.

`revathi install` merges into your settings (backups kept), never touches your `CLAUDE.md` or rules files, and leaves any skill you already have alone. `revathi uninstall` reverses exactly what it did.

## Commands
| Command | Does |
|---|---|
| `revathi install [--dry-run]` · `uninstall` | Connect / disconnect your AI tools |
| `revathi doctor` | Check each tool, with a real test event |
| `revathi mode [observe\|careful\|balanced\|full]` | Show or set strictness |
| `revathi log [--list] [--session ID]` | What the agent did |
| `revathi undo [--list] [ID]` | Restore a snapshot |
| `revathi canary plant <dir>` · `status` | Plant decoy credentials |

## Known limits
- Undo covers local files only: not pushes, published packages, sent messages or databases.
- The guard matches command patterns; a determined attacker can find wording it misses. It is a safety net, not a sandbox.
- The proof check knows a test ran and passed, not whether the tests are good.
- **Antigravity:** the hooks install and pass `doctor`, but have not yet been confirmed in a live Antigravity session. Antigravity 2.0 did not load global hooks in our test.

## Docs
[Developer guide](revathi_dev_guide.md) · [Decisions](revathi_decisions.md) · [Changelog](CHANGELOG.md) · [Evals](evals/README.md)

## License
[MIT](LICENSE)
