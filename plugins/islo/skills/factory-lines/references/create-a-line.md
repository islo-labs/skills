# Create a factory line

The end-to-end workflow for building a new line from a user's request. Work the phases in order. Phase 2 is an approval gate: nothing is created or deployed before the user approves the design.

## Phase 0: preflight (read-only)

Run these before asking the user anything, so the questions are informed:

```bash
islo status
islo schema factory --short
islo schema job --short
```

If an integration trigger is likely (the request mentions Slack, GitHub, or Linear events):

```bash
islo factory triggers list --with-status
```

Query live models for the candidate harness instead of recalling a list; see `harness-models-knowledge.md`.

## Phase 1: intake questions, all up front

Ask once, as one batch, then **stop**. Do not dribble questions across the conversation. Do not attach a design summary, a filled-in runtime profile copied from a nearby line, or a Phase 2 approval question in the same turn.

When the host provides a structured interactive question tool, **use it for the entire Phase 1 intake** instead of rendering the questions as prose. Put every intake question in one tool call. Offer discovered or recommended choices where useful, and always retain the tool's "Other / I'll specify" path for free-text identities such as repositories, Linear projects, labels, and states. Fall back to prose only when no interactive question tool is available.

Identity vs pattern: nearby lines, `islo-agents` examples, and the current workspace may suggest stage shape (how many jobs, routing). They must not fill identity. If the user did not name a value **in this request**, ask. A guess is not an answer. Never present a single inferred option as the only choice; always include "other / I'll specify".

1. Outcome and stage breakdown. 2 to 6 stages, one responsibility each. Propose a breakdown from the request and let the user correct it.
2. Trigger. Manual, schedule (cron and timezone), webhook, or integration (provider, event). Then ask the selector the user actually wants — after `islo factory triggers get <provider> <event>`, ask the scoping questions that selector requires. Do not copy a nearby line's selector. See `triggers.md`.
   - Linear: team, project, and any label/state filter (or "all issues in that team/project").
   - GitHub: owner/repo (and which event).
   - Slack: workspace and channel.
3. Repositories. Which `owner/repo` each stage checks out. Ask unless the user named it in this request. Do not inherit from a nearby line, a snapshot name, or the current workspace.
4. Runtime profile: ONE confirm-or-override block for harness, model, sandbox, and snapshot only. See below. Repositories are item 3, not a default inside this block.
5. Limits: `max_iterations`, `timeout`, budget.
6. Where results land: PR, Slack message, knowledge item, outputs.

### The runtime profile block

Harness, model, sandbox, and snapshot are the remaining load-bearing runtime concepts. Present them as one compact block for the whole line, splitting per stage only where stages genuinely differ. Each concept gets a one-line explanation and a prescriptive default with its rationale, filled in from Phase 0 (live models, `islo status` for the GitHub connection). End the block with a single question: confirm, or override any line.

Do not put `owner/repo`, Linear team/project, Slack channel, or a nearby line's snapshot/gateway into this block as if the user already chose them.

```text
Runtime profile (confirm or override):
- Harness    the agent CLI each stage runs. Default: codex.
             Every harness (codex, claude, cursor, opencode) can use Islo
             inference via the gateway URL; no special case.
- Model      what the harness thinks with. Default: <recommended
             from the live model list for that harness>.
- Sandbox    the VM each stage runs in. Default: fresh per stage
             (provision + teardown); isolated, no stale state.
- Snapshot   prebuilt sandbox image with repos, tools, and harness
             code. Default: yes. Most lines need one. Propose a
             new name for this line. Reuse an existing snapshot
             only if the user names it. Skip only if the user
             explicitly wants a bare image.
```

Do not re-ask harness/model/sandbox/snapshot separately afterward; an override lands in the design summary and that is where the user re-checks it. If any identity field (repo, Linear team/project, Slack channel) is still a guess, stay in Phase 1.

## Phase 2: design summary and APPROVAL GATE

Present one summary and wait for explicit approval. Do not create, deploy, or scaffold anything before it. Do not reach this phase until Phase 1 identity (repos, trigger selector) has answers from the user, not from a nearby line. The summary contains:

- Stage table: id, job name, description, and a runtime line per stage in the form `harness / model / sandbox mode / snapshot / repos` (identical rows collapse to one "all stages" line above the table).
- ASCII transition graph, including loops and failure routes.
- Trigger sketch: type, selector, filters, trigger outputs.
- Deploy sequence you will run (Phase 6 order).
- Cost note: validation is static; the first real feedback is a billed run.

## Phase 3: author

- Copy the nearest example from [islo-labs/islo-agents](https://github.com/islo-labs/islo-agents) (`examples/`) and treat it as a pattern, not a drop-in. Clone or browse that repo if it is not already on disk.
- `islo job init <name>` per stage. Add `--with-verification` on stages whose outputs gate transitions.
- Write the `job.toml` files first: params and outputs are the line's contract. Then `line.toml`. Confirm every field against `islo schema job --short` and `islo schema factory --short`; see `job-manifest.md` and `line-manifest.md` only for policy the schema does not state.
- Create a snapshot as the default. Follow the platform skill's sandboxes reference, put harness code in `snapshot-src/`, and set `snapshot_name` on the jobs. Skip the snapshot only if the approved profile explicitly opted out.
- Agent instructions: write the stage brief in the job `run_agent` prompt so a prompt change is a new job version. If the user's repo already contains skills, check it out with an idempotent fetch-or-clone exec step (the pattern in `job-manifest.md`; the default gateway profile injects GitHub credentials) and point at that skill. Put supporting or fan-out briefs in the snapshot when they would clutter the line/job view. Never copy procedural content into Knowledge; deploy rejects procedural knowledge.

## Phase 4: static validation

```bash
islo job deploy --path jobs/<name>/job.toml --dry-run   # per job
islo factory line validate line.toml
islo factory line deploy line.toml --dry-run
```

A 422 or "Extra inputs are not permitted" means an unknown key; manifests reject unknown fields. Diff against `islo schema factory --short` or `islo schema job --short` instead of guessing.

## Phase 5: single-stage smoke test

Deploy the first agent stage's job for real and run it alone before deploying the rest:

```bash
islo job deploy --path jobs/<first-stage>/job.toml
islo job run <first-stage> --param KEY=VALUE --watch
islo job status <first-stage> <run-id>
islo job event <command-id>     # per-step detail from the step timeline
```

Confirm the declared outputs actually appear with the right values. If the outputs are wrong, the line's routing will be wrong; fix here, not after the line is live.

## Phase 6: deploy in canonical order

Knowledge items first, then every stage job, then the line last. The line pins `job_version_id` at deploy time, so redeploying a job alone does not update an already-deployed line; redeploy the line after any job change.

```bash
islo job deploy --path jobs/<stage>/job.toml   # each stage
islo factory line deploy line.toml             # last
```

Schedule only via the manifest `[trigger]`; a schedule created any other way is reverted by the next deploy.

## Phase 7: end-to-end verify

Manual and scheduled lines:

```bash
islo factory line run <name> --param KEY=VALUE
islo factory line-run status <run-id>
islo factory line-run events <run-id>
```

Integration lines: fire ONE real trigger event (post one message in the selected channel, open one test PR) with an expected-effects checklist written before the event, for example: reaction appears, every stage reports the same sandbox, PR contains the recording, final reaction appears.

If no run appears:

```bash
islo factory line-run list --line <name>
islo factory triggers list --with-status
```

For failures and run control, see `run-control-and-debugging.md`.
