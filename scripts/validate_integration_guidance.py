"""Validate integration guidance and its relative Markdown links and anchors."""

import re
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

SKILLS = Path(__file__).resolve().parents[1] / "plugins/islo/skills"
SKILL_NAMES = ("factory-lines", "platform", "integrations")
LINK = re.compile(r"\[[^]\n]+\]\(([^)\s]+)\)")
BLOCKED_COMMAND = re.compile(
    r"\bislo (?:login --tool\b|factory triggers list --with-status\b)"
)
SAFE_CONTEXT = re.compile(
    r"do not run|never run|outside (?:a )?sandbox|outside sandboxes|reject sandbox callers",
    re.IGNORECASE,
)


def validate_text(content: str) -> list[int]:
    """Return lines that prescribe blocked commands without an explicit scope."""
    return [
        number
        for number, line in enumerate(content.splitlines(), 1)
        if BLOCKED_COMMAND.search(line) and not SAFE_CONTEXT.search(line)
    ]


def prose(content: str) -> str:
    """Remove code examples while preserving line numbers for diagnostics."""
    lines = []
    fence = None
    for line in content.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence:
            closing = rf" {{0,3}}{re.escape(fence[0])}{{{len(fence)},}}\s*"
            if re.fullmatch(closing, line):
                fence = None
            lines.append("")
        elif marker:
            fence = marker.group(1)
            lines.append("")
        else:
            lines.append(line)
    return "\n".join(lines)


def anchors(content: str) -> set[str]:
    """Return GitHub-style heading anchors, including duplicate suffixes."""
    found = set()
    for line in prose(content).splitlines():
        heading = re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not heading:
            continue
        title = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", heading.group(1))
        title = re.sub(r"<[^>]*>", "", title).lower()
        slug = "".join(
            char
            for char in title
            if char in "-_ " or unicodedata.category(char)[0] in "LN"
        ).replace(" ", "-")
        candidate = slug
        suffix = 0
        while candidate in found:
            suffix += 1
            candidate = f"{slug}-{suffix}"
        found.add(candidate)
    return found


def validate_links(source: Path) -> list[str]:
    """Check documentation links, excluding external URLs and app routes."""
    failures = []
    for number, line in enumerate(prose(source.read_text()).splitlines(), 1):
        line = re.sub(r"(`+).*?\1", "", line)
        for target in LINK.findall(line):
            url = urlsplit(target)
            if url.scheme or url.netloc or target.startswith("/"):
                continue
            destination = source.parent / unquote(url.path) if url.path else source
            if not destination.is_file():
                failures.append(f"{source}:{number}: missing relative file {target}")
            elif (
                url.fragment
                and unquote(url.fragment) not in anchors(destination.read_text())
            ):
                failures.append(f"{source}:{number}: missing heading anchor {target}")
    return failures


def validate_integration_skill() -> list[str]:
    skill = SKILLS / "integrations/SKILL.md"
    if not skill.is_file():
        return [f"{skill}: missing skill entrypoint"]
    # This skill uses only the two required plain YAML scalars.
    if not re.match(
        r"\A---\nname: integrations\n"
        r"description: [A-Za-z][A-Za-z0-9 ,.;/()\-]*[A-Za-z0-9.]\n---\n",
        skill.read_text(),
    ):
        return [f"{skill}: expected valid name and description frontmatter"]
    return []


def main() -> int:
    failures = validate_integration_skill()
    for name in SKILL_NAMES:
        for path in sorted((SKILLS / name).rglob("*.md")):
            failures.extend(validate_links(path))
            for number in validate_text(path.read_text()):
                failures.append(
                    f"{path.relative_to(SKILLS)}:{number}: "
                    "Use the integrations skill for connection checks. "
                    "Scope any retained connection CLI command to outside a sandbox "
                    "or explicitly prohibit running it in the sandbox."
                )
    if failures:
        print("\n".join(failures))
        return 1
    print("Integration guidance, frontmatter, relative links, and anchors are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
