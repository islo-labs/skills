# Gateway and integrations

Provider credentials without tokens in the sandbox: GitHub, Slack, model providers, custom APIs, gateway profiles.

## Core rule

Do not put provider tokens inside the sandbox by default. Connect providers with `islo login --tool <provider>` and use the `default` gateway profile. The gateway injects credentials on allowed outbound requests at the network layer; real tokens stay in the control plane.

Sandboxes may expose phantom placeholder env vars (`GITHUB_TOKEN`, `SLACK_TOKEN`, values starting `islo_p`). Some tools read them directly; the gateway replaces them on egress. Treat them as placeholders, not secrets.

## Flow

```bash
islo login --tool github
islo login --tool slack
islo use <sandbox>
```

Sandboxes pick up the `default` profile automatically. Inspect when something fails:

```bash
islo gateway ls
islo status
```

Create a custom profile only for stricter egress, extra hosts, or different auth rules:

```bash
islo gateway create --name my-profile --default-action deny
islo gateway my-profile add-rule --host api.example.com --action allow --provider-key my-key --auth-mode bearer
islo use <sandbox> --gateway-profile my-profile
```

If you change gateway rules after a sandbox was created, recreate or reconnect the sandbox and retest.

## GitHub

Connect before sandbox work that touches private repos or the GitHub API; `islo status` confirms it shows connected. Covers `gh` commands, REST and GraphQL to allowed hosts, private checkout during `islo use` bootstrap (see the sandboxes reference), and Actions runner registration.

## Slack

Connect Slack outside the sandbox; the `default` profile already allows Slack hosts. Do not store a bot token in `islo.yaml`, job params, setup scripts, or sandbox env unless the user explicitly bypasses gateway-managed credentials.

## Incoming webhook secrets are different

An incoming webhook secret (HMAC, bearer, basic) verifies requests coming INTO Islo. A provider token authorizes calls going OUT. Keep the two paths separate in explanations and code; see `webhooks-and-sdk.md`.

## Islo inference

Islo-managed models are separate from provider integrations: platform-owned upstream credentials, credit billing, routed via the gateway.

- Model list: `GET /inference/models` or the docs MCP server.
- OpenAI-compatible base: `https://gateway.islo.dev/inference/openai/v1`
- Anthropic-compatible base: `https://gateway.islo.dev/inference/anthropic`
- Codex defaults to OpenAI (`model_provider = "islo"`). Set `model_provider = "islo_inference"` on a Codex `run_agent` step to use this OpenAI-compatible base. Claude uses the Anthropic-compatible base via `ANTHROPIC_BASE_URL`. Pairing is in the factory-lines harness/models reference.

Provider-managed egress (Claude and Cursor CLIs calling provider APIs) goes through `/gateway/proxy/{*path}` with the customer's connected credentials. Do not mix the paths: inference URLs are for direct model calls, gateway proxy is for provider SDK and CLI egress.

## Escape hatch

Users can pass their own tokens. Warn that it weakens the no-token-in-sandbox model, scope the example, and avoid logging secrets.

## Troubleshooting

- Provider call fails: `islo status` for the integration, `islo gateway ls` for the profile, then check allow rules cover the destination host.
- `Repository not found` or 404 on a private repo: usually GitHub is not connected, or the clone happened outside `islo use` source bootstrap.
- 401 from a provider API: confirm connection and host allow rules before debugging inside the sandbox.
- Rules changed after sandbox creation: recreate or reconnect the sandbox.
