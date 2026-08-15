# Jobs

Use this reference when a user **explicitly** wants a standalone durable job (`job.toml`) — without Factory line orchestration. In normal flows, jobs are **stage building blocks inside Factory lines**; start with `factory.md` instead.

## Discovery

Do not write or edit `job.toml` from memory. The installed CLI is the source of truth:

```bash
islo schema job
islo job --help
ISLO_HELP=full islo job
```

The schema example shows the current `run_agent` shape: nested `[run.tasks.steps.run_agent]` with `[run.tasks.steps.run_agent.prompt]` bindings, plus top-level `[outputs.<name>]` for structured agent results.

## Required workflow

```bash
islo job init <name>
# edit jobs/<name>/job.toml — use islo schema job for field shapes
islo job deploy <name> --dry-run
islo job deploy <name>
```

Always start from `islo job init <name>`. The scaffold sets the current baseline; edit from there.

## Agent-first jobs

When the automation needs judgment, summarization, triage, or tool use across services, the job should run an agent inside the sandbox — not a hand-written shell script that calls APIs directly.

Good examples:

- Take one Linear ticket and post a daily summary to Slack.
- Review open PRs every morning and leave GitHub comments.
- Check failed CI runs, investigate, and open a fix PR.

Use session-mode `run_agent` steps. Pattern (validate against `islo schema job`):

```toml
[[run.tasks.steps]]
name = "summarize"

[run.tasks.steps.run_agent]
mode = "session"
harness = "claude"
model = "claude-sonnet-4"

[run.tasks.steps.run_agent.prompt]
type = "literal"
value = "Summarize {ticket_id} and return JSON with a summary field."

[outputs.summary]
type = "string"
required = true
```

Prompt bindings can also reference knowledge: `{ type = "knowledge", slug = "..." }`. See `knowledge.md` and `agents-and-inference.md` for harness and model selection.

Do not shell-wrap `claude`, `agent`, or `codex` CLI entrypoints in exec steps when `run_agent` is available.

For runnable examples, see `templates.md` and `https://github.com/islo-labs/islo-agents`.

## Params and runs

- Declare job params in the manifest per `islo schema job`.
- Pass values at run time: `islo job run <name> --param KEY=VALUE --watch`.
- For scheduled jobs, every param the schedule needs must have a default before you add the schedule. Check `islo schema job` for param and schedule rules.
- Keep scheduled tasks idempotent — retries and repeated runs are part of the model.

## Sandbox and gateway defaults

- Use the `default` gateway profile when the job needs provider API access.
- Use a named environment when the job sandbox should reuse environment-owned variables or gateway-injected secrets. Check `islo schema job` and `islo schema use`.
- Do not hand-write sandbox provisioning fields from memory. Use `islo job init` and `islo schema job`.
- Use the platform default image (`ghcr.io/islo-labs/islo-runner:latest`) or a fully qualified image reference — not unqualified image names.

## Example workflow: Linear ticket → Slack summary

Narrative pattern (not a drop-in manifest):

1. `islo job init linear-to-slack`
2. Edit `jobs/linear-to-slack/job.toml` using `islo schema job` — params for ticket ID and Slack channel, a session-mode `run_agent` step with harness `claude`, nested prompt binding, declared `outputs`, sandbox on the default runner image, `default` gateway profile.
3. Connect Linear and Slack integrations before deploy (`islo login --tool` as needed).
4. Add a daily schedule only after every param has a default.
5. `islo job deploy linear-to-slack --dry-run`, then deploy.
6. Verify with `islo job run linear-to-slack --watch`.

For a runnable template, start from `https://github.com/islo-labs/islo-agents`.

## Common commands

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

Scheduled jobs use a schedule section in `job.toml`. Deploy updates the schedule on the control plane. Check `islo schema job` for schedule fields, enable/disable behavior, and param-default requirements before adding one.

- One active schedule per job.
- Removing or disabling the schedule takes effect on the next deploy.
- Keep scheduled tasks idempotent — retries and repeated runs are part of the model.

## Things to avoid

- Do not hand-write job manifests from memory or skill examples. Use `islo job init` and `islo schema job`.
- Do not add a schedule until every param has a default.
- Do not turn a one-off shell command into a job unless it needs repeatability, scheduling, or auditability.
- Do not replace agent judgment with hand-written shell business logic or shell-wrapped agent CLIs.
- Do not put provider tokens in job params or sandbox env by default.
