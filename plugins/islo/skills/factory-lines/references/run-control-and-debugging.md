# Run control and debugging

How to inspect, steer, and debug line runs. Verbs here match the current CLI contract.

If you started the run for a chat request, follow [Waiting for line runs you start](wait-for-line-runs.md) before using recovery commands. The controls below do not authorize intervention in a run you are only observing.

## The verbs

```bash
islo factory line-run status <run-id>
islo factory line-run events <run-id>
islo factory line-run stop <run-id> --reason "<why>"
islo factory line-run retry <run-id>
islo factory line-run steer <run-id> <stage> --param KEY=VALUE
islo factory line-run ask <run-id> --message "<question>"
islo factory line-run agent-turn <run-id> --stage-name <stage> --message "<message>"
```

- `stop` kills in-flight stage work for real (compute events resolved, children cancelled) but parks the run resumable: status becomes `stopped` with an open control window for `steer`.
- `retry` reruns the latest failed stage and continues the line. No flags; the failed stage is implied.
- `steer` sends a stopped or finished run back to a named stage. Steering an active run returns 409; stop first, then steer. `--param` overrides merge over the stage's last attempt params and are type-coerced against the job manifest; unset params are inherited.
- An open question alone does not block `steer` or `retry`. The Manager may interpret the person's exact free-text chat message as their answer and route accordingly. Never invent an answer without user input or dismiss remaining questions merely to route. For question delivery and reply handling, see [questions.md](questions.md).
- A failed stage goes to the Line Manager, which follows the `line-manager-recovery` skill: plain retries until the stage's `max_attempts` (default 3) is reached, then up to two diagnosed recovery attempts, then stop. To opt a stage out, see "Failed stages and opting out of recovery" in [line-manifest.md](line-manifest.md).
- `ask` messages the line manager about the run: reassess, explain, or route.
- `agent-turn` sends another turn to one stage's successful agent session. Use it for the stage's agent; use `ask` for the manager.

## Failure modes to commands

| Symptom | Do this |
|---------|---------|
| Trigger fired but no run appeared | `islo factory line-run list --line <name> --paged --limit 20`, `islo factory triggers list`, then check providers with the [integrations skill](../../integrations/SKILL.md#check-connection-status) |
| Stage failed | `islo factory line-run events <run-id>`, then `islo job event <command-id>` for the failing step's detail |
| Agent did the wrong thing mid-stage | `islo factory line-run agent-turn` with a corrective message; inspect with `islo ssh <sandbox>` and `islo logs <sandbox>` |
| Manager routed wrong or you want a reassessment | `islo factory line-run ask` |
| Deploy returned 422 or "Extra inputs are not permitted" | Unknown key; diff the manifest against `islo schema factory --short` / `islo schema job --short` |
| Line runs a stale job version after a job redeploy | Redeploy the line; it pins `job_version_id` at line deploy time |
| Schedule reverted after a deploy | The schedule was created outside the manifest; move it into the line `[trigger]` |
| Run stuck at a decision | `islo factory line-run status`, then stop, retry, or steer as fits |

For trigger and provider failures, follow the [integrations skill](../../integrations/SKILL.md#check-connection-status) for the connection check and the [chat connection gate](chat-embeds.md#integration-connect-cards) for connect cards and waiting.

## Debug loop for a failed stage

```bash
islo factory line-run status <run-id>
islo factory line-run events <run-id>
islo job event <command-id>
islo ls -a
islo ssh <sandbox-name>
islo logs <sandbox-name>
```

`events` names each stage attempt and its steps; each step carries a compute command id. `islo job event` shows that step's exit code, error detail, and output tails. When the tail is not enough, the sandbox itself (if still alive per its lifecycle policy) has the full story via `ssh` and `logs`.
Stage sandboxes belong to job identities, so use `islo ls -a` to find them by `<agent>-<line_run_id>` or the stage's `sandbox_name`. An empty plain `islo ls` does not establish that a stage sandbox is absent.

Once the aggregated debug API ships, `GET /factories/{ref}/line-runs/{run_id}/debug` returns the joined per-stage view with a failure summary, and `GET /factories/{ref}/line-runs/{run_id}/logs?stage=&step=` resolves full step output. Prefer them over hand-joining events when available.

## After fixing

### Offer to fix the Line

Use the same finish-the-work-then-offer flow as chat's automation suggestion. First complete the authorized run repair and confirm its result. Then, if the cause will recur, offer to update the existing Line in the same reply. Name the stage prompt, output contract, Agent, or Machine change in one or two sentences:

> The report is now published as Knowledge. Want me to update the Line's report stage to publish it and return its Knowledge slug on future runs too?

- **Yes:** inspect the current Line and affected resources, apply only the proposed change, validate and save/deploy it through the existing CLI workflow, then confirm what changed. A clear yes to this concrete proposal authorizes that narrow edit; do not require a second draft approval for it. Substantial redesign still follows the setup contract. Approval does not cover shared Agent/Machine changes affecting other Lines; explain those effects and get approval before including them.
- **No:** leave the Line definition and its dependent resources unchanged; do not keep offering the same improvement in this conversation.
- **No answer:** leave the definition unchanged. The run repair itself never implies permission to edit the reusable Line.
- **One-off infrastructure or bad input:** finish the repair without an improvement offer. A flaky service or a malformed input is not evidence that the Line needs redesign.

Tenant chat delegates a product run's repair to its Manager as usual, then offers only after the outcome is confirmed. Do not duplicate an offer already made by the Manager or chat. For Manager turns, use the existing [question flow](questions.md) when an answer is needed and end the turn; do not block recovery on a future-run improvement. Route report/Surface publication to the stage agent that owns its sandbox, following the [surfaces skill](../../surfaces/SKILL.md).

For example, correcting an output contract to publish Knowledge is recurring; retrying after a brief provider outage is one-off. A permanent selector correction is recurring too: propose it with the [trigger inclusion/exclusion checks](triggers.md#linear-label-only-selection), rather than silently editing a tenant Line.

### Verify an approved persistent update

After an Agent update, start a fresh Line run. Retrying an already visited stage keeps the Agent configuration that run first resolved.

Only when explicitly asked to maintain an existing Job, deploy its updated version, update its existing Line binding, validate, redeploy, and start a fresh run. Leave existing Job stages in place and add no new ones. After a Machine update, wait for the Machine to return to ready before starting a fresh run.

Follow [Waiting for line runs you start](wait-for-line-runs.md) for the fresh run, then verify its final outputs before continuing the original task.
