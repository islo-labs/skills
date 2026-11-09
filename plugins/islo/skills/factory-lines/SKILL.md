---
name: factory-lines
description: Design, create, and manage Islo Factories, Machines, reusable Agents, and Lines from an automation goal. Use for Factory setup, Machine setup, line runs, schedules, or triggers.
---

# Islo Factories

A Factory contains Machines, reusable Agents, and Lines. A Line references saved Agents as its stages and routes their semantic inputs and outputs. Managers route a Line between stages.

## Setup contract

For a request to build or substantially change a Factory, follow [factory-design.md](references/factory-design.md) before [create-a-line.md](references/create-a-line.md). Inventory with read-only commands first. Distinguish observed resources, inferred defaults, and decisions still needed from the user. Ask one batch containing only unresolved decisions, then recommend one complete blueprint. Wait for explicit approval of that blueprint before any create, update, deploy, provider event, or external write.

Keep the discussion in product terms: Factory, Machines, Agents, their interactions, shared workspaces, semantic inputs and outputs, integrations, side effects, and verification. Choose a Script Agent for deterministic commands, a Decision Agent for typed choice or score questions, and a Prompt Agent for open-ended judgment or tool use.

Never write a manifest from memory. Check the installed `islo schema factory --short` and `islo schema agent`; validate before deploy. Every stage references a reusable Agent by name. If the installed CLI lacks a required command or Agent-stage capability, report the unresolved capability and stop dependent deployment. Keep the approved design in terms of supported product resources.

## References

| Need | Read |
|---|---|
| Discover resources, design a Factory, get approval | [factory-design.md](references/factory-design.md) |
| Create resources and verify a Line | [create-a-line.md](references/create-a-line.md) |
| Machine lifecycle and readiness | [machines.md](references/machines.md) |
| Agent, Manager, harness, model, Skills, or MCP | [agents-and-managers.md](references/agents-and-managers.md) |
| Line manifest, triggers, or run debugging | [line-manifest.md](references/line-manifest.md), [triggers.md](references/triggers.md), [run-control-and-debugging.md](references/run-control-and-debugging.md) |

Use the platform skill for sandbox and snapshot lifecycle, environments, gateway profiles, provider connections, incoming webhooks, and Knowledge CRUD. Treat nearby examples as shape references; never copy their repo, selector, destination, or gateway identity into a new Factory.

`scripts/validate_commands.sh` and `scripts/validate_examples.sh` validate documented commands and manifest examples against the installed CLI.
