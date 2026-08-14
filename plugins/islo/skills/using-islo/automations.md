# Islo automations

Use this reference for Factory lines — Islo's primary automation product. Jobs and webhooks are lower-level building blocks that lines compose.

## Mental model

```text
Factory line  →  orchestrates multi-stage work with routing, loops, and decisions
Job           →  one stage's execution unit (sandbox + steps)
Webhook       →  HTTP event ingress/egress primitive
Manager       →  decision agent for line pause points
```

**Default recommendation:** when automation spans multiple stages, needs routing or loops, runs on a schedule or integration event, or requires decision points — build a Factory line. Use jobs or webhooks directly only for simpler, single-purpose work.

## Factory-first workflow

1. **Design the line** — identify stages, routing, triggers, and decision points.
2. **Write stage jobs** — one `job.toml` per stage. See `jobs.md`.
3. **Write the manager** — `manager.toml` with harness, model, and instructions.
4. **Write the line** — `line.toml` wiring stages, transitions, and triggers.
5. **Deploy in order:**

```bash
islo job deploy review-job
islo job deploy fix-job
islo factory manager deploy manager.toml
islo factory line deploy line.toml --dry-run
islo factory line deploy line.toml
```

6. **Run and monitor:**

```bash
islo factory line run pr-review --param repo=org/repo --param pr_number=42
islo factory line status <run-id>
```

For manifest details, transitions, decisions, triggers, and validation rules, read `factory.md`.

## Choosing harness and model

Each stage job's `run_agent` step declares harness and model. Managers declare their own harness and model for decision points.

- **Codex** — Islo-managed inference; no provider key needed. See `agents-and-inference.md`.
- **Claude / Cursor** — provider-managed via gateway integrations.

Pick harness and model before writing job manifests. Query `GET /inference/models` for current Islo inference models rather than hardcoding lists.

## Triggers

Factory lines support four trigger types in `line.toml`:

| Trigger | When to use |
|---------|-------------|
| `manual` | Operator or API invocation |
| `schedule` | Cron-based recurring runs |
| `webhook` | External HTTP events → `POST /factory/lines/{name}/webhook` |
| `integration_trigger` | GitHub, Linear, or Slack events with selector + filters |

For standalone webhook receivers (sandbox lifecycle, job triggers without a line), see `webhooks.md`.

## Recipes and templates

The Islo UI includes built-in Factory recipes (PR review, bug fix, QA, CI fix). For runnable template repos:

```text
https://github.com/islo-labs/islo-agents
```

See `templates.md` for how to adopt templates.

## Knowledge in automations

Attach tenant knowledge to agent-powered job stages:

```toml
[[run.tasks.steps]]
type = "run_agent"
mode = "session"
harness = "claude"
knowledge = ["auth-rules", "pr-policy"]
```

Manage items with `islo knowledge`. See `knowledge.md`.

## Lower-level primitives

When a Factory line is more than you need:

- **Single-stage durable work** — deploy and run a job directly. See `jobs.md`.
- **HTTP event without orchestration** — create an incoming webhook. See `webhooks.md`.
- **Outgoing notifications** — configure outgoing webhooks in job steps or via `islo webhook outgoing`. See `webhooks.md`.

## Things to avoid

- Do not build multi-stage orchestration in shell when a Factory line handles routing, loops, and decisions.
- Do not write manifests from memory. Validate with `--dry-run` before deploy.
- Do not put provider tokens in manifests or sandbox env by default.
- Do not replace agent judgment with hand-written shell business logic.
- Do not hardcode inference model lists — query `/inference/models`.
