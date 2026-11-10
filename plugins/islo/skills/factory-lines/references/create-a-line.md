# Build the approved Factory

Start with [factory-design.md](factory-design.md). Intake identifies the Machines and reusable Agents for each stage, their semantic inputs and outputs, and approved effects. This workflow implements the approved blueprint. Keep its effects checklist nearby while verifying.

## Prepare Machines and Agents

1. Select the approved Factory explicitly or create the approved new one. Confirm `islo factory current` or pass `--factory KEY|UUID` to scoped commands.
2. Check provider connections through the local CLI with `islo status`. Configure approved tenant environments and gateway profiles, including allow and authentication rules for MCP hosts. Follow the platform gateway reference. Keep provider tokens out of manifests and prompts.
3. Create or update the approved Machines. Follow [machines.md](machines.md) for repositories, capabilities, environment, lifecycle, and gateway profile. Wait for a published, usable version. A failed build or one parked for Author questions is not ready.
4. Inspect existing Agents with `islo agent list` and `islo agent get <name>`. Reuse suitable Agents. Author create or update TOML using `islo schema agent --short` and [agent-manifest.md](agent-manifest.md). Make the Machine, prompt or commands or questions, and supported harness, model, provider, effort, Skills, and MCP settings explicit.
5. Validate complete Agent configurations, then create or update the approved Agents. Update files omit the immutable name. Inspect saved Agents before wiring the Line. Prepare a Prompt Agent Manager only if the blueprint calls for one.

```bash
islo schema agent --short
islo agent validate agent.toml
islo agent create agent.toml
islo agent update <name> agent-update.toml
islo agent get <name>
```

Check installed help and update-schema semantics before applying partial updates. If a required capability is absent, report the specific gap and stop dependent work.

## Author and deploy the Line

Use `islo schema factory --short` and [line-manifest.md](line-manifest.md). Each stage names its reusable Agent with `agent = "..."`. Declare stage params and outputs, transition bindings, trigger, limits, and result destinations in `line.toml`. Keep reusable execution configuration in the Agent; use stage overrides only for deliberate differences in this Line.

Agent stages may share a `sandbox_name` containing `{{line_run_id}}`. Validate that every stage in a shared group resolves to the same Machine. They share files, while their Agent sessions remain separate.

```bash
islo schema factory --short
islo factory line validate line.toml
islo factory line deploy line.toml
islo factory line get <name>
```

Inspect created resources and record saved configuration, Line version, and Machine readiness. Complete runnable manifests are maintained and validated in [the validated PR-review example in islo-labs/islo-agents](https://github.com/islo-labs/islo-agents/tree/59ec4503b68212e047af0b0d42645c4c55e0505b/examples/pr-review).

## Verify with a minimal manual Line

The CLI has no standalone Agent run command. Build a temporary manual Line with one Agent stage, representative input bindings, an entry transition from `trigger`, and a completion transition to `done`. Use the live schema to author it. Include deployment, run, expected external effects, and removal in the approved blueprint.

Generate a unique temporary Line name with at least eight random lowercase hexadecimal characters. Continue only when `islo factory line get <temporary-name>` explicitly reports that the name does not exist; stop on any other error. Use a separate `sandbox_name` containing `{{line_run_id}}`. Track whether this workflow successfully deployed the temporary Line.

Validate, deploy, and run the temporary Line:

```bash
islo factory line validate temporary-line.toml
islo factory line deploy temporary-line.toml
islo factory line run <temporary-name> --param input="<representative-input>"
islo factory line-run status <run-id>
islo factory line-run stages <run-id>
islo factory line-run events <run-id>
```

Choose params from the actual stage contract; use `--param-json` or `--params-file` for typed values. Inspect outputs, sandbox identity, and approved effects. Separate inference failures from setup and routing results. A provider failure after inference begins does not establish that setup failed.

After recording results, stop any active run and confirm its stopped status. Remove the temporary Line with `islo factory line rm <temporary-name> --force` only if this workflow deployed it, even if its run failed. Removing a Line does not stop its run or delete its sandbox. Clean up only resources this test created, within the approved blueprint. Do not send a provider event for this isolated test unless approved.

## Verify the deployed trigger

Run the deployed Line once with approved input. For an integration trigger, send one approved test event using [triggers.md](triggers.md). Prepare the expected-effects checklist before sending it.

Inspect status, stages, events, Agent sessions, outputs, shared workspaces, and result destinations. Compare external writes against the approved effects. Report inference failures separately; verification without model credentials can establish setup and routing up to the inference boundary, but cannot establish model-dependent results.

Use [run-control-and-debugging.md](run-control-and-debugging.md) for recovery. Line schedules belong in `[trigger]`; Machine refresh schedules belong in the Machine spec.
