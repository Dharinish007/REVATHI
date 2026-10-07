"""Antigravity adapter tests: same engine, Antigravity's event and answer shapes.  Run: python -m unittest discover -s tests"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "adapters" / "antigravity" / "hook.py"
SK = "sk-" + "ant-api03-abcdefghijklmnopqrstuvwxyz"
GHP = "ghp_" + "b" * 36


class AntigravityHook(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="revathi-ag-")
        self.env = {**os.environ, "REVATHI_HOME": self.home}

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def send(self, event_name, tool=None, args=None, **extra):
        raw = {"conversationId": "c1", "workspacePaths": [self.home], **extra}
        if tool:
            raw["toolCall"] = {"name": tool, "args": args or {}}
        out = subprocess.run([sys.executable, str(HOOK), event_name], input=json.dumps(raw), capture_output=True,
                             text=True, env=self.env)
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.loads(out.stdout)

    def verdict(self, tool, args):
        decision = self.send("PreToolUse", tool, args).get("decision", "pass")
        return "ask" if decision == "force_ask" else decision

    def test_ask_is_force_ask(self):
        # "ask" would respect Antigravity's "Always Allow" and silently pass (seen live 2026-10-08)
        out = self.send("PreToolUse", "run_command", {"CommandLine": "git reset --hard", "Cwd": "/w"})
        self.assertEqual(out["decision"], "force_ask")

    # Ported from the Agentic OS Antigravity cases
    def test_ported_cases(self):
        cases = [
            ("run_command", {"CommandLine": "rm -rf ~", "Cwd": "/w"}, "deny"),
            ("run_command", {"CommandLine": "git reset --hard", "Cwd": "/w"}, "ask"),
            ("run_command", {"CommandLine": "npm test", "Cwd": "/w"}, "pass"),
            ("write_to_file", {"TargetFile": r"C:\w\config.py", "CodeContent": 'KEY = "AKIA' + 'ABCDEFGHIJKLMNOP"'}, "deny"),
            ("replace_file_content", {"TargetFile": "/w/a.py", "TargetContent": f'k = "{SK}"',
                                      "ReplacementContent": 'k = os.environ["K"]'}, "pass"),
            ("multi_replace_file_content", {"TargetFile": "/w/a.py", "ReplacementChunks": [
                {"TargetContent": "x", "ReplacementContent": f'token = "{GHP}"'}]}, "deny"),
            ("write_to_file", {"TargetFile": r"C:\w\.env", "CodeContent": f"K={SK}"}, "pass"),
            ("view_file", {"AbsolutePath": "/w/.env"}, "pass"),
        ]
        for tool, args, expected in cases:
            with self.subTest(tool=tool, args=args):
                self.assertEqual(self.verdict(tool, args), expected)

    def test_holes_are_closed_here_too(self):
        self.assertEqual(self.verdict("run_command", {"CommandLine": "git -C . reset --hard", "Cwd": "/w"}), "ask")
        self.assertEqual(self.verdict("run_command", {"CommandLine": f'echo K="{SK}" > c.py', "Cwd": "/w"}), "deny")

    def test_reason_format(self):
        out = self.send("PreToolUse", "run_command", {"CommandLine": "git reset --hard", "Cwd": "/w"})
        self.assertTrue(out["reason"].startswith("REVATHI guard: "))

    def test_proof_sends_back_once(self):
        path = os.path.join(self.home, "app.py")
        self.send("PostToolUse", "write_to_file", {"TargetFile": path, "CodeContent": "x = 1"}, error="")
        first = self.send("Stop", executionNum=1, terminationReason="done")
        self.assertEqual(first["decision"], "continue")
        self.assertIn("app.py", first["reason"])
        self.assertEqual(self.send("Stop", executionNum=2, terminationReason="done"), {})

    def test_failed_command_is_a_failed_check(self):
        path = os.path.join(self.home, "app.py")
        self.send("PostToolUse", "write_to_file", {"TargetFile": path, "CodeContent": "x = 1"}, error="")
        self.send("PostToolUse", "run_command", {"CommandLine": "pytest", "Cwd": self.home}, error="exit status 1")
        self.assertIn("failed", self.send("Stop")["reason"])
        self.send("PostToolUse", "run_command", {"CommandLine": "pytest", "Cwd": self.home}, error="")
        self.assertEqual(self.send("Stop"), {})

    def test_bad_input_answers_empty(self):
        out = subprocess.run([sys.executable, str(HOOK), "PreToolUse"], input="nope", capture_output=True, text=True,
                             env=self.env)
        self.assertEqual(json.loads(out.stdout), {})


if __name__ == "__main__":
    unittest.main()
