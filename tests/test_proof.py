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
        self.assertBlocked(self.s.stop(), "but no test")

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
        out = self.s.stop()
        self.assertBlocked(out, "other.py")
        self.assertNotIn("calc.py", out["reason"])

    def test_blocks_once_even_without_the_tools_flag(self):
        # Antigravity has no stop_hook_active: the log alone must stop a second block for the same change
        self.s.edit("app.py")
        self.assertIsNotNone(self.s.stop())
        self.assertIsNone(self.s.stop())
        self.s.edit("app.py")
        self.assertIsNotNone(self.s.stop(), "a new change gets checked again")

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


class ObserveAndSubagents(unittest.TestCase):
    """observe mode (audit only) and per-subagent logs (agent_id) + SubagentStop."""

    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="revathi-test-")
        self.s = Session(self.home)

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def set_mode(self, mode):
        Path(self.home, "config.json").write_text(json.dumps({"mode": mode}), encoding="utf-8")

    def test_observe_never_interrupts_but_records(self):
        self.set_mode("observe")
        pre = self.s.send({"hook_event_name": "PreToolUse", "tool_name": "Bash", "cwd": self.home,
                           "tool_input": {"command": "git reset --hard"}})
        self.assertIsNone(pre)
        self.s.edit("app.py")
        self.assertIsNone(self.s.stop())
        verdicts = [(r["event"], r.get("verdict")) for r in self.s.records() if r["event"] in ("pre", "stop")]
        self.assertEqual(verdicts, [("pre", "would-ask"), ("stop", "unproven")])
        self.assertFalse(Path(self.home, "snapshots").exists(), "observe mode takes no snapshots")

    def test_subagent_has_its_own_log_and_proof(self):
        sub = {"agent_id": "a1", "agent_type": "general-purpose"}
        self.s.send({"hook_event_name": "PostToolUse", "tool_name": "Edit", **sub,
                     "tool_input": {"file_path": "sub.py", "new_string": "x"}, "tool_response": {}})
        self.assertIsNone(self.s.stop(), "the parent did not change code")
        out = self.s.send({"hook_event_name": "SubagentStop", "stop_hook_active": False, **sub})
        self.assertEqual(out["decision"], "block")
        self.assertIn("sub.py", out["reason"])
        self.assertEqual(self.s.records(), [r for r in self.s.records() if r.get("path") != "sub.py"])


class ShellEdits(unittest.TestCase):
    """Eval pilot 2026-10-08: an agent edited code with `sed -i` in Bash, so REVATHI never saw a code change."""

    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="revathi-test-")
        self.s = Session(self.home)

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def test_shell_edits_need_proof(self):
        for command in ("sed -i 's/a/b/' inventory.py", "perl -pi -e 's/a/b/' app.js",
                        "echo 'x = 1' > config.py", "cat <<EOF >> main.go", "Set-Content -Path app.ps1 -Value x"):
            with self.subTest(command=command):
                s = Session(self.home, sid=command[:8])
                s.run(command)
                self.assertIsNotNone(s.stop(), command)

    def test_edit_and_test_in_one_command_counts_as_verified(self):
        self.s.run("sed -i 's/a/b/' inventory.py && python -m unittest -q", stdout="OK")
        self.assertIsNone(self.s.stop())

    def test_writing_non_code_or_reading_is_not_an_edit(self):
        self.s.run("echo hi > notes.txt")
        self.s.run("cat inventory.py")
        self.s.run("grep -n x app.py > /dev/null")
        self.assertIsNone(self.s.stop())


