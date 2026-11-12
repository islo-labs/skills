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

After the user approves the draft, check every provider the request needs, including both triggers and tools. Complete this gate before any create, update, or deploy command, including Factory, Machine, Environment, Agent, Job, and Line creation. Keep design and question turns free of connect cards; list the providers in the blueprint's Needs line instead.

1. Run `islo status -o json` and read `integrations`. A provider is connected when at least one matching entry has `connected: true` in the scope the request needs. If status omits scope and the provider requires one (for example Tenant for Cursor Jobs), run `islo api /integrations/PROVIDER_ID` and check that scope’s `connected` value; a personal connection cannot satisfy a Tenant requirement. A failed scope lookup is unknown. A reliable result without such an entry means the provider is missing. Do not send a card for a connected provider.
2. If a needed provider is missing, send its connect card, then wait for the user to say they are done. Do not create or deploy while waiting, or while any needed provider remains missing or pending owner approval.
3. After the user says done, run `islo status -o json` again. Continue only when all needed providers are connected. If a provider is still missing, explain that status and wait; do not repeat its card.

Treat status as **unknown** if the command fails, reports integration status unavailable (including a non-null `integrations_error`), or returns an empty `integrations` array with a null `auth.tenant_name` (called `tenant_name` in older output). Missing or malformed status fields are also unknown. This covers older CLIs and backends that hide lookup failures. Tell the user you could not check; send the card unless they say the provider is connected. Wait and re-check after they say done. When status remains unknown, the user's explicit confirmation that the provider is connected in the required scope is sufficient to continue; never override a reliable missing result with that fallback. Never claim a provider is connected without a positive status result or the user's word.

Send at most one card per provider per conversation, including retries and debugging. Put the link alone in its own paragraph. Do not add a notice-style lead-in such as “Linear is required:”. At most one plain sentence may tie the provider to the user's goal:

```markdown
To start from Linear labels, connect Linear.

[Linear](/integrations?connect=linear&view=connect)
```

Integrations belong to the tenant, so use `/integrations`, without a Factory prefix. Use a known preset id, such as `github`, `slack`, `linear`, `sentry`, `notion`, `atlassian`, `anthropic`, `cursor`, or `openai`. Unknown providers remain plain links. The same URL outside chat opens the dialog on the integrations page.

The browser card shows not connected, pending owner approval, or Connected with Tenant or Personal scope. Connect opens the existing dialog over chat. OAuth returns to the conversation, and the card refreshes on return and window focus. Browser refresh alone is not confirmation to resume work. Do not run `islo login --tool` in a sandbox. Use `islo factory triggers list` for the event catalog; `--with-status` is not the sandbox connection check.

When a trigger does not fire or a provider call fails, run `islo status -o json` and apply the same missing/unknown checks and card limit before retrying dependent work. A connection does not authorize provider events or external writes; those still require the approved effects checklist.

## Creation outcomes

After successfully creating or deploying an item, post exactly one card link for it, alone in its own paragraph. Use the name or ID returned by the CLI. For Factory resources, run `islo factory current --output json` with the same Factory selection used for the create or deploy, and use `factory.key`. The CLI does not print an app URL; build the URL from that key and the URL-encoded item name.

```markdown
[linear-standup](/factories/FACTORY_KEY/lines/linear-standup?view=card)
```

Use the same rule for Machines, explicitly requested standalone Jobs, and Knowledge items. Environments belong to the tenant: use their returned ID at `/settings/environments/ENVIRONMENT_ID?view=card`, with no Factory prefix. Do not post a success card when creation failed, repeat the same card in a list or sentence, or add follow-up suggestion chips.

Run it now opens the existing run dialog so the user can choose version, region, and inputs. A Line without an active version cannot run. Starting a Line from its card keeps the conversation open and shows run progress with Open run.
