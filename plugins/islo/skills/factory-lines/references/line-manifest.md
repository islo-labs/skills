# Line manifests

Do not reconstruct `line.toml` from this skill. Confirm every key against the live schema:

```bash
islo schema factory --short
```

Unknown keys 422. Treat every TOML example in this repo as a pattern, not a drop-in.

## Manager Agent example

Prepare the Machine and create this Agent before validating the Line. The Agent prompt is reusable; `manager.prompt` in the Line, when present, replaces it for that Line.

<!-- validate: agent -->
```toml
name = "skill-example-manager"
machine = "reviewer-machine"
type = "prompt"
harness = "codex"
model = "openai/gpt-6-sol"
model_provider = "islo_inference"
prompt = "Review stage results and choose the next action."
```

<!-- validate: manager-line -->
```toml
[line]
name = "review-line"

[manager]
agent = "skill-example-manager"

[trigger]
type = "manual"

[[stages]]
id = "review"
agent = "skill-example-review-stage"

[[transitions]]
id = "start"
type = "conditional"
from = "trigger"
to = "review"
when = { op = "always" }

[[transitions]]
id = "finish"
type = "conditional"
from = "review"
to = "done"
when = { op = "always" }
```

## Script, Decision, and Prompt Agent stages

Create and validate the reusable Agents before validating the Line. This example uses the built-in Manager and passes semantic outputs between Agent stages.

<!-- validate: line -->
```toml
[line]
name = "ticket-readiness"

[trigger]
type = "manual"

[[stages]]
id = "normalize"
agent = "normalize-ticket"
sandbox_name = "ticket-readiness-{{line_run_id}}"

[[stages]]
id = "decide"
agent = "ticket-readiness"
sandbox_name = "ticket-readiness-{{line_run_id}}"

[[stages]]
id = "investigate"
agent = "investigate-ticket"
sandbox_name = "ticket-readiness-{{line_run_id}}"

[[transitions]]
id = "start"
type = "conditional"
from = "trigger"
to = "normalize"
when = { op = "always" }

[[transitions]]
id = "normalize-to-decision"
type = "conditional"
from = "normalize"
to = "decide"
when = { op = "always" }
params = { state = { type = "output", stage = "normalize", name = "output" } }

[[transitions]]
id = "ready-to-investigate"
type = "conditional"
from = "decide"
to = "investigate"
when = { op = "eq", left = { type = "stage", path = "$.outputs.readiness" }, right = { type = "literal", value = "ready" } }
params = { input = { type = "output", stage = "normalize", name = "output" } }

[[transitions]]
id = "not-ready"
type = "conditional"
from = "decide"
to = "done"
when = { op = "ne", left = { type = "stage", path = "$.outputs.readiness" }, right = { type = "literal", value = "ready" } }

[[transitions]]
id = "finish"
type = "conditional"
from = "investigate"
to = "done"
when = { op = "always" }
```

## Run one Agent several times in parallel

Set `fanout` on an Agent stage to run copies of it at the same time. Each copy has its own sandbox and session. `fanout` takes the same bindings as transition params:

- a number, such as `{ type = "literal", value = 3 }`, runs that many copies with the same input;
- a list runs one copy per item, and each copy gets its item as `input`. The list can be a literal, a run input (`{ type = "input", name = "repos" }`), or an earlier stage's output (`{ type = "output", stage = "plan", name = "repos" }`).

When the user's prompt says how many copies or which items, have an earlier stage output the list and fan out over that output.

```toml
[[stages]]
id = "review"
agent = "reviewer"
prompt = "Use the declared stage params and return the declared outputs."
fanout = { type = "output", stage = "plan", name = "repos" }
max_fanout = 20
concurrency = 3
```

`max_fanout` (default 20) fails the stage when there are more copies. `concurrency` (default 3) limits how many run at once. Each output becomes a list in copy order, so the next stage must declare an array input to receive it. If one copy fails, the other copies still finish, and then the stage fails.

## Policy the schema does not state

- Omit `[manager]` for the built-in Manager. Legacy `[agent.instructions]` is valid only without `[manager]`. Agentic transition instructions apply to that transition. Reusable Agent prompts live in the Agent configuration; optional Agent-stage overrides live in the Line.
- A line declares identity, what starts a run, Agent interactions, and routing. Prefer a reusable Script Agent for deterministic commands, a Decision Agent for typed choice or score questions, and a Prompt Agent for open-ended judgment or tool use. Harness and model belong only to Agent types that expose them in `islo schema agent`.
- Agent-stage contracts vary by Agent type and installed CLI version. Use only the `params`, `outputs`, and transition bindings exposed by `islo schema factory --short`. Check `islo schema agent` as well. If these schemas cannot express a required capability, report the missing capability and stop the dependent design and deployment. Do not author a Job or consult the Job schema for a fallback. New Lines use Agent stages only; leave existing Job stages in place and add no new ones.
- Agent stages with the same `sandbox_name` share one Machine-backed filesystem for that Line run, but keep separate sessions. Every Agent sharing that sandbox must use the same Machine; validate this before deploy. Shared sandboxes are for sequential stages: parallel group members must have different names, including when they use the same Agent.
- Line run schedules live in `[trigger]`; a line run schedule created any other way is reverted on the next line deploy. Factory Machine refresh schedules are separate and live in the Machine spec (see `machines.md`).
- Follow the complete dependency and deploy order in [create-a-line.md](create-a-line.md).
- Reserved agentic option names belong to line controls. Do not reuse them as option labels.
- Trigger field shapes and the condition AST are in the schema; wiring (selectors, filters, one-real-event verify) is in `triggers.md`.

