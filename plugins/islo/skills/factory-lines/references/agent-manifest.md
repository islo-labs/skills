# Agent manifests

An Agent belongs to one Factory and names an existing Machine. The Machine supplies repositories, environment, gateway profile, capabilities, and lifecycle. The Agent owns execution settings and its reusable prompt, commands, or questions.

The installed schema is authoritative:

```bash
islo schema agent --short
islo agent list
islo agent get <name>
islo agent validate agent.toml
islo agent create agent.toml
islo agent update <name> agent-update.toml
```

Create manifests require `name`, `machine`, and `type`, plus the type-specific fields below. Names are immutable. Update files omit `name`; omitted fields keep their values, while lists replace the entire list. TOML cannot express null. Use JSON to clear nullable fields as described by `agent_update_config` in the live schema. Validate the complete create configuration before saving it, and check update semantics before applying a partial update.

## Prompt Agents

Prompt Agents are the default for repository work, open-ended judgment, and tool use. They require `harness`, `model`, and `prompt`. Optional fields include `model_provider`, `effort`, `skills`, and `mcp`.

The prompt defines the Agent's responsibility, allowed effects, and expected result. The default Prompt Agent contract appends its `input` param to the prompt. If a Line stage declares custom named params instead, reference them explicitly as `{{name}}` in the Agent prompt or stage prompt override. Declaring a param alone does not include its value in the Agent context. A reusable prompt belongs in the Agent; a Line may replace it for one stage with a supported override.

Skills are unique installation sources passed to `npx skills add`, with at most 20 entries. MCP entries have unique keys and HTTP(S) URLs. This fragment illustrates only an MCP field:

```toml
[[mcp]]
key = "team-tools"
url = "https://mcp.example.com/tools"
```

Each MCP host also needs a gateway allow rule and appropriate authentication in the Agent's Machine gateway profile. A declaration alone does not grant connectivity. Provider, model, and harness pairing is in [harness-models-knowledge.md](harness-models-knowledge.md).

## Script Agents

Script Agents require a nonempty `commands` array. They use the named Machine without prompt harness or model fields. Keep commands deterministic and safe to repeat when a stage retries. Declare their input and output contract in the Line using the live Factory schema. Commands publish declared results through `$ISLO_OUTPUT`.

## Decision Agents

Decision Agents require a nonempty `questions` map. Question names use lowercase letters, digits, and underscores, starting with a letter. The live schema exposes these question types:

| Type | Required fields |
|---|---|
| `choice` | `instructions` and a nonempty `criteria` map from choice names to criteria |
| `score` | `instructions` and a nonempty `criteria` array |
| `noul` | `instructions` |

A question fragment illustrates a typed choice:

```toml
[questions.readiness]
type = "choice"
instructions = "Classify the ticket readiness."
criteria = { ready = "Implementation can start", clarify = "More detail is needed" }
```

The optional `model` must support `typesafe_system_one` in the live model catalog. Omitting it uses the catalog default. Decision Agents do not take prompt harness, provider, Skills, or MCP fields. Inspect the Factory schema for the stage's state input and typed outputs before binding questions to transitions.

For complete runnable manifests, use [the validated PR-review example in islo-labs/islo-agents](https://github.com/islo-labs/islo-agents/tree/70d2597b031483a39bf7bcdf35b427359f1901fd/examples/pr-review), which owns their validation.
