---
name: platform
description: "Islo infrastructure reference: local skill and plugin installation, sandboxes, snapshots, gateway profiles, incoming webhooks, environments, knowledge, and the SDK. Use for installing Islo in Claude Code, Cursor, Codex, or another local agent, or when the user works with islo.yaml, islo use, sandboxes, snapshots, gateway credentials, or @islo-labs/sdk directly."
---

# Islo platform

Reference for Islo's infrastructure primitives. For automating workflows (factory lines, jobs, line runs, schedules, triggers), use the islo factory-lines skill instead.

Ground rules that apply everywhere:

- The installed CLI is the source of truth. Use `islo schema <command>` and `--help` for exact flags; do not write config shapes from memory.
- Claude Code, Cursor agent, and Codex are preinstalled in sandboxes. OpenCode is installed on first `islo use --agent opencode`. They run without in-sandbox auth when the matching integration (or Islo inference for OpenCode) is available.
- This skill runs inside Islo sandboxes and in the user's own agent. Some tenant commands are blocked inside a sandbox, and cards render only in Agent chat; see [where you are running](../factory-lines/SKILL.md#where-you-are-running).
- Provider tokens stay out of sandboxes; follow the [integrations skill](../integrations/SKILL.md#check-connection-status) for the connection check and the [chat connection gate](../factory-lines/references/chat-embeds.md#integration-connect-cards) for connect cards and waiting.

## Install Islo in your own agent

When the user asks to install locally, give the instructions for their agent. Skills preinstalled in an Islo sandbox do not install the plugin on the user's computer. These instructions ship with the skill; no GitHub search is needed.

### Claude Code

Run these commands in Claude Code on your computer:

```text
/plugin marketplace add islo-labs/skills
/plugin install islo@islo-plugin
```

For local plugin development, point Claude Code at the `plugins/islo` directory of a checkout of `islo-labs/skills`.

### Cursor

Install `islo-labs/skills` through Cursor's plugin marketplace flow. Cursor discovers the repository through `.cursor-plugin/marketplace.json`. For local development, point a local plugin install at that repository. The plugin includes the Islo docs MCP server.

### Codex and other agents

Agents that support the common plugin layout can load `plugins/islo` from a checkout of `islo-labs/skills`. For agents that support skills only, use the generic installer in a local terminal:

```bash
npx skills add islo-labs/skills
```

For a skills-only install, configure the docs MCP server manually:

```json
{
  "mcpServers": {
    "islo-docs": {
      "url": "https://docs.islo.dev/_mcp/server"
    }
  }
}
```

The docs MCP URL is `https://docs.islo.dev/_mcp/server`. Use the agent's MCP configuration format if it differs from this example.

## Waiting for line runs you start

If you start a Line run for an interactive task through the SDK or a webhook, follow [Waiting for line runs you start](../factory-lines/references/wait-for-line-runs.md). Read its result and continue the original task in the same chat.

## Where to go

| Topic | Read |
|-------|------|
| Create, connect, exec, pause, resume, delete sandboxes; `islo use`; `islo.yaml`; environments; sessions; snapshots and the snapshot-src pattern | `references/sandboxes-and-snapshots.md` |
| Gateway profiles, provider integrations, phantom tokens, GitHub, Slack, Islo inference routing, credential troubleshooting | `references/gateway-integrations.md` |
| Incoming webhooks (HTTP event to sandbox or single job) and the TypeScript/Python SDKs | `references/webhooks-and-sdk.md` |
| Knowledge items: CRUD, levels, repo and tag links, rendering | `references/knowledge.md` |
