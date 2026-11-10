---
type: llm
focus: trace
weight: 1
---

The assistant actually invokes read-only Islo CLI inventory and checks `islo schema agent --short` and `islo schema factory --short`. It uses a Prompt Agent for repository inspection and release planning. It checks whether the required deterministic lifecycle behavior is supported by Agent-backed stages. If the schema cannot express it, the assistant reports the specific capability gap and stops dependent design without guessing fields or substituting another resource. The supported blueprint portion identifies Machines, reusable Agents, semantic inputs and outputs, routing, limits, verification, and approved effects. It waits for explicit approval before any write.
