# job.toml anatomy

Pattern, not drop-in. Confirm every field against `islo schema job --short` before deploying. The examples below are validated in CI by `scripts/validate_examples.sh` against the installed CLI.

A job is one stage's execution unit: typed params in, a sandbox, ordered steps, typed outputs out. Params and outputs are the line's contract; write them first. Harness and model live here on the `run_agent` step, not in `line.toml`.

## Full example: reproduce stage of a bug-fix line

<!-- validate: job -->
```toml
[job]
name = "bug-fix-reproduce"
version = "0.2.0"
description = "Confirm the bug and capture it in a failing test"

# Typed params. Substituted as {{name}} in step fields before execution.
# Every param a schedule will use must have a default. Reserved: run_id.
[job.params.repo]
type = "string"
required = false
default = "your-org/your-app"
description = "GitHub repository in owner/name form"
pattern = "^[^/]+/[^/]+$"

[job.params.report]
type = "string"
required = true
description = "The bug report text"

[job.params.work_key]
type = "string"
required = true
description = "Stable identifier for this piece of work; names the sandbox"
pattern = "^[a-zA-Z0-9][a-zA-Z0-9._-]{0,62}$"

# Declared outputs are transition fuel: the line routes on them, and the
# agent must set them. If omitted, run_agent results are not published.
[outputs.reproduced]
type = "boolean"
required = true
description = "Whether the bug could be reproduced"

[outputs.failing_test]
type = "string"
required = true
description = "The test that now captures the bug"

[run]
fail_fast = true
timeout = 5400
teardown_on_complete = false
workdir = "/workspace/your-app"

[run.sandbox]
# provision = fresh sandbox per run (default, prefer it).
# ensure = create if missing, reattach if present; use only when stages must
# share a workspace, and derive the name from a param so runs stay isolated.
mode = "ensure"
name = "bugfix-{{work_key}}"
image = "ghcr.io/islo-labs/islo-runner:latest"
# Harness code (servers, CLIs, test assets) ships in a snapshot, never inline.
snapshot_name = "your-line-snapshot-v1"
vcpus = 4
memory_mb = 4096
disk_gb = 10
# Gateway profile injects provider credentials; no tokens in the manifest.
gateway_profile = "default"
internet_enabled = true
init = { type = "full" }

[run.sandbox.lifecycle]
pause_after_idle = 1800
delete_after = 172800

[[run.tasks]]
name = "reproduce"

# Idempotent fetch-or-clone before the agent step. The default gateway
# profile injects GitHub credentials on egress, so the plain https URL works
# with no token in the manifest. The checkout keeps repo skills and prompts
# the source of truth: the agent reads them at run time, never a copy.
[[run.tasks.steps]]
name = "checkout"
exec = [
  "bash",
  "-lc",
  "set -euo pipefail\nif [ ! -d /workspace/your-app/.git ]; then\n  git clone https://github.com/your-org/your-app /workspace/your-app\nfi\ncd /workspace/your-app\ngit fetch origin main\ngit checkout -B fix/{{work_key}} origin/main\n",
]

# run_agent for the judgment work. Harness: claude, cursor, codex, or custom.
# model is optional; the harness default applies when omitted.
[[run.tasks.steps]]
name = "reproduce"

[run.tasks.steps.run_agent]
mode = "session"
harness = "claude"
prompt = { type = "literal", value = "Read and follow .claude/skills/reproduce-bugs/SKILL.md in /workspace/your-app.\n\nYou are on branch fix/{{work_key}}. Bug report:\n{{report}}\n\nReproduce this bug and add a test that fails because of it. Do not fix the bug. Commit only the failing test.\n\nSet reproduced=true only if the new test fails for the reported reason. Set failing_test to the test path and name." }
session = "bug-fix-reproduce"
```

## The parts that matter

**Params and outputs are the contract.** The line's transitions bind params from trigger outputs, literals, and prior stages' outputs (`line-manifest.md`). Output types: string, integer, number, boolean, object, array. The routing condition `$.outputs.reproduced` in the line only works because this manifest declares `outputs.reproduced`.

**Sandbox mode.** Default to `provision` with `teardown_on_complete = true`: a fresh environment per stage, handoff via a pushed branch or declared outputs. Use `ensure` with a param-derived `name` only when stages of one run must share a workspace, as above. `reuse` attaches to an existing sandbox and is rare.

**Snapshots carry harness code.** Executable trees, test harnesses, and assets live in a snapshot named by `snapshot_name`, built from `snapshot-src/` in your line repo. Never embed code in `job.toml` as base64 or heredoc bootstrap. See the platform skill's sandboxes reference for building snapshots.

**Repos carry prompts and skills.** Check the repo out with an idempotent fetch-or-clone exec step before the agent step, as in the example, and keep the `run_agent` prompt a short literal that points at the checked-out skill or prompt file. The `default` gateway profile injects `GH_TOKEN`/`GITHUB_TOKEN` on egress, so private clones need no token in the manifest. Do not copy procedural content into Islo Knowledge; deploy rejects procedural knowledge anyway. Warning: `sandbox.sources[]` validates (it is declared in the server schema) but is currently not implemented on the live platform, so the checkout silently never happens; do not use it until the backend fix ships.

**Schedules on standalone jobs** use a `[schedule]` section (cron, timezone, enabled) and require a default for every param. For a line, schedule the line trigger instead; see `triggers.md` and `standalone-jobs.md`.

**Verification.** `islo job init <name> --with-verification` scaffolds the optional evaluation layer (`[verification] enabled = true`). Use it on stages whose outputs gate transitions.

## Validation

```bash
islo job init <name>
islo job deploy --path jobs/<name>/job.toml --dry-run
```

Always scaffold with `islo job init` and edit from there. "Extra inputs are not permitted" means an unknown key; diff against `islo schema job --short`.
