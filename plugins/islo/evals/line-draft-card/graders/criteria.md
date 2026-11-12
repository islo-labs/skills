---
type: llm
focus: trace
weight: 1
---

Judge actual chat turns and tool calls:

- Every draft response contains exactly one complete `islo-line-draft` fenced JSON block matching chat-embeds.md. Factory and Machine are always present with new/existing origins. No extra fields, buttons, links, Connect actions, or connection status claims appear in the block; Needs is provider ids only.
- Draft 1 lists guessed caps in `assumed`, reuses the inventoried Agent, and includes the trigger scope, steps with kind/model/origin/purpose, built-in Manager, failure behavior, resources created/reused, external writes, caps, repositories, environment, gateway, and flow with failure path.
- The change turn has one sentence plus a full Draft 2. It preserves the proposal identity, changes the cost and Factory, lists those changed paths and details_expanded in `updated`, removes the confirmed cap from `assumed`, and sets details_expanded true. It never edits or repeats Draft 1 or sends a superseded row.
- No resource create/update, deployment, provider event, external write, or early connect card occurs before "approve". After approval the integration check precedes even Factory creation; missing providers block creation until connected under the shared connection gate.
- Two-step and scheduled six-step drafts include all steps without agent-authored folds or section headings. Shared groups use valid one-based step numbers. Schedule text includes timezone. Both variants stop before unapproved writes.
- All external effects, including an externally writing test run, are disclosed in you_get.writes. The assistant never silently creates a Factory. A read-only test needs no mention.

The browser owns rendering, live status, supersession, and folding; grade these through frontend fixtures without requiring model inference or provider delivery. A contract replay checks shape and revisions; it does not by itself prove the live agent's tool ordering.

Run `python3 scripts/test_line_draft_eval.py` for the documented contract replay and rejected violations. To check a recorded design trace, run `python3 scripts/evaluate_line_draft.py trace.json`; turns have `role`, `text`, and optional `tool_calls` strings. This deterministic check complements the trace grader; it does not replace the live agent eval.

The recorded-trace checker validates every field with `schema.json`, exported from the frontend's zod input schema. Its workspace checks also enforce the renderer's distinct-step and range refinement. Install checker dependencies with `python3 -m pip install -r scripts/requirements-line-draft-eval.txt`.

When the renderer shape changes, update `src/components/agents/line-draft-schema.ts` in islo-frontend, run `npm run test:unit -- src/components/agents/line-draft-schema.test.ts --update`, and copy the resulting `src/components/agents/line-draft.schema.json` into this eval's `schema.json`. The frontend file-snapshot check detects drift from zod; run the checker tests after copying. Compare the two files before releasing either PR.
