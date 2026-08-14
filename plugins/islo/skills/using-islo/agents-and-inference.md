# Agents, harnesses, models, and inference

Use this reference when choosing a harness, picking a model, or routing inference through Islo.

## Harnesses

Supported harness values:

| Harness | Session mode | Exec mode | Typical inference path |
|---------|--------------|-----------|------------------------|
| `codex` | Yes | Yes | **Islo inference** (platform-managed models) |
| `claude` | Yes | Yes | Provider integration / gateway proxy |
| `cursor` | Yes | Yes | Provider integration / gateway proxy |
| `custom` | No | Yes only | User-defined `command` |

In `job.toml`, agent steps use `run_agent`:

```toml
[[run.tasks.steps]]
name = "review"
type = "run_agent"
mode = "session"
harness = "codex"
model = "kimi-k2.7-code"
prompt = "Review the PR and summarize findings."
```

Session mode requires `prompt` or `prompt_ref` (not both). Exec mode requires `command` instead.

Factory managers also declare harness and model:

```toml
[manager]
name = "my-agent"
harness = "claude"
model = "claude-sonnet-4-6"
```

## Picking a harness

- **Codex + Islo inference** — no provider API key needed. Islo bills inference usage and routes to enabled upstream models. Best default when the user wants Islo-managed models.
- **Claude** — use when the user wants Anthropic models via connected integration. Good for structured outputs and knowledge-aware stages.
- **Cursor** — use when the user wants Cursor agent models (`composer-2.5`, `auto`, etc.) via connected integration.

Interactive sandbox use:

```bash
islo use --agent codex
islo use --agent claude --task "Review this PR"
islo use --agent cursor --task "Add tests for the auth flow"
```

## Model selection

### Job stages

- `model` is optional on `run_agent` session steps; omit to use harness defaults.
- No catalog validation at deploy — any string is accepted.
- Exec mode does not send `model`; the command owns the protocol.

### Managers

- `model` is **required** on `[manager]`.

### Discovering Islo inference models

Do not hardcode model lists from memory. Query the catalog:

```bash
curl -H "Authorization: Bearer $ISLO_API_KEY" https://api.islo.dev/inference/models
```

Or check docs MCP for `GET /inference/models`. Enabled models include ids like `kimi-k2.7-code`, `minimax-m3`, `qwen3.7-plus` (availability varies by tenant).

## Islo inference vs provider-managed

### Islo-owned inference

- Routes: `https://gateway.islo.dev/inference/openai/v1` and `https://gateway.islo.dev/inference/anthropic`
- Platform-owned upstream credentials; tenant billed via credits.
- Codex in sandboxes uses `model_provider=islo` (CLI) or `model_provider=islo_inference` (UI/onboarding) — both target Islo-managed inference.
- Direct SDK usage:

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
- Used by Claude/Cursor/Codex CLIs calling provider APIs from sandboxes.
- Connect integrations: `islo login --tool github`, `islo login --tool slack`, etc.
- Real tokens stay in the control plane; sandboxes get phantom placeholders.

Do not mix these paths. Inference URLs are for direct model calls; gateway proxy is for provider SDK/CLI egress.

## Knowledge in agent steps

Session-mode `run_agent` steps on `claude` or `codex` can reference tenant knowledge:

```toml
[[run.tasks.steps]]
type = "run_agent"
mode = "session"
harness = "claude"
prompt_ref = "my-review-rules"
knowledge = ["auth-rules", "pr-policy"]
```

Manage knowledge with `islo knowledge` — see `knowledge.md`.

## Structured outputs

`[outputs]` in `job.toml` require exactly one session-mode `run_agent` step with harness `claude` or `codex`. See `jobs.md` for the full job manifest reference.

## Agent entrypoints in jobs

Shell is a launcher; the agent does the work:

```bash
# Claude
claude -p "<prompt>"

# Cursor
agent --yolo --trust -p "<prompt>"

# Codex (Islo inference)
codex --sandbox danger-full-access -c model_provider=islo exec --skip-git-repo-check "<prompt>"
```

For Factory lines, put `run_agent` steps in the stage job manifest rather than raw shell entrypoints when possible — the control plane passes harness, model, and prompt to compute directly.
