---
name: planning
description: Produce an implementation plan before coding a multi-step feature, refactor, migration, or architectural change. Use when the task touches several files or systems, has real design choices, or when asked to plan, design, or propose an approach.
---

# Planning

Goal: a plan the user can approve or correct before effort is spent, grounded in the actual code.

## Procedure
1. **Explore first** (see codebase-analysis): read the code the change will touch. Plans written before reading are guesses.
2. **Define done:** the success criterion and how it will be verified.
3. **Choose an approach.** If there are real alternatives, give the recommended one plus at most one alternative with the tradeoff in a line. Prefer the simplest approach that meets the requirement.
4. **Write the plan:** ordered steps, each naming the files/components it changes and how that step is checked. Flag risky or irreversible steps (migrations, deletions, API changes).
5. **List open questions** that block or change the plan. Ask them now, not mid-implementation.
6. For long plans, save to a file so it survives context compaction and can be tracked.

## Failure handling
- Requirements too unclear to plan: ask the smallest set of questions that unblock it.
- Exploration shows the task is trivial: skip the formal plan and say so.

## Output
Goal + done criterion · recommended approach · numbered steps (files, verification) · risks · open questions.
