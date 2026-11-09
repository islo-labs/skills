# Agents and Managers

An Agent is reusable across Lines. It belongs to one Factory and uses one Machine. Check `islo schema agent` before choosing its type or fields:

| Agent type | Use for | Configuration |
|---|---|---|
| Script | Deterministic shell commands, normalization, or handoff logic | `commands`; writes declared results to `$ISLO_OUTPUT` |
| Decision | Typed classification or scoring | `questions` with `choice`, `score`, or other kinds exposed by the schema; optional System One model |
| Prompt | Open-ended judgment, repository work, or tool use | `harness`, `model`, `prompt`, optional effort, Skills, and MCP servers |


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

The Machine supplies the filesystem, repositories, environment, gateway profile, and lifecycle for every Agent type. Configure the reusable Agent with the fields exposed by `islo schema agent`.

For a Prompt Agent, recommend a model from the appropriate live catalog, taking capability, cost, and provider connection into account. Do not assume one catalog works for every harness. Its prompt should say what it owns and what it must return, while Line inputs provide task-specific context. Attach repository procedures as Skills or keep them in the repository.

For a Decision Agent, use only question kinds and model aliases exposed by the live schema and model catalog. Its Line contract may use a fixed state input and one typed output per question; inspect `islo schema factory --short` before binding them.

For a Script Agent, keep commands deterministic and idempotent where retries are possible. Use only the input/output contract exposed by the live Factory schema.

Validate every complete Agent configuration with `islo agent validate` before saving it.

List every remote MCP server used by a Prompt Agent in the blueprint. An Agent's MCP declaration does not by itself authorize network access: configure the Machine's gateway profile with an allow rule for each required host and an appropriate authentication rule. Connect credentials locally; never paste them into an Agent manifest or prompt. Verify a server's connectivity with an approved, read-only request before the Agent depends on it. A provider connection can still be invisible to sandbox-side reads, so use local CLI status for that check.

The built-in Manager is the default for Line routing. Only a Prompt Agent can be a custom Manager. Use one when reusable routing behavior or a chosen harness/model is needed. Its Agent has its own Machine; prepare that Machine first. The Agent prompt carries reusable policy. A Line-specific `manager.prompt`, where supported by the installed schema, replaces the reusable prompt for that Line. Do not combine a Manager Agent with legacy `[agent.instructions]`; transition instructions describe individual routing decisions. Check `islo schema factory --short` for the currently supported Manager form.

Two Agent stages in one Line run with the same `sandbox_name` share the Machine-backed filesystem, while retaining separate Agent sessions. Every Agent in the group must reference the same Machine. Choose distinct names for isolation. Do not imply that separate Machines can share one stage workspace or that one session's conversation becomes another's context. Pass semantic outputs explicitly between interactions.
