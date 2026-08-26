# Harness, model, and knowledge for line stages

Harness and model are declared per stage on the job's `run_agent` step (`job-manifest.md`), never in `line.toml`. Pair them: the harness picks the protocol, the model catalog, and the host. A model id from the wrong catalog is a failed run, not a helpful 422.

Do not write field shapes from memory — confirm `model_provider` and env keys against `islo schema job --short`. Treat the fragments below as pairing patterns, not drop-in jobs.

## Pairing

| Harness | How the model is reached | How to pick `model` | Required extras |
|---------|--------------------------|---------------------|-----------------|
| `codex` | `model_provider` on the step | `GET /inference/models` when using `islo_inference`; native OpenAI ids when using the default | `model_provider = "islo_inference"` for Islo catalog ids |
| `claude` | `[run.sandbox.env] ANTHROPIC_BASE_URL` | Anthropic / `ship-like/…` ids, or catalog ids that advertise `anthropic_messages` | Matching `ANTHROPIC_*` env; omit `model_provider` |
| `cursor` | Cursor cloud via the gateway | `agent --list-models` (Composer, Grok, `auto`, …) — not the Islo catalog | Omit `model_provider`; tenant Cursor key for jobs |
| `custom` | Exec-mode only | n/a | User-defined command |

`GET /inference/models` is **not** a shared list. Cursor ids are not in it. Anthropic / `ship-like/…` ids fail on Codex. Catalog Fireworks ids fail on Codex unless `model_provider = "islo_inference"`.

`harness` must be a literal (`codex`, `claude`, or `cursor`) at deploy. `{{harness}}` 422s. Session outputs require one of those three harnesses.

## Codex

`model_provider` is session-mode Codex only. Values: `islo` or `islo_inference`. Putting it on `claude` or `cursor`, or in exec mode, 422s. Templates for `model_provider` also 422.

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

Omit `model_provider`. Point Claude at Islo inference with sandbox env, and set every Claude model env to the **same** id as `run_agent.model`. Without `ANTHROPIC_BASE_URL`, Claude misses the gateway.

```toml
[run.sandbox.env]
ANTHROPIC_BASE_URL = "https://gateway.islo.dev/inference/anthropic"
ANTHROPIC_MODEL = "<same id as run_agent.model>"
ANTHROPIC_DEFAULT_HAIKU_MODEL = "<same id>"
ANTHROPIC_SMALL_FAST_MODEL = "<same id>"
CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS = "1"

[run.tasks.steps.run_agent]
mode = "session"
harness = "claude"
model = "<ship-like or catalog id with anthropic_messages>"
```

A connected Anthropic account is optional when using Islo inference this way. Claimed session outputs are filled from inline json-schema.

The same catalog id can work on both Codex and Claude only when you pair the protocol: Codex + `islo_inference` (Responses) vs Claude + `ANTHROPIC_BASE_URL` (Messages). Marketing name is not enough.

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

## Knowledge in lines

Knowledge items are for declarative content: conventions, policies, house rules an agent stage should always know.

- Attach to a stage via `run_agent` prompt bindings (`{ type = "knowledge", slug = "..." }`) or the `run_agent.knowledge` array. Shapes per `islo schema job --short`.
- Line routing instructions (`[agent.instructions]` in line.toml) can also bind knowledge.
- Deploy knowledge items before the jobs that reference them (Phase 6 order in `create-a-line.md`).

Procedural content (skills, step-by-step prompts, playbooks) is rejected at knowledge deploy, and copying it would fork it from the repo anyway. Keep it in the repo, check it out with the fetch-or-clone step from `job-manifest.md`, and point a short literal prompt at the file.

Browsing and creating knowledge items (`islo knowledge` CRUD) is in the platform skill.
