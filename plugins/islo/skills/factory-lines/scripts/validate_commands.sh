#!/usr/bin/env bash
# Validate every `islo ...` command in fenced bash blocks across both skills
# against the installed CLI: the subcommand path must resolve and every --flag
# must appear in that subcommand's --help output.
#
# scripts/pending_commands.txt lists subcommand paths documented ahead of a CLI
# release (one per line, e.g. "factory line-run stop"). A command that fails
# resolution but matches a pending entry reports PENDING, not FAIL. A pending
# entry that now resolves FAILS the run: delete the stale entry.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 - "$here" <<'PY'
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

here = Path(sys.argv[1])
skills_root = here.parent.parent
pending_file = here / "pending_commands.txt"

if subprocess.run(["which", "islo"], capture_output=True).returncode != 0:
    sys.exit("islo CLI not on PATH")

md_files = sorted(
    p for d in ("factory-lines", "platform")
    for p in (skills_root / d).rglob("*.md")
    if (skills_root / d).is_dir()
)
if not md_files:
    sys.exit(f"no skill markdown found under {skills_root}")

pending = []
if pending_file.is_file():
    for line in pending_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            pending.append(line)


@lru_cache(maxsize=None)
def get_help(path: str):
    """Return (ok, help_text) for `islo <path> --help`."""
    cmd = ["islo", *path.split(), "--help"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode == 0, proc.stdout + proc.stderr


def bash_lines(md: Path):
    inblock = False
    for line in md.read_text().splitlines():
        if re.match(r"^```(bash|sh)\s*$", line):
            inblock = True
            continue
        if line.startswith("```"):
            inblock = False
            continue
        if inblock:
            yield line


WORD = re.compile(r"^[a-z][a-z0-9-]*$")
fail = False

for md in md_files:
    rel = md.relative_to(skills_root)
    for raw in bash_lines(md):
        line = raw.strip()
        if not (line == "islo" or line.startswith("islo ")):
            continue
        line = line.split("#", 1)[0].strip()
        toks = line.split()
        words, flags = [], []
        for t in toks[1:]:
            if t.startswith("--"):
                flags.append(t.split("=", 1)[0])
            elif not flags and WORD.match(t):
                words.append(t)

        full = " ".join(words)
        match = next((p for p in pending if full.startswith(p)), None)
        if match:
            print(f"PENDING {rel}: islo {full} (awaiting CLI release: {match})")
            continue

        # Resolve the deepest path the CLI recognizes; trailing words may be
        # positional values that only look like subcommands.
        # The root command has no positionals, so a real invocation must
        # resolve at least its first word (n >= 1).
        resolved = None
        for n in range(len(words), 0, -1):
            path = " ".join(words[:n])
            ok, _ = get_help(path)
            if ok:
                resolved = path
                break

        if resolved is None:
            print(f"FAIL {rel}: cannot resolve: {line}")
            fail = True
            continue

        _, help_text = get_help(resolved)
        bad = [f for f in flags if f != "--" and f not in help_text]
        for f in bad:
            print(f"FAIL {rel}: flag {f} not in 'islo {resolved} --help': {line}")
            fail = True
        if not bad:
            suffix = f" [{' '.join(flags)}]" if flags else ""
            print(f"ok   {rel}: islo {resolved or '<root>'}{suffix}")

for p in pending:
    ok, _ = get_help(p)
    if ok:
        print(f"FAIL stale pending entry (CLI now ships it): {p}")
        fail = True

sys.exit(1 if fail else 0)
PY
