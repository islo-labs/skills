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
name = "reviewer"
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
agent = "reviewer"

[trigger]
type = "manual"

[[stages]]
id = "review"
job = "review-job"

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

## Policy the schema does not state

- Omit `[manager]` for the built-in Manager. Legacy `[agent.instructions]` is valid only without `[manager]`. Agentic transition instructions apply to that transition, while stage prompts live in each job.
- A line declares identity, what starts a run, the stages, and the routing between them. Harness, model, params, and outputs live on each stage's job.
- Line run schedules live in `[trigger]`; a line run schedule created any other way is reverted on the next line deploy. Factory Machine refresh schedules are separate and live in the Machine spec (see `machines.md`).
- Follow the complete dependency and deploy order in [create-a-line.md Phase 6](create-a-line.md#phase-6-deploy-in-canonical-order). The line pins `job_version_id` at deploy time.
- Reserved agentic option names belong to line controls. Do not reuse them as option labels.
- Trigger field shapes and the condition AST are in the schema; wiring (selectors, filters, one-real-event verify) is in `triggers.md`.
