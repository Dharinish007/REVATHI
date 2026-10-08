# 📘 REVATHI: developer guide

The single source of truth for anyone building REVATHI, human or AI. Read the sections you need.
**Labels:** ✔️ verified (checked in the repo) · 💭 plan/opinion · ❓ unverified (check before relying on it).
**Current phase:** **Phase 5 (Proven) 🔨 in progress** · Phase 4 ✅ built (Antigravity live test pending) · Phase 3 ✅ (2026-10-08) · Phase 0 ✅ · Phase 1 ✅ · Phase 2 ✅ (2026-10-08) → 🌱 v0.1 scope complete.

---

## 1. In one line
**REVATHI is the trust layer for AI agents: any AI tool becomes safe, honest, remembering and consistent. Install once, works everywhere.**

## 2. The story
> An AI agent is a brilliant new employee 🧑‍💻: smart and fast, but it sometimes **says "done" when it isn't** 🤥, **breaks things by accident** 💥, **forgets what you said yesterday** 🧠, and **wastes money** 💸.
> REVATHI is the company system around that employee: 📘 handbook, 🛡️ security guard, 🧾 manager who checks proof, 📼 CCTV recorder, 🗄️ filing cabinet, ↩️ undo button, 💰 accountant.
> **The employee stays the same. The company becomes trustworthy.**

## 3. Vision, mission, principles
- 🌟 **Vision:** a world where anyone can trust AI agents: safe, correct, affordable and accountable.
- 🚀 **Mission:** build the trust layer for AI agents, so every action is checked, provable, reversible and explained in plain words.

| # | Principle | Meaning |
|---|---|---|
| 1 | 🧪 Proof over promises | No proof, no "done". Features and rules must show measured benefit. |
| 2 | 🧱 Hard rules for safety | Code blocks danger, not AI opinion |
| 3 | ♻️ Reuse first | Adopt good existing tools; build only the gaps |
| 4 | 💬 Plain language | A non-coder understands every message |
| 5 | 🙋 Human in control | AI suggests; the user approves rules, memory, deletions, spending |
| 6 | 🪶 Lean and honest | Small context; no overclaiming |

---

## 4. Problems we solve (priority order)
Feasibility % = 💭 estimate, not a measurement.

| # | Problem | Simple meaning | Solution | Type | Feasible | Phase |
|---|---|---|---|---|---|---|
| 1 | 🤥 Fake "done" | Says finished, isn't | Stop hook checks a passing test/build ran (proof receipt) | py | ~75% | 2 |
| 2 | 🎲 Not consistent | Works today, fails tomorrow | Repeated evals (3+ runs) + scorecard | py | ~70% | 5 |
| 3 | 🙈 Can't see own mistakes | Sure it's right when wrong | Scripts first (tests/lint), then independent reviewer subagent | md + py | ~60% | 1, 5 |
| 4 | 🎣 Prompt injection | Hidden text tricks the agent | "Data, not commands" rule + canary traps + guard on risky actions | md + py | ~50% | 3 |
| 5 | 💥 Dangerous actions | Deletes data, leaks secrets | Guard (deny/ask) + undo snapshot | py | ~80% (local) | 1, 3 |
| 6 | 🤫 Silent failures | Something breaks, nobody told | Black-box recorder + "ignored error" flags | py | ~70% | 2 |
| 7 | 🧠 Persistent memory | Forgets between sessions and tools | Local memory files + index + search, shared by all tools | md + py | ~80% | 7 |
| 8 | 🧪 Memory poisoning | Bad info planted for later | Approval-gated memory; source, date, expiry on every entry | py | ~65% | 7 |
| 9 | 💰 Cost ⬇️ + quality ⬆️ | Burns money, unclear value | Lean rules, skills on demand, caching, right model per task, scripts before AI; metric = cost per correct result | md + py | ~60% | 5 |
| 10 | 🤖 Subagent use | Wastes tokens, loses context | When-to-use rules + eval with/without subagents | md | ~70% | 1, 5 |
| 11 | 🪜 Weaker tools | Weaker model, weaker results | Same rules, step-by-step skills and guard everywhere; strongest model available | md + py | ~30–40% of gap | 8 |
| 12 | 🧑‍💼 Non-coders at risk | Can wreck things unknowingly | Safe modes, plain-English messages, trust earned step by step, starter packs | md + data | ~60% | 4, 8 |
| 13 | 🔀 Tool chaos | Different rules per tool | One source → installer → each tool's native location | py | ~75% | 4 |
| 14 | 📏 Hard to measure | Short tests can't judge long tasks | Long-task evals with hidden tests | py | ~50% | 8 |
| 15 | 🏢 No team control | Can't see or stop agents | Shared policy, combined logs, kill switch | py | ~50% | 8 |

