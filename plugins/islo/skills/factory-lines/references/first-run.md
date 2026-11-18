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
islo factory line-run list --line <line-name> --factory <key-or-uuid> --output json
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

Name the observed step and offer **one** next action with a link. For example, if a deployed Line has no runs: "Your Line is set up, but it has not run yet. Try it on one real issue with Run it now."

Link that suggestion to `[LINE_NAME](/factories/FACTORY_KEY/lines/LINE_NAME?view=card)`. Resolve `factory.key` from the inventory and URL-encode the Line name. Do not treat deployment as completion of the user's first run. Offer the run without starting it unless the user authorized its input and effects.

For a run waiting for an answer, link its question at `/factories/FACTORY_KEY/runs/lines/RUN_ID?view=question`. For a finished run, link its result at `/factories/FACTORY_KEY/runs/lines/RUN_ID?view=card`. Use `/factories/FACTORY_KEY/runs?view=inbox` for Runs. Follow [chat-embeds.md](chat-embeds.md) for exact link behavior. For a missing provider, use its connect card. For missing resources, offer a [Line draft card](chat-embeds.md#line-draft-cards) and link the relevant Factory's Lines or Machines page.

If you start a run, follow [wait-for-line-runs.md](wait-for-line-runs.md), read its outputs, and continue the user's task.

## What Machine levels let your Lines do

Inspect the Machine's level and latest build with `islo factory machine get <machine-name>` before answering "can my Lines do full verification?" A source checkout alone does not establish test or runtime readiness.

| Machine level | What it prepares for your Lines |
|---|---|
| `source` | Repository checkouts for editing code and opening PRs. Builds, tests, and a running app are not prepared at this level. |
| `build` | Adds the toolchain and build setup so Agents can build and run the repository's tests on the Machine. Build-level Machine verification runs install and build; it does not itself run tests. |
| `verify` | Adds runtime setup, startup, health checks, and verification targets so Agents can start the app and check it end to end. |

For a source-level Machine, explain that build and test work needs a build-level Machine, and starting and checking the app end to end needs a verify-level Machine. Link the observed Machine at `/factories/FACTORY_KEY/machines/MACHINE_NAME?view=card` and offer the readiness upgrade as the next step. Do not claim that choosing a level proves a particular PR passes. The Line still needs to run the intended checks and report evidence.

For an app already deployed elsewhere, recommend the [remote controller pattern](remote-verification.md). The Machine runs the test tools against that endpoint. Machine level alone does not grant network access or credentials. Use [machines.md](machines.md) for Machine operations and exact readiness contracts.
