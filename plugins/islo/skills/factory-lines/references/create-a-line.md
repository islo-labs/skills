# Build the approved Factory

Start with [factory-design.md](factory-design.md). This page starts only after the user has approved its complete blueprint. Keep the approved effects checklist nearby while implementing and verifying.

## Dependency order

1. Select the approved existing Factory explicitly or create the approved new one. Confirm `islo factory current` or pass `--factory KEY|UUID` to scoped commands. Never let an inherited default silently select the destination.
2. Connect required providers through the **local** CLI, after approval. Check `islo status`. Configure tenant-scoped environments and gateway profiles, including explicit allow rules for custom MCP hosts, before creating dependent sandboxes. Follow the platform gateway reference. Do not put provider tokens in manifests, prompts, or sandbox env.
3. Create declarative Factory Knowledge only when the Agent needs it. Skills and procedures belong in repositories or Agent skill attachments, not Knowledge.
4. Create or update each Machine with the approved repositories, capabilities, environment, lifecycle, and gateway profile. Follow [machines.md](machines.md). Inspect the build and wait for a published, usable version before creating or running dependent Agents. A build parked for Author questions is not ready. A failed build is not ready.
5. Validate and create or update reusable Agents from the live `islo schema agent`. Confirm their Machine, harness/model pairing, instructions, Skills, MCP servers, and Knowledge using [agents-and-managers.md](agents-and-managers.md). Prepare a prompt Agent Manager only if the blueprint calls for one.
6. If a stage needs typed contracts, deterministic commands, snapshots, fan-out, verification, or lifecycle controls that Agent stages cannot express, scaffold and deploy an internal Job using `islo job init` and `islo schema job --short`. Its user-facing responsibility remains an Agent interaction. Keep Job-specific files and names out of the user decision flow.
7. Author the Line using `islo schema factory --short` and [line-manifest.md](line-manifest.md). Agent stages name their reusable Agent and, where shared workspace is intended, their `sandbox_name`. Use the default Agent `input`/`output` contract on current CLI schema. Validate shared-sandbox Machine consistency. Configure Manager, transitions, trigger, limits, and destinations. Validate and deploy the Line **last**.

Check the installed CLI help before invoking create/update commands. If it lacks a required Agent or Manager surface, report the specific missing command or schema field and stop dependent deployment; do not disguise the gap with a Job-first design.

## Static validation and isolated run

Validate draft Agents and the Line with the installed CLI. Dry-run any internal Job deploy. Validation must cover references, supported fields, gateway host rules, and the shared-sandbox Machine invariant. Inspect each created resource with its `get` or `list` command and record version/build status.

Run one approved Agent stage in isolation with representative input, using the supported Agent or Line test surface on the installed CLI. Check the semantic output and that only approved effects occurred. If the stage is compiled through an internal Job, use its isolated run command and inspect the resulting output. Do not trigger a provider event for this test unless the blueprint approved it.

## End-to-end verification

Run the deployed Line once with approved test input. For an integration trigger, send **one** approved test event with its expected-effects checklist prepared beforehand. Inspect the Line run's status, stage timeline, Agent sessions, outputs, sandbox grouping, and result destination. Compare every external write or provider event with the approved effects checklist. Report any inference failure separately from setup or routing results; lack of model credentials does not prove setup failed. A Line redeploy is needed when it pins an internal Job version that changed.

For run inspection and recovery, use [run-control-and-debugging.md](run-control-and-debugging.md). Schedules belong in the Line `[trigger]`; Machine refresh schedules belong in the Machine spec.
