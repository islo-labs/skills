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

When a run pauses for a decision, the operator or line routing agent can provide follow-up input. Operators can also stop active work, steer a parked or completed run to a stage, or retry its latest failed stage.

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
islo factory line-run stop <run-id> --reason "<reason>"
islo factory line-run steer <run-id> <stage> --param KEY=VALUE
islo factory line-run retry <run-id>
islo factory line-run follow-up <run-id> --stage-name <stage> --reason "<reason>"
islo factory line-run agent-turn <run-id> --stage-name <stage> --message "<message>"
```

`stop` interrupts active stage work and parks the line without terminal cancellation. `steer` does not interrupt an active line: stop it first, wait until its status is `stopped`, then steer it. `retry` is shorthand for continuing a failed line from its latest failed stage.

## Transitions

Line routing uses typed transitions declared in `line.toml`. Check `islo schema factory` for the full condition AST and param bindings.

| Type | Use when |
|------|----------|
| `conditional` | Deterministic routing on stage status, outputs, trigger fields, or loop exhaustion (`max_iterations`) |
| `agentic` | The product-managed line routing agent chooses among named options at a decision pause |

Every line needs exactly one entry transition from `trigger` with an always-when entry transition. Completion must target the reserved `done` sink explicitly. Check `islo schema factory` for the condition AST.

## Decision pauses

A line run can pause when routing is ambiguous, a loop is exhausted, or an operator needs to weigh in. Use `follow-up` at a pending decision. Use `stop` and then `steer` when active work needs to be redirected, or `retry` after a stage failure.

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

## Deploy order

Deploy **every stage job first**, then the line. The line pins `job_version_id` at deploy time — deploying a job alone does not refresh what an already-deployed line runs.

```bash
islo job deploy stage-a --dry-run && islo job deploy stage-a
islo job deploy stage-b --dry-run && islo job deploy stage-b
islo factory line deploy line.toml --dry-run && islo factory line deploy line.toml
```

## Sandbox modes across stages

| Mode | Use when |
|------|----------|
| `provision` + `teardown_on_complete = true` | One-shot stage jobs; fresh env every run; hand off via git branch or typed outputs |
| `ensure` + named sandbox | Multiple stages intentionally share one VM and workspace |
| `session` on `run_agent` | Resume agent turns within a sandbox that supports sessions (`ensure` / reuse) |

Prefer **provision per stage** when stages only need a pushed branch — avoids stale env from `ensure` reconnects and delete/create races.

## Failure routing

Use **conditional** transitions to route hard failures to `done` when no human decision is wanted:

```toml
[transitions.when]
left = { type = "stage", path = "$.status" }
op = "eq"
right = { type = "literal", value = "failed" }
```

Use **`agentic`** transitions only when the line routing agent (or operator) should choose retry vs cancel. For automated loops, use conditional transitions with `max_iterations` on the back-edge.

## Multi-stage verify loops

Common pattern for agent implement → review → verify → open-pr:

```text
implement → review → verify → open-pr → done
     ↑_________|         ↑_______|
   review_feedback    verify_feedback
```

- **Implement** pushes a branch; does not open a PR until verify passes.
- **Review** checks diff vs acceptance criteria (no full CI).
- **Verify** runs CI-equivalent checks.
- Pass feedback from review/verify outputs into the next implement run via transition param mappings (`type = "output"`, `stage = "review"`, `name = "feedback"`).

## Shared sandbox across stages

When stages should share workspace state, configure the stage jobs to reuse the same sandbox (`ensure`). Check `islo schema job` for sandbox `mode` options.

## Harness code in line snapshots

Factory lines that run **harness code** (HTTP servers, CLIs, Playwright trees, scenario YAML) must ship that code in a **sandbox snapshot** referenced by stage jobs (`snapshot_name` on `[run.sandbox]`). The line/job repo holds harness source under `snapshot-src/`; `job.toml` stays thin — prompts, params, `run_agent`, and short `exec` steps only.

**Never** embed harness in `job.toml` with base64 blobs or bootstrap heredocs. That bloats manifests, hides diffs, and breaks the snapshot model. See **Harness and scripts in snapshots** in `jobs.md`.

## Recipes and templates

Runnable job and Factory line examples live in [`islo-labs/islo-agents`](https://github.com/islo-labs/islo-agents), including lines under `lines/`.

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
- Do not embed harness scripts or assets in `job.toml` (base64 or heredoc bootstrap). Use a line snapshot — see **Harness code in line snapshots** above.
