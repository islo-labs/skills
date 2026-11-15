"""Reject Job authoring paths in the new-Line guidance."""

from pathlib import Path
import re

SKILL = Path(__file__).resolve().parents[1] / "plugins/islo/skills/factory-lines"
NEW_LINE_FILES = (
    "SKILL.md",
    "references/create-a-line.md",
    "references/factory-design.md",
    "references/agents-and-managers.md",
    "references/line-manifest.md",
)
FORBIDDEN = re.compile(
    r"\bislo\s+job\s+init\b|\binternal[\s-]+jobs?\b|\bjob\s*=",
    re.IGNORECASE,
)


def violations(content: str) -> list[int]:
    return sorted({
        content.count("\n", 0, match.start()) + 1
        for match in FORBIDDEN.finditer(content)
    })


def main() -> int:
    failures = []
    for name in NEW_LINE_FILES:
        for line in violations((SKILL / name).read_text()):
            failures.append(
                f"{name}:{line}: New Lines use Agent stages only. "
                "Report missing Agent capabilities and stop the dependent design. "
                "Keep existing Job maintenance in its dedicated references."
            )
    if failures:
        print("\n".join(failures))
        return 1
    print("New-Line guidance uses Agent stages only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
