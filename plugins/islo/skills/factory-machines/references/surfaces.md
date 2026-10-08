# Live run surfaces

After the Machine stack starts and passes its health checks, inspect `islo surface --help` and the help for each supported target kind in the installed CLI. Choose useful user-facing interfaces discovered from the repositories and running stack. The current CLI supports `web` and `terminal`; apply the relevant checks below and adapt to any additional installed kinds using their help. A Machine can have multiple useful interfaces or none. A listening port alone does not show that a service is user-facing. Do not select services through blind port scanning.

## Web

Publish a web interface only when its selected service is healthy and reachable through the sandbox at the intended port, and a real user-facing page or endpoint responds. Check actual content or an application-specific readiness probe; a bound port or successful TCP connection is insufficient. Confirm the backing process remains running, then use `islo surface web PORT --label "LABEL"` as supported by installed help. This creates a **public web share**. Check the exposed UI and responses for secrets, private data, privileged admin actions, or unintended access before publishing. Never expose databases, debug ports, internal metrics, or other internal services.

## Terminal

Publish a terminal only for a useful persistent user-facing TUI, REPL, live log view, or similar command. Verify that the command starts, remains active, and shows useful output or interaction. Use `islo surface terminal NAME --label "LABEL" -- COMMAND ...` as supported by installed help; the Surface command creates the persistent session. Do not publish an ordinary shell merely because terminal surfaces are available. Avoid commands that print secrets or grant unintended privileged access.

Publish while the backing processes are alive, then keep them available during remaining review and verification. If a surface fails, diagnose its service or session and retry when safe; record unresolved failures in Machine findings. Record the verified start, readiness, and publication steps in the generated `islo-machine` skill for later stage agents.
