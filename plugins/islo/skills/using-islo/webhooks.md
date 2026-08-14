# Webhooks

Use this reference for lower-level incoming and outgoing webhooks. Factory lines can also be triggered by webhook or integration events — see `factory.md` for line-level triggers.

## Incoming webhooks

Incoming webhooks react to external HTTP events (GitHub, Stripe, Slack, custom services).

Discovery:

```bash
islo schema webhook
islo webhook incoming --help
```

### Actions

| Action | Purpose |
|--------|---------|
| `ensure-sandbox` | Create or ensure a sandbox from a template |
| `resume-sandbox` | Resume a paused sandbox |
| `pause-sandbox` | Pause a running sandbox |
| `delete-sandbox` | Delete a sandbox |
| `deliver-to-port` | Forward the request to a port inside a running sandbox |
| `trigger-job` | Start a job run with params from the payload |

### Create example

```bash
islo webhook incoming create \
  --name github-runner \
  --action ensure-sandbox \
  --ensure-image ghcr.io/islo-labs/islo-runner:latest \
  --ensure-vcpus 2 \
  --ensure-memory-mb 2048 \
  --ensure-disk-gb 20 \
  --gateway-profile default \
  --path /webhooks/github \
  --hmac-secret-name github-secret \
  --hmac-secret-value "$GITHUB_WEBHOOK_SECRET"
```

Trigger a job from an incoming webhook:

```bash
islo webhook incoming create \
  --name trigger-review \
  --action trigger-job \
  --job-name pr-review \
  --path /webhooks/review
```

### Sandbox template fields

For `ensure-sandbox`, the sandbox template requires `image`, `vcpus`, `memory_mb`, and `disk_gb`. See `islo schema webhook` for the full `IncomingWebhookSandboxTemplate` schema including `init`, `lifecycle`, `sources`, `snapshot_name`, and `setup_scripts`.

Default image: `ghcr.io/islo-labs/islo-runner:latest`

### Management

```bash
islo webhook incoming ls
islo webhook incoming get <id>
islo webhook incoming rm <id> --force
```

Use `--output json` for structured output. Use `--request-json` or `--request-toml` for full configuration when the CLI flags are not enough.

## Outgoing webhooks

Outgoing webhooks send HTTP notifications from job steps or automation events. Check `islo schema webhook` and docs MCP for the current outgoing surface.

## Auth separation

Incoming webhook secrets verify the **sender** (HMAC, bearer, basic auth). Outbound provider credentials use gateway profiles and integrations — keep these paths separate.

## Factory line webhooks vs incoming webhooks

| | Factory line webhook trigger | Incoming webhook |
|--|------------------------------|------------------|
| **Config** | `[trigger] type = "webhook"` in `line.toml` | `islo webhook incoming create` |
| **Target** | Starts a line run | Sandbox lifecycle, port delivery, or job trigger |
| **Use when** | Multi-stage orchestration needed | Simple event → sandbox or single job |

For integration-triggered lines (GitHub PR opened, Linear issue updated), use `integration_trigger` in `line.toml` instead. See `factory.md`.

## Things to avoid

- Do not store webhook HMAC secrets or provider API tokens in job params or sandbox env.
- Do not use incoming webhooks for multi-stage orchestration when a Factory line is the right abstraction.
- Do not assume webhook CLI flags from memory — run `islo schema webhook` for the current surface.
