# Line manifests

Do not reconstruct `line.toml` from this skill. Confirm every key against the live schema:

```bash
islo schema factory --short
```

Unknown keys 422. Treat every TOML example in this repo as a pattern, not a drop-in.

## Policy the schema does not state

- A line declares identity, what starts a run, the stages, and the routing between them. Harness, model, params, and outputs live on each stage's job.
- Schedules live in `[trigger]` and nowhere else; a schedule created any other way is reverted on the next deploy.
- Deploy order is knowledge, then every stage job, then the line last. The line pins `job_version_id` at deploy time.
- Reserved agentic option names belong to line controls. Do not reuse them as option labels.
- Trigger field shapes and the condition AST are in the schema; wiring (selectors, filters, one-real-event verify) is in `triggers.md`.
