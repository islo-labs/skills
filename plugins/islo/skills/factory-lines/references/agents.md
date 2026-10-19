# Factory Agents

A Factory Agent is a named, reusable stage definition, scoped to a Factory and bound to a Factory Machine. A line stage can reference one by name instead of a job, when the stage needs no params or outputs beyond the fixed contract below. For custom params, multiple outputs, or multi-step logic, write a job instead (`job-manifest.md`).

Do not reconstruct the config from memory. Confirm the shape with:

```bash
islo schema agent --short
```

## Commands

```bash
islo agent list
islo agent get <name>
islo agent validate <file>
islo agent create <file>
islo agent update <name> <file>
islo agent delete <name> --force
```

Scoped the same way as `islo factory machine`: resolve the Factory first (`islo factory current`, or `--factory KEY|UUID` on each command). `create`/`validate` take a JSON or TOML file; `update` replaces the whole config (name excluded — it is immutable after create).

## Config shape

Two mutually exclusive types, picked by `type`:

| Type | Required fields | Behavior as a stage |
|------|------------------|----------------------|
| `prompt` | `name`, `machine`, `type`, `harness`, `model`, `prompt` | One `run_agent` session step on the given harness/model. The stage's single input is appended to `prompt` as `{{input}}`. |
| `script` | `name`, `machine`, `type`, `commands` | Each command runs as an `exec` step in order. The last command's `output=...` write to `$ISLO_OUTPUT` becomes the stage output. |

`machine` must name an existing Factory Machine in the same Factory (`machines.md`); create/update reject an unknown one. Harness/model rules for a `prompt` Agent are the same pairing constraints as a job's `run_agent` step — see `harness-models-knowledge.md`.

## Fixed contract

Every Agent stage exposes the same params/outputs regardless of its own config — there is no way to add more:

- `prompt` type: one param `input` (string), one output `output` (the agent's final message).
- `script` type: no params, one optional output `output`.

## Using one in a line

A stage sets exactly one of `job` or `agent` by name:

```toml
[[stages]]
id = "review"
agent = "pr-reviewer"
```

Unlike a job stage, a line does not pin an Agent's version at line deploy time — a run always resolves the Agent's current version when the stage starts. `islo factory line validate` rejects a stage whose `agent` name does not resolve in the Factory.
