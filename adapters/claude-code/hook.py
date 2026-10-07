"""Claude Code PreToolUse hook: translate the event, ask the REVATHI guard, answer in Claude Code's format.

Always exits 0; the decision travels as JSON on stdout. No output = no opinion (normal permissions apply).
If the guard itself fails on an action it should check, the action is sent to the user to confirm (fail safe).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # REVATHI root, for "engine"

from engine import guard  # noqa: E402
from engine.event import COMMAND, OTHER, WRITE, Decision, Event  # noqa: E402

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
    tool = raw.get("tool_name", "")
    tool_input = raw.get("tool_input") or {}
    if tool in COMMAND_TOOLS:
        return Event("claude-code", COMMAND, command=str(tool_input.get("command", "")), raw=raw)
    if tool in WRITE_TOOLS:
        return Event("claude-code", WRITE, path=str(tool_input.get("file_path", "")),
                     texts=list(_new_texts(tool_input)), raw=raw)
    return Event("claude-code", OTHER, raw=raw)


def answer(decision):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision.verdict,
        "permissionDecisionReason": f"REVATHI guard: {decision.reason}",
    }}))


def main():
    try:
        raw = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return  # not a tool event we can read
    if not isinstance(raw, dict):
        return
    event = to_event(raw)
    if event.kind == OTHER:
        return
    try:
        decision = guard.check(event)
    except Exception as exc:  # fail safe: never silently allow when the check broke
        decision = Decision("ask", f"the safety check failed ({type(exc).__name__}), so please confirm this action yourself")
    if decision:
        answer(decision)


if __name__ == "__main__":
    main()
    sys.exit(0)
