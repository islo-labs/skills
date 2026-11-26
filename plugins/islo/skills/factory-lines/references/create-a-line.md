# Build the approved Factory

Start with [factory-design.md](factory-design.md). This page starts only after the user has approved its complete blueprint. Keep the approved effects checklist nearby while implementing and verifying.

Verify that the Islo CLI is logged in before creating resources, following the skill's [login check](../SKILL.md#log-in-before-line-creation). Request local login only for missing or invalid authentication, then wait for confirmation and recheck.

## Groups or fanout

Use a group when different Agents or different work can run independently: for
example `plan -> [backend, ui] -> review`, with review rerunning only `ui` when
needed. Use fanout when the same Agent handles many inputs, such as reviewing
`api` and `web`. A group member may itself fan out. Declare a covering join and
separate sandboxes for group members; the same Agent in two members otherwise
collides at its default `<agent>-{{line_run_id}}` sandbox. See
[line-manifest.md](line-manifest.md) for `allowed`, `targets`, and output defaults.

## Dependency order

1. Confirm that all blueprint choices and required selectors are resolved and the complete blueprint is approved. If answers are still missing, follow the [integration gate's readiness check](chat-embeds.md#integration-connect-cards) before proceeding. Select the approved Factory explicitly with `--factory KEY|UUID` for read-only commands. Never let an inherited default silently select the destination.
2. After approval, check providers with the [integrations skill](../../integrations/SKILL.md#check-connection-status). Complete the [chat connection gate](chat-embeds.md#integration-connect-cards) before creating anything, including a new Factory. Then create the approved Factory if needed and confirm `islo factory current`. Configure tenant-scoped environments and gateway profiles, including explicit allow rules for custom MCP hosts, before creating dependent sandboxes. When a required environment name has no saved value, use an [environment setup card](chat-embeds.md#environment-setup-cards) and wait for the user to reply "finished". Follow the platform gateway reference. Do not put provider tokens in manifests, prompts, or sandbox env.
3. Create or update each Machine with the approved repositories, capabilities, environment, lifecycle, and gateway profile. Follow [machines.md](machines.md). Inspect the build and wait for a published, usable version before creating or running dependent Agents. A build parked for Author questions is not ready. A failed build is not ready.
4. Validate and create or update reusable Agents from the live `islo schema agent`. Use a Script Agent for deterministic commands, a Decision Agent for typed choice or score questions, and a Prompt Agent for open-ended judgment or tool use. Confirm each type's supported Machine, commands or questions, harness/model pairing, instructions, Skills, and MCP servers using [agents-and-managers.md](agents-and-managers.md). Prepare a Prompt Agent Manager only if the blueprint calls for one.
5. Confirm that every new stage uses a reusable Agent. If `islo schema agent` and `islo schema factory --short` cannot express a required snapshot, fan-out with reduction, verification, lifecycle, or contract capability, report the missing capability and stop the dependent design and deployment. Do not author a Job or look for a fallback in the Job schema. Leave existing Job stages in place and add no new ones.
6. Author the Line using `islo schema factory --short` and [line-manifest.md](line-manifest.md). Agent stages name their reusable Agent and, where shared workspace is intended, their `sandbox_name`. Use only the Agent-stage contract fields exposed by the installed schema. Validate shared-sandbox Machine consistency. Configure Manager, transitions, trigger, limits, and destinations. Validate and deploy the Line **last**.

Check the installed CLI help before invoking create/update commands. If it lacks a required Agent or Manager surface, report the specific missing command or schema field and stop dependent deployment; do not substitute a Job.

## Static validation and isolated run

Validate draft Agents and the Line with the installed CLI. Validation must cover references, supported fields, gateway host rules, and the shared-sandbox Machine invariant. Inspect each created resource with its `get` or `list` command and record version/build status.

For an Agent stage, the CLI has no standalone Agent run command. Make a temporary manual Line containing just that Agent stage, an entry transition that passes representative `input`, and a completion transition. Generate a unique Line name with a random suffix. Continue only when `islo factory line get <temporary-name>` explicitly reports that the name does not exist; stop on any other error. Track whether this workflow deployed the Line, and remove it only when that deployment succeeded. Give the stage a unique `sandbox_name` so it cannot collide with the production Line. Include deployment, run, and removal in the approved blueprint. List every test run that writes outside Islo in the draft card's `you_get.writes`; a test without external effects needs no mention in the card. Do not run a side-effecting Agent until those effects are approved.

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

Validate and deploy the uniquely named Line, run it with `--param input=...`, and follow [Waiting for line runs you start](wait-for-line-runs.md). Read the final stages for the Agent's semantic `output`, sandbox identity, and approved effects. If observation ends while the run is active, paused, or its status is unknown, leave the temporary Line in place; do not stop the run for cleanup. Once the run is `succeeded` or `failed` and its result is recorded, remove the temporary Line with `islo factory line rm <temporary-name> --force` only if this workflow deployed it, even when the run failed. Removing a Line does not stop its run or delete the run's sandbox, so do not treat Line removal as run or sandbox cleanup. Do not trigger a provider event for this test unless the blueprint approved it.

## End-to-end verification

Run the deployed Line once with approved test input. For an integration trigger, send **one** approved test event with its expected-effects checklist prepared beforehand. Follow [Waiting for line runs you start](wait-for-line-runs.md) for the resulting run, including runs started by a test event. After it finishes, inspect its stage timeline, Agent sessions, outputs, sandbox grouping, and result destination. Compare every external write or provider event with the approved effects checklist. Report any inference failure separately from setup or routing results; lack of model credentials does not prove setup failed.

For run inspection and recovery, use [run-control-and-debugging.md](run-control-and-debugging.md). Schedules belong in the Line `[trigger]`; Machine refresh schedules belong in the Machine spec.

## Outcome in chat

After the final successful deploy, post exactly one Line outcome card on its own line, using the Factory key from `factory.key` in `islo factory current --output json`: `[LINE_NAME](/factories/FACTORY_KEY/lines/LINE_NAME?view=card)`. URL-encode the name. Follow [chat-embeds.md](chat-embeds.md#creation-outcomes); do not stop at a text-only deployment confirmation.
