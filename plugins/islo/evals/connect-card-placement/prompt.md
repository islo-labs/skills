---
max_turns: 30
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Build a Line that starts when our Acme Linear team adds the `agent-ready` label and sends the issue to our existing `issue-triage` Agent on `triage-machine`. Use the existing `acme` Factory and recommend the complete draft before changing anything. Ask me about any unresolved selectors first.

Exercise these variants with read-only inventory and a stub CLI; do not make live provider writes:

1. Question turn: leave the Linear team UUID unresolved until I answer. Then approve the complete draft. Status returns `integrations: []`, `integrations_error: null`, and `auth.tenant_name: "Acme"`. After the card, pause the conversation. Resume with “Done”; the next status still has no Linear entry. Resume with “I fixed it, done”; the next status includes `{"provider":"linear","connected":true}`.
2. Connected: approve the draft with Linear already connected. No connection card is needed.
3. Unknown: approve the draft, then return an integration lookup error. Repeat with older output containing `integrations: []` and `auth.tenant_name: null` but no error field. After the card, answer “Linear is already connected”; the follow-up status remains unknown.
4. Tool dependency and reconnection: use a manual trigger with a Slack posting tool. Approve the draft, with Slack missing but Linear connected. After the first Slack card, reply "Done" while Slack remains missing. Then connect only Slack, confirm, and return connected Slack status so the approved deployment can complete. In the same conversation, disconnect Slack and ask "The Slack tool is failing again. Check readiness before retrying." Return reliable status with only Linear connected. Reply "Done" once more while Slack remains missing, then reconnect Slack and confirm again. Keep all turns in the same session, including the successful deployment and later debugging.
5. Debugging: an existing Line's Linear trigger did not fire. Status says Linear is missing. If this conversation already showed the Linear card, explain the remaining connection issue without sending a second card.

6. Cursor scope: approve a draft that needs a Cursor-backed internal Job. Exercise a connected Tenant Cursor integration (no card), a Personal-only connection (Tenant remains missing), and a retry after the Cursor card already appeared. When status omits scope, provide GET /integrations/cursor responses with user.connected and tenant.connected. Do not treat a Personal-only connection as satisfying a Tenant requirement.

7. Incomplete approval: expose only a Linear event that requires both a team UUID and a label. Resolve the team but leave the label unanswered in the draft, with a Slack summary destination already resolved. Reply “Approved. Proceed.” while both providers are disconnected. After the assistant's next reply, supply the missing label and approve the completed blueprint. Then exercise missing and connected status as above.
