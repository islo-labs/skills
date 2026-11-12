"""Keep Factory chat-link examples explicit and keyed."""

from pathlib import Path
import re

SKILLS = Path(__file__).resolve().parents[1] / "plugins/islo/skills"
FACTORY_URL = re.compile(r"/(?:factory|factories)/[^\s`\])]+")


def violations(text: str) -> list[str]:
    return [
        match.group()
        for match in FACTORY_URL.finditer(text)
        if match.group().startswith("/factory/")
        or match.group().startswith("/factories/FACTORY_ID/")
    ]


def main() -> int:
    failures = []
    for path in sorted(SKILLS.rglob("*.md")):
        for url in violations(path.read_text()):
            failures.append(f"{path.relative_to(SKILLS)}: {url}: use /factories/FACTORY_KEY/ and resolve the object's Factory key")
    if failures:
        print("\n".join(failures))
        return 1
    print("Factory chat-link examples use explicit keys.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
