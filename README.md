# Islo Skills

Agent skills and plugin metadata for working with [Islo](https://islo.dev), the sandbox and automation platform for AI coding agents.

This repo teaches coding agents how to use Islo for:

- **Factory lines**: multi-stage orchestration with typed transitions, integration triggers, and `islo factory line-run` controls
- **Harness and model selection**: Codex (Islo inference), Claude, Cursor
- **Jobs**: lower-level durable stage execution units
- **Webhooks**: lower-level HTTP event ingress and egress
- **Knowledge**: tenant memories, skills, and rules for agent steps
- Sandbox lifecycle: create, connect, exec, pause, resume, stop, delete, snapshots, sharing
- Built-in agents: Claude Code, Cursor agent, and Codex inside Islo sandboxes
- Gateway integrations: GitHub, Slack, Islo inference, and provider credentials without copying tokens into the sandbox
- SDK usage: programmatic integrations with the generated Islo SDKs

For runnable automation templates, use [`islo-labs/islo-agents`](https://github.com/islo-labs/islo-agents). That repo contains concrete GitHub Actions wrappers, `job.toml` manifests, prompts, and the shared agent harness for PR review, CI babysitting, E2E verification, and task execution.

## Install

### Generic Skills installer

```bash
npx skills add islo-labs/skills
```

### Cursor

Cursor discovers this repo through `.cursor-plugin/marketplace.json`. Install it through Cursor's plugin marketplace flow, or point a local plugin install at this repo while developing.

The plugin includes an MCP server entry for the Islo docs:

```text
https://docs.islo.dev/_mcp/server
```

### Claude Code

Add the marketplace and install the plugin:

```text
/plugin marketplace add islo-labs/skills
/plugin install islo@islo-plugin
```

For local development, point Claude Code at the plugin root:

```text
plugins/islo
```

### Codex and other agents

Agents that support the common plugin layout can load `plugins/islo`. Agents that only support skills can install with `npx skills add` and configure the docs MCP server manually:

```json
{
  "mcpServers": {
    "islo-docs": {
      "url": "https://docs.islo.dev/_mcp/server"
    }
  }
}
```

## Contents

```text
plugins/islo/skills/using-islo/
├── SKILL.md
├── automations.md          # Factory-first automation guide
├── factory.md              # line.toml, transitions, triggers, line-run
├── agents-and-inference.md # harness, model, Islo inference
├── jobs.md                 # lower-level job.toml reference
├── webhooks.md             # lower-level incoming/outgoing webhooks
├── knowledge.md            # tenant knowledge items
├── sandbox-lifecycle.md
├── gateway-integrations.md
├── sdk.md
└── templates.md
```

Start with `SKILL.md`. It loads the focused references only when the user asks about that part of Islo.

## Updating skills in sandboxes

Skills are baked into the `islo-runner` image at build time and seeded into the workspace on first boot. Pushing to this repo does **not** automatically update existing sandboxes.

To ship updates:

1. Merge changes to `islo-labs/skills` on GitHub.
2. Rebuild `ghcr.io/islo-labs/islo-runner:latest` (daily cron or manual `workflow_dispatch` in bear-agent).
3. New sandboxes get the updated skill on first boot.

To update an existing sandbox manually:

```bash
cd /workspace
npx skills add islo-labs/skills -y --copy --all
```

## Development

Keep the skill concise and move details into one-level reference files. Before publishing, validate JSON and check that the expected terms are present:

```bash
python -m json.tool .mcp.json
python -m json.tool .cursor-plugin/marketplace.json
python -m json.tool .claude-plugin/plugin.json
python -m json.tool .claude-plugin/marketplace.json
python -m json.tool .agents/plugins/marketplace.json
python -m json.tool plugins/islo/plugin.json
python -m json.tool plugins/islo/.cursor-plugin/plugin.json
python -m json.tool plugins/islo/.claude-plugin/plugin.json
python -m json.tool plugins/islo/.codex-plugin/plugin.json
rg "https://docs.islo.dev/_mcp/server|using-islo|factory|islo factory|islo knowledge|islo webhook|islo job|islo use|@islo-labs/sdk|islo-agents" .
```
