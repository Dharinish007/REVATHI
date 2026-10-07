# 🌸 REVATHI

**The trust layer for AI agents.** Make any AI tool safe, honest, remembering and consistent: install once, works everywhere.

> ⚠️ **Status: pre-alpha, design stage.** Nothing below is built yet. This README is a sample and will be rewritten when the first release ships.

## Why
AI agents are smart, but you can't fully trust them yet. They say "done" when it isn't, break things by accident, forget what you told them, and cost more than expected.

## What REVATHI does
| | Feature | What it means for you |
|---|---|---|
| 🛡️ | **Guard** | Dangerous actions (deleting everything, leaking a key) are blocked or need your OK |
| 🧾 | **Proof before "done"** | The agent can't claim success without passing tests |
| 📼 | **Recorder** | A record of everything the agent did |
| ↩️ | **Undo** | Roll back the agent's local changes with one command |
| 🧠 | **Memory** | Remembers you and your projects, only with your approval |
| 🔄 | **Write once, use everywhere** | The same rules and skills in Claude Code, Antigravity, Codex, Cursor and more |
| 💰 | **Cost clarity** | Shows what each correct result costs |
| 💬 | **Plain English** | Every warning makes sense to non-coders |

REVATHI makes agents **trustworthy**, not smarter: the model's intelligence stays the same.

## Quick start (planned)
```bash
pip install revathi
revathi install
revathi doctor
```
Then use your AI tool as usual. REVATHI works in the background.

## Supported tools (planned)
Claude Code · Antigravity · Codex · Cursor · Gemini CLI · OpenCode

## Docs
- 📘 [Developer guide](revathi_dev_guide.md): full plan and architecture
- 🧭 [Decisions](revathi_decisions.md)
- 📝 [Changelog](CHANGELOG.md)

## License
To be decided.
