# Verify against an existing environment

Use this guidance when a user wants a Line to test PRs on an existing preview environment, ephemeral environment, or external cluster.

## Recommend the controller pattern

For "how would I…" questions, give a short recommendation first: "Use the Machine as the test controller. Pass your preview URL to a verification Agent, which runs your tests against it. Supply access through an Islo environment and gateway host rules."

Then offer a [Line draft card](chat-embeds.md#line-draft-cards). Do not start resource creation or an interactive credential flow to answer an approach question. Follow [factory-design.md](factory-design.md) for inventory, unresolved choices, and approval before deployment or external writes.

The Machine hosts the test runner and tools. The preview application stays on its existing infrastructure as a remote endpoint. Do not propose moving or redeploying it into the Machine. A build-level Machine can prepare the test tools; use verify level when the Machine must also start and check local services. See [Machine levels](first-run.md#what-machine-levels-let-your-lines-do).

## Pass the target between stages

Recommend this flow, adapting stage names to the user's deployment process:

1. Resolve or deploy the preview for the requested PR. If the preview already exists, resolve it without creating another environment.
2. Return its URL and the deployed PR revision as a Line output. Keep credentials out of outputs.
3. Pass that output to a verification Agent as semantic input. Use the installed `islo schema agent` and `islo schema factory --short` for the exact output contract and transition bindings.
4. Wait for the endpoint's documented readiness check. Confirm the deployed revision matches the PR before running tests.
5. Run the repository's API or browser tests against the supplied URL. Return the target, revision, checks, results, and artifact links.

Do not assume a URL file crosses stage sandbox boundaries. Use [Line outputs](line-manifest.md) even when stages use different Machines. Use a Script Agent for deterministic readiness checks and test commands; add a Prompt Agent only when interpretation is needed. If the live Agent and Line schemas cannot express a required contract, report that specific gap and stop dependent deployment. Do not substitute a Job.

## Configure access without logging in inside the VM

Use an Islo environment attached to the controller Machine and gateway allow rules for the destination hosts. Configure both before running dependent Agents. Follow the [environment setup card](chat-embeds.md#environment-setup-cards) contract for missing values: list key names, let the user enter values privately, and wait for "finished". Do not ask for secrets in chat or put them in prompts, manifests, URLs, outputs, or logs.

For an API protected by a bearer token, name the required token key in the setup card and configure the gateway to inject it for the allowed host. Include the preview host and any identity, artifact, or control-plane hosts the checks actually call. Dynamic previews need a scoped host rule that covers their actual names. Follow [gateway-integrations.md](../../platform/references/gateway-integrations.md) for the supported rule and auth modes. An environment value alone does not allow a destination through the gateway.

AWS and Kubernetes access need their own non-interactive plan. Install the required CLI and test tools on the Machine. Establish which scoped cloud identity, credential mechanism, cluster context, and API endpoints the workflow needs. Supply required settings through the environment setup flow, and allow the relevant hosts. AWS request signing and Kubernetes authentication are not generic bearer-token injection. Confirm that the available environment and gateway mechanisms support the required auth before promising access. Never run `aws sso login`, an interactive cloud login, or an interactive `kubectl` authentication plugin inside the VM. If no supported non-interactive path exists, name the missing capability and stop that dependent step.

A host allow rule does not create a route to a private VPC or cluster. Confirm the controller can reach the target through the user's supported network path. If it cannot, explain the reachability requirement before offering to run checks. Browser tests can use the preview URL without cloud or cluster access when the tests need only the application's public interface.

## Inspect and prove the setup

Inside a sandbox, inspect the attached environment and gateway profile with `islo factory machine get <machine-name>`. Never run `islo environment list` or `islo gateway ls` inside a sandbox; both return `ACCESS_DENIED`. From the user's own agent, those commands work. For tenant-wide configuration, link [Environments](/settings/environments) and [Gateway](/settings/gateway). Never read environment values to check access.

The draft card should identify the preview URL source, PR revision, test command, required key names, allowed hosts, and result destination. List deployment, test-data writes, and cleanup effects in `you_get.writes` for approval. Default to leaving an existing preview in place; do not assume the Line owns it.

After approval and access setup, check reachability and readiness, then run once against an approved PR. Record authentication or network failures separately from test failures. If a Prompt Agent reaches an inference boundary without provider credentials, report that limitation separately; do not describe the verification tests as passed.
