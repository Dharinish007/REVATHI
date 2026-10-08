"""revathi: the trust layer for AI agents.

  revathi install [--dry-run]        connect REVATHI to Claude Code and Antigravity
  revathi uninstall [--dry-run]      reverse exactly what install did
  revathi doctor                     check that everything is connected and working
  revathi mode [careful|balanced|full]   show or set how strict REVATHI is
  revathi log [--session ID] [--all] what the agent did (newest session by default)
  revathi undo [--list] [ID]         restore what an agent action changed or deleted
  revathi canary plant <dir> | status    decoy credentials that reveal hidden instructions
  revathi memory propose|list|show|approve|reject|forget|check   what agents remember (you approve)
"""
import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # REVATHI root, for "engine"

from engine import canary, config, log, memory, undo  # noqa: E402

try:
    import install as installer  # same folder (cli/)
except ImportError:
    from cli import install as installer

MODE_HELP = {
    "observe": "audit only: records what it would block or ask, never interrupts (no snapshots)",
    "careful": "asks before every push, delete, amend and package install, on top of the normal checks",
    "balanced": "blocks catastrophic actions, asks before risky ones (default)",
    "full": "local risky actions (reset, clean, deletes) run without asking once a snapshot is saved; "
            "irreversible ones (push --force, publish, DROP TABLE) still ask",
}
ICONS = {("pre", "deny"): "⛔ blocked", ("pre", "ask"): "❓ asked", ("pre", "allow"): "✅ allowed (full mode, snapshot saved)",
         ("stop", "block"): "🧾 sent back: no proof yet", ("stop", "unproven"): "⚠️ finished without proof"}


def _print(lines):
    for line in lines:
        print(line)


def cmd_install(args):
    _print(installer.install(dry=args.dry_run))
    return 0


def cmd_uninstall(args):
    _print(installer.uninstall(dry=args.dry_run))
    return 0


def cmd_doctor(args):
    lines, ok = installer.doctor()
    _print(lines)
    return 0 if ok else 1


def cmd_mode(args):
    if args.mode:
        config.set_mode(args.mode)
        print(f"Mode set to {args.mode}: {MODE_HELP[args.mode]}.")
    else:
        current = config.mode()
        for name in config.MODES:
            print(f"{'▶' if name == current else ' '} {name:<9} {MODE_HELP[name]}")
    return 0


def _describe(r):
    target = r.get("command") or r.get("path") or ""
    event = r.get("event")
    if event == "post":
        check = {"pass": " ✅ check passed", "fail": " ❌ check failed"}.get(r.get("check"), "")
        verb = "ran" if r.get("kind") == "command" else "changed"
        return f"{'▶' if r.get('ok') else '✗'} {verb} {target}{check}"
    if event == "snapshot":
        return f"📸 snapshot {r.get('id')} ({r.get('snapshot')})"
    label = ICONS.get((event, r.get("verdict")), f"{event} {r.get('verdict', '')}")
    return f"{label}: {target} {('- ' + r['reason']) if r.get('reason') and event == 'pre' else ''}".rstrip()


def cmd_log(args):
    folder = log.home() / "logs"
    files = sorted(folder.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True) if folder.exists() else []
    if not files:
        print("No sessions recorded yet.")
        return 0
    if args.session:
        files = [f for f in files if f.stem.startswith(args.session)]
        if not files:
            print(f"No session starting with {args.session}.")
            return 1
    if args.list:
        for f in files[:20]:
            print(f"{f.stem}  {sum(1 for _ in open(f, encoding='utf-8'))} records")
        return 0
    records = log.read(files[0].stem)
    print(f"Session {files[0].stem}: {len(records)} records, "
          f"{'record intact ✅' if log.chain_ok(records) else 'RECORD WAS CHANGED ❌'}")
    for r in records:
        print(f"  {r.get('ts', '')[11:19]}  {_describe(r)}")
    return 0


def cmd_undo(args):
    if args.list:
        snaps = undo.snapshots()
        if not snaps:
            print("No snapshots yet.")
        for m in snaps[:args.limit]:
            print(f"{m['id']}  {m['kind']:<5}  {m.get('reason', '')}")
        return 0
    _print(undo.restore(args.id))
    return 0


def cmd_canary(args):
    if args.action == "plant":
        if not args.dir or not Path(args.dir).is_dir():
            print("Give an existing folder: revathi canary plant <dir>")
            return 1
        decoy = canary.plant(args.dir)
        print(f"Decoy planted: {decoy}\n"
              "If an agent reads it, you will be asked to confirm. If its fake key shows up in any action, "
              "the action is blocked. Keep it out of git (add it to .gitignore).")
        return 0
    decoys = canary.state().get("decoys", [])
    print("\n".join(decoys) if decoys else "No decoys planted.")
    return 0


