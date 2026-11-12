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

## Line draft cards

Before approval, present the complete blueprint as exactly one fenced `islo-line-draft` JSON block per draft. The draft has no stored object or URL. Keep the block free of links, buttons, Connect actions, and connection status claims. The browser validates it with zod and renders a read-only card; invalid JSON or an invalid shape stays an ordinary code block. While the block streams, the browser shows "Drafting the line...".

```islo-line-draft
{
  "draft": 1,
  "title": "Polish a Linear ticket",
  "description": "Rewrites a labeled ticket into an implementation-ready one.",
  "line": "linear-ticket-polisher",
  "starts_when": {
    "provider": "linear",
    "text": "A Linear ticket is labeled \"Islo-check-my-ticket\"",
    "scope": "Any team or project"
  },
  "steps": [
    {
      "agent": "polish-and-rewrite",
      "kind": "prompt",
      "model": "codex",
      "origin": "new",
      "purpose": "Reads the ticket and the repos, rewrites the description."
    }
  ],
  "shared_workspace": [],
  "manager": "built-in",
  "on_failure": "The run stops and is marked failed.",
  "runs_on": {
    "factory": {
      "name": "polish-factory",
      "origin": "existing"
    },
    "machine": {
      "name": "islo-dev",
      "origin": "existing"
    }
  },
  "creates": [
    "1 agent",
    "1 line"
  ],
  "reuses": [],
  "needs": [
    "linear"
  ],
  "you_get": {
    "result": "A rewritten ticket description",
    "writes": "Writes to Linear: the description, and removes the label.",
    "max_cost_usd": 2,
    "max_minutes": 30
  },
  "details": {
    "repos": [
      "acme/web",
      "acme/api"
    ],
    "environment": {
      "name": "dev-env",
      "origin": "existing"
    },
    "gateway": {
      "name": "linear-profile",
      "host": "api.linear.app",
      "auth": "Linear OAuth",
      "origin": "existing"
    },
    "size": "medium",
    "flow": "label added → polish-and-rewrite → done; on failure → run failed",
    "retained_resources": [
      "dev-env environment",
      "linear-profile gateway profile",
      "provider connections"
    ]
  },
  "assumed": [
    "starts_when.scope",
    "you_get.max_cost_usd"
  ],
  "updated": []
}
```

Field rules:

- `draft` starts at 1 and increases by one on each revision. Keep `line` stable for revisions of the same proposal. `title` and `description` explain the outcome.
- `starts_when.text` is a readable trigger sentence; `scope` includes the resolved selector scope, or the schedule and timezone for a scheduled Line. `provider` is optional for manual and schedule triggers.
- Each `steps` entry has `agent`, `kind` (`script`, `decision`, or `prompt`), `origin` (`new` or `existing`), and a one-line `purpose`. Prompt steps also require `model`; Script and Decision steps omit it. Include the semantic input and output in the purpose when useful. Steps follow execution order.
- `shared_workspace` contains groups of at least two distinct, one-based step numbers, such as `[[1, 2]]`. Every number must refer to a step in this draft. Omit notes for isolated steps by using `[]`.
- `manager` is `built-in` unless a named reusable Manager is justified. `on_failure` describes the failure path and any retry behavior.
- `runs_on.factory` and `runs_on.machine` are always present, each with `name` and `origin`. Never silently create a Factory. `creates` lists every new resource and `reuses` lists reused Agents and other resources.
- `needs` contains provider ids only. Never send a status, a connection object, or a claim that a provider is connected. The browser reads live connection status with the user's session.
- `you_get.result` states the done condition. Every external write goes in `you_get.writes`, including provider events and any test run that writes outside Islo. Say "No external writes" when there are none. A test run with no external effect needs no mention. `max_cost_usd` is a nonnegative number and `max_minutes` is a positive number; these are caps per run.
- `details` contains `repos`, `environment` (`name`, `origin`), `gateway` (`host`, `auth`, `origin`, and optional profile `name`), `size`, and `flow` including the failure path. Optional `model` can describe the model configuration; otherwise the browser uses the Prompt step models. `retained_resources` lists tenant-wide environments, gateway profiles, and connections that deleting the Factory keeps. Put relevant capabilities, lifecycle, readiness, ownership, instructions, Skills, MCP hosts, and semantic contracts into the corresponding concise descriptions. Do not expose credentials.
- `details_expanded` is optional and defaults to false. Set it to true in a full revised draft when the user asks to see Details. This is a native open/closed section, with no button.
- `assumed` lists every guessed field path, such as `starts_when.scope` or `you_get.max_cost_usd`. `updated` lists all paths changed since the previous draft. Use dot-separated paths and zero-based array indexes, such as `steps.0.purpose`. Both arrays are required; use `[]` when empty.
- Do not add unlisted fields. Required strings are nonempty. The frontend owns the header, section titles, footer, numbering, and fold: at six or more steps it shows the first two, a visible "N more steps" row, and the last two with their actual numbers.

After the card, wait for the user to write "approve". On a change request, answer in one sentence and post a full new card with `draft` increased by one and `updated` filled in. Never edit or repeat the old card. The frontend automatically collapses earlier drafts with the same `line` to "Draft 1 · superseded by draft 2"; the agent does not send that row. If the name changes, keep the proposal's `line` identity stable until approval and describe the requested final name in the title or description.

