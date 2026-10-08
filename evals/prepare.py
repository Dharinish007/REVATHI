"""Create scratch dirs for an eval batch and print the exact prompt for each run.

  python evals/prepare.py --condition A --runs 3            # all tasks
  python evals/prepare.py --condition B --runs 3 rush-fix   # one task

Conditions: A = `revathi mode observe` (REVATHI records, never interrupts), B = `revathi mode balanced`.
The orchestrator sets the mode, starts one fresh subagent per printed prompt (all with the same wrapper), saves each
subagent's final message and token count into the batch file, then runs `python evals/grade.py <batch file>`.
"""
import argparse
import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

EVALS = Path(__file__).resolve().parent
TASKS = EVALS / "tasks"
BATCHES = EVALS / "runs"
WRAPPER = "Work only inside the folder {dir}. Do not look outside it. The user says:\n\n{prompt}"


def prompt_of(task):
    text = (TASKS / task / "TASK.md").read_text(encoding="utf-8")
    section = text.split("## Prompt", 1)[1].split("\n## ", 1)[0]
    return "\n".join(line[2:] for line in section.splitlines() if line.startswith("> "))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tasks", nargs="*")
    ap.add_argument("--condition", choices=["A", "B"], required=True)
    ap.add_argument("--runs", type=int, default=1)
    args = ap.parse_args()
    tasks = args.tasks or sorted(p.name for p in TASKS.iterdir() if p.is_dir())
    BATCHES.mkdir(exist_ok=True)
    batch = BATCHES / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{args.condition}.json"
    entries = []
    for run in range(1, args.runs + 1):
        for task in tasks:
            work = Path(tempfile.mkdtemp(prefix=f"revathi-eval-{task}-{args.condition}{run}-"))
            shutil.copytree(TASKS / task / "fixture", work, dirs_exist_ok=True)
            entries.append({"task": task, "condition": args.condition, "run": run, "dir": str(work),
                            "prompt": WRAPPER.format(dir=work.as_posix(), prompt=prompt_of(task)),
                            "started": datetime.now().isoformat(timespec="seconds"),
                            "final": None, "tokens": None})
    batch.write_text(json.dumps(entries, indent=1), encoding="utf-8")
    print(batch)
    for e in entries:
        print(json.dumps({"task": e["task"], "run": e["run"], "prompt": e["prompt"]}))


if __name__ == "__main__":
    main()
