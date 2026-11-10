# Factory links in Agent chat

This reference describes Markdown links that display Factory objects inline in Agent chat. The link displays existing data. A question link does not create a question or grant permission to ask one. The [question reference](questions.md) defines that separate request shape and permission contract.

## Link shape

A supported link on its own paragraph, with a `view` query argument, renders an embed:

```markdown
[Release run](/factories/team-key/runs/lines/019c0000-0000-7000-8000-000000000001?view=card)
```

The Factory reference, run UUID, Line name, and Knowledge slug come from actual resource reads. The values above illustrate the shape. URL-encode each path segment and query value.

The prefix `/factories/<factory-ref>` explicitly selects a Factory by its key or public UUID. The prefix `/factory` inherits the surrounding chat's Factory scope. An explicit prefix selects that Factory even when the chat belongs to another Factory. Navigation retains that scope.

## Supported views

Append these paths to either prefix:

| Object | Path | `view` | Content |
|---|---|---|---|
| Run | `/runs/lines/<run-id>` | `inbox` | Compact row with its question, stop reason, or artifacts |
| Run | `/runs/lines/<run-id>` | `card` | Stages, status, and cost |
| Run question | `/runs/lines/<run-id>` | `question` | Stored structured question and answer controls |
| Run list | `/runs` | `inbox`, `table` | Filtered runs |
| Line | `/lines/<line-name>` | `card` | Line details |
| Line list | `/lines` | `table` | Filtered Lines |
| Knowledge item | `/knowledge/<slug>` | `card` | Referenced content; images remain media |
| Knowledge list | `/knowledge` | `table` | Filtered Knowledge |

A question view reflects the stored run state. An answered question clears after an accepted write. A cancelled run's question is read-only, with a cancellation notice and no send action. A run with no open question displays that state.

## List filters

Lists default to five items. The `limit` query argument is bounded to 1 through 10.

| List | Filters |
|---|---|
| Runs | `status` and `name` accept comma-separated values; `q`, `waiting_for_answer=true`, `mine=true` |
| Lines | `q`, `trigger` |
| Knowledge | `q`, `level`, `tag` |

For example, a filtered Line table uses this shape:

```markdown
[Release Lines](/factories/team-key/lines?view=table&q=release&trigger=manual&limit=5)
```

**Show all** opens the same Factory page with the same filters. It removes the chat-only `view` and `limit` arguments.

## Ordinary references

Links inside sentences, multiple links in one paragraph, list-item links, links without `view`, and `view=chip` keep their ordinary link or chip rendering. Unsupported views and external URLs do not become embeds. A standalone link in shared Markdown outside Agent chat also keeps ordinary rendering.

This guidance belongs to the installed skill and its references. Saved Agent prompts remain unchanged when chat sessions launch.
