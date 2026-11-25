# islo-desktop commands

All commands run inside the Windows sandbox. From outside, prefix each with `islo use <sandbox> -- cmd /c`. `islo-desktop help` prints the installed version's usage, which is the source of truth.

| Command | Does |
|---|---|
| `islo-desktop start [-Width 1920 -Height 1080]` | Start the desktop session (Remote Desktop from the VM to itself, account `islo-desktop`). Idempotent. |
| `islo-desktop status` | Show the session: id, state, whether the shell is ready. |
| `islo-desktop run <program> [args...] [-Wait]` | Start a program in the session. Returns when it has started; `-Wait` waits for it to exit and returns its exit code. |
| `islo-desktop exec "<command line>" [-TimeoutSec 300]` | Run a command line in the session and return its output and exit code. Pass the whole command line as one quoted string. Used for agent-desktop. |
| `islo-desktop windows` | List visible windows: handle, process, `x= y= w= h=`, title. `*` marks the foreground window; `(disabled: a dialog is open)` marks windows blocked by a modal dialog. |
| `islo-desktop type "<text>" [-Window <title or process>]` | Bring a window to the front (default: the topmost) and type. `\n` in the text is Enter. |
| `islo-desktop key "<keys>" [-Window <title or process>]` | Press keys in SendKeys syntax: `^` Ctrl, `%` Alt, `+` Shift, `{ENTER}`, `{TAB}`, `{ESC}`, `{F4}`, `{DOWN}`. Examples: `"^s"`, `"%{F4}"`, `"%n"`. |
| `islo-desktop click <x> <y> [-Right] [-Double] [-Window <title or process>]` | Click at screen coordinates, the same coordinates as in screenshots. |
| `islo-desktop screenshot [file.png]` | Capture the whole desktop. Default `C:\workspace\desktop-<time>.png`. |
| `islo-desktop record [file.mp4] [-Seconds 10 -Fps 10]` | Record the desktop (H.264) and wait until done. |
| `islo-desktop stop` | Log the session off, disable its account, switch Remote Desktop off. |

Exit codes: 0 on success, 1 on errors (message on stderr); `run -Wait` and `exec` return the program's exit code.

`-Window` matches a title substring or an exact process name, case-insensitively, and only among enabled windows.

## Recording a flow

`record` blocks while it records. To capture steps as you take them, run it in the background on your side and act meanwhile:

```bash
W="islo use my-win -- cmd /c"
$W islo-desktop record 'C:\workspace\flow.mp4' -Seconds 30 &
sleep 2
# ... drive the app with run, exec agent-desktop, click, type, key ...
wait   # returns when the 30 s recording is written
```

Do not pass ffmpeg options through `islo-desktop run ffmpeg ...`: arguments that start with `-` are read as islo-desktop's own parameters.

ffmpeg in the image is an LGPL build; use `libopenh264` for H.264 (`libx264` is not included).

## Notes

- `start` creates the session account with a new random password each time; nothing is stored in plain text. Do not try to log in as it.
- Programs started with `run`, and agent-desktop through `exec`, run elevated as the session account, so they can drive each other.
- The session keeps running until `stop`, a sandbox restart, or the sandbox is deleted.
