# Good Line examples

These bundled TOMLs are complete Line shapes with explicit prompts, typed inputs/outputs, and routing. They are adapted from feature-delivery, architecture-spike, and publishing patterns observed while authoring this skill. No access to those private Lines or the Islo tenant is needed: all relevant instructions are here.

## Agent and Machine context

Every stage references `example-worker`, defined in [worker.agent.toml](worker.agent.toml). The complete stage `prompt` overrides that Agent's fallback prompt; the Line declares the stage-specific params and outputs. Replace example names and Machine/model choices with approved resources from the user's Factory. The Machine must have the Islo CLI, the installed skills, and the repository/provider tools and access needed by the chosen example. For PR work it must contain the approved checkout and authenticated GitHub tooling; for Linear comments it needs the approved provider connection. Tokens never belong in these files.

Follow [the setup and approval workflow](../references/create-a-line.md). Inspect the installed schemas, validate/create the adapted Agent before the Line, and validate the **whole** Line with `islo factory line validate FILE`. Validation checks schema and references; it does not grant permission to deploy, start a run, post comments, or publish Knowledge. The validator accepts only the expected unknown-Agent error when the portable example Agent has not been installed; that proves schema shape, not a runnable deployment.

The manual report Line takes string input `request`; the manual PR Line takes string input `task`. The integration Line binds `issue_id` from the provider payload. Every stage emits standard `summary`, including on a blocker. Array handoffs stay arrays through `type = "output"`; a consumer never extracts IDs from prose. Blocked outcomes park at `wait` with an explicit agentic resume transition so the Manager can resolve the blocker or end the run as failed, rather than claim success. Publication/comment references are optional only so a blocked outcome can omit them: Agent instructions require real references on success.

## Pick the final deliverable first

| File | Final deliverable and publication | Stage outputs (types) |
|---|---|---|
| [final-report.line.toml](final-report.line.toml) | One report/text outcome, published as **one Knowledge item for the Line** by `publish`. The investigator does not publish. Retries update the same slug. A final artifact could serve the same purpose through the harness's supported artifact contract. | `investigate`: `summary:string`, `draft:string`, `evidence_refs:string[]`. `publish`: `summary:string`, `result:published\|blocked`, `report_slug:string?`. |
| [pr-comment.line.toml](pr-comment.line.toml) | PRs and their review comments are the outcome; **zero Knowledge items**. Existing PR/comment links are the deliverable references, without a duplicate report. | `implement`: `summary:string`, `pull_requests:string[]`. `review`: `summary:string`, `result:reviewed\|blocked`, `comment_urls:string[]`. |
| [labeled-comment.line.toml](labeled-comment.line.toml) | A Linear triage comment is the outcome; **zero Knowledge items**. Only issues created with or gaining the intended label enter the Line. | `comment`: `summary:string`, `result:commented\|blocked`, `comment_url:string?`. |

Example stage results (illustrative values, not already-published resources):

| Line / stage | Result |
|---|---|
| Final report / investigate | `{"summary":"Compared two designs using local evidence.","draft":"Design A meets the requested constraints...","evidence_refs":["https://example.test/evidence/1"]}` |
| Final report / publish | `{"summary":"Published the final comparison report.","result":"published","report_slug":"final-report-RUN_ID"}` |
| PR/comment / implement | `{"summary":"Implemented the requested change; focused checks passed.","pull_requests":["https://github.com/example/app/pull/42"]}` |
| PR/comment / review | `{"summary":"Reviewed the change and posted the findings.","result":"reviewed","comment_urls":["https://github.com/example/app/pull/42#issuecomment-1"]}` |
| Labeled comment / comment | `{"summary":"Posted the requested triage findings.","result":"commented","comment_url":"https://linear.app/example/issue/EX-1#comment-example"}` |

For report publication commands, see the [Knowledge surface example](../../surfaces/references/knowledge.md#publish-a-markdown-document). Only the owning stage opens the Surface. Intermediate summaries, evidence handoffs, PRs and comments do not each need their own Knowledge item. A comment that is itself the requested action stays a comment; a separate final report/text deliverable is the case that requires artifact/Knowledge publication.

## Label-only trigger checks

The bundled label-only example uses the catalog's `issue.labeled` event and `scope = "selected"`, `labels = ["islo"]`. Empty team/project/state lists would add no restriction. Under selected scope, populated dimensions combine with AND and alternatives within a dimension with OR; label IDs/names match case-insensitively. Under all scope, the Linear selector bypasses those criteria. See [trigger semantics and safe verification](../references/triggers.md#linear-label-only-selection) and the [bad counterpart](../lines-bad-examples/all-issues.line.toml).

| Synthetic provider case | Expected for `labeled-comment.line.toml` |
|---|---|
| Create with intended label (including a case variant) | Match |
| Create unlabeled or with only another label | No match |
| Add intended label to an existing issue | Match |
| Title update retaining intended label, unrelated label addition, or removal | No match |

Use the current catalog payload shape and actual matcher in local fixtures first. Schema validity alone does not establish correct filtering. Real provider events, including negative tests that could accidentally start a run, require approved effects. Reading or validating these examples authorizes none of those writes. The [bad example explanations](../lines-bad-examples/README.md) pair defects with these corrected files.
