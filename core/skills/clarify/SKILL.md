---
name: clarify
description: Ask the minimum set of focused questions needed to do a task right, in short rounds. Use when a request is ambiguous in a way that changes the result, has two or more valid interpretations, or is missing a fact you cannot find or safely default.
---

# Clarify

Goal: remove only the uncertainty that changes the outcome, at the lowest cost to the user's time.

## When to ask (all must hold)
- The answer **changes what you build or do**, not just a detail.
- You **cannot find it** in the code, files, conversation, or docs.
- A **wrong default would be costly** to undo.
Otherwise: pick the sensible default, state it in one line, and proceed.

## Procedure
1. **List the unknowns**, then cross out any you can answer by looking or safely default.
2. **Rank** the rest by impact. Ask the top **1–3** per round, never a long questionnaire.
3. **Make each question easy to answer:** offer 2–4 concrete options with your recommendation first and its tradeoff in a few words. Use the tool's question UI when it has one.
4. **Explain why you ask** only if it isn't obvious (one clause).
5. After answers: update the brief or plan, then either start work or run one more round if a new high-impact unknown appeared. Stop after 3 rounds; proceed with stated assumptions.

## Failure handling
- User says "you decide" or "do the best": choose, state the choice and why in one line, proceed.
- Answers conflict with earlier ones: point out the conflict and ask which wins.

## Output
Numbered questions, each with options (recommended first) · what you will assume for anything not asked.
