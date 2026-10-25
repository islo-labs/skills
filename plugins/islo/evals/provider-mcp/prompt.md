---
max_turns: 20
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Design a Factory that triages new Linear issues for our Acme team, uses a custom MCP server at https://mcp.acme.example to look up internal service ownership, and posts a summary to our existing Slack triage channel. Use read-only Islo CLI inventory to recommend the setup and wait for my approval before any write.
