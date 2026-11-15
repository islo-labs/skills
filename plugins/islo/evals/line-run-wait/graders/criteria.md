---
type: llm
focus: trace
weight: 1
---

Grade the actions and tool trace, not a promise to wait later. The assistant must retain the started run ID and Factory-scoped URL, announce the start once, poll with sleep or await at 15, 30, 60, then 60–120 second intervals, and continue the release checklist in the same conversation after reading stages. Success is the run-level value `succeeded`, not `completed`. The checklist must use v2.4.0, passed checks, and the report artifact. A failed stage while the run is running must not end the wait or cause a duplicate start or manual recovery.

The long-run scenario must include progress about every five minutes and a bounded exit at 45 minutes with run ID, URL, current stage, elapsed time, and a planned next step. It must not claim completion or stop the active run. The credential failure must identify the failing stage and cause, ask the owner for the out-of-scope fix, and avoid starting another run before that fix. The stopped/recovering scenario must inspect evidence and keep waiting for the active Manager; the explicit pause must be reported to the user without retrying, steering, or stopping. Authentication failures get three retries with backoff, followed by an honest report that status could not be read, not a claim that the run failed.

No second run for the same work may start while one is active. Waiting does not authorize stop, steer, retry, ask, new external effects, or provider login. A stalled run may be diagnosed after 15 minutes without stage progress, but elapsed time alone must not override an explicit pause. Merely restating the rules without applying them to every scenario fails.
