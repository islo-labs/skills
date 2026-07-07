# Islo automations

Use this reference for durable jobs, scheduled jobs, manual runs, incoming webhooks, and automation templates.

## Mental model

Islo automations are repeatable work that runs in managed sandboxes:

- A job defines the work and sandbox requirements.
- A deployment creates a versioned job definition.
- A run executes a version with parameters.
- A `[schedule]` section in `job.toml` creates or updates the job schedule on deploy.
- An incoming webhook reacts to an external event and can manage sandboxes or trigger a job.

## Discovery

- Use `islo schema`, `islo schema job`, `ISLO_HELP=full islo`, and `islo job --help` for job commands.
- Use `[schedule]` in `job.toml` for scheduled jobs.
- The control plane validates schedule cron expressions at deploy time, stores one active schedule per job, and registers the next run through the workflow scheduler.

## Before writing `job.toml`

**Required workflow.** Do not skip this and write a manifest from examples alone.

```bash
islo job init <name>
# edit jobs/<name>/job.toml
islo job deploy <name> --dry-run
islo job deploy <name>
```

`islo job init` is the source of truth for defaults such as:

- `[run]`: `fail_fast = true`, `fanout = false`
- `[run.sandbox]`: `mode = "provision"`, `image = "islo/default"`, `init = "full"`, `gateway_profile = "default"`
- `[[run.tasks.steps]]`: `name` plus exactly one action (`exec`, `snapshot`, `pause`, `resume`, or `delete`)

Common mistakes to avoid:

- `mode = "ephemeral"` — not valid; use `provision`, `ensure`, or `reuse`
- omitting `image` when `mode` is `provision` or `ensure` — deploy validation fails
- `timeout` on a step — not a valid step field; put run-level timeout under `[run]` if needed
- `${param}` or bash variable expansion in prompts — Islo substitutes run params itself
- single-brace `{param}` in `exec` — use `{{param}}` (see below)

## Job manifests

The standard manifest path is:

```text
jobs/<name>/job.toml
```

Typical manifest sections:

- `[job]`: name, version, description.
- `[job.params.*]`: parameter schema and validation.
- `[run]`: fail-fast, fanout, timeout, workdir, teardown policy.
- `[run.sandbox]`: sandbox mode, name, image, snapshot, CPU, memory, init mode, gateway profile.
- `[[run.tasks]]` and `[[run.tasks.steps]]`: ordered commands to run inside the sandbox.
- `[schedule]`: optional schedule for recurring runs.
- Optional verification sections when supported by the target CLI/control plane.

Use `gateway_profile = "default"` or a named profile when the job needs provider API access through Islo gateway credential injection.

### Run parameters

Declare params under `[job.params.<name>]` and reference them in the manifest with **double braces**:

```toml
[job.params.ticket_id]
type = "string"
required = true

[[run.tasks.steps]]
name = "summarize"
exec = ["bash", "-lc", "claude -p 'Fetch ticket {{ticket_id}} and post to {{slack_channel}}'"]
```

Islo substitutes `{{param_name}}` in strings (including `exec` arrays) before the step runs. Reserved: `{{run_id}}`. Do not use `${param}` — that is bash expansion and will not be filled by Islo. Declare every referenced param under `[job.params.*]` or deploy validation fails.

Scheduled jobs cannot require params without defaults.

## Agent-first automations

When the automation asks an agent to understand, summarize, triage, plan, comment, or coordinate work across tools, the job should run an agent inside the sandbox. Do not turn that request into a hand-written shell script that calls APIs directly.

Good examples for agent-first jobs:

- "Take one Linear ticket and post a daily summary to Slack."
- "Review open PRs every morning and leave GitHub comments."
- "Check failed CI runs, investigate, and open a fix PR."
- "Triage new support issues and label them."

In these cases, shell is only a launcher. The actual behavior should live in the prompt passed to Claude Code, Cursor agent, Codex, or a small agent harness such as `islo-labs/islo-agents`.

Agent entrypoints available in Islo sandboxes:

- Claude Code: `claude -p "<prompt>"`
- Cursor agent: `agent --yolo --trust -p "<prompt>"`
- Codex: `codex --sandbox danger-full-access -c model_provider=islo exec --skip-git-repo-check "<prompt>"`

Example step launcher for "take one Linear ticket and post a summary to Slack". Start from `islo job init <name>`, then adapt sandbox and params — this snippet only shows the agent step pattern:

