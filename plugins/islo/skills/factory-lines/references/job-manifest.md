# Maintain existing Job manifests

This compatibility reference applies to an explicit Job maintenance request or an existing `job.toml`. Do not reconstruct `job.toml` from this skill. Scaffold with `islo job init`, then confirm every key against the live schema:

```bash
islo schema job --short
```

Unknown keys 422. Treat every TOML example in this repo as a pattern, not a drop-in.

## Policy the schema does not state

- Params and outputs are the line's contract. Write them first. Transitions bind params from trigger outputs, literals, and prior stages' outputs.
- A Job owns its `run_agent` settings. Session harnesses include `codex`, `claude`, `cursor`, `opencode`, and `grok`. Supported settings may use whole-param templates declared in the Job; check the live schema.
- `model_provider` is session-only. Supported values include `islo`, `islo_inference`, and `subscription`; the harness/provider pairing must be valid. Omit it on Cursor and OpenCode.
- Cursor model ids come from `agent --list-models`, not `GET /inference/models`. Harness and provider pairing details are below.
- `[[run.sandbox.sources]]` is accepted and never checked out. Clone with an idempotent `exec` step instead (see the checkout pattern in the islo-agents examples).
- Reserved agentic option names (`cancel`, `stop`, and the rest listed by `islo schema factory --short`) belong to line controls. Do not reuse them as option labels.
- Write the stage brief in the job. If the user's repo already has skills, check it out and point a short literal at the skill file. Supporting or fan-out briefs may live in the snapshot. Never copy procedural content into Knowledge.

## Harness, model, and Knowledge for Jobs

Existing Job stages declare harness and model on the Job's `run_agent` step. Pair them: the harness picks the protocol, model catalog, and host. A model id from the wrong catalog is a failed run, not a helpful 422. For reusable Agent configuration, see [agent-manifest.md](agent-manifest.md).

Confirm `model_provider` and env keys against `islo schema job --short`. Treat the fragments below as pairing patterns, not drop-in jobs.

### Pairing

| Harness | How the model is reached | How to pick `model` | Required extras |
|---------|--------------------------|---------------------|-----------------|
| `codex` | `model_provider` on the step | `GET /inference/models` when using `islo_inference`; native OpenAI ids when using the default | `model_provider = "islo_inference"` for Islo catalog ids |
| `claude` | `model_provider` on the step | Anthropic ids, or catalog ids that advertise `anthropic_messages` | `model_provider = "islo_inference"` for Islo catalog ids |
| `cursor` | Cursor cloud via the gateway | `agent --list-models`, separate from the Islo catalog | Omit `model_provider`; tenant Cursor key for jobs |
| `opencode` | Injected `opencode.json` with OpenAI-compatible Islo inference | `GET /inference/models` with bare catalog ids or aliases | Omit `model_provider` |
| `grok` | Session provider routing | Models supported by the Grok harness | Check `islo` or `subscription` routing |
| `custom` | Exec-mode only | n/a | User-defined command |

`GET /inference/models` is **not** a shared list. Cursor ids are not in it. Anthropic model ids fail on Codex. Catalog Fireworks ids fail on Codex unless `model_provider = "islo_inference"`. OpenCode takes those catalog ids on the OpenAI-compatible base (no `model_provider`).

The current schema supports fixed settings or one `{{name}}` referencing a declared param for supported settings. Resolved values are checked before a sandbox starts; invalid settings fail with `AGENT_SETTINGS_INVALID`. Session outputs support Codex, Claude, Cursor, OpenCode, and Grok.

### Codex

`model_provider` applies to supported session harnesses. Codex accepts `islo`, `islo_inference`, or `subscription`. Cursor, OpenCode, and exec-mode actions omit it. Subscription routing requires a member deployer of the Job version; confirm execution identity before using it.

- Omit the field or set `islo` (the default) to send Codex to OpenAI (`https://api.openai.com/v1`). Use native OpenAI model ids.
- Set `islo_inference` to send Codex to Islo inference (`https://gateway.islo.dev/inference/openai/v1`). Use catalog ids that support the matching protocol.
- Codex uses OpenAI Responses; choose a model supporting that protocol.

```toml
[run.tasks.steps.run_agent]
mode = "session"
harness = "codex"
model = "<id from GET /inference/models>"
model_provider = "islo_inference"
```

Claimed session outputs are filled from a native json_schema file. A model that writes markdown and never calls `task_complete` leaves harvest empty even if the review happened.

