# Standalone jobs

For the rare case where the user explicitly wants a single-stage durable or scheduled run without line orchestration. In normal flows, jobs are stage building blocks inside a line; start with `create-a-line.md`.

## Workflow

```bash
islo job init <name>
islo job deploy --path jobs/<name>/job.toml --dry-run
islo job deploy --path jobs/<name>/job.toml
islo job run <name> --param KEY=VALUE --watch
islo job status <name> <run-id>
islo job event <command-id>
```

Run `islo job run` with representative params and inspect step output via `islo job event` **before** wiring incoming webhooks, integration triggers, or schedules to production traffic.

Always scaffold with `islo job init` and edit per `job-manifest.md`; the manifest anatomy is identical to a stage job.

## Agent-first

When the work needs judgment (triage, summarization, review, cross-service tool use), the job runs an agent via `run_agent`, not a hand-written shell script calling APIs. Do not shell-wrap `claude`, `cursor`, `codex`, or `opencode` CLI entrypoints in exec steps; `run_agent` is the path.

Good standalone jobs: post a daily Linear-to-Slack summary, review open PRs every morning, investigate failed CI runs and open a fix PR. If the work grows a second stage, routing, or a decision point, it is a line.

## Schedules

A `[schedule]` section (cron, timezone, enabled) in `job.toml` creates or updates the schedule on deploy. Rules:

- Every param the schedule uses must have a default before you add it.
- One active schedule per job; removing or disabling it takes effect on the next deploy.
- Keep scheduled tasks idempotent; retries and repeated runs are part of the model.

## Inspecting

```bash
islo job runs <name>
islo job status <name> <run-id>
islo job event <command-id>
islo job versions <name>
islo job list
islo job get <name>
islo job rm <name>
```
