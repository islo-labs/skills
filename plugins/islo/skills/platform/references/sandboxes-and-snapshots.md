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

Claude Code, Cursor agent, Codex, and OpenCode are preinstalled in sandboxes. If the matching integration was connected before sandbox use, the agent runs without an in-sandbox login. Do not reinstall them, copy local key files, or set provider API keys in sandbox env to make an agent start.

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

## Sandbox modes (jobs and webhook templates)

| Mode | Use when |
|------|----------|
| `provision` + `teardown_on_complete = true` | Default. Fresh environment per run; hand off via a pushed branch or typed outputs |
| `ensure` + param-derived name | Only when multiple stages must share one workspace |
| `reuse` | Attach to an existing sandbox; rare |

Prefer provision per stage; `ensure` reconnects invite stale environments and delete/create races.

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

Snapshots are also referenced from job manifests (`snapshot_name`) and incoming webhook sandbox templates.

### The snapshot-src pattern

Harness code a job runs (servers, CLIs, test trees, scenario assets) lives in the line repo under `snapshot-src/`, gets rsynced onto a build sandbox at a fixed path like `/workspace/<line>/`, and is saved as a named snapshot the jobs reference. Never embed harness code in manifests as base64 or heredoc bootstrap. After harness edits: rebuild the snapshot, then redeploy jobs and line.

```text
<line>/
  snapshot-src/setup-snapshot.sh   # rsync harness onto a build sandbox
  snapshot-src/harness/            # source of truth
  jobs/<stage>/job.toml            # snapshot_name + short exec steps
  line.toml
```

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
