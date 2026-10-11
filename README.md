# 🌸 REVATHI

**The trust layer for AI agents.** REVATHI sits between your AI coding agent and your computer. It stops dangerous actions, won't let the agent say "done" without proof, records what happened, can undo mistakes, and remembers what you decided, across sessions and tools, only with your approval.

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
| 🧠 | **Memory** | Notes you approved (preferences, project facts, lessons) reach every new session in Claude Code and Antigravity. Agents only suggest; you approve in `revathi memory review`. REVATHI also suggests notes from your own work (tests that failed then passed, checks you always run). Notes expire after 6 months; nothing is deleted |
| 🧰 | **Skills** | 16 step-by-step skills (debugging, code review, planning…) and 2 subagents |

## Evidence
From REVATHI's own evals (same model, same prompt, with and without REVATHI): on a task where the user says *"no need to test"* and the obvious fix crashes, correct fixes went **4/5 → 7/8** and actually-tested fixes **1/5 → 7/8**, at about **+2% tokens**. Where the model already tests, REVATHI changes nothing and costs nothing. Small samples, one model: see [evals/FINDINGS.md](evals/FINDINGS.md).

Memory, in a pre-registered eval where the user's past decisions existed only in memory: **0/3 → 3/3** correct, at **+0.9% tokens**. Where the answer is already in the code, memory adds nothing (also measured).

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
| `revathi memory review` | Approve or reject suggested notes (in your own terminal) |
| `revathi memory list` · `search <words>` · `show <id>` · `forget <id>` | See, find and retire notes |
| `revathi memory learn` · `import --from claude` · `tidy` · `check` | Suggest notes from your sessions or Claude Code's memory; archive expired notes; verify the history |
| `revathi memory graph` | A local, offline map of what your agents know |

## Known limits
- Undo covers local files only: not pushes, published packages, sent messages or databases.
- The guard matches command patterns; a determined attacker can find wording it misses. It is a safety net, not a sandbox.
- The proof check knows a test ran and passed, not whether the tests are good.
- **Antigravity:** memory recall is confirmed live in Antigravity IDE; the guard and proof checks pass `doctor` but are not yet confirmed in a live Antigravity session. Antigravity 2.0 did not load global hooks in our test.
- Memory only knows what you approved, and approving a bad note lets it in. It informs the agent; it doesn't make the model smarter.

## Docs
[Developer guide](revathi_dev_guide.md) · [Decisions](revathi_decisions.md) · [Changelog](CHANGELOG.md) · [Evals](evals/README.md)

## License
[MIT](LICENSE)
