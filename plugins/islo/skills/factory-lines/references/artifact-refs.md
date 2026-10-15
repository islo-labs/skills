# Artifact refs

Jobs emit artifact refs — durable external resources a job step created or materially changed (pull requests, issues, comments, Slack messages, knowledge items). They appear on `JobRunResponse.artifact_refs` after the run completes. Lines aggregate artifact refs from their stage job runs; they do not independently create them.

## Discovery

The authoritative schema lives in the JobRun output contract:

```bash
islo schema job-run --short
```

This returns the full `JobRunResponse` closure including `artifact_refs` and all provider `external_ref` shapes. The schema is derived from the control-plane OpenAPI spec at build time. Do not reconstruct the shape from this skill; use the CLI output as the source of truth.

## Quick reference

The table and examples below are illustrative; `islo schema job-run --short` is authoritative.

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
| `exec` or `run_agent` exec mode (`$ISLO_OUTPUT`) | **No schema injected.** The side-channel file accepts free-form key=value lines. | Write `artifacts=<JSON array>` to `$ISLO_OUTPUT`. Each element is validated against `ArtifactRef` at finalization. |

If a job declares its own output named `artifacts`, the framework does not inject the built-in property — the declared output takes precedence.

## Validation contract

Every emitted artifact is validated against `ArtifactRef` at job run finalization. Valid artifacts persist to `JobRunResponse.artifact_refs`. Invalid artifacts are rejected and recorded as validation errors in `result_payload._artifact_validation_errors` — they do not silently disappear. Inspect with `islo job status <name> <run-id> -o json`.

## Lines aggregate, not create

Line runs do not have their own artifact creation path. Stage artifacts flow from `JobRun.artifact_refs` into the line run's stage projections and summary. The line displays bounded `ArtifactSummary` objects derived from the validated job run artifacts.

## When to use artifact refs

Always emit artifact refs for durable external resources the step creates or changes. Do not emit them for local files, logs, intermediate state, or resources the step only read.
