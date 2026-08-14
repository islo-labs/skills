# Jobs

Use this reference for lower-level durable job manifests (`job.toml`), schedules, and single-stage agent runs. Factory lines compose jobs as stage execution units — see `automations.md` and `factory.md` for orchestration.

## Before writing `job.toml`

**Required workflow.** Do not skip this and write a manifest from memory.

```bash
islo job init <name>
# edit jobs/<name>/job.toml
islo job deploy <name> --dry-run
islo job deploy <name>
```

Always start from `islo job init <name>`. The scaffold sets section layout, field names, the platform default sandbox image, and a param example.

## Manifest sections

Path: `jobs/<name>/job.toml`

| Section | Purpose |
|---------|---------|
| `[job]` | name, version, description |
| `[job.params.*]` | parameter schema and validation |
| `[run]` | fail-fast, fanout, timeout, workdir, teardown |
| `[run.sandbox]` | mode, name, image, snapshot, CPU, memory, gateway profile, environment |
| `[[run.tasks]]` / `[[run.tasks.steps]]` | ordered steps (shell, exec, run_agent) |
| `[schedule]` | optional cron schedule |
| `[outputs]` | optional structured outputs (claude/codex session agent only) |

Use `gateway_profile = "default"` when the job needs provider API access.

Use `environment = "production"` when a job sandbox should receive the environment's sandbox env vars or environment-owned gateway-injected secrets.

## Run parameters

Declare params under `[job.params.<name>]`. Islo substitutes `{param_name}` in exec strings before the step runs.

**Inline exec:**

```toml
[job.params.ticket_id]
type = "string"
default = "ENG-1"

[[run.tasks.steps]]
name = "summarize"
exec = ["bash", "-lc", "claude -p 'Fetch ticket {ticket_id}'"]
```

**Inside a heredoc** (single-quoted delimiter): use `{{param_name}}` in the manifest to leave `{param_name}` for run-time substitution.

### Params and schedules

If `[schedule]` is present, **every param the scheduled run needs must have a `default`**.

```toml
[job.params.ticket_id]
type = "string"
default = "ENG-123"

[schedule]
cron = "0 9 * * *"
timezone = "UTC"
enabled = true
```

Manual runs can override: `islo job run <name> --param ticket_id=ENG-456 --watch`.

## Agent steps

For judgment-heavy work, use `run_agent` instead of shell-wrapping an agent CLI:

```toml
[[run.tasks.steps]]
name = "review"
type = "run_agent"
mode = "session"
harness = "codex"
model = "kimi-k2.7-code"
prompt = "Review the changes and summarize findings."
```

See `agents-and-inference.md` for harness, model, and inference selection.

### Verified example: Linear ticket → Slack summary

Requires Linear and Slack integrations connected. Uses the `default` gateway profile.

```toml
[job]
name = "linear-to-slack"
version = "1.0.0"
description = "Fetch a Linear ticket and post a daily AI summary to Slack"

[job.params.ticket_id]
type = "string"
default = "ENG-1"

[job.params.slack_channel]
type = "string"
default = "#general"

[run]
fail_fast = true

[run.sandbox]
mode = "provision"
image = "ghcr.io/islo-labs/islo-runner:latest"
gateway_profile = "default"

[[run.tasks]]
name = "post-summary"

[[run.tasks.steps]]
name = "run-agent"
type = "run_agent"
mode = "session"
harness = "claude"
prompt = """
Fetch Linear ticket {ticket_id} and post a concise standup update to {slack_channel}.
Use gateway-managed credentials — do not ask for API tokens.
"""

[schedule]
cron = "0 9 * * *"
timezone = "UTC"
enabled = true
```

## Common workflow

```bash
islo job init <name>
islo job deploy <name> --dry-run
islo job deploy <name>
islo job run <name> --param KEY=VALUE --watch
islo job status <name> <run-id>
islo job runs <name>
islo job list
islo job get <name>
islo job versions <name>
islo job rm <name>
```

## Scheduled jobs

`[schedule]` in `job.toml` creates or updates the schedule on deploy:

- `cron` is required for an active schedule.
- `timezone` defaults to `UTC`.
- `enabled` defaults to `true`.
- Removing `[schedule]` or setting `enabled = false` disables on next deploy.
- One active schedule per job.

Keep scheduled tasks idempotent — retries and repeated runs are part of the model.

## Things to avoid

- Do not hand-write `[run.sandbox]` schema from memory. Use `islo schema job` or `islo job init`.
- Do not use unqualified image names; use `ghcr.io/islo-labs/islo-runner:latest` or a fully qualified reference.
- Do not add `[schedule]` until every param has a `default`.
- Do not turn a one-off shell command into a job unless it needs repeatability, scheduling, or auditability.
- Do not put provider tokens in job params or sandbox env by default.
