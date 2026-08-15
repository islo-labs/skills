# Jobs

Use this reference for lower-level durable jobs (`job.toml`), schedules, and single-stage agent runs. Factory lines compose jobs as stage execution units — see `automations.md` and `factory.md` for orchestration.

## Discovery

Do not write or edit `job.toml` from memory. The installed CLI is the source of truth:

```bash
islo schema job
islo job --help
ISLO_HELP=full islo job
```

## Required workflow

```bash
islo job init <name>
# edit jobs/<name>/job.toml
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

Use `run_agent` steps in the job manifest. See `agents-and-inference.md` for harness and model selection. Check `islo schema job` for the current `run_agent` shape.

For runnable examples, see `templates.md` and `https://github.com/islo-labs/islo-agents`.

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

Scheduled jobs use a schedule section in `job.toml`. Deploy updates the schedule. Check `islo schema job` for schedule fields and param-default requirements before adding one.

Keep scheduled tasks idempotent — retries and repeated runs are part of the model.

## Things to avoid

- Do not hand-write job manifests from memory or skill examples. Use `islo job init` and `islo schema job`.
- Do not turn a one-off shell command into a job unless it needs repeatability, scheduling, or auditability.
- Do not replace agent judgment with hand-written shell business logic.
- Do not put provider tokens in job params or sandbox env by default.
