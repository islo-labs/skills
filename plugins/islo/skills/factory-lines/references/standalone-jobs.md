# Maintain existing standalone Jobs

Read this reference only when the user explicitly asks to maintain an existing Job or `job.toml`. For a new automation goal, start with `factory-design.md` and use Agent stages. Leave existing Job stages in place and add no new ones.

## Workflow

```bash
islo job deploy --path jobs/<name>/job.toml --dry-run
islo job deploy --path jobs/<name>/job.toml
islo job run <name> --param KEY=VALUE --watch
islo job status <name> <run-id>
islo job event <command-id>
```

Run `islo job run` with representative params and inspect step output via `islo job event` **before** wiring incoming webhooks, integration triggers, or schedules to production traffic.

Inspect the existing Job and edit its manifest per `job-manifest.md`. Do not scaffold a new Job.

## Agent-first

When the work needs judgment (triage, summarization, review, cross-service tool use), the job runs an agent via `run_agent`, not a hand-written shell script calling APIs. Do not shell-wrap `claude`, `cursor`, `codex`, or `opencode` CLI entrypoints in exec steps; `run_agent` is the path.

For a new Line with routing or multiple stages, use Agents. If the Agent schemas cannot express a required capability, report the missing capability and stop the dependent design.

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

## Outcome in chat

After successfully deploying an explicitly requested standalone Job, post exactly one card in its own paragraph: `[JOB_NAME](/factories/FACTORY_KEY/jobs/JOB_NAME?view=card)`. Use the Factory key from `factory.key` in `islo factory current --output json` with the deployment's Factory selection, and URL-encode the Job name. Follow [chat-embeds.md](chat-embeds.md#creation-outcomes). Do not post cards for internal Jobs compiled from Agent stages.
