"""Recorder: an append-only, hash-chained log of what the agent did, one JSONL file per session.

Location: $REVATHI_HOME/logs/<session>.jsonl (default ~/.revathi). Commands are trimmed and secrets redacted;
command output is never stored. Each line carries the previous line's hash, so edits to the file are detectable.
"""
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

MAX_TEXT = 500
GENESIS = "0" * 64


def home():
    return Path(os.environ.get("REVATHI_HOME") or Path.home() / ".revathi")


def session_file(session):
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", session or "unknown")[:100]
    return home() / "logs" / f"{safe}.jsonl"


def redact(text, secret_patterns):
    for pattern in secret_patterns:
        text = pattern.sub("[secret]", text)
    return text[:MAX_TEXT]


def _digest(prev, entry):
    body = json.dumps(entry, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256((prev + body).encode("utf-8")).hexdigest()


def read(session):
    """All readable records of a session, oldest first."""
    path = session_file(session)
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def append(session, entry):
    """Add one record; returns it with ts, prev and hash filled in."""
    path = session_file(session)
    path.parent.mkdir(parents=True, exist_ok=True)
    records = read(session)
    prev = records[-1].get("hash", GENESIS) if records else GENESIS
    entry = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), **entry, "prev": prev}
    entry["hash"] = _digest(prev, entry)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def chain_ok(records):
    """True if no record was changed, removed or reordered."""
    prev = GENESIS
    for record in records:
        body = {k: v for k, v in record.items() if k != "hash"}
        if record.get("prev") != prev or record.get("hash") != _digest(prev, body):
            return False
        prev = record["hash"]
    return True
