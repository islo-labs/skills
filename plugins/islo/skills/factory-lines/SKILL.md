---
name: factory-lines
description: Create, deploy, run, and debug Islo Factory lines and jobs. Use when the user wants to automate a workflow on Islo, mentions factory lines, line.toml, job.toml, line runs, schedules, triggers, or asks to build or fix an Islo automation.
---

# Islo Factory lines

Factory lines are Islo's automation product: multi-stage work with typed routing, loops, schedules, and event triggers. A line (`line.toml`) orchestrates stages; each stage runs a job (`job.toml`); jobs execute in sandboxes with agents doing the judgment work.

## Iron rules

1. Never write or edit a manifest from memory. Scaffold with `islo job init`, read `islo schema factory --short` and `islo schema job --short`, validate with `--dry-run`. Treat every example and template in this skill as a pattern, not a drop-in.
2. Creating a line follows `references/create-a-line.md` phase by phase. Phase 2 is an approval gate: present the design summary and wait for explicit approval before creating or deploying anything.
3. Deploy order matters and is defined once, in create-a-line.md Phase 6: knowledge, then every stage job, then the line last.
4. Schedules live in the line manifest `[trigger]` and nowhere else; anything else is reverted on the next deploy.
5. Harness code ships in sandbox snapshots; repo skills and prompts reach agents via a fetch-or-clone checkout step plus a short literal prompt, never copied into manifests or Knowledge.
6. Agents do the judgment work via `run_agent`. Do not replace them with hand-written shell business logic or shell-wrapped agent CLIs, and do not put provider tokens in manifests or sandbox env.

## Where to go

| Task | Read |
|------|------|
| Build a new line from a request | `references/create-a-line.md` |
| Write or fix `line.toml` (stages, transitions, trigger shapes) | `references/line-manifest.md` |
| Write or fix `job.toml` (params, outputs, sandbox, steps) | `references/job-manifest.md` |
| Choose or wire a trigger; schedule rules; webhook vs incoming webhook | `references/triggers.md` |
| Inspect, steer, or debug a run; a stage failed; no run appeared | `references/run-control-and-debugging.md` |
| Pick harness or model; use knowledge in stages | `references/harness-models-knowledge.md` |
| Single-stage job without orchestration (rare, explicit ask only) | `references/standalone-jobs.md` |

Starting points: `templates/` holds complete line templates synced from islo-labs/islo-agents (see `templates/README.md`). Copy the nearest one and adapt.

For sandbox lifecycle, snapshots, gateway profiles, incoming webhooks, environments, knowledge CRUD, and the SDK, use the islo platform skill.

## Maintenance

`scripts/validate_commands.sh` and `scripts/validate_examples.sh` check every documented command and manifest example against the installed CLI; CI runs them. `scripts/sync_templates.sh` refreshes `templates/` from the pinned islo-agents ref; never hand-edit templates.
