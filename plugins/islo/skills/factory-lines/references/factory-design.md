# Design a Factory from a goal

Use this workflow for a new Factory or a substantial change to an existing one. The user's outcome and approved effects drive the design; do not ask them to select a Job or understand a Job manifest.

For Line creation, complete [Islo login](../SKILL.md#log-in-before-line-creation) before the read-only inventory below.

## Read-only inventory

Read the request for the goal, done condition, repositories, trigger, result destination, and any approved external side effects. Inspect the selected Factory and tenant before asking anything:

```bash
islo factory current
islo factory list
islo factory machine list
islo agent list
islo factory line list
islo environment list
islo gateway ls
islo factory triggers list
islo schema factory --short
islo schema agent
```

List Agents in the selected Factory and inspect plausible matches with `islo agent get <name>` before proposing a new Agent. Use Factory, Machine, Line, trigger, and model-catalog detail commands only for relevant candidates; check subcommand help on the installed CLI first. `islo factory current` can be inherited from a project or environment and is not proof that the user chose that Factory. Label every item as **observed**, **inferred default**, or **unresolved**. Show Factory scope separately from tenant-scoped environments and gateway profiles; deleting a Factory does not own or delete those tenant resources. Never treat a nearby example or local checkout as authorization to use its repository or selector.

The sandbox cannot read integration connection status. Post a [connect card](chat-embeds.md#integration-connect-cards) for every provider the proposed trigger or tools need. The browser card is the source of truth. Never claim that a provider is connected from sandbox evidence. Ask the user to say when done, or offer to deploy now; deployment does not validate readiness, and the Line starts once connected. A connection is a capability, not authorization to send an event.

## Resolve only real choices

Ask once in a single batch for decisions that inventory and the request cannot resolve. Group related identities: which Factory or new name; repositories; trigger scope (for example GitHub owner/repo, Linear team/project, or Slack channel); where results go; allowed writes and provider events; and any cost or time limit. Ask about a Machine, Agent, model, or Manager only if a material product choice cannot be recommended from observed resources. Offer a concrete default and an override where useful. Never ask whether to use an Agent or Job. Do not ask for credentials in chat; post the provider's connect card when needed. If answers change the design, incorporate them before approval.

## Recommend one complete blueprint

Present one proposed configuration, marking inferred defaults. It must contain:

| Area | What to show |
|---|---|
| Outcome | Goal, done condition, acceptance checks, and allowed external effects |
| Factory | Existing key or proposed new name; what is reused and created |
| Machines | Each Machine's repositories, environment, capabilities, size/lifecycle, gateway profile, build/readiness, and ownership |
| Agents | Each reusable Agent's type and reason: Script for deterministic commands, Decision for typed choice/score questions, or Prompt for open-ended judgment/tool use; include only the type-specific Machine, commands, model, instructions, Skills, and MCP details exposed by the live schema |
| Line | Trigger and selector, each stage id mapped to its named reusable Agent and Agent type, Manager, transition graph, per-stage semantic inputs and outputs, shared-sandbox groups, limits, and result destinations |
| Integrations | Required providers with browser connect cards, gateway host/auth rules, and any tenant-scoped environment/profile changes |
| Verification | Resource checks, one stage in isolation, one end-to-end run, and expected effects checklist |

For Agents with the same `sandbox_name` in one Line run, explain that they share one Machine-backed filesystem but have separate sessions. Every Agent in a shared-sandbox group must use the **same Machine**. Different `sandbox_name` values create workspace boundaries; pass results through Line outputs or an approved external artifact instead of assuming files cross the boundary. Include failure and retry paths in the graph when relevant.

Describe inputs and outputs by meaning, such as “issue URL in” and “PR URL out.” Use the Agent-stage contracts exposed by the live Factory schema. If a required capability is absent, verify that gap against both Agent and Job schemas before proposing an internal Job. Snapshot pinning, fan-out with output reduction, verification, and lifecycle actions are Job candidates only when the Agent schema cannot express them and the Job schema unambiguously supports the exact required behavior. A similarly named field is not proof. If either side is unclear, report only the unresolved semantic capability and stop the dependent design; do not name internal fields, offer implementation workarounds, or ask the user how to solve it. Otherwise record only that the smallest necessary internal Job will implement the capability, never present it as a user choice or expose its fields unless a developer asks; keep every other stage Agent-backed. A standalone or user-facing Job requires an explicit user request. Include a proposed Manager: built-in unless a reusable Prompt Agent is justified.

Ask for explicit approval of this **complete** blueprint before creating or changing any resource, deploying, sending a provider event, or writing to an external destination. Read-only inventory and local draft files are allowed before approval. If a requested effect was not included, obtain approval for the revised blueprint before doing it.
