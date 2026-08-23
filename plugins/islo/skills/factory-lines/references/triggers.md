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

Discover what exists and whether the tenant is connected before designing around one:

```bash
islo factory triggers list --with-status
islo factory triggers get slack message.received
islo factory triggers get github pull_request.opened
```

`triggers get` returns the event's payload shape, selector shape, and example filters for that provider. The selector scopes which resources fire the line (channels, repositories, issues); filters drop unwanted payloads with the condition AST; trigger outputs bind payload paths to line inputs. All three appear in the full example in `line-manifest.md`.

If the provider shows as not connected, connect it first (`islo login --tool slack`) and re-check with `--with-status`.

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
islo factory line-run status <run-id>
islo factory manager runs
islo factory triggers list --with-status
```

The one-real-event procedure with an expected-effects checklist is Phase 7 of `create-a-line.md`.
