---
name: using-islo
description: Use Islo sandboxes, Factory lines, line runs, harness and model selection, Islo inference, knowledge, jobs, schedules, webhooks, gateway profiles, environments, and SDKs. Use when the user mentions Islo, islo.dev, islo.yaml, Factory, line.toml, line-run, islo factory, islo factory triggers, islo use, islo environment, islo job, job.toml, run_agent, islo knowledge, islo webhook, automation, scheduled job, line run, harness, model selection, Islo inference, gateway+, GitHub or Slack integrations, or @islo-labs/sdk.
---

# Using Islo

Use this skill when helping users build on Islo.

Islo gives agents secure cloud sandboxes, **Factory lines** for multi-stage automation, gateway-managed provider credentials, and generated SDKs. Jobs and webhooks are lower-level building blocks that Factory lines compose. Claude Code, Cursor agent, and Codex are preinstalled in sandboxes and can run without in-sandbox auth when integrations were connected before sandbox use. Connect integrations with `islo login --tool`; the `default` gateway profile handles credential injection for most work. Prefer retrieval over memory. Islo changes quickly.

## First checks

1. Search the Islo docs through the docs MCP server when it is available: `https://docs.islo.dev/_mcp/server`.
2. If the `islo` CLI is installed, use CLI discovery for exact flags:
   - `islo schema`
   - `islo schema <command>`
   - `ISLO_HELP=full islo`
3. **Before writing or editing manifests, always scaffold first:**
   - Factory: `islo schema factory`, then `islo factory line deploy line.toml --dry-run`
   - Factory integration triggers: `islo factory triggers list --with-status`
   - Jobs: `islo job init <name>` → edit → `islo schema job` → `islo job deploy <name> --dry-run`
   - Webhooks: `islo schema webhook`
   - Sandbox config: `islo schema use`
   - Knowledge: `islo schema knowledge`
   - Do not write manifest field shapes from memory — the installed CLI is the source of truth
   - Treat skill examples as patterns, not drop-in manifests
4. Do not ask users to install or authenticate Claude Code, Cursor agent, or Codex inside the sandbox before trying them. They are preinstalled, and connected integrations provide auth.
5. Do not tell users to put GitHub, Slack, model-provider, or other provider tokens inside a sandbox unless they explicitly choose that escape hatch. Prefer connected providers and the `default` gateway profile.
6. For reusable sandbox variables and secrets, use `islo environment` and check `islo schema use` for how environments attach to sandboxes and jobs.

## When to use what

| User goal | Start here |
|-----------|------------|
| Automation (default) | Factory line — `automations.md`, `factory.md` |
| Interactive sandbox or ad hoc agent work | `islo use` — `sandbox-lifecycle.md` |
| Harness, model, or inference routing | `agents-and-inference.md` |
| HTTP event → sandbox, no line orchestration | Incoming webhook — `webhooks.md` |
| Reusable policy, skills, or rules for agent steps | `islo knowledge` — `knowledge.md` |
| Provider credentials without tokens in sandbox | `gateway-integrations.md` |
| Product integration in code | SDK — `sdk.md` |
| Runnable starting points | `templates.md` and `https://github.com/islo-labs/islo-agents` |
| Standalone single-stage job (advanced) | Job — `jobs.md` |

**Default recommendation:** use a Factory line for automation. Jobs are stage building blocks inside lines — users rarely author `job.toml` directly unless they explicitly want a single-stage durable or scheduled run without line orchestration.

## Choose the right reference

- **Factory lines, stages, transitions, triggers, line runs, and decision pauses:** read `automations.md` and `factory.md`.
- **Harness, model, and Islo inference selection (including Islo inference in Factory):** read `agents-and-inference.md`.
- **Standalone jobs (advanced):** read `jobs.md` only when the user explicitly wants a single-stage job without line orchestration.
- **Lower-level incoming/outgoing webhooks:** read `webhooks.md`.
- **Knowledge items (memories, skills, rules):** read `knowledge.md`.
- **Sandbox create/connect/exec/pause/resume/stop/delete flows:** read `sandbox-lifecycle.md`.
- **Gateway profiles, provider integrations, phantom tokens, GitHub, Slack, and no-token-in-sandbox patterns:** read `gateway-integrations.md`.
- **Programmatic usage with generated SDKs instead of shelling out to the CLI:** read `sdk.md`.
- **Runnable automation examples (e.g. PR review):** read `templates.md`.

## Working rules

- Treat **Factory lines** as the primary automation product. Prefer a line when work spans multiple stages, loops, decisions, schedules, webhooks, or integration triggers.
- Use **jobs** as stage building blocks inside Factory lines. Suggest standalone `job.toml` only when the user explicitly wants single-stage durable or scheduled work without line orchestration — see `jobs.md`.
- Use **webhooks** for HTTP event ingress/egress; Factory lines can also be triggered by webhook or integration events.
- For interactive or ad hoc sandbox work, prefer `islo use`. It creates or reconnects, then opens a shell or runs a command.
- For reusable sandbox environment variables or environment-owned gateway-injected secrets, use `islo environment` to manage a named environment and `islo use --environment <name>` to apply it at sandbox creation.
- For agent work in sandboxes, prefer `islo use --agent claude`, `islo use --agent cursor`, or `islo use --agent codex`; use `--task` for a background prompt.
- For agent work in Factory stage jobs, prefer `run_agent` steps with nested prompt bindings per `islo schema job`. Do not shell-wrap `claude`, `agent`, or `codex` CLI entrypoints unless `islo schema job` shows an exec-mode path that requires it.
- For Factory line run control after a run starts, use `islo factory line-run` (`status`, `events`, `retry-stage`, `agent-turn`, `cancel`).
- For judgment-heavy automation, run an agent inside the job stage or sandbox. Do not replace the agent with hand-written shell business logic.
- For internal tools, dashboards, and custom launchers, prefer the SDK.
