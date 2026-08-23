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

The plugin ships two skills:

```text
plugins/islo/skills/
├── factory-lines/            # TASK skill: create and operate factory lines
│   ├── SKILL.md              # router + iron rules
│   ├── references/           # create-a-line workflow, manifest anatomy, triggers,
│   │                         # run control and debugging, harness/model/knowledge
│   ├── templates/            # synced from islo-labs/islo-agents at a pinned ref
│   └── scripts/              # validate_commands.sh, validate_examples.sh, sync_templates.sh
└── platform/                 # REFERENCE skill: Islo infrastructure
    ├── SKILL.md
    └── references/           # sandboxes and snapshots, gateway integrations,
                              # webhooks and SDK, knowledge
```

Each SKILL.md is a router that loads a focused reference only when the task needs it.

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

Keep each SKILL.md a lean router and move details into one-level reference files. CI runs these; run them locally before publishing:

```bash
python3 scripts/validate_manifest_shapes.py
bash scripts/sync_plugin_manifests.sh --check
bash plugins/islo/skills/factory-lines/scripts/validate_commands.sh
bash plugins/islo/skills/factory-lines/scripts/validate_examples.sh
bash plugins/islo/skills/factory-lines/scripts/sync_templates.sh --check
```

The canonical plugin manifest is `plugins/islo/.claude-plugin/plugin.json`; edit it and run `scripts/sync_plugin_manifests.sh` to refresh the per-platform copies. Never hand-edit `factory-lines/templates/`; it is synced from islo-labs/islo-agents at the ref pinned in `templates/.pinned-ref`.

## Release

1. Bump `version` in `plugins/islo/.claude-plugin/plugin.json` and sync the copies.
2. Merge to `islo-labs/skills` on GitHub.
3. Rebuild `ghcr.io/islo-labs/islo-runner:latest` so new sandboxes ship the new skills (the installed cache lags until this happens).
