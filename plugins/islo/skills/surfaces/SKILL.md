---
name: surfaces
description: Publish knowledge documents, media, live web interfaces, and terminals in Islo line runs. Use to show Markdown or HTML reports, embed knowledge media, show a running service, terminal, TUI, REPL, or logs, or route a Surface request.
---

# Islo run surfaces

Surfaces show knowledge items, live web interfaces, and persistent terminal sessions in the line-run canvas. Read [Surface usage](references/usage.md) for commands, readiness checks, and safety rules. For documents and media, read [Knowledge surfaces](references/knowledge.md) for publishing, Markdown embeds, and self-contained HTML.

Ground rules:

- Use the installed `islo surface --help` output as the source of truth for supported kinds and flags.
- Only a stage agent with the line-run Surface environment invokes `islo surface`.
- A Line Manager routes a Surface request to the stage agent that owns the sandbox.
