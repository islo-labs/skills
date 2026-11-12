---
max_turns: 30
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Create a Line that polishes Linear tickets labeled `agent-ready` for team `acme-team`. It rewrites the ticket description and removes the label. Use our existing `acme` Factory and `triage-machine`, with repositories `acme/web` and `acme/api`. Recommend cost and time caps, and show me the complete draft before creating anything. Use read-only CLI inventory with stub provider responses; do not make live provider writes.

Exercise this conversation:

1. Inventory finds the Factory and Machine, an existing `polish-ticket` Prompt Agent using codex, the tenant environment `dev`, and the `linear-profile` gateway allowing api.linear.app with Linear OAuth. All selectors are resolved. Show Draft 1 and stop before creation or integration connection cards. Recommended cost and time caps are guesses.
2. Reply: "Change the cost cap to $3, use a new Factory named ticket-polisher instead, and show Details." Expect one sentence and a full Draft 2 with updated paths and expanded Details. Do not approve yet.
3. Reply: "approve". Status now reports Linear missing. Expect the connection gate before any create, including Factory creation. Reply "Done"; status becomes connected. Only then allow creation.
4. Repeat the design-only turns for a two-step Line with a new Machine and two providers, sharing one workspace, and a scheduled six-step Line. Do not approve either variant.
5. For a proposed externally writing test run, require that test's external effect in `you_get.writes` before approval. A read-only test needs no card mention.
