"""Claude Code hook for REVATHI. One script, dispatched by hook_event_name:

  PreToolUse                      -> guard: deny / ask / no opinion; blocked or asked actions are recorded
  PostToolUse, PostToolUseFailure -> recorder: what ran or changed, and whether a check passed
  Stop                            -> proof: no finishing after a code change until a check has passed (blocks once)

Always exits 0; decisions travel as JSON on stdout. No output = no opinion.
If the guard fails on an action it should check, the user is asked to confirm (fail safe, D10).
The recorder and the proof check never break the tool: if they fail, the agent carries on.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # REVATHI root, for "engine"

from engine import guard, log, proof  # noqa: E402
from engine import policy as policy_mod  # noqa: E402
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


def record(raw, entry):
    try:
        log.append(str(raw.get("session_id", "")), {"tool": raw.get("tool_name", ""), **entry})
    except Exception:
        pass  # a broken recorder must never stop the agent's work


def _summary(event, pol):
    if event.kind == COMMAND:
        return {"kind": COMMAND, "command": log.redact(event.command, pol.guard.secrets)}
    return {"kind": WRITE, "path": event.path}


def pre_tool_use(raw, event):
    try:
        decision = guard.check(event)
    except Exception as exc:  # fail safe: never silently allow when the check broke
        decision = Decision("ask", f"the safety check failed ({type(exc).__name__}), so please confirm this action yourself")
    if not decision:
        return
    try:
        record(raw, {"event": "pre", "verdict": decision.verdict, "reason": decision.reason,
                     **_summary(event, policy_mod.load())})
    except Exception:
        pass
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision.verdict,
        "permissionDecisionReason": f"REVATHI guard: {decision.reason}",
    }}))


def post_tool_use(raw, event, ok):
    pol = policy_mod.load()
    entry = {"event": "post", "ok": ok, **_summary(event, pol)}
    if event.kind == COMMAND and proof.is_check(event.command, pol.proof):
        response = raw.get("tool_response")
        stdout = response.get("stdout", "") if isinstance(response, dict) else str(response or "")
        passed = ok and not proof.output_failed(stdout, pol.proof)
        entry["check"] = "pass" if passed else "fail"
    record(raw, entry)


def stop(raw):
    session = str(raw.get("session_id", ""))
    decision = proof.check(log.read(session), policy_mod.load().proof)
    if not decision:
        return
    if raw.get("stop_hook_active"):
        record(raw, {"event": "stop", "verdict": "unproven", "reason": decision.reason})
        return  # already sent back once: let it finish, the log keeps the gap visible
    record(raw, {"event": "stop", "verdict": "block", "reason": decision.reason})
    print(json.dumps({"decision": "block", "reason": f"REVATHI proof check: {decision.reason}"}))


def main():
    try:
        raw = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return  # not an event we can read
    if not isinstance(raw, dict):
        return
    name = raw.get("hook_event_name", "PreToolUse")
    if name == "Stop":
        try:
            stop(raw)
        except Exception:
            pass  # never trap the agent because the proof check broke
        return
    event = to_event(raw)
    if event.kind == OTHER:
        return
    if name == "PreToolUse":
        pre_tool_use(raw, event)
    elif name in ("PostToolUse", "PostToolUseFailure"):
        try:
            post_tool_use(raw, event, ok=name == "PostToolUse")
        except Exception:
            pass


if __name__ == "__main__":
    main()
    sys.exit(0)
