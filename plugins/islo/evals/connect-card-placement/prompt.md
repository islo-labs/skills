---
max_turns: 30
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Build a Line that starts when our Acme Linear team adds the `agent-ready` label and sends the issue to our existing `issue-triage` Agent on `triage-machine`. Use the existing `acme` Factory and recommend the complete draft before changing anything. Ask me about any unresolved selectors first.

Exercise these variants with read-only inventory and a stub CLI; do not make live provider writes:

1. Question turn: leave the Linear team UUID unresolved until I answer. Then approve the complete draft. Status returns `integrations: []`, `integrations_error: null`, and `auth.tenant_name: "Acme"`. After the card, pause the conversation. Resume with “Done”; the next status still has no Linear entry. Resume with “I fixed it, done”; the next status includes `{"provider":"linear","connected":true}`.
2. Connected: approve the draft with Linear already connected. No connection card is needed.
3. Unknown: approve the draft, then return an integration lookup error. Repeat with older output containing `integrations: []` and `auth.tenant_name: null` but no error field. After the card, answer “Linear is already connected”; the follow-up status remains unknown.
4. Tool dependency: use a manual trigger with a Slack posting tool. Approve the draft, with Slack missing but Linear connected. Connect only Slack, then confirm and return connected Slack status.
5. Debugging: an existing Line's Linear trigger did not fire. Status says Linear is missing. If this conversation already showed the Linear card, explain the remaining connection issue without sending a second card.
