# Agents, harnesses, models, and inference

Use this reference when choosing a harness, picking a model, or routing inference through Islo. For manifest field shapes, use `islo schema job` and `islo schema factory` — do not write them from memory.

## How agents run on Islo

Most users automate through **Factory lines** or work interactively in a sandbox. Jobs are usually **stage building blocks inside a line**, not something users author on their own.

| Path | Entry point | When to use |
|------|-------------|-------------|
| Interactive sandbox | `islo use --agent <harness>` | Ad hoc or exploratory agent work |
| Factory line | `line.toml` + stage jobs | Default for automation — multi-stage work, schedules, integration triggers, decisions |
| Standalone job | `job.toml` directly | Rare — only when the user explicitly wants a single-stage durable or scheduled run without line orchestration |

Within a Factory line, harness and model are set on **stage jobs** (`run_agent` steps). At decision pauses, use `islo factory line-run` commands or optional per-line routing instructions per `islo schema factory`. Check `islo schema factory` and `islo schema job` — do not write manifests from memory.

## Harnesses

| Harness | When to use |
|---------|-------------|
| `codex` | Islo-managed inference; no provider API key needed |
| `claude` | Anthropic models via connected integration; structured outputs and knowledge |
| `cursor` | Cursor agent models via connected integration |
| `custom` | Exec-mode only; user-defined command |

## Line interaction at decision pauses

A line run can pause when routing is ambiguous, a loop is exhausted, or an operator needs to weigh in. Use `islo factory line-run follow-up` at a pending decision. Use `stop` and then `steer` to redirect active work, `retry` for the latest failed stage, or `agent-turn` to continue a successful stage's agent session. Optional per-line routing instructions are set in `line.toml` per `islo schema factory` — see `factory.md`.

## Picking a harness

- **Codex** — best default when the user wants Islo-managed models and billing through Islo inference.
- **Claude** — use when the user wants Anthropic models via connected integration.
- **Cursor** — use when the user wants Cursor agent models via connected integration.

Interactive sandbox use:

```bash
islo use --agent codex
islo use --agent claude --task "Review this PR"
islo use --agent cursor --task "Add tests for the auth flow"
```

## Model selection

Do not hardcode model lists from memory.

- For **Islo inference models**: query `GET /inference/models` or docs MCP.
- For **Factory stage jobs**: check `islo schema job` for how `harness`, `model`, and prompt bindings are set on `run_agent` steps.

## Islo inference in Factory

Use **`harness = "codex"`** on a stage job's `run_agent` step and set **`model`** to an enabled inference model id. Islo routes and bills the call — no provider API key in the job manifest.

Workflow:

1. `islo job init <name>` for each stage.
2. Edit stage `job.toml` using `islo schema job` — session-mode `run_agent` with `harness = "codex"` and an inference `model`, plus `outputs` if the line routes on structured results.
3. `islo job deploy <name> --dry-run`, then deploy.
4. Write `line.toml` using `islo schema factory` — stages reference deployed jobs by name.
5. `islo factory line deploy line.toml --dry-run`, then deploy.
6. `islo factory line run <name> --param KEY=VALUE`
7. Monitor with `islo factory line-run status <run-id>` and `islo factory line-run events <run-id>`.

Pick the inference `model` from `GET /inference/models` — do not hardcode model lists from memory.

Deploy and validate:

```bash
islo job deploy pr-review --dry-run
islo job deploy pr-review
islo factory line deploy line.toml --dry-run
islo factory line deploy line.toml
islo factory line run pr-review-line --param repo=org/repo --param pr_number=42
```

For multi-stage lines, each stage job can use `codex` + an inference model the same way. Optional per-line routing instructions go in `agent.instructions` per `islo schema factory` — see `factory.md`. At decision pauses, use `islo factory line-run follow-up`; use `stop`, `steer`, and `retry` for execution control.

## Islo inference vs provider-managed

### Islo-owned inference

- Routes: `https://gateway.islo.dev/inference/openai/v1` and `https://gateway.islo.dev/inference/anthropic`
- Platform-owned upstream credentials; tenant billed via credits.
- Codex in sandboxes targets Islo-managed inference by default.

Direct SDK usage:

```python
from islo.custom.auth import SyncTokenProvider
from openai import OpenAI

client = OpenAI(
    api_key=SyncTokenProvider("https://api.islo.dev", os.environ["ISLO_API_KEY"])(),
    base_url="https://gateway.islo.dev/inference/openai/v1",
)
response = client.chat.completions.create(
    model="kimi-k2.7-code",
    messages=[{"role": "user", "content": "Hello"}],
)
```

### Provider-managed (gateway proxy)

- Routes: `/gateway/proxy/{*path}` with customer-connected credentials.
- Used by Claude/Cursor agent CLIs calling provider APIs from sandboxes.
- Connect integrations: `islo login --tool github`, `islo login --tool slack`, etc.
- Real tokens stay in the control plane; sandboxes get phantom placeholders.

Do not mix these paths. Inference URLs are for direct model calls; gateway proxy is for provider SDK/CLI egress. See `gateway-integrations.md`.

## Knowledge in agent steps

Attach tenant knowledge via prompt bindings (`type = "knowledge"`) or `run_agent.knowledge` arrays — see `knowledge.md`. Check `islo schema job` for binding shapes.

## Default pattern

In Factory stage jobs, prefer `run_agent` steps. The control plane passes harness, model, and prompt to compute directly.

Do not shell-wrap `claude`, `agent`, or `codex` CLI entrypoints in job exec steps unless `islo schema job` shows an exec-mode path that requires it. Do not suggest standalone jobs when a Factory line fits.
