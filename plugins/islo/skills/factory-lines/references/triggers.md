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
islo factory triggers get linear issue.updated
```

`triggers get` returns the event's payload shape, selector shape, and example filters for that provider. The selector scopes which resources fire the line (channels, repositories, issues); filters drop unwanted payloads with the condition AST; trigger outputs bind payload paths to line inputs. Bind semantic Line inputs to Agent stage params through transitions. Complete runnable trigger manifests live in [islo-labs/islo-agents](https://github.com/islo-labs/islo-agents).

After `triggers get`, ask the user which resource to scope to. Do not copy team, project, channel, repository, or `scope = "all"` from a nearby line.

| Provider | Ask |
|----------|-----|
| Linear | Team, project, and any label/state filter (or all issues in that team/project) |
| GitHub | Owner/repo (and which event) |
| Slack | Workspace and channel |

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

## Line webhook triggers

`[trigger] type = "webhook"` starts a Line run at a Line-owned path. Its stages reference reusable Agents, which select the Machines used for execution. Incoming webhooks for sandbox lifecycle are a separate product covered by the platform skill.

## Verifying a trigger end to end

After the minimal manual Line check, deploy the approved trigger and send one approved event. Inspect the resulting run:

```bash
islo factory line-run list --line <name>
islo factory triggers list --with-status
islo factory line-run status <run-id>
islo factory line-run stages <run-id>
islo factory line-run events <run-id>
```

Confirm the event selected the intended Line and bound the expected Agent inputs. Check outputs and approved destinations when inference is available. Separate provider inference failures from trigger delivery failures.

The one-real-event procedure with an approved expected-effects checklist is in `create-a-line.md` under Verify the deployed trigger.
