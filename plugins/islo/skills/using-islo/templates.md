# Automation templates

Use this reference when the user wants runnable examples instead of conceptual guidance.

The template repo is:

```text
https://github.com/islo-labs/islo-agents
```

Do not copy those templates into this skills repo. Link to the template repo and explain which path fits the use case.

## How to use templates

1. Run `islo job init <name>` locally so you have the current scaffold defaults before copying template structure.
2. Pick the closest template.
3. Read its `job.toml` to understand the sandbox, gateway profile, params, and steps.
4. Read its `action.yml` if the user wants GitHub Actions integration.
5. Read its prompt file before changing behavior.
6. Validate with `islo job deploy <name> --dry-run`, then deploy.
7. Add any required CI secret, usually `ISLO_API_KEY`.

## Template-backed webhook jobs

Use this shape when an external event should launch a reusable agent template:

```text
external provider event
-> Islo incoming webhook verification/filtering
-> job run with small stable params
-> template job.toml
-> template prompt/harness behavior
```

Setup flow:

1. Pick the closest `islo-agents` template or user fork.
2. Copy its `job.toml` into `jobs/<name>/job.toml`.
3. Run `islo job deploy <name> --dry-run`, then deploy.
4. Create the Islo incoming webhook.
5. Configure the external provider webhook to call Islo.
6. Keep event filtering in the webhook and behavior in the template.
7. Verify with a real delivery or job run.

## Advice for agents

- Use templates as starting points, not hidden magic.
- Keep repo-specific guidance in files such as `REVIEW.md` or `VERIFY.md` when the template supports them.
- Keep provider access through Islo gateway integrations.
- Keep template changes in `islo-agents`, not in this skills repo, unless the user explicitly asks to move template ownership.
- Keep workflow-specific triggers, prompt policy, output behavior, and job-specific lifecycle defaults in the template repo or a user fork.
