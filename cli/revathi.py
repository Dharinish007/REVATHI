"""revathi command (Phase 3 subset: undo, canary). Phase 4 adds install / doctor / mode / log.

  python cli/revathi.py undo               restore the newest snapshot
  python cli/revathi.py undo --list        show snapshots
  python cli/revathi.py undo <id>          restore one snapshot
  python cli/revathi.py canary plant <dir> put a decoy credentials file in <dir>
  python cli/revathi.py canary status      show planted decoys
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # REVATHI root, for "engine"

from engine import canary, undo  # noqa: E402


def cmd_undo(args):
    if args.list:
        snaps = undo.snapshots()
        if not snaps:
            print("No snapshots yet.")
        for m in snaps[:args.limit]:
            print(f"{m['id']}  {m['kind']:<5}  {m.get('reason', '')}")
        return 0
    for line in undo.restore(args.id):
        print(line)
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
    parser = argparse.ArgumentParser(prog="revathi", description="REVATHI: the trust layer for AI agents")
    sub = parser.add_subparsers(dest="command", required=True)
    p_undo = sub.add_parser("undo", help="restore what an agent action changed or deleted")
    p_undo.add_argument("id", nargs="?", help="snapshot id (default: newest)")
    p_undo.add_argument("--list", action="store_true", help="show snapshots instead of restoring")
    p_undo.add_argument("--limit", type=int, default=20)
    p_undo.set_defaults(run=cmd_undo)
    p_canary = sub.add_parser("canary", help="decoy credentials that reveal hidden instructions")
    p_canary.add_argument("action", choices=["plant", "status"])
    p_canary.add_argument("dir", nargs="?")
    p_canary.set_defaults(run=cmd_canary)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
