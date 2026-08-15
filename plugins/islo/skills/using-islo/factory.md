# Factory lines

Use this reference for Factory lines — Islo's primary automation product. Jobs and webhooks are lower-level building blocks that lines compose. For manifest field shapes, use `islo schema factory` and validate with `--dry-run` — do not write manifests from memory.

## Mental model

```text
Factory line  →  orchestrates multi-stage work with routing, loops, and decisions
Job           →  one stage's execution unit (sandbox + steps); deploy job.toml separately
Webhook       →  HTTP event ingress/egress primitive
line.toml     →  orchestration graph (stages, transitions, triggers)
```

**Default recommendation:** when automation spans multiple stages, needs routing or loops, runs on a schedule or integration event, or requires decision points — build a Factory line. Use jobs or webhooks directly only for simpler, single-purpose work.

When a run pauses for a decision, the operator or line routing agent continues it — retry a stage, send another agent turn, or cancel.

## Workflow

1. **Design the line** — identify stages, routing, triggers, and where decision pauses need operator or agent follow-up.
2. **Write stage jobs** — `islo job init <name>` for each stage. See `jobs.md` and `agents-and-inference.md` for `run_agent` steps and Islo inference (`codex` harness).
3. **Write the line** — `line.toml` with typed `conditional` or `agentic` transitions per `islo schema factory`. Optional `agent.instructions` for routing at decision pauses.
4. **Deploy in order:**

```bash
islo job deploy review-job --dry-run
islo job deploy review-job
islo factory line deploy line.toml --dry-run
islo factory line deploy line.toml
```

5. If the tenant Factory Manager runtime is disabled, enable it before lines that need routing decisions:

```bash
islo factory manager status
islo factory manager enable
```

6. **Run and monitor:**

```bash
islo factory line run pr-review --param repo=org/repo --param pr_number=42
islo factory line-run status <run-id>
islo factory line-run events <run-id>
```

The first stage's job defines the line's external input contract. Later stages receive params from transition mappings or job defaults.

## Discovery

```bash
islo schema factory
islo schema job
islo factory --help
ISLO_HELP=full islo factory
islo factory triggers list --with-status
islo factory triggers get github pull_request.opened
islo factory triggers get linear issue.updated
islo factory triggers get slack message.received
```

## Line commands

```bash
islo factory line validate line.toml
islo factory line deploy line.toml --dry-run
islo factory line deploy line.toml
islo factory line list
islo factory line get <name>
islo factory line run <name> --param KEY=VALUE
islo factory line runs <name>
```

## Line runs

Inspect and control a run after `islo factory line run`:

```bash
islo factory line-run status <run-id>
islo factory line-run events <run-id>
islo factory line-run retry-stage <run-id> --stage-name <stage> --reason "<reason>"
islo factory line-run rerun-from-stage <run-id> --stage-name <stage> --reason "<reason>"
islo factory line-run follow-up <run-id> --stage-name <stage> --reason "<reason>"
islo factory line-run agent-turn <run-id> --stage-name <stage> --message "<message>"
islo factory line-run cancel <run-id> --reason "<reason>"
```

## Transitions

Line routing uses typed transitions declared in `line.toml`. Check `islo schema factory` for the full condition AST and param bindings.

| Type | Use when |
|------|----------|
| `conditional` | Deterministic routing on stage status, outputs, trigger fields, or loop exhaustion (`max_iterations`) |
| `agentic` | The product-managed line routing agent chooses among named options at a decision pause |

Every line needs exactly one entry transition from `trigger` with an always-when entry transition. Completion must target the reserved `done` sink explicitly. Check `islo schema factory` for the condition AST.

## Decision pauses

A line run can pause when routing is ambiguous, a loop is exhausted, or an operator needs to weigh in. Continue the run with `islo factory line-run` commands above.

Optional per-line instructions for the product-managed line routing agent go in `agent.instructions` per `islo schema factory` (`literal` or `knowledge` bindings). They guide routing for this line; they do not replace stage job prompts.

## Triggers

Factory lines can start manually, on a schedule, via webhook, or from integration events (GitHub, Linear, Slack). Check `islo schema factory` for the current trigger types, selectors, and wiring.

| Trigger kind | Use when |
|--------------|----------|
| Manual | Operator or API starts a run |
| Schedule | Recurring cron-based runs |
| Webhook | External HTTP events should start a line run |
| Integration | GitHub, Linear, or Slack events should start a line run |

For standalone webhook receivers (sandbox lifecycle, single job trigger without orchestration), see `webhooks.md`.

## Harness and model

Each stage job's `run_agent` step declares harness and model. For Islo inference, use `harness = "codex"` and an inference model id — see **Islo inference in Factory** in `agents-and-inference.md`.

- **Codex** — Islo-managed inference; no provider key needed.
- **Claude / Cursor** — provider-managed via gateway integrations.

Query `GET /inference/models` for current Islo inference models rather than hardcoding lists.

## Knowledge

Attach tenant knowledge to agent-powered stage jobs via `run_agent` prompt or knowledge bindings — see `knowledge.md`. Check `islo schema job` for binding shapes.

## Shared sandbox across stages

When stages should share workspace state, configure the stage jobs to reuse the same sandbox. Check `islo schema job` for sandbox `mode` options.

## Recipes and templates

The Islo UI includes built-in Factory recipes (PR review, bug fix, QA, CI fix). For runnable template repos:

```text
https://github.com/islo-labs/islo-agents
```

See `templates.md` for how to adopt templates.

## Escape hatches

Users rarely need these. Prefer a Factory line first.

- **Standalone single-stage job** — only when the user explicitly wants durable or scheduled work without line orchestration. See `jobs.md`.
- **HTTP event without orchestration** — create an incoming webhook. See `webhooks.md`.
- **Outgoing notifications** — configure outgoing webhooks. See `webhooks.md` and `islo schema webhook`.

## Things to avoid

- Do not write line or stage job manifests from memory. Use `islo schema factory`, `islo schema job`, and `--dry-run`.
- Do not build multi-stage orchestration in shell when a Factory line handles routing, loops, and decisions.
- Do not put provider tokens in manifests or sandbox env by default.
- Do not replace agent judgment with hand-written shell business logic or shell-wrapped agent CLIs.
- Do not hardcode inference model lists — query `/inference/models`.
