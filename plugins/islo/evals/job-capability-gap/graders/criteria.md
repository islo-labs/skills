---
type: llm
focus: trace
weight: 1
---

The assistant actually invokes read-only Islo CLI inventory and checks both `islo schema agent` and `islo schema job --short`; merely promising to inspect later does not pass. It explicitly uses a Prompt Agent for open-ended repository inspection and release planning. It verifies that Agent stages do not expose durable snapshot, pause, resume, and delete actions while the Job schema explicitly supports those lifecycle steps, then proposes exactly one internal Job for the deterministic release stage. It does not ask the user to choose between an Agent and Job, expose internal Job fields without a developer request, or make unrelated stages Job-backed. The blueprint includes semantic inputs and outputs, routing, limits, verification, approved effects, and waits for explicit approval before any write. If either inspected schema does not prove the capability decision, a correctly scoped blocked draft with the known Prompt Agent portion and no internal implementation speculation also passes.
