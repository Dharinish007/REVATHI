"""Proof: the agent may not finish a turn in which it changed code until a check has passed after the last change."""
import os
import re

from engine.event import Decision

# Where a shell command writes files: redirects, tee, PowerShell writers (same shape as the guard's secret check).
_REDIRECT = re.compile(
    r"""(?:>>?|\btee\s+(?:-a\s+)?|\b(?:Out-File|Set-Content|Add-Content)\s+(?:-(?:File)?Path\s+)?)\s*["']?([^\s"'|;&>]+)""",
    re.I)
_IN_PLACE = re.compile(r"\b(sed|perl)\b[^|;&]*\s-\w*i", re.I)  # sed -i, perl -pi


def shell_edits(command, pol):
    """Code files a shell command writes (sed -i, perl -i, >, >>, tee, Set-Content, Out-File)."""
    paths = [p for p in _REDIRECT.findall(command)]
    for segment in re.split(r"[|;&]+", command):
        if _IN_PLACE.search(segment):
            paths += [w.strip("\"'") for w in segment.split()[1:]]
    seen = []
    for p in paths:
        if is_code(p, pol) and p not in seen:
            seen.append(p)
    return seen


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


TEST_NAME = re.compile(r"^(test_.+\.py|.+_test\.(py|go)|.+\.(test|spec)\.[cm]?[jt]sx?)$", re.I)


def nearby_tests(paths, limit=4):
    """Names of the project's own test files near the edited files (same folder, a tests/ folder, one level up)."""
    found = []
    for path in paths:
        folder = os.path.dirname(os.path.abspath(path))
        for base in (folder, os.path.dirname(folder)):
            for where in (base, os.path.join(base, "tests"), os.path.join(base, "test")):
                try:
                    names = sorted(os.listdir(where))
                except OSError:
                    continue
                found += [n for n in names if TEST_NAME.match(n) and n not in found]
    return found[:limit]


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
    edited_paths = [r["path"] for r in records[:last_edit + 1]
                    if r.get("event") == "post" and r.get("kind") == "write" and r.get("path")]
    checks = [r for r in records[last_edit + 1:] if r.get("event") == "post" and r.get("check")]
    if any(r["check"] == "pass" for r in checks):
        return None
    files = sorted(set(changed))
    shown = ", ".join(files[:3]) + (f" and {len(files) - 3} more" if len(files) > 3 else "")
    if checks:
        return Decision("block", f"the last check after your code change failed (`{checks[-1].get('command', '')}`). "
                                 "Fix it and run the check again, or tell the user plainly that it is failing.")
    tests = nearby_tests(edited_paths)
    if tests:  # point at the project's own tests: an invented one-off check can miss what they catch
        return Decision("block", f"you changed code ({shown}) but no test has passed since. This project has its own "
                                 f"tests ({', '.join(tests)}): run them, not just a one-off check. If they can't run, "
                                 "tell the user that plainly instead of saying it works.")
    return Decision("block", f"you changed code ({shown}) but no test, build or lint check has passed since. "
                             "Run the project's checks now. If there is no way to check, tell the user that plainly "
                             "instead of saying it works.")
