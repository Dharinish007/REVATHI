# Claude Code adapter

`hook.py` is one script for four Claude Code hook events. It turns each event into a REVATHI `Event` and calls the engine.

| Hook event | Engine part | What happens |
|---|---|---|
| `PreToolUse` | 🛡️ guard | `deny` / `ask` / no opinion. Blocked and asked actions are recorded |
| `PostToolUse` | 📼 recorder | What ran or changed. Test/build/lint commands are marked `check: pass` |
| `PostToolUseFailure` | 📼 recorder | Same, marked failed (`check: fail` for checks) |
| `Stop` | 🧾 proof | If code changed and no check passed afterwards → `block` once, with the reason. If the agent stops again, it may finish and the log records `unproven` |

| Claude Code tool | Event kind | Guard checks |
|---|---|---|
| `Bash`, `PowerShell` | command | dangerous commands, secrets in the command |
| `Write`, `Edit`, `MultiEdit` | write | secrets in the new text (`.env` files allowed) |
| anything else | other | nothing (not recorded) |

Logs: `~/.revathi/logs/<session>.jsonl` (override with `REVATHI_HOME`). No command output is stored; secrets are replaced with `[secret]`.
Fail behavior: guard crash → `ask` (D10). Recorder or proof crash → the agent carries on (never trapped).

## Known limits
- Files changed through shell commands (`sed -i`, `echo >`) are not seen as code edits; only `Write`/`Edit`/`MultiEdit` are.
- A check is recognized by its command (`policy/default.toml` → `[proof]`). Unusual test commands need adding there.
- "Passed" = exit code 0 and no failure text in the output (catches `pytest | tail` hiding a failure). It cannot judge whether the tests are meaningful.

## Turn it on (manual, until `revathi install` exists in Phase 4)
Copy `settings.example.json` into your project's `.claude/settings.json` (or `~/.claude/settings.json` for all projects) and replace `<ABSOLUTE-PATH-TO>` with the real folder. Restart the Claude Code session. Needs Python 3.11+ on PATH.

## Test
`python -m unittest discover -s tests` from the REVATHI root.
