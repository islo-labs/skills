# UI Automation with agent-desktop

[agent-desktop](https://github.com/vercel-labs/agent-desktop) reads a window's UI Automation tree and acts on elements by ref, so forms can be filled by control name instead of pixel coordinates. It must run inside the desktop session; call it through `islo-desktop exec` with the whole command line as one string. Every command prints one JSON envelope: `{"ok": true, "data": ...}` or `{"ok": false, "error": {"code": ..., "message": ..., "suggestion": ...}}`.

`agent-desktop <command> --help` prints the installed version's options.

## Fill a form

Example: Notepad's Font dialog (Format > Font).

```bash
W="islo use my-win -- cmd /c"
$W islo-desktop exec "agent-desktop list-windows"
#   data[]: id "w-458782", title "Font", app_name "notepad.exe", bounds ...
$W islo-desktop exec "agent-desktop find --window-id w-458782 --role combobox --timeout-ms 20000"
#   data.matches[]: {ref_id "@s38x:e1", name "Font:",       value "Consolas"}
#                   {ref_id "@s38x:e2", name "Font style:", value "Regular"}
#                   {ref_id "@s38x:e3", name "Size:",       value "11"}
#                   {ref_id "@s38x:e4", name "Script:",     value "Western"}
$W islo-desktop exec "agent-desktop select @s38x:e4 Greek --timeout-ms 20000"
$W islo-desktop exec "agent-desktop set-value @s38x:e3 28 --timeout-ms 20000"
$W islo-desktop exec "agent-desktop set-value @s38x:e2 Bold --timeout-ms 20000"
$W islo-desktop exec "agent-desktop find --window-id w-458782 --role combobox --timeout-ms 20000"
#   read back: Script=Greek, Size=28, Font style=Bold
$W islo-desktop exec "agent-desktop find --window-id w-458782 --role button --name OK --exact"
$W islo-desktop exec "agent-desktop click @s91q:e1"
```

## Choosing the action

| Control | Action |
|---|---|
| Drop-down list (pick from fixed items) | `select <ref> "<item text>"` |
| Text field, editable combobox (Font style, Size above) | `set-value <ref> "<text>"`; `select` returns `ACTION_NOT_SUPPORTED` on these |
| Button, link, menu item, tab | `click <ref>` |
| Checkbox, toggle | `check` / `uncheck` / `toggle` |
| Tree or expandable item | `expand` / `collapse` |

## Finding controls

- `find --window-id <id> --role <role> [--name <name> --exact]` returns matching elements with ref, name, and value. Roles include `button`, `combobox`, `textfield`, `checkbox`, `listitem`, `menuitem`, `tab`.
- `snapshot --window-id <id> -i --compact` returns the interactive tree. On windows with long lists the tree can be truncated (`"complete": false`); use `find` for specific controls.
- Each `find` or `snapshot` issues new refs. After the UI changes (a dialog opens, a list repopulates), find again before acting.

## Pitfalls

- `TIMEOUT` ("did not stabilize before its deadline"): the tree was still changing. Add `--timeout-ms 20000` or more; freshly opened dialogs and long lists need it.
- `"application_commit": "not_verified"` in a success reply means agent-desktop set the value but cannot prove the app accepted it. Read the value back, or screenshot.
- Changing one field can reset another (choosing Script resets Font style). Set fields in dependency order and verify all of them at the end.
- Apps that draw their own UI (games, canvas-based UIs, some Java apps) expose little to UI Automation. Fall back to screenshots plus `islo-desktop click`, `type`, and `key`.
- Chromium and Electron apps can need extra time before their tree is complete; agent-desktop's error suggestion says what to raise.
