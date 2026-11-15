# Agents and Managers

An Agent is reusable across Lines. It belongs to one Factory and uses one Machine. Check `islo schema agent` before choosing its type or fields:

| Agent type | Use for | Configuration |
|---|---|---|
| Script | Deterministic shell commands, normalization, or handoff logic | `commands`; writes declared results to `$ISLO_OUTPUT` |
| Decision | Typed classification or scoring | `questions` with `choice`, `score`, or other kinds exposed by the schema; optional System One model |
| Prompt | Open-ended judgment, repository work, or tool use | `harness`, `model`, `prompt`, optional effort, Skills, and MCP servers |

Build new Lines from Agent stages only. If `islo schema agent` and `islo schema factory --short` cannot express a required capability, report the missing capability and stop the dependent design and deployment. Do not author a Job or consult the Job schema for a fallback. Leave existing Job stages in place and add no new ones. Read Job references only when the user explicitly asks to maintain an existing Job or `job.toml`.

## Agent examples

Treat these as shapes and validate them against the installed CLI.

<!-- validate: agent -->
```toml
name = "normalize-ticket"
machine = "ticket-machine"
type = "script"
commands = [
  "jq -c . ticket.json > normalized.json",
  "printf 'output=%s\n' \"$(cat normalized.json)\" >> \"$ISLO_OUTPUT\"",
]
```

<!-- validate: agent -->
```toml
name = "ticket-readiness"
machine = "ticket-machine"
type = "decision"

[questions.readiness]
type = "choice"
instructions = "Classify the ticket readiness."
criteria = { ready = "Implementation can start", clarify = "More detail is needed", blocked = "An external dependency blocks work" }

[questions.confidence]
type = "score"
instructions = "Score confidence in the readiness classification."
criteria = ["The goal is explicit", "Acceptance criteria are testable"]
```

<!-- validate: agent -->
```toml
name = "investigate-ticket"
machine = "ticket-machine"
type = "prompt"
harness = "codex"
model = "openai/gpt-6-sol"
model_provider = "islo_inference"
prompt = "Investigate the ticket in the available repositories and return a recommended implementation approach."
```

The Machine supplies the filesystem, repositories, environment, gateway profile, and lifecycle for every Agent type. Job-only `run_agent` fields and sandbox environment variables do not belong in an Agent configuration.

For a Prompt Agent, recommend a model from the appropriate live catalog, taking capability, cost, and provider connection into account. Do not assume one catalog works for every harness. Its prompt should say what it owns and what it must return, while Line inputs provide task-specific context. Attach repository procedures as Skills or keep them in the repository.

## Pair harnesses and models

The harness determines the protocol, catalog, and host. Confirm the supported `harness`, `model`, and `model_provider` fields with `islo schema agent` before configuring a Prompt Agent or Manager. Use literal harness names supported by that schema.

| Harness | Model selection |
|---|---|
| `codex` | Native OpenAI ids for direct OpenAI routing; compatible ids from `GET /inference/models` with `model_provider = "islo_inference"` |
| `claude` | Anthropic ids for direct routing; catalog ids advertising `anthropic_messages` for Islo inference |
| `cursor` | Discover ids with `agent --list-models` in a sandbox with Cursor auth; the Islo inference catalog does not list Cursor models |
| `opencode` | Bare Islo catalog ids or aliases on the OpenAI-compatible inference endpoint; omit `model_provider` |

Codex uses OpenAI Responses and Claude uses Anthropic Messages. A shared marketing name does not prove protocol compatibility. Do not put Anthropic-only ids on Codex or send Islo catalog ids to direct OpenAI routing. Cursor also omits `model_provider`. For OpenCode, prefer aliases for slash-containing ids so the CLI does not interpret the prefix as a provider name.

Follow the [integrations skill](../../integrations/SKILL.md#check-connection-status) for provider checks and the [chat connection gate](chat-embeds.md#integration-connect-cards) for connect cards and waiting. The platform skill's gateway reference covers inference URLs, gateway proxying, and phantom tokens.

## Use Knowledge for declarative content

Knowledge holds conventions, policies, and house rules. Procedural content, including Skills and playbooks, is rejected at Knowledge deploy. Keep procedures in the Machine's checked-out repository or attach them as Skills. Point a short Agent prompt at the procedure rather than copying it.

Use only Knowledge bindings exposed by the live Agent schema, and deploy referenced Knowledge before dependent resources. A Prompt Agent Manager uses its Agent `prompt`, optionally replaced for one Line by `manager.prompt`. Legacy built-in Manager instructions can bind Knowledge only when `[manager]` is absent. Knowledge CRUD is in the platform skill.

## Validate and connect Agents

For a Decision Agent, use only question kinds and model aliases exposed by the live schema and model catalog. Its Line contract may use a fixed state input and one typed output per question; inspect `islo schema factory --short` before binding them.

For a Script Agent, keep commands deterministic and idempotent where retries are possible. Use only the input/output contract exposed by the live Factory schema.

Validate every complete Agent configuration with `islo agent validate` before saving it.

List every remote MCP server used by a Prompt Agent in the blueprint. An Agent's MCP declaration does not by itself authorize network access: configure the Machine's gateway profile with an allow rule for each required host and an appropriate authentication rule. Connect credentials locally; never paste them into an Agent manifest or prompt. Verify a server's connectivity with an approved, read-only request before the Agent depends on it. A provider connection can still be invisible to sandbox-side reads, so use local CLI status for that check.

The built-in Manager is the default for Line routing. Only a Prompt Agent can be a custom Manager. Use one when reusable routing behavior or a chosen harness/model is needed. Its Agent has its own Machine; prepare that Machine first. The Agent prompt carries reusable policy. A Line-specific `manager.prompt`, where supported by the installed schema, replaces the reusable prompt for that Line. Do not combine a Manager Agent with legacy `[agent.instructions]`; transition instructions describe individual routing decisions. Check `islo schema factory --short` for the currently supported Manager form.

Two Agent stages in one Line run with the same `sandbox_name` share the Machine-backed filesystem, while retaining separate Agent sessions. Every Agent in the group must reference the same Machine. Choose distinct names for isolation. Do not imply that separate Machines can share one stage workspace or that one session's conversation becomes another's context. Pass semantic outputs explicitly between interactions.
