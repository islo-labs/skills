# Sandbox lifecycle

Use this reference for creating, connecting to, executing in, pausing, resuming, stopping, deleting, and inspecting Islo sandboxes.

## Default command

Prefer `islo use` for day-to-day work. It is the main create-or-connect entry point.

```bash
islo use <sandbox-name>
islo use <sandbox-name> -- <command>
islo use --agent claude
islo use --agent cursor --task "Implement the issue"
islo use --agent codex --task "Fix the failing tests"
```

`islo use` handles the common path:

1. Resolve auth, region, and `islo.yaml`.
2. Find an existing sandbox or create one.
3. Resume if the sandbox is paused and the user confirms.
4. Run setup and agent bootstrap when needed.
5. Open an interactive session, run a one-shot command, or start a background agent task.

Do not invent separate `islo create` or `islo exec` commands unless the current CLI exposes them. In current Islo CLI patterns, `islo use <name> -- <command>` is the exec path.

## Built-in agents

Claude Code, Cursor agent, and Codex are already installed inside Islo sandboxes. Do not add setup steps that reinstall them unless the user asks for a custom version.

Use `islo use --agent <name>` to start an interactive agent session:

```bash
islo use <name> --agent claude
islo use <name> --agent cursor
islo use <name> --agent codex
```

Use `--task` to start a background prompt:

```bash
islo use <name> --agent claude --task "Review this PR"
islo use <name> --agent cursor --task "Add tests for the auth flow"
islo use <name> --agent codex --task "Fix the lint errors"
```

If the matching integration was connected before sandbox use, the agent should work without running a login flow inside the sandbox. Prefer this path over copying local key files or setting provider API keys in sandbox env.

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
- `image`: container or VM image (optional; defaults to `ghcr.io/islo-labs/islo-runner:latest`)
- `gateway_profile`: gateway rules for egress and credential injection
- `sources`: repositories to clone into the sandbox
- `setup_scripts`: commands to run after source checkout
- `init`: minimal, full, or custom platform setup
- `lifecycle`: idle pause, TTL, and auto-resume policy

CLI flags should win over `islo.yaml`. `islo.yaml` should win over defaults.

## Default image

The platform default sandbox image is:

```text
ghcr.io/islo-labs/islo-runner:latest
```

It is pre-pulled on Islo infrastructure for fast startup and includes common dev tools plus preinstalled agents (Claude Code, Cursor agent, Codex).

- For `islo use` and `islo.yaml`, omitting `image` uses this default.
- For `job.toml` with `mode = "provision"` or `"ensure"`, `image` is **required** — set the fully qualified reference above.
- Do not use `islo/default` in job manifests. The `islo job init` scaffold may emit it, but compute resolves it as `docker.io/islo/default` and provisioning fails.

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
