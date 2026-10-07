---
name: explain
description: Present reasoning, decisions, plans, and results in a short, scannable, presentable way. Use when reporting what you did or found, justifying a decision, presenting a plan or analysis, or when asked to explain, summarize, or "show your thinking".
---

# Explain

Goal: the reader understands what happened, why, and what they need to do, in under a minute.

## Procedure
1. **Lead with the answer or result** in one line. No preamble, no restating the question.
2. **Show the reasoning as a short chain**, not a narrative: 3–6 steps of "observed → so → therefore". Include only steps that change the conclusion.
3. **Pick the format by content:**
   - comparisons → table
   - sequences or flows → numbered steps or a diagram (e.g. Mermaid)
   - commands and code → code blocks
   - nuanced tradeoffs → a few sentences of prose
4. **Separate certainty levels** when it matters: verified, inferred, assumed.
5. **End with what the reader must decide or do**, if anything. Skip the recap.
6. **Fit the reader** (see `user-lens`): define jargon for beginners, skip basics for experts. Match their language and tone, including emojis if they use them.

## Failure handling
- Long output is unavoidable: put the summary first and details under headings.
- Bad news (failure, risk, wrong premise): state it plainly in the first lines, not buried.

## Output
Answer first · short reasoning chain · structured details · decisions needed from the reader.
