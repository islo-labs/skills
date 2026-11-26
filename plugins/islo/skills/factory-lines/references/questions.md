# Line-run questions

Use this page when your instructions let you ask the person a question.
Every Line stage prompt and the Line Manager prompt do. If nothing in your
instructions lets you ask, say in your reply what you would ask, and stop.

## What the person sees

The question shows in the run's conversation, and in the chat that started
the run: the `briefing` as a message, then a small card with each prompt and
its options. The card adds Other for a custom answer.

Asking ends your turn, so your final reply is not shown. Put what the person
needs in `briefing`: the decision, the key facts and your recommendation, in a
few short lines. Link a ticket, PR or file for longer detail, such as a full plan.
Keep each prompt to one short question (30 words or fewer).

## Request

```bash
islo api -X POST "/factories/$ISLO_FACTORY/line-runs/$ISLO_LINE_RUN_ID/questions" --input - <<'EOF_JSON'
{
  "stage_name": "implement",
  "briefing": "The API checks pass. The UI review is still pending. I recommend waiting for that review.",
  "questions": [{
    "id": "review",
    "kind": "single_choice",
    "prompt": "Wait for the UI review?",
    "options": [
      {"id": "wait", "label": "Wait for review", "recommended": true},
      {"id": "continue", "label": "Continue now"}
    ]
  }]
}
EOF_JSON
```

`ISLO_FACTORY` and `ISLO_LINE_RUN_ID` identify the current Factory and Line run.
Use the `stage_name` from your instructions; omit it for a chat with no stages.

- Send 1 to 10 questions per request, each `single_choice` or `multi_choice` with 1 to 8 options. The card supplies Other automatically.
- `selected: true` pre-checks an option; `recommended: true` tags it. Neither answers it.
- Use `required: false` on a `multi_choice` when picking nothing is a valid answer.
- Put every question for this turn in one request, then end the turn.
- Keep secrets and private values out of questions.

The API rejects a malformed request and says what to fix.

## After asking

A response with a question id means it was recorded. If the request fails,
check the run's conversation before posting again, so you don't ask twice.
If recording cannot be confirmed, follow your instructions' fallback or report
the failure and end the turn.

The person answers in the card or by typing in the chat. A typed reply that
matches no option arrives with `answer: null` and their words in `raw_text`.
Use their words when the meaning is clear, and ask again when it isn't. Use
only answers the person gave.
