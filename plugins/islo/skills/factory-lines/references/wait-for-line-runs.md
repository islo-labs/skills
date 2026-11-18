# Waiting for line runs you start

When you start a Line run to fulfill a chat request, wait for its result and continue the original task in the same chat. Starting the run does not finish the task. This applies to manual runs and runs started by an approved test event or SDK call. It does not make a stage agent wait for its own parent run or make a Line Manager wait inside a routing turn.

## Record the run and wait

For a few targeted searches for related runs, use `--line` and one or more
`--q` values, for example `islo factory line-run list --line feature-delivery --q ISL-2416 --q "shared initialization"`.
Every `--q` is one case-insensitive substring, and all must match. Search
covers names, run IDs, selected trigger fields, and artifact titles and
identifiers. It does not search run params, so keep the complete lookup below.
For new traversal, prefer `--paged --limit 20 -o json`, then pass the returned
opaque `cursor` as `--cursor` with the same filters and sort until null.
Paged JSON is `{items, cursor, total?}`. `--total` requests a point-in-time
exact count on the first page only. Legacy `--offset` syntax and JSON arrays
remain valid; do not combine `--offset` with `--cursor`.

1. Before starting, check `islo factory line-run list --line <name> --limit 20 --offset 0 -o json` in the selected Factory. Match run params and origin to the same work, rather than the Line name alone. If a matching run is active, observe it instead of starting another. Otherwise, repeat with `--offset 20`, `--offset 40`, and so on until a page has fewer than 20 runs. A full page never proves no matching active run exists; increasing the limit once is insufficient. Apply this complete lookup after a lost start response too. If a page fails or the earlier start outcome remains uncertain, report the incomplete lookup and do not start another run.
2. Record the run ID, Line name, Factory, URL, and start time immediately. Resolve `factory.key` with `islo factory current --factory KEY_OR_UUID --output json`. Follow [chat links](chat-embeds.md) for the URL `/factories/FACTORY_KEY/runs/lines/RUN_ID`. Preserve a known explicit URL if key lookup fails; never start another run because link lookup failed.
3. Tell the user once: "Started line `<line>` (run `<id>`). Waiting for it to finish." Include the run link.
4. Read status immediately, then wait with a sleep or await tool before each new poll. Use delays of 15 seconds, 30 seconds, 60 seconds, then 60–120 seconds. Split a delay into shorter awaits if the chat's tool limit requires it. Never busy-poll or end the turn expecting the run to wake you later.

```bash
islo factory line-run status <run-id> -o json
```

Use the same explicit Factory selection for every command. Track elapsed wall time and the latest stage progress across polls. About every five minutes, post one line with the current stage and elapsed time. Do not send an update for every poll.

Stop waiting at 45 minutes from the recorded start time. Cap each sleep and request timeout to the remaining time. At the deadline, read status once more if possible, then report the run ID, link, current stage, elapsed time, and planned next step. Leave the run active. Propose resuming observation of this run, or diagnosing a stall when the evidence supports that. This is the planned handoff limit for an active run; do not end observation early merely because a stage is slow.

If status fails with a network or authentication error, retry it three times after sleeps of 15, 30, and 60 seconds. These retries count toward the same deadline. After all three retries fail, report that observation is blocked, with the last known status, run ID, link, elapsed time, and next step. Do not label the run failed or start a replacement. In a pre-authenticated sandbox, report the credential problem without attempting login or looking for credential files.

For several runs, keep one polling loop with a deadline and next-poll time per run. Continue when all runs finish, or continue independent follow-up work as each finishes. Do not restart a run that is still active or whose status is unknown.

## Separate stage failure from run completion

Read the top-level run `status`; a stage's `status`, `outcome`, or a timestamp alone does not establish completion.

A failed stage goes to the Line Manager. It gets plain attempts up to `max_attempts`, then up to two diagnosed recovery attempts. Keep waiting through those attempts. The Manager can temporarily park a run during recovery, so `stopped` after a failed stage needs inspection before a handoff.

On an apparent end state, read stages. Read events only when the state is ambiguous, an error needs explanation, or progress appears stuck.

```bash
islo factory line-run stages <run-id> -o json
islo factory line-run events <run-id> -o json
```

For a stopped run following stage failure, inspect events for an active Manager recovery turn or scheduled retry. Match `manager_turn_started` and `manager_turn` events by `payload.workflow_run_id`; inspect `payload.resolved_action` and later events for the Manager's decision. An old unmatched start alone does not prove recovery is still active. If recovery is underway, continue polling without intervening. If the evidence is unclear, recheck after the next sleep; do not wait indefinitely on an old Manager event. An explicit pause or a Manager decision to park for input takes precedence over recovery assumptions.

## Read the result and continue

The CLI uses `succeeded` for successful completion, not `completed`. Handle the run-level states as follows:

| Run state | Action |
|---|---|
| `succeeded` | Read the stages' outputs and artifacts. Summarize them in 2–4 lines, then use them to continue the original task in this turn. Do not merely offer to continue or claim downstream work is done. |
| `failed` | Read stages and the run's error. Use events if the failing stage or cause is unclear, including a failure between stages. Report the stage or transition and cause. Fix within the original scope and start a fresh run after the old one has ended, then wait again. If the fix needs an owner decision or work outside scope, ask the user with the evidence. |
| `cancelled` | End observation. Read the available stage outputs and cancellation reason from status or events. Report cancellation and ask the user how to proceed. Leave the run untouched; do not resume it or start a replacement without user direction. |
| `stopped` | After ruling out active Manager recovery, report the pause or parking reason and ask the user how to proceed. Leave the run untouched. |
| Any other value | Keep observing within the deadline. If the value is unfamiliar, inspect events and report it without inventing a terminal state. |

The observed CLI represents a parked run as `stopped`. If another version returns `parked`, inspect it like `stopped`. A null `completed_at` does not authorize resuming a paused run.

Waiting grants no run-control permission. Never `stop`, `steer`, `retry`, or `ask` a run you are only observing unless the user requested it or evidence shows no stage progress for 15 minutes. Diagnose such a stall with read-only status, stages, and events first. Manager retries count as progress; elapsed run time alone is insufficient. Never override an explicit pause, bypass a question, or issue controls while Manager recovery is active. Keep any recovery within the original authorization and avoid duplicate external effects.
