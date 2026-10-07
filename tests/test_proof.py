"""Recorder + proof tests, end to end through the Claude Code adapter.  Run: python -m unittest discover -s tests"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "adapters" / "claude-code" / "hook.py"
sys.path.insert(0, str(ROOT))

from engine import log  # noqa: E402

FAKE_ANT = "sk-" + "ant-api03-Zx9Qw8Er7Ty6Ui5Op4As3Df2Gh1Jk0Lz"


class Session:
    """Feeds one simulated Claude Code session through the hook."""

    def __init__(self, home, sid="s1"):
        self.home, self.sid = home, sid

    def send(self, event):
        env = {**os.environ, "REVATHI_HOME": self.home}
        out = subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"session_id": self.sid, **event}),
                             capture_output=True, text=True, env=env)
        assert out.returncode == 0, out.stderr
        return json.loads(out.stdout) if out.stdout.strip() else None

    def edit(self, path="app.py"):
        return self.send({"hook_event_name": "PostToolUse", "tool_name": "Edit",
                          "tool_input": {"file_path": path, "old_string": "a", "new_string": "b"},
                          "tool_response": {"filePath": path}})

    def run(self, command, ok=True, stdout=""):
        if ok:
            return self.send({"hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_input": {"command": command},
                              "tool_response": {"stdout": stdout, "stderr": "", "interrupted": False}})
        return self.send({"hook_event_name": "PostToolUseFailure", "tool_name": "Bash", "tool_input": {"command": command},
                          "error": "Exit code 1\n" + stdout, "is_interrupt": False})

    def stop(self, active=False):
        return self.send({"hook_event_name": "Stop", "stop_hook_active": active, "last_assistant_message": "Done."})

    def records(self):
        os.environ["REVATHI_HOME"] = self.home
        return log.read(self.sid)

    def log_path(self):
        os.environ["REVATHI_HOME"] = self.home
        return log.session_file(self.sid)


class ProofTests(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="revathi-test-")
        self.s = Session(self.home)

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def assertBlocked(self, out, words):
        self.assertIsNotNone(out)
        self.assertEqual(out["decision"], "block")
        self.assertTrue(out["reason"].startswith("REVATHI proof check: "))
        self.assertIn(words, out["reason"])

    def test_no_code_change_can_finish(self):
        self.s.run("ls")
        self.assertIsNone(self.s.stop())

    def test_docs_only_change_can_finish(self):
        self.s.edit("README.md")
        self.assertIsNone(self.s.stop())

    def test_code_change_without_check_is_blocked(self):
        self.s.edit("app.py")
        self.assertBlocked(self.s.stop(), "app.py")

    def test_code_change_then_passing_check_can_finish(self):
        self.s.edit("app.py")
        self.s.run("python -m pytest -q", stdout="3 passed in 0.1s")
        self.assertIsNone(self.s.stop())

    def test_failing_check_is_blocked(self):
        self.s.edit("app.py")
        self.s.run("npm test", ok=False, stdout="1 failing")
        self.assertBlocked(self.s.stop(), "failed")

    def test_failure_hidden_by_pipe_is_caught(self):
        self.s.edit("app.py")
        self.s.run("pytest -q | tail -3", stdout="1 failed, 2 passed in 0.2s")
        self.assertBlocked(self.s.stop(), "failed")

    def test_forced_success_does_not_count(self):
        self.s.edit("app.py")
        self.s.run("pytest || true", stdout="")
        self.assertBlocked(self.s.stop(), "no test, build or lint check has passed")

    def test_check_before_the_last_edit_does_not_count(self):
        self.s.edit("a.py")
        self.s.run("pytest", stdout="5 passed")
        self.s.edit("b.py")
        self.assertBlocked(self.s.stop(), "b.py")

    def test_blocks_only_once(self):
        self.s.edit("app.py")
        self.assertIsNotNone(self.s.stop())
        self.assertIsNone(self.s.stop(active=True))
        self.assertEqual([r["verdict"] for r in self.s.records() if r["event"] == "stop"], ["block", "unproven"])

    def test_disclosed_gap_does_not_block_later_turns(self):
        # Live test 2026-10-08: an edit already recorded as unproven blocked every later turn.
        self.s.edit("calc.py")
        self.s.stop()
        self.s.stop(active=True)
        self.s.edit("NOTES.md")
        self.assertIsNone(self.s.stop())

    def test_new_code_change_after_gap_is_checked_again(self):
        self.s.edit("calc.py")
        self.s.stop()
        self.s.stop(active=True)
        self.s.edit("other.py")
        self.assertBlocked(self.s.stop(), "other.py")
        self.assertNotIn("calc.py", self.s.stop()["reason"])

    def test_sessions_are_separate(self):
        self.s.edit("app.py")
        self.assertIsNone(Session(self.home, "other").stop())


class RecorderTests(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="revathi-test-")
        self.s = Session(self.home)

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def test_actions_are_recorded_and_chained(self):
        self.s.send({"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "git reset --hard"}})
        self.s.edit("app.py")
        self.s.run("pytest", stdout="1 passed")
        records = self.s.records()
        self.assertEqual([r["event"] for r in records], ["pre", "post", "post"])
        self.assertEqual(records[0]["verdict"], "ask")
        self.assertEqual(records[2]["check"], "pass")
        self.assertTrue(log.chain_ok(records))

    def test_tampering_is_detected(self):
        self.s.run("ls")
        self.s.run("pwd")
        path = self.s.log_path()
        lines = path.read_text(encoding="utf-8").splitlines()
        lines[0] = lines[0].replace('"ls"', '"rm -rf build"')
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.assertFalse(log.chain_ok(self.s.records()))

    def test_secrets_are_redacted(self):
        self.s.run(f"echo 'KEY={FAKE_ANT}' >> .env")
        text = self.s.log_path().read_text(encoding="utf-8")
        self.assertNotIn(FAKE_ANT, text)
        self.assertIn("[secret]", text)

    def test_other_tools_are_not_recorded(self):
        self.s.send({"hook_event_name": "PostToolUse", "tool_name": "Read", "tool_input": {"file_path": ".env"}})
        self.assertEqual(self.s.records(), [])


if __name__ == "__main__":
    unittest.main()
