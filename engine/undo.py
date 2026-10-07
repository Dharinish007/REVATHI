"""Undo: save what an action could destroy, before it runs; restore it with `revathi undo`.

Snapshots live in $REVATHI_HOME/snapshots/<id>/ with a manifest.json. Three kinds:
  files - copies of files about to be written/edited (a file that didn't exist is deleted on undo)
  git   - the whole working tree (tracked + untracked, not ignored) as a hidden commit under refs/revathi/;
          the user's branch, staging area and stash are never touched
  copy  - copies of folders about to be deleted outside git (skipped above SIZE_LIMIT)
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from engine import log

SIZE_LIMIT = 50 * 1024 * 1024   # bytes per snapshot copy; larger targets are not saved
KEEP = 200                      # newest snapshots kept
GIT_ID = {"GIT_AUTHOR_NAME": "REVATHI", "GIT_AUTHOR_EMAIL": "revathi@localhost",
          "GIT_COMMITTER_NAME": "REVATHI", "GIT_COMMITTER_EMAIL": "revathi@localhost"}


def store():
    return log.home() / "snapshots"


def _new(kind, session, reason, **extra):
    now = datetime.now(timezone.utc)
    root = store()
    root.mkdir(parents=True, exist_ok=True)
    base = now.strftime("%Y%m%dT%H%M%S%f")
    sid, n = base, 1
    while (root / sid).exists():
        n += 1
        sid = f"{base}-{n}"
    (root / sid).mkdir()
    return {"id": sid, "ts": now.isoformat(timespec="seconds"), "kind": kind, "session": session,
            "reason": reason, **extra}


def _save(manifest):
    path = store() / manifest["id"] / "manifest.json"
    path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
    _prune()
    return manifest


def _prune():
    for old in sorted(p for p in store().iterdir() if p.is_dir())[:-KEEP]:
        try:
            manifest = json.loads((old / "manifest.json").read_text(encoding="utf-8"))
            if manifest.get("kind") == "git":  # release the hidden ref so git can clean the snapshot up
                _git(["update-ref", "-d", f"refs/revathi/snapshots/{manifest['id']}"], manifest["root"])
        except (OSError, json.JSONDecodeError, KeyError, subprocess.SubprocessError):
            pass
        shutil.rmtree(old, ignore_errors=True)


def _size(path):
    if path.is_file():
        return path.stat().st_size
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def _git(args, cwd, env=None):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=30,
                          env={**os.environ, **(env or {})})


def git_root(cwd):
    try:
        out = _git(["rev-parse", "--show-toplevel"], cwd)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


# ---------- snapshot ----------

def snapshot_files(paths, session="", reason=""):
    """Save the current version of each file (or that it didn't exist)."""
    manifest = _new("files", session, reason, entries=[])
    folder = store() / manifest["id"]
    for i, p in enumerate(paths):
        path = Path(p).resolve()
        entry = {"path": str(path), "existed": path.is_file()}
        if entry["existed"]:
            if path.stat().st_size > SIZE_LIMIT:
                entry["skipped"] = "too large"
            else:
                shutil.copy2(path, folder / f"{i}.bak")
                entry["stored"] = f"{i}.bak"
        manifest["entries"].append(entry)
    return _save(manifest)


def snapshot_git(top, session="", reason=""):
    """Hidden commit of the whole working tree; nothing the user sees changes."""
    with tempfile.TemporaryDirectory() as tmp:
        env = {"GIT_INDEX_FILE": os.path.join(tmp, "index"), **GIT_ID}
        if _git(["add", "-A"], top, env).returncode != 0:
            return None
        tree = _git(["write-tree"], top, env).stdout.strip()
        head = _git(["rev-parse", "-q", "--verify", "HEAD"], top).stdout.strip()
        branch = _git(["symbolic-ref", "-q", "--short", "HEAD"], top).stdout.strip()
        manifest = _new("git", session, reason, root=top, head=head, branch=branch)
        args = ["commit-tree", tree, "-m", f"REVATHI snapshot {manifest['id']}"] + (["-p", head] if head else [])
        commit = _git(args, top, env).stdout.strip()
        if not commit:
            shutil.rmtree(store() / manifest["id"], ignore_errors=True)
            return None
        _git(["update-ref", f"refs/revathi/snapshots/{manifest['id']}", commit], top)
        manifest["commit"] = commit
    return _save(manifest)


def snapshot_copy(paths, session="", reason=""):
    """Copy folders/files about to be deleted (outside git)."""
    manifest = _new("copy", session, reason, entries=[])
    folder = store() / manifest["id"]
    for i, p in enumerate(paths):
        path = Path(p).resolve()
        entry = {"path": str(path)}
        if not path.exists():
            entry["skipped"] = "does not exist"
        elif _size(path) > SIZE_LIMIT:
            entry["skipped"] = "too large"
        else:
            target = folder / str(i)
            shutil.copytree(path, target) if path.is_dir() else shutil.copy2(path, target)
            entry["stored"] = str(i)
        manifest["entries"].append(entry)
    return _save(manifest)


_ARG = r"""("[^"]*"|'[^']*'|[^\s;&|]+)"""
_LEADING_CD = re.compile(r"^\s*(?:cd|Set-Location|sl|pushd)\s+" + _ARG + r"\s*(?:&&|;)", re.I)
_GIT_DIR = re.compile(r"\bgit\s+-C\s+" + _ARG, re.I)


def target_dir(command, cwd):
    """The folder a command really acts on: follows a leading `cd <dir> &&` and `git -C <dir>`."""
    m = _LEADING_CD.match(command)
    if m:
        cwd = os.path.join(cwd, os.path.expanduser(m.group(1).strip("\"'")))
    m = _GIT_DIR.search(command)
    if m:
        cwd = os.path.join(cwd, os.path.expanduser(m.group(1).strip("\"'")))
    return cwd


def snapshot_for_command(cwd, delete_targets, session="", reason="", command=""):
    """Best snapshot for a risky command. Returns the manifest, or None if nothing could be saved."""
    if not cwd:
        return None  # without the agent's folder we can't know what the command would touch
    cwd = target_dir(command, cwd)
    targets = [os.path.join(cwd, t.strip("\"'")) for t in delete_targets]
    if targets:  # copying the exact targets also covers git-ignored files (.env, build output)
        manifest = snapshot_copy(targets, session, reason)
        if all("stored" in e for e in manifest["entries"]):
            return manifest
        shutil.rmtree(store() / manifest["id"], ignore_errors=True)
    top = git_root(cwd)
    return snapshot_git(top, session, reason) if top else None


# ---------- list / restore ----------

def snapshots():
    """All manifests, newest first."""
    if not store().exists():
        return []
    found = []
    for folder in sorted((p for p in store().iterdir() if p.is_dir()), reverse=True):
        try:
            found.append(json.loads((folder / "manifest.json").read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return found


def restore(snapshot_id=None):
    """Restore one snapshot (default: the newest). Returns a list of plain-English lines."""
    all_snaps = snapshots()
    manifest = next((m for m in all_snaps if m["id"] == snapshot_id), None) if snapshot_id else \
        (all_snaps[0] if all_snaps else None)
    if not manifest:
        return ["No snapshot found. Nothing was changed."]
    folder = store() / manifest["id"]
    lines = [f"Restoring snapshot {manifest['id']} ({manifest['kind']}): {manifest.get('reason') or 'no reason recorded'}"]

    if manifest["kind"] == "files":
        paths = [e["path"] for e in manifest["entries"]]
        backup = snapshot_files(paths, manifest.get("session", ""), f"before undo of {manifest['id']}")
        for e in manifest["entries"]:
            path = Path(e["path"])
            if e.get("stored"):
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(folder / e["stored"], path)
                lines.append(f"  restored  {path}")
            elif not e["existed"] and path.exists():
                path.unlink()
                lines.append(f"  removed   {path} (it did not exist before)")
            elif e.get("skipped"):
                lines.append(f"  skipped   {path} ({e['skipped']})")
        lines.append(f"Your current versions were saved first: `revathi undo {backup['id']}` reverses this undo.")

    elif manifest["kind"] == "git":
        top = manifest["root"]
        backup = snapshot_git(top, manifest.get("session", ""), f"before undo of {manifest['id']}")
        with tempfile.TemporaryDirectory() as tmp:
            env = {"GIT_INDEX_FILE": os.path.join(tmp, "index")}
            _git(["read-tree", manifest["commit"]], top, env)
            out = _git(["checkout-index", "-a", "-f"], top, env)
        if out.returncode != 0:
            return lines + [f"Restore failed: {out.stderr.strip()}"]
        lines.append(f"  restored all files in {top} as they were (your staging area was not changed)")
        head = _git(["rev-parse", "-q", "--verify", "HEAD"], top).stdout.strip()
        if manifest.get("head") and head != manifest["head"]:
            lines.append(f"  note: your branch moved since then (was {manifest['head'][:10]}, now {head[:10]}). "
                         f"To move it back too: git reset --soft {manifest['head'][:10]}")
        if backup:
            lines.append(f"Your current files were saved first: `revathi undo {backup['id']}` reverses this undo.")

    elif manifest["kind"] == "copy":
        for e in manifest["entries"]:
            path = Path(e["path"])
            if e.get("stored"):
                src = folder / e["stored"]
                shutil.copytree(src, path, dirs_exist_ok=True) if src.is_dir() else shutil.copy2(src, path)
                lines.append(f"  restored  {path}")
            else:
                lines.append(f"  skipped   {path} ({e.get('skipped')})")
    return lines
