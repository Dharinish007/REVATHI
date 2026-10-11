"""Import tests (Phase 7g): Claude Code auto memory -> REVATHI inbox, never approved.  Run: python -m unittest discover -s tests"""
import os
import re
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


def note(name, kind, description, body):
    return f"---\nname: {name}\ndescription: {description}\nmetadata:\n  type: {kind}\n---\n\n{body}\n"


class Import(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="revathi-home-")
        self.claude = Path(tempfile.mkdtemp(prefix="claude-home-"))
        self.work = Path(tempfile.mkdtemp(prefix="revathi-proj-"))
        self._old = os.environ.get("REVATHI_HOME")
        os.environ["REVATHI_HOME"] = self.home
        here = self.claude / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(self.work.resolve())) / "memory"
        other = self.claude / "projects" / "D--elsewhere" / "memory"
        here.mkdir(parents=True)
        other.mkdir(parents=True)
        (here / "MEMORY.md").write_text("- [Tables](prefs.md) — hook\n", encoding="utf-8")
        (here / "prefs.md").write_text(note("tables", "feedback", "User wants short answers with tables",
                                            "Use tables. **Why:** asked twice."), encoding="utf-8")
        (here / "role.md").write_text(note("role", "user", "User is a Python developer", "Knows Python well."),
                                      encoding="utf-8")
        (here / "deploy.md").write_text(note("deploy", "project", "Deploys go through staging first",
                                             "Never deploy straight to prod."), encoding="utf-8")
        (other / "other.md").write_text(note("other", "project", "Other project uses Go", "Go 1.22."),
                                        encoding="utf-8")
        self.here = here

    def tearDown(self):
        if self._old is None:
            os.environ.pop("REVATHI_HOME", None)
        else:
            os.environ["REVATHI_HOME"] = self._old
        for d in (self.home, self.claude, self.work):
            shutil.rmtree(d, ignore_errors=True)

    def run_import(self, *extra):
        out = subprocess.run([sys.executable, str(CLI), "memory", "import", "--from", "claude", *extra],
                             capture_output=True, text=True, encoding="utf-8",
                             env={**os.environ, "REVATHI_HOME": self.home, "CLAUDE_CONFIG_DIR": str(self.claude)})
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        return out.stdout

    def titles(self):
        return {n["meta"]["title"]: n["meta"] for n in memory.notes("inbox")}

    def test_global_notes_land_in_inbox_unapproved(self):
        out = self.run_import()
        self.assertIn("Imported 2 note(s)", out)
        found = self.titles()
        self.assertEqual(set(found), {"User wants short answers with tables", "User is a Python developer"})
        prefs = found["User wants short answers with tables"]
        self.assertEqual(prefs["type"], "preference")
        self.assertEqual(prefs["generated"]["by"], "claude-code-auto-memory")
        self.assertTrue(prefs["sources"][0].startswith("claude-auto-memory:"))
        self.assertEqual(memory.approved(), [])

    def test_project_notes_only_for_the_named_project(self):
        self.run_import("--project", str(self.work))
        found = self.titles()
        self.assertIn("Deploys go through staging first", found)
        self.assertNotIn("Other project uses Go", found)
        deploy = found["Deploys go through staging first"]["x-revathi"]
        self.assertEqual((deploy["scope"], deploy["project"]), ("project", memory.project_id(self.work)))

    def test_reimport_skips_known_notes_but_catches_edits(self):
        self.run_import()
        self.assertIn("Imported 0 note(s)", self.run_import())
        (self.here / "role.md").write_text(note("role", "user", "User is a Python and Go developer", "Both."),
                                           encoding="utf-8")
        self.assertIn("Imported 1 note(s)", self.run_import())

    def test_rejected_import_is_not_suggested_again(self):
        self.run_import()
        for n in memory.notes("inbox"):
            memory.reject(n["id"])
        self.assertIn("Imported 0 note(s)", self.run_import())

    def test_secret_in_a_claude_note_is_refused(self):
        fake_key = "sk-ant-" + "Qq7w" * 12
        (self.here / "key.md").write_text(note("key", "user", "API key", f"key is {fake_key}"), encoding="utf-8")
        out = self.run_import()
        self.assertIn("not imported", out)
        self.assertNotIn("API key", self.titles())


if __name__ == "__main__":
    unittest.main()
