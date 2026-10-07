# REVATHI: decisions

Why we chose what we chose, so nobody re-argues it.
Status: **Accepted** (user approved) · **Proposed** (waiting for the user) · **Replaced** (kept for history; points to the new one).
Agents may add *Proposed* entries. Only the user accepts them.

| ID | Decision | Status | Why | Date |
|---|---|---|---|---|
| D1 | Name the project **REVATHI**, built from scratch | Accepted | A fresh start focused on trust; Agentic OS is reference only | 2026-10-08 |
| D2 | Use standard file names: `README.md`, `CHANGELOG.md`, `AGENTS.md`, `CLAUDE.md`; `revathi_` prefix only for custom docs | Accepted | GitHub and AI tools auto-detect only the exact standard names | 2026-10-08 |
| D3 | Keep `REVATHI/` inside the Agentic OS folder and repo **for now** | Accepted | Easy reuse while starting. Known risks: Agentic OS rules may also load; files commit to the Agentic OS repo. Revisit before launch. | 2026-10-08 |
| D4 | Promise **trust, not intelligence**; no AGI claims | Accepted | Rules can't make a model smarter; overclaiming destroys trust | 2026-10-08 |
| D5 | Problem list and priority order in the dev guide §4 | Accepted | Agreed in planning (2026-10-07/08) | 2026-10-08 |
| D6 | Two layers: **Markdown = advice**, **code at hooks = enforcement** | Proposed | An AI can skip instructions; it can't skip a hook. Safety needs enforcement. | 2026-10-08 |
| D7 | **Python** for the engine (standard library only) | Proposed | Existing guard is Python (39 tests); widely installed; readable. Risk: non-coders may lack Python → later ship a single binary. Alternatives: Node (`npx`), Go/Rust binary. | 2026-10-08 |
| D8 | Minimum Python version **3.11** | Proposed | Gives `tomllib` (TOML reading) in the standard library; 3.11 is widely available. | 2026-10-08 |
| D9 | Policy file in **TOML** (`policy/default.toml`) | Proposed | Human-friendly like YAML, but readable with the standard library (YAML would need a dependency, breaking D7). | 2026-10-08 |
| D10 | Hooks **fail safe**: if the check of a command or file write crashes, answer **ask** (the user decides) | Proposed | A broken guard must not become an open door, but a bug must not freeze all work either, so *ask*, not *deny*. Unreadable input (not a tool event) is ignored. Implemented in Phase 1. | 2026-10-08 |
| D11 | **Local and private by default**: no network, no telemetry | Proposed | Trust product; works offline; nothing leaves the machine | 2026-10-08 |
| D12 | Memory is **approval-gated**: agents propose, the user approves | Proposed | Prevents memory poisoning; the user stays in control | 2026-10-08 |
| D13 | Distribution: GitHub → Claude Code plugin → PyPI, then other tool stores | Proposed | Reaches developers first; exact store steps still to check | 2026-10-08 |
| D14 | Recorder logs go to `~/.revathi/logs/<session>.jsonl` (override: `REVATHI_HOME`); commands only, trimmed and redacted; no output | Proposed | Keeps users' repos clean; private and local (D11); output could hold secrets or personal data | 2026-10-08 |
| D15 | Proof check **blocks once**: if the agent stops again, it may finish, and the log records `unproven` | Proposed | Some projects have no tests; blocking forever would trap the agent. One push back plus an honest record is enough | 2026-10-08 |
| D16 | Proof only applies to **code** files (list in policy); docs and config edits don't need a check | Proposed | Avoids nagging on README or settings edits; list is easy to extend | 2026-10-08 |
| D17 | Undo snapshots: file copies before every write; before risky commands a hidden git commit (`refs/revathi/snapshots/*`) in git repos, else a copy of folders being deleted (≤50 MB); newest 200 kept in `~/.revathi/snapshots` | Proposed | Cheap, never touches the user's branch, staging or stash; works without git for deletes | 2026-10-08 |
| D18 | Canary is **opt-in** (`revathi canary plant <dir>`); decoy read → ask, fake key in any action → deny | Proposed | Planting files in users' projects without asking would be intrusive; near-zero false alarms | 2026-10-08 |

## Open questions (need the user)
| ID | Question | Options |
|---|---|---|
| Q1 | License | MIT · Apache-2.0 · other |
| Q2 | Move REVATHI to its own repo? When? | Before Phase 6 (launch) is suggested |
| Q3 | Business model | Free core only · free core + paid team features later |
