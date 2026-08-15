# Knowledge

Use this reference for tenant knowledge items — memories, skills, and rules that agent-powered job stages can reference.

## Discovery

```bash
islo schema knowledge
islo knowledge --help
```

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

Use `--output json` for structured output.

## Using knowledge in jobs and Factory

- Attach knowledge to agent-powered job stages instead of embedding long policy text in manifests.
- Manager instructions can reference policies inline; knowledge items keep instructions reusable across jobs and lines.
- The Factory UI renders knowledge-backed prompts in the line description view.

Check `islo schema job` for how knowledge links into agent steps.

## Linking

Items can be linked to repositories and tags. Use `islo knowledge render` to concatenate matching bodies as Markdown for a given repo and tag filter. Check `islo schema knowledge` for level and linking options.

## Things to avoid

- Do not embed long policy text directly in manifests when a knowledge item keeps it reusable.
- Do not assume knowledge field shapes from memory — check `islo schema job`.
