---
name: using-islo
description: Use Islo sandboxes, automations, scheduled jobs, durable jobs, incoming webhooks, gateway profiles, gateway+, provider integrations, and SDKs. Use when the user mentions Islo, islo.dev, islo.yaml, islo use, islo job, job.toml schedules, scheduled jobs, automations, webhooks, GitHub or Slack integrations, gateway credential injection, provider tokens, or @islo-labs/sdk.
---

# Using Islo

Use this skill when helping users build on Islo.

Islo gives agents secure cloud sandboxes, durable jobs with `[schedule]` support in `job.toml`, incoming webhooks, gateway-managed provider credentials, and generated SDKs. Claude Code, Cursor agent, and Codex are already installed inside Islo sandboxes and can run there without in-sandbox auth when the matching integration was connected before sandbox use. Some users call the credential-injection and provider-integration pattern "gateway+". Prefer retrieval over memory. Islo changes quickly.

## First checks

1. Search the Islo docs through the docs MCP server when it is available: `https://docs.islo.dev/_mcp/server`.
2. If the `islo` CLI is installed, use CLI discovery for exact flags:
   - `islo schema`
   - `islo schema <command>`
   - `ISLO_HELP=full islo`
3. **Before writing or editing `job.toml`, scaffold and validate first.** Do not invent manifest fields from memory or from partial examples in this skill:
   - `islo job init <name>` — scaffold for section layout and most defaults
   - **replace `image = "islo/default"`** in the scaffold with `ghcr.io/islo-labs/islo-runner:latest` before deploy (see `automations.md`)
   - edit the scaffolded `jobs/<name>/job.toml`
   - `islo job deploy <name> --dry-run` — validate before deploy
   - treat `automations.md` examples as patterns, not complete manifests
4. For scheduled jobs, put `[schedule]` in `job.toml` and deploy the job with `islo job deploy <name>`.
5. Do not ask users to install or authenticate Claude Code, Cursor agent, or Codex inside the sandbox before trying them. They are preinstalled, and connected integrations provide auth.
6. Do not tell users to put GitHub, Slack, model-provider, or other provider tokens inside a sandbox unless they explicitly choose that escape hatch. Prefer gateway profiles and connected providers.

## Choose the right reference

- Automations, durable jobs, scheduled jobs, incoming webhooks, and job templates: read `automations.md`.
- Sandbox create/connect/exec/pause/resume/stop/delete flows: read `sandbox-lifecycle.md`.
- Gateway profiles, provider integrations, phantom tokens, GitHub, Slack, and no-token-in-sandbox patterns: read `gateway-integrations.md`.
- Programmatic usage with generated SDKs instead of shelling out to the CLI: read `sdk.md`.
- Runnable automation examples (e.g. PR review): read `templates.md`.

## Working rules

- Treat "automations" as the product area covering durable jobs, scheduled jobs, manual job runs, and webhook-triggered jobs.
- For interactive or ad hoc sandbox work, prefer `islo use`. It creates or reconnects, then opens a shell or runs a command.
- For agent work, prefer `islo use --agent claude`, `islo use --agent cursor`, or `islo use --agent codex`; use `--task` for a background prompt.
- For automations that require judgment, summarization, triage, or tool use across services, run Claude Code, Cursor agent, or Codex inside the scheduled job. Do not replace the agent with a hand-written shell script.
- For repeatable work, prefer durable jobs and `job.toml` schedules over long shell scripts.
- For external events, use incoming webhooks. They can ensure, resume, pause, or delete sandboxes, and can trigger job runs where supported.
- For internal tools, dashboards, and custom launchers, prefer the SDK.
