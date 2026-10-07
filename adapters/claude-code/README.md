# Claude Code adapter

`hook.py` is a **PreToolUse** hook. It turns Claude Code's event (`tool_name`, `tool_input`) into a REVATHI `Event`, asks `engine/guard.py`, and answers with `permissionDecision` = `deny` or `ask` (no output = no opinion).

| Claude Code tool | Event kind | Checked for |
|---|---|---|
| `Bash`, `PowerShell` | command | dangerous commands, secrets in the command |
| `Write`, `Edit`, `MultiEdit` | write | secrets in the new text (`.env` files allowed) |
| anything else | other | nothing |

If the guard crashes on a command or write, the hook answers `ask` so the user decides (fail safe).

## Turn it on (manual, until `revathi install` exists in Phase 4)
Add to `.claude/settings.json` (project) or `~/.claude/settings.json` (all projects), with the absolute path to this file:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|PowerShell|Write|Edit|MultiEdit",
        "hooks": [{ "type": "command", "command": "python \"<ABSOLUTE-PATH>/REVATHI/adapters/claude-code/hook.py\"", "timeout": 10 }]
      }
    ]
  }
}
```
Restart the Claude Code session after editing settings. Needs Python 3.11+ on PATH.

## Test
`python -m unittest discover -s tests` from the REVATHI root.
