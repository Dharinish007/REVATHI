---
name: next-best-step
description: Decide the single most valuable action to take right now and who should take it. Use when the user asks "what next", "what should I do", gives an idea without a plan, finishes a milestone, is stuck between options, or when several tasks compete.
---

# Next best step

Goal: one clear recommendation that moves the real goal forward the most for the least cost and risk.

## Procedure
1. **Anchor on the goal and done criterion.** If they're unclear, the next best step is to clarify them (see `idea-intake`).
2. **List candidate actions** (usually 3–5), including "ask the user" and "do nothing yet".
3. **Score each quickly:**
   - **Value:** how much closer to the goal.
   - **Unblocks:** does it enable other work or remove a big unknown?
   - **Cost:** time, tokens, user effort.
   - **Risk:** reversibility, chance of wasted work.
   Prefer steps that remove the biggest uncertainty early, and urgent safety fixes before features.
4. **Decide who acts:**
   - **Agent does it** when it is in scope, reversible, and the user asked for execution.
   - **Ask first** when it is irreversible, outward-facing, costly, or outside what was asked.
   - **User does it** when it needs their credentials, judgment, accounts, or physical action.
5. **Recommend one step**, with a one-line why. Mention at most one alternative.

## Failure handling
- Candidates are tied: pick the more reversible one.
- The step depends on a decision only the user can make: present that decision as the step.

## Output
Recommended step · why (one line) · who does it · what comes after (one line) · alternative (optional).
