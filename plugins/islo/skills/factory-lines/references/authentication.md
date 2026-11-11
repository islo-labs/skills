# Check CLI authentication before Line creation

Before inventory, design, or resource creation, run this non-interactive, read-only check in the environment where the agent will use the CLI:

```bash
islo factory list --output json
```

Interpret the result before continuing:

- Exit code 0 with a Factory array, including `[]`, confirms that authentication is valid. Continue without asking the user to log in. An empty list means there are no available Factories, not that login is required.
- An explicit authentication error, such as `Not authenticated`, `Authentication required`, `AUTH_REQUIRED`, `AUTH_TOKEN_EXPIRED`, or `AUTH_TOKEN_INVALID`, means authentication is missing or invalid. Only then ask the user to run `islo login` in their local terminal outside a sandbox. Wait for confirmation, then repeat the check before continuing.
- A network error, timeout, permission denial, server error, missing CLI, or unexpected response does not establish that authentication is missing. Report and diagnose that error; do not ask for login solely because the command failed.

Use the CLI's configured credentials, including injected API keys or a login session. Do not infer valid authentication from an environment variable's presence, inspect credential files, or start an interactive login inside a sandbox. Local login does not necessarily update a sandbox's injected credentials. If the repeated check still fails after confirmation, report the remaining authentication problem instead of repeatedly asking the user to log in.

This check authenticates access to Islo. It does not establish provider connection status or select the user's intended Factory. Continue using browser integration cards and explicit Factory selection in the normal workflow. Do not run `islo status` or `islo login --tool` inside a sandbox for this check.

## CLI support

`islo factory list --help` documents listing Factories available to the current tenant and supports `--output json`. The CLI's [Factory command handler](https://github.com/islo-labs/islo-cli/blob/9043cca0d012760f326b15a39f14d00807b46600/crates/cli/src/commands/factory.rs) obtains credentials through `context::auth_token()` and prints the returned array. The [API client](https://github.com/islo-labs/islo-cli/blob/9043cca0d012760f326b15a39f14d00807b46600/crates/web-api-client/src/factory.rs) makes an authenticated `GET /factories`. The [auth implementation](https://github.com/islo-labs/islo-cli/blob/9043cca0d012760f326b15a39f14d00807b46600/crates/auth/src/lib.rs) uses the configured API key or existing login session and returns an error when unauthenticated; it does not initiate browser login.
