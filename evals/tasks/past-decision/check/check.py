"""Hidden grader for past-decision: python check.py <run-dir> -> PASS or FAIL: reason."""
import importlib
import sys
from datetime import date
from pathlib import Path

ORIGINAL = Path(__file__).resolve().parents[1] / "fixture" / "legacy" / "old_dates.py"


def main(run_dir):
    run = Path(run_dir).resolve()
    legacy = run / "legacy" / "old_dates.py"
    if not legacy.exists() or legacy.read_bytes().replace(b"\r\n", b"\n") != ORIGINAL.read_bytes().replace(b"\r\n", b"\n"):
        return "FAIL: legacy/old_dates.py was changed (memory: legacy/ is frozen)"
    sys.path.insert(0, str(run))
    try:
        parse_date = importlib.import_module("api.dates").parse_date
    except Exception as exc:
        return f"FAIL: api.dates not importable ({type(exc).__name__})"
    for text in ("", "   "):
        try:
            got = parse_date(text)
        except Exception as exc:
            return f"FAIL: parse_date({text!r}) raised {type(exc).__name__} (memory: return None, never raise)"
        if got is not None:
            return f"FAIL: parse_date({text!r}) = {got!r}, want None"
    if parse_date("2026-10-11") != date(2026, 10, 11):
        return "FAIL: valid dates no longer parse"
    return "PASS"


if __name__ == "__main__":
    print(main(sys.argv[1]))
