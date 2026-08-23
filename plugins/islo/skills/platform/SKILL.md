---
name: platform
description: "Islo infrastructure reference: sandboxes, snapshots, gateway profiles, incoming webhooks, environments, knowledge, and the SDK. Use when the user works with islo.yaml, islo use, sandboxes, snapshots, gateway credentials, or @islo-labs/sdk directly."
---

# Islo platform

Reference for Islo's infrastructure primitives. For automating workflows (factory lines, jobs, line runs, schedules, triggers), use the islo factory-lines skill instead.

Ground rules that apply everywhere:

- The installed CLI is the source of truth. Use `islo schema <command>` and `--help` for exact flags; do not write config shapes from memory.
- Claude Code, Cursor agent, and Codex are preinstalled in sandboxes and work without in-sandbox auth when the matching integration was connected first.
- Provider tokens stay out of sandboxes. Connect integrations with `islo login --tool <provider>` and let the `default` gateway profile inject credentials.

## Where to go

| Topic | Read |
|-------|------|
| Create, connect, exec, pause, resume, delete sandboxes; `islo use`; `islo.yaml`; environments; sessions; snapshots and the snapshot-src pattern | `references/sandboxes-and-snapshots.md` |
| Gateway profiles, provider integrations, phantom tokens, GitHub, Slack, Islo inference routing, credential troubleshooting | `references/gateway-integrations.md` |
| Incoming webhooks (HTTP event to sandbox or single job) and the TypeScript/Python SDKs | `references/webhooks-and-sdk.md` |
| Knowledge items: CRUD, levels, repo and tag links, rendering | `references/knowledge.md` |
