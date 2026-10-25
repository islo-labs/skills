# Build the approved Factory

Start with [factory-design.md](factory-design.md). This page starts only after the user has approved its complete blueprint. Keep the approved effects checklist nearby while implementing and verifying.

## Dependency order

1. Select the approved existing Factory explicitly or create the approved new one. Confirm `islo factory current` or pass `--factory KEY|UUID` to scoped commands. Never let an inherited default silently select the destination.
2. Connect required providers through the **local** CLI, after approval. Check `islo status`. Configure tenant-scoped environments and gateway profiles, including explicit allow rules for custom MCP hosts, before creating dependent sandboxes. Follow the platform gateway reference. Do not put provider tokens in manifests, prompts, or sandbox env.
3. Create or update each Machine with the approved repositories, capabilities, environment, lifecycle, and gateway profile. Follow [machines.md](machines.md). Inspect the build and wait for a published, usable version before creating or running dependent Agents. A build parked for Author questions is not ready. A failed build is not ready.
4. Validate and create or update reusable Agents from the live `islo schema agent`. Confirm their Machine, harness/model pairing, instructions, Skills, and MCP servers using [agents-and-managers.md](agents-and-managers.md). Prepare a prompt Agent Manager only if the blueprint calls for one.
5. If a stage needs typed contracts, deterministic commands, snapshots, fan-out, verification, or lifecycle controls that Agent stages cannot express, scaffold and deploy an internal Job using `islo job init` and `islo schema job --short`. Its user-facing responsibility remains an Agent interaction. Keep Job-specific files and names out of the user decision flow.
6. Author the Line using `islo schema factory --short` and [line-manifest.md](line-manifest.md). Agent stages name their reusable Agent and, where shared workspace is intended, their `sandbox_name`. Use the Agent runtime's default `input`/`output` contract. Validate shared-sandbox Machine consistency. Configure Manager, transitions, trigger, limits, and destinations. Validate and deploy the Line **last**.

Check the installed CLI help before invoking create/update commands. If it lacks a required Agent or Manager surface, report the specific missing command or schema field and stop dependent deployment; do not disguise the gap with a Job-first design.

## Static validation and isolated run

Validate draft Agents and the Line with the installed CLI. Dry-run any internal Job deploy. Validation must cover references, supported fields, gateway host rules, and the shared-sandbox Machine invariant. Inspect each created resource with its `get` or `list` command and record version/build status.

For an Agent stage, the CLI has no standalone Agent run command. Make a temporary manual Line containing just that Agent stage, an entry transition that passes representative `input`, and a completion transition. Generate a unique Line name with a random suffix. Continue only when `islo factory line get <temporary-name>` explicitly reports that the name does not exist; stop on any other error. Track whether this workflow deployed the Line, and remove it only when that deployment succeeded. Give the stage a unique `sandbox_name` so it cannot collide with the production Line. Include the deployment, run, expected external effects, and removal in the approved blueprint. Do not run a side-effecting Agent until those effects are approved.

Use the live schema to confirm the fields. Replace `{{unique_suffix}}` with at least eight random lowercase hexadecimal characters before validation. Keep the resulting name for cleanup:

<!-- validate: line -->
```toml
[line]
name = "isolated-agent-check-{{unique_suffix}}"

[trigger]
type = "manual"

[[stages]]
id = "check"
agent = "existing-agent"
sandbox_name = "isolated-check-{{line_run_id}}"

[[transitions]]
id = "start"
type = "conditional"
from = "trigger"
to = "check"
when = { op = "always" }
params = { input = { type = "input", name = "input" } }

[[transitions]]
id = "finish"
type = "conditional"
from = "check"
to = "done"
when = { op = "always" }
```

Validate and deploy the uniquely named Line, run it with `--param input=...`, and inspect `islo factory line-run status` and `islo factory line-run events` for the Agent's semantic `output`, sandbox identity, and approved effects. After recording the result, stop the run if it is still active and confirm it is stopped. Then remove the temporary Line with `islo factory line rm <temporary-name> --force` only if this workflow deployed it, even when the run failed. Removing a Line does not stop its run or delete the run's sandbox, so do not treat Line removal as run or sandbox cleanup. If the stage is compiled through an internal Job, use its isolated Job run and inspect the output. Do not trigger a provider event for this test unless the blueprint approved it.

## End-to-end verification

Run the deployed Line once with approved test input. For an integration trigger, send **one** approved test event with its expected-effects checklist prepared beforehand. Inspect the Line run's status, stage timeline, Agent sessions, outputs, sandbox grouping, and result destination. Compare every external write or provider event with the approved effects checklist. Report any inference failure separately from setup or routing results; lack of model credentials does not prove setup failed. A Line redeploy is needed when it pins an internal Job version that changed.

For run inspection and recovery, use [run-control-and-debugging.md](run-control-and-debugging.md). Schedules belong in the Line `[trigger]`; Machine refresh schedules belong in the Machine spec.
