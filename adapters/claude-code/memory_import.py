"""Read Claude Code's own auto memory (~/.claude/projects/<project>/memory/*.md) as neutral note suggestions.

Claude writes these notes itself, without the user's approval, so REVATHI only ever proposes them (inbox);
the user approves each one in `revathi memory review` (Phase 7g, D12). MEMORY.md is Claude's index: skipped.
Claude names a project folder after its path with every non-letter/digit replaced by "-" (D:\\a b -> D--a-b).
"""
import hashlib
import os
import re
from pathlib import Path

# Claude memory type -> (REVATHI type, project-specific?)
TYPES = {"user": ("fact", False), "feedback": ("preference", False), "project": ("fact", True),
         "reference": ("fact", True)}


def claude_home():
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def folder_name(project):
    return re.sub(r"[^A-Za-z0-9]", "-", str(Path(project).resolve()))


def notes(parse, project=None, home=None):
    """Yield dicts for memory.propose(): user/feedback notes from every project; project/reference notes only for
    `project` (a folder). `parse` is engine.memory.parse (passed in so this adapter stays import-light)."""
    root = (home or claude_home()) / "projects"
    wanted = folder_name(project).lower() if project else None
    for folder in sorted(root.glob("*/memory")) if root.exists() else []:
        here = folder.parent.name.lower() == wanted
        for path in sorted(folder.glob("*.md")):
            if path.name.upper() == "MEMORY.MD":
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            try:
                meta, body = parse(text)
            except ValueError:
                meta, body = {}, text
            kind = str(meta.get("type") or "").strip().lower()  # flat, or nested under "metadata:" (read flat)
            rtype, project_only = TYPES.get(kind, ("fact", True))
            if project_only and not here:
                continue
            title = str(meta.get("description") or meta.get("name") or path.stem).strip()
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]
            yield {"type": rtype, "title": title[:120], "body": body.strip() or title,
                   "sources": [f"claude-auto-memory:{folder.parent.name}/{path.name}"],
                   "scope": "project" if project_only else "user", "project": project if project_only else None,
                   "key": f"import:claude:{folder.parent.name.lower()}/{path.name}:{digest}"}
