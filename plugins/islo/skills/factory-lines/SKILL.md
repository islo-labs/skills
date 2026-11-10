---
name: factory-lines
description: Design, create, and manage Islo Factories, Machines, reusable Agents, and Lines from an automation goal. Use for Factory setup, Machine setup, line runs, triggers, or low-level manifests when explicitly requested.
---

# Islo Factories

Machines provide the environment. Agents define execution and prompts. Lines orchestrate Agent-backed stages, pass inputs and outputs, and route results. A Factory contains these resources; its Line Managers choose the next action when routing needs judgment.

## Setup contract

For a request to build or substantially change a Factory, follow [factory-design.md](references/factory-design.md) before [create-a-line.md](references/create-a-line.md). Inventory with read-only commands first. Distinguish observed resources, inferred defaults, and decisions still needed from the user. Ask one batch containing only unresolved decisions, then recommend one complete blueprint. Wait for explicit approval of that blueprint before any create, update, deploy, provider event, or external write.

Make Machine ownership and reusable Agents explicit for each stage. Use a Prompt Agent for open-ended judgment or tool use, a Script Agent for deterministic commands, and a Decision Agent for typed questions. Keep reusable execution settings in Agents and stage contracts, routing, and optional overrides in the Line.

Check `islo schema agent --short` and `islo schema factory --short` before authoring manifests. Validate Agent TOML with `islo agent validate`, then create or update the Agents with `islo agent create` or `islo agent update`. Validate and deploy `line.toml` after its Agents exist. If the installed CLI lacks a required command or capability, report the exact gap and stop dependent work rather than guessing field semantics.

## References

| Need | Read |
|---|---|
| Discover resources, design a Factory, get approval | [factory-design.md](references/factory-design.md) |
| Create resources and verify a Line | [create-a-line.md](references/create-a-line.md) |
| Machine lifecycle and readiness | [machines.md](references/machines.md) |
| Author Agent TOML, including Prompt, Script, and Decision types | [agent-manifest.md](references/agent-manifest.md) |
| Agent reuse, Managers, and shared workspaces | [agents-and-managers.md](references/agents-and-managers.md) |
| Harness, model, provider, Skills, MCP, or Knowledge | [harness-models-knowledge.md](references/harness-models-knowledge.md) |
| Line manifest, triggers, or run debugging | [line-manifest.md](references/line-manifest.md), [triggers.md](references/triggers.md), [run-control-and-debugging.md](references/run-control-and-debugging.md) |
| Explicit request to maintain a Job or an existing `job.toml` | [job-manifest.md](references/job-manifest.md) and [standalone-jobs.md](references/standalone-jobs.md) |

Use the platform skill for sandbox and snapshot lifecycle, environments, gateway profiles, provider connections, incoming webhooks, and Knowledge CRUD. Never copy a nearby example's repository, selector, destination, or gateway identity into a new Factory.

Complete runnable Agent and Line examples and their manifest validation belong to [the validated PR-review example in islo-labs/islo-agents](https://github.com/islo-labs/islo-agents/tree/59ec4503b68212e047af0b0d42645c4c55e0505b/examples/pr-review). References here contain only focused syntax fragments. `scripts/validate_commands.sh` checks documented commands against the installed CLI.
