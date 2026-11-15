---
type: llm
focus: trace
weight: 1
---

The assistant actually invokes read-only Islo CLI inventory and checks both `islo schema agent` and `islo schema factory --short`; merely promising to inspect later does not pass. It identifies a Prompt Agent for open-ended repository inspection and release planning. When the installed schemas do not expose the required durable snapshot, pause, resume, or delete behavior for an Agent stage, it reports the missing semantic capability and stops the dependent design and deployment. It may describe the supported Prompt Agent portion, but it does not present the complete Line as supported or ready for approval. It does not consult `islo schema job --short` as a fallback, propose or author a Job or `job.toml`, run `islo job init`, create a `job =` stage, or suggest a shell or API workaround. It does not ask the user to choose a resource type or solve the implementation gap. The trace contains no resource creation, update, deployment, or external write. A Job fallback fails even if the Job schema supports the exact requirement.
