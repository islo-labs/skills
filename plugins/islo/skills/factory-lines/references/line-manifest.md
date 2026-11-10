# Line manifests

A Line defines its trigger, Agent-backed stages, contracts, routing, limits, and optional Manager. Confirm every key with the installed schema:

```bash
islo schema factory --short
islo factory line validate line.toml
islo factory line deploy line.toml
```

Create or update the referenced Agents first. Full runnable Agent and Line manifests live in [the validated PR-review example in islo-labs/islo-agents](https://github.com/islo-labs/islo-agents/tree/59ec4503b68212e047af0b0d42645c4c55e0505b/examples/pr-review), which owns manifest validation.

## Agent stages and contracts

A stage references a reusable Agent by name. This fragment describes one stage only:

```toml
[[stages]]
id = "review"
agent = "reviewer"
sandbox_name = "review-{{line_run_id}}"
```

Declare stage `params` and `outputs` in the Line using the type-specific contract in the Factory schema. Transitions bind input values, literals, previous outputs, or failure reasons to target params. For example, this field belongs to a transition and passes a prior stage output:

```toml
params = { input = { type = "output", stage = "prepare", name = "output" } }
```

Prompt Agents own their reusable prompt, harness, model, provider, effort, Skills, MCP, and Machine selection. A Prompt Agent stage can override these settings where the live Factory schema permits it. Some overrides accept one `{{name}}` referring to a declared param. Lists replace the saved list. Saved Agent settings remain unchanged. Invalid resolved settings fail before a sandbox starts. Script and Decision stages use their own contracts; do not assume Prompt overrides apply to them.

`sandbox_name` must contain `{{line_run_id}}`; omitting it uses `<agent-name>-{{line_run_id}}`. Stages with the same name reuse one filesystem, while sessions stay separate.

## Manager configuration

Omit `[manager]` for the built-in Manager. A custom Manager must reference an existing Prompt Agent in this Factory. This fragment configures only the Manager:

```toml
[manager]
agent = "routing-manager"
prompt = "Review stage results and choose the next action."
```

`manager.prompt` is optional and replaces the Agent's reusable prompt for this Line. `[agent.instructions]` applies only to the built-in Manager and cannot be combined with `[manager]`. Agentic transition instructions guide that transition. Use `line-run ask` for the Manager and `line-run agent-turn` for a stage's successful Agent session.

## Routing and runtime constraints

- Declare exactly one conditional entry transition from `trigger` with `when = { op = "always" }`. Completion explicitly targets `done`.
- Use `conditional` transitions for typed conditions and `agentic` transitions for named options chosen by the Manager. Reserved control option names are listed in the live schema.
- When a transition targets `wait`, declare one agentic transition from `wait` to resume. Its options cannot target `wait` again.
- Every stage sharing a `sandbox_name` must resolve to the same Machine, including stage overrides. Validate this before deploy.
- Line schedules live in `[trigger]`; edits outside the manifest are reverted on the next deploy. Machine refresh schedules are separate.
- Follow [create-a-line.md](create-a-line.md) to save Agents before deploying the Line. Trigger selectors, filters, and event verification are in [triggers.md](triggers.md).

## Failed stages and opting out of recovery

A failed stage first takes any conditional transition that matches. If none matches, the run parks for the Line Manager, which follows the `line-manager-recovery` skill. This happens whether or not the stage has an agentic transition. A stage's `max_attempts` defaults to 3 and bounds plain attempts before the Manager diagnoses and recovers.

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
