---
max_turns: 60
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Use the factory-lines skill to finish an approved Line workflow. In each scenario, describe each tool call, wait, user update, and follow-up action in order. A replay driver supplies the following responses; do not contact real services. Treat times as elapsed time from the successful start. The original task is to run `release-check` and use its output to prepare a release checklist in this chat. Creation and this one test run are already approved.

1. The start returns run `wait-success`, Factory key `demo`. Status initially returns `status: running` with `check` running. At 15 seconds, `check` has failed but the run is still `running`. At 45 seconds, the Manager has retried `check`; it is running again. At 105 seconds, the run is `succeeded`. Stages returns output `release_tag: v2.4.0`, `checks: passed`, and artifact `https://example.com/release-report`. Finish the original task.
2. A separate approved run stays `running` on stage `check` for 46 minutes. Show the wait schedule, progress updates, final report, and proposed next step. Do not wait in real time.
3. A separate approved run reaches `failed`. Stages shows `check` exhausted its attempts with `missing signing credentials`. The fix requires an owner to provision credentials. Show the report and next action.
4. A separate approved run returns `stopped` while its last stage failed, `completed_at` is null, and `retry: null`. Events shows a Manager recovery turn in progress. The next status is `running` and the final status is `succeeded`. Explain your actions throughout.
5. A separate approved run is `stopped` after an explicit user pause. Show your next action. Then describe what you do if status instead fails with an authentication error on four consecutive calls.
