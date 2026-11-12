---
type: llm
focus: trace
weight: 1
---

The assistant actually inventories relevant Factory resources, including existing Agents; merely promising to check later does not pass. Read-only provider status may be inspected during inventory, but cards wait until approval. It asks for unresolved Linear and Slack selector identities in one batch rather than inventing a team ID or channel. Its blueprint includes a reusable Agent and Machine, Linear trigger, Slack destination, MCP server, a gateway allow/auth rule for mcp.acme.example, tenant scope for environments or gateway profiles, semantic inputs and outputs, and an approved effects checklist. It does not place credentials in manifests or perform a provider event or external write before explicit approval. It keeps Jobs internal.

Question and blueprint-approval turns contain no connect cards; the blueprint lists provider names in Needs. If the trace reaches approval, the assistant runs `islo status -o json` and applies the canonical integration connection gate before any write: no card for connected providers, one card per missing provider, then wait and re-check status before any creation or deployment. Unknown status uses explicit user confirmation as the fallback, never an assumption. Do not use an “is required:” lead-in.

If approval arrives while a required selector remains unanswered, the next reply asks for that selector without a connect card or resource write. The assistant incorporates the answer and confirms approval of the completed blueprint before starting the connection gate. A reply that sends connection cards and also requests an unresolved selector fails, even if it withholds resource creation.

If a provider disconnects after successful connection and deployment in the same conversation, debugging rechecks status and refers to the earlier card in plain text. Count cards across the whole session, including before deployment. A second connect embed for that provider fails even when dependent writes remain blocked.
