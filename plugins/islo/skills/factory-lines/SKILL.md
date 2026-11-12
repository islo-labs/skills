---
name: factory-lines
description: Design, create, and manage Islo Factories, Machines, reusable Agents, and Lines from an automation goal. Use for Factory setup, Machine setup, line runs, triggers, chat object links, or low-level manifests when explicitly requested.
---

# Islo Factories

A Factory contains Machines, reusable Agents, and Lines. Agents are the user-facing execution units. A Line connects Agent interactions and routes their results. The runtime may compile an Agent stage into an internal Job; do not make the user choose or configure a Job. Managers route a Line between stages.

## Log in before Line creation

Before starting a Line creation workflow, verify that the Islo CLI is logged in with this read-only check:

```bash
islo factory list --output json
```

On success, including an empty array, continue without asking the user to log in. Only for missing or invalid authentication, ask the user to run `islo login` in their local terminal outside a sandbox. Wait for confirmation and recheck before inventory, design, or resource creation. Diagnose other failures without requesting login. Provider connections still use the integration cards below.

## Setup contract

For a request to build or substantially change a Factory, follow [factory-design.md](references/factory-design.md) before [create-a-line.md](references/create-a-line.md). Inventory with read-only commands first. Distinguish observed resources, inferred defaults, and decisions still needed from the user. Ask one batch containing only unresolved decisions, then present the blueprint as a [Line draft card](references/chat-embeds.md#line-draft-cards). Wait for the user to write "approve" for that card before any create, update, deploy, provider event, or external write.

Keep the discussion in product terms: Factory, Machines, Agents, their interactions, shared workspaces, semantic inputs and outputs, integrations, side effects, and verification. Choose a Script Agent for deterministic commands, a Decision Agent for typed choice or score questions, and a Prompt Agent for open-ended judgment or tool use. Create a user-facing or standalone Job only when the user explicitly requests the low-level Job layer.

Never write a manifest from memory. Check the installed `islo schema factory --short` and `islo schema agent`; validate before deploy. If the installed CLI lacks a required command or Agent-stage field, report the exact gap rather than silently substituting an unrelated resource. Use an internal Job only when a required capability is demonstrably unavailable to Agent stages and `islo schema job --short` unambiguously supports the exact requirement. If either side is unclear, report only the unresolved semantic capability and stop; do not name internal fields, propose implementation workarounds, ask the user to resolve the implementation gap, or infer support from a similarly named field. Keep an internal Job out of the user's choices and its configuration out of the blueprint unless a developer asks.

## Integration connections

Follow the [integration connection gate](references/chat-embeds.md#integration-connect-cards) before creating or deploying resources.

## Chat links

Always use explicit `/factories/FACTORY_KEY/...` routes for Factory objects. Resolve the object's Factory key with `islo factory current --factory KEY_OR_UUID --output json` and read `factory.key`; use the same selection as the object operation. Never emit legacy singular-Factory run URLs or guess a Factory from the current conversation. If the key cannot be resolved, keep a known explicit link as a badge with `view=chip`, rather than requesting a card. If no explicit URL is known, describe the run in text until its Factory is identified. Follow [chat-embeds.md](references/chat-embeds.md) for views and filters.

## References

When authorized to ask Line-run questions, send choice question objects with prompts of 30 words or fewer. Every choice includes Other for a custom answer. Follow [questions.md](references/questions.md) for the request format.

| Need | Read |
|---|---|
| Discover resources, design a Factory, get approval | [factory-design.md](references/factory-design.md) |
| Create resources and verify a Line | [create-a-line.md](references/create-a-line.md) |
| Machine lifecycle and readiness | [machines.md](references/machines.md) |
| Agent, Manager, harness, model, Skills, or MCP | [agents-and-managers.md](references/agents-and-managers.md) |
| Line manifest, triggers, or run debugging | [line-manifest.md](references/line-manifest.md), [triggers.md](references/triggers.md), [run-control-and-debugging.md](references/run-control-and-debugging.md) |
| Show an outcome card, Line, run, question, Machine, environment, Job, or Knowledge item in Agent chat | [chat-embeds.md](references/chat-embeds.md) |
| Internal Job harness, model, Knowledge, manifest, or explicit standalone Job request | [harness-models-knowledge.md](references/harness-models-knowledge.md), [job-manifest.md](references/job-manifest.md), and [standalone-jobs.md](references/standalone-jobs.md) |

Use the platform skill for sandbox and snapshot lifecycle, environments, gateway profiles, provider connections, incoming webhooks, and Knowledge CRUD. Treat nearby examples as shape references; never copy their repo, selector, destination, or gateway identity into a new Factory.

`scripts/validate_commands.sh` and `scripts/validate_examples.sh` validate documented commands and manifest examples against the installed CLI.
