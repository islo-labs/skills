---
type: llm
focus: trace
weight: 1
---

The assistant actually invokes read-only Islo CLI inventory including `islo agent list`; merely promising to inspect resources does not pass. The recommendation uses one Machine with both named repositories for the two Agents that share a sandbox_name. It states that those Agent stages share a Machine-backed filesystem for one Line run and have separate sessions. It does not claim that separate Machines share files, and it shows semantic handoff between implementation and review. It records both PRs as approved external effects to request, includes a trigger, limits, outputs, and verification, and waits for explicit blueprint approval before creating or posting anything. It does not ask the user to configure Jobs.
