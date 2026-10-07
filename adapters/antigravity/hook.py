"""Antigravity hook for REVATHI: translate Antigravity events for engine/pipeline.py and answer in its format.

Called as `hook.py <PreToolUse|PostToolUse|Stop>` (Antigravity's input has no event-name field).
Input (camelCase): conversationId, workspacePaths, toolCall {name, args}; PostToolUse adds `error` (empty on success).
  PreToolUse  -> {"decision": "deny"|"force_ask", "reason": ...} or {}
  PostToolUse -> {}
  Stop        -> {"decision": "continue", "reason": ...} once per code change (sends the agent back), else {}
Antigravity has no "already sent back" flag; the engine tracks that in the session log.
Always exits 0. If anything here breaks, the agent carries on (the guard itself fails safe inside the pipeline).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # REVATHI root, for "engine"

from engine import pipeline  # noqa: E402
from engine.event import COMMAND, OTHER, WRITE, Event  # noqa: E402

TOOL = "antigravity"
WRITE_TOOLS = ("write_to_file", "replace_file_content", "multi_replace_file_content")


def _new_texts(value):
    """New text lives under keys ending in "Content", except TargetContent (the text being replaced)."""
    if isinstance(value, dict):
        for k, v in value.items():
            if isinstance(v, str) and k.endswith("Content") and k != "TargetContent":
                yield v
            elif isinstance(v, (dict, list)):
                yield from _new_texts(v)
    elif isinstance(value, list):
        for v in value:
            yield from _new_texts(v)


def to_event(raw):
    call = raw.get("toolCall") or {}
    name, args = str(call.get("name", "")), call.get("args") or {}
    if name == "run_command":
        return Event(TOOL, COMMAND, name, command=str(args.get("CommandLine", "")), raw=raw)
    if name in WRITE_TOOLS:
        return Event(TOOL, WRITE, name, path=str(args.get("TargetFile", "")), texts=list(_new_texts(args)), raw=raw)
    return Event(TOOL, OTHER, name, raw=raw)


def _cwd(raw):
    args = (raw.get("toolCall") or {}).get("args") or {}
    paths = raw.get("workspacePaths") or []
    return str(args.get("Cwd") or (paths[0] if paths else ""))


def handle(name, raw):
    session = str(raw.get("conversationId", ""))
    if name == "Stop":
        decision = pipeline.finish(session)
        return {"decision": "continue", "reason": f"REVATHI proof check: {decision.reason}"} if decision else {}
    event = to_event(raw)
    if name == "PreToolUse":
        args = (raw.get("toolCall") or {}).get("args")
        decision = pipeline.before(session, _cwd(raw), event, args)
        if not decision:
            return {}
        # "ask" respects Antigravity's "Always Allow"; force_ask always prompts, so REVATHI's asks can't be skipped (D24)
        verdict = "force_ask" if decision.verdict == "ask" else decision.verdict
        return {"decision": verdict, "reason": f"REVATHI guard: {decision.reason}"}
    if name == "PostToolUse":
        pipeline.after(session, event, ok=not raw.get("error"), output=str(raw.get("error") or ""))
    return {}


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "PreToolUse"
    answer = {}
    try:
        raw = json.load(sys.stdin)
        if isinstance(raw, dict):
            answer = handle(name, raw)
    except Exception:
        answer = {}  # never break the agent's tool because of REVATHI
    print(json.dumps(answer))


if __name__ == "__main__":
    main()
    sys.exit(0)
