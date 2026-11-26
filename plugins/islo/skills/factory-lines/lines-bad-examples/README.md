# Bad Line examples — do not deploy

These are intentional anti-examples, not deployment templates. They use the same [documented Agent context](../lines-good-examples/README.md#agent-and-machine-context) as the good examples. Their TOML can parse and even pass schema validation while still expressing the wrong behavior. The validator parses this folder separately; it never counts these files as positive deployment examples. No private tenant access is needed to understand or repair them.

| Bad TOML | Defect and reason | Corrected good counterpart |
|---|---|---|
| [inline-report.line.toml](inline-report.line.toml) | The Line's final deliverable is report/text, but the only copy is an inline `output` string. Keep intermediate drafts typed and publish the final report once, not once per Agent. | [final-report.line.toml](../lines-good-examples/final-report.line.toml) |
| [redundant-publication.line.toml](redundant-publication.line.toml) | A PR/comment workflow creates an unnecessary Knowledge report for each Agent. The PR and comment URLs already identify the final deliverables; zero Knowledge items is appropriate. | [pr-comment.line.toml](../lines-good-examples/pr-comment.line.toml) |
| [all-issues.line.toml](all-issues.line.toml) | Linear all scope bypasses label criteria; this `issue.updated` Line also admits updates to unlabeled issues. Use selected scope and the event matching the requested timing. | [labeled-comment.line.toml](../lines-good-examples/labeled-comment.line.toml) |
| [missing-summary.line.toml](missing-summary.line.toml) | A comment action or no-op finishes without a standard `summary`. A result URL does not replace the per-stage explanation; neither needs a Knowledge item. | [labeled-comment.line.toml](../lines-good-examples/labeled-comment.line.toml) |

The selector defect was reported from a chat-created Line. Missing standard summaries and inline-report patterns were also observed in tenant definitions while authoring the skill; those observations are embodied here rather than requiring readers to inspect the source Lines. The redundant-publication example captures the requester's correction to this skill's earlier guidance. See the [good bundle's stage output examples](../lines-good-examples/README.md#pick-the-final-deliverable-first) and [trigger inclusion/exclusion checks](../lines-good-examples/README.md#label-only-trigger-checks).

A separate workflow mistake is to fix this run and silently deploy the corrected Line. Follow the [repair-consent flow](../references/run-control-and-debugging.md#offer-to-fix-the-line): confirm the repair, offer a concrete update, and persist only after explicit yes. A user's no leaves the definition unchanged; one-off infrastructure/bad-input repairs do not need an improvement offer.
