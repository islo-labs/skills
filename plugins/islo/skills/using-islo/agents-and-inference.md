# Agents, harnesses, models, and inference

Use this reference when choosing a harness, picking a model, or routing inference through Islo. For manifest field shapes, use `islo schema job` and `islo schema factory` — do not write them from memory.

## How agents run on Islo

Most users automate through **Factory lines** or work interactively in a sandbox. Jobs are usually **stage building blocks inside a line**, not something users author on their own.

| Path | Entry point | When to use |
|------|-------------|-------------|
| Interactive sandbox | `islo use --agent <harness>` | Ad hoc or exploratory agent work |
| Factory line | `line.toml` + stage jobs + optional manager | Default for automation — multi-stage work, schedules, integration triggers, decisions |
| Standalone job | `job.toml` directly | Rare — only when the user explicitly wants a single-stage durable or scheduled run without line orchestration |

Within a Factory line, harness and model are set on **stage jobs** (`run_agent` steps) and on the **manager** (decision pauses). Check `islo schema factory` and `islo schema job` for shapes — do not write manifests from memory.

## Harnesses

| Harness | When to use |
|---------|-------------|
| `codex` | Islo-managed inference; no provider API key needed |
| `claude` | Anthropic models via connected integration; structured outputs and knowledge |
| `cursor` | Cursor agent models via connected integration |
| `custom` | Exec-mode only; user-defined command |

## Factory managers

A **manager** is the decision agent for a Factory line. When a line run hits a decision pause — a loop exhausted, no matching transition, or an operator follow-up — the manager's harness, model, and instructions define how that pause is handled.

Managers are deployed separately (`islo factory manager deploy manager.toml`) and referenced from `line.toml`. They are not the same as stage jobs:

- **Stage jobs** do the work (review, fix, notify).
- **Managers** decide what happens at pause points (retry, branch, escalate, stop).

Check `islo schema factory` and `factory.md` for manager deploy and line wiring.

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
- For **Factory stage jobs and managers**: check `islo schema job` and `islo schema factory` for how `model` is set.

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

Attach tenant knowledge to agent-powered Factory stage jobs instead of embedding long policy text in manifests. Manage items with `islo knowledge` — see `knowledge.md`. Check `islo schema job` for how knowledge links into `run_agent` steps.

## Default pattern

In Factory stage jobs, prefer `run_agent` steps. The control plane passes harness, model, and prompt to compute directly.

Do not shell-wrap `claude`, `agent`, or `codex` CLI entrypoints in job exec steps unless `islo schema job` shows an exec-mode path that requires it. Do not suggest standalone jobs when a Factory line fits.
