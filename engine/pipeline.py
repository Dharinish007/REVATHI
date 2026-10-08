"""The tool-neutral flow for every hook event. Adapters translate their tool's events into these three calls.

  before(...)  canary -> guard -> mode -> snapshot -> record; returns a Decision (ask/deny) or None
               (observe mode: records what it would have done, never interrupts)
  after(...)   record what ran or changed, and whether a check passed
  finish(...)  proof check; returns a "block" Decision once per code change, else None
"""
import os

from engine import canary, config, guard, log, proof, undo
from engine import policy as policy_mod
from engine.event import COMMAND, OTHER, WRITE, Decision

NOT_UNDOABLE = " REVATHI could not save a snapshot for this one, so it cannot be undone."
UNDOABLE = " A snapshot was saved first: run `revathi undo` to restore."


def record(session, name, entry):
    try:
        log.append(session, {"tool": name, **entry})
    except Exception:
        pass  # a broken recorder must never stop the agent's work


def _summary(event, pol):
    if event.kind == COMMAND:
        return {"kind": COMMAND, "command": log.redact(event.command, pol.guard.secrets)}
    if event.kind == WRITE:
        return {"kind": WRITE, "path": event.path}
    return {"kind": OTHER}


def _guard(event, mode, pol):
    try:
        decision = guard.check(event, pol.guard)
    except Exception as exc:  # fail safe (D10): never silently allow when the check broke
        return Decision("ask", f"the safety check failed ({type(exc).__name__}), so please confirm this action yourself")
    if not decision and mode == "careful" and event.kind == COMMAND:
        for pattern, reason in pol.careful_ask:
            if pattern.search(guard.normalize_git(event.command)):
                return Decision("ask", f"{reason}. Please confirm this is intended")
    return decision


def _snapshot(session, cwd, event, decision, pol):
    """Save what the action could destroy. Returns the manifest, None if it failed, or False if not needed."""
    if event.kind == WRITE and event.path and (not decision or decision.verdict == "ask"):
        return undo.snapshot_files([event.path], session, f"before {event.name or 'write'} of {event.path}")
    if event.kind == COMMAND and decision and decision.verdict == "ask":
        return undo.snapshot_for_command(cwd, list(guard.recursive_delete_targets(event.command)), session,
                                         f"before: {log.redact(event.command, pol.guard.secrets)}", command=event.command)
    return False


def before(session, cwd, event, tool_input):
    """Decide on an action before it runs."""
    pol = policy_mod.load()
    mode = config.mode()
    decision = None
    try:
        decision = canary.check(tool_input or {})
    except Exception:
        pass  # the canary is an extra alarm; the guard below still runs
    if not decision and event.kind != OTHER:
        decision = _guard(event, mode, pol)
    if mode == "observe":  # audit only: record what REVATHI would have done, never interrupt
        if decision:
            record(session, event.name, {"event": "pre", "verdict": "would-" + decision.verdict, "mode": "observe",
                                         "reason": decision.reason, **_summary(event, pol)})
        return None
    if event.kind != OTHER and not (decision and decision.verdict == "deny"):
        try:
            snap = _snapshot(session, cwd, event, decision, pol)
        except Exception:
            snap = None
        if snap:
            record(session, event.name, {"event": "snapshot", "id": snap["id"], "snapshot": snap["kind"]})
        if decision and snap is not False:
            if snap and decision.undoable and mode == "full":
                record(session, event.name, {"event": "pre", "verdict": "allow", "mode": "full",
                                             "reason": decision.reason, **_summary(event, pol)})
                return None  # full mode: local, undoable action runs without asking
            decision = Decision(decision.verdict, decision.reason + "." + (UNDOABLE if snap else NOT_UNDOABLE),
                                decision.undoable)
    if decision:
        record(session, event.name, {"event": "pre", "verdict": decision.verdict, "reason": decision.reason,
                                     **_summary(event, pol)})
    return decision


def after(session, event, ok, output="", cwd=""):
    """Record an action after it ran (ok = the tool reported success; cwd = the agent's folder, if known)."""
    if event.kind == OTHER:
        return
    pol = policy_mod.load()
    if event.kind == COMMAND:  # code edited through the shell counts as a code edit (recorded before any check)
        base = undo.target_dir(event.command, cwd) if cwd else ""  # follows a leading `cd <dir> &&`
        for path in proof.shell_edits(event.command, pol.proof):
            if base and not os.path.isabs(path):
                path = os.path.normpath(os.path.join(base, path))
            record(session, event.name, {"event": "post", "ok": True, "kind": WRITE, "path": path, "via": "command"})
    entry = {"event": "post", "ok": ok, **_summary(event, pol)}
    if event.kind == COMMAND and proof.is_check(event.command, pol.proof):
        entry["check"] = "pass" if ok and not proof.output_failed(output, pol.proof) else "fail"
    record(session, event.name, entry)


def finish(session, sent_back=False):
    """Called when the agent wants to stop. Returns a "block" Decision at most once per code change."""
    pol = policy_mod.load()
    records = log.read(session)
    decision = proof.check(records, pol.proof)
    if not decision:
        return None
    if config.mode() == "observe":
        record(session, "", {"event": "stop", "verdict": "unproven", "mode": "observe", "reason": decision.reason})
        return None  # audit only: the gap is recorded, the agent is not sent back
    if sent_back or proof.already_sent_back(records, pol.proof):
        record(session, "", {"event": "stop", "verdict": "unproven", "reason": decision.reason})
        return None  # already sent back once: let it finish, the log keeps the gap visible
    record(session, "", {"event": "stop", "verdict": "block", "reason": decision.reason})
    return decision
