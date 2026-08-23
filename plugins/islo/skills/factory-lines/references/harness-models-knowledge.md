# Harness, model, and knowledge for line stages

Harness and model are declared per stage on the job's `run_agent` step (`job-manifest.md`), never in `line.toml`.

## Harnesses

| Harness | Use when |
|---------|----------|
| `codex` | Islo-managed inference and billing; no provider key needed. Best default |
| `claude` | Anthropic models via connected integration |
| `cursor` | Cursor agent models via connected integration |
| `custom` | Exec-mode only; user-defined command |

Session outputs (declared `outputs.*` set by the agent) require `claude`, `codex`, or `cursor`.

## Models

Never write a model id from memory. For Islo inference (`codex` harness), query the live list: `GET /inference/models` on the API, or the docs MCP server. For `claude` and `cursor`, the provider integration governs available models; omit `model` to take the harness default when the user has no preference.

Islo inference routes through platform-owned credentials and bills the tenant credits; provider-managed harnesses call out through the gateway with the customer's connected credentials. The plumbing (inference URLs, gateway proxy, phantom tokens) is in the platform skill's gateway reference.

## Knowledge in lines

Knowledge items are for declarative content: conventions, policies, house rules an agent stage should always know.

- Attach to a stage via `run_agent` prompt bindings (`{ type = "knowledge", slug = "..." }`) or the `run_agent.knowledge` array. Shapes per `islo schema job --short`.
- Line routing instructions (`[agent.instructions]` in line.toml) can also bind knowledge.
- Deploy knowledge items before the jobs that reference them (Phase 6 order in `create-a-line.md`).

Procedural content (skills, step-by-step prompts, playbooks) is rejected at knowledge deploy, and copying it would fork it from the repo anyway. Keep it in the repo and hand it to the agent via `sandbox.sources[]` checkout plus a short literal prompt pointing at the file, per `job-manifest.md`.

Browsing and creating knowledge items (`islo knowledge` CRUD) is in the platform skill.
