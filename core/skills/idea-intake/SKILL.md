---
name: idea-intake
description: Turn a raw idea, vague request, or "I want to build X" into a clear brief before any work starts. Use when the user shares an idea, a goal without specifics, a new project or feature concept, or says "what do you think", "help me build", "I have an idea".
---

# Idea intake

Goal: a short brief that the user confirms, so the work solves the real problem for the real user.

## Procedure
1. **Restate the idea in one line**, in your own words. If you can't, you don't understand it yet.
2. **Look before asking.** Read the existing project, files, or context the idea touches; answer what you can yourself.
3. **Draft the brief** from what you know, marking each field as known, inferred, or unknown:
   - **Goal:** the outcome, not the feature ("users find X faster", not "add search").
   - **For whom:** the primary user and their situation (see `user-lens`).
   - **Done when:** an observable, checkable result.
   - **Scope:** in, out, and what is deliberately deferred.
   - **Constraints:** stack, time, budget, platforms, must-keep behavior.
   - **Risks / unknowns:** what could make this wrong or wasted.
4. **Resolve unknowns that change the result** with `clarify`. Fill the rest with sensible defaults and say so.
5. **Give an honest take:** is the idea sound? Name a simpler or stronger version if one exists, and anything that already solves it.
6. **Recommend the next step** with `next-best-step`, and state whether you will do it or the user should.

## Failure handling
- Idea is a one-line trivial task: skip the brief, just do it.
- User only wants to brainstorm: give options and tradeoffs, no brief or plan.
- The premise looks wrong: say so with evidence before building anything.

## Output
One-line restatement · brief (goal, for whom, done when, scope, constraints, risks) · honest take · questions (if any) · recommended next step.
