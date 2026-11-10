# Agents and Managers

An Agent is reusable across Lines and uses one Machine. [agent-manifest.md](agent-manifest.md) describes the type-specific configuration. Inspect existing Agents before creating another one.

## Ownership

The Machine owns the filesystem, repositories, environment, capabilities, gateway profile, and lifecycle. The Agent owns its prompt or deterministic execution, harness, model, provider, effort, Skills, and MCP configuration where its type supports them. The Line owns stage params and outputs, routing, triggers, limits, and optional stage overrides.

A Prompt Agent's prompt states what it owns and what it returns. Line inputs supply task-specific context. Attach repository procedures as Skills or keep them in the repository. Choose harness and model together using [harness-models-knowledge.md](harness-models-knowledge.md).

List remote MCP servers in the blueprint. Configure an allow rule and authentication for each required host in the Machine's gateway profile. Connect credentials locally, and verify connectivity with an approved read-only request. Local CLI status checks provider connections; sandbox-side reads may not show every connection.

## Managers

The built-in Manager is the default for Line routing. Only a Prompt Agent can be a custom Manager. Use one when reusable routing behavior or a chosen harness and model is needed. Its Agent has its own Machine; prepare that Machine first.

The Agent prompt carries reusable policy. A Line-specific `manager.prompt` replaces that prompt for the Line. Do not combine `[manager]` with `[agent.instructions]`, which configures the built-in Manager. Agentic transition instructions describe individual routing decisions. Check `islo schema factory --short` for supported forms.

`islo factory line-run ask` addresses the Manager. `islo factory line-run agent-turn` addresses a stage's successful Agent session. These controls have different recipients.

## Shared workspaces

Agent stages in one Line run with the same `sandbox_name` share a Machine-backed filesystem and keep separate sessions. Every Agent in the group must resolve to the same Machine, including any stage Machine override. Distinct names create workspace boundaries. Separate sessions do not inherit one another's conversation; pass semantic outputs explicitly between stages.
