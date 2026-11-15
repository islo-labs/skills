---
name: integrations
description: Check Islo provider connections and use connected integrations. Use before calling GitHub, Linear, Slack, or another external provider from an Islo agent or sandbox, and when diagnosing provider authentication failures.
---

# Check and use integrations

Before calling a provider, check its connection in the scope the task needs. An environment variable or phantom placeholder token does not prove a connection. Checking never involves a login command.

## Check connection status

Run this read-only check and read `integrations`:

```bash
islo status -o json
```

Classify each needed provider by its provider ID:

- **Connected**: at least one matching entry has `connected: true` in the required scope.
- **Missing**: a reliable result has no connected entry for that provider in the required scope. A pending connection is not connected.
- **Unknown**: the command fails, integration status is unavailable, or `integrations_error` is non-null. Missing or malformed status fields are also unknown. An empty `integrations` array with null `auth.tenant_name` is unknown, including the top-level `tenant_name` in older output. A null tenant name alone does not invalidate a nonempty, otherwise valid result.

If status omits scope and the task requires one, inspect the provider detail:

```bash
islo api /integrations/PROVIDER_ID
```

Read `tenant.connected` for Tenant scope or `user.connected` for Personal scope. For example, Cursor Jobs need Tenant scope; a Personal connection cannot satisfy that requirement. A failed lookup or a missing or malformed required scope is unknown.

Sandbox identities see Tenant connections. A Personal-only connection may therefore appear missing from a sandbox; the result describes the connection visible to that identity.

Re-check status before retrying a failed provider call or investigating a trigger that did not fire. Connection status does not grant permission for external writes or provider events.

## Use a connected provider

Read [using-providers.md](references/using-providers.md) for GitHub and Linear commands, gateway credentials, and provider environment variable names. Never look for credentials on disk or run a provider login flow.

For gateway profiles, host allow rules, custom APIs, and Islo inference routing, read [gateway-integrations.md](../platform/references/gateway-integrations.md).
