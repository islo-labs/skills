# Sandbox lifecycle

Use this reference for creating, connecting to, executing in, pausing, resuming, stopping, deleting, and inspecting Islo sandboxes.

## Default command

Prefer `islo use` for day-to-day work. It is the main create-or-connect entry point.

```bash
islo use <sandbox-name>
islo use <sandbox-name> -- <command>
islo use --agent cursor --task "Implement the issue"
```

`islo use` handles the common path:

1. Resolve auth, region, and `islo.yaml`.
2. Find an existing sandbox or create one.
3. Resume if the sandbox is paused and the user confirms.
4. Run setup and agent bootstrap when needed.
5. Open an interactive session, run a one-shot command, or start a background agent task.

Do not invent separate `islo create` or `islo exec` commands unless the current CLI exposes them. In current Islo CLI patterns, `islo use <name> -- <command>` is the exec path.

## Common commands

```bash
islo use <name>
islo use <name> -- npm test
islo ls
islo status
islo status <name>
islo pause <name>
islo resume <name>
islo stop <name>
islo rm <name>
islo cp <local> <name>:<remote>
```

For scripts and tools, prefer JSON output where the command supports it.

## Creation inputs

Sandbox creation can use:

- CLI flags
- `islo.yaml`
- defaults from the current account and region

Common `islo.yaml` fields include:

- `sandbox`: default sandbox name
- `image`: container or VM image
- `gateway_profile`: gateway rules for egress and credential injection
- `sources`: repositories to clone into the sandbox
- `setup_scripts`: commands to run after source checkout
- `init`: minimal, full, or custom platform setup
- `lifecycle`: idle pause, TTL, and auto-resume policy

CLI flags should win over `islo.yaml`. `islo.yaml` should win over defaults.

## Bootstrap

Server-side bootstrap handles platform init, sources, and setup scripts. Client-side post-create work may install agent tools or sync local git identity.

Use setup scripts for deterministic project setup. Avoid doing project setup by hand in an interactive shell if the result should be repeatable by other agents or schedules.

## Sessions and tasks

Use sessions when work should remain attachable:

```bash
islo use <name> --list-sessions
islo use <name> --new-session
islo use <name> --session <session-name>
```

Use `--task` for background agent work. Use a stable sandbox name when a task should resume state across runs.

## Pause, stop, and delete

- `pause` keeps the sandbox state and is the normal cost-saving path.
- `resume` brings a paused sandbox back.
- `stop` halts the sandbox while preserving enough state to inspect or restart if supported.
- `rm` or `delete` removes the sandbox.

When writing automation, prefer lifecycle policy over manual cleanup scripts where possible.

## Cache and snapshots

If the user asks about warm starts, caches, or snapshots, verify current docs and CLI support before giving exact commands. The platform can reuse cached images and snapshots, but the user-facing command shape may vary.

## Good defaults

- Use named sandboxes for repeatable agent work.
- Use `islo.yaml` for project defaults.
- Use jobs for repeated or scheduled work.
- Use gateway profiles for provider access.
- Use `islo status` and `islo ls` before destructive commands.
