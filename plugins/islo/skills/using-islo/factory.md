# Factory lines

Use this reference for `manager.toml`, `line.toml`, stages, transitions, decisions, triggers, deploy, and line runs.

Factory is Islo's orchestration layer. **Jobs** are stage-level work units. **Lines** wire jobs through stages, transitions, and optional manager decisions. **Managers** define the decision agent for pause points.

## Mental model

```text
manager.toml  →  decision agent identity (harness + model + instructions)
job.toml      →  one stage's work (sandbox + steps, including run_agent)
line.toml     →  orchestration graph (stages, transitions, triggers, limits)
```

Deploy order:

1. Deploy each job referenced by line stages: `islo job deploy <name>`
2. Deploy the manager: `islo factory manager deploy manager.toml`
3. Validate, then deploy the line: `islo factory line deploy line.toml --dry-run` → `islo factory line deploy line.toml`

The first stage's job defines the line's external input contract. Later stages receive params from transition mappings or job defaults.

## Manager manifest (`manager.toml`)

```toml
[manager]
name = "pr-review-agent"
harness = "claude"
model = "claude-sonnet-4-6"

[manager.instructions]
text = """
You help operators decide what to do when a line stage needs human or agent judgment.
"""
```

CLI:

```bash
islo factory manager validate manager.toml
islo factory manager deploy manager.toml
islo factory manager list
islo factory manager get pr-review-agent
```

## Line manifest (`line.toml`)

```toml
[line]
name = "pr-review"
description = "Review a PR, fix if needed, loop until approved"

[manager]
ref = "pr-review-agent"

[trigger]
type = "manual"   # manual | webhook | schedule | integration_trigger

[[stages]]
id = "review"
job = "pr-review-job"

[[stages]]
id = "fix"
job = "pr-fix-job"

[[transitions]]
from = "review"
to = "fix"
when = "result.outputs.passed == false"
label = "needs work"
max_iterations = 3

[transitions.params]
pr_number = { source = "inputs.pr_number" }
summary = { source = "outputs.review.summary" }

[[transitions]]
from = "fix"
to = "review"
when = "always"

[[decisions]]
after_stage = "review"
when = "exhausted(review:fix:result.outputs.passed == false)"
manager = "pr-review-agent"
allowed_actions = ["retry-stage", "stop", "cancel"]

[limits]
max_iterations = 10
timeout = "1h"
```

### Stages

- Each stage runs one job per visit.
- `id` must be unique; use `[a-zA-Z0-9_-]`, 1–63 chars.
- `job` references a deployed job name.
- Optional `job_version_id` pins a specific job version.

### Transitions

- `from` / `to` reference stage ids or `done` (terminal).
- `when` expressions:
  - `""`, `"true"`, `"always"` — always match
  - `result.<path> == <literal>` or `!=`
  - bare `result.<path>` — truthy check
  - job outputs: `result.outputs.<name>`
- `params` wire inputs to the target stage job:
  - `{ source = "inputs.<param>" }` — from line run entry params
  - `{ source = "outputs.<stage_id>.<output>" }` — from a prior stage
  - `{ value = <literal> }` — inline value
- `max_iterations` caps loop trips on that transition.
- Transition id defaults to `{from}:{to}:{when}` if omitted.

### Decisions

- Fire when no transition matches or a loop is exhausted.
- `when = "exhausted(<transition_id>)"` for capped loops.
- `allowed_actions`: `stop`, `complete`, `done`, `cancel`, `retry-stage`, `rerun-from-stage`, `follow-up`.

### Triggers

| Type | Use |
|------|-----|
| `manual` | Operator or API run with entry params |
| `webhook` | `POST /factory/lines/{name}/webhook` |
| `schedule` | Cron; entry job must run with `{}` params (all params need defaults) |
| `integration_trigger` | GitHub, Linear, Slack events with selector + filters |

Schedule example:

```toml
[trigger]
type = "schedule"
cron = "0 9 * * *"
timezone = "UTC"
```

## CLI workflow

```bash
islo factory line validate line.toml
islo factory line deploy line.toml --dry-run
islo factory line deploy line.toml
islo factory line list
islo factory line get pr-review
islo factory line run pr-review --param repo=org/repo --param pr_number=42
islo factory line runs pr-review
islo factory line status <run-id>
```

## Shared sandbox across stages

Use `mode = "ensure"` with a stable sandbox name in each stage job so later stages see earlier work:

```toml
[run.sandbox]
mode = "ensure"
name = "pr-42"
image = "ghcr.io/islo-labs/islo-runner:latest"
gateway_profile = "default"
```

## Common validation failures

- Line `name` must match the deploy path name.
- `manager.ref` must reference a deployed manager.
- Each stage `job` must exist.
- Transition `when` referencing `result.outputs.X` requires the source job to declare output `X`.
- Transition `params` must satisfy the target job's required params.
- Schedule triggers require entry job params to have defaults.

## When to use jobs or webhooks directly

- **Single-stage, no routing** — a job alone is enough. See `jobs.md`.
- **HTTP ingress without orchestration** — an incoming webhook alone may be enough. See `webhooks.md`.
- **Multi-stage, loops, decisions, or integration triggers** — use a Factory line.

For harness and model selection in job stages and managers, see `agents-and-inference.md`.