The sequence is draft card, "approve", integration check, a connect card only for missing providers, then creation once connected. The draft's Needs section replaces connect cards during design. Follow the [integration connection gate](#integration-connect-cards) after approval. Do not create, deploy, send provider events, or write externally before approval.

## Integration connect cards

After the user approves the draft, check every provider the request needs, including both triggers and tools. Complete this gate before any create, update, or deploy command, including Factory, Machine, Environment, Agent, Job, and Line creation. Keep design and question turns free of connect cards; list the providers in the blueprint's Needs line instead.

Before starting the gate, confirm that the blueprint has no unanswered choices or required selectors. Approval does not fill in an unresolved trigger label, team, channel, or destination. If the user approves an incomplete draft, ask for the missing answers without connect cards, then incorporate the answers and confirm the complete blueprint's approval before checking connections. Keep any further design question in its own turn, before the connection gate.

1. Run `islo status -o json` and read `integrations`. A provider is connected when at least one matching entry has `connected: true` in the scope the request needs. If status omits scope and the provider requires one (for example Tenant for Cursor Jobs), run `islo api /integrations/PROVIDER_ID` and check that scope’s `connected` value; a personal connection cannot satisfy a Tenant requirement. A failed scope lookup is unknown. A reliable result without such an entry means the provider is missing. Do not send a card for a connected provider.
2. If a needed provider is missing, check whether its card already appeared in an earlier assistant reply in this conversation. If it has, refer to that earlier card in plain text, such as "Use the Slack card above to reconnect." Do not emit another connect link. Otherwise, send its card and remember the provider ID as already shown. In either case, wait for the user to say they are done. Do not create or deploy while waiting, or while any needed provider remains missing or pending owner approval.
3. After the user says done, run `islo status -o json` again. Continue only when all needed providers are connected. If a provider is still missing, explain that status and wait; do not repeat its card.

Treat status as **unknown** if the command fails, reports integration status unavailable (including a non-null `integrations_error`), or returns an empty `integrations` array with a null `auth.tenant_name` (called `tenant_name` in older output). Missing or malformed status fields are also unknown. This covers older CLIs and backends that hide lookup failures. Tell the user you could not check. Unless they say the provider is connected, use step 2 to send its first card or refer to its earlier card. Wait and re-check after they say done. When status remains unknown, the user's explicit confirmation that the provider is connected in the required scope is sufficient to continue; never override a reliable missing result with that fallback. Never claim a provider is connected without a positive status result or the user's word.

Send at most one card per provider per conversation, including retries and debugging. Track the provider IDs whose cards have appeared across the whole conversation, and preserve them in any conversation summary. Successful connection, creation, deployment, and later disconnection never clear that history. A provider becoming missing again changes its connection status, not whether its card was already shown. Put a first card's link alone in its own paragraph. Do not add a notice-style lead-in such as “Linear is required:”. At most one plain sentence may tie the provider to the user's goal:

```markdown
To start from Linear labels, connect Linear.

[Linear](/integrations?connect=linear&view=connect)
```

Integrations belong to the tenant, so use `/integrations`, without a Factory prefix. Use a known preset id, such as `github`, `slack`, `linear`, `sentry`, `notion`, `atlassian`, `anthropic`, `cursor`, or `openai`. Unknown providers remain plain links. The same URL outside chat opens the dialog on the integrations page.

The browser card shows not connected, pending owner approval, or Connected with Tenant or Personal scope. Connect opens the existing dialog over chat. OAuth returns to the conversation, and the card refreshes on return and window focus. Browser refresh alone is not confirmation to resume work. Do not run `islo login --tool` in a sandbox. Use `islo factory triggers list` for the event catalog; `--with-status` is not the sandbox connection check.

When a trigger does not fire or a provider call fails, run `islo status -o json` and apply the same missing/unknown checks before retrying dependent work. If the provider needs reconnection, check its card history using step 2, even after a successful deployment. Refer to an earlier card in plain text when one exists; otherwise send its first card. Wait for confirmation and a status recheck before retrying. A connection does not authorize provider events or external writes; those still require the approved effects checklist.

## Creation outcomes

After successfully creating or deploying an item, post exactly one card link for it, alone in its own paragraph. Use the name or ID returned by the CLI. For Factory resources, run `islo factory current --output json` with the same Factory selection used for the create or deploy, and use `factory.key`. The CLI does not print an app URL; build the URL from that key and the URL-encoded item name.

```markdown
[linear-standup](/factories/FACTORY_KEY/lines/linear-standup?view=card)
```

Use the same rule for Machines, explicitly requested standalone Jobs, and Knowledge items. Environments belong to the tenant: use their returned ID at `/settings/environments/ENVIRONMENT_ID?view=card`, with no Factory prefix. Do not post a success card when creation failed, repeat the same card in a list or sentence, or add follow-up suggestion chips.

Run it now opens the existing run dialog so the user can choose version, region, and inputs. A Line without an active version cannot run. Starting a Line from its card keeps the conversation open and shows run progress with Open run.
