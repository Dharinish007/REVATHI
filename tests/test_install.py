"""install / doctor / mode / uninstall in a fake home folder (your real settings are never touched).
Run: python -m unittest discover -s tests"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "cli" / "revathi.py"
GIT_ID = ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]


class InstallFlow(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix="revathi fake home-"))  # a space, like many real home folders
        self.env = {**os.environ, "HOME": str(self.home), "USERPROFILE": str(self.home),
                    "REVATHI_HOME": str(self.home / ".revathi"), "REVATHI_NO_CLAUDE_CLI": "1"}
        self.env.pop("CLAUDE_CONFIG_DIR", None)
        self.claude = self.home / ".claude"
        self.ag = self.home / ".gemini" / "config"
        (self.claude / "skills" / "debugging").mkdir(parents=True)
        (self.claude / "skills" / "debugging" / "SKILL.md").write_text("my own version", encoding="utf-8")
        (self.claude / "CLAUDE.md").write_text("my personal rules", encoding="utf-8")
        self.user_hook = {"matcher": "Bash", "hooks": [{"type": "command", "command": "echo mine"}]}
        (self.claude / "settings.json").write_text(json.dumps({
            "model": "opus", "permissions": {"allow": ["Bash(ls:*)"]},
            "hooks": {"PreToolUse": [self.user_hook]}}), encoding="utf-8")
        self.ag.mkdir(parents=True)
        (self.ag / "hooks.json").write_text(json.dumps({"agent-os-guard": {"enabled": True, "PreToolUse": []}}),
                                            encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def revathi(self, *args, expect=0):
        out = subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True, env=self.env,
                             encoding="utf-8")
        self.assertEqual(out.returncode, expect, out.stdout + out.stderr)
        return out.stdout

    def settings(self):
        return json.loads((self.claude / "settings.json").read_text(encoding="utf-8"))

    def ag_hooks(self):
        return json.loads((self.ag / "hooks.json").read_text(encoding="utf-8"))

    def test_dry_run_changes_nothing(self):
        before = (self.claude / "settings.json").read_text(encoding="utf-8")
        out = self.revathi("install", "--dry-run")
        self.assertIn("Dry run", out)
        self.assertEqual((self.claude / "settings.json").read_text(encoding="utf-8"), before)
        self.assertFalse((self.home / ".revathi" / "app").exists())

    def test_install_merges_and_keeps_user_content(self):
        out = self.revathi("install")
        s = self.settings()
        self.assertEqual(s["model"], "opus")
        self.assertEqual(s["permissions"], {"allow": ["Bash(ls:*)"]})
        self.assertIn(self.user_hook, s["hooks"]["PreToolUse"])
        for event in ("PreToolUse", "PostToolUse", "PostToolUseFailure", "Stop"):
            self.assertTrue(any(".revathi/app/adapters/claude-code/hook.py" in h["command"]
                                for g in s["hooks"][event] for h in g["hooks"]), event)
        self.assertEqual((self.claude / "CLAUDE.md").read_text(encoding="utf-8"), "my personal rules")
        self.assertEqual((self.claude / "skills" / "debugging" / "SKILL.md").read_text(encoding="utf-8"), "my own version")
        self.assertIn("conflict", out)
        self.assertTrue((self.claude / "skills" / "planning" / "SKILL.md").exists())
        self.assertTrue((self.claude / "agents" / "reviewer.md").exists())
        ag = self.ag_hooks()
        self.assertFalse(ag["agent-os-guard"]["enabled"])
        self.assertTrue(ag["revathi"]["enabled"])
        self.assertTrue((self.ag / "skills" / "debugging" / "SKILL.md").exists())
        self.assertTrue(any((self.home / ".revathi" / "backups").rglob("settings.json")))

    def test_install_twice_does_not_duplicate(self):
        self.revathi("install")
        self.revathi("install")
        self.assertEqual(len(self.settings()["hooks"]["PreToolUse"]), 2)  # the user's + REVATHI's
        self.assertEqual(len(self.settings()["hooks"]["Stop"]), 1)

    def test_doctor(self):
        self.assertIn("not installed", self.revathi("doctor", expect=1))
        self.revathi("install")
        out = self.revathi("doctor")
        self.assertNotIn("❌", out)
        self.assertIn("guard answers", out)

    def test_antigravity_hook_runs_through_its_shell(self):
        # live 2026-10-08: Antigravity runs hooks via `cmd /c` from the hooks.json folder; quoted paths broke
        self.revathi("install")
        sys.path.insert(0, str(ROOT / "cli"))
        import install
        command = self.ag_hooks()["revathi"]["PreToolUse"][0]["hooks"][0]["command"]
        event = {"conversationId": "t", "toolCall": {"name": "run_command", "args": {"CommandLine": "rm -rf /"}}}
        out = subprocess.run(install.shell_argv(command), input=json.dumps(event), capture_output=True, text=True,
                             cwd=self.ag, env=self.env)
        self.assertIn('"deny"', out.stdout, out.stderr)

    def test_installed_hook_runs_from_app(self):
        self.revathi("install")
        hook = self.home / ".revathi" / "app" / "adapters" / "claude-code" / "hook.py"
        event = {"session_id": "t", "hook_event_name": "PreToolUse", "cwd": str(self.home), "tool_name": "Bash",
                 "tool_input": {"command": "git -C . reset --hard"}}
        out = subprocess.run([sys.executable, str(hook)], input=json.dumps(event), capture_output=True, text=True,
                             env=self.env)
        self.assertIn('"ask"', out.stdout)

    def test_uninstall_reverses_install(self):
        self.revathi("install")
        self.revathi("uninstall")
        s = self.settings()
        self.assertEqual(s["hooks"], {"PreToolUse": [self.user_hook]})
        self.assertEqual(s["model"], "opus")
        self.assertFalse((self.claude / "skills" / "planning").exists())
        self.assertFalse((self.claude / "agents" / "reviewer.md").exists())
        self.assertEqual((self.claude / "skills" / "debugging" / "SKILL.md").read_text(encoding="utf-8"), "my own version")
        ag = self.ag_hooks()
        self.assertNotIn("revathi", ag)
        self.assertTrue(ag["agent-os-guard"]["enabled"])
        self.assertFalse((self.home / ".revathi" / "app").exists())


class AgentOsDetection(unittest.TestCase):
    """Parses real `claude plugin list` output (found on a real machine: the ❯ marker broke decoding)."""
    LIST = ("Skills-directory plugins (.claude/skills/*):\n\n  ❯ agent-os@skills-dir\n    Version: 0.1.0\n"
            "    Scope: user\n    Path: ~\\.claude\\skills\\agent-os\n    Status: {status}\n")

    def detect(self, stdout):
        sys.path.insert(0, str(ROOT / "cli"))
        import install
        original = install._claude_cli
        install._claude_cli = lambda *a: subprocess.CompletedProcess(a, 0, stdout, "")
        try:
            return install._agent_os_loaded()
        finally:
            install._claude_cli = original

    def test_loaded(self):
        self.assertTrue(self.detect(self.LIST.format(status="✔ loaded")))

    def test_disabled(self):
        self.assertFalse(self.detect(self.LIST.format(status="✘ disabled")))

    def test_absent_or_unreadable(self):
        self.assertFalse(self.detect("No plugins installed."))
        self.assertFalse(self.detect(None))


class Modes(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix="revathi-mode-"))
        self.work = self.home / "repo"
        self.work.mkdir()
        self.env = {**os.environ, "REVATHI_HOME": str(self.home / ".revathi")}

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def revathi(self, *args):
        return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True, env=self.env,
                              encoding="utf-8", check=True).stdout

    def pre(self, command):
        hook = ROOT / "adapters" / "claude-code" / "hook.py"
        event = {"session_id": "m", "hook_event_name": "PreToolUse", "cwd": str(self.work), "tool_name": "Bash",
                 "tool_input": {"command": command}}
        out = subprocess.run([sys.executable, str(hook)], input=json.dumps(event), capture_output=True, text=True,
                             env=self.env).stdout
        return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out.strip() else "pass"

    def test_balanced_is_default(self):
        self.assertIn("▶ balanced", self.revathi("mode"))
        self.assertEqual(self.pre("git push origin feature"), "pass")

    def test_careful_asks_more(self):
        self.revathi("mode", "careful")
        self.assertEqual(self.pre("git push origin feature"), "ask")
        self.assertEqual(self.pre("pip install requests"), "ask")
        self.assertEqual(self.pre("ls"), "pass")

    def test_full_runs_undoable_actions_with_a_snapshot(self):
        subprocess.run(["git", *GIT_ID, "init", "-q"], cwd=self.work, check=True)
        (self.work / "a.txt").write_text("wip", encoding="utf-8")
        self.revathi("mode", "full")
        self.assertEqual(self.pre("git reset --hard"), "pass")
        self.assertIn("git", self.revathi("undo", "--list"))
        self.assertEqual(self.pre("git push --force origin feature"), "ask")   # irreversible: still asks
        self.assertEqual(self.pre("rm -rf /"), "deny")                         # catastrophic: still denied


if __name__ == "__main__":
    unittest.main()
