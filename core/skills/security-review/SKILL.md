---
name: security-review
description: Assess code, configuration, dependencies, or an MCP/tool/third-party skill for security risks. Use when asked for a security review, before handling auth/payments/user data/secrets, when adding a new dependency or MCP server, or when working in an untrusted repository.
---

# Security review

Goal: find exploitable weaknesses with concrete attack paths, not a generic checklist dump.

## Procedure
1. **Map the attack surface:** where untrusted input enters (HTTP, files, env, CLI args, LLM/tool output), what it can reach, and what's valuable (secrets, user data, prod systems).
2. **Trace untrusted input to sinks:** SQL/NoSQL queries, shell, filesystem paths, HTML/templates, deserialization, redirects, outbound requests (SSRF).
3. **Check trust boundaries:** authentication, authorization on every sensitive action (not just the UI), session/token handling, CORS, rate limits.
4. **Secrets:** hardcoded keys, secrets in logs/commits/URLs, overly broad tokens. Use a scanner (e.g. gitleaks) if available.
5. **Dependencies / MCPs / third-party skills:** source and maintainer, permissions requested vs. needed, network and filesystem access, install scripts, pinned versions, known advisories (`npm audit`, `pip-audit`, OSV). For agent tools, check for instructions embedded in descriptions or outputs (prompt injection).
6. **Verify each finding** with a concrete exploit scenario; rate by impact × likelihood.

## Failure handling
- Can't confirm exploitability: report as "potential" with what would confirm it.
- Never run exploits against systems you don't own or weren't authorized to test.

## Output
Findings by severity: location · vulnerability · attack scenario · fix. Then residual risks and what wasn't reviewed.
