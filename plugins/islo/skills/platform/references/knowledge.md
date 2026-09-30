# Knowledge

Tenant knowledge items: memories, skills, and rules that agent steps can reference. Knowledge is for declarative content; procedural content is rejected at deploy and belongs in the repo (the factory-lines skill covers handing repo skills to agents).

## Discovery

```bash
islo schema knowledge
islo knowledge --help
```

## CRUD

```bash
islo knowledge list
islo knowledge list --type rule --repo owner/repo
islo knowledge list --tag auth --query namespace
islo knowledge get <identifier>
islo knowledge create auth-rule --type rule --body @rule.md --tag auth --repo owner/repo
islo knowledge update <identifier> --body @rule.md --tag auth --repo owner/repo
islo knowledge delete <identifier> --force
islo knowledge render --repo owner/repo --tag policy
```

Use `--output json` for structured output.

## Types and linking

Items have a type (memory, skill, rule, prompt, image, video, or audio) and can be linked to repositories and tags. `islo knowledge render` concatenates matching bodies as Markdown for a repo and tag filter. Check `islo schema knowledge` for type and linking options.

## Using knowledge from agents

Attach items to agent steps via prompt bindings or the `run_agent.knowledge` array instead of embedding long policy text in manifests; binding shapes per `islo schema job`. Line routing instructions can also bind knowledge. The Factory UI renders knowledge-backed prompts in the line description view.
