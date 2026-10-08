---
name: surfaces
description: Publish live web and terminal interfaces from Islo line-run stage sandboxes. Use when an agent should show a running service, terminal, TUI, REPL, or logs in a line run, or when routing a Surface request.
---

# Islo run surfaces

Surfaces show live web interfaces and persistent terminal sessions in the line-run canvas. Read [Surface usage](references/usage.md) for commands, readiness checks, and safety rules.

Ground rules:

- Use the installed `islo surface --help` output as the source of truth for supported kinds and flags.
- Only a stage agent with the line-run Surface environment invokes `islo surface`.
- A Line Manager routes a Surface request to the stage agent that owns the sandbox.