class Handback(unittest.TestCase):
    """Eval batch 1: subagents deliver their report via SubagentHandback *before* SubagentStop, so the
    proof check must refuse the handback itself (once per code change)."""

    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="revathi-test-")
        self.s = Session(self.home)
        self.sub = {"agent_id": "h1", "agent_type": "general-purpose"}

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def handback(self):
        out = self.s.send({"hook_event_name": "PreToolUse", "tool_name": "SubagentHandback", **self.sub,
                           "tool_input": {"message": "Fixed it."}})
        return out["hookSpecificOutput"] if out else None

    def sub_edit(self):
        self.s.send({"hook_event_name": "PostToolUse", "tool_name": "Edit", **self.sub,
                     "tool_input": {"file_path": "inventory.py", "new_string": "x"}, "tool_response": {}})

    def test_untested_handback_is_refused_once(self):
        self.sub_edit()
        first = self.handback()
        self.assertEqual(first["permissionDecision"], "deny")
        self.assertIn("REVATHI proof check", first["permissionDecisionReason"])
        self.assertIsNone(self.handback(), "second try is allowed and recorded as unproven")

    def test_tested_handback_passes(self):
        self.sub_edit()
        self.s.send({"hook_event_name": "PostToolUse", "tool_name": "Bash", **self.sub,
                     "tool_input": {"command": "python -m unittest"}, "tool_response": {"stdout": "OK"}})
        self.assertIsNone(self.handback())

    def test_handback_without_code_change_passes(self):
        self.assertIsNone(self.handback())


class SendBackNamesTests(unittest.TestCase):
    """Eval batch 2 run 1: sent back, the agent ran its own one-line check and missed the bug the project's test
    would have caught. The reason should point at the project's own tests."""

    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="revathi-test-")
        self.work = Path(tempfile.mkdtemp(prefix="revathi-proj-"))
        (self.work / "test_inventory.py").write_text("", encoding="utf-8")
        (self.work / "tests").mkdir()
        (self.work / "tests" / "test_more.py").write_text("", encoding="utf-8")
        self.s = Session(self.home)

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)
        shutil.rmtree(self.work, ignore_errors=True)

    def test_reason_names_nearby_tests(self):
        self.s.edit(str(self.work / "inventory.py"))
        reason = self.s.stop()["reason"]
        self.assertIn("test_inventory.py", reason)
        self.assertIn("test_more.py", reason)

    def test_no_tests_nearby_keeps_generic_reason(self):
        empty = Path(tempfile.mkdtemp(prefix="revathi-empty-"))
        try:
            self.s.edit(str(empty / "app.py"))
            self.assertIn("Run the project's checks", self.s.stop()["reason"])
        finally:
            shutil.rmtree(empty, ignore_errors=True)


class BatchThreeBugs(unittest.TestCase):
    """Eval batch 3: (1) a shell edit was recorded as a relative path and the send-back named the wrong project's
    tests; (2) `python -m pytest | tail` without pytest installed counted as a passing check."""

    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="revathi-test-")
        self.work = Path(tempfile.mkdtemp(prefix="revathi-proj-"))
        (self.work / "test_inventory.py").write_text("", encoding="utf-8")
        self.s = Session(self.home)

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)
        shutil.rmtree(self.work, ignore_errors=True)

    def run_in(self, command, stdout="", cwd=None):
        return self.s.send({"hook_event_name": "PostToolUse", "tool_name": "Bash", "cwd": cwd or self.home,
                            "tool_input": {"command": command},
                            "tool_response": {"stdout": stdout, "stderr": "", "interrupted": False}})

    def test_shell_edit_path_resolves_against_the_commands_folder(self):
        self.run_in(f'cd "{self.work}" && sed -i "s/a/b/" inventory.py')
        reason = self.s.stop()["reason"]
        self.assertIn("test_inventory.py", reason)
        self.assertNotIn("test_guard.py", reason)

    def test_check_that_did_not_run_is_not_a_pass(self):
        for out in ("C:\\Python\\python.exe: No module named pytest", "bash: pytest: command not found",
                    "'pytest' is not recognized as an internal or external command", "Ran 0 tests in 0.000s\n\nOK",
                    "collected 0 items"):
            with self.subTest(out=out):
                s = Session(self.home, sid=str(abs(hash(out))))
                s.edit(str(self.work / "inventory.py"))
                s.run("python -m pytest -q | tail -5", stdout=out)
                self.assertIsNotNone(s.stop(), out)