**Why some scores are low:** no known method blocks injection fully (#4) · undo can't reverse emails or remote databases (#5) · quality checks cost tokens (#9) · rules improve discipline, not reasoning (#11) · #14 and #15 need the recorder first.

### Scope check: what REVATHI does
| Capability | Answer | Limit |
|---|---|---|
| 🧠 Persistent memory / second brain | ✅ Yes | Knows only what's saved; needs cleanup |
| 🔄 All agents synced | ✅ Yes, for supported tools | Each tool needs an adapter; guard needs the tool to support hooks |
| 🌍 Write once, use everywhere | ✅ Yes (`AGENTS.md` + `SKILL.md` open formats) | Hooks and subagents differ per tool |
| 👤 Adapts to the user deeply | 🟡 Grows over time | Learns only what the user allows; builds over weeks |
| ⚡ Efficient and powerful | 🟡 Must be proven | Can't make a model smarter; Agentic OS today: +6–13% tokens, no proven gain ✔️ |

### Out of scope
⚖️ Legal liability · 🧠 making models smarter / AGI · 🤖🤖 large agent swarms (until #6 and #15 exist) · 🏗️ heavy architecture (MCP gateway, thinker/doer split): integrate later.

---

## 5. Core idea: advice vs enforcement
| | 📝 Advice (`.md`) | ⚙️ Enforcement (`.py` at hooks) |
|---|---|---|
| Who runs it | The AI reads it | The computer runs it |
| Reliability | Most of the time | Every time |
| Can the AI skip it? | Yes (forgets, gets tricked) | No |
| Use for | How to think and work | What must always or never happen |
| Analogy | "Please don't enter" sign | Locked door with key card |

**Rule:** must never fail → code. Guidance → Markdown. About 70% of REVATHI is code, 30% Markdown (💭 estimate).

**Why Python (D7, proposed):** the existing guard is Python with 39 passing tests ✔️; widely installed; readable; standard library only, so hooks run anywhere. Risk: some non-coders lack Python → ship a single binary later.

---

## 6. Architecture

### 6.1 Components
| Component | Analogy | Job | Type |
|---|---|---|---|
| 📘 Rules (`core/AGENTS.md`) | Handbook | How to think, verify, report | md |
| 🧰 Skills (`core/skills/`) | Training manuals | Step-by-step procedures, loaded on demand | md |
| 👥 Subagents (`core/agents/`) | Expert colleagues | Reviewer, researcher | md |
| 🛡️ Guard (`engine/guard`) | Security guard | Before every action: allow / ask / deny | py |
| 🧾 Proof (`engine/proof`) | Manager | Blocks "done" without passing tests | py |
| 📼 Recorder (`engine/log`) | CCTV | Hash-chained log of every action and result | py + jsonl |
| ↩️ Undo (`engine/undo`) | Backup | Snapshot before risky steps; restore | py |
| 🗄️ Memory (`engine/memory`) | Filing cabinet | Save (with approval), search, expire | py + md |
| 💰 Cost (`engine/cost`) | Accountant | Tokens and cost per correct result | py |
| 📋 Policy (`policy/`) | Company policy | Deny/ask lists, modes, packs | toml |
| 🔌 Adapters (`adapters/`) | Interpreters | Translate each tool's events ↔ common format; install paths | py + md |
| ⌨️ CLI (`cli/`) | Front desk | `revathi install / doctor / mode / undo / log / eval` | py |
| 🧪 Evals (`evals/`) | Quality audit | Prove REVATHI helps: baseline vs REVATHI | py + md |

### 6.2 File type per problem
| Problem # | md | py | data |
|---|---|---|---|
| 1 Fake done | `verify-before-done` skill | Stop hook | receipt (json) |
| 2 Consistency | eval task specs | eval runner, scorecard | results (csv) |
| 3 Own mistakes | review skill, reviewer agent | run tests/lint first | – |
| 4 Injection | "data, not commands" rule | canary check in guard | canaries |
| 5 Danger | safety rules | guard + undo | policy (toml) |
| 6 Silent fails | – | recorder | actions (jsonl) |
| 7–8 Memory | memory notes, `learn` flow | save/search/validate | memory files + index |
| 9 Cost | lean-context guide | cost tracker | token records |
| 10 Subagents | when-to-use rules | – | agent files |
| 11 Weaker tools | step-by-step skills | same guard | – |
| 12 Non-coders | plain messages, packs | mode switcher | presets |
| 13 Sync | one source | installer CLI | adapter map |
| 14 Measure | long-task specs | hidden-test checker | fixtures |
| 15 Teams | team policy doc | log export, kill switch | team policy |

### 6.3 Folder structure (💭 target)
```
REVATHI/
├── AGENTS.md  CLAUDE.md  README.md  CHANGELOG.md
├── revathi_dev_guide.md  revathi_decisions.md
├── core/                 📝 portable source, tool-neutral
│   ├── AGENTS.md         rules shipped to users (not the same file as ./AGENTS.md)
│   ├── skills/<name>/SKILL.md
│   └── agents/<name>.md
├── engine/               ⚙️ one Python package, stdlib only
│   ├── event.py          common event format (Event, Decision)
│   ├── policy.py         loads policy/*.toml
│   ├── guard.py          allow / ask / deny
│   └── proof, log, undo, memory, cost   (one module each, added by phase; split into packages only when they grow)
├── policy/               📋 default.toml, modes/, packs/
├── adapters/             🔌 claude-code/, antigravity/, codex/, cursor/, gemini/, opencode/
├── cli/                  ⌨️ revathi command
├── evals/                🧪 tasks/, runner, scorecard
└── tests/                ✅ unit tests for engine + adapters
```
Note: `./AGENTS.md` = rules for agents **building** REVATHI. `core/AGENTS.md` = rules REVATHI **ships to users**.

### 6.4 Common event format (💭 draft)
Adapters convert each tool's hook input into one shape, so the engine is written once:
```json
{"tool": "claude-code", "kind": "command | write | read | stop | other",
 "command": "...", "path": "...", "content": "...", "session": "...", "raw": {}}
```
And one decision shape back: `allow` · `ask` (with reason) · `deny` (with reason), which the adapter translates to the tool's format.
✔️ The Agentic OS guard already does this for 2 tools in one file (Claude Code `tool_name/tool_input`, Antigravity `toolCall`).

### 6.5 How one task flows
```
👤 "Fix the login bug"
   │
📘 Rules + 🗄️ Memory load  →  🧰 "debugging" skill opens
   │
🤖 Agent wants to act (edit / run)
   │
🛡️ GUARD ── ⛔ deny (wipe disk, leak key)
   │     └─ ❓ ask (git reset --hard)
   │     └─ ✅ allow
   │
↩️ Snapshot (if risky) + 📼 Recorder logs it
   │
🤖 "Done!"
   │
🧾 PROOF: tests ran and passed?
   ├─ ❌ → "Not done: run the tests" 🔁
   └─ ✅ → plain-English report
   │
💰 Cost logged · 🗄️ Lesson → inbox (user approves)
```

### 6.6 How a user turns it on (💭 planned)
| Step | User does | Result |
|---|---|---|
| 1 | `pip install revathi` or install the Claude Code plugin | Files downloaded |
| 2 | `revathi install` | Detects AI tools; installs rules, skills, guard into each |
| 3 | `revathi mode balanced` | 🛡️ careful / ⚖️ balanced / 🚀 full |
| 4 | `revathi doctor` | Shows what is active in which tool |
| 5 | Use the AI tool normally | REVATHI runs silently |
| 🆘 | `revathi undo` · `revathi log` | Restore · see what happened |

### 6.7 Tool support facts
| Tool | Rules file | Skills | Hooks (needed for guard/proof) |
|---|---|---|---|
| Claude Code | `~/.claude/CLAUDE.md` | `~/.claude/skills/` | ✔️ PreToolUse used in Agentic OS · ❓ Stop hook for proof: test in Phase 2 |
| Antigravity | `~/.gemini/GEMINI.md` | `~/.gemini/config/skills/` | ✔️ hooks.json used in Agentic OS |
| Codex | `~/.codex/AGENTS.md` | `~/.agents/skills/` | ❓ check |
| Gemini CLI | `~/.gemini/GEMINI.md` | `~/.agents/skills/` | ❓ check |
| Cursor | Settings UI (manual) | `~/.agents/skills/` | ❓ check |
| OpenCode | ❓ | ❓ | ❓ |
Paths from Agentic OS `adapters/README.md` (checked against docs 2026-09/10). Re-check before each adapter is built.

---

## 7. Reuse from Agentic OS (`../`)
Copy into REVATHI and adapt. Never edit the originals.

| Asset | Path | Plan |
|---|---|---|
| 16 skills ✔️ | `../skills/*/SKILL.md` | Reuse; trim; keep only what earns its place |
| Rules | `../AGENTS.md` | Base for `core/AGENTS.md`; shorter, trust-focused |
| Guard + 39 tests ✔️ | `../adapters/claude-code/plugin/hooks/guard.py`, `test_guard.py` | Split into engine + adapters; move lists into policy; fix 2 holes (below) |
| Hook config | `../adapters/claude-code/plugin/hooks/hooks.json` | Template for the Claude Code adapter |
| Subagents | `../adapters/claude-code/plugin/agents/` | Reuse reviewer + researcher |
| Commands | `../adapters/claude-code/plugin/commands/` | Reuse idea / next / verify / review |
| Presets ✔️ | `../adapters/claude-code/presets/` (careful, balanced, full) | Become `policy/modes/` |
| Evals ✔️ 10 tasks | `../evals/` (run.py, scorecard.py, tasks/) | Reuse; add cost per correct result; run the 7 untested tasks |
| Tool paths | `../adapters/*/README.md` | Reference for adapters |
| Lesson inbox | `../LEARNINGS.md`, `../skills/learn/` | Basis for approval-gated memory |
| Sync | `../sync.ps1` | ❌ Don't port (Windows-only); replace with the cross-platform CLI |

**Known guard holes ✔️ (reproduced 2026-10-07), fix in Phase 1:**
1. Secrets written through shell commands are not scanned (`echo API_KEY="sk-ant-…" > config.py` → allowed).
2. Git flags before the subcommand bypass the patterns (`git -C . reset --hard` → allowed).

---

## 8. Roadmap
Each phase ends only when its **done-criterion** is shown with evidence.

| Phase | Goal | Builds | Problems | Done when |
|---|---|---|---|---|
| 0 📄 Docs ✅ | Shared understanding | These docs | – | Docs written and reviewed |
| 1 🧱 Foundation ✅ | Clean base | Folder structure; `core/` rules + skills ported; `engine/event.py`; policy file; guard ported with 2 holes fixed; Claude Code adapter | 5, 3, 10 | Guard tests pass, including both holes and a dangerous-command test set; works live in Claude Code |
| 2 🧾 Trust ✅ | No fake "done" | Proof Stop hook + receipt; recorder | 1, 6 | "Done without proof" is blocked in a live test; every action appears in the log |
| 3 ↩️ Safety net ✅ | Survive mistakes | Undo snapshot/restore; canary traps | 5, 4 | Seeded destructive action restored by `revathi undo`; canary touch is flagged |
| 4 ⌨️ Front desk 🔨 | One-command setup | CLI: install / doctor / mode / undo / log; Antigravity adapter; Windows + Mac/Linux | 13, 12 | Fresh machine → `revathi install` → `revathi doctor` all green in 2 tools |
| 5 🧪 Proven 🔨 | Evidence | All evals 3+ runs, baseline vs REVATHI; cost per correct result; CI | 2, 3, 9, 10 | Scorecard shows a verdict for every skill; neutral + costly skills cut |
| 6 🚀 Launch | Public v1 | GitHub release, Claude Code plugin, PyPI; real README; license | – | A new user installs from a public channel and passes the quick start |
| 7 🧠 Memory | Second brain | Memory store, index, search, approval, expiry | 7, 8 | Facts survive across sessions and 2 tools; a planted bad memory is rejected |
| 8 🌍 Expand | Reach + scale | Codex, Cursor, Gemini, OpenCode adapters; starter packs; long-task evals; team mode | 11, 12, 14, 15 | Same skill passes the same eval in 3+ tools |

**Quick wins inside Phase 1–2:** fix guard holes → proof hook → cost metric → simple log.

### Releases (build in thin slices: one tool first, every slice working and tested)
| Release | Phases | What the user gets |
|---|---|---|
| 🌱 v0.1 | 1 + 2 | Safe + honest agent in Claude Code |
| 🌿 v0.2 | 3 + 4 | Undo + one-command install, 2 tools |
| 🌳 v0.5 | 5 | Evidence: scorecard proves the benefit |
| 🚀 v1.0 | 6 | Public launch |
| 🧠 v1.x | 7 | Second brain (memory) |
| 🌍 v2.0 | 8 | Every tool + teams |

**Why this order:** the guard is the gate every later feature runs through · the recorder feeds proof, cost and teams · one tool first keeps mistakes cheap, the second proves portability · evals before launch so we never ship unproven claims · memory after a stable base · expansion last (largest scope).

### Phase 1 checklist
- [x] Folders: `core/`, `engine/`, `policy/`, `adapters/claude-code/`, `tests/`
- [x] `core/AGENTS.md` (rules shipped to users), `core/skills/` (16, copied as-is; trimming waits for Phase 5 evidence), `core/agents/` (reviewer, researcher)
- [x] `engine/event.py`, `engine/policy.py`, `engine/guard.py`; lists in `policy/default.toml`
- [x] Fix hole 1 (secrets via shell) and hole 2 (git global options)
- [x] Claude Code adapter (`adapters/claude-code/hook.py` + hook config)
- [x] Tests: ported Claude Code cases + holes + dangerous-command set, all passing (58 cases + 3 adapter checks; the old guard fails 12 of the new cases)
- [x] Live test in a real Claude Code session (2026-10-08, project hook): secret in a shell command was blocked with the REVATHI message and no file written · `git -C . rebase --abort` and `find … -delete` asked for confirmation · `ls` ran normally. Caveat: for the two "ask" tests, the REVATHI reason text was not confirmed; Claude Code's default permissions can also ask

**Phase 1 notes:** hook round-trip ≈100 ms, mostly Python startup (target <100 ms; revisit in Phase 4) · skills `add-mcp` and `learn` still point at Agentic OS files (`mcp/registry.md`, `LEARNINGS.md`): adapt when memory lands (Phase 7) · guard false positive seen: fake keys in test fixtures get blocked; tests build them at runtime.

### Phase 2 checklist
- [x] Confirm from the Claude Code docs that a Stop hook can block finishing (`decision: "block"`, `stop_hook_active`, 8-continuation cap) and that PostToolUseFailure reports failed Bash commands
- [x] `engine/log.py`: recorder, one JSONL file per session in `~/.revathi/logs/`, hash-chained, secrets redacted, no command output stored
- [x] `engine/proof.py` + `[proof]` in the policy: after a code edit, finishing is blocked until a check passes; blocks once, then records `unproven`
- [x] Claude Code adapter handles PreToolUse, PostToolUse, PostToolUseFailure, Stop; `settings.example.json`
- [x] Tests: `tests/test_proof.py` (12 proof + 4 recorder tests), guard tests unchanged; 23/23 pass
- [x] Live test in a real Claude Code session (2026-10-08): the agent was told not to test; the proof check sent it back once with the REVATHI reason, and it then told the user plainly the fix was unverified. Log: 7 records, hash chain intact. **Bug found:** the already-disclosed `calc.py` gap blocked the next, docs-only turn too. Fixed (only judge records after the last `unproven`), 2 regression tests added, and a replay of the real log no longer blocks.

**Phase 2 limits (honest):** edits made through shell commands aren't seen as code edits · checks are recognized by command patterns · "passed" = exit 0 and no failure text; it can't judge test quality · each tool call now runs the hook twice (before + after), about 100 ms each.

### Phase 3 checklist
- [x] `engine/undo.py`: snapshots before file writes (copies) and before risky commands (git: hidden commit under `refs/revathi/`, user's branch/staging/stash untouched; outside git: copy of folders about to be deleted, ≤50 MB); keeps newest 200; undo of an undo
- [x] `engine/canary.py`: opt-in decoy `credentials.backup` with a unique fake key; touching the decoy → ask; the key in any action → deny
- [x] `cli/revathi.py`: `undo [--list] [id]`, `canary plant <dir> | status` (rest of the CLI in Phase 4)
- [x] Hook: canary → guard → snapshot; ask messages say "a snapshot was saved" or "cannot be undone"
- [x] Tests: `tests/test_safety_net.py` (13: real `reset --hard` + `clean -fd`, moved branch, `rm -rf` outside git, overwrite, new file, undo of undo, unsaveable command, canary read/leak/normal/log, pruning); 36/36 pass
- [x] Live test in a real Claude Code session (2026-10-08, throwaway repo outside the project): `git -C <repo> reset --hard` asked with "a snapshot was saved", the user approved, work was lost, and `revathi undo` brought back "important unsaved work" ✅ · reading the decoy asked ✅ (recorded) · the fake-key `curl` was reported blocked, but **no REVATHI record exists** for it, so the block came from somewhere else (likely the agent declining, or Claude Code itself). Replaying that exact command through the hook → REVATHI denies it. Log chain intact; fake key never written to the log.

**Phase 3 notes:** found while timing: pruned git snapshots left hidden refs behind → fixed with a regression test (my timing run had also created 7 refs in the real Agentic OS repo; removed) · undo is local only (no pushes, publishes, messages, databases) · canary catches only attacks that touch the decoy.

### Phase 4 checklist
- [x] `engine/pipeline.py`: one tool-neutral flow (before / after / finish) so adapters only translate; "block once" now tracked in the log, not a tool flag
- [x] Antigravity adapter (`adapters/antigravity/hook.py`): PreToolUse, PostToolUse, Stop (`decision: continue`), from the Antigravity hooks docs
- [x] `cli/install.py` + `revathi install [--dry-run] | uninstall | doctor`: runtime copied to `~/.revathi/app`; Claude Code hooks merged into `settings.json`, skills + subagents placed (conflicts left alone), Agent OS plugin disabled; Antigravity `revathi` hooks group + skills; backups; uninstall reverses exactly what install recorded
- [x] `revathi mode careful|balanced|full` (REVATHI strictness only) and `revathi log`
- [x] Tests: `test_antigravity.py` (6), `test_install.py` (12, fake home), all suites 56/56; mutation check: 2 planted installer bugs caught
- [x] Cross-platform: Python only (no `.ps1`); `python` on Windows, `python3` elsewhere. ✅ CI green on Windows, Linux, macOS (2026-10-08)
- [x] Real install on this machine + `revathi doctor` all green in Claude Code and Antigravity (2026-10-08)
- [x] Live test in Claude Code after install: risky command asked with "snapshot saved" and was recorded
- [ ] Live test in Antigravity. **Antigravity IDE** loads REVATHI's hooks (its log), the quoting fix is untested live there. **Antigravity 2.0** (v2.15.0) shows no hooks loading at all, though its bundled docs say `~/.gemini/config/hooks.json` is read; REVATHI skills do reach it. Cause unknown ❓

**Phase 4 notes:** live: Antigravity hooks loaded but failed (quoted path under `cmd /c`) → fixed; `ask` → `force_ask` (D24) · the real-machine dry run found a crash the tests missed (`claude plugin list` prints `❯`, Windows decoded it wrongly) → fixed + test · the "disabled" wording of `claude plugin list` is assumed, not seen yet.

### Phase 5 checklist
- [x] `revathi mode observe` (audit only) so baseline runs also produce an objective log
- [x] Subagents: own log per `agent_id`; `SubagentStop` proof check; installer registers it
- [x] Shell code edits (`sed -i`, `perl -i`, `>`, `>>`, `tee`, `Set-Content`) count as code edits (found in the eval pilot: an agent edited with `sed -i` and REVATHI saw no change)
- [x] `evals/` harness: prepare / grade / scorecard; tasks `verify-feature`, `debug-pagination`, new pressure task `rush-fix`
- [x] Batch 1: 3 tasks × 3 runs × A/B (18 runs) → `evals/SCORECARD.md`
- [ ] Top-level-session runs (Stop block works there): needs headless CLI login or manual runs
- [x] Explain why `SubagentStop` blocks did not continue in-app subagents: the report is delivered via `SubagentHandback` before `SubagentStop`; the proof check now gates the handback. Batch 2: pressure task verified 0/3 → 2/3 (see `evals/FINDINGS.md`)
- [x] CI: `.github/workflows/revathi-tests.yml` (Windows, Linux, macOS × Python 3.11/3.13)
- [x] Name the project's test files in the send-back reason; batch 3: pressure task B 5/5 pass and verified. Totals A → B: pass 4/5 → 7/8, verified 1/5 → 7/8, tokens per correct 72k → 66k (see `evals/FINDINGS.md`)
- [ ] More pressure tasks (hidden failure behind `| tail`, "just push it") so the gain isn't one task's quirk
- [ ] Weaker-model runs; skill verdicts with cost

**Batch 1 result (honest):** pass 8/9 → 8/9, verified 6/9 → 7/9, honest 9/9 → 9/9, tokens 57k → 57k. REVATHI detected every unverified finish but could not enforce it on in-app subagents. Neutral on outcome, zero model cost.

### Backlog (later, not now)
Cross-model second opinion · hidden tests / mutation testing · thinker/doer split · MCP gateway · skill registry with evidence scores · "REVATHI-verified" badge · formal verification (research only).

---

## 9. How it scales
| Need | How |
|---|---|
| New AI tool | Add one adapter; the engine is unchanged |
| New danger | Edit the policy file; no code |
| New skill | Add a folder with `SKILL.md` (open standard) |
| Domain packs | Policy + skill packs (e.g. `db-pack`, `aws-pack`) |
| Memory growth | Plain files first; SQLite only when needed (stdlib) |
| Teams | Shared policy + combined logs + kill switch |
| Speed | Pattern checks only in hooks, no AI calls; target <100 ms |
| Quality | CI runs tests + evals before every release |

**Future path:** personal → team → company governance → ecosystem of packs → any agent type (browser, email, data) → a trust standard/badge.

---

## 10. Publishing (💭 planned, D13)
| Channel | For |
|---|---|
| GitHub (source, releases) | Everyone |
| Claude Code plugin (marketplace) ❓ exact steps | Claude Code users |
| PyPI (`pip install revathi`) ❓ name availability | Developers |
| Other tool stores/extensions ❓ | Their users |
| Docs page | Non-coders |

Versioning: Semantic Versioning + `CHANGELOG.md`. Releases only after tests and evals pass, and only with user approval.

## 11. Quality bar
- ✅ Every engine module has unit tests; adapters have event-shape tests.
- ⚡ Hooks: stdlib only, no network, target <100 ms, fail safe (D10).
- 🔒 No secrets in code, logs, tests, commits. No telemetry (D11).
- 💬 Every user-facing message: what happened, why, what to do, in plain words.
- 🧾 Every claim in docs labelled; every feature tied to a done-criterion.

## 12. Glossary
| Term | Meaning |
|---|---|
| Hook | A script the AI tool runs automatically at a moment (before an action, at stop); it can block |
| Guard | REVATHI's hook that decides allow / ask / deny |
| Adapter | Small translator between one AI tool and REVATHI's engine |
| Policy | The settings file listing what to block, ask or allow |
| Skill | A Markdown procedure the AI loads only when the task needs it |
| Subagent | A helper AI with its own context for a focused job |
| Eval | A fixed test task run with and without REVATHI to measure benefit |
| Receipt | Proof that tests/builds ran and passed, checked by a script |
| Canary | A fake key or tool with no real use; touching it signals an attack |
