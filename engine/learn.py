"""Learner (Phase 7d): turn the session logs into memory suggestions. Runs offline, never inside a hook (D32).

  episodes  a check failed, code was changed, and the same check then passed: recorded automatically as
            evidence in memory/episodes/ (never shown to the agent; the ladder in 7f builds on them)
  facts     the same check passed in a project in MIN_SESSIONS or more sessions: proposed to the inbox
            ("this project is checked with `pytest -q`"); the user approves or rejects it

Only checks that passed count as evidence (D33). Every suggestion carries a `key`, so anything already
waiting, approved, rejected or forgotten is never suggested again.
"""
import os
import re

from engine import log, memory, policy, proof

MIN_SESSIONS = 3
_NOISE = re.compile(r"\s*(2>&1|\|\s*(tail|head|grep|tee)\b.*)$")


def check_name(command, pol):
    """The check part of a command line, without cd prefixes and output plumbing ("pytest -q")."""
    for segment in re.split(r"&&|;|\|\|", command):
        while _NOISE.search(segment):  # "pytest 2>&1 | tail -3" -> "pytest"
            segment = _NOISE.sub("", segment)
        segment = segment.strip()
        if proof.is_check(segment, pol):
            return re.sub(r"\s+", " ", segment)[:120]
    return None


def _sessions():
    folder = log.home() / "logs"
    return sorted(p.stem for p in folder.glob("*.jsonl")) if folder.exists() else []


def _known_keys():
    return {(n["meta"].get("x-revathi") or {}).get("key") for n in memory.notes()} - {None}


def _episodes(session, records, pol):
    """(check, project, changed files, record hash) for each fail -> change -> pass in one session."""
    found, failing = [], {}  # check -> (project, files changed since it failed)
    for r in records:
        if r.get("event") != "post":
            continue
        if r.get("kind") == "write" and r.get("ok") and proof.is_code(r.get("path", ""), pol):
            for files in failing.values():
                name = os.path.basename(str(r["path"]).replace("\\", "/"))
                if name not in files[1]:
                    files[1].append(name)
            continue
        check = check_name(r.get("command", ""), pol) if r.get("check") else None
        if not check:
            continue
        if r["check"] == "fail":
            failing.setdefault(check, (r.get("project"), []))
        elif check in failing:
            project, files = failing.pop(check)
            if files:
                found.append((check, project or r.get("project"), files, r.get("hash", "")))
    return found


def mine():
    """Read every session log; record new episodes and propose new facts. Returns a summary dict."""
    pol = policy.load().proof
    known = _known_keys()
    passes = {}  # (project, check) -> {session: record hash}
    episodes, proposed = 0, []
    for session in _sessions():
        records = log.read(session)
        for r in records:
            if r.get("event") == "post" and r.get("check") == "pass" and r.get("project"):
                check = check_name(r.get("command", ""), pol)
                if check:
                    passes.setdefault((r["project"], check), {})[session.split(".")[0]] = r.get("hash", "")
        for check, project, files, digest in _episodes(session, records, pol):
            key = f"episode:{session}:{check}"
            if key in known:
                continue
            memory.record_episode(f"Fixed a failing `{check}` by changing {', '.join(files[:5])}",
                                  f"`{check}` failed, then {', '.join(files)} changed, then it passed.",
                                  [f"log:{session}#{digest[:12]}"], key=key, project_key=project)
            known.add(key)
            episodes += 1
    for (project, check), sessions in sorted(passes.items()):
        key = f"check:{project}:{check}"
        if len(sessions) < MIN_SESSIONS or key in known:
            continue
        sources = [f"log:{s}#{h[:12]}" for s, h in sorted(sessions.items())[:5]]
        note = memory.propose("fact", f"This project is checked with `{check}`",
                              f"`{check}` passed in {len(sessions)} sessions of this project. "
                              f"Run it after changing code.", sources, scope="project",
                              project_key=project, by="revathi-learner", key=key)
        known.add(key)
        proposed.append(note)
    return {"episodes": episodes, "proposed": proposed}
