"""revathi: the trust layer for AI agents.

  revathi install [--dry-run]        connect REVATHI to Claude Code and Antigravity
  revathi uninstall [--dry-run]      reverse exactly what install did
  revathi doctor                     check that everything is connected and working
  revathi mode [careful|balanced|full]   show or set how strict REVATHI is
  revathi log [--session ID] [--all] what the agent did (newest session by default)
  revathi undo [--list] [ID]         restore what an agent action changed or deleted
  revathi canary plant <dir> | status    decoy credentials that reveal hidden instructions
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # REVATHI root, for "engine"

from engine import canary, config, log, undo  # noqa: E402

try:
    import install as installer  # same folder (cli/)
except ImportError:
    from cli import install as installer

MODE_HELP = {
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

    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
