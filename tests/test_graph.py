"""Graph tests (Phase 7h): map data, safety of the page, offline, 500 notes.  Run: python -m unittest discover -s tests"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CLI = ROOT / "cli" / "revathi.py"

from cli import graph  # noqa: E402
from engine import memory  # noqa: E402


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
        n = memory.propose(kw.pop("type", "fact"), title, body or title, kw.pop("sources", ["chat"]), **kw)
        return memory.approve(n["id"], by="alice") if approve else n


class Data(Base):
    def test_states_links_and_hubs(self):
        good = self.note("User likes tables", type="preference")
        waiting = self.note("Project uses pytest", approve=False)
        self.note("Checked with `pytest -q`", "Run `pytest -q`.")
        self.note("Checked with `nose`", "Run `nose`.", approve=False)
        ep = memory.record_episode("Fixed calc", "x", ["log:s1#a"], key="episode:s1:x", files=["calc.py"],
                                   check="pytest")
        lesson = self.note("calc.py breaks often", type="lesson", sources=[f"memory:{ep['id']}"], approve=False)
        edited = self.note("Will be edited")
        Path(edited["path"]).write_text(Path(edited["path"]).read_text(encoding="utf-8") + "\nevil", encoding="utf-8")
        gone = self.note("Old fact")
        memory.forget(gone["id"])
        data = graph.graph_data()
        state = {n["id"]: n["state"] for n in data["nodes"] if n["kind"] == "note"}
        self.assertEqual(state[good["id"]], "approved")
        self.assertEqual(state[waiting["id"]], "inbox")
        self.assertEqual(state[ep["id"]], "episode")
        self.assertEqual(state[edited["id"]], "untrusted")
        self.assertEqual(state[gone["id"]], "archive")
        kinds = {(lk["source"], lk["target"], lk["kind"]) for lk in data["links"]}
        self.assertIn((lesson["id"], ep["id"], "evidence"), kinds)
        self.assertIn((good["id"], "hub:user", "place"), kinds)
        self.assertTrue(any(k == "conflict" for _, _, k in kinds))


class Page(Base):
    def test_note_html_can_never_run(self):
        self.note("</script><script>alert(1)</script>", "<img src=x onerror=alert(2)>")
        page = graph.html(graph.graph_data())
        self.assertNotIn("</script><script>alert(1)", page)
        self.assertEqual(page.count("</script>"), 2)  # only the page's own two script tags close
        self.assertNotIn("innerHTML", page)

    def test_page_is_offline(self):
        page = graph.html(graph.graph_data())
        self.assertIsNone(re.search(r"(src|href)\s*=\s*[\"']https?://", page))
        self.assertNotIn("fetch(", page)

    def test_cli_writes_without_opening(self):
        self.note("User likes tables", type="preference")
        out = Path(self.home) / "map.html"
        run = subprocess.run([sys.executable, str(CLI), "memory", "graph", "--no-open", "--out", str(out)],
                             capture_output=True, text=True, encoding="utf-8", env={**os.environ, "REVATHI_HOME": self.home})
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("1 note(s)", run.stdout)
        self.assertIn("User likes tables", out.read_text(encoding="utf-8"))

    def test_500_notes(self):
        for i in range(500):
            memory.propose("fact", f"Fact {i}", f"detail {i}", ["chat"])
        start = time.perf_counter()
        page = graph.html(graph.graph_data())
        took = time.perf_counter() - start
        print(f"\n  graph of 500 notes: {took * 1000:.0f} ms, {len(page) // 1024} KB")
        self.assertEqual(page.count('"kind": "note"'), 500)
        self.assertLess(len(page), 2_000_000)


if __name__ == "__main__":
    unittest.main()
