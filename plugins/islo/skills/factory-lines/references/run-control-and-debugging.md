# Run control and debugging

How to inspect, steer, and debug line runs. Verbs here match the current CLI contract.

## The verbs

```bash
islo factory line-run status <run-id>
islo factory line-run events <run-id>
islo factory line-run stages <run-id>
islo factory line-run stop <run-id> --reason "<why>"
islo factory line-run retry <run-id>
islo factory line-run steer <run-id> <stage> --param KEY=VALUE
islo factory line-run steer <run-id> <stage> --reset-iterations
islo factory line-run cancel <run-id> --reason "<why>"
islo factory line-run ask <run-id> --message "<question>"
islo factory line-run agent-turn <run-id> --stage-name <stage> --message "<message>"
```

- `stop` kills in-flight stage work for real (compute events resolved, children cancelled) but parks the run resumable: status becomes `stopped` with an open control window for `steer`.
- `retry` reruns the latest failed stage and continues the line. No flags; the failed stage is implied.
- `steer` sends a stopped or finished run back to a named stage (positional `<stage>`, not a flag). Steering an active run returns 409; stop first, then steer. `--param` overrides merge over the stage's last attempt params and are type-coerced against the job manifest; unset params are inherited. Steer preserves the run's global `max_iterations` counter by default; pass `--reset-iterations` to reset it when the run is capped and more work is legitimately needed.
- `cancel` terminates a running line for good — unlike `stop`, there is no resumable control window afterward.
- `ask` messages the line manager about the run: reassess, explain, or route.
- `agent-turn` sends another turn to one stage's successful agent session (`--stage-name` is a flag here, unlike `steer`). Use it for the stage's agent; use `ask` for the manager.

## Failure modes to commands

| Symptom | Do this |
|---------|---------|
| Trigger fired but no run appeared | `islo factory line-run list --line <name>`, `islo factory triggers list --with-status` |
| Stage failed | `islo factory line-run events <run-id>`, then `islo job event <command-id>` for the failing step's detail |
| Agent did the wrong thing mid-stage | `islo factory line-run agent-turn` with a corrective message; inspect with `islo ssh <sandbox>` and `islo logs <sandbox>` |
| Manager routed wrong or you want a reassessment | `islo factory line-run ask` |
| Deploy returned 422 or "Extra inputs are not permitted" | Unknown key; diff the manifest against `islo schema factory --short` / `islo schema job --short` |
| Line runs a stale job version after a job redeploy | Redeploy the line; it pins `job_version_id` at line deploy time |
| Schedule reverted after a deploy | The schedule was created outside the manifest; move it into the line `[trigger]` |
| Run stuck at a decision | `islo factory line-run status`, then stop, retry, or steer as fits |
| Run capped by `max_iterations` but more work is legitimately needed | Stop, then `steer` with `--reset-iterations` |

## Debug loop for a failed stage

```bash
islo factory line-run status <run-id>
islo factory line-run events <run-id>
islo job event <command-id>
islo ssh <sandbox-name>
islo logs <sandbox-name>
```

`events` names each stage attempt and its steps; each step carries a compute command id. `islo job event` shows that step's exit code, error detail, and output tails. When the tail is not enough, the sandbox itself (if still alive per its lifecycle policy) has the full story via `ssh` and `logs`.

Once the aggregated debug API ships, `GET /factory/line-runs/{run_id}/debug` returns the joined per-stage view with a failure summary, and `GET /factory/line-runs/{run_id}/logs?stage=&step=` resolves full step output. Prefer them over hand-joining events when available.

## After fixing

Manifest fixes follow the deploy order in `create-a-line.md` Phase 6: jobs, then the line. Then `retry` the failed run or start a fresh one and verify with `status` and `events`.
