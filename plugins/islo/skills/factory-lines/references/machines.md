# Factory Machines

A Factory Machine is a Factory resource with its own version build. Islo runs each build through a product-managed Line. You do not create its `line.toml` or `job.toml`, and you do not use the line creation workflow. Use `islo factory machine`.

## Commands

Check the installed CLI before choosing flags:

```bash
islo factory machine --help
islo factory machine create --help
islo factory machine update --help
islo factory machine build --help
islo factory machine delete --help
```

Check the resolved Factory with `islo factory current`. If it is not the intended Factory, pass `--factory KEY|UUID` to each Machine command or select the intended Factory with `islo factory set KEY --project`. Then use the Machine name:

```bash
islo factory machine list
islo factory machine create <name> --repo <git-url> --capability docker
islo factory machine get <name>
islo factory machine update <name> --vcpus 4 --memory-mb 4096
islo factory machine build <name>
islo factory machine delete <name>
```

`create` starts the first build. `build` forces a new Machine version from the current spec. Use `get` to inspect the spec and latest build after either operation. If the API returns 404 for Machine commands, `factory-machine-v1` may be disabled for the tenant; there is no skill-side feature flag.

`delete` removes the Machine and frees its name. Saved snapshots stay. A running build returns 409 and deletes nothing. The command asks for confirmation in a terminal; `--force` skips it.

A Machine refresh schedule belongs to its Machine spec, not a line `[trigger]`. Set it with `--schedule` on `create` or `update`, and disable it with `--schedule-off` on `update`. A refresh checks repository revisions and starts a new build only when they change. Editing the schedule does not start a build.

## Build lifecycle

Machine creation runs **Prepare**, then **Author**, then **Finalize**:

1. **Prepare** runs `islo machine prepare --spec <file|->` as the sandbox user. The command validates the schema-1 spec, prepares every registered repository, and generates `/tmp/islo-machine-context.json`. A separate privileged step installs that document at `/etc/islo/machine.json` with mode `0644`, so repository files remain user-owned.
2. **Author** explores every repository before it changes files. If setup intent is missing, Author returns a typed batch of 1 to 10 questions without editing or committing. The manager asks the user and parks the run. The manager then resumes the same Author session with the answers. Author can repeat this question loop.
3. **Finalize** runs `islo machine verify`, saves the snapshot, and deletes the build sandbox. Verification reads only the installed context and repository files. It validates `machine.md`, component definitions, image and capacity requirements, required environment names, and the repeated component lifecycle. If validation fails, Finalize publishes the bounded structured report, does not save a snapshot, and keeps the sandbox for diagnosis.

Author writes exactly one `.islo/<machine-name>/machine.md` in the repository that owns the top-level orchestration. It writes component definitions and lifecycle entrypoints in the repositories that own them. Author commits every changed repository and leaves each checkout clean.

Machine repository entries use stable `MachineRepo.key` values for component and cross-repository references. This key contract applies to Machine repositories. Do not assume that generic Git sources have stable keys.

A scheduled refresh runs **Prepare**, then **Finalize**. It skips **Author**.

Author commits only to the checked-out repositories. It does not push or open a pull request. Until Machines have an explicit upstream delivery path, a scheduled refresh cannot preserve or reuse definitions from those local commits.

## Local workspace commands

Use the same deterministic verification as Finalize when authoring or diagnosing a Machine:

```bash
islo machine verify
islo machine verify --output json
```

Keep `islo components ...` for lower-level graph and lifecycle troubleshooting. `islo machine verify` is the complete acceptance check and exits non-zero when its schema-1 report has `passed: false`.

The prepare spec contains `schema`, `mode`, `machine_id`, `machine_name`, `repositories`, and `capacity`. Repository entries contain `key`, `repo_url`, `checkout_path`, and optional `creation_branch`. Capacity contains `capabilities`, `vcpus`, `memory_mb`, `disk_gb`, and `image`. URLs cannot contain credentials, checkout paths must be unique children of `/workspace`, and keys and paths must be unique.

The installed schema-1 context excludes repository URLs and credentials. It records mode, Machine identity, repository key/path registrations with optional creation branches, and typed capacity. Do not hand-edit it or depend on temporary spec files.

## Runner image requirement

Any new runner image visible to Jobs must put a compatible `islo` CLI on `PATH` at `/usr/local/bin/islo`. Machine Jobs must not self-update or use a hardcoded home-local binary.

## Updates and builds

| Change in `update` | Starts a new build? |
|---|---|
| Repositories (`--repo`, `--clear-repos`) | Yes |
| Capabilities (`--capability`, `--clear-capabilities`) | Yes |
| Disk size (`--disk-gb`) | Yes |
| vCPUs (`--vcpus`) or memory (`--memory-mb`) | No |
| Lifecycle, environment, or gateway profile | No |
| Refresh schedule or timezone | No |

Repeat `--repo` or `--capability` for multiple values. On update, supplying either replaces the entire corresponding list; include all values to keep, or use `--clear-repos` / `--clear-capabilities` to empty it. Lifecycle, environment, gateway, and schedule edits can be made with their `update` flags; check `islo factory machine update --help` for the current names and clear options. Use `build` when a new version is wanted without a spec change. Jobs keep using the last published version until that build succeeds.
