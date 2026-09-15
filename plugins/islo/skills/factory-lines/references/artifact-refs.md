# Artifact refs

Artifact refs record the durable external resources a job step created or materially changed — pull requests, issues, comments, Slack messages, knowledge items. They appear on `JobRunResponse.artifact_refs` after a run completes.

## Discovery

`islo schema factory` and `islo schema job` expose the line and job **manifest** schemas (what you author in `line.toml` / `job.toml`). The `ArtifactRef` type is a **run result** type, not a manifest type, so it does not appear there. To obtain the live schema with all provider `external_ref` shapes:

```bash
islo schema artifact-ref --short
```

The schema is derived from the control-plane OpenAPI spec at build time. Do not reconstruct the shape from this skill; use the CLI output as the source of truth.

## Quick reference

The table and examples below are illustrative; `islo schema artifact-ref --short` is authoritative.

### Providers

| Provider | Kind(s) |
|----------|---------|
| `github` | `pull_request`, `issue`, `comment` |
| `linear` | `issue`, `comment` |
| `slack` | `message` |
| `islo` | `knowledge_item` |
| `jira` | `issue`, `epic`, `comment` |
| `url` | `url` |

### Session agent example

```json
{
  "summary": "Opened fix PR",
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
      "url": "https://github.com/acme/backend/pull/42"
    }
  ]
}
```

### $ISLO_OUTPUT example

```bash
artifacts=[{"type":"issue","provider":"linear","operation":"updated","external_ref":{"provider":"linear","kind":"issue","identifier":"ENG-99"}}]
```

## How artifacts reach a run

There are two paths, and the schema contract differs:

| Path | Schema | How the agent writes artifacts |
|------|--------|--------------------------------|
| `run_agent` session mode | Control plane **injects** an `artifacts` array property into the structured-output JSON schema sent to the agent. The agent fills it as part of its claimed output. | The injected schema is a strict subset of `ArtifactRef` (no `metadata` dict, no nullable wrappers — only the fields an agent can fill). The agent returns `artifacts` alongside its declared outputs. |
| `exec` or `run_agent` exec mode (`$ISLO_OUTPUT`) | **No schema injected.** The side-channel file accepts free-form key=value lines. | Write `artifacts=<JSON array>` to `$ISLO_OUTPUT`. Each element is validated server-side against the full `ArtifactRef` model when stored, but there is no pre-flight schema constraint. |

If a job declares its own output named `artifacts`, the framework does not inject the built-in property — the declared output takes precedence.

## When to use artifact refs

Artifact refs are the structured way for the control plane to track what a job produced. Lines use them to display results, link stage outputs to external resources, and provide traceability across multi-stage runs. Always emit artifact refs for durable external resources the step creates or changes. Do not emit them for local files, logs, intermediate state, or resources the step only read.
