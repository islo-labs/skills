# Webhooks

Use this reference for lower-level incoming and outgoing webhooks. Factory lines can also be triggered by webhook or integration events — see `factory.md`.

## Discovery

```bash
islo schema webhook
islo webhook incoming --help
```

Do not write webhook config from memory. `islo schema webhook` includes the CLI surface and sandbox template shape.

## Incoming webhooks

Incoming webhooks react to external HTTP events (GitHub, Stripe, Slack, custom services). Check `islo schema webhook` for available actions and configuration.

### Create examples

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

```bash
islo webhook incoming create \
  --name trigger-review \
  --action trigger-job \
  --job-name pr-review \
  --path /webhooks/review
```

### Management

```bash
islo webhook incoming ls
islo webhook incoming get <id>
islo webhook incoming rm <id> --force
```

Use `--output json` for structured output. Use `--request-json` or `--request-toml` when CLI flags are not enough.

## Outgoing webhooks

Check `islo schema webhook` and docs MCP for the current outgoing surface.

## Auth separation

Incoming webhook secrets verify the **sender** (HMAC, bearer, basic auth). Outbound provider credentials use gateway profiles and integrations — keep these paths separate.

## Factory line webhooks vs incoming webhooks

| | Factory line webhook trigger | Incoming webhook |
|--|------------------------------|------------------|
| **Setup** | Deploy a line with a webhook trigger | `islo webhook incoming create` |
| **Target** | Starts a line run | Sandbox lifecycle, port delivery, or job trigger |
| **Use when** | Multi-stage orchestration needed | Simple event → sandbox or single job |

For integration-triggered lines (GitHub PR opened, Linear issue updated), use a Factory line with an integration trigger. See `factory.md` and `islo schema factory`.

## Things to avoid

- Do not store webhook HMAC secrets or provider API tokens in job params or sandbox env.
- Do not use incoming webhooks for multi-stage orchestration when a Factory line is the right abstraction.
- Do not assume webhook flags or template fields from memory — run `islo schema webhook`.
