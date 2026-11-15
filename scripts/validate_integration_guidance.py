"""Reject sandbox-blocked connection commands in agent skill instructions."""

from pathlib import Path
import re

SKILLS = Path(__file__).resolve().parents[1] / "plugins/islo/skills"
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


def main() -> int:
    failures = []
    for name in ("factory-lines", "platform"):
        for path in sorted((SKILLS / name).rglob("*.md")):
            for number in validate_text(path.read_text()):
                failures.append(
                    f"{path.relative_to(SKILLS)}:{number}: "
                    "Use a browser connect card for integration status. "
                    "Scope any retained connection CLI command to outside a sandbox "
                    "or explicitly prohibit running it in the sandbox."
                )
    if failures:
        print("\n".join(failures))
        return 1
    print("Integration connection guidance agrees across both skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
