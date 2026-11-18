# Get to a first successful run

Use this path for "how do I use Islo?", "what should I do now?", or questions about verification readiness.

## Find the user's current step

Inspect the selected Factory with read-only commands before recommending setup. Follow the [login check](../SKILL.md#log-in-before-line-creation) if Line creation is needed. Confirm the intended Factory rather than assuming the chat's inherited default is correct.

```bash
islo factory current --factory <key-or-uuid> --output json
islo factory machine list --factory <key-or-uuid> --output json
islo agent list --factory <key-or-uuid> --output json
islo factory line list --factory <key-or-uuid> --output json
islo factory line get <line-name> --factory <key-or-uuid> --output json
islo factory line-run list --line <line-name> --paged --limit 20 --factory <key-or-uuid> --output json
islo factory machine get <machine-name> --factory <key-or-uuid> --output json
```

Inspect only relevant Lines and Machines. Check provider status with the [integrations skill](../../integrations/SKILL.md#check-connection-status). Treat a failed inventory request as unknown, not evidence that a resource is missing. If run history is paginated, check more pages before claiming a Line has never run.

The user's path is:

1. Connect the providers the workflow needs.
2. Create a Machine with the repository and the readiness level the workflow needs. Wait for a usable published version.
3. Create reusable Agents for the work.
4. Connect the Agents in a Line with an input and a done condition.
5. Run the Line on one real item, such as an issue or a pull request.
6. Answer questions and review the result in Runs, including outputs and PRs.
7. Improve the instructions, tests, or routing based on that result, then run again.

Name the observed step and offer to do **one** next action yourself. Do not treat deployment as completion of the user's first run.

For example, if a deployed Line has no runs: "Your Line `ship-ticket-ci` is set up but has not run yet. Want me to run it on one ticket? Which one?" A Line with an integration trigger can still run manually. Read its inputs with `islo factory line get <line-name>`, ask for the one real item, and name the effects the run will have, such as opening a PR. After the user confirms, start it:

```bash
islo factory line run <line-name> --param KEY=VALUE --factory <key-or-uuid>
```

Then follow [wait-for-line-runs.md](wait-for-line-runs.md): wait, read its outputs, and report the result and any PR. If the run asks a question, show it and relay the user's answer.

Show objects as links for the user to see, not as tasks for the user to do. In Agent chat, use [chat-embeds.md](chat-embeds.md): the Line card at `/factories/FACTORY_KEY/lines/LINE_NAME?view=card`, a run at `/factories/FACTORY_KEY/runs/lines/RUN_ID?view=card`, or its question at `?view=question`. In the user's own agent, use full `https://app.islo.dev/...` URLs. Resolve `factory.key` from the inventory and URL-encode path segments.

Hand a step to the user only when you cannot do it: connecting a provider (follow the [chat connection gate](chat-embeds.md#integration-connect-cards) in Agent chat, or link `https://app.islo.dev/settings/integrations?connect=PROVIDER` in the user's own agent), entering secret values (use an [environment setup card](chat-embeds.md#environment-setup-cards)), or a command blocked where you run. For missing resources, offer a [Line draft card](chat-embeds.md#line-draft-cards) and create the resources yourself after approval.

## What Machine levels let your Lines do

Inspect the Machine's level and latest build with `islo factory machine get <machine-name>` before answering "can my Lines do full verification?" A source checkout alone does not establish test or runtime readiness.

| Machine level | What it prepares for your Lines |
|---|---|
| `source` | Repository checkouts for editing code and opening PRs. Builds, tests, and a running app are not prepared at this level. |
| `build` | Adds the toolchain and build setup so Agents can build and run the repository's tests on the Machine. Build-level Machine verification runs install and build; it does not itself run tests. |
| `verify` | Adds runtime setup, startup, health checks, and verification targets so Agents can start the app and check it end to end. |

For a source-level Machine, explain that build and test work needs a build-level Machine, and starting and checking the app end to end needs a verify-level Machine. Link the observed Machine at `/factories/FACTORY_KEY/machines/MACHINE_NAME?view=card` and offer the readiness upgrade as the next step. Do not claim that choosing a level proves a particular PR passes. The Line still needs to run the intended checks and report evidence.

For an app already deployed elsewhere, recommend the [remote controller pattern](remote-verification.md). The Machine runs the test tools against that endpoint. Machine level alone does not grant network access or credentials. Use [machines.md](machines.md) for Machine operations and exact readiness contracts.
