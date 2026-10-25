---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Design a Factory that reads changes in github.com/acme/api and github.com/acme/web, has one Agent implement a coordinated fix and a second Agent review it using the same checkout, then opens a PR in each repository after approval. Both Agents must see the same filesystem during one Line run. I want to review the proposed setup before anything is changed.
