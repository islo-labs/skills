# Knowledge

Use this reference for tenant knowledge items — memories, skills, and rules that agent-powered job stages and Factory managers can reference.

## Levels

| Level | Purpose |
|-------|---------|
| `memory` | Persistent context the agent should remember |
| `skill` | Reusable capability or workflow instructions |
| `rule` | Policy or constraint the agent must follow |

## CLI

```bash
islo knowledge list
islo knowledge list --level rule --repo owner/repo
islo knowledge list --tag auth --query namespace
islo knowledge get <identifier>
islo knowledge create auth-rule --level rule --body @rule.md --tag auth --repo owner/repo
islo knowledge update <identifier> --body @rule.md --tag auth
islo knowledge delete <identifier> --force
islo knowledge render --repo owner/repo --tag policy
```

Use `--output json` for structured output. Identifiers are lowercase, hyphen-separated, and immutable after creation.

## Using knowledge in jobs

Session-mode `run_agent` steps on `claude` or `codex` can reference knowledge by slug:

```toml
[[run.tasks.steps]]
type = "run_agent"
mode = "session"
harness = "claude"
prompt = "Review this PR following our policies."
knowledge = ["auth-rules", "pr-policy"]
```

Or use `prompt_ref` to reference a knowledge item as the prompt body:

```toml
[[run.tasks.steps]]
type = "run_agent"
mode = "session"
harness = "claude"
prompt_ref = "pr-review-prompt"
knowledge = ["pr-policy"]
```

## Using knowledge in Factory

- Attach knowledge to stage job `run_agent` steps (see above).
- Manager instructions in `manager.toml` can reference policies inline; link knowledge items to keep instructions maintainable.
- The Factory UI renders knowledge-backed prompts in the line description view.

## Linking

Items can be linked to repositories (`--repo owner/repo`) and tags (`--tag auth`). Use `islo knowledge render` to concatenate matching bodies as Markdown for a given repo and tag filter.

## Things to avoid

- Do not embed long policy text directly in `job.toml` when a knowledge item keeps it reusable across jobs and lines.
- Knowledge is supported on `claude` and `codex` harnesses only — not `cursor` or `custom`.
