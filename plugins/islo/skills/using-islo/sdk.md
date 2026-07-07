# Islo SDK

Use this reference when the user is building a service, script, dashboard, bot, integration, or custom automation launcher on top of Islo.

Do not build per-language deep dives in this skill. The SDKs are generated from Islo's OpenAPI/Fern pipeline, so exact method names can change. Use docs MCP and the package references for the current surface.

## When to use SDK instead of CLI

Use the SDK when code needs to:

- create or manage sandboxes programmatically
- start durable jobs or schedule-backed launchers from an internal tool
- create or manage incoming webhooks
- configure gateway profiles and rules
- inspect runs, events, sessions, or sandbox status
- integrate Islo into a product workflow

Use the CLI when a human or coding agent is working interactively in a repo.

## Packages

Primary packages:

- TypeScript: `@islo-labs/sdk`
- Python: `islo`

Generated SDKs also exist for Go.

## TypeScript quick start

```bash
npm install @islo-labs/sdk
```

```typescript
import { Islo } from "@islo-labs/sdk";

const client = new Islo();
```

The SDK reads `ISLO_API_KEY` from the environment by default. Check the package reference or docs MCP for current environment names and method paths before writing non-trivial code.

## Python quick start

```bash
pip install islo
```

```python
from islo import Islo

client = Islo()
```

The Python SDK also reads Islo auth from the environment by default. Verify constructor names and token-provider helpers against the current package docs before writing production examples.

## Auth and base URLs

Use `ISLO_API_KEY` for server-side tools and CI. Do not embed the key in source code.

Common environment variables include:

- `ISLO_API_KEY`
- `ISLO_BASE_URL`
- `ISLO_COMPUTE_URL`

Confirm current names in docs MCP or package docs before giving exact deployment instructions.

## SDK design advice

- Prefer explicit names for sandboxes, jobs, webhooks, and gateway profiles.
- Keep job behavior in `job.toml`; use SDK code to deploy, schedule, trigger, or inspect.
- Keep provider credentials in Islo integrations and gateway profiles, not in SDK config files.
- For long-running automation, persist run IDs and correlate them with Islo events.
- For webhooks, store the returned receiver URL in the external provider and manage webhook config through the authenticated SDK/API.

## Before writing code

1. Search docs MCP for the entity, such as `sandbox SDK`, `jobs SDK`, `incoming webhooks SDK`, or `gateway profiles SDK`.
2. Check the package README/reference for current generated method names.
3. Use the smallest SDK example that answers the user. Do not paste a generated reference into the chat.
