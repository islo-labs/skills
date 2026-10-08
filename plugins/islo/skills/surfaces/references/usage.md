# Surface usage

Surface commands publish interfaces from the current line-run stage sandbox into the run canvas.

## Commands

```bash
islo surface web PORT --label "LABEL"
islo surface terminal NAME --label "LABEL" -- COMMAND ...
islo surface ls
```

The current CLI supports `web` and `terminal`. Inspect `islo surface --help` and the kind-specific help before use. Adapt to additional installed kinds using their help.

## What to publish

Choose useful user-facing interfaces from the repository and running stack. A run can have multiple useful interfaces or none. A listening port alone does not show that a service is user-facing. Do not select services through blind port scanning.

## Web

Publish a web interface only when its service is healthy and reachable through the sandbox at the intended port, and a real user-facing page or endpoint responds. Check actual content or an application-specific readiness probe. A bound port or successful TCP connection is insufficient.

The web server must remain running while the Surface is in use. This command creates a **public web share**. Check the exposed UI and responses for secrets, private data, privileged admin actions, or unintended access before publishing. Never expose databases, debug ports, internal metrics, or other internal services.

## Terminal

Publish a terminal only for a useful persistent user-facing TUI, REPL, live log view, or similar command. Verify that the command starts, remains active, and shows useful output or interaction.

The Surface command starts the persistent session. Do not publish an ordinary shell merely because terminal surfaces are available. Avoid commands that print secrets or grant unintended privileged access.

If publication fails, diagnose the web service or terminal session and retry only when safe.
