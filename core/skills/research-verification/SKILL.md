---
name: research-verification
description: Research a question and verify the claims in the answer against independent, primary sources. Use for technical/factual questions where accuracy matters, comparisons, "what's the current/best/latest", checking a claim, or any research report.
---

# Research verification

Goal: an answer whose important claims are each backed by evidence of known quality, with disagreements and gaps visible.

## Inputs
- The question and what decision it feeds (sets how much verification is worth doing).
- Time sensitivity: does "current" matter?

## Procedure
1. **Decompose** the question into the specific claims the answer will depend on. Mark which are load-bearing.
2. **Search broadly, then go to the source.** Use search to find candidates; confirm load-bearing claims in primary sources (official docs, specs, changelogs, source code, papers, original data). Note publication dates.
3. **Cross-check** each load-bearing claim with a second independent source. Two articles citing the same origin count as one.
4. **Challenge the draft.** Look for evidence against your conclusion: known issues, deprecations, contrary benchmarks, newer versions.
5. **Resolve conflicts:** prefer primary over secondary, newer over older for changing facts, measured over asserted. If unresolved, report both sides.
6. **Synthesize** only from verified material. Label each point as verified, single-source, or inference.

## Failure handling
- No primary source found: say so and label the claim accordingly.
- Sources conflict and can't be resolved: present the conflict and which way you lean, with why.
- Search tool unavailable: answer from knowledge, flagged as unverified with your cutoff date.

## Output
Answer first · key claims with confidence labels · sources (linked, dated when relevant) · open questions / conflicts.
