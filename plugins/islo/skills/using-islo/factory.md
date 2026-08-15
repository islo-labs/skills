# Factory lines

Use this reference for Factory lines, deploy, line runs, and interaction at decision pauses. For manifest field shapes, use `islo schema factory` and validate with `--dry-run` — do not write manifests from memory.

## Mental model

```text
job.toml   →  one stage's work (deploy separately)
line.toml  →  orchestration graph (stages, transitions, triggers)
```

Factory is Islo's orchestration layer. **Jobs** are stage-level work units. **Lines** wire jobs through stages, transitions, and triggers. When a run pauses for a decision, the operator or line routing agent continues it — retry a stage, send another agent turn, or cancel.

## Deploy order

1. Deploy each job referenced by line stages: `islo job deploy <name>`
2. Validate, then deploy the line:
   ```bash
   islo factory line deploy line.toml --dry-run
   islo factory line deploy line.toml
   ```
3. If the tenant Factory Manager runtime is disabled, enable it before lines that need routing decisions:
   ```bash
   islo factory manager status
   islo factory manager enable
   ```

The first stage's job defines the line's external input contract. Later stages receive params from transition mappings or job defaults.

## Discovery

```bash
islo schema factory
islo factory --help
ISLO_HELP=full islo factory
islo factory triggers list --with-status
islo factory triggers get github pull_request.opened
```

## Line workflow

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

Every line needs exactly one entry transition from `trigger` with `when = { op = "always" }`. Completion must target the reserved `done` sink explicitly.

## Interaction at decision pauses

A line run can pause when routing is ambiguous, a loop is exhausted, or an operator needs to weigh in. Continue the run with `islo factory line-run` commands above.

Optional per-line instructions for the product-managed line routing agent go in `line.toml` as `[agent.instructions]` — check `islo schema factory` for binding shapes (`literal` or `knowledge`). They guide routing for this line; they do not replace stage job prompts.

## Triggers

Factory lines can start manually, on a schedule, via webhook, or from integration events (GitHub, Linear, Slack). Check `islo schema factory` for the current trigger types, selectors, and wiring. Discover integration triggers with `islo factory triggers list` and `islo factory triggers get`.

For standalone HTTP ingress without line orchestration, see `webhooks.md`.

## Shared sandbox across stages

When stages should share workspace state, configure the stage jobs to reuse the same sandbox. Check `islo schema job` for sandbox `mode` options and `islo schema factory` for how stages reference jobs.

## When to use jobs or webhooks directly

- **Single-stage, no routing** — a job alone is enough. See `jobs.md`.
- **HTTP ingress without orchestration** — an incoming webhook alone may be enough. See `webhooks.md`.
- **Multi-stage, loops, decisions, or integration triggers** — use a Factory line.

For harness, model, and Islo inference in stage jobs, see `agents-and-inference.md`.

## Things to avoid

- Do not write line or stage job manifests from memory. Use `islo schema factory`, `islo schema job`, and `--dry-run`.
- Do not build multi-stage orchestration in shell when a Factory line handles routing, loops, and decisions.
