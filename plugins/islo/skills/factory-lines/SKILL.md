---
name: factory-lines
description: Design, create, and manage Islo Factories, Machines, reusable Agents, and Lines from an automation goal. Use for "how do I use Islo", "what should I do next", onboarding, verification readiness, testing existing preview environments, Factory setup, Machine setup, line runs, triggers, chat object links, or low-level manifests when explicitly requested.
---

# Islo Factories

A Factory contains Machines, reusable Agents, and Lines. Agents are the execution units for new Lines. A Line connects Agent interactions and routes their results. Managers route a Line between stages.

For getting started or "what now?", read [first-run.md](references/first-run.md). Inspect what exists, name the user's current step, and offer one next step with a link. For verification on an existing preview environment, read [remote-verification.md](references/remote-verification.md). Answer the approach question briefly before offering a Line draft card.

## Log in before Line creation

Before starting a Line creation workflow, verify that the Islo CLI is logged in with this read-only check:

```bash
islo factory list --output json
```

On success, including an empty array, continue without asking the user to log in. Only for missing or invalid authentication, ask the user to run `islo login` in their local terminal outside a sandbox. Wait for confirmation and recheck before inventory, design, or resource creation. Diagnose other failures without requesting login. Provider connections still use the integration cards below.

## Setup contract

For a request to build or substantially change a Factory, follow [factory-design.md](references/factory-design.md) before [create-a-line.md](references/create-a-line.md). Inventory with read-only commands first. Distinguish observed resources, inferred defaults, and decisions still needed from the user. Ask one batch containing only unresolved decisions, then present the blueprint as a [Line draft card](references/chat-embeds.md#line-draft-cards). Wait for the user to write "approve" for that card before any create, update, deploy, provider event, or external write.

Keep the discussion in product terms: Factory, Machines, Agents, their interactions, shared workspaces, semantic inputs and outputs, integrations, side effects, and verification. Choose a Script Agent for deterministic commands, a Decision Agent for typed choice or score questions, and a Prompt Agent for open-ended judgment or tool use. Build new Lines from Agent stages only. Leave existing Job stages in place when changing a Line, and do not add new ones. Load Job references only when the user explicitly asks to maintain an existing Job or `job.toml`.

Never write a manifest from memory. Check the installed `islo schema factory --short` and `islo schema agent`; validate before deploy. If these schemas cannot express a required capability, or the installed CLI lacks a required command, report the missing capability and stop the dependent design and deployment. Do not author a Job, consult the Job schema for a fallback, or propose an implementation workaround. Do not infer support from a similarly named field or ask the user to solve the implementation gap.

## Integration connections

Before creating or deploying resources, check providers with the [integrations skill](../integrations/SKILL.md#check-connection-status). Follow the [chat connection gate](references/chat-embeds.md#integration-connect-cards) for connect cards and waiting.

## Chat links

Always use explicit `/factories/FACTORY_KEY/...` routes for Factory objects. Resolve the object's Factory key with `islo factory current --factory KEY_OR_UUID --output json` and read `factory.key`; use the same selection as the object operation. Never emit legacy singular-Factory run URLs or guess a Factory from the current conversation. If the key cannot be resolved, keep a known explicit link as a badge with `view=chip`, rather than requesting a card. If no explicit URL is known, describe the run in text until its Factory is identified. Follow [chat-embeds.md](references/chat-embeds.md) for views and filters.

## Waiting for line runs you start

Read and follow [Waiting for line runs you start](references/wait-for-line-runs.md) whenever you start a run for a chat request. Wait through Manager recovery, read the final outputs, and continue the original task in the same turn.

## References

When authorized to ask Line-run questions, send choice question objects with 1 to 8 explicit options and prompts of 30 words or fewer. One option is enough because every choice includes Other for a custom answer. Follow [questions.md](references/questions.md) for the request format.

| Need | Read |
|---|---|
| Get started, find the next step, or understand what Machine levels let Lines do | [first-run.md](references/first-run.md) |
| Verify PRs against an existing preview or ephemeral environment | [remote-verification.md](references/remote-verification.md) |
| Discover resources, design a Factory, get approval | [factory-design.md](references/factory-design.md) |
| Create resources and verify a Line | [create-a-line.md](references/create-a-line.md) |
| Machine lifecycle and readiness | [machines.md](references/machines.md) |
| Agent, Manager, harness, model, Skills, or MCP | [agents-and-managers.md](references/agents-and-managers.md) |
| Line manifest, triggers, or run debugging | [line-manifest.md](references/line-manifest.md), [triggers.md](references/triggers.md), [run-control-and-debugging.md](references/run-control-and-debugging.md) |
| Show an outcome card, Line, run, question, Machine, environment, Job, or Knowledge item in Agent chat | [chat-embeds.md](references/chat-embeds.md) |
| Only when explicitly asked to maintain an existing Job or `job.toml` | [harness-models-knowledge.md](references/harness-models-knowledge.md), [job-manifest.md](references/job-manifest.md), and [standalone-jobs.md](references/standalone-jobs.md) |

Use the platform skill for sandbox and snapshot lifecycle, environments, gateway profiles, provider connections, incoming webhooks, and Knowledge CRUD. Treat nearby examples as shape references; never copy their repo, selector, destination, or gateway identity into a new Factory.

`scripts/validate_commands.sh` and `scripts/validate_examples.sh` validate documented commands and manifest examples against the installed CLI.
