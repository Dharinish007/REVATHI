"""Proof: the agent may not finish a turn in which it changed code until a check has passed after the last change."""
import os

from engine.event import Decision


def is_check(command, pol):
    """True if the command counts as a test/build/lint check."""
    if any(p.search(command) for p in pol.not_counted):
        return False
    return any(p.search(command) for p in pol.verify_commands)


def output_failed(text, pol):
    return any(p.search(text or "") for p in pol.failure_output)


def is_code(path, pol):
    return os.path.splitext(str(path))[1].lower() in pol.code_extensions


def _since_last_gap(records):
    """A gap already recorded as "unproven" was disclosed: only judge what happened after it."""
    for i in range(len(records) - 1, -1, -1):
        if records[i].get("event") == "stop" and records[i].get("verdict") == "unproven":
            return records[i + 1:]
    return records


def _code_edits(records, pol):
    """(index of the last code edit or None, names of changed code files)."""
    last_edit, changed = None, []
    for i, r in enumerate(records):
        if r.get("event") == "post" and r.get("kind") == "write" and r.get("ok") and is_code(r.get("path", ""), pol):
            last_edit = i
            changed.append(os.path.basename(r["path"].replace("\\", "/")))
    return last_edit, changed


def already_sent_back(records, pol):
    """True if the agent was already sent back once since its last code change (block once, D15)."""
    records = _since_last_gap(records)
    last_edit, _ = _code_edits(records, pol)
    start = 0 if last_edit is None else last_edit + 1
    return any(r.get("event") == "stop" and r.get("verdict") == "block" for r in records[start:])


def check(records, pol):
    """Look at the session log and return a "block" Decision, or None if finishing is fine."""
    records = _since_last_gap(records)
    last_edit, changed = _code_edits(records, pol)
    if last_edit is None:
        return None  # no code changed: nothing to prove
    checks = [r for r in records[last_edit + 1:] if r.get("event") == "post" and r.get("check")]
    if any(r["check"] == "pass" for r in checks):
        return None
    files = sorted(set(changed))
    shown = ", ".join(files[:3]) + (f" and {len(files) - 3} more" if len(files) > 3 else "")
    if checks:
        return Decision("block", f"the last check after your code change failed (`{checks[-1].get('command', '')}`). "
                                 "Fix it and run the check again, or tell the user plainly that it is failing.")
    return Decision("block", f"you changed code ({shown}) but no test, build or lint check has passed since. "
                             "Run the project's checks now. If there is no way to check, tell the user that plainly "
                             "instead of saying it works.")
