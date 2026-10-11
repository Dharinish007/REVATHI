"""Tidy tests (Phase 7e): expiry, duplicates, conflicts; nothing is ever deleted.  Run: python -m unittest discover -s tests"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CLI = ROOT / "cli" / "revathi.py"

from engine import memory  # noqa: E402

LATER = "2099-01-01"


class Base(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="revathi-home-")
        self._old = os.environ.get("REVATHI_HOME")
        os.environ["REVATHI_HOME"] = self.home

    def tearDown(self):
        if self._old is None:
            os.environ.pop("REVATHI_HOME", None)
        else:
            os.environ["REVATHI_HOME"] = self._old
        shutil.rmtree(self.home, ignore_errors=True)

    def note(self, title, body="", approve=True, **kw):
        n = memory.propose(kw.pop("type", "fact"), title, body or title, ["chat"], **kw)
        return memory.approve(n["id"], by="alice") if approve else n


class Expiry(Base):
    def test_approval_sets_six_month_date(self):
        meta = self.note("Uses pytest")["meta"]
        self.assertGreater(meta["stale_after"], meta["verified"][-1]["at"][:10])
        self.assertFalse(memory.stale(meta))
        self.assertTrue(memory.stale(meta, today=LATER))

    def test_old_note_without_date_uses_approval_date(self):
        self.assertTrue(memory.stale({"verified": [{"by": "human:a", "at": "2020-01-01T00:00:00+00:00"}]}))
        self.assertFalse(memory.stale({}))

    def test_expired_notes_stop_being_shown_and_are_archived_not_deleted(self):
        n = self.note("Uses pytest")
        memory.expire(today=LATER)
        self.assertEqual(memory.approved(), [])
        archived = memory.notes("archive")
        self.assertEqual([a["id"] for a in archived], [n["id"]])
        self.assertTrue(archived[0]["meta"]["x-revathi"]["invalid_at"])
        self.assertEqual(memory.history()[-1]["action"], "expire")
        self.assertTrue(memory.check()["history_ok"])

    def test_past_date_is_hidden_even_before_tidy_runs(self):
        n = self.note("Uses pytest")
        path = Path(n["path"])
        text = path.read_text(encoding="utf-8").replace(n["meta"]["stale_after"], "2000-01-01")
        path.write_text(text, encoding="utf-8")  # (also breaks the approval hash: doubly hidden)
        self.assertEqual(memory.approved(), [])


class Findings(Base):
    def test_duplicate_suggestion_is_flagged(self):
        self.note("This project is checked with `pytest -q`", "Run `pytest -q` after changing code.")
        self.note("This project is checked with `pytest -q`", "Run `pytest -q` after changing code.", approve=False)
        kinds = [f["kind"] for f in memory.findings()]
        self.assertEqual(kinds, ["duplicate"])

    def test_conflicting_values_are_flagged(self):
        self.note("This project is checked with `pytest -q`", "Run `pytest -q` after changing code.")
        self.note("This project is checked with `nose`", "Run `nose` after changing code.", approve=False)
        self.assertEqual([f["kind"] for f in memory.findings()], ["conflict"])

    def test_unrelated_or_differently_scoped_notes_are_not_flagged(self):
        work = tempfile.mkdtemp()
        try:
            self.note("User likes tables", type="preference")
            self.note("Release steps: bump the version, build, tag", "Bump, build, tag.")
            self.note("This project is checked with `pytest -q`", "Run `pytest -q` after changing code.")
            self.note("This project is checked with `nose`", "Run `nose` after changing code.",
                      scope="project", project=work)
            self.assertEqual(memory.findings(), [])
        finally:
            shutil.rmtree(work, ignore_errors=True)

    def test_tidy_command_reports_in_plain_english(self):
        self.note("This project is checked with `pytest -q`", "Run `pytest -q` after changing code.")
        self.note("This project is checked with `nose`", "Run `nose` after changing code.", approve=False)
        out = subprocess.run([sys.executable, str(CLI), "memory", "tidy"], capture_output=True, text=True, encoding="utf-8",
                             env={**os.environ, "REVATHI_HOME": self.home})
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("may contradict each other", out.stdout)
        self.assertEqual(len(memory.notes("inbox")), 1)  # tidy flags; only the user rejects


if __name__ == "__main__":
    unittest.main()