## Failed stages and opting out of recovery

A failed single stage first takes any conditional transition that matches. Parallel group failures skip conditional routes, including the fail-fast pattern below, and park for the Manager. If none matches, the run parks for the Line Manager, which follows the `line-manager-recovery` skill. This happens whether or not the stage has an agentic transition. A stage's `max_attempts` (default 3) is how many plain retries the Manager makes before it diagnoses and recovers.

To make a stage fail fast instead, for example a deploy that must not be retried, route its failure to `done`. A failed stage routed to `done` ends the run as failed (`stage_failed`) without a Manager turn:

```toml
[[transitions]]
id = "deploy-crashed"
type = "conditional"
from = "deploy"
to = "done"
when = { op = "eq", left = { type = "stage", path = "$.status" }, right = { type = "literal", value = "failed" } }
```

`$.status == "failed"` matches only when the stage itself failed (agent error, timeout, lost sandbox). A stage that succeeds with an unwanted output, such as `review_result = "needs_changes"`, has `status = "succeeded"` and is routed by its output conditions.

## Parallel groups and joins

Use different stages for different work: `plan -> [backend, ui] -> review`.
Here review can rerun only `ui`, retaining backend's last successful output.
Create the named Agents first; stage params and outputs replace their default contracts.

<!-- validate: line -->
```toml
[line]
name = "parallel-review"

[trigger]
type = "manual"

[[stages]]
id = "plan"
agent = "implementer"
prompt = "Use the declared stage params and return the declared outputs."
params = { input = { type = "string", default = "Plan the work" } }
outputs = { run = { type = "array", items = "string" } }

[[stages]]
id = "backend"
agent = "implementer"
prompt = "Use the declared stage params and return the declared outputs."
sandbox_name = "backend-{{line_run_id}}"
params = { input = { type = "string" } }
outputs = { output = { type = "string" } }

[[stages]]
id = "ui"
agent = "implementer"
prompt = "Use the declared stage params and return the declared outputs."
sandbox_name = "ui-{{line_run_id}}"
params = { input = { type = "string" } }
outputs = { output = { type = "string" } }

[[stages]]
id = "review"
agent = "reviewer"
prompt = "Use the declared stage params and return the declared outputs."
params = { backend = { type = "string" }, ui = { type = "string" } }
outputs = { needs_changes = { type = "boolean" } }

[[transitions]]
id = "start"
type = "conditional"
from = "trigger"
to = "plan"
when = { op = "always" }

[[transitions]]
id = "implement"
type = "conditional"
from = "plan"
to = ["backend", "ui"]
when = { op = "always" }
params = { input = { type = "literal", value = "Implement the plan" } }
targets.ui.params = { input = { type = "literal", value = "Implement the UI" } }

[[transitions]]
id = "join-review"
type = "conditional"
from = ["backend", "ui"]
to = "review"
when = { op = "always" }
params = { backend = { type = "output", stage = "backend", name = "output", default = "No backend work" }, ui = { type = "output", stage = "ui", name = "output", default = "No UI work" } }

[[transitions]]
id = "revise-ui"
type = "conditional"
from = "review"
to = "ui"
when = { op = "truthy", operand = { type = "stage", path = "$.outputs.needs_changes" } }
params = { input = { type = "literal", value = "Address the UI review" } }

[[transitions]]
id = "finish"
type = "conditional"
from = "review"
to = "done"
when = { op = "falsy", operand = { type = "stage", path = "$.outputs.needs_changes" } }
```

A fixed destination list requires at least two distinct real stage IDs. Reserved
IDs `trigger`, `done`, `wait`, and `fail` cannot be group members. The trigger
transition cannot start a group. `targets.<stage>.params` merges over shared
`params` for that member only.

For an output-selected group, replace the `implement` transition's destination:

```toml
to = { type = "output", stage = "plan", name = "run" }
allowed = ["backend", "ui"]
```

The output must be an array of stage-name strings drawn from the non-empty,
unique `allowed` list. Every allowed entry must name a real stage. A pick of
`["ui"]` runs just UI and retains backend's last successful outputs. An empty or
invalid pick fails with `TRANSITION_PARAMS_INVALID`.

Every group needs a join whose `from` includes all fixed members or all `allowed`
stages. A join condition must name the stage it reads, for example
`{ type = "stage", stage = "ui", path = "$.status" }`. After a group, only joins
covering all members that ran are candidates; an exact match wins, otherwise
multiple candidates fail with `ambiguous_transition`. No matching join parks
with all member results.

An output param binding may set `default`, used when the source has no outputs.
Without a default, the source must be guaranteed to have run on that route.
The defaults above also permit a first visit that selects only UI.

Group members cannot share a sandbox. The default `<agent>-{{line_run_id}}`
collides when the same Agent occupies two members, so use distinct
`sandbox_name` overrides. Each member can use its own manifest `fanout`.

A group failure skips conditional routes, including the fail-fast pattern above,
and parks with `routing_context.stage_results` and `failed_stages`. A join blocks
while any named member's latest result is failed. Retry reruns only failed
members, preserving their own params and successful siblings' newer results.
After a successful single-member steer or retry, an own matching route wins,
otherwise a covering join advances the run. See
[run controls](run-control-and-debugging.md) for recovery and stop semantics.
