---
name: windows-desktop
description: Run, drive, screenshot, and record Windows desktop apps (GUI) in an Islo Windows sandbox with islo-desktop and agent-desktop. Use when a task involves a Windows app's user interface, filling a form or dropdown in a Windows app, Windows screenshots or screen recordings, or a sandbox from global/windows-2025-desktop-v2.
---

# Windows desktop apps in Islo sandboxes

Commands sent to a Windows sandbox (`islo use <sandbox> -- ...`, SSH, SDK exec) run as `islo` on a hidden service desktop, and the VM has no display. Programs with windows started that way are never drawn: screenshots come back blank and input goes nowhere. To use a GUI app, open a real desktop session with `islo-desktop` and do everything inside it.

`islo-desktop` and `agent-desktop` ship in the `global/windows-2025-desktop-v2` snapshot. Check with `islo use <sandbox> -- cmd /c islo-desktop help`; older Windows snapshots do not have them.

```bash
islo use my-win --snapshot global/windows-2025-desktop-v2 -- cmd /c ver
```

## Workflow

Run each step with `islo use <sandbox> -- cmd /c <command>` (or `powershell -NoProfile -Command "<command>"`). Calling `islo-desktop` without `cmd /c` fails. In a bash shell, single-quote Windows paths (`'C:\workspace\shot.png'`) so the backslashes survive.

1. `islo-desktop start` opens the session (1920x1080 by default; `-Width 1280 -Height 800`). The first start takes 20 to 40 s.
2. `islo-desktop run "C:\Program Files\App\app.exe" [args]` starts the app in the session. It returns once the app has started; the window may appear seconds later.
3. Observe: `islo-desktop windows` lists visible windows with position, size, and title. `islo-desktop screenshot` saves a PNG under `C:\workspace`. Look at screenshots to understand the UI.
4. Act, preferring elements over pixels:
   - By element, through UI Automation: `islo-desktop exec "agent-desktop ..."`. Find controls by role and name, then `set-value`, `select`, or `click` them by ref. See [UI Automation with agent-desktop](references/ui-automation.md).
   - By coordinates and keys, for apps that expose little to UI Automation: `click`, `type`, `key`. See [commands](references/commands.md).
5. Verify after every change: read values back with agent-desktop or take a screenshot. Never assume an action took effect.
6. Record: `islo-desktop record C:\workspace\clip.mp4 -Seconds 10` blocks while it records, so use it for a still state. To record your own actions, run `record` in the background on your side, do the steps, then wait for it (see [recording a flow](references/commands.md#recording-a-flow)).
7. `islo-desktop stop` ends the session and switches Remote Desktop off again. Always stop when done.

## Rules

- Never start GUI programs with plain exec; use `islo-desktop run`, or the window is never drawn.
- Use `select` for drop-down lists and `set-value` for text fields and editable comboboxes. When fields depend on each other (a choice that repopulates another list), set them in dependency order and read all values back.
- Give agent-desktop room on large or freshly opened UIs: add `--timeout-ms 20000`. A `TIMEOUT` error means the tree had not settled, not that the control is missing.
- Refs (`@s1:e3`) belong to the `find` or `snapshot` that returned them. After the UI changes, find again; a stale ref fails with `STALE_REF`.
- Press dialog buttons by name with agent-desktop `click`, or with Alt plus the underlined letter (`islo-desktop key "%n"` for Do&n't Save). A bare letter can be swallowed.
- `-Window <title or process>` targets an enabled window; while a modal dialog is open, its owner is disabled and skipped, so input goes to the dialog.
- Screenshot pixel coordinates are click coordinates.
- Do not enable Remote Desktop for remote access or create other accounts. The session is loopback-only by design and blocked from outside the VM.

## Getting files out

Screenshots and recordings are written inside the sandbox (default `C:\workspace`). `islo cp` does not support Windows sandboxes yet; read files as base64 through exec:

```bash
islo use my-win -- powershell -NoProfile -Command "[Convert]::ToBase64String([IO.File]::ReadAllBytes('C:\workspace\shot.png'))" \
  | sed 's/^data: //' | tr -d '\r\n ' | base64 -d > shot.png
```

Keep files small for this path: screenshots and short recordings are fine; large files are slow.
