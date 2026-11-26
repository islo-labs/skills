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

- `stop` parks single-stage work resumably; during a parallel group it lets running members finish, skips the join, and leaves the run `stopped` with an open control window for `steer`.
- `retry` reruns the latest failed stage, or only the failed group members with each member’s own params, and continues the line. No flags; the failed stage is implied.
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

After an Agent update, start a fresh Line run. Retrying an already visited stage keeps the Agent configuration that run first resolved.

Only when explicitly asked to maintain an existing Job, deploy its updated version, update its existing Line binding, validate, redeploy, and start a fresh run. Leave existing Job stages in place and add no new ones. After a Machine update, wait for the Machine to return to ready before starting a fresh run.

Follow [Waiting for line runs you start](wait-for-line-runs.md) for the fresh run, then verify its final outputs before continuing the original task.

## Parallel controls (CLI v0.93.0+)

For `plan -> [backend, ui] -> review`, steer UI alone to retain backend's last
outputs. Steering a member clears only that stage and stages after its group.
After success the run follows an own matching route, otherwise a covering join;
a failed member parks. A blocked join never runs while a named member's latest
result is failed: retry reruns that member and keeps siblings' newer results.

```bash
islo factory line-run steer RUN_ID backend ui --params-file - --reason "Revise both" <<'EOF'
{"backend":{"follow_up":"Revise the API"},"ui":{"follow_up":"Revise the UI"}}
EOF
islo factory line-run steer RUN_ID ui --param follow_up="Address review" --reason "UI only"
islo factory line-run steer RUN_ID review --fanout '["api","web"]' --reason "Review each input"
```

Use only declared params. Multi-stage `--params-file` takes an object keyed by
stage name. `--param`, `--param-json`, and `--fanout` are single-stage only.
The API sends either `stage_name` plus `params`, or `stages: [{stage_name, params}]`.
`stages` forbids duplicates, `done`, `wait`, `fail`, and top-level `params` or
`fanout`. Each steered stage counts toward the limit.

Fanout is one Agent stage's per-visit override: a positive count repeats shared
params; a non-empty list supplies each copy's `input`. The stage's `max_fanout`
and `concurrency` apply, and outputs collect in item order. Retry reuses the
visit's override; a later steer without it uses manifest fanout again.

Group failures skip conditional routes, including fail-fast. Inspect the decision's
`routing_context.stage_results` for every member and `failed_stages` for
`{stage, error_code, reason}`. Retry only reruns failures with their own params.
No covering join parks with every result for the Manager. Stop during a group
lets running members finish without running the join, leaves the run `stopped`,
and a later steer continues it. Group active time counts once, first start to
last result, while each member adds an iteration.
