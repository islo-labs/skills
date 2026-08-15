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
3. **Write the manager** — `manager.toml` for decision pause points. See `factory.md`.
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

For deploy commands and line runs, read `factory.md`. For manifest shapes, use `islo schema factory` and `islo schema job`.

## Choosing harness and model

Each stage job's agent step declares harness and model. Managers declare their own harness and model for decision points.

- **Codex** — Islo-managed inference; no provider key needed. See `agents-and-inference.md`.
- **Claude / Cursor** — provider-managed via gateway integrations.

Query `GET /inference/models` for current Islo inference models rather than hardcoding lists.

## Recipes and templates

The Islo UI includes built-in Factory recipes (PR review, bug fix, QA, CI fix). For runnable template repos:

```text
https://github.com/islo-labs/islo-agents
```

See `templates.md` for how to adopt templates.

## Knowledge in automations

Attach tenant knowledge to agent-powered job stages instead of embedding long policy text in manifests. Manage items with `islo knowledge` — see `knowledge.md`.

## Lower-level primitives

When a Factory line is more than you need:

- **Single-stage durable work** — deploy and run a job directly. See `jobs.md`.
- **HTTP event without orchestration** — create an incoming webhook. See `webhooks.md`.
- **Outgoing notifications** — configure outgoing webhooks. See `webhooks.md` and `islo schema webhook`.

## Things to avoid

- Do not build multi-stage orchestration in shell when a Factory line handles routing, loops, and decisions.
- Do not write manifests from memory. Use `islo schema <command>` and `--dry-run`.
- Do not put provider tokens in manifests or sandbox env by default.
- Do not replace agent judgment with hand-written shell business logic.
- Do not hardcode inference model lists — query `/inference/models`.
