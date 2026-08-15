---
name: using-islo
description: Use Islo sandboxes, Factory lines, managers, reusable environments, harness and model selection, Islo inference, knowledge, jobs, webhooks, gateway profiles, and SDKs. Use when the user mentions Islo, islo.dev, islo.yaml, Factory, line.toml, manager.toml, islo factory, islo use, islo environment, islo job, job.toml, islo knowledge, islo webhook, harness, model selection, Islo inference, gateway+, GitHub or Slack integrations, or @islo-labs/sdk.
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
   - Jobs: `islo job init <name>` → edit → `islo schema job` → `islo job deploy <name> --dry-run`
   - Webhooks: `islo schema webhook`
   - Do not write manifest field shapes from memory — the installed CLI is the source of truth
   - Treat skill examples as patterns, not drop-in manifests
4. Do not ask users to install or authenticate Claude Code, Cursor agent, or Codex inside the sandbox before trying them. They are preinstalled, and connected integrations provide auth.
5. Do not tell users to put GitHub, Slack, model-provider, or other provider tokens inside a sandbox unless they explicitly choose that escape hatch. Prefer connected providers and the `default` gateway profile.
6. For reusable sandbox variables and secrets, use `islo environment` and check `islo schema use` for how environments attach to sandboxes and jobs.

## Choose the right reference

- **Factory lines, managers, stages, transitions, triggers, and line runs:** read `automations.md` and `factory.md`.
- **Harness, model, and Islo inference selection:** read `agents-and-inference.md`.
- **Lower-level job manifests, schedules, and single-step agent runs:** read `jobs.md`.
- **Lower-level incoming/outgoing webhooks:** read `webhooks.md`.
- **Knowledge items (memories, skills, rules):** read `knowledge.md`.
- Sandbox create/connect/exec/pause/resume/stop/delete flows: read `sandbox-lifecycle.md`.
- Gateway profiles, provider integrations, phantom tokens, GitHub, Slack, and no-token-in-sandbox patterns: read `gateway-integrations.md`.
- Programmatic usage with generated SDKs instead of shelling out to the CLI: read `sdk.md`.
- Runnable automation examples (e.g. PR review): read `templates.md`.

## Working rules

- Treat **Factory lines** as the primary automation product. Prefer a line when work spans multiple stages, loops, decisions, schedules, webhooks, or integration triggers.
- Use **jobs** for single-stage execution units that a line stage references, or for simple one-off durable work.
- Use **webhooks** for HTTP event ingress/egress; Factory lines can also be triggered by webhook or integration events.
- For interactive or ad hoc sandbox work, prefer `islo use`. It creates or reconnects, then opens a shell or runs a command.
- For reusable sandbox environment variables or environment-owned gateway-injected secrets, use `islo environment` to manage a named environment and `islo use --environment <name>` to apply it at sandbox creation.
- For agent work, prefer `islo use --agent claude`, `islo use --agent cursor`, or `islo use --agent codex`; use `--task` for a background prompt.
- For judgment-heavy automation, run an agent inside the job stage or sandbox. Do not replace the agent with hand-written shell business logic.
- For internal tools, dashboards, and custom launchers, prefer the SDK.
