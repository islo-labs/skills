# Line checklist and examples

Read this before drafting a Line or proposing a persistent repair. These are adapted patterns, not ready-to-deploy tenant configurations. Confirm fields with `islo schema factory --short` and `islo schema agent`; use [create-a-line.md](create-a-line.md) for approval, resource creation, and verification.

## Checklist

- **Every stage has a summary.** Declare a required string `summary` output and instruct the Agent to return a short account of its result, evidence, and any blocker. Include a summary for a successful no-op. A verdict, session transcript, or `writer_summary` alone does not supply the standard stage summary.
- **Publish the deliverable.** Agent instructions must publish reports and final results as artifacts or Knowledge, verify publication, and return their references. Put the short explanation in `summary`; do not leave the only report in chat text or a sandbox file. Use the existing artifact output contract for the harness, not a made-up artifact command. For stored reports, follow the [Knowledge publication example](../../surfaces/references/knowledge.md#publish-a-markdown-document).
- **Type the handoff.** Keep verdicts in enum strings, PR/evidence references in string arrays, and Knowledge slugs in strings. Declare matching inputs on consuming stages and bind the actual outputs with `type = "output"`. Do not make a downstream Agent recover IDs or decisions by parsing a summary.
- **Choose the event and its scope.** Start manual while testing; use schedules with an explicit timezone or the catalog's provider event for approved automation. Resolve selectors from the user's request. In Linear, a label-only request uses selected scope, not all scope with a labels list. Verify both inclusion and exclusion with the [trigger examples](triggers.md#linear-label-only-selection).
- **Route and bound the work.** Use Agent stages, explicit success/revision/blocked outcomes, and the Line's iteration/time/budget limits as appropriate. Define what the Manager should do when evidence or publication is unavailable. Shared sandbox groups require the same Machine.
- **Verify the promised result.** Inspect every stage's summary, typed handoffs, and published deliverables. Check approved side effects against the blueprint. A provider/model failure is a limitation to report, not evidence that a deliverable exists. Use local trigger fixtures first; live provider tests need approved effects.

## Reference observations

Read-only inspection of the Islo Factory on 2026-11-26 provided these patterns:

| Source | Pattern reused |
|---|---|
| `feature-delivery` v46 (also observed in recent runs) | `implement`, `review`, and `verify` each declare `summary`; verdicts are enums and `pull_requests`/`acceptance_criteria` are string arrays passed through output bindings. |
| `architecture-spike` v8 and its investigator Agent | The investigator creates/updates a run-scoped Knowledge report, opens its Surface, checks publication, and returns `knowledge_slug` plus bounded `evidence_refs`; the reviewer returns a typed decision and report reference. |
| `ticket-planner` v1 | Separate author/reviewer/publisher roles and an explicit publish stage returning `issue_url`, `publish_result`, and `summary`. |
| `linear-janitor` v2 | Its output contract contains the entire report in `output` and an enum `result`, but no `summary` or published report reference. |
| `islo-news` v1 | The stage has no declared outputs and its Agent explicitly suppresses a run message when there is no news. This leaves no stage summary for a successful no-op. |
| `weekly-changelog` v7 | Several stages use role-specific summaries or only a verdict/path. Those are useful semantic outputs, but each stage still needs the standard `summary`. |

The bad selector below comes from the requester's report of a chat-created Line. The other observations are tenant definitions; their creation channel was not exposed by the read API, so do not claim they all came from chat. The good examples below deliberately add missing standard summaries and publication contracts; they are not claims that the inspected Lines already implement the whole checklist. No source Line was changed.

## Good examples

Each JSON object is an illustrative stage result, not a claim that these example URLs/slugs have been published. The Agent prompt must require publication before returning them. Replace all resource identities and destinations with the approved Factory's resources.

### Feature delivery: implement, review, verify

Use the feature-delivery contract's separation of summaries, routing verdicts, and typed handoffs. A manual trigger fits a single approved task; for label-driven intake, use the selected selector in [triggers.md](triggers.md#linear-label-only-selection), not copied tenant labels.

| Stage | Outputs, including the stage summary |
|---|---|
| `implement` | `{"summary":"Implemented the requested change; focused tests passed.","implementation_result":"ready","pull_requests":["https://github.com/example/app/pull/42"],"acceptance_criteria":["The report opens from the run."],"report_slug":"implementation-RUN_ID"}` |
| `review` | `{"summary":"Reviewed both changed paths; no blocking findings.","review_result":"approved","report_slug":"review-RUN_ID"}` |
| `verify` | `{"summary":"Verified the requested behavior; one provider check remains unavailable.","verification_result":"blocked","report_slug":"verification-RUN_ID"}` |

Each stage publishes its detailed report as Knowledge; return PR artifacts for the implementation's PR set through the harness's artifact contract. Keep `ready|blocked`, `approved|needs_changes|blocked`, and `passed|failed|blocked` as enums. Pass PR and criteria arrays through typed output bindings. Route blocked verification to the Manager with the limitation, rather than silently marking it passed.

### Research: investigate, review

Adapt the architecture-spike pattern: manual input for an approved research request, or an explicitly approved label selector for recurring intake. The investigator writes and opens one run-scoped Knowledge report, updates that same item across retries, confirms publication, then returns its slug. The reviewer reads that report, records the decision in it, confirms the update, and returns the same reference.

| Stage | Outputs, including the stage summary |
|---|---|
| `investigate` | `{"summary":"Compared two designs using code and a local prototype.","knowledge_slug":"research-RUN_ID","evidence_refs":["https://example.test/evidence/1"]}` |
| `review` | `{"summary":"Recommended design A; production measurements remain unverified.","review_result":"approved","knowledge_slug":"research-RUN_ID"}` |

This Line fragment shows the **typed contract and handoff**, not a complete Line. The reusable Agents must already have publication/summary instructions and the reviewer must declare a string `knowledge_slug` input. Stage `prompt` overrides replace the reusable prompt, so preserve the complete task instructions if using one.

```toml
[[stages]]
id = "investigate"
agent = "research-investigator"
outputs.summary = { type = "string", required = true }
outputs.knowledge_slug = { type = "string", required = true }
outputs.evidence_refs = { type = "array", items = "string", required = true }

[[stages]]
id = "review"
agent = "research-reviewer"
params.knowledge_slug = { type = "string", required = true }
outputs.summary = { type = "string", required = true }
outputs.review_result = { type = "string", enum = ["approved", "needs_more_proof", "blocked"], required = true }
outputs.knowledge_slug = { type = "string", required = true }

[[transitions]]
id = "investigation-to-review"
type = "conditional"
from = "investigate"
to = "review"
when = { op = "always" }
params = { knowledge_slug = { type = "output", stage = "investigate", name = "knowledge_slug" } }
```

For example, the investigator's instructions include: "Write the findings and evidence to `research-$ISLO_LINE_RUN_ID` as Knowledge, open its Surface from this stage, and confirm the write succeeds before returning `knowledge_slug`. Return `summary` and the bounded `evidence_refs` array too. If publication fails, report the blocker instead of claiming publication." Use [the existing create/update/open commands](../../surfaces/references/knowledge.md#publish-a-markdown-document); the Manager asks the owning stage to publish rather than invoking a Surface in its own sandbox.

### Scheduled maintenance: sweep and report

Adapt the janitor's enum result, keeping the report separate from the summary. A schedule needs an explicit timezone; whether closing issues or posting messages is enabled belongs in the approved effects, not in an assumed default.

```toml
[trigger]
type = "schedule"
cron = "0 9 * * *"
timezone = "UTC"

[[stages]]
id = "sweep"
agent = "maintenance-reporter"
outputs.summary = { type = "string", required = true }
outputs.result = { type = "string", enum = ["completed", "could_not_finish"], required = true }
outputs.report_slug = { type = "string", required = false }
```

The Agent instructions require a report published as Knowledge for every completed sweep, including no-op runs, and a summary even when nothing changes. Example result: `{"summary":"Checked 20 issues; none needed changes.","result":"completed","report_slug":"maintenance-RUN_ID"}`. Confirm the report write before returning `completed`; a failed write returns `could_not_finish` with an accurate blocker summary, without fabricating a reference. The reference is optional in the schema to allow that failure outcome; require it for `completed` in the Agent instructions and route `could_not_finish` to the Manager.

## Bad examples paired with fixes

| Bad pattern and evidence | Fixed version | Reason |
|---|---|---|
| A chat-created Linear selector has `scope = "all"` with `labels = ["islo"]`. | Use `scope = "selected"`, keep only the requested criteria, and choose `issue.labeled` for creation-with-label/addition; verify a labeled issue matches and an unlabeled issue does not. | All scope bypasses label criteria; schema validity does not prove correct selection. |
| A janitor returns `output = "<entire report>"` and `result = "completed"` only, as in the inspected `linear-janitor` contract. | Publish the report as Knowledge, then return `summary`, enum `result`, and string `report_slug`, as in the scheduled example. | Inline report text is not a published deliverable and does not fill the standard summary. |
| A newsletter stage declares no outputs and says "post nothing and finish" on no news, as in `islo-news`. | Return `summary = "No merged PRs in the reporting window; no message sent."`; when there is a report, publish it as Knowledge and return its reference plus the approved message URL if sent. | A no-op needs a visible stage outcome even when no external notification is appropriate. |
| A writer returns only `writer_summary` or a local `changelog_path`, as in parts of `weekly-changelog`. | Also return standard `summary`, publish the final report/result as an artifact or Knowledge, and pass its typed reference to the publisher. | Role-specific text and local paths do not supply the standard summary or a durable result. |
| A repair publishes today's missing report, then silently redeploys the Line. This is the ticket's reported workflow gap extended with an unauthorized edit. | Finish the repair, then ask "Want me to update the report stage to publish Knowledge on future runs too?" Apply only that change after yes; no preserves the definition. | Permission to repair one run is not permission to change future runs. |

For the consent flow, including no answer, one-off failures, shared-resource effects, and avoiding duplicate offers, follow [Offer to fix the Line](run-control-and-debugging.md#offer-to-fix-the-line).
