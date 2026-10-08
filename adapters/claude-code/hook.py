"""Claude Code hook for REVATHI: translate Claude Code events for engine/pipeline.py and answer in its format.

  PreToolUse                      -> pipeline.before: ask / deny / no output
  PostToolUse, PostToolUseFailure -> pipeline.after
  Stop, SubagentStop              -> pipeline.finish: {"decision": "block"} once per code change
SubagentHandback (PreToolUse) -> pipeline.finish too: a subagent delivers its report before it stops.
A subagent's events carry agent_id; they get their own log (<session>.<agent_id>), so its proof check judges
only its own work and the parent's log stays clean.

Always exits 0. If anything here breaks, the agent carries on (the guard itself fails safe inside the pipeline).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # REVATHI root, for "engine"

from engine import pipeline  # noqa: E402
from engine.event import COMMAND, OTHER, WRITE, Event  # noqa: E402

TOOL = "claude-code"
COMMAND_TOOLS = ("Bash", "PowerShell")
WRITE_TOOLS = ("Write", "Edit", "MultiEdit")
NEW_TEXT_KEYS = ("content", "new_string")


def _new_texts(value):
    """Collect new text under content/new_string keys, including nested MultiEdit edits."""
    if isinstance(value, dict):
        for k, v in value.items():
            if isinstance(v, str) and k in NEW_TEXT_KEYS:
                yield v
            elif isinstance(v, (dict, list)):
                yield from _new_texts(v)
    elif isinstance(value, list):
        for v in value:
            yield from _new_texts(v)


def to_event(raw):
    name = raw.get("tool_name", "")
    tool_input = raw.get("tool_input") or {}
    if name in COMMAND_TOOLS:
        return Event(TOOL, COMMAND, name, command=str(tool_input.get("command", "")), raw=raw)
    if name in WRITE_TOOLS:
        return Event(TOOL, WRITE, name, path=str(tool_input.get("file_path", "")),
                     texts=list(_new_texts(tool_input)), raw=raw)
    return Event(TOOL, OTHER, name, raw=raw)


def handle(raw):
    name = raw.get("hook_event_name", "PreToolUse")
    session = str(raw.get("session_id", ""))
    if raw.get("agent_id"):
        session = f"{session}.{raw['agent_id']}"
    if name in ("Stop", "SubagentStop"):
        decision = pipeline.finish(session, sent_back=bool(raw.get("stop_hook_active")))
        if decision:
            return {"decision": "block", "reason": f"REVATHI proof check: {decision.reason}"}
        return None
    if name == "PreToolUse" and raw.get("tool_name") == "SubagentHandback":
        # A subagent hands its report back *before* SubagentStop fires, so the proof check gates the handback:
        # refusing it keeps the subagent working with the reason as feedback (once per code change).
        decision = pipeline.finish(session)
        if decision:
            return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                           "permissionDecisionReason": f"REVATHI proof check: {decision.reason}"}}
        return None
    event = to_event(raw)
    if name == "PreToolUse":
        decision = pipeline.before(session, str(raw.get("cwd", "")), event, raw.get("tool_input"))
        if decision:
            return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision.verdict,
                                           "permissionDecisionReason": f"REVATHI guard: {decision.reason}"}}
    elif name in ("PostToolUse", "PostToolUseFailure"):
        response = raw.get("tool_response")
        output = response.get("stdout", "") if isinstance(response, dict) else str(response or "")
        pipeline.after(session, event, ok=name == "PostToolUse", output=output)
    return None


def main():
    try:
        raw = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return
    if not isinstance(raw, dict):
        return
    try:
        answer = handle(raw)
    except Exception:
        return  # never break the agent's tool because of REVATHI
    if answer:
        print(json.dumps(answer))


if __name__ == "__main__":
    main()
    sys.exit(0)
