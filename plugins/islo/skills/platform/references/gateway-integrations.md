# Gateway and integrations

Provider credentials without tokens in the sandbox: GitHub, Slack, model providers, custom APIs, gateway profiles.

## Core rule

Do not put provider tokens inside the sandbox by default. Ask the user to connect providers through a chat card and use the `default` gateway profile. The gateway injects credentials on allowed outbound requests at the network layer; real tokens stay in the control plane.

Sandboxes may expose phantom placeholder env vars (`GITHUB_TOKEN`, `SLACK_TOKEN`, values starting `islo_p`). Some tools read them directly; the gateway replaces them on egress. Treat them as placeholders, not secrets.

## Flow

Before or alongside deploying, post one card for every provider a trigger or tool needs. Explain why it is needed, then put the link alone in its own paragraph:

```markdown
[GitHub](/integrations?connect=github&view=connect)

[Slack](/integrations?connect=slack&view=connect)
```

Use a known integration preset id for `connect`: `github`, `slack`, `linear`, `sentry`, `notion`, `atlassian`, `anthropic`, `cursor`, or `openai`. Outbound provider ids also include `gitlab` and `npm`; a provider without a matching UI preset remains a plain integrations link.

The browser card reads connection status with the user's session and opens the existing dialog over chat. Never claim an integration is connected from sandbox evidence. Ask the user to say when done, or offer to deploy now; the line starts once connected. Deploy does not check integration readiness.

Do not run `islo login --tool`, `islo status`, or `islo factory triggers list --with-status` inside a sandbox. Their connection-status calls are rejected. The card is the source of truth for not connected, pending owner approval, and connected states.

Sandboxes pick up the `default` profile automatically. Inspect the gateway profile when a provider request fails:

```bash
islo gateway ls
```

Create a custom profile only for stricter egress, extra hosts, or different auth rules:

```bash
islo gateway create --name my-profile --default-action deny
islo gateway my-profile add-rule --host api.example.com --action allow --provider-key my-key --auth-mode bearer
islo use <sandbox> --gateway-profile my-profile
```

If you change gateway rules after a sandbox was created, recreate or reconnect the sandbox and retest.

## GitHub

Post a GitHub connect card before sandbox work that touches private repos or the GitHub API. Let the browser card show connection status. Covers `gh` commands, REST and GraphQL to allowed hosts, private checkout during `islo use` bootstrap (see the sandboxes reference), and Actions runner registration.

## Slack

Post a Slack connect card; the `default` profile already allows Slack hosts. Do not store a bot token in `islo.yaml`, job params, setup scripts, or sandbox env unless the user explicitly bypasses gateway-managed credentials.

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

- Provider call fails: post a connect card for the browser to resolve status, run `islo gateway ls` for the profile, then check allow rules cover the destination host.
- `Repository not found` or 404 on a private repo: usually GitHub is not connected, or the clone happened outside `islo use` source bootstrap.
- 401 from a provider API: confirm connection and host allow rules before debugging inside the sandbox.
- Rules changed after sandbox creation: recreate or reconnect the sandbox.
