#!/usr/bin/env python3
"""Validate the Factory Machines skill's static metadata and local Markdown links."""

import re
from pathlib import Path


SKILL = Path(__file__).resolve().parent.parent / "plugins/islo/skills/factory-machines/SKILL.md"
LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")


def validate() -> None:
    content = SKILL.read_text()
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", content, re.DOTALL)
    assert frontmatter, "SKILL.md needs YAML frontmatter"
    # Accept only two plain scalar fields. Excluding YAML collection, quote,
    # comment, and block markers makes malformed YAML fail without a dependency.
    fields = re.fullmatch(
        r"name: (?P<name>[a-z][a-z0-9-]*)\n"
        r"description: (?P<description>[A-Za-z][A-Za-z0-9 ,.;/()\-]*[A-Za-z0-9.])",
        frontmatter.group(1),
    )
    assert fields, "frontmatter must contain valid name and description scalars"
    assert fields.group("name") == "factory-machines"

    files = [SKILL, *sorted((SKILL.parent / "references").glob("*.md"))]
    assert len(files) > 1, "skill needs focused references"
    for source in files:
        for target in LINK.findall(source.read_text()):
            if "://" not in target and not target.startswith("#"):
                assert (source.parent / target.split("#", 1)[0]).is_file(), (
                    f"{source}: missing local reference {target}"
                )

    lifecycle = (SKILL.parent / "references/lifecycle.md").read_text()
    surfaces = (SKILL.parent / "references/surfaces.md").read_text()
    for required in (
        "`cli start` and `cli health`",
        "Run `cli stop` before the inspect stage finishes",
        "backing process start command, readiness check, and publication command",
        "when inside a line run",
        "Outside a line run",
    ):
        assert required in lifecycle, f"lifecycle guidance missing: {required}"
    for required in (
        "`islo surface --help`",
        "`web` and `terminal`",
        "multiple useful interfaces or none",
        "A listening port alone",
        "blind port scanning",
        "healthy and reachable through the sandbox",
        "**public web share**",
        "secrets",
        "persistent user-facing TUI, REPL, live log view",
        "Do not publish an ordinary shell",
        "Never expose databases, debug ports, internal metrics",
    ):
        assert required in surfaces, f"Surface guidance missing: {required}"


if __name__ == "__main__":
    validate()
    print("validated Factory Machines skill frontmatter and local references")
