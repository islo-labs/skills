# Triggers

What starts a line run, and how to pick and wire it. Field shapes live in `line-manifest.md`; confirm against `islo schema factory --short`.

## Choosing

| Trigger | Use when |
|---------|----------|
| `manual` | An operator or the API starts runs; also the right first trigger while a line is under test |
| `schedule` | Recurring cron-based runs |
| `webhook` | An external HTTP POST to a line-owned path starts runs |
| `integration_trigger` | Provider-native GitHub, Slack, or Linear events start runs |

## Integration triggers

Discover the event catalog before designing around a trigger:

```bash
islo factory triggers list
islo factory triggers get slack message.received
islo factory triggers get github pull_request.opened
islo factory triggers get linear issue.updated
```

`triggers get` returns the event's payload shape, selector shape, and example filters for that provider. The selector scopes which resources fire the line (channels, repositories, issues); filters drop unwanted payloads with the condition AST; trigger outputs bind payload paths to line inputs. All three appear in the full example in `line-manifest.md`.

After `triggers get`, ask the user which resource to scope to. Do not copy team, project, channel, repository, or `scope = "all"` from a nearby line.

| Provider | Ask |
|----------|-----|
| Linear | Team, project, and any label/state filter (or all issues in that team/project) |
| GitHub | Owner/repo (and which event) |
| Slack | Workspace and channel |

Before or alongside deploying, post one connect card for every provider the trigger or its tools need. Explain why each provider is needed, then put its link alone in a paragraph:

```markdown
[Slack](/integrations?connect=slack&view=connect)
```

Use the provider id in `connect`, such as `github`, `slack`, `linear`, or `sentry`. See [chat-embeds.md](chat-embeds.md) for the full link contract.

The browser card resolves the user's connection status. The agent cannot check it: `islo status`, `islo login --tool`, and `triggers list --with-status` use status endpoints that reject sandbox callers. Never claim a provider is connected. Ask the user to say when done, or offer to deploy now; the line starts once its required integration is connected. Deploying a line does not validate its integration.

## Schedules

A scheduled line declares cron and timezone in the manifest `[trigger]` and nowhere else:

```toml
[trigger]
type = "schedule"
cron = "0 7 * * *"
timezone = "UTC"
```

The manifest is the source of truth. A schedule created or edited outside it is reverted by the next line deploy, so treat "schedule reverted" as the symptom of exactly this mistake.

## Line webhook trigger vs incoming webhook

Two different products:

| | Line webhook trigger | Incoming webhook |
|--|---------------------|------------------|
| Setup | `[trigger] type = "webhook"` in line.toml | `islo webhook incoming create` |
| Target | Starts a line run | Sandbox lifecycle or a single job |
| Use when | Multi-stage orchestration | Simple event to sandbox or job |

Incoming webhooks are covered in the platform skill. For anything multi-stage, use a line trigger.

## Verifying a trigger end to end

Deploy, then fire ONE real event and watch it arrive:

```bash
islo factory line-run list --line <name>
islo factory triggers list
```

The one-real-event procedure with an approved expected-effects checklist is in `create-a-line.md` under End-to-end verification.
