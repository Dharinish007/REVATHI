---
name: add-mcp
description: Add or update an MCP server / tool entry in the Personal Agent OS registry (mcp/registry.md). Use when I say "add this MCP", "register this tool", "update the MCP registry", or after connecting a new MCP server to any agent tool.
---

# Add MCP to registry

Goal: an accurate, secret-free registry entry that tells any agent what the server does, what it risks, and where it's actually set up.

## Inputs
- The server name, package/URL, or the tool config where I connected it.

## Procedure
1. **Inspect sources:** the server's official docs/repo, and (if present) its entry in the current tool's config. Read the config for command, transport, and env var **names** only.
2. **Capabilities:** list its tools/resources. If connected in this session, use the actual tool list; otherwise take them from docs and note "from docs".
3. **Auth & permissions:** auth method (none / API key / OAuth), env var names, scopes, what it can read/write/execute, network reach.
4. **Risks:** run the `security-review` skill's dependency/MCP checks for third-party servers (publisher, permissions vs. need, pinned version, injection surface).
5. **Compatibility:** mark `✓` only for tools where it's verified configured; `?` if unknown. Don't infer.
6. **Write the entry** using the template at the bottom of `mcp/registry.md`, keep it under ~10 lines, update the compatibility matrix and `Updated` date. For an existing entry, edit in place; don't duplicate.
7. **Tell me what to connect manually** in any other tool I want it in (the command or config location from the registry's table), without writing credentials.

## Never
- Copy tokens, keys, passwords, or full config blobs containing them into this folder. If a config contains a secret, record only the variable name.
- Mark a server as working in a tool you haven't verified.

## Output
Entry added/updated · verified vs. from-docs parts · risks flagged · manual setup steps for other tools.
