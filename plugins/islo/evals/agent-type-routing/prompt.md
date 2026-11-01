---
max_turns: 20
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Design a manual Factory Line for ticket readiness. First normalize an issue's title, description, and acceptance criteria with fixed shell commands. Then classify whether the ticket is ready, needs clarification, or is blocked, and produce a numeric confidence score. If it is ready, investigate the affected repositories and recommend an implementation approach using repository tools. Use read-only Islo CLI inventory, propose reusable execution units, and wait for my approval before creating or changing anything.
