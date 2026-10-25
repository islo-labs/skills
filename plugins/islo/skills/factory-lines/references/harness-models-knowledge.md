# Harness, model, and Knowledge for internal Jobs

Internal Job stages declare harness and model on the Job's `run_agent` step (`job-manifest.md`). Pair them: the harness picks the protocol, model catalog, and host. A model id from the wrong catalog is a failed run, not a helpful 422. Configure reusable Agents with `islo schema agent` and [agents-and-managers.md](agents-and-managers.md), not with the Job-only fields below.

Do not write field shapes from memory — confirm `model_provider` and env keys against `islo schema job --short`. Treat the fragments below as pairing patterns, not drop-in jobs.

## Pairing

| Harness | How the model is reached | How to pick `model` | Required extras |
|---------|--------------------------|---------------------|-----------------|
| `codex` | `model_provider` on the step | `GET /inference/models` when using `islo_inference`; native OpenAI ids when using the default | `model_provider = "islo_inference"` for Islo catalog ids |
| `claude` | `model_provider` on the step | Anthropic ids, or catalog ids that advertise `anthropic_messages` | `model_provider = "islo_inference"` for Islo catalog ids |
| `cursor` | Cursor cloud via the gateway | `agent --list-models` (Composer, Grok, `auto`, …) — not the Islo catalog | Omit `model_provider`; tenant Cursor key for jobs |
| `opencode` | Injected `opencode.json` → OpenAI-compatible Islo inference | `GET /inference/models` (bare catalog ids / aliases such as `kimi-k2.7-code`) | Omit `model_provider` |
| `custom` | Exec-mode only | n/a | User-defined command |

`GET /inference/models` is **not** a shared list. Cursor ids are not in it. Anthropic / `ship-like/…` ids fail on Codex. Catalog Fireworks ids fail on Codex unless `model_provider = "islo_inference"`. OpenCode takes those catalog ids on the OpenAI-compatible base (no `model_provider`).

`harness` must be a literal (`codex`, `claude`, `cursor`, or `opencode`) at deploy. `{{harness}}` 422s. Session outputs require one of those four harnesses.

## Codex

`model_provider` is for session-mode Codex or Claude steps. Values: `islo` or `islo_inference`. Putting it on `cursor` or `opencode`, or in exec mode, 422s. Templates for `model_provider` also 422.

- Omit the field or set `islo` (the default) to send Codex to OpenAI (`https://api.openai.com/v1`). Use native OpenAI model ids.
- Set `islo_inference` to send Codex to Islo inference (`https://gateway.islo.dev/inference/openai/v1`). Use ids from `GET /inference/models`. Without this field, those ids fail with `model_not_found` on OpenAI.
- Do not put Anthropic or `ship-like/…` ids on Codex. Codex speaks OpenAI Responses; those ids die on convert-to-anthropic.

```toml
[run.tasks.steps.run_agent]
mode = "session"
harness = "codex"
model = "<id from GET /inference/models>"
model_provider = "islo_inference"
```

Claimed session outputs are filled from a native json_schema file. A model that writes markdown and never calls `task_complete` leaves harvest empty even if the review happened.

## Claude

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

## Cursor

Omit `model_provider`. Discover ids with `agent --list-models` inside a sandbox that already has Cursor auth — not `GET /inference/models`.

```toml
[run.tasks.steps.run_agent]
mode = "session"
harness = "cursor"
model = "<id from agent --list-models>"
```

Job VMs do not receive a personal Cursor key. Interactive `islo use` stamps the user and can inject `islo login --tool cursor`. Job provision is tenant-only: it looks up the tenant Cursor slot (`cursor-org`). `islo status` showing a personal Cursor connection is not enough for jobs. Connect Cursor at tenant/org level before a Cursor stage will auth.

Claimed session outputs are prompt-only. The agent must emit the claimed keys; JSON that appears only in chat while the CLI hangs will not harvest.

The inference URLs, gateway proxy, and phantom tokens are in the platform skill's gateway reference.

## OpenCode

Omit `model_provider`. Sandboxes get a phantom `~/.config/opencode/opencode.json` pointing at `https://gateway.islo.dev/inference/openai/v1` with `{env:ISLO_API_KEY}`. Use a bare Islo catalog id (or alias) as `model`; the adapter prefixes `openai/` for OpenCode's `provider/model` flag. Slash-containing canonical ids such as `ship-like/claude-opus-5` should be passed as their alias (`claude-opus-5`) so OpenCode does not treat the prefix as a provider name.

```toml
[run.tasks.steps.run_agent]
mode = "session"
harness = "opencode"
model = "kimi-k2.7-code"
```

Omit `model` to use the injected default (`kimi-k2.7-code`). Claimed session outputs are prompt-only (two-phase finalization, same as Cursor).

## Knowledge in internal Jobs and built-in Manager instructions

Knowledge items are for declarative content: conventions, policies, house rules an agent stage should always know.

- Attach Knowledge to an internal Job with `run_agent` prompt bindings (`{ type = "knowledge", slug = "..." }`) or `run_agent.knowledge` per `islo schema job --short`.
- Legacy built-in Manager routing instructions (`[agent.instructions]` in line.toml) can bind knowledge only when `[manager]` is absent. A prompt Agent Manager instead uses its Agent `prompt`, optionally replaced for one Line by `manager.prompt`.
- Deploy Knowledge before internal Jobs that reference it.

Procedural content (skills, step-by-step prompts, playbooks) is rejected at knowledge deploy, and copying it would fork it from the repo anyway. Keep it in the repo, check it out with the fetch-or-clone step from `job-manifest.md`, and point a short literal prompt at the file.

Browsing and creating knowledge items (`islo knowledge` CRUD) is in the platform skill.
