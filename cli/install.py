"""revathi install / uninstall / doctor.

install: copy REVATHI to $REVATHI_HOME/app, then connect each detected tool:
  Claude Code - hooks merged into ~/.claude/settings.json, skills into ~/.claude/skills, subagents into
                ~/.claude/agents, the Agent OS plugin disabled (D19). ~/.claude/CLAUDE.md is never touched (D20).
  Antigravity - a "revathi" group in ~/.gemini/config/hooks.json, skills into ~/.gemini/config/skills.
Rules of the road: merge, never delete user content; back up every file before changing it; an existing skill or
agent that differs from ours is reported as a conflict and left alone; everything done is recorded in config.json
so uninstall reverses exactly that.
"""
import filecmp
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine import config, log  # noqa: E402

RUNTIME = ("engine", "adapters", "policy", "core", "cli")
AGENT_OS_PLUGIN = "agent-os@skills-dir"
CLAUDE_EVENTS = {
    "PreToolUse": "Bash|PowerShell|Write|Edit|MultiEdit|Read|Grep|WebFetch|WebSearch|SubagentHandback|mcp__.*",
    "PostToolUse": "Bash|PowerShell|Write|Edit|MultiEdit",
    "PostToolUseFailure": "Bash|PowerShell|Write|Edit|MultiEdit",
    "Stop": None,
    "SubagentStop": None,
}
AG_PRE = "run_command|write_to_file|replace_file_content|multi_replace_file_content|view_file|read_url_content|search_web"
AG_POST = "run_command|write_to_file|replace_file_content|multi_replace_file_content"


# ---------- locations ----------

def app_dir():
    return log.home() / "app"


def claude_dir():
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def antigravity_dir():
    return Path.home() / ".gemini" / "config"


def python_cmd():
    return "python" if os.name == "nt" else "python3"


def _short_path(path):
    """Windows 8.3 form of a path (no spaces), or the path unchanged if Windows can't give one."""
    try:
        import ctypes
        buf = ctypes.create_unicode_buffer(1024)
        if ctypes.windll.kernel32.GetShortPathNameW(str(path), buf, 1024):
            return Path(buf.value)
    except (ImportError, AttributeError, OSError):
        pass
    return Path(path)


def hook_cmd(tool, *args, quoted=True):
    """Command line for a hook. Antigravity runs hooks with `cmd /c` on Windows, which passes quotes through to
    Python literally (seen live 2026-10-08), so its command is unquoted; a path with spaces uses the short form."""
    script = app_dir() / "adapters" / tool / "hook.py"
    if quoted:
        return " ".join([python_cmd(), f'"{script.as_posix()}"', *args])
    if " " in str(script) and os.name == "nt":
        script = _short_path(script)
    return " ".join([python_cmd(), script.as_posix(), *args])


def shell_argv(command):
    """How Antigravity runs a hook command (from its bundled hooks docs)."""
    return ["cmd", "/c", command] if os.name == "nt" else ["sh", "-c", command]


def _is_ours(command):
    return (app_dir() / "adapters").as_posix() in str(command)


# ---------- helpers ----------

class Report:
    def __init__(self, dry):
        self.dry, self.lines = dry, []

    def say(self, mark, text):
        self.lines.append(f"  {mark} {text}")


def _read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def _write_json(path, data, report, backup_dir):
    if report.dry:
        return
    if path.exists():
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_dir / path.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _same_tree(a, b):
    if a.is_file() or b.is_file():
        return a.is_file() and b.is_file() and filecmp.cmp(a, b, shallow=False)
    cmp = filecmp.dircmp(a, b)
    if cmp.left_only or cmp.right_only or cmp.funny_files:
        return False
    if any(not filecmp.cmp(a / f, b / f, shallow=False) for f in cmp.common_files):
        return False
    return all(_same_tree(a / d, b / d) for d in cmp.common_dirs)