### Claude

Set `model_provider = "islo_inference"` to route Claude through Islo inference, and use a catalog id that advertises `anthropic_messages`. Omit `model_provider` when the session should use direct Anthropic routing.

```toml
[run.tasks.steps.run_agent]
mode = "session"
harness = "claude"
model = "<catalog id with anthropic_messages>"
model_provider = "islo_inference"
```

A connected Anthropic account is optional when using Islo inference. Claimed session outputs are filled from inline json-schema.

The same catalog id can work on both Codex and Claude only when you pair the protocol: Codex uses Responses while Claude uses Messages. Marketing name is not enough.

### Cursor

Omit `model_provider`. Discover ids with `agent --list-models` inside a sandbox that already has Cursor auth. This catalog is separate from `GET /inference/models`.

```toml
[run.tasks.steps.run_agent]
mode = "session"
harness = "cursor"
model = "<id from agent --list-models>"
```

Job VMs do not receive a personal Cursor key. Interactive `islo use` stamps the user and can inject `islo login --tool cursor`. Job provision is tenant-only: it looks up the tenant Cursor slot (`cursor-org`). `islo status` showing a personal Cursor connection is not enough for jobs. Connect Cursor at tenant/org level before a Cursor stage will auth.

Claimed session outputs are prompt-only. The agent must emit the claimed keys; JSON that appears only in chat while the CLI hangs will not harvest.

The inference URLs, gateway proxy, and phantom tokens are in the platform skill's gateway reference.

### OpenCode

Omit `model_provider`. Sandboxes get a phantom `~/.config/opencode/opencode.json` pointing at `https://gateway.islo.dev/inference/openai/v1` with `{env:ISLO_API_KEY}`. Use a bare Islo catalog id (or alias) as `model`; the adapter prefixes `openai/` for OpenCode's `provider/model` flag. Slash-containing canonical ids such as `ship-like/claude-opus-5` should be passed as their alias (`claude-opus-5`) so OpenCode does not treat the prefix as a provider name.

```toml
[run.tasks.steps.run_agent]
mode = "session"
harness = "opencode"
model = "kimi-k2.7-code"
```

Omit `model` only when the injected default suits the workload. Claimed session outputs are prompt-only (two-phase finalization, same as Cursor).

### Knowledge in internal Jobs and built-in Manager instructions

Knowledge items are for declarative content: conventions, policies, house rules an agent stage should always know.

- Attach Knowledge to an internal Job with `run_agent` prompt bindings (`{ type = "knowledge", slug = "..." }`) or `run_agent.knowledge` per `islo schema job --short`.
- Legacy built-in Manager routing instructions (`[agent.instructions]` in line.toml) can bind knowledge only when `[manager]` is absent. A prompt Agent Manager instead uses its Agent `prompt`, optionally replaced for one Line by `manager.prompt`.
- Deploy Knowledge before internal Jobs that reference it.

Procedural content (skills, step-by-step prompts, playbooks) is rejected at knowledge deploy, and copying it would fork it from the repo anyway. Keep it in the repository, check it out with an idempotent fetch-or-clone step, and point a short literal prompt at the file.

Browsing and creating knowledge items (`islo knowledge` CRUD) is in the platform skill.

## Versions and diagnostics

A Job-backed Line stage pins `job_version_id` at Line deployment. After changing a Job, deploy its new version, validate and redeploy the dependent Line, and start a fresh run. Inspect bindings with `islo factory line get <name>`.

```bash
islo job event <command-id>
islo job versions <name>
```

Line-run events identify compute command ids. `islo job event` supplies exit codes, error details, and output tails for those commands. Use sandbox logs when the tails are insufficient.

## Existing snapshot-based execution

For existing snapshot-backed Jobs, keep harness source in the repository, copy it onto a build sandbox, and save a named snapshot. Reference that snapshot with the live Job schema's `snapshot_name`. After changing the harness, rebuild the snapshot and redeploy the dependent Jobs and Line. Do not embed harness code as base64 or bootstrap heredocs in manifests.

Existing Job sandbox modes include `provision` for fresh execution, `ensure` for a stable workspace name, and `reuse` for an existing sandbox. Confirm lifecycle and teardown fields against the live Job schema before changing them.

For an existing incoming webhook that starts a Job, inspect `islo schema webhook` before changing its `trigger-job` action or `--job-name`. Keep that compatibility wiring separate from Line triggers.
