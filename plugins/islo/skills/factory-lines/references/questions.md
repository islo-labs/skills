# Line-run questions

This page teaches the shape of a line-run question batch. It does not give you permission to ask.

## Permission

Post a question only when the document that sent you here says you may ask, names the line run, and names the decisions that are yours to ask. Reading this page is not that permission. A general request to talk to the user is not that permission. A Factory Machine, a line, or a job does not grant it unless its own document says you may ask.

When no document has granted permission, do not call the questions endpoint, do not invent a question, and do not park a run waiting for an answer. Say what you were going to ask and stop.

When a document has granted permission, ask only the decisions it names, in the batches it names. Use this page for the request body. Do not add a question it did not list.

## One batch

Put every question for the turn in one request. End the turn after a successful post. Do not ask the next batch in the same turn.

```bash
islo api --method POST --input - /factory/line-runs/LINE_RUN_ID/questions <<'EOF'
{
  "stage_name": "STAGE",
  "questions": [
    {
      "id": "choice-id",
      "kind": "single_choice",
      "prompt": "Prompt from the granting document",
      "options": [
        {"id": "option-a", "label": "First option", "selected": true},
        {"id": "option-b", "label": "Second option", "recommended": true}
      ]
    }
  ]
}
EOF
```

`LINE_RUN_ID` and `stage_name` come from the document that granted permission. Omit `stage_name` only when that document says to omit it.

A batch holds 1 to 10 questions. Each question has a stable `id`, a `kind`, and a `prompt`. Kinds are `single_choice`, `multi_choice`, and `text`. A choice has 2 to 8 options. Each option has a stable `id` and a `label`. Option ids are unique inside the question. Question ids are unique inside the batch. `required` defaults to true. A text question has no options.

On either choice kind, an option may set `selected` and `recommended`; both default to false. `selected: true` checks that option when the form opens. It does not submit an answer: the person still confirms or changes the selection. A `single_choice` may have at most one selected option; a `multi_choice` may have any number. `recommended: true` shows a Recommended tag and does not check the option. The flags are independent: an option may have either, both, or neither. Omit both for an unchecked option with no tag.

When the granting document allows the person to select nothing, post the `multi_choice` with `required: false`. An empty selection is a complete answer; do not add a `none` option for that case. Keep a single-choice `none` option when that question must have one answer.

Prefer `single_choice` and `multi_choice`. Use `text` only when the answer cannot be a choice. Do not put secrets, credentials, or private values in a prompt, an option, or a summary.

A bare string array cannot carry options. A string is stored as a text question and the choices are dropped. Send question objects.

A successful response contains a question ID. That ID confirms the question was recorded. If the post fails or returns no question ID, do not claim the question was asked. Follow the fallback the granting document specifies. If it specifies none, stop with the failure.

The example above is the request shape. The granting document decides `stage_name`, the question ids, the prompts, and the options.
