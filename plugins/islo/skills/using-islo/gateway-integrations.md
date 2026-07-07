# Gateway integrations

Use this reference for GitHub, Slack, model providers, custom provider APIs, gateway profiles, provider keys, and keeping real tokens out of sandboxes.

## Core rule

Do not put provider tokens inside the sandbox by default. Use connected providers and gateway profiles.

Inside the sandbox, tools may see placeholder credentials such as `GITHUB_TOKEN`, `GH_TOKEN`, or `SLACK_TOKEN`. Treat those as phantom tokens, not secrets. Egress through the Islo gateway replaces matching outbound requests with real credentials outside the sandbox.

Claude Code, Cursor agent, and Codex are already installed inside Islo sandboxes. If the user connected the matching integration before using the sandbox, these agents can run without an in-sandbox login. Do not copy local auth files or API keys into the sandbox just to make the agent start.

## Flow

1. The user connects a provider outside the sandbox, for example GitHub or Slack.
2. A gateway profile defines which hosts and paths a sandbox may call.
3. A gateway rule can attach a `provider_key` and auth strategy.
4. The sandbox is created with that `gateway_profile`.
5. Tools inside the sandbox call normal provider APIs.
6. The gateway injects real credentials for allowed requests.

The sandbox should only get the profile key and phantom tokens. Real provider tokens stay in the control plane or provider integration store.

## Common CLI flow

Check exact flags with `islo schema`, `ISLO_HELP=full islo`, or docs MCP before finalizing commands.

Typical flow:

```bash
islo login --tool github
islo login --tool slack
islo login --tool claude
islo login --tool cursor
islo login --tool openai
islo gateway profile create <profile>
islo gateway rule create <profile> --host api.github.com --provider-key github --auth-mode bearer
islo use <sandbox> --gateway-profile <profile>
```

For project defaults, set the gateway profile in `islo.yaml`:

```yaml
gateway_profile: default
```

## GitHub

Use gateway integration for:

- `gh api`
- GitHub REST and GraphQL calls
- private repository access where supported
- GitHub Actions runner registration flows

The GitHub runner pattern combines:

- an incoming webhook from GitHub
- a sandbox image with the GitHub runner and `gh`
- a gateway profile that allows GitHub API calls
- phantom GitHub tokens in the sandbox

Reference implementation: `https://github.com/islo-labs/islo-agents` for agent jobs, and the Islo GitHub runner image in the Islo platform repos for webhook-driven self-hosted runner bootstrapping.

## Slack

Use gateway integration for Slack API calls from sandboxed agents. Connect Slack outside the sandbox, then allow Slack hosts in the gateway profile and use the matching provider key.

Do not store a Slack bot token in `islo.yaml`, job params, setup scripts, or sandbox env unless the user explicitly asks to bypass gateway-managed credentials.

## Incoming webhooks are different

Incoming webhook secrets verify requests coming into Islo. They are not provider API tokens for outbound calls.

Example distinction:

- GitHub webhook HMAC secret: verifies GitHub sent the event.
- GitHub provider token: authorizes outbound calls to GitHub APIs.

Keep those paths separate in explanations and code.

## Escape hatches

Users can override env vars or pass their own tokens. If they ask for that, warn that it weakens the no-token-in-sandbox model. Keep examples scoped and avoid logging secrets.

## Troubleshooting

If provider calls fail:

- Check the sandbox was created with the expected `gateway_profile`.
- Check the gateway profile has an allow rule for the destination host.
- Check the rule has the intended `provider_key` and auth mode.
- Check the provider was connected with `islo login --tool <provider>` or an equivalent control-plane flow.
- Check the tool is calling the provider host directly, not a mirror or proxy host the rule does not match.
