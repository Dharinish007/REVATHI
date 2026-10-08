"""Learner tests (Phase 7d): suggestions from session logs, episodes, dedupe, review.  Run: python -m unittest discover -s tests"""
import json
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
HOOK = ROOT / "adapters" / "claude-code" / "hook.py"

from engine import learn, log, memory, pipeline, policy  # noqa: E402
from engine.event import COMMAND, Event  # noqa: E402


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

    def check(self, session, command, result, project="p1"):
        log.append(session, {"tool": "Bash", "event": "post", "ok": result == "pass", "kind": "command",
                             "command": command, "check": result, "project": project})

    def edit(self, session, path):
        log.append(session, {"tool": "Edit", "event": "post", "ok": True, "kind": "write", "path": path})


class CheckName(unittest.TestCase):
    def test_strips_prefix_and_plumbing(self):
        pol = policy.load().proof
        self.assertEqual(learn.check_name("cd /x && pytest -q 2>&1 | tail -3", pol), "pytest -q")
        self.assertEqual(learn.check_name("python -m unittest discover -s tests", pol),
                         "python -m unittest discover -s tests")
        self.assertIsNone(learn.check_name("ls -la", pol))


class Facts(Base):
    def test_check_used_in_three_sessions_is_suggested_once(self):
        for s in ("s1", "s2", "s3"):
            self.check(s, "cd /repo && pytest -q 2>&1 | tail -3", "pass")
        result = learn.mine()
        self.assertEqual(len(result["proposed"]), 1)
        note = result["proposed"][0]
        self.assertIn("pytest -q", note["meta"]["title"])
        self.assertEqual(note["meta"]["x-revathi"]["scope"], "project")
        self.assertEqual(note["meta"]["x-revathi"]["project"], "p1")
        self.assertEqual(len(note["meta"]["sources"]), 3)
        self.assertEqual(memory.approved(), [])  # suggested, never approved by the learner
        self.assertEqual(learn.mine()["proposed"], [])  # already waiting: not suggested twice

    def test_rejected_suggestion_never_comes_back(self):
        for s in ("s1", "s2", "s3"):
            self.check(s, "pytest -q", "pass")
        memory.reject(learn.mine()["proposed"][0]["id"])
        self.check("s4", "pytest -q", "pass")
        self.assertEqual(learn.mine()["proposed"], [])

    def test_too_few_sessions_or_failures_only_give_nothing(self):
        self.check("s1", "pytest -q", "pass")
        self.check("s2", "pytest -q", "pass")
        for s in ("s3", "s4", "s5"):
            self.check(s, "npm test", "fail")
        self.assertEqual(learn.mine()["proposed"], [])

    def test_projects_are_kept_apart(self):
        for s, p in (("s1", "p1"), ("s2", "p2"), ("s3", "p3")):
            self.check(s, "pytest -q", "pass", project=p)
        self.assertEqual(learn.mine()["proposed"], [])


class Episodes(Base):
    def test_fail_change_pass_is_recorded_as_evidence_only(self):
        self.check("s1", "pytest -q", "fail")
        self.edit("s1", "/repo/calc.py")
        self.check("s1", "pytest -q", "pass")
        self.assertEqual(learn.mine()["episodes"], 1)
        episodes = memory.notes("episode")
        self.assertEqual(len(episodes), 1)
        self.assertIn("calc.py", episodes[0]["meta"]["title"])
        self.assertEqual(memory.approved(), [])
        self.assertNotIn("calc.py", memory.index_text("", ""))  # evidence is never shown to the agent
        self.assertEqual(learn.mine()["episodes"], 0)  # not recorded twice
        self.assertTrue(memory.check()["history_ok"])

    def test_pass_without_a_fix_is_not_an_episode(self):
        self.check("s1", "pytest -q", "fail")
        self.check("s1", "pytest -q", "pass")  # flaky test, nothing changed
        self.assertEqual(learn.mine()["episodes"], 0)


class Recorder(Base):
    def test_checks_are_recorded_with_their_project(self):
        work = tempfile.mkdtemp(prefix="revathi-proj-")
        try:
            event = Event("claude-code", COMMAND, "Bash", command="pytest -q")
            pipeline.after("s1", event, ok=True, output="1 passed", cwd=work)
            self.assertEqual(log.read("s1")[-1]["project"], memory.project_id(work))
        finally:
            shutil.rmtree(work, ignore_errors=True)


class Review(Base):
    def test_waiting_suggestions_are_mentioned_at_session_start(self):
        memory.propose("fact", "Uses pytest", "x", ["chat"])
        self.assertIn("1 memory suggestion(s) are waiting", memory.index_text("", ""))

    def test_review_needs_a_person_at_a_terminal(self):
        memory.propose("fact", "Uses pytest", "x", ["chat"])
        out = subprocess.run([sys.executable, str(CLI), "memory", "review"], input="a\n", capture_output=True,
                             text=True, env={**os.environ, "REVATHI_HOME": self.home})
        self.assertEqual(out.returncode, 1)
        self.assertIn("your own terminal", out.stdout)
        self.assertEqual(memory.approved(), [])

    def test_agent_cannot_run_review(self):
        for command in ("revathi memory review", "echo a | revathi memory review"):
            event = {"session_id": "s1", "hook_event_name": "PreToolUse", "cwd": self.home, "tool_name": "Bash",
                     "tool_input": {"command": command}}
            out = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(event), capture_output=True,
                                 text=True, env={**os.environ, "REVATHI_HOME": self.home})
            self.assertEqual(json.loads(out.stdout)["hookSpecificOutput"]["permissionDecision"], "deny", command)

    def test_learn_command_only_suggests(self):
        for s in ("s1", "s2", "s3"):
            self.check(s, "pytest -q", "pass")
        out = subprocess.run([sys.executable, str(CLI), "memory", "learn"], capture_output=True, text=True,
                             env={**os.environ, "REVATHI_HOME": self.home})
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("1 new suggestion", out.stdout)
        self.assertEqual(memory.approved(), [])


if __name__ == "__main__":
    unittest.main()
