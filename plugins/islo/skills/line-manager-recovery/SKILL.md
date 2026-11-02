---
name: line-manager-recovery
description: Recover a failed Line stage as the Islo Line Manager. Use when a routing turn's context has reason `stage_failed`, to choose between a plain retry, a diagnosed steer, a fresh session, a sandbox replacement, or stopping.
---

# Recovering a failed Line stage

This skill is for the Line Manager. A failed stage parks the run and gives you a
routing turn whose context says `"reason": "stage_failed"`. The context fields
that drive this policy are:

| Field | Meaning |
|---|---|
| `attempt_count` | Consecutive failures of this stage, including recovery attempts |
| `max_attempts` | Plain attempts the stage gets before recovery starts. The stage's `max_attempts`, or 3 when the Line does not set it |
| `stage_exhausted` | `attempt_count >= max_attempts`: plain retries are used up |
| `recovery_attempt` | 0 while plain retries remain, then 1, 2, ... for each failure after that |
| `error_code`, `error_message` | The failed JobRun's error |

## Decide by `recovery_attempt`

- **0: plain retry.** Run `islo factory line-run retry RUN_ID` with no changes.
  Each outcome is evidence: the same error again suggests a deterministic
  failure, a different error suggests a flaky one. This is the only case where
  repeating an identical attempt is allowed.
- **1 or 2: diagnose and recover.** Find the cause before acting, then change
  something you can name. Never repeat an identical retry here.
- **3 or more: stop.** Always end the turn with
  `islo factory line-run stop RUN_ID --reason "..."`, giving the diagnosis and
  the action a human needs to take. If a person must decide, put the question
  in the reason; never end this turn without the stop. Add `--skip-current-stage`
  only when the stage itself is non-essential and should be recorded as
  `skipped` rather than `stopped`; it still parks the run, it does not advance
  the line.

If the error can never succeed on a retry (missing credentials, a rejected
parameter, a policy refusal), skip the remaining plain retries and go straight
to recovery or stop.

## Diagnose

```bash
islo factory line-run stages RUN_ID        # per-stage attempts and outcomes
islo factory line-run events RUN_ID        # step timeline and compute command ids
islo job event COMMAND_ID                  # exit code, error detail, output tails
islo factory line get LINE_NAME            # the stage's params, types, and defaults
```

When the tails are not enough, confirm the stage sandbox still exists with
`islo ls`, then inspect it with `islo logs` or `islo use <sandbox> -- <command>`.
`islo use` creates a sandbox that does not exist, so never run it on a name
`islo ls` did not list.

## Recover

Pick the smallest change that addresses the cause:

| Cause | Action |
|---|---|
| Wrong or missing input | `steer` the stage with corrected `--param` / `--param-json` values |
| Agent went down a wrong path | `steer` with a focused `resume_prompt` (or the stage's prompt-like param) written as if the agent has no other context |
| Agent conversation is broken or cannot resume | `steer RUN_ID STAGE --fresh-session --reason "..."` |
| Sandbox is broken (disk full, corrupt checkout, dead services) | Replace the sandbox, below |

`--fresh-session` starts the stage agent in a new conversation. It receives a
Previous attempts handoff built from the stage's earlier attempts, which
includes your `--reason`, so write the reason as an instruction to the new
agent. On a normal steer the reason only goes on the timeline; use params to
reach the agent.

### Replace a broken sandbox

1. If `islo ls` lists the old sandbox, run `git status` in it with
   `islo use <sandbox> -- ...` and push any unpushed work to its PR branch.
2. Delete it with `islo rm <stage sandbox>`. Stage sandboxes are named
   `<agent>-<line_run_id>` unless the stage sets `sandbox_name`.
3. `steer RUN_ID STAGE --fresh-session --reason "..."`. The stage recreates the
   sandbox from its Machine, which clones the repository default branch; tell
   the agent in the reason which PR branch to check out.

Never discard pushed commits, PR branches, or stage outputs.

## Limits

This policy is advisory. The Line's `max_iterations` limit is the backstop, and
`[limits] timeout` or `budget_usd` caps still apply; see the Line Manager prompt
for `--reset-iterations` and `--reset-usage`.