def cmd_memory(args):
    try:
        if args.action == "propose":
            note = memory.propose(args.type, args.title, " ".join(args.text), args.source, scope=args.scope,
                                  project=args.project, tool=args.tool, by=args.by)
            print(f"Proposed {note['id']} → inbox. It is not used until you approve it: "
                  f"revathi memory approve {note['id']}")
        elif args.action == "list":
            state = "inbox" if args.inbox else "archive" if args.archive else "approved"
            found = memory.notes(state) if state != "approved" else memory.approved()
            if not found:
                print({"inbox": "Inbox is empty.", "archive": "Archive is empty.",
                       "approved": "No approved memories yet."}[state])
            for n in found:
                m = n["meta"]
                print(f"{n['id']}  {m.get('type', '?'):<10}  {m.get('title', '')}")
        elif args.action == "show":
            n = memory._record(memory._find(args.id))
            m = n["meta"]
            print(f"{m.get('title')}  [{m.get('type')}, {n['state']}, status {memory.status(m)}]")
            print(f"Sources: {', '.join(map(str, m.get('sources') or []))}")
            for v in m.get("verified") or []:
                print(f"Approved by {v.get('by')} at {v.get('at')}")
            print("\n" + n["body"].rstrip())
        elif args.action == "approve":
            n = memory.approve(args.id, by=getpass.getuser())
            print(f"✅ {args.id} approved: agents will now rely on \"{n['meta']['title']}\".")
        elif args.action == "reject":
            memory.reject(args.id)
            print(f"❌ {args.id} rejected and moved to the archive (kept, never used).")
        elif args.action == "forget":
            memory.forget(args.id)
            print(f"🗃️ {args.id} forgotten: moved to the archive, agents no longer use it.")
        else:  # check
            report = memory.check()
            c = report["counts"]
            print(f"Memory: {c['approved']} approved, {c['inbox']} waiting for review, {c['archive']} archived.")
            print("History intact ✅" if report["history_ok"] else
                  "HISTORY WAS CHANGED ❌ someone edited log.md by hand; approvals may not be trustworthy.")
            for p in report["problems"]:
                print(f"  ⚠️ {p}")
            return 0 if report["history_ok"] else 1
    except KeyError:
        print(f"No memory note with id {args.id}. See: revathi memory list --inbox")
        return 1
    except ValueError as exc:
        print(f"Not saved: {exc}.")
        return 1
    return 0


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # emoji output on Windows consoles
    parser = argparse.ArgumentParser(prog="revathi", description="REVATHI: the trust layer for AI agents")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("install", help="connect REVATHI to your AI tools")
    p.add_argument("--dry-run", action="store_true", help="show what would change, change nothing")
    p.set_defaults(run=cmd_install)
    p = sub.add_parser("uninstall", help="reverse what install did")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(run=cmd_uninstall)
    sub.add_parser("doctor", help="check everything is connected and working").set_defaults(run=cmd_doctor)
    p = sub.add_parser("mode", help="show or set strictness")
    p.add_argument("mode", nargs="?", choices=config.MODES)
    p.set_defaults(run=cmd_mode)
    p = sub.add_parser("log", help="what the agent did")
    p.add_argument("--session", help="session id (or its start)")
    p.add_argument("--list", action="store_true", help="list recent sessions")
    p.set_defaults(run=cmd_log)
    p = sub.add_parser("undo", help="restore what an agent action changed or deleted")
    p.add_argument("id", nargs="?", help="snapshot id (default: newest)")
    p.add_argument("--list", action="store_true", help="show snapshots instead of restoring")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(run=cmd_undo)
    p = sub.add_parser("canary", help="decoy credentials that reveal hidden instructions")
    p.add_argument("action", choices=["plant", "status"])
    p.add_argument("dir", nargs="?")
    p.set_defaults(run=cmd_canary)

    p = sub.add_parser("memory", help="what agents remember across sessions (you approve every note)")
    msub = p.add_subparsers(dest="action", required=True)
    q = msub.add_parser("propose", help="suggest a note; it waits in the inbox for approval")
    q.add_argument("--type", required=True, choices=list(memory.TYPES))
    q.add_argument("--title", required=True)
    q.add_argument("--source", action="append", default=[], help="where this came from (repeatable)")
    q.add_argument("--scope", default="user", choices=memory.SCOPES)
    q.add_argument("--project", help="project folder (scope project)")
    q.add_argument("--tool", help="tool name (scope tool)")
    q.add_argument("--by", default="agent", help="who proposes it")
    q.add_argument("text", nargs="+", help="the note itself")
    q = msub.add_parser("list", help="approved notes (or --inbox / --archive)")
    q.add_argument("--inbox", action="store_true")
    q.add_argument("--archive", action="store_true")
    for name, text in (("show", "show one note"), ("approve", "approve a note from the inbox"),
                       ("reject", "reject a note (kept in the archive)"), ("forget", "retire an approved note")):
        msub.add_parser(name, help=text).add_argument("id")
    msub.add_parser("check", help="verify history and find broken or unapproved files")
    p.set_defaults(run=cmd_memory, id=None)

    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
