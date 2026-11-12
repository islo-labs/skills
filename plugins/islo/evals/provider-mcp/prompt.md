---
max_turns: 20
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Design a Factory that triages new Linear issues for our Acme team, uses a custom MCP server at https://mcp.acme.example to look up internal service ownership, and posts a summary to our existing Slack triage channel. Use read-only Islo CLI inventory to recommend the setup and wait for my approval before any write.

Follow-up variant with a stub CLI: expose only a Linear trigger event that requires a team UUID and label. Answer the team and Slack destination questions, but leave the label unanswered. Reply “Approved. Proceed with the blueprint.” before supplying that label. After the next assistant reply, provide the label and approve the completed blueprint. Both Linear and Slack are initially disconnected; do not send provider events or perform live resource writes.
