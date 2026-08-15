# Factory lines

Use this reference for Factory managers, lines, deploy, and line runs. For manifest field shapes, use `islo schema factory` and validate with `--dry-run` — do not write manifests from memory.

## Mental model

```text
manager.toml  →  decision agent identity for line pause points
job.toml      →  one stage's work (deploy separately)
line.toml     →  orchestration graph (stages, transitions, triggers)
```

Factory is Islo's orchestration layer. **Jobs** are stage-level work units. **Lines** wire jobs through stages, transitions, and optional manager decisions. **Managers** define the decision agent for pause points.

## Deploy order

1. Deploy each job referenced by line stages: `islo job deploy <name>`
2. Deploy the manager: `islo factory manager deploy manager.toml`
3. Validate, then deploy the line:
   ```bash
   islo factory line deploy line.toml --dry-run
   islo factory line deploy line.toml
   ```

The first stage's job defines the line's external input contract. Later stages receive params from transition mappings or job defaults.

## Discovery

```bash
islo schema factory
islo factory --help
ISLO_HELP=full islo factory
```

## Manager workflow

Managers are the decision agent for a line. Deploy and validate before referencing a manager from a line:

```bash
islo factory manager validate manager.toml
islo factory manager deploy manager.toml
islo factory manager list
islo factory manager get <name>
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
islo factory line status <run-id>
```

## Triggers

Factory lines can start manually, on a schedule, via webhook, or from integration events (GitHub, Linear, Slack). Check `islo schema factory` for the current trigger types, selectors, and wiring.

For standalone HTTP ingress without line orchestration, see `webhooks.md`.

## Shared sandbox across stages

When stages should share workspace state, configure the stage jobs to reuse the same sandbox. Check `islo schema job` for sandbox `mode` options and `islo schema factory` for how stages reference jobs.

## When to use jobs or webhooks directly

- **Single-stage, no routing** — a job alone is enough. See `jobs.md`.
- **HTTP ingress without orchestration** — an incoming webhook alone may be enough. See `webhooks.md`.
- **Multi-stage, loops, decisions, or integration triggers** — use a Factory line.

For harness and model selection, see `agents-and-inference.md`.

## Things to avoid

- Do not write `line.toml`, `manager.toml`, or stage `job.toml` from memory. Use `islo schema factory`, `islo schema job`, and `--dry-run`.
- Do not build multi-stage orchestration in shell when a Factory line handles routing, loops, and decisions.
