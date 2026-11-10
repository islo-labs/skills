# Islo object links in Agent chat

Use this reference to show an existing Islo object inside an Agent chat reply. It teaches the link shape, like [questions.md](questions.md) teaches question shape. Keep the saved Agent prompt unchanged; do not append these instructions when launching a chat.

Write a Markdown link alone in its own paragraph to request an embed:

```markdown
[Run awaiting your answer](/factories/FACTORY_ID/runs/lines/RUN_ID?view=question)
```

Replace `FACTORY_ID`, `RUN_ID`, `LINE_NAME`, and `SLUG` with values returned by Islo tools. Use the object's Factory ID, including when it differs from the surrounding chat's Factory. URL-encode path segments and filter values. An embed link reads an existing object; it does not create a run, post a question, or grant permission to act.

## Supported views

| Object | URL | What appears |
|---|---|---|
| Line run | `/factories/FACTORY_ID/runs/lines/RUN_ID?view=inbox` | Compact row with the current question, stop reason, or artifacts |
| Line run | `/factories/FACTORY_ID/runs/lines/RUN_ID?view=card` | Run stages, status, and cost |
| Run question | `/factories/FACTORY_ID/runs/lines/RUN_ID?view=question` | The stored question and answer form when the run accepts answers |
| Run list | `/factories/FACTORY_ID/runs?view=inbox` | Run rows; `view=table` also works |
| Line | `/factories/FACTORY_ID/lines/LINE_NAME?view=card` | One Line |
| Line list | `/factories/FACTORY_ID/lines?view=table` | Lines table |
| Knowledge item | `/factories/FACTORY_ID/knowledge/SLUG?view=card` | Stored content; images remain media |
| Knowledge list | `/factories/FACTORY_ID/knowledge?view=table` | Knowledge table |

The Factory reference can be its key or public UUID. The `/factory` prefix also works and inherits the surrounding Factory. Explicit Factory links keep that Factory for reads, answers, and navigation. Prefer an explicit prefix when the Factory is known. App-relative links and `https://app.islo.dev` URLs are supported.

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
[Release runs awaiting answers](/factories/FACTORY_ID/runs?view=inbox&name=release&q=approval&waiting_for_answer=true&limit=3)
```

To ask a new question, follow the permission and request-body rules in [questions.md](questions.md). A `view=question` link only displays a question already stored on the referenced run.
