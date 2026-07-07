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

## PR review template

For automated PR review, use or fork `https://github.com/islo-labs/islo-agents`. Keep reusable review behavior there, not in the skill repo.

Read these files before changing review automation:

- `review/job.toml`: durable job params, sandbox mode, lifecycle, and steps.
- `review/action.yml`: GitHub wrapper behavior when the user chooses that integration path.
- `review/prompt.md`: review behavior and GitHub PR review instructions.
- `src/agent.ts`: prompt loading, variable substitution, session reuse, and Claude Agent SDK execution.
- `review/validate-job.mjs`: deployed job compatibility checks.

For webhook-driven PR review, use `automations.md` for webhook and job boundaries, then point the webhook at a job that runs the `islo-agents` review harness or a user fork. Do not embed the full review prompt in the webhook or `job.toml`.

The primary review output belongs on GitHub as a PR review with inline comments and a summary. Files written inside the sandbox are optional debug artifacts.

## Advice for agents

- Use templates as starting points, not hidden magic.
- Keep repo-specific guidance in files such as `REVIEW.md` or `VERIFY.md` when the template supports them.
- Keep provider access through Islo gateway integrations.
- Keep template changes in `islo-agents`, not in this skills repo, unless the user explicitly asks to move template ownership.
