---
name: codebase-analysis
description: Build an accurate understanding of an unfamiliar repository or subsystem - structure, architecture, entry points, data flow, and conventions. Use when starting work in a new repo, when asked "how does X work", or before a change that spans multiple modules.
---

# Codebase analysis

Goal: a correct, evidence-backed mental model of the code relevant to the task, built with minimal reading.

## Inputs
- The question or upcoming task (it defines what "relevant" means - don't map the whole repo without reason).

## Procedure
1. **Orient cheaply:** README, project AGENTS.md/CLAUDE.md, manifest files (package.json, pyproject, go.mod...), top-level tree, build/test commands.
2. **Find entry points** for the area in question: routes, CLI commands, main, handlers, jobs.
3. **Trace the real flow** for one concrete path end-to-end (input → processing → storage/output), reading the files on that path. Use search to jump; read whole functions, not fragments.
4. **Note conventions** that will constrain changes: existing helpers, error handling, testing style, naming.
5. **Check claims against code**, not docs alone - docs drift.
6. For large repos, delegate broad searches to a subagent if the tool supports it, and keep only conclusions in context.

## Failure handling
- Dynamic dispatch, generated code, or config-driven behavior you can't trace statically: say where the trail goes cold and what running it would reveal.

## Output
Short map: key components and their roles · the traced flow with `file:line` references · conventions to follow · open questions. Scale length to the question.
