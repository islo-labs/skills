# Sandboxes and snapshots

Creating, connecting to, executing in, pausing, resuming, and deleting Islo sandboxes, and saving state as snapshots.

## Default command

`islo use` is the create-or-connect entry point. It resolves auth, region, and `islo.yaml`, finds or creates the sandbox, resumes it if paused, runs bootstrap, then opens a shell, runs a command, or starts an agent task.

```bash
islo use <sandbox-name>
islo use <sandbox-name> -- npm test
islo use --agent claude
islo use --agent cursor --task "Add tests for the auth flow"
islo use --agent codex --task "Fix the failing tests"
islo use --agent opencode
```

There are no separate `islo create` or `islo exec` commands; `islo use <name> -- <command>` is the exec path.

## Built-in agents

Claude Code, Cursor agent, and Codex are preinstalled in sandboxes. OpenCode is installed on first `islo use --agent opencode` (official installer into `~/.opencode/bin`). If the matching integration was connected before sandbox use, Claude/Cursor/Codex run without an in-sandbox login. OpenCode uses Islo inference via the injected config; do not copy local key files or set provider API keys in sandbox env to make an agent start.

## Project setup

```bash
islo init                    # create islo.yaml
islo add                     # detect project signals and add setup scripts
islo add <tool> [version]    # append a setup_scripts entry from a built-in recipe
```

Check `islo schema use` for the current `islo.yaml` shape and flag precedence. Use setup scripts for deterministic setup rather than hand configuration in an interactive shell.

## Common commands

```bash
islo ls
islo status
islo status <name>
islo pause <name>
islo resume <name>
islo stop <name>
islo rm <name>
islo cp <local> <name>:<remote>
islo doctor
```

`pause` is the normal cost-saving path and keeps state; `stop` halts; `rm` deletes. Prefer JSON output (`--output json`) in scripts. Check `islo status` and `islo ls` before destructive commands.

## Environments

Reusable sandbox variables and environment-owned gateway-injected secrets live in named environments:

```bash
islo environment list
islo environment get production
islo environment create --name production --variable PUBLIC_FLAG=enabled
islo use <name> --environment production
```

## Sources

Clone repos during sandbox bootstrap with `--source` or the sources field in `islo.yaml` (shapes per `islo schema use`):

```bash
islo login --tool github   # required for private repos
islo use my-sandbox --source github://owner/repo
islo use my-sandbox --source github://owner/repo:main
```

Checkout happens during bootstrap, before your command or shell. Do not embed tokens in clone URLs. `Repository not found` on a private repo usually means GitHub is not connected; check `islo status` before assuming the path is wrong.

## Default image

`ghcr.io/islo-labs/islo-runner:latest`, pre-pulled on Islo infrastructure, with common dev tools and the preinstalled agents. Omitting `image` in `islo use` and `islo.yaml` uses it. Use it or a fully qualified reference, never an unqualified image name.

## Machine-backed Line workspaces

Factory Agents use Machine-backed sandboxes. A Line stage selects a reusable Agent; `sandbox_name` groups stages that share a filesystem within one run. Every Agent in that group must resolve to the same Machine. See the factory-lines skill for Agent and Line configuration.

## Sessions and tasks

```bash
islo use <name> --list-sessions
islo use <name> --new-session
islo use <name> --session <session-name>
```

Use `--task` for background agent work and a stable sandbox name when a task should resume state across runs.

## Snapshots

```bash
islo snapshot save <name>              # snapshot a running sandbox
islo snapshot save <name> --name snap  # custom snapshot name
islo snapshot ls
islo snapshot rm <name>
islo use new-sandbox --snapshot <name> # restore
```

Incoming webhook sandbox templates can also reference snapshots. Factory Agents select Machines for their environment; use Machine repositories and build configuration for reusable Line execution environments.

## Port forwarding, sharing, SSH, logs

```bash
islo port-forward <name> <port>
islo share <name> [port] --ttl 1h
islo shares <name>
islo unshare <name> <slug>
islo ssh <name>
islo logs <name>
```

## Tenancy and keys

```bash
islo api-key create
islo api-key ls
islo region ls
islo switch <tenant>
```
