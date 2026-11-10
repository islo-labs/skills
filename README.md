# Islo Skills

Agent skills and plugin metadata for working with [Islo](https://islo.dev), the sandbox and automation platform for AI coding agents.

This repo teaches coding agents how to use Islo for:

- **Factories**: Machines provide the environment, Agents define execution and prompts, and Lines orchestrate Agent-backed stages with typed transitions and integration triggers
- **Run surfaces**: publish live web and terminal interfaces from line-run stage sandboxes
- **Harness and model selection**: pair Codex / Claude / Cursor to the matching catalog and host (not one shared model list)
- **Webhooks**: lower-level HTTP event ingress and egress
- **Knowledge**: tenant memories and declarative policies for Agents and Managers
- Sandbox lifecycle: create, connect, exec, pause, resume, stop, delete, snapshots, sharing
- Built-in agents: Claude Code, Cursor agent, and Codex inside Islo sandboxes
- Gateway integrations: GitHub, Slack, Islo inference, and provider credentials without copying tokens into the sandbox
- SDK usage: programmatic integrations with the generated Islo SDKs

For runnable automation templates, use [`islo-labs/islo-agents`](https://github.com/islo-labs/islo-agents). That repo owns complete runnable Agent and Line manifests, prompts, and manifest validation. This skill repository keeps only focused syntax fragments.

## Factories

Start with Machine and Agent inventory, then design the Line. Use `islo schema agent --short` to author reusable Agents. Validate with `islo agent validate`, then save with `islo agent create` or `islo agent update`. Use `islo schema factory --short` to author and validate `line.toml` stages that reference those Agents with `agent = "..."`.

Machines own repositories, environment, gateway profile, and lifecycle. Agents own prompts and supported harness, model, provider, Skills, and MCP settings. Lines own stage params and outputs, routing, triggers, limits, and optional overrides. Verify an Agent through a minimal manual Line run, then inspect its line-run status, stages, and events before testing the approved trigger.

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

The plugin ships four skills:

```text
plugins/islo/skills/
├── factory-lines/            # TASK skill: create and operate factory lines
│   ├── SKILL.md              # router + iron rules
│   ├── references/           # create-a-line workflow, machines, question shape,
│   │                         # manifest anatomy, triggers, run control, harness/model
│   └── scripts/              # validate_commands.sh
├── line-manager-recovery/    # TASK skill: Line Manager policy for failed stages
│   └── SKILL.md              # read by the Line Manager on stage failures
├── surfaces/                 # TASK skill: publish live line-run interfaces
│   ├── SKILL.md              # router
│   └── references/           # target-specific readiness and safety
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
python3 scripts/validate_surfaces_skill.py
python3 scripts/test_validate_surfaces_skill.py
bash scripts/sync_plugin_manifests.sh --check
bash plugins/islo/skills/factory-lines/scripts/validate_commands.sh
```

The canonical plugin manifest is `plugins/islo/.claude-plugin/plugin.json`; edit it and run `scripts/sync_plugin_manifests.sh` to refresh the per-platform copies.

## Release

1. Bump `version` in `plugins/islo/.claude-plugin/plugin.json` and sync the copies.
2. Merge to `islo-labs/skills` on GitHub.
3. Rebuild `ghcr.io/islo-labs/islo-runner:latest` so new sandboxes ship the new skills (the installed cache lags until this happens).
