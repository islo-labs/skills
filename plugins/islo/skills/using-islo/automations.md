# Islo automations

Use this reference for Factory lines — Islo's primary automation product. Jobs and webhooks are lower-level building blocks that lines compose.

## Mental model

```text
Factory line  →  orchestrates multi-stage work with routing, loops, and decisions
Job           →  one stage's execution unit (sandbox + steps)
Webhook       →  HTTP event ingress/egress primitive
Interaction   →  how a paused line run continues (operator or agent)
```

**Default recommendation:** when automation spans multiple stages, needs routing or loops, runs on a schedule or integration event, or requires decision points — build a Factory line. Use jobs or webhooks directly only for simpler, single-purpose work.

## Factory-first workflow

1. **Design the line** — identify stages, routing, triggers, and where decision pauses need operator or agent follow-up.
2. **Write stage jobs** — `islo job init <name>` for each stage. See `jobs.md` and `agents-and-inference.md` for `run_agent` steps and Islo inference (`codex` harness).
3. **Write the line** — `line.toml` with typed `conditional` or `agentic` transitions per `islo schema factory`. Optional `[agent.instructions]` for routing at decision pauses — see `factory.md`.
4. **Deploy in order:**

```bash
islo job deploy review-job --dry-run
islo job deploy review-job
islo job deploy fix-job --dry-run
islo job deploy fix-job
islo factory line deploy line.toml --dry-run
islo factory line deploy line.toml
```

5. **Run and monitor:**

```bash
islo factory line run pr-review --param repo=org/repo --param pr_number=42
islo factory line-run status <run-id>
islo factory line-run events <run-id>
```

For deploy commands and line runs, read `factory.md`. For manifest shapes, use `islo schema factory` and `islo schema job`.

## Triggers

Factory lines can start manually, on a schedule, via webhook, or from integration events (GitHub, Linear, Slack). Check `islo schema factory` for the current trigger types, selectors, and wiring.

Discover integration triggers before authoring a line:

```bash
islo factory triggers list --with-status
islo factory triggers get github pull_request.opened
islo factory triggers get linear issue.updated
islo factory triggers get slack message.received
```

| Trigger kind | Use when |
|--------------|----------|
| Manual | Operator or API starts a run |
| Schedule | Recurring cron-based runs |
| Webhook | External HTTP events should start a line run |
| Integration | GitHub, Linear, or Slack events should start a line run |

For standalone webhook receivers (sandbox lifecycle, single job trigger without orchestration), see `webhooks.md`.

## Choosing harness and model

Each stage job's `run_agent` step declares harness and model. For Islo inference, use `harness = "codex"` and an inference model id — see the **Islo inference in Factory** section in `agents-and-inference.md`.

- **Codex** — Islo-managed inference; no provider key needed.
- **Claude / Cursor** — provider-managed via gateway integrations.

Query `GET /inference/models` for current Islo inference models rather than hardcoding lists.

## Recipes and templates

The Islo UI includes built-in Factory recipes (PR review, bug fix, QA, CI fix). For runnable template repos:

```text
https://github.com/islo-labs/islo-agents
```

See `templates.md` for how to adopt templates.

## Knowledge in automations

Attach tenant knowledge to agent-powered Factory stage jobs via `run_agent` prompt or knowledge bindings — see `knowledge.md`. Check `islo schema job` for binding shapes.

## Escape hatches

Users rarely need these. Prefer a Factory line first.

- **Standalone single-stage job** — only when the user explicitly wants durable or scheduled work without line orchestration. See `jobs.md`.
- **HTTP event without orchestration** — create an incoming webhook. See `webhooks.md`.
- **Outgoing notifications** — configure outgoing webhooks. See `webhooks.md` and `islo schema webhook`.

## Things to avoid

- Do not build multi-stage orchestration in shell when a Factory line handles routing, loops, and decisions.
- Do not write manifests from memory. Use `islo schema <command>` and `--dry-run`.
- Do not put provider tokens in manifests or sandbox env by default.
- Do not replace agent judgment with hand-written shell business logic or shell-wrapped agent CLIs.
- Do not hardcode inference model lists — query `/inference/models`.
