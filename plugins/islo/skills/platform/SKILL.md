---
name: platform
description: "Islo infrastructure reference: sandboxes, snapshots, gateway profiles, incoming webhooks, environments, knowledge, and the SDK. Use when the user works with islo.yaml, islo use, sandboxes, snapshots, gateway credentials, or @islo-labs/sdk directly."
---

# Islo platform

Reference for Islo's infrastructure primitives. For automating workflows (factory lines, jobs, line runs, schedules, triggers), use the islo factory-lines skill instead.

Ground rules that apply everywhere:

- The installed CLI is the source of truth. Use `islo schema <command>` and `--help` for exact flags; do not write config shapes from memory.
- Claude Code, Cursor agent, and Codex are preinstalled in sandboxes. OpenCode is installed on first `islo use --agent opencode`. They run without in-sandbox auth when the matching integration (or Islo inference for OpenCode) is available.
- Provider tokens stay out of sandboxes. Post one standalone `[Provider](/integrations?connect=PROVIDER_ID&view=connect)` card for every provider a trigger or tool needs, before or alongside deploying. The browser card owns connection status. Never claim a connection from sandbox evidence. See [gateway-integrations.md](references/gateway-integrations.md) for the flow.
- Do not run `islo login --tool`, `islo status`, or `islo factory triggers list --with-status` inside a sandbox. Use `islo factory triggers list` for the event catalog.

## Where to go

| Topic | Read |
|-------|------|
| Create, connect, exec, pause, resume, delete sandboxes; `islo use`; `islo.yaml`; environments; sessions; snapshots and the snapshot-src pattern | `references/sandboxes-and-snapshots.md` |
| Gateway profiles, provider integrations, phantom tokens, GitHub, Slack, Islo inference routing, credential troubleshooting | `references/gateway-integrations.md` |
| Incoming webhooks (HTTP event to sandbox or single job) and the TypeScript/Python SDKs | `references/webhooks-and-sdk.md` |
| Knowledge items: CRUD, levels, repo and tag links, rendering | `references/knowledge.md` |
