# Harness, model, and knowledge for line stages

Harness and model are declared per stage on the job's `run_agent` step (`job-manifest.md`), never in `line.toml`.

## Harnesses

| Harness | Use when |
|---------|----------|
| `codex` | Default agent CLI |
| `claude` | Claude Code CLI |
| `cursor` | Cursor CLI |
| `opencode` | OpenCode CLI |
| `custom` | Exec-mode only; user-defined command |

`codex`, `claude`, `cursor`, and `opencode` all support Islo inference via the gateway URL (tenant credits, no provider key required). A connected Anthropic or Cursor account is optional, not a requirement of those harnesses.

Session outputs (declared `outputs.*` set by the agent) require `claude`, `codex`, `cursor`, or `opencode`.

## Models

Never write a model id from memory. Query the live catalog (`GET /inference/models` on the API, or the docs MCP server) — it is the same list for every harness — and pick from that. Omit `model` only when the user has no preference and the harness default is acceptable.

The plumbing (inference URLs, gateway proxy, phantom tokens) is in the platform skill's gateway reference.

## Knowledge in lines

Knowledge items are for declarative content: conventions, policies, house rules an agent stage should always know.

- Attach to a stage via `run_agent` prompt bindings (`{ type = "knowledge", slug = "..." }`) or the `run_agent.knowledge` array. Shapes per `islo schema job --short`.
- Line routing instructions (`[agent.instructions]` in line.toml) can also bind knowledge.
- Deploy knowledge items before the jobs that reference them (Phase 6 order in `create-a-line.md`).

Procedural content (skills, step-by-step prompts, playbooks) is rejected at knowledge deploy, and copying it would fork it from the repo anyway. Keep it in the repo, check it out with the fetch-or-clone step from `job-manifest.md`, and point a short literal prompt at the file.

Browsing and creating knowledge items (`islo knowledge` CRUD) is in the platform skill.
