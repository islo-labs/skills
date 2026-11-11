---
name: islo-chat
description: Islo chat only. Use this skill only when the system prompt or the user explicitly says you are running inside Islo chat (the Islo web app Agent chat). Never use it in Cursor, Claude Code, Codex, a local terminal, or any other host.
---

# Islo chat

Behaviour that works only inside Islo chat: connection cards and object embeds rendered by the Islo web app, and the limits of the chat sandbox.

## Gate

Use this skill only when you were explicitly told you are inside Islo chat. If you were not told, stop reading. Nothing here applies, and the other Islo skills describe the correct local behaviour.

Do not infer chat from a sandbox, from `ISLO_*` environment variables, or from the repo you are in. The links below are relative paths that only the Islo chat renders. Anywhere else they are dead links.

## Precedence

Inside Islo chat, this skill overrides `factory-lines` and `platform` wherever they disagree. In particular, replace these instructions:

| Other skills say | In Islo chat do this |
|---|---|
| `islo login --tool <provider>` | Post a connection card for the provider |
| `islo status` or an integration status check | Post a connection card; the card shows the status |
| `islo factory triggers list --with-status` | Run `islo factory triggers list` and post a connection card for each provider the trigger needs |
| Connect GitHub before `--source` on a private repo | Post a GitHub connection card first |
| Connect Cursor at tenant level for jobs | Post a Cursor connection card and ask the user to choose Tenant scope |
| Ask the user to connect the provider locally | Post the connection card |

## Integration connection cards

The chat sandbox cannot read integration connection status. `islo login --tool`, `islo status`, and `islo factory triggers list --with-status` use status endpoints that reject sandbox callers. Do not run them inside the sandbox.

Before or alongside deploying a Line, post one card for every provider a trigger or tool needs. Say why it is needed in the paragraph before the link, then put the link alone in its own paragraph:

```markdown
Slack is needed to start this Line when a message arrives in the selected channel.

[Slack](/integrations?connect=slack&view=connect)
```

- The browser card reads the user's connection status and owns it: not connected, pending owner approval, or Connected with Tenant or Personal scope.
- Never claim a provider is connected from sandbox evidence.
- Ask the user to say when they are done, or offer to deploy now. Deployment does not check integration readiness, and the Line starts once its integration is connected.
- A connection is a capability, not authorization to send an event.
- Never ask for credentials in chat, and never put tokens in manifests, prompts, or sandbox env.

Use a known preset id for `connect`: `github`, `slack`, `linear`, `sentry`, `notion`, `atlassian`, `anthropic`, `cursor`, or `openai`. A provider without a preset, such as `gitlab` or `npm`, stays a plain link. Details are in [embeds.md](references/embeds.md#integration-connect-cards).

When a provider call fails (a 401, or `Repository not found` on a private repo), post the connection card, then check `islo gateway ls` and the gateway allow rules for the destination host.

## Object embeds

To show an existing Line, run, run question, or Knowledge item in chat, read [embeds.md](references/embeds.md) for the link shapes and views.
