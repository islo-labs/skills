# Job manifests

Do not reconstruct `job.toml` from this skill. Scaffold with `islo job init`, then confirm every key against the live schema:

```bash
islo schema job --short
```

Unknown keys 422. Treat every TOML example in this repo as a pattern, not a drop-in.

## Policy the schema does not state

- Params and outputs are the line's contract. Write them first. Transitions bind params from trigger outputs, literals, and prior stages' outputs.
- Harness and model live on the `run_agent` step, never in `line.toml`.
- `[[run.sandbox.sources]]` is accepted and never checked out. Clone with an idempotent `exec` step instead (see the checkout pattern in the islo-agents examples).
- Reserved agentic option names (`cancel`, `stop`, and the rest listed by `islo schema factory --short`) belong to line controls. Do not reuse them as option labels.
- Write the stage brief in the job. If the user's repo already has skills, check it out and point a short literal at the skill file. Supporting or fan-out briefs may live in the snapshot. Never copy procedural content into Knowledge.