def _place(src, dest, report, label):
    """Copy src (file or folder) to dest unless something different is already there. Returns True if we own it."""
    if dest.exists():
        if _same_tree(src, dest):
            report.say("=", f"{label}: already there (same)")
            return False
        report.say("!", f"{label}: a different version exists at {dest}; left alone (conflict)")
        return False
    if not report.dry:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dest) if src.is_dir() else shutil.copy2(src, dest)
    report.say("+", f"{label}: installed")
    return True


def _remove_if_ours(src, dest, report, label):
    if dest.exists() and _same_tree(src, dest):
        if not report.dry:
            shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
        report.say("-", f"{label}: removed")
    elif dest.exists():
        report.say("!", f"{label}: changed since install; left in place")


def _claude_cli(*args):
    if os.environ.get("REVATHI_NO_CLAUDE_CLI") or not shutil.which("claude"):
        return None
    try:
        return subprocess.run(["claude", *args], capture_output=True, text=True, timeout=60,
                              encoding="utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError):
        return None


def _agent_os_loaded():
    out = _claude_cli("plugin", "list")
    if not out or AGENT_OS_PLUGIN not in (out.stdout or ""):
        return False
    block = out.stdout.split(AGENT_OS_PLUGIN, 1)[1].split("❯", 1)[0]
    return "disabled" not in block.lower()


# ---------- install ----------

def install(dry=False):
    report = Report(dry)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    backups = log.home() / "backups" / stamp
    state = config.load()
    record = {"ts": stamp, "python": python_cmd()}

    report.lines.append(f"REVATHI runtime -> {app_dir()}")
    if not dry:
        if app_dir().exists():
            shutil.rmtree(app_dir())
        for part in RUNTIME:
            shutil.copytree(ROOT / part, app_dir() / part, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    report.say("+", "engine, adapters, policy, skills, cli copied")

    cdir = claude_dir()
    if cdir.exists():
        report.lines.append(f"Claude Code ({cdir})")
        settings_path = cdir / "settings.json"
        settings = _read_json(settings_path)
        hooks = settings.setdefault("hooks", {})
        for event, matcher in CLAUDE_EVENTS.items():
            group = {"hooks": [{"type": "command", "command": hook_cmd("claude-code"), "timeout": 10}]}
            if matcher:
                group = {"matcher": matcher, **group}
            kept = [g for g in hooks.get(event, []) if not any(_is_ours(h.get("command")) for h in g.get("hooks", []))]
            hooks[event] = kept + [group]
        _write_json(settings_path, settings, report, backups / "claude")
        report.say("+", "hooks merged into settings.json (your other settings kept; backup saved)")
        skills = [s.name for s in sorted((ROOT / "core" / "skills").iterdir())
                  if _place(s, cdir / "skills" / s.name, report, f"skill {s.name}")]
        agents = [a.name for a in sorted((ROOT / "core" / "agents").glob("*.md"))
                  if _place(a, cdir / "agents" / a.name, report, f"subagent {a.stem}")]
        disabled = False
        if _agent_os_loaded():
            if not dry:
                out = _claude_cli("plugin", "disable", AGENT_OS_PLUGIN)
                disabled = bool(out and out.returncode == 0)
                report.say("-" if disabled else "!", "Agent OS plugin disabled" if disabled else
                           f"could not disable the Agent OS plugin: {(out.stderr or out.stdout).strip() if out else 'claude not found'}")
            else:
                report.say("-", "Agent OS plugin would be disabled")
        report.say("=", "CLAUDE.md not touched (your personal rules stay as they are)")
        record["claude"] = {"skills": skills, "agents": agents, "disabled_agent_os": disabled}
    else:
        report.lines.append("Claude Code: not found, skipped")

    adir = antigravity_dir()
    if adir.exists():
        report.lines.append(f"Antigravity ({adir})")
        hooks_path = adir / "hooks.json"
        data = _read_json(hooks_path)
        disabled_group = False
        if isinstance(data.get("agent-os-guard"), dict) and data["agent-os-guard"].get("enabled", True):
            data["agent-os-guard"]["enabled"] = False
            disabled_group = True
            report.say("-", "Agent OS guard group disabled")
        data["revathi"] = {
            "enabled": True,
            "PreToolUse": [{"matcher": AG_PRE, "hooks": [
                {"type": "command", "command": hook_cmd("antigravity", "PreToolUse", quoted=False), "timeout": 10}]}],
            "PostToolUse": [{"matcher": AG_POST, "hooks": [
                {"type": "command", "command": hook_cmd("antigravity", "PostToolUse", quoted=False), "timeout": 10}]}],
            "Stop": [{"type": "command", "command": hook_cmd("antigravity", "Stop", quoted=False), "timeout": 10}],
        }
        _write_json(hooks_path, data, report, backups / "antigravity")
        report.say("+", "hooks.json: 'revathi' group added (other groups kept; backup saved)")
        skills = [s.name for s in sorted((ROOT / "core" / "skills").iterdir())
                  if _place(s, adir / "skills" / s.name, report, f"skill {s.name}")]
        record["antigravity"] = {"skills": skills, "disabled_agent_os_group": disabled_group}
    else:
        report.lines.append("Antigravity: not found, skipped")

    if not dry:
        previous = state.get("install", {})
        for tool in ("claude", "antigravity"):  # keep ownership from earlier installs
            if tool in previous and tool in record:
                for key in ("skills", "agents"):
                    record[tool][key] = sorted(set(previous[tool].get(key, [])) | set(record[tool].get(key, [])))
                for key in ("disabled_agent_os", "disabled_agent_os_group"):
                    record[tool][key] = previous[tool].get(key, False) or record[tool].get(key, False)
        state["install"] = record
        state.setdefault("mode", config.DEFAULT_MODE)
        config.save(state)
        report.lines.append("Done. Restart your AI tools so they load the hooks, then run `revathi doctor`.")
    else:
        report.lines.append("Dry run: nothing was changed.")
    return report.lines


# ---------- uninstall ----------

def uninstall(dry=False):
    report = Report(dry)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    backups = log.home() / "backups" / stamp
    state = config.load()
    record = state.get("install")
    if not record:
        return ["REVATHI is not installed (nothing recorded). Nothing was changed."]

    cdir = claude_dir()
    if "claude" in record and cdir.exists():
        report.lines.append(f"Claude Code ({cdir})")
        settings_path = cdir / "settings.json"
        settings = _read_json(settings_path)
        hooks = settings.get("hooks", {})
        for event in list(hooks):
            hooks[event] = [g for g in hooks[event] if not any(_is_ours(h.get("command")) for h in g.get("hooks", []))]
            if not hooks[event]:
                del hooks[event]
        if not hooks:
            settings.pop("hooks", None)
        _write_json(settings_path, settings, report, backups / "claude")
        report.say("-", "REVATHI hooks removed from settings.json")
        for name in record["claude"].get("skills", []):
            _remove_if_ours(app_dir() / "core" / "skills" / name, cdir / "skills" / name, report, f"skill {name}")
        for name in record["claude"].get("agents", []):
            _remove_if_ours(app_dir() / "core" / "agents" / name, cdir / "agents" / name, report, f"subagent {name}")
        if record["claude"].get("disabled_agent_os"):
            if not dry:
                _claude_cli("plugin", "enable", AGENT_OS_PLUGIN)
            report.say("+", "Agent OS plugin enabled again")

    adir = antigravity_dir()
    if "antigravity" in record and adir.exists():
        report.lines.append(f"Antigravity ({adir})")
        hooks_path = adir / "hooks.json"
        data = _read_json(hooks_path)
        data.pop("revathi", None)
        if record["antigravity"].get("disabled_agent_os_group") and isinstance(data.get("agent-os-guard"), dict):
            data["agent-os-guard"]["enabled"] = True
            report.say("+", "Agent OS guard group enabled again")
        _write_json(hooks_path, data, report, backups / "antigravity")
        report.say("-", "'revathi' group removed from hooks.json")
        for name in record["antigravity"].get("skills", []):
            _remove_if_ours(app_dir() / "core" / "skills" / name, adir / "skills" / name, report, f"skill {name}")

    if not dry:
        shutil.rmtree(app_dir(), ignore_errors=True)
        state.pop("install", None)
        config.save(state)
        report.lines.append(f"Done. Your logs, snapshots and settings stay in {log.home()} (delete that folder to remove them).")
    else:
        report.lines.append("Dry run: nothing was changed.")
    return report.lines


# ---------- doctor ----------

def _probe(argv, event, cwd=None):
    """Run a hook the way its tool would, with a sample risky event; True if it answers like REVATHI."""
    try:
        out = subprocess.run(argv, input=json.dumps(event), capture_output=True, text=True, timeout=20, cwd=cwd,
                             env={**os.environ, "REVATHI_HOME": str(log.home() / "doctor")})
    except (OSError, subprocess.SubprocessError):
        return False
    finally:
        shutil.rmtree(log.home() / "doctor", ignore_errors=True)
    return "REVATHI guard" in out.stdout and "deny" in out.stdout


def doctor():
    """Returns (lines, ok)."""
    lines, ok = [], True

    def check(passed, good, bad):
        nonlocal ok
        ok = ok and passed
        lines.append(f"  {'✅' if passed else '❌'} {good if passed else bad}")

    record = config.load().get("install")
    lines.append("REVATHI")
    py = shutil.which(python_cmd())
    version = None
    if py:
        out = subprocess.run([py, "-c", "import sys;print('%d.%d' % sys.version_info[:2])"], capture_output=True, text=True)
        version = out.stdout.strip()
    good_py = bool(version) and tuple(int(x) for x in version.split(".")) >= (3, 11)
    check(good_py, f"`{python_cmd()}` is Python {version}", f"`{python_cmd()}` must be Python 3.11+ on PATH (found: {version or 'none'})")
    check(bool(record), "installed", "not installed: run `revathi install`")
    check((app_dir() / "engine" / "pipeline.py").exists(), f"runtime in {app_dir()}", f"runtime missing in {app_dir()}")
    lines.append(f"  ℹ️  mode: {config.mode()}")
    if not record:
        return lines, False
    danger = "rm -rf /"

    if "claude" in record:
        lines.append("Claude Code")
        hooks = _read_json(claude_dir() / "settings.json").get("hooks", {})
        for event in CLAUDE_EVENTS:
            found = any(_is_ours(h.get("command")) for g in hooks.get(event, []) for h in g.get("hooks", []))
            check(found, f"{event} hook connected", f"{event} hook missing: run `revathi install`")
        check(_probe([sys.executable, str(app_dir() / "adapters" / "claude-code" / "hook.py")], {"session_id": "doctor", "hook_event_name": "PreToolUse", "cwd": ".",
                                          "tool_name": "Bash", "tool_input": {"command": danger}}),
              "guard answers (test: `rm -rf /` is blocked)", "guard did not answer a test event")
        if record["claude"].get("disabled_agent_os") or _claude_cli("--version"):
            check(not _agent_os_loaded(), "Agent OS plugin is off (no double checks)", "Agent OS plugin is still on")
        lines.append(f"  ℹ️  {len(record['claude'].get('skills', []))} skills and "
                     f"{len(record['claude'].get('agents', []))} subagents installed by REVATHI")

    if "antigravity" in record:
        lines.append("Antigravity")
        group = _read_json(antigravity_dir() / "hooks.json").get("revathi", {})
        check(group.get("enabled") is True and all(k in group for k in ("PreToolUse", "PostToolUse", "Stop")),
              "hooks connected (PreToolUse, PostToolUse, Stop)", "hooks missing: run `revathi install`")
        command = (group.get("PreToolUse") or [{}])[0].get("hooks", [{}])[0].get("command", "")
        check(_probe(shell_argv(command), {"conversationId": "doctor", "toolCall": {
                  "name": "run_command", "args": {"CommandLine": danger, "Cwd": "."}}}, cwd=antigravity_dir()),
              "guard answers when run the way Antigravity runs it (test: `rm -rf /` is blocked)",
              f"guard did not answer when run the way Antigravity runs it: {command}")
    lines.append("All good. Restart your AI tools after installing or changing REVATHI." if ok else
                 "Something needs attention (see ❌ above).")
    return lines, ok
