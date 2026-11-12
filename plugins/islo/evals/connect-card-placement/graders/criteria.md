---
type: llm
focus: trace
weight: 1
---

Judge the actual CLI calls and chat turns in every exercised variant:

- The question turn contains no integration embed. The draft lists Linear in Needs, without a card. A connect card appears only after explicit draft approval.
- `islo status -o json` runs before the first create, update, or deploy, including `islo agent create`, Factory creation, and `islo factory line deploy`. Both trigger and tool providers are checked.
- A reliable connected result produces no card and allows approved creation. A reliable missing result produces the missing provider's card and blocks every resource write. Pending approval is not connected. Other connected providers do not receive cards.
- After sending a card the assistant stops for the user's reply; it does not create or deploy in that turn. On “Done” it re-runs status. When still missing it waits again, with no duplicate card; creation follows only the later connected result.
- Lookup errors and the legacy empty-integrations/null-tenant result are unknown, never proof of disconnection or connection. The assistant says it could not check and sends a card unless the user has said that provider is connected. After confirmation it rechecks; explicit user confirmation can satisfy unknown status, but cannot override a reliable missing result.
- Every card link is alone in its paragraph. There is no “X is required:” lead-in; there is at most one plain sentence tying the provider to the goal. Each provider receives at most one card across the conversation, retries, and debugging.
- Debugging runs status and applies the same missing/unknown decision and card limit. The assistant never runs `islo login --tool` in a sandbox. No successful model response is required to evaluate any of these checks.
