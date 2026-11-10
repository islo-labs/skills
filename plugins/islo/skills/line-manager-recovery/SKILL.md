---
name: line-manager-recovery
description: Recover a failed Line stage as the Islo Line Manager. Use when a routing turn's context has reason `stage_failed`, to choose between a plain retry, a diagnosed steer, a fresh session, a sandbox replacement, or ending the run as failed.
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
| `error_code`, `error_message` | The failed stage's error |

## Decide by `recovery_attempt`

- **0: plain retry.** Run `islo factory line-run retry RUN_ID` with no changes.
  Each outcome is evidence: the same error again suggests a deterministic
  failure, a different error suggests a flaky one. This is the only case where
  repeating an identical attempt is allowed.
- **1 or 2: diagnose and recover.** Find the cause before acting, then change
  something you can name. Never repeat an identical retry here.
- **3 or more: end the run as failed.** End the turn with
  `islo factory line-run steer RUN_ID fail --reason "..."`. This ends the run
  `failed`, preserves the failed stage's error classification, and leaves the
  run steerable or retryable. If a person must decide first, post a question
  as described below, then end the turn.

If the error can never succeed on a retry (missing credentials, a rejected
parameter, a policy refusal), skip the remaining plain retries and go straight
to recovery or ending the run as failed.

## Ending states

Use `islo factory line-run steer RUN_ID fail --reason "..."` when giving up on
this run. It takes no stage params. Write the reason in this form:

`<error_code> x <attempt_count> on <stage>; what was tried; PR heads and unpushed-work state; what a person must do`

Include the actual PR head SHAs and whether work is pushed, unpushed, or
unreachable. The reason is recorded on the timeline. `steer fail` explicitly
ends the run `failed` regardless of the last stage's status; `steer done` is
for normal completion, not giving up.

When a person must decide, post the question with what you attempted and found,
then end the turn:

```bash
islo api -X POST /factory/line-runs/RUN_ID/questions --input - <<'EOF'
{"questions":["QUESTION"],"attempted":["WHAT WAS TRIED"],"findings":["WHAT WAS FOUND"]}
EOF
```

Use `stop` only for an explicit pause or after a posted question. Do not hide
questions in a stop reason; that does not notify anyone. Never use `stop` to
give up on a failed stage.

## Diagnose

```bash
islo factory line-run stages RUN_ID        # per-stage attempts and outcomes
islo factory line-run events RUN_ID        # step timeline and compute command ids
islo factory line get LINE_NAME            # the stage's params, types, and defaults
```

When the tails are not enough, run `islo ls -a` and match the stage sandbox by
`<agent>-<line_run_id>`, or by the stage's `sandbox_name` when set.
Plain `islo ls` shows only the caller's sandboxes and can return
`No sandboxes found.` even when a Machine-backed stage sandbox exists.
Never conclude that no stage sandbox exists from an empty plain `islo ls`;
check `islo ls -a` first. Inspect a listed sandbox with `islo logs` or
`islo use <sandbox> -- <command>`. `islo use` creates a missing sandbox, so
never run it on a name that `islo ls -a` did not list.

## Recover

Pick the smallest change that addresses the cause:

| Cause | Action |
|---|---|
| Wrong or missing input | `steer` the stage with corrected `--param` / `--param-json` values |
| Agent went down a wrong path | `steer` with a focused `resume_prompt` (or the stage's prompt-like param) written as if the agent has no other context |
| Agent conversation is broken or cannot resume | `steer RUN_ID STAGE --fresh-session --reason "..."` |
| Sandbox is broken (disk full, corrupt checkout, dead services), or a listed paused sandbox repeatedly fails `ensure_sandbox` | Replace the sandbox, below |

`--fresh-session` starts the stage agent in a new conversation. It receives a
Previous attempts handoff built from the stage's earlier attempts, which
includes your `--reason`, so write the reason as an instruction to the new
agent. On a normal steer the reason only goes on the timeline; use params to
reach the agent.

### Replace a broken sandbox

1. Run `islo ls -a` and match the old sandbox by `<agent>-<line_run_id>` or
   the stage's `sandbox_name`. If it is reachable, run `git status` in it with
   `islo use <sandbox> -- ...` and push any unpushed work to its PR branch.
   If it cannot be reached, record that in the steer reason.
2. Delete the listed sandbox with `islo rm <stage sandbox>` before steering.
   A paused sandbox with repeated `ensure_sandbox` failures is a replacement
   candidate even if its status does not say `failed`.
3. `steer RUN_ID STAGE --fresh-session --reason "..."`. The stage recreates the
   sandbox from its Machine, which clones the repository default branch; tell
   the agent in the reason which PR branch to check out.

Never discard pushed commits, PR branches, or stage outputs.

## Limits

This policy is advisory. The Line's `max_iterations` limit is the backstop, and
`[limits] timeout` or `budget_usd` caps still apply; see the Line Manager prompt
for `--reset-iterations` and `--reset-usage`.
