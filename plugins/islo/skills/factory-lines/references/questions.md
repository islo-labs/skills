# Line-run questions

This page teaches the shape of a line-run question batch. It does not give you permission to ask.

## Permission

Post a question only when the document that sent you here says you may ask, names the line run, and names the decisions that are yours to ask. Reading this page is not that permission. A general request to talk to the user is not that permission. A Factory Machine, a line, or a job does not grant it unless its own document says you may ask.

When no document has granted permission, do not call the questions endpoint, do not invent a question, and do not park a run waiting for an answer. Say what you were going to ask and stop.

When a document has granted permission, ask only the decisions it names, in the batches it names. Use this page for the request body. Do not add a question it did not list.

## One batch

Put every question for the turn in one request. End the turn after a successful post. Do not ask the next batch in the same turn.

```bash
islo api --method POST --input - "/factories/$ISLO_FACTORY/line-runs/$ISLO_LINE_RUN_ID/questions" <<'EOF'
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

`ISLO_FACTORY` and `ISLO_LINE_RUN_ID` identify the current Factory and Line run. Job steps export both variables. `stage_name` comes from the document that granted permission. Omit `stage_name` only when that document says to omit it.

A batch holds 1 to 10 question objects. Each question has a stable `id`, a `kind`, and a `prompt`. Use `single_choice` or `multi_choice` with 2 to 8 options. Each option has a stable `id` and a `label`. Option ids are unique inside the question. Question ids are unique inside the batch. `required` defaults to true.

Keep each question prompt to 30 words or fewer. This is authoring guidance; the backend does not enforce a word limit.

On either choice kind, an option may set `selected` and `recommended`; both default to false. `selected: true` checks that option when the form opens. It does not submit an answer: the person still confirms or changes the selection. A `single_choice` may have at most one selected option; a `multi_choice` may have any number. `recommended: true` shows a Recommended tag and does not check the option. The flags are independent: an option may have either, both, or neither. Omit both for an unchecked option with no tag.

When the granting document allows the person to select nothing, post the `multi_choice` with `required: false`. An empty selection is a complete answer; do not add a `none` option for that case. Keep a single-choice `none` option when that question must have one answer.

Open-ended `text` questions are disabled. Both choice kinds automatically include an Other control where the person can enter their own answer. Do not add Other to the options array. A `multi_choice` answer can combine selected options with Other text. Do not put secrets, credentials, or private values in a prompt, an option, or a summary.

The API returns HTTP 400 for the old string-array format, including a batch that mixes strings and objects. Send question objects with options.

A successful response contains a question ID. That ID confirms the question was recorded. If the post fails or returns no question ID, do not claim the question was asked. Follow the fallback the granting document specifies. If it specifies none, stop with the failure.

The example above is the request shape. The granting document decides `stage_name`, the question ids, the prompts, and the options.
