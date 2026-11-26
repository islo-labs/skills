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
islo factory triggers get linear issue.labeled
```

`triggers get` returns the event's payload shape, selector shape, and example filters for that provider. The selector scopes which resources fire the line (channels, repositories, issues); filters drop unwanted payloads with the condition AST; trigger outputs bind payload paths to line inputs. All three appear in the full example in `line-manifest.md`.

After `triggers get`, ask the user which resource to scope to. Do not copy team, project, channel, repository, or `scope = "all"` from a nearby line.

| Provider | Ask |
|----------|-----|
| Linear | Team, project, and any label/state filter (or all issues in that team/project) |
| GitHub | Owner/repo (and which event) |
| Slack | Workspace and channel |

Check providers used by triggers and tools with the [integrations skill](../../integrations/SKILL.md#check-connection-status). Follow the [chat connection gate](chat-embeds.md#integration-connect-cards) for cards and waiting.

### Linear label-only selection

Check the current catalog and `islo schema factory --short` before choosing an event. The catalog inspected for these examples exposes `issue.updated` and `issue.labeled`; do not assume `issue.created` is a deployable catalog entry just because Linear sends create webhooks.

The Linear matcher treats `scope = "all"` as an immediate selector match: it ignores `labels`, `team_ids`, `project_ids`, and `states`. Those fields constrain issues only with `scope = "selected"`. Under selected scope, populated dimensions combine with AND; alternatives within each list combine with OR. Empty lists add no constraint. Labels match IDs or names case-insensitively. Trigger `filters` are separate payload conditions, all of which must pass; setting a selector label is not a filter on an all-issues selector.

**Bad, reported from a chat-created Line:** the labels look restrictive, but this selector admits unlabeled issues too (subject to the event and any separate filters).

```toml
[trigger.selector]
kind = "issue"
provider = "linear"
scope = "all"
labels = ["islo"]
project_ids = []
states = []
team_ids = []
```

**Fixed for "start once when an issue is created with, or gains, label islo":** choose `issue.labeled` and selected scope. No team/project criteria are needed for a label-only request. Ask before adding them.

```toml
[trigger]
type = "integration_trigger"
provider = "linear"
name = "issue.labeled"

[trigger.selector]
kind = "issue"
provider = "linear"
scope = "selected"
labels = ["islo"]

[trigger.outputs]
issue_id = { type = "trigger_path", path = "trigger.raw.data.identifier" }
```

`issue.labeled` handles creation with a matching label and additions of a matching label, once per issue/subscription. It does not fire for unrelated updates while the issue merely retains the label. For every update to an already labeled issue, use `issue.updated` with the same selected selector. For creation only, keep `issue.labeled` and add a `trigger.filters` equality condition on `$.action` against literal `create`. For an update-only label-addition workflow, the existing `issue.updated` pattern uses an `exists` filter on `$.updatedFrom.labelIds`; that opts the selector into checking added labels rather than all current labels. Do not copy that filter when you want ordinary updates of labeled issues.

Validate the **whole** draft, including outputs and transitions. Schema validation alone does not establish that the selector expresses the user's intent. Before enabling automatic effects, check representative payloads against the matcher:

| Case for the fixed `issue.labeled` trigger | Expected |
|---|---|
| Create an issue with label `islo` | Match |
| Create an issue without labels, or with only `other` | No match |
| Add `islo` to an existing unlabeled issue | Match |
| Update a title while retaining `islo`, or remove `islo` | No match |

Use the catalog payload shape (`type = "Issue"`, `data.id`, `data.labels` objects with `id` and `name`, and `updatedFrom.labelIds` for updates). Use synthetic local fixtures first. A documentation edit never authorizes deploying a Line or creating/changing real provider issues. See [the complete checklist and examples](line-best-practices.md).

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

After the blueprint and expected effects are approved, deploy and fire one approved positive event and watch it arrive:

```bash
islo factory line-run list --line <name> --paged --limit 20
islo factory triggers list
```

Wait for the run started by your test event using [Waiting for line runs you start](wait-for-line-runs.md), then continue with its outputs.

The one-real-event procedure with an approved expected-effects checklist is in `create-a-line.md` under End-to-end verification.

For a restrictive trigger, also verify a negative fixture (for example an unlabeled issue). A live negative test is a separate provider action: get approval for that action and for the accidental run effects if filtering is wrong. Observe the provider event and bounded run/event history to confirm no matching run, rather than treating an unobserved event as exclusion proof. When approval or provider access is unavailable, report the local fixture results and the live-verification limitation; do not emit events to complete a documentation check.
