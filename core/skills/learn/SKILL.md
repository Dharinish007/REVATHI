---
name: learn
description: Turn a lesson from real use into an approved, minimal change to the Personal Agent OS (AGENTS.md, a skill, the MCP registry, or project context) - or discard it. Use when I say "remember this", "make this a rule", "add this to my debugging knowledge", "this worked", "update the skill", "remove this rule", or when reviewing LEARNINGS.md.
---

# Learn

Goal: the OS improves from experience **without growing noise**. Propose; I approve; git records; sync distributes.
Agent OS root = the folder containing this `skills/` directory.

## 1. Capture
If the lesson isn't already in `LEARNINGS.md`, add an entry (format at the top of that file). If a similar entry exists, bump its `Seen` count instead. Recording needs no approval.

## 2. Classify by scope and reuse
| If the lesson... | Destination |
|---|---|
| is a one-off event, luck, or a transient outage | **discard** (or keep as `temporary` until it recurs) |
| applies only to one repo/project | that project's own `AGENTS.md`/`CLAUDE.md`, **never** the global OS |
| is a step in a specific kind of task | the matching `skills/<name>/SKILL.md` |
| is a new, distinct, recurring procedure (no existing skill fits) | new skill, only if it has come up ≥2 times |
| describes a tool/MCP capability, limit, or risk | `mcp/registry.md` |
| is about how a specific tool is configured | `adapters/<tool>/README.md` |
| is how I want responses/work done, everywhere | `AGENTS.md` (Communication, or the relevant section) |
| is a universal behavior that prevents a recurring failure across tasks | `AGENTS.md` |

Default when unsure: the narrowest scope that fits. Skills before global rules; project before global.

## 3. Check before proposing
Read the destination file and `AGENTS.md`, then:
- **Duplicate?** Same intent already stated (even in different words), so propose sharpening that line or bumping `Seen`, not adding a new one.
- **Conflict?** Contradicts an existing rule, so show both and ask which wins. Never keep both.
- **Worth its tokens?** For `AGENTS.md`: does it fix a failure that has actually recurred (≥2 times) or that is costly when it happens? Would the model do this anyway? If not, don't promote.
- **Something to delete?** If the lesson makes an existing line obsolete, propose removing or replacing it. Prefer edit > replace > add.

## 4. Propose and wait
Show exactly this, then stop and wait for an explicit yes:
```
Learning: <title>
Destination: <file> (<why this scope>)
Checks: duplicate: <none | line> · conflict: <none | line> · recurrence: <n>
Proposed diff:
  - <removed line>
  + <added line>
Approve?
```
No reply or an ambiguous reply means no change. I may edit the proposal; re-show it if it changes materially.

## 5. Apply (after approval only)
1. Make exactly the approved edit.
2. Verify: re-read the file; check for new duplicates or contradictions; for skills, keep the frontmatter valid (`name` matches folder, `description` present); keep `AGENTS.md` ≲150 lines.
3. Remove the entry from `LEARNINGS.md` (or mark `rejected`, then delete it at the next review).
4. Commit in the Agent OS repo: `git add <files>` then `git commit -m "learn(<destination>): <title>"`, with the reason in the body. Committing is part of the approved change; ask if the approval was ambiguous.
5. Tell me to run `sync.ps1` (or run it if I ask), and report its output.

## Pruning (on "review learnings" or "prune")
- Delete inbox entries older than ~30 days with `Seen: 1`.
- Propose removing rules/skill lines that no longer earn their place: obsolete tools, duplicated elsewhere, never relevant in practice.
- Same approval format; removal diffs are welcome.

## Output
The proposal (step 4), or after applying: files changed · commit hash · sync status.
