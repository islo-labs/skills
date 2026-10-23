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
        {"id": "option-a", "label": "First option"},
        {"id": "option-b", "label": "Second option"}
      ]
    }
  ]
}
EOF
```

`LINE_RUN_ID` and `stage_name` come from the document that granted permission. Omit `stage_name` only when that document says to omit it.

A batch holds 1 to 10 questions. Each question has a stable `id`, a `kind`, and a `prompt`. Kinds are `single_choice`, `multi_choice`, and `text`. A choice has 2 to 8 options. Each option has a stable `id` and a `label`. Option ids are unique inside the question. Question ids are unique inside the batch. `required` defaults to true. A text question has no options.

Prefer `single_choice` and `multi_choice`. Use `text` only when the answer cannot be a choice. Do not put secrets, credentials, or private values in a prompt, an option, or a summary.

A bare string array cannot carry options. A string is stored as a text question and the choices are dropped. Send question objects.

A successful response contains a question ID. That ID confirms the question was recorded. If the post fails or returns no question ID, do not claim the question was asked. Follow the fallback the granting document specifies. If it specifies none, stop with the failure.

The example above is the request shape. The granting document decides `stage_name`, the question ids, the prompts, and the options.
