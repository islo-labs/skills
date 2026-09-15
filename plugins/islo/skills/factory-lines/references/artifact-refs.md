# Artifact refs

Artifact refs record the durable external resources a job step created or materially changed — pull requests, issues, comments, Slack messages, knowledge items. They appear on `JobRunResponse.artifact_refs` after a run completes.

## Discovery

`islo schema factory` and `islo schema job` expose the line and job **manifest** schemas (what you author in `line.toml` / `job.toml`). The `ArtifactRef` type is a **run result** type, not a manifest type, so it does not appear there.

To obtain the live schema:

```bash
islo job status <job-name> <run-id> -o json
```

The `.artifact_refs` array on the response carries the shape. For the canonical definition, the control-plane OpenAPI spec documents `ArtifactRef` under `components/schemas`.

## How artifacts reach a run

There are two paths, and the schema contract differs:

| Path | Schema | How the agent writes artifacts |
|------|--------|--------------------------------|
| `run_agent` session mode | Control plane **injects** an `artifacts` array property into the structured-output JSON schema sent to the agent. The agent fills it as part of its claimed output. | The injected schema is a strict subset of `ArtifactRef` (no `metadata` dict, no nullable wrappers — only the fields an agent can fill). The agent returns `artifacts` alongside its declared outputs. |
| `exec` or `run_agent` exec mode (`$ISLO_OUTPUT`) | **No schema injected.** The side-channel file accepts free-form key=value lines. | Write `artifacts=<JSON array>` to `$ISLO_OUTPUT`. Each element is validated server-side against the full `ArtifactRef` model when stored, but there is no pre-flight schema constraint. |

If a job declares its own output named `artifacts`, the framework does not inject the built-in property — the declared output takes precedence.

## ArtifactRef shape

Every artifact ref has a top-level envelope and a provider-discriminated `external_ref`:

```text
type          Resource type, normally matches external_ref.kind
provider      Must match external_ref.provider
operation     What the step did: created, updated, published, etc.
external_ref  Provider-specific stable identity (see provider table)
url           Canonical resource URL (optional)
title         Human-readable label (optional)
status        Current state (optional)
metadata      Provider-specific details, not identity (optional; exec/$ISLO_OUTPUT only — not in the session-injected schema)
```

### Provider external_ref shapes

| Provider | Kind | Required identity fields |
|----------|------|------------------------|
| `github` | `pull_request`, `issue`, `comment` | PRs/issues: `owner`, `repo`, `number`. Comments: `id`. |
| `linear` | `issue`, `comment` | Issues: `id` or `identifier`. Comments: `id`. Optional: `team`, `issue_id`. |
| `slack` | `message` | `channel`, `ts` |
| `islo` | `knowledge_item` | `slug` |
| `jira` | `issue`, `epic`, `comment` | Issues/epics: `key`. Comments: `id`. Optional: `project`, `site`. |
| `url` | `url` | `url` (HTTP/HTTPS). Optional: `display_hint` with `title`, `icon_url`, `provider_name`. |

### Session agent example (returned as part of structured output)

```json
{
  "summary": "Opened fix PR for the auth middleware",
  "artifacts": [
    {
      "type": "pull_request",
      "provider": "github",
      "operation": "created",
      "external_ref": {
        "provider": "github",
        "kind": "pull_request",
        "owner": "acme",
        "repo": "backend",
        "number": 42
      },
      "url": "https://github.com/acme/backend/pull/42",
      "title": "fix(auth): rotate session tokens on refresh"
    }
  ]
}
```

### $ISLO_OUTPUT example (exec or run_agent exec mode)

```bash
artifacts=[{"type":"pull_request","provider":"github","operation":"created","external_ref":{"provider":"github","kind":"pull_request","owner":"acme","repo":"backend","number":42},"url":"https://github.com/acme/backend/pull/42"}]
```

## When to use artifact refs

Artifact refs are the structured way for the control plane to track what a job produced. Lines use them to display results, link stage outputs to external resources, and provide traceability across multi-stage runs. Always emit artifact refs for durable external resources the step creates or changes. Do not emit them for local files, logs, intermediate state, or resources the step only read.
