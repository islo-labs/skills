# Incoming webhooks and the SDK

## Incoming webhooks

An incoming webhook reacts to an external HTTP event with a sandbox action, without line orchestration. For workflows triggered by events, use a factory line trigger instead (the factory-lines skill).

Do not write webhook config from memory:

```bash
islo schema webhook
islo webhook incoming --help
```

Create examples:

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

Management:

```bash
islo webhook incoming ls
islo webhook incoming get <id>
islo webhook incoming rm <id> --force
```

Use `--output json` for structured output and `--request-json` or `--request-toml` when flags are not enough. For outgoing webhooks, check `islo schema webhook` for the current surface.

Auth separation: incoming webhook secrets verify the sender; outbound provider credentials come from gateway profiles. See `gateway-integrations.md`. Store the returned receiver URL in the external provider.

## SDK

For services, dashboards, bots, and custom launchers built on Islo. Use the CLI when a human or coding agent works interactively in a repo; use the SDK when code needs to manage sandboxes, start Line runs, manage webhooks, configure gateway profiles, or inspect runs.

Packages: TypeScript `@islo-labs/sdk`, Python `islo`; generated SDKs also exist for Go. They are generated from the OpenAPI/Fern pipeline, so method names change; check docs MCP or the package reference before writing non-trivial code.

```bash
npm install @islo-labs/sdk
```

```typescript
import { Islo } from "@islo-labs/sdk";

const client = new Islo();
```

```bash
pip install islo
```

```python
from islo import Islo

client = Islo()
```

Both read `ISLO_API_KEY` from the environment. Common env vars: `ISLO_API_KEY`, `ISLO_BASE_URL`, `ISLO_COMPUTE_URL`; confirm current names in docs before deployment instructions. Do not embed the key in source.

Design advice: explicit names for sandboxes, Agents, Lines, webhooks, and profiles; define reusable Agents and reference them in Line stages; keep credentials in integrations and gateway profiles; persist run IDs for long-running automation and correlate with events.
