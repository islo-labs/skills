---
name: factory-lines
description: Create, deploy, run, and debug Islo Factory lines and jobs. Use when the user wants to automate a workflow on Islo, mentions factory lines, line.toml, job.toml, line runs, schedules, triggers, or asks to build or fix an Islo automation.
---

# Islo Factory lines

Factory lines are Islo's automation product: multi-stage work with typed routing, loops, schedules, and event triggers. A line (`line.toml`) orchestrates stages; each stage runs a job (`job.toml`); jobs execute in sandboxes with agents doing the judgment work.

## Iron rules

1. Never write or edit a manifest from memory. Scaffold with `islo job init`, read `islo schema factory --short` and `islo schema job --short`, validate with `--dry-run`. Treat every example as a pattern, not a drop-in. Nearby lines supply stage shape only — never copy repo, Linear team/project, Slack channel, snapshot, or gateway without the user naming them in this request.
2. Creating a line follows `references/create-a-line.md` phase by phase. Phase 1 is an intake gate: ask identity (repos, Linear team/project, Slack channel) and stop. Phase 2 is an approval gate: present the design summary and wait for explicit approval before creating or deploying anything.
3. Deploy order matters and is defined once, in create-a-line.md Phase 6: knowledge, then every stage job, then the line last.
4. Schedules live in the line manifest `[trigger]` and nowhere else; anything else is reverted on the next deploy.
5. Harness code ships in sandbox snapshots. Put the stage brief in the job `run_agent` prompt so a prompt change is a new job version. Leave supporting or fan-out briefs in the snapshot when they would clutter the line/job view. Repo skills may be a fetch-or-clone checkout plus a short pointer. Never copy procedural content into Knowledge.
6. Agents do the judgment work via `run_agent`. Do not replace them with hand-written shell business logic or shell-wrapped agent CLIs, and do not put provider tokens in manifests or sandbox env.

## Where to go

| Task | Read |
|------|------|
| Build a new line from a request | `references/create-a-line.md` |
| Write or fix `line.toml` | `islo schema factory --short`, then `references/line-manifest.md` for policy |
| Write or fix `job.toml` | `islo schema job --short`, then `references/job-manifest.md` for policy |
| Choose or wire a trigger; schedule rules; webhook vs incoming webhook | `references/triggers.md` |
| Inspect, steer, or debug a run; a stage failed; no run appeared | `references/run-control-and-debugging.md` |
| Pick harness or model; use knowledge in stages | `references/harness-models-knowledge.md` |
| Single-stage job without orchestration (rare, explicit ask only) | `references/standalone-jobs.md` |

Starting points: copy the nearest example from [islo-labs/islo-agents](https://github.com/islo-labs/islo-agents). There is no in-skill copy; clone or browse that repo if it is not already on disk.

For sandbox lifecycle, snapshots, gateway profiles, incoming webhooks, environments, knowledge CRUD, and the SDK, use the islo platform skill.

## Maintenance

`scripts/validate_commands.sh` and `scripts/validate_examples.sh` check every documented command and manifest example against the installed CLI; CI runs them.
