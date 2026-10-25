# Design a Factory from a goal

Use this workflow for a new Factory or a substantial change to an existing one. The user's outcome and approved effects drive the design; do not ask them to select a Job or understand a Job manifest.

## Read-only inventory

Read the request for the goal, done condition, repositories, trigger, result destination, and any approved external side effects. Inspect the selected Factory and tenant before asking anything:

```bash
islo status
islo factory current
islo factory list
islo factory machine list
islo factory line list
islo environment list
islo gateway ls
islo knowledge list
islo factory triggers list --with-status
islo schema factory --short
islo schema agent
```

Use Factory, Machine, Line, Agent, trigger, and model-catalog detail commands only for relevant candidates; check subcommand help on the installed CLI first. `islo factory current` can be inherited from a project or environment and is not proof that the user chose that Factory. Label every item as **observed**, **inferred default**, or **unresolved**. Show Factory scope separately from tenant-scoped environments and gateway profiles; deleting a Factory does not own or delete those tenant resources. Never treat a nearby example or local checkout as authorization to use its repository or selector.

An integration connection check runs through the local CLI (`islo status` and relevant integration commands). Sandbox reads do not yet provide complete connection visibility; do not use a sandbox check to claim a provider is connected. A connection is a capability, not authorization to send an event.

## Resolve only real choices

Ask once in a single batch for decisions that inventory and the request cannot resolve. Group related identities: which Factory or new name; repositories; trigger scope (for example GitHub owner/repo, Linear team/project, or Slack channel); where results go; allowed writes and provider events; and any cost or time limit. Ask about a Machine, Agent, model, or Manager only if a material product choice cannot be recommended from observed resources. Offer a concrete default and an override where useful. Never ask whether to use an Agent or Job. Do not ask for credentials in chat; ask the user to connect the provider locally when needed. If answers change the design, incorporate them before approval.

## Recommend one complete blueprint

Present one proposed configuration, marking inferred defaults. It must contain:

| Area | What to show |
|---|---|
| Outcome | Goal, done condition, acceptance checks, and allowed external effects |
| Factory | Existing key or proposed new name; what is reused and created |
| Machines | Each Machine's repositories, environment, capabilities, size/lifecycle, gateway profile, build/readiness, and ownership |
| Agents | Each reusable Agent's Machine, responsibility, harness/model, instructions, Skills, MCP servers, and relevant Knowledge |
| Line | Trigger and selector, Agent interactions and Manager, transition graph, per-stage semantic inputs and outputs, shared-sandbox groups, limits, and result destinations |
| Integrations | Provider connection status, gateway host/auth rules, and any tenant-scoped environment/profile changes |
| Verification | Resource checks, one stage in isolation, one end-to-end run, and expected effects checklist |

For Agents with the same `sandbox_name` in one Line run, explain that they share one Machine-backed filesystem but have separate sessions. Every Agent in a shared-sandbox group must use the **same Machine**. Different `sandbox_name` values create workspace boundaries; pass results through Line outputs or an approved external artifact instead of assuming files cross the boundary. Include failure and retry paths in the graph when relevant.

Describe inputs and outputs by meaning, such as “issue URL in” and “PR URL out.” The installed schema currently gives Agent stages default `input` and `output`; use an internal Job for richer typed contracts and keep that mechanism out of the user-facing choice. Include a proposed Manager: built-in unless a reusable prompt Agent is justified. State how Agent version selection will be verified against the installed schema, rather than assuming a deployed Line follows future Agent edits.

Ask for explicit approval of this **complete** blueprint before creating or changing any resource, deploying, sending a provider event, or writing to an external destination. Read-only inventory and local draft files are allowed before approval. If a requested effect was not included, obtain approval for the revised blueprint before doing it.