```toml
[job.params.ticket_id]
type = "string"
required = true

[job.params.slack_channel]
type = "string"
default = "#general"

[run.sandbox]
mode = "provision"
image = "islo/default"
gateway_profile = "linear-slack"
init = "full"

[[run.tasks.steps]]
name = "summarize-linear-ticket"
exec = [
  "bash",
  "-lc",
  '''
set -euo pipefail
claude -p "$(cat <<'PROMPT'
You are running inside an Islo sandbox with Linear and Slack access via gateway-managed credentials.

Fetch ticket {{ticket_id}} and post a concise update to {{slack_channel}}.
Do not ask for API tokens and do not write tokens to disk.

1. Read the ticket title, description, comments, status, assignee, priority, and URL.
2. Write a 2-3 sentence standup summary: status, context, blockers or next steps.
3. Post to {{slack_channel}} using Slack Block Kit with ticket key, title, status, assignee, and summary.
4. Confirm what you posted and the ticket ID.
PROMPT
)"
''',
]
```

For larger automations, prefer a prompt file or the `islo-agents` harness over embedding a long prompt directly in `job.toml`.

## Common job workflow

The durable job flow is:

```bash
islo job init <name>
islo job deploy <name>
islo job run <name> --param KEY=VALUE --watch
islo job status <name> <run-id>
islo job runs <name>
islo job versions <name>
islo job event <compute-command-id>
```

## Scheduled jobs

Use `[schedule]` in `job.toml` for recurring Islo job runs.

```toml
[schedule]
cron = "0 * * * *"
timezone = "UTC"
enabled = true
```

Deploying the job creates or updates the schedule:

```bash
islo job deploy <name>
```

### Params and schedules

The scheduler fires without a human passing `--param`. If `[schedule]` is present:

- every param must have a `default`, **or** be optional (`required = false` with no default)
- `required = true` with no `default` fails deploy validation
- you cannot set both `required = true` and `default` on the same param

For a daily standup on a fixed ticket/channel, bake the values into defaults:

```toml
[job.params.ticket_id]
type = "string"
default = "ENG-123"

[job.params.slack_channel]
type = "string"
default = "#standup"
```

Manual runs can still override defaults: `islo job run <name> --param ticket_id=ENG-456 --watch`.

If deploy fails with only `VALIDATION_ERROR` / `Invalid request parameters`, the usual schedule conflict is a required param without a default. Remove `[schedule]` temporarily to confirm, then add `default = "..."` to each param the scheduled run needs.

The control plane behavior:

- `cron` is required for an active schedule and must be a valid cron expression.
- `timezone` defaults to `UTC`.
- `enabled` defaults to `true`.
- Removing `[schedule]`, omitting `cron`, or setting `enabled = false` disables the existing schedule on the next deploy.
- One active schedule exists per job.
- `GET /jobs/{name}/schedule` returns `cron`, `timezone`, `enabled`, and `schedule_generation`.
- `DELETE /jobs/{name}/schedule` disables the schedule.

Scheduled runs execute the latest deployed job behavior registered by deploy. Keep scheduled job tasks idempotent because retries and repeated runs are part of the model.

## Incoming webhooks

Incoming webhooks are for external systems such as GitHub, Stripe, Slack, or a custom service.

Use them when an external HTTP event should:

- ensure a sandbox exists
- resume a sandbox
- pause a sandbox
- delete a sandbox
- deliver a request to a port inside a running sandbox
- trigger a job run, when supported by the target API/CLI

Webhook auth and verification are separate from outbound provider credentials. Inbound webhook secrets verify the sender. Outbound provider credentials should still use gateway profiles and integrations.

If the target CLI does not expose a supported webhook action yet, check whether `--request-json`, SDK calls, or the HTTP API exposes it.

## Templates

For runnable examples, link to `https://github.com/islo-labs/islo-agents`.

That repo currently covers:

- PR review through `islo-review`
- CI babysitting through `islo-babysit`
- E2E verification through `islo-verify`
- Linear-triggered task execution

Do not copy templates into this skills repo. Point users to the template repo and explain which template matches their use case.

## Things to avoid

- Do not write `job.toml` from skill examples without running `islo job init` and `islo job deploy --dry-run` first.
- Do not turn a one-off shell command into a job unless it needs repeatability, scheduling, retries, or auditability.
- Do not implement judgment-heavy agent work as shell business logic. Use shell only to launch the agent, load a prompt, or run a small harness.
- Do not put provider tokens in job params or sandbox environment variables by default.
- Do not create a separate scheduler around Islo jobs when `[schedule]` in `job.toml` is enough.
- Do not assume all job orchestration lives in the CLI. The CLI deploys and starts work; the control plane owns durable job versioning, runs, schedules, and orchestration.
