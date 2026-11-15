---
type: llm
focus: trace
weight: 1
---

The assistant actually invokes read-only Islo CLI inventory, including `islo agent list`, `islo schema agent`, and `islo schema factory --short`; merely promising to inspect later does not pass. Its blueprint uses a Script Agent with commands for deterministic normalization, a Decision Agent with typed choice and score questions for readiness, and a Prompt Agent with a harness, model, and prompt for repository investigation. The Line contains three stages that reference those reusable Agents. It does not author or recommend `job.toml`, `islo job init`, or a `job =` Line stage. It may mention that internal Jobs exist for proven capability gaps, but it does not present Agent versus Job as a user choice. It includes semantic inputs and outputs, a trigger, limits, verification, and approved effects, and waits for explicit blueprint approval before any write.
