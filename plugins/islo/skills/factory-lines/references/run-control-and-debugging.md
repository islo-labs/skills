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
islo factory line-run ask <run-id> --message "<question>"
islo factory line-run agent-turn <run-id> --stage-name <stage> --message "<message>"
```

- `stop` kills in-flight stage work for real (compute events resolved, children cancelled) but parks the run resumable: status becomes `stopped` with an open control window for `steer`.
- `retry` reruns the latest failed stage and continues the line. The failed stage is implied. Optional `--reset-usage` and `--reset-iterations` reopen the corresponding limits only when intended.
- `steer` sends a stopped or finished run back to a named stage. Steering an active run returns 409; stop first, then steer. `--param` sends string overrides; use `--param-json` or `--params-file` for typed values. Overrides merge over the stage's previous params; omitted params are inherited. Check the stage contract in the Line.
- A failed stage goes to the Line Manager, which follows the `line-manager-recovery` skill: plain retries until the stage's `max_attempts` (default 3) is reached, then up to two diagnosed recovery attempts, then end the run as failed. To opt a stage out, see "Failed stages and opting out of recovery" in [line-manifest.md](line-manifest.md).
- `ask` messages the line manager about the run: reassess, explain, or route.
- `agent-turn` sends another turn to one stage's successful agent session. Use it for the stage's agent; use `ask` for the manager.

## Failure modes to commands

| Symptom | Do this |
|---------|---------|
| Trigger fired but no run appeared | `islo factory line-run list --line <name>`, `islo factory triggers list --with-status` |
| Stage failed | `islo factory line-run stages <run-id>` and `islo factory line-run events <run-id>`, then the listed sandbox logs |
| Successful Agent session needs another turn | `islo factory line-run agent-turn` with a corrective message; inspect the listed sandbox with `islo ssh <sandbox>` and `islo logs <sandbox>` |
| Manager routed wrong or you want a reassessment | `islo factory line-run ask` |
| Deploy returned 422 or "Extra inputs are not permitted" | Unknown key; diff the manifest against `islo schema factory --short` and `islo schema agent --short` |
| Schedule reverted after a deploy | The schedule was created outside the manifest; move it into the line `[trigger]` |
| Run stuck at a decision | `islo factory line-run status`, then stop, retry, or steer as fits |

## Debug loop for a failed stage

```bash
islo factory line-run status <run-id>
islo factory line-run events <run-id>
islo factory line-run stages <run-id>
islo ls -a
islo ssh <sandbox-name>
islo logs <sandbox-name>
```

`stages` projects each stage's attempts and outcomes; `events` shows the timeline and failure details. Inspect the Agent configuration with `islo agent get <name>` and the Line's stage contracts with `islo factory line get <name>`. If an event includes an archived Agent turn id, read it with `islo factory agent-turn transcript <turn-id>`.

Use `islo ls -a` to locate the Machine-backed sandbox by `<agent-name>-<line_run_id>` or its stage `sandbox_name`. An empty plain `islo ls` does not establish that a stage sandbox is absent. Inspect only a listed sandbox with `ssh` and `logs`; avoid creating a new sandbox while trying to debug an old one. Its availability depends on the Machine lifecycle policy.

## After fixing

After an Agent update, start a fresh Line run. Retrying an already visited stage keeps the Agent configuration that run first resolved.

After a Machine update, wait for the Machine to return to ready before starting a fresh run.

After a Line contract or override change, validate and redeploy the Line. Verify a fresh run with `status`, `stages`, and `events`.
