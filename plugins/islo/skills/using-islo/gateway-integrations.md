# Gateway integrations

Use this reference for GitHub, Slack, model providers, custom provider APIs, gateway profiles, provider keys, and keeping real tokens out of sandboxes.

## Core rule

Do not put provider tokens inside the sandbox by default. Connect providers with `islo login --tool <provider>` and attach a `gateway_profile` to the sandbox.

The gateway injects credentials on allowed outbound requests at the network layer. Connect the integration, create or use a gateway profile with allow rules for the provider hosts, then run `islo use` — you do not manually wire tokens for normal CLI workflows.

The sandbox may also expose phantom placeholder env vars (`GITHUB_TOKEN`, `GH_TOKEN`, `SLACK_TOKEN`, … with `islo_p…` values). Some tools read these directly; the gateway can replace them on egress when they appear in a request. Treat them as placeholders, not secrets.

Claude Code, Cursor agent, and Codex are already installed inside Islo sandboxes. If the user connected the matching integration before using the sandbox, these agents can run without an in-sandbox login. Do not copy local auth files or API keys into the sandbox just to make the agent start.

## Flow

1. Connect providers outside the sandbox: `islo login --tool github` (and slack, openai, etc. as needed).
2. Use an existing gateway profile (often `default`) or create one with allow rules for provider hosts.
3. Create or reconnect the sandbox with `--gateway-profile <name>` or `gateway_profile:` in `islo.yaml`.
4. Tools inside the sandbox call provider APIs on allowed hosts; the gateway injects credentials automatically.

Real provider tokens stay in the control plane or integration store. The sandbox gets the profile name and phantom placeholders only.

## Common CLI flow

Check exact flags with `islo schema`, `ISLO_HELP=full islo`, or docs MCP before finalizing commands.

Typical flow:

```bash
islo login --tool github
islo login --tool slack
islo gateway ls
islo gateway create --name my-profile --default-action allow
islo gateway my-profile add-rule --host api.github.com --provider-key github --auth-mode bearer
islo use <sandbox> --gateway-profile my-profile
```

Many accounts already have a `default` gateway profile with provider allow rules. Check with `islo gateway default` before creating a new profile.

For project defaults:

```yaml
gateway_profile: default
```

If you change gateway rules after a sandbox was created, recreate or reconnect the sandbox and retest.

## GitHub

Use gateway integration for:

- `gh api` and other `gh` commands
- GitHub REST and GraphQL calls to allowed hosts
- private repository access when GitHub is connected
- GitHub Actions runner registration flows

Connect GitHub before sandbox work that touches private repos or the GitHub API:

```bash
islo login --tool github
islo status   # confirm github shows as connected
```

Repo checkout during `islo use` bootstrap is covered in `sandbox-lifecycle.md`, not here.

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

- Run `islo status` and confirm the integration is connected.
- Check the sandbox was created with the expected `gateway_profile` (`islo gateway ls`, `islo gateway <name>`).
- Check allow rules cover the destination host (`api.github.com`, `github.com`, `slack.com`, etc.).
- Check the rule has the intended `provider_key` and `auth_mode` when credential injection is required.
- If you changed gateway rules after the sandbox was created, recreate or reconnect the sandbox.

Common misleading failures:

- **`Repository not found` / 404 on a private GitHub repo** — usually GitHub is not connected, or the clone happened outside `islo use` source bootstrap. See `sandbox-lifecycle.md`.
- **401 from a provider API** — confirm the integration is connected and the gateway profile allows that host before debugging from inside the sandbox.
