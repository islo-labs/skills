---
name: factory-lines
description: Design, create, and manage Islo Factories, Machines, reusable Agents, and Lines from an automation goal. Use for Factory setup, Machine setup, line runs, triggers, or low-level manifests when explicitly requested.
---

# Islo Factories

A Factory contains Machines, reusable Agents, and Lines. Agents are the user-facing execution units. A Line connects Agent interactions and routes their results. The runtime may compile an Agent stage into an internal Job; do not make the user choose or configure a Job. Managers route a Line between stages.

## Setup contract

For a request to build or substantially change a Factory, follow [factory-design.md](references/factory-design.md) before [create-a-line.md](references/create-a-line.md). Inventory with read-only commands first. Distinguish observed resources, inferred defaults, and decisions still needed from the user. Ask one batch containing only unresolved decisions, then recommend one complete blueprint. Wait for explicit approval of that blueprint before any create, update, deploy, provider event, or external write.

Keep the discussion in product terms: Factory, Machines, Agents, their interactions, shared workspaces, semantic inputs and outputs, integrations, side effects, and verification. Use an internal Job only when the runtime needs richer typed contracts, deterministic commands, snapshots, fan-out, verification, or lifecycle control. Explain that implementation detail only when a developer asks for it.

Never write a manifest from memory. Check the installed `islo schema factory --short`, `islo schema agent`, and, for internal Jobs, `islo schema job --short`; validate before deploy. If the installed CLI lacks a required command or Agent-stage field, report the exact gap rather than silently substituting an unrelated resource. Agent stages use the runtime's default `input` and `output` contract; use an internal Job for richer typed contracts until the CLI exposes custom Agent-stage params and outputs.

## References

| Need | Read |
|---|---|
| Discover resources, design a Factory, get approval | [factory-design.md](references/factory-design.md) |
| Create resources and verify a Line | [create-a-line.md](references/create-a-line.md) |
| Machine lifecycle and readiness | [machines.md](references/machines.md) |
| Agent, Manager, harness, model, Skills, or MCP | [agents-and-managers.md](references/agents-and-managers.md) |
| Line manifest, triggers, or run debugging | [line-manifest.md](references/line-manifest.md), [triggers.md](references/triggers.md), [run-control-and-debugging.md](references/run-control-and-debugging.md) |
| Internal Job harness, model, Knowledge, manifest, or explicit standalone Job request | [harness-models-knowledge.md](references/harness-models-knowledge.md), [job-manifest.md](references/job-manifest.md), and [standalone-jobs.md](references/standalone-jobs.md) |

Use the platform skill for sandbox and snapshot lifecycle, environments, gateway profiles, provider connections, incoming webhooks, and Knowledge CRUD. Treat nearby examples as shape references; never copy their repo, selector, destination, or gateway identity into a new Factory.

`scripts/validate_commands.sh` and `scripts/validate_examples.sh` validate documented commands and manifest examples against the installed CLI.
