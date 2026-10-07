# Antigravity adapter

`hook.py <PreToolUse|PostToolUse|Stop>` translates Antigravity hook events for `engine/pipeline.py`.
Event shapes and answers from the Antigravity hooks docs (https://antigravity.google/docs/hooks, checked 2026-10-08).

| Event | Antigravity input | REVATHI answer |
|---|---|---|
| `PreToolUse` | `toolCall.name` / `toolCall.args`, `conversationId`, `workspacePaths` | `{"decision": "deny"\|"force_ask", "reason"}` or `{}`. `force_ask`, not `ask`: `ask` respects "Always Allow" and would pass silently |
| `PostToolUse` | same + `error` (empty on success) | `{}` (recorded) |
| `Stop` | `executionNum`, `terminationReason` | `{"decision": "continue", "reason"}` once per code change, else `{}` |

| Tool | Kind |
|---|---|
| `run_command` (`CommandLine`, `Cwd`) | command |
| `write_to_file`, `replace_file_content`, `multi_replace_file_content` (`TargetFile`, `*Content`) | write |
| everything else (`view_file`, `read_url_content`, `search_web`) | other: canary only |

Installed by `revathi install` as a `revathi` group in `~/.gemini/config/hooks.json`.
Limits: no exit code, only `error` text; no "already sent back" flag (the engine tracks it in the log).
