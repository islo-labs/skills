# Gateway and integrations

Provider credentials without tokens in the sandbox: GitHub, Slack, model providers, custom APIs, gateway profiles.

## Core rule

Do not put provider tokens inside the sandbox by default. Use the `default` gateway profile. The gateway injects credentials on allowed outbound requests at the network layer; real tokens stay in the control plane.

Sandboxes may expose phantom placeholder env vars (`GITHUB_TOKEN`, `SLACK_TOKEN`, values starting `islo_p`). Some tools read them directly; the gateway replaces them on egress. Treat them as placeholders, not secrets.

## Flow

Follow the [integrations skill](../../integrations/SKILL.md#check-connection-status) for the connection check and the [chat connection gate](../../factory-lines/references/chat-embeds.md#integration-connect-cards) for connect cards and when work can continue.

Sandboxes pick up the `default` profile automatically. Inside a chat sandbox, never run `islo gateway ls` or `islo environment list`. Both return `ACCESS_DENIED: Operation is not allowed from inside a sandbox`. Inspect the Machine's attached environment and gateway profile instead:

```bash
islo factory machine get <machine-name>
```

For tenant-wide configuration, link [Environments](/settings/environments) and [Gateway](/settings/gateway). From an authenticated local terminal outside a sandbox, `islo gateway ls` lists profiles. Do not read environment values to troubleshoot access.

Create a custom profile only for stricter egress, extra hosts, or different auth rules. Run these administration commands from an authenticated local terminal outside a sandbox:

```bash
islo gateway create --name my-profile --default-action deny
islo gateway my-profile add-rule --host api.example.com --action allow --provider-key my-key --auth-mode bearer
islo use <sandbox> --gateway-profile my-profile
```

If you change gateway rules after a sandbox was created, recreate or reconnect the sandbox and retest.

For a Line testing an existing preview or external cluster, follow [remote-verification.md](../../factory-lines/references/remote-verification.md). The Machine runs the tests against the remote endpoint. Use an environment setup card for missing credential names and allow rules for the destination hosts. Cloud request signing, cluster authentication, and private-network reachability need a supported non-interactive path; a bearer rule alone does not supply them.

## GitHub

Before using private repos or the GitHub API, check GitHub with the [integrations skill](../../integrations/SKILL.md#check-connection-status). Follow the [chat connection gate](../../factory-lines/references/chat-embeds.md#integration-connect-cards) for cards and waiting. This applies to `gh` commands, REST and GraphQL to allowed hosts, private checkout during `islo use` bootstrap (see the sandboxes reference), and Actions runner registration.

## Slack

Check Slack with the [integrations skill](../../integrations/SKILL.md#check-connection-status). Follow the [chat connection gate](../../factory-lines/references/chat-embeds.md#integration-connect-cards) for cards and waiting. The `default` profile already allows Slack hosts. Do not store a bot token in `islo.yaml`, job params, setup scripts, or sandbox env unless the user explicitly bypasses gateway-managed credentials.

## Incoming webhook secrets are different

An incoming webhook secret (HMAC, bearer, basic) verifies requests coming INTO Islo. A provider token authorizes calls going OUT. Keep the two paths separate in explanations and code; see `webhooks-and-sdk.md`.

## Islo inference

Islo-managed models are separate from provider integrations: platform-owned upstream credentials, credit billing, routed via the gateway.

- Model list: `GET /inference/models` or the docs MCP server.
- OpenAI-compatible base: `https://gateway.islo.dev/inference/openai/v1`
- Anthropic-compatible base: `https://gateway.islo.dev/inference/anthropic`
- Codex defaults to OpenAI (`model_provider = "islo"`). Set `model_provider = "islo_inference"` on a Codex or Claude session-mode internal Job step to use the matching Islo inference protocol. OpenCode in sandboxes targets the OpenAI-compatible base by default (phantom `opencode.json`). Pairing is in the factory-lines harness/models reference.

Provider-managed egress (Claude and Cursor CLIs calling provider APIs) goes through `/gateway/proxy/{*path}` with the customer's connected credentials. Do not mix the paths: inference URLs are for direct model calls, gateway proxy is for provider SDK and CLI egress.

## Escape hatch

Users can pass their own tokens. Warn that it weakens the no-token-in-sandbox model, scope the example, and avoid logging secrets.

## Troubleshooting

- Provider call fails: re-check status with the [integrations skill](../../integrations/SKILL.md#check-connection-status). Follow the [chat connection gate](../../factory-lines/references/chat-embeds.md#integration-connect-cards) for cards and waiting. Inspect the attached profile with `islo factory machine get <machine-name>`, then use [Gateway](/settings/gateway) to check its destination host rules. Never run `islo gateway ls` inside a sandbox.
- `Repository not found` or 404 on a private repo: usually GitHub is not connected, or the clone happened outside `islo use` source bootstrap.
- 401 from a provider API: confirm connection and host allow rules before debugging inside the sandbox.
- Rules changed after sandbox creation: recreate or reconnect the sandbox.
