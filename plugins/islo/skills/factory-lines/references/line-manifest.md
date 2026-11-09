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

## Policy the schema does not state

- Omit `[manager]` for the built-in Manager. Legacy `[agent.instructions]` is valid only without `[manager]`. Agentic transition instructions apply to that transition. Reusable Agent prompts live in the Agent configuration, optional Agent-stage overrides live in the Line.
- A line declares identity, what starts a run, Agent interactions, and routing. Prefer a reusable Script Agent for deterministic commands, a Decision Agent for typed choice or score questions, and a Prompt Agent for open-ended judgment or tool use. Harness and model belong only to Agent types that expose them in `islo schema agent`.
- Agent-stage contracts vary by Agent type and installed CLI version. Use only the `params`, `outputs`, and transition bindings exposed by `islo schema factory --short`. If a required capability is absent, report the gap and stop dependent deployment.
- Agent stages with the same `sandbox_name` share one Machine-backed filesystem for that Line run, but keep separate sessions. Every Agent in that group must use the same Machine; validate this before deploy.
- Line run schedules live in `[trigger]`; a line run schedule created any other way is reverted on the next line deploy. Factory Machine refresh schedules are separate and live in the Machine spec (see `machines.md`).
- Follow the complete dependency and deploy order in [create-a-line.md](create-a-line.md). Inspect the deployed Line to confirm every stage references the intended Agent.
- Reserved agentic option names belong to line controls. Do not reuse them as option labels.
- Trigger field shapes and the condition AST are in the schema; wiring (selectors, filters, one-real-event verify) is in `triggers.md`.

## Failed stages and opting out of recovery

A failed stage first takes any conditional transition that matches. If none matches, the run parks for the Line Manager, which follows the `line-manager-recovery` skill. This happens whether or not the stage has an agentic transition. A stage's `max_attempts` (default 3) is how many plain retries the Manager makes before it diagnoses and recovers.

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
