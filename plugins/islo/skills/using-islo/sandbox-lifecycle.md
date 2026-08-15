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

## Project setup

Scaffold project defaults before day-to-day sandbox work:

```bash
islo init                    # create islo.yaml (interactive or --template)
islo add                     # detect project signals and add setup scripts
islo add <tool> [version]    # append a setup_scripts entry from a built-in recipe
```

## Common commands

```bash
islo use <name>
islo use <name> -- npm test
islo use <name> --environment production
islo environment list
islo environment get production
islo environment create --name production --variable PUBLIC_FLAG=enabled
islo ls
islo status
islo status <name>
islo pause <name>
islo resume <name>
islo stop <name>
islo rm <name>
islo cp <local> <name>:<remote>
islo doctor                  # check auth, config, and API connectivity
islo doctor --output json
```

For scripts and tools, prefer JSON output where the command supports it.

## Creation inputs

Sandbox creation can use CLI flags, `islo.yaml`, or account defaults. Check `islo schema use` for the current `islo.yaml` shape and flag precedence.

Use environment names in user-facing flows: `islo use --environment production` and the environment field in `islo.yaml` per `islo schema use`.

## Sources

Clone repos during sandbox bootstrap with `--source` or the sources field in `islo.yaml`. Check exact formats with `islo schema use`.

```bash
islo login --tool github   # required for private repos
islo use my-sandbox --source github://owner/repo
islo use my-sandbox --source github://owner/repo:main
islo use my-sandbox --source https://github.com/owner/repo:feat/branch
```

In `islo.yaml`, check `islo schema use` for the current sources configuration.

Islo runs source checkout during sandbox bootstrap before your command or shell. For private GitHub repos, connect the integration first (`islo login --tool github`). Do not tell users to manually embed tokens in clone URLs for normal `islo use` source checkout.

If clone fails with `Repository not found` on a private repo, check `islo status` for a connected GitHub integration before assuming the repo path is wrong.

## Default image

The platform default sandbox image is:

```text
ghcr.io/islo-labs/islo-runner:latest
```

It is pre-pulled on Islo infrastructure for fast startup and includes common dev tools plus preinstalled agents (Claude Code, Cursor agent, Codex).

- For `islo use` and `islo.yaml`, omitting `image` uses this default.
- For `job.toml` with sandbox provisioning or ensure modes, check `islo schema job` for image requirements.

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

## Snapshots

Save and restore sandbox state:

```bash
islo snapshot save <name>              # save snapshot of running sandbox
islo snapshot save <name> --name snap  # save with custom name
islo snapshot ls
islo snapshot rm <name>
islo use new-sandbox --snapshot <name> # restore from snapshot
```

Snapshots can also be referenced in job manifests and incoming webhook sandbox templates. Check `islo schema job` and `islo schema webhook`.

## Port forwarding and sharing

```bash
islo port-forward <name> <port>        # forward a sandbox port locally
islo share <name> [port]               # create shareable URL
islo share <name> [port] --ttl 1h      # share with expiration
islo shares <name>
islo unshare <name> <slug>
```

## SSH, logs, and API keys

```bash
islo ssh <name>                        # SSH into sandbox
islo logs <name>                       # view sandbox logs
islo api-key create                    # create an API key
islo api-key ls
islo region ls                         # list available regions
islo switch <tenant>                   # switch active tenant
```

## Good defaults

- Use named sandboxes for repeatable agent work.
- Use `islo.yaml` for project defaults.
- Use jobs for repeated or scheduled work.
- Use the `default` gateway profile for provider access unless the user needs a custom profile.
- Use `islo status` and `islo ls` before destructive commands.
