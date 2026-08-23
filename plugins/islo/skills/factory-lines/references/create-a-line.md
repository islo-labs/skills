# Create a factory line

The end-to-end workflow for building a new line from a user's request. Work the phases in order. Phase 2 is an approval gate: nothing is created or deployed before the user approves the design.

## Phase 0: preflight (read-only)

Run these before asking the user anything, so the questions are informed:

```bash
islo status
islo factory manager status
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
2. Trigger. Manual, schedule (cron and timezone), webhook, or integration (provider, event, selector). See `triggers.md`.
3. Harness per agent stage (claude, cursor, codex, custom) and model from the live list.
4. Integrations needed and whether they are connected (`islo factory triggers list --with-status`, `islo status`).
5. Sandbox strategy. Fresh per stage is the default; shared only when stages must hand off a live workspace. Snapshot needs for harness code.
6. Limits: `max_iterations`, `timeout`, budget.
7. Where results land: PR, Slack message, knowledge item, outputs.

## Phase 2: design summary and APPROVAL GATE

Present one summary and wait for explicit approval. Do not create, deploy, or scaffold anything before it. The summary contains:

- Stage table: id, job name, harness/model, sandbox mode.
- ASCII transition graph, including loops and failure routes.
- Trigger sketch: type, selector, filters, trigger outputs.
- Deploy sequence you will run (Phase 6 order).
- Cost note: validation is static; the first real feedback is a billed run.

## Phase 3: author

- Copy the nearest template from `templates/` and treat it as a pattern, not a drop-in.
- `islo job init <name>` per stage. Add `--with-verification` on stages whose outputs gate transitions.
- Write the `job.toml` files first: params and outputs are the line's contract. Then `line.toml`. See `job-manifest.md` and `line-manifest.md`.
- Harness code (servers, test runners, assets) goes in `snapshot-src/` and a sandbox snapshot, referenced by `snapshot_name`. See the platform skill's sandboxes reference.
- Repo skills and prompts stay in the repo: check the repo out via `sandbox.sources[]` and keep the `run_agent` prompt a short literal, for example "Read and follow `.claude/skills/<x>/SKILL.md` in the checkout". Never copy procedural content into Knowledge; deploy rejects procedural knowledge.

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

Schedule only via the manifest `[trigger]`; a schedule created any other way is reverted by the next deploy. If the manager is disabled, `islo factory manager enable`.

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
islo factory manager status
islo factory manager runs
islo factory triggers list --with-status
```

For failures and run control, see `run-control-and-debugging.md`.

## Phase 8: handoff

Generate `RUNBOOK.md` in the user's line directory: the deploy commands in order, the test-one-event procedure with its checklist, and the snapshot rebuild steps. The runbook is what makes the line operable by someone who was not in this session.
