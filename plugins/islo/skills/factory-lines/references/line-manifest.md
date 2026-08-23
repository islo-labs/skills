# line.toml anatomy

Pattern, not drop-in. Confirm every field against `islo schema factory --short` before deploying. The examples below are validated in CI by `scripts/validate_examples.sh` against the installed CLI.

A line manifest declares four things: the line identity (`[line]`), what starts a run (`[trigger]`), the stages that do the work (`[[stages]]`), and the routing between them (`[[transitions]]`). Harness, model, params, and outputs live in each stage's `job.toml`, not here. See `job-manifest.md`.

## Full example: integration-triggered bug-fix line

Assembled from a production line that reproduces Slack-reported bugs, fixes them, and opens a PR.

<!-- validate: line -->
```toml
[line]
name = "bug-fix"
description = "Slack-reported bug: reproduce, fix, verify, open a PR"
# Optional grouping label shown in the Factory UI.
category = "fix"

[limits]
# Total stage executions across the run, loops included.
max_iterations = 12
# Wall-clock budget for the whole run.
timeout = "6h"

[agent.instructions]
# Optional guidance for the product-managed line routing agent at decision
# pauses. literal or knowledge binding. It does not replace stage job prompts.
type = "literal"
value = "Retry a stage once on transient sandbox failure. Cancel if the report cannot become a failing check."

# Stage ids are line-local names. Reserved ids: trigger, done, wait.
# job references a deployed job by name; the line pins its version at deploy.
[[stages]]
id = "reproduce"
job = "bug-fix-reproduce"
description = "Reproduce the bug and add a failing test"

[[stages]]
id = "implement"
job = "bug-fix-implement"
description = "Fix the bug and commit on the branch"

[[stages]]
id = "review"
job = "bug-fix-review"
description = "Review the fix before verification"

# Integration trigger: a provider-native event starts the run.
# Discover events and connection status: islo factory triggers list --with-status
[trigger]
type = "integration_trigger"
provider = "slack"
name = "message.received"

[trigger.selector]
# Provider-specific resource selector; selector.provider must match trigger.provider.
provider = "slack"
kind = "channel"
scope = "selected"
channels = ["C0000000000"]

# Optional raw-payload filters using the condition AST. Only trigger operands
# are available here. This one drops edited or thread-broadcast messages.
[[trigger.filters]]
op = "missing"
operand = { type = "trigger", path = "$.event.subtype" }

# Trigger outputs become the line's inputs, bound by trigger_path.
# work_key gives every run a stable identity for sandbox naming and dedupe.
[trigger.outputs]
work_key = { type = "trigger_path", path = "trigger.raw.event_id" }
report = { type = "trigger_path", path = "trigger.raw.event.text" }
slack_channel = { type = "trigger_path", path = "trigger.raw.event.channel" }

# Exactly one conditional entry transition from "trigger", with op = "always".
[[transitions]]
id = "trigger-to-reproduce"
from = "trigger"
to = "reproduce"
type = "conditional"

[transitions.when]
op = "always"

# Params map job param names to bindings:
#   { type = "input", name = "..." }              a line input (trigger output)
#   { type = "output", stage = "...", name = "..." } a prior stage's output
#   { type = "literal", value = ... }             a constant
[transitions.params.work_key]
type = "input"
name = "work_key"

[transitions.params.report]
type = "input"
name = "report"

# Conditional routing on a stage output. The when clause is a typed condition
# AST: left/right for binary ops, operand for unary, conditions for all/any.
# Ops: always, eq, ne, contains, not_contains, exists, missing, truthy, falsy,
# all, any, not. When stage is omitted, paths resolve against the from stage.
[[transitions]]
id = "reproduce-to-implement"
from = "reproduce"
to = "implement"
type = "conditional"

[transitions.when]
left = { type = "stage", path = "$.outputs.reproduced" }
op = "eq"
right = { type = "literal", value = true }

[transitions.params.work_key]
type = "input"
name = "work_key"

[transitions.params.report]
type = "input"
name = "report"

# Failure route: end the run instead of pausing when reproduction fails.
[[transitions]]
id = "reproduce-to-done"
from = "reproduce"
to = "done"
type = "conditional"

[transitions.when]
left = { type = "stage", path = "$.outputs.reproduced" }
op = "eq"
right = { type = "literal", value = false }

[[transitions]]
id = "implement-to-review"
from = "implement"
to = "review"
type = "conditional"

[transitions.when]
op = "always"

[transitions.params.work_key]
type = "input"
name = "work_key"

# Back-edge for a review loop. max_iterations caps how many times this edge
# fires; route the exhausted case separately or the run pauses for a decision.
[[transitions]]
id = "review-to-implement"
from = "review"
to = "implement"
type = "conditional"
max_iterations = 3

[transitions.when]
left = { type = "stage", path = "$.outputs.review_result" }
op = "eq"
right = { type = "literal", value = "needs_changes" }

[transitions.params.work_key]
type = "input"
name = "work_key"

[transitions.params.report]
type = "input"
name = "report"

# An output binding hands a prior stage's declared output to the next job.
[transitions.params.feedback]
type = "output"
stage = "review"
name = "feedback"

# Completion must target the reserved done sink explicitly.
# done is never a source; trigger is never a target.
[[transitions]]
id = "review-to-done"
from = "review"
to = "done"
type = "conditional"

[transitions.when]
left = { type = "stage", path = "$.outputs.review_result" }
op = "eq"
right = { type = "literal", value = "approved" }
```

