"""Guard: decide deny / ask / no opinion for one Event, using the policy file."""
import os
import re

from engine import policy as policy_mod
from engine.event import COMMAND, WRITE, Decision

# git options that may come before the subcommand ("git -C repo reset --hard").
_QUOTED_OR_WORD = r"""(?:"[^"]*"|'[^']*'|\S+)"""
_GIT_GLOBAL_OPTS = re.compile(
    r"\bgit((?:\s+(?:-[Cc]\s+" + _QUOTED_OR_WORD +
    r"|--(?:git-dir|work-tree|namespace|exec-path|config-env)(?:=|\s+)" + _QUOTED_OR_WORD +
    r"|--no-pager|--paginate|-p|-P|--bare|--no-replace-objects|--literal-pathspecs|--no-optional-locks))+)(?=\s)",
    re.I)

# Where a shell command writes output: "> file", ">> file", "tee [-a] file", PowerShell Out-File / Set-Content / Add-Content.
_WRITE_TARGETS = re.compile(
    r"""(?:>>?|\btee\s+(?:-a\s+)?|\b(?:Out-File|Set-Content|Add-Content)\s+(?:-(?:File)?Path\s+)?)\s*["']?([^\s"'|;&>]+)""",
    re.I)


def normalize_git(command):
    """Drop git global options so policy patterns see "git <subcommand>"."""
    return _GIT_GLOBAL_OPTS.sub("git", command)


def _is_env_file(path, pol):
    name = os.path.basename(str(path).replace("\\", "/")).lower()
    return name.startswith(".env") and not name.endswith(pol.env_template_suffixes)


def _find_secret(text, pol):
    for pattern in pol.secrets:
        for m in pattern.finditer(text):
            if not pol.placeholder.search(m.group(0)):
                return True
    return False


def recursive_delete_targets(command):
    """Yield the path arguments of rm -r / Remove-Item -Recurse calls."""
    for seg in re.split(r"[|;&]+", command):
        words = seg.split()
        if not words:
            continue
        head, args = words[0].lower(), words[1:]
        if head == "sudo" and args:
            head, args = args[0].lower(), args[1:]
        flags = [a for a in args if a.startswith("-")]
        if head == "rm" and any(re.match(r"^-\w*[rR]", f) or f == "--recursive" for f in flags):
            yield from (a for a in args if not a.startswith("-"))
        elif head in ("remove-item", "rm", "ri", "del") and any(f.lower().startswith("-r") for f in flags):
            yield from (a for a in args if not a.startswith("-"))


def check_command(command, pol):
    for target in recursive_delete_targets(command):
        if target.strip("\"'").lower().rstrip() in pol.root_targets:
            return Decision("deny", f"deleting '{target}' would wipe your whole drive, home or project folder")
    if _find_secret(command, pol):
        targets = _WRITE_TARGETS.findall(command)
        if not (targets and all(_is_env_file(t, pol) for t in targets)):
            return Decision("deny", "this command contains a secret key, which would end up in files, history or logs. "
                                    "Put it in an environment variable or a git-ignored .env file instead")
    normalized = normalize_git(command)
    for pattern, reason, _ in pol.deny:
        if pattern.search(normalized):
            return Decision("deny", reason)
    for pattern, reason, undoable in pol.ask:
        if pattern.search(normalized):
            return Decision("ask", f"{reason}. Please confirm this is intended", undoable)
    return None


def check_write(path, texts, pol):
    if _is_env_file(path, pol):
        return None  # .env files are the right place for secrets
    name = os.path.basename(str(path).replace("\\", "/")) or "a file"
    for text in filter(None, texts):
        if _find_secret(text, pol):
            return Decision("deny", f"this would save a secret key into {name}. "
                                    "Use an environment variable or a git-ignored .env file instead")
    return None


def check(event, pol=None):
    """Return a Decision, or None for no opinion."""
    pol = pol or policy_mod.load().guard
    if event.kind == COMMAND:
        return check_command(event.command, pol)
    if event.kind == WRITE:
        return check_write(event.path, event.texts, pol)
    return None
