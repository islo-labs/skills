---
max_turns: 20
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

I am a Factory developer reviewing the resource design. Design a manual Factory Line that has an agent inspect a monorepo and recommend a release plan. The next single stage must run the deterministic release build, create a named sandbox snapshot as a durable step, pause and resume that sandbox before its smoke test, and delete it after publishing the result. Use read-only Islo CLI inventory and identify any necessary internal resource type, but do not ask me to choose between resource types or show low-level manifest fields. Wait for my approval before creating or changing anything.