## Schedule-triggered line

A minimal daily line. Cron is validated at deploy; timezone defaults to UTC. The manifest `[trigger]` is the only supported way to schedule a line. Do not create the schedule any other way, or a later deploy reverts it.

<!-- validate: line -->
```toml
[line]
name = "daily-qa"
description = "Daily QA sweep, then Slack notification"

[trigger]
type = "schedule"
cron = "0 7 * * *"
timezone = "UTC"

[[stages]]
id = "qa"
job = "daily-qa-run"
description = "Run the QA agents"

[[stages]]
id = "notify"
job = "daily-qa-notify"
description = "Post validated findings to Slack"

[[transitions]]
id = "trigger-to-qa"
from = "trigger"
to = "qa"
type = "conditional"

[transitions.when]
op = "always"

[[transitions]]
id = "qa-to-notify"
from = "qa"
to = "notify"
type = "conditional"

[transitions.when]
op = "always"

[[transitions]]
id = "notify-to-done"
from = "notify"
to = "done"
type = "conditional"

[transitions.when]
op = "always"
```

## The other trigger shapes

Manual (operator or API starts runs):

```toml
[trigger]
type = "manual"
```

Webhook (an HTTP POST to a line-owned path starts runs; different from the standalone incoming webhooks in the platform skill):

```toml
[trigger]
type = "webhook"
path = "/lines/bug-fix"
```

For selector and filter shapes per provider, run `islo factory triggers get <provider> <name>`, for example `islo factory triggers get github pull_request.opened`. See `triggers.md` for choosing a trigger and wiring integrations.

## Agentic transitions

A transition with `type = "agentic"` lets the product-managed routing agent choose among named options at a decision pause. At most one agentic transition per source; each option names a target stage, `done`, or `wait`. Option names are manifest identifiers, not CLI verbs, and the API reserves `cancel` and `stop` (deploy rejects them with "reserved for line controls"); names like `retry`, `steer`, `follow-up`, `ask`, `agent-turn`, and `cancel-run` are allowed. None of the production lines use agentic transitions today; prefer conditional routing on declared outputs and reserve them for genuinely ambiguous routing.

## Validation

```bash
islo factory line validate line.toml
islo factory line deploy line.toml --dry-run
```

A 422 or "Extra inputs are not permitted" means an unknown key; manifests reject unknown fields. Diff your manifest against `islo schema factory --short` instead of guessing.
