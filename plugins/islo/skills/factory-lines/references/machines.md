# Factory Machines

A Factory Machine is a Factory resource with its own bake. A request to create or change one does not need a `line.toml`, a `job.toml`, or the line creation workflow. Use `islo factory machine`; do not create a line or job for the Machine.

## Commands

Check the installed CLI before choosing flags:

```bash
islo factory machine --help
islo factory machine create --help
islo factory machine update --help
```

Check the resolved Factory with `islo factory current`. If it is not the intended Factory, pass `--factory KEY|UUID` to each Machine command or select the intended Factory with `islo factory set KEY --project`. Then use the Machine name:

```bash
islo factory machine list
islo factory machine create <name> --repo <git-url> --capability docker
islo factory machine get <name>
islo factory machine update <name> --vcpus 4 --memory-mb 4096
islo factory machine rebake <name>
```

`create` starts the first bake. `rebake` explicitly starts a new bake with the current spec. Use `get` to inspect the spec and latest bake after either operation. If the API returns 404 for Machine commands, `factory-machine-v1` may be disabled for the tenant; there is no skill-side feature flag.

A Machine refresh schedule belongs to its Machine spec, not a line `[trigger]`. Set it with `--schedule` on `create` or `update`, and disable it with `--schedule-off` on `update`. These schedule edits do not start a bake.

## Updates and rebakes

| Change in `update` | Starts a new bake? |
|---|---|
| Repositories (`--repo`, `--clear-repos`) | Yes |
| Capabilities (`--capability`, `--clear-capabilities`) | Yes |
| Disk size (`--disk-gb`) | Yes |
| vCPUs (`--vcpus`) or memory (`--memory-mb`) | No |
| Lifecycle, environment, or gateway profile | No |
| Refresh schedule or timezone | No |

Repeat `--repo` or `--capability` for multiple values. On update, supplying either replaces the entire corresponding list; include all values to keep, or use `--clear-repos` / `--clear-capabilities` to empty it. Lifecycle, environment, gateway, and schedule edits can be made with their `update` flags; check `islo factory machine update --help` for the current names and clear options. Use `rebake` when a new bake is wanted without a spec change.
