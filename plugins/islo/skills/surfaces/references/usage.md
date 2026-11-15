# Surface usage

Surface commands publish knowledge items and interfaces from the current line-run stage sandbox into the run canvas.

## Commands

```bash
islo surface knowledge SLUG --label "LABEL"
islo surface web PORT --label "LABEL"
islo surface terminal NAME --label "LABEL" -- COMMAND ...
islo surface ls
```

In addition to `web` and `terminal`, the current CLI supports `knowledge`. Inspect `islo surface --help` and the kind-specific help before use. Adapt to additional installed kinds using their help.

## What to publish

Choose useful user-facing interfaces from the repository and running stack. A run can have multiple useful interfaces or none. A listening port alone does not show that a service is user-facing. Do not select services through blind port scanning.

## Knowledge

Use a knowledge Surface for a stored Markdown report, image, video, audio, or HTML document. Create the item before opening it with `islo surface knowledge SLUG`. The canvas follows updates to that slug. Read [Knowledge surfaces](knowledge.md) for creation commands, media embeds, and HTML constraints.

## Web

Publish a web interface only when its service is healthy and reachable through the sandbox at the intended port, and a real user-facing page or endpoint responds. Check actual content or an application-specific readiness probe. A bound port or successful TCP connection is insufficient.

Before publishing a web Surface, ensure the server listens on `0.0.0.0`. Verify the service at `http://localhost:PORT` inside the sandbox before and after publishing. For example, run `curl --fail --show-error http://localhost:8080/` and check the page content or an application-specific readiness response.

The server decides the default visibility for Web Surfaces according to your organization's rollout settings. Without a visibility flag, the CLI leaves that decision to the server. Only signed-in members of the organization can open a private share. A private Surface URL requires a browser session, so an unauthenticated `curl` returns `401`. A `401` from that URL does not mean the local service failed. Use localhost for service verification.

To request a private Surface explicitly, use `islo surface web PORT --private`. To allow anyone with the link to open the interface, use `islo surface web PORT --public` only when public access is intended. The flags cannot be combined. Check the installed CLI's help for supported flags. Upgrade the CLI if `--public` or `--private` is unavailable.

The web server must remain running while the Surface is in use. Check the exposed UI and responses for secrets, private data, privileged admin actions, or unintended access before publishing. Never expose databases, debug ports, internal metrics, or other internal services.

## Terminal

Publish a terminal only for a useful persistent user-facing TUI, REPL, live log view, or similar command. Verify that the command starts, remains active, and shows useful output or interaction.

The Surface command starts the persistent session. Do not publish an ordinary shell merely because terminal surfaces are available. Avoid commands that print secrets or grant unintended privileged access.

If publication fails, diagnose the web service or terminal session and retry only when safe.
