# Islo object links in Agent chat

Use this reference to show an existing Islo object inside an Agent chat reply. It teaches the link shape, like [questions.md](questions.md) teaches question shape. Keep the saved Agent prompt unchanged; do not append these instructions when launching a chat.

Write a Markdown link alone in its own paragraph to request an embed:

```markdown
[Run awaiting your answer](/factories/FACTORY_KEY/runs/lines/RUN_ID?view=question)
```

Replace `FACTORY_KEY`, `RUN_ID`, `LINE_NAME`, `MACHINE_NAME`, `JOB_NAME`, `ENVIRONMENT_ID`, and `SLUG` with values returned by Islo tools. Use the object's Factory key, including when it differs from the surrounding chat's Factory. URL-encode path segments and filter values. An embed link reads an existing object; it does not create a run, post a question, or grant permission to act.

## Supported views

| Object | URL | What appears |
|---|---|---|
| Integration | `/integrations?connect=linear&view=connect` | Provider logo, description, browser connection status, and Connect dialog |
| Line run | `/factories/FACTORY_KEY/runs/lines/RUN_ID?view=inbox` | Compact row with the current question, stop reason, or artifacts |
| Line run | `/factories/FACTORY_KEY/runs/lines/RUN_ID?view=card` | Run stages, status, and cost |
| Run question | `/factories/FACTORY_KEY/runs/lines/RUN_ID?view=question` | The stored question and answer form when the run accepts answers |
| Run list | `/factories/FACTORY_KEY/runs?view=inbox` | Run rows; `view=table` also works |
| Line | `/factories/FACTORY_KEY/lines/LINE_NAME?view=card` | Line details, next run or Manual, and Run it now |
| Machine | `/factories/FACTORY_KEY/machines/MACHINE_NAME?view=card` | Level, last build, version, and capabilities; plain link when Machines are disabled |
| Environment | `/settings/environments/ENVIRONMENT_ID?view=card` | Variable and secret counts and default status |
| Job | `/factories/FACTORY_KEY/jobs/JOB_NAME?view=card` | Schedule, last run, version, Machine, and Run it now |
| Line list | `/factories/FACTORY_KEY/lines?view=table` | Lines table |
| Knowledge item | `/factories/FACTORY_KEY/knowledge/SLUG?view=card` | Stored content; images remain media |
| Knowledge list | `/factories/FACTORY_KEY/knowledge?view=table` | Knowledge table |

Resolve the object's Factory with `islo factory current --factory KEY_OR_UUID --output json` and use `factory.key` in the URL. Select the Factory that owns the object, even when it differs from the surrounding chat. Never emit a legacy singular-Factory URL, substitute a UUID for the key, or infer the Factory from the current conversation. App-relative links and `https://app.islo.dev` URLs are supported.

If the key cannot be resolved, keep a known explicit URL as a badge by omitting `view` or using `view=chip`. Do not request a run-list card, guess a key, or generate an ambiguous URL. If there is no known explicit URL, describe the run in text until its Factory is identified. Historical ambiguous run links remain badges in the app.

Inline links inside sentences, multiple links in one paragraph, links without `view`, `view=chip`, unsupported views, and external URLs remain ordinary references. List-item links remain ordinary references in tight, loose, and nested lists; blank lines between list items do not request embeds. Shared Markdown outside Agent chat also keeps ordinary rendering.

An accepted answer clears the stored question from the embed. A cancelled run's question is read-only, with a cancellation notice and no send action. A run with no open question displays that state.

## List filters

List embeds default to 5 items. Add `limit=1` through `limit=10` to choose a smaller or larger list. Values outside that range are clamped. Show all opens the destination page with the same filters and removes `view` and `limit`.

| List | Filters |
|---|---|
| Runs | `status` and `name` accept comma-separated values; `q`, `waiting_for_answer=true`, and `mine=true` also work |
| Lines | `q` and `trigger` |
| Knowledge | `q`, `level`, and `tag` |

For example, show up to three matching runs awaiting answers:

```markdown
[Release runs awaiting answers](/factories/FACTORY_KEY/runs?view=inbox&name=release&q=approval&waiting_for_answer=true&limit=3)
```

To ask a new question, follow the permission and request-body rules in [questions.md](questions.md). A `view=question` link only displays a question already stored on the referenced run.

## Integration connect cards

Post one card for each provider a line trigger or tool needs, before or alongside deployment. State why it is needed in the paragraph before its link:

```markdown
Slack is needed to start this line when a message arrives in the selected channel.

[Slack](/integrations?connect=slack&view=connect)
```

Integrations belong to the tenant, so use `/integrations`, without a Factory prefix. Only known preset ids render cards; unknown providers remain plain links. The same URL outside chat opens the dialog on the integrations page.

The browser reads the user's status: not connected, pending owner approval, or Connected with Tenant or Personal scope. Connect opens the existing dialog over chat. OAuth returns to the conversation, and the card refreshes on return and window focus.

The sandbox cannot read integration status. Never claim a provider is connected from sandbox evidence. Do not run `islo login --tool` in a sandbox. Ask the user to say when done, or offer to deploy now; the line starts once its required integration is connected.

## Creation outcomes

After successfully creating or deploying an item, post exactly one card link for it, alone in its own paragraph. Use the name or ID returned by the CLI. For Factory resources, run `islo factory current --output json` with the same Factory selection used for the create or deploy, and use `factory.key`. The CLI does not print an app URL; build the URL from that key and the URL-encoded item name.

```markdown
[linear-standup](/factories/FACTORY_KEY/lines/linear-standup?view=card)
```

Use the same rule for Machines, explicitly requested standalone Jobs, and Knowledge items. Environments belong to the tenant: use their returned ID at `/settings/environments/ENVIRONMENT_ID?view=card`, with no Factory prefix. Do not post a success card when creation failed, repeat the same card in a list or sentence, or add follow-up suggestion chips.

Run it now opens the existing run dialog so the user can choose version, region, and inputs. A Line without an active version cannot run. Starting a Line from its card keeps the conversation open and shows run progress with Open run.
