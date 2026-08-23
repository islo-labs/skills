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

Ask once, as one batch. Do not dribble questions across the conversation.

1. Outcome and stage breakdown. 2 to 6 stages, one responsibility each. Propose a breakdown from the request and let the user correct it.
2. Trigger. Manual, schedule (cron and timezone), webhook, or integration (provider, event, selector), and whether the trigger's provider is connected (`islo factory triggers list --with-status`). See `triggers.md`.
3. Runtime profile: ONE confirm-or-override block, not five questions. See below.
4. Limits: `max_iterations`, `timeout`, budget.
5. Where results land: PR, Slack message, knowledge item, outputs.

### The runtime profile block

Sandbox, snapshot, harness, model, and repositories are the five load-bearing runtime concepts of a line. Present them as one compact block for the whole line, splitting per stage only where stages genuinely differ. Each concept gets a one-line explanation and a prescriptive default with its rationale, filled in from Phase 0 (live models, `islo status` for the GitHub connection). End the block with a single question: confirm, or override any line.

```text
Runtime profile (confirm or override):
- Harness    the agent CLI each stage runs. Default: codex
             (Islo-managed inference, no provider key to wire).
- Model      what the harness thinks with. Default: <recommended
             from the live model list for that harness>.
- Sandbox    the VM each stage runs in. Default: fresh per stage
             (provision + teardown); isolated, no stale state.
- Snapshot   prebuilt sandbox image with your harness code. Default:
             none. Only propose one if the approved profile needs
             servers, test harnesses, or bundled assets; then create
             it with the platform skill before deploy.
- Repos      what each stage's checkout step clones: <owner/repo,
             detected from the request or the current repo>. GitHub
             integration: <connected | not connected, run islo login
             --tool github>.
```

Do not re-ask any of the five separately afterward; an override lands in the design summary and that is where the user re-checks it.

## Phase 2: design summary and APPROVAL GATE

Present one summary and wait for explicit approval. Do not create, deploy, or scaffold anything before it. The summary contains:

- Stage table: id, job name, description, and a runtime line per stage in the form `harness / model / sandbox mode / snapshot / repos` (identical rows collapse to one "all stages" line above the table).
- ASCII transition graph, including loops and failure routes.
- Trigger sketch: type, selector, filters, trigger outputs.
- Deploy sequence you will run (Phase 6 order).
- Cost note: validation is static; the first real feedback is a billed run.

## Phase 3: author

- Copy the nearest example from [islo-labs/islo-agents](https://github.com/islo-labs/islo-agents) (`examples/`) and treat it as a pattern, not a drop-in. Clone or browse that repo if it is not already on disk.
- `islo job init <name>` per stage. Add `--with-verification` on stages whose outputs gate transitions.
- Write the `job.toml` files first: params and outputs are the line's contract. Then `line.toml`. Confirm every field against `islo schema job --short` and `islo schema factory --short`; see `job-manifest.md` and `line-manifest.md` only for policy the schema does not state.
- Do not create a snapshot unless the approved runtime profile named one. If it did, follow the platform skill's sandboxes reference, put harness code in `snapshot-src/`, and set `snapshot_name`.
- Agent instructions: if the user's repo already contains skills, check it out with an idempotent fetch-or-clone exec step before the agent step (the pattern in `job-manifest.md`; the default gateway profile injects GitHub credentials) and keep the `run_agent` prompt a short literal pointing at that skill. If there is no repo, or the repo has no skills, write the prompt in the job. Never copy procedural content into Knowledge; deploy rejects procedural knowledge.

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
