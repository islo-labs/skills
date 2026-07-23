# Gateway integrations

Use this reference for GitHub, Slack, model providers, custom provider APIs, gateway profiles, provider keys, and keeping real tokens out of sandboxes.

## Core rule

Do not put provider tokens inside the sandbox by default. Use connected providers and gateway profiles.

Islo uses two related mechanisms:

1. **Gateway rule injection** — a gateway profile with `--provider-key` and `--auth-mode` rules injects real credentials on allowed outbound requests at the network layer. Code can call matching provider hosts without embedding secrets.
2. **Phantom tokens** — the sandbox env may also contain placeholder values such as `GITHUB_TOKEN`, `GH_TOKEN`, `SLACK_TOKEN`, `NPM_TOKEN`, or `OPENAI_API_KEY` (`islo_p…`). When a tool sends one of these placeholders in a request, the gateway replaces it with the real credential on egress.

For **Islo CLI flows** (`islo use`, `--source github://…`, connected integrations, gateway profiles on the sandbox), auth is wired automatically. Do not tell users to manually embed tokens for normal CLI source checkout or provider setup.

For **manual scripts inside the sandbox** (raw `curl`, hand-written `git clone`, custom HTTP clients), the request must include the phantom token or rely on a matching gateway injection rule. A truly naked request to a provider host may stay unauthenticated if neither mechanism applies.

Treat phantom tokens as placeholders, not secrets. Do not copy real provider tokens into the sandbox unless the user explicitly chooses that escape hatch.

Claude Code, Cursor agent, and Codex are already installed inside Islo sandboxes. If the user connected the matching integration before using the sandbox, these agents can run without an in-sandbox login. Do not copy local auth files or API keys into the sandbox just to make the agent start.

## Flow

1. The user connects a provider outside the sandbox, for example GitHub or Slack.
2. A gateway profile defines which hosts a sandbox may call and how credentials are injected.
3. The sandbox is created or reconnected with that `gateway_profile`.
4. Islo CLI-managed flows and env-aware tools authenticate automatically.
5. Manual outbound calls use gateway injection rules and/or phantom tokens in the request.

The sandbox should only get the profile key and phantom placeholders. Real provider tokens stay in the control plane or provider integration store.

### Verify GitHub access

After connecting GitHub and creating or reconnecting a sandbox with the expected `gateway_profile`:

```bash
# CLI-managed API call — should work without manual token wiring:
gh api user

# Or verify phantom-token replacement directly:
curl -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user
```

If both fail, check the integration, gateway profile, and whether the sandbox predates recent gateway changes.

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
islo gateway rule create <profile> --host github.com --provider-key github --auth-mode basic --auth-username x-access-token
islo use <sandbox> --gateway-profile <profile>
# inside the sandbox — CLI tools and Islo-managed flows authenticate automatically:
gh api user
```

Gateway rules with `--provider-key` and `--auth-mode` inject credentials for allowed hosts. Phantom tokens in the sandbox env are replaced when a tool sends them. Islo CLI flows wire this up automatically; do not add manual token steps for normal `islo use` or `--source github://…` setup.

If you change gateway rules after the sandbox was created, recreate or reconnect the sandbox and retest.

For project defaults, set the gateway profile in `islo.yaml`:

```yaml
gateway_profile: default
```

## GitHub

Use gateway integration for:

- `gh api` and other `gh` commands
- GitHub REST and GraphQL calls
- private repository access through connected integrations
- GitHub Actions runner registration flows

### Sources and private repos

For `islo use --source github://owner/repo` or `sources:` in `islo.yaml`, connect GitHub first:

```bash
islo login --tool github
islo use <sandbox> --source github://owner/repo --gateway-profile <profile>
```

Islo clones private repos through the connected integration automatically. Do not tell users to manually embed `$GITHUB_TOKEN` in the clone URL for normal CLI source checkout.

If the user clones manually inside the sandbox (outside Islo source bootstrap), use the phantom token:

```bash
git clone "https://x-access-token:${GITHUB_TOKEN}@github.com/OWNER/REPO"
```

Or configure a credential helper that reads `$GITHUB_TOKEN` for `github.com` HTTPS URLs.

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
- Check the gateway profile has allow rules for the destination host (`api.github.com`, `github.com`, etc.).
- Check the rule has the intended `provider_key` and auth mode.
- Check the provider was connected with `islo login --tool <provider>` or an equivalent control-plane flow.
- Check the tool is calling the provider host directly, not a mirror or proxy host the rule does not match.
- If you changed gateway rules after the sandbox was created, recreate or reconnect the sandbox and retest.
- For CLI source checkout failures on private repos, verify `islo login --tool github` completed before sandbox creation.

Common misleading failures:

- **`Repository not found` / 404 on a private GitHub repo** — usually means GitHub is not connected, the sandbox lacks the expected gateway profile, or a **manual** naked `git clone https://github.com/…` was used instead of Islo CLI source checkout. It rarely means the repo is missing.
- **401 from GitHub or Slack APIs** — verify with `gh api user` or an explicit phantom-token curl before debugging gateway rules.
