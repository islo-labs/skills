"""Keep Islo chat behaviour inside the islo-chat skill.

The `islo-chat` skill holds everything that only works in Islo chat (connection
cards, object embeds). Other skills are used from Cursor, Claude Code, Codex,
and local terminals, so they must stay CLI-first and must not contain chat-only
links.
"""

from pathlib import Path
import re

SKILLS = Path(__file__).resolve().parents[1] / "plugins/islo/skills"
CHAT = "islo-chat"
LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")
# Relative app links that render as cards or embeds only in Islo chat.
CHAT_EMBED = re.compile(r"\]\(/(?:integrations|factor(?:y|ies))\b[^)]*\bview=")
GATED_BY = re.compile(r"\bexplicitly\b", re.IGNORECASE)


def chat_only_lines(content: str) -> list[int]:
    """Return lines that contain a chat-only embed link."""
    return [
        number
        for number, line in enumerate(content.splitlines(), 1)
        if CHAT_EMBED.search(line)
    ]


def skill_description(content: str) -> str:
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", content, re.DOTALL)
    if not frontmatter:
        return ""
    match = re.search(r"^description: (.*)$", frontmatter.group(1), re.MULTILINE)
    return match.group(1) if match else ""


def main() -> int:
    failures = []

    chat_skill = SKILLS / CHAT / "SKILL.md"
    if not chat_skill.is_file():
        failures.append(f"{CHAT}/SKILL.md is missing")
    else:
        description = skill_description(chat_skill.read_text())
        if not GATED_BY.search(description) or "Islo chat" not in description:
            failures.append(
                f"{CHAT}/SKILL.md: description must say the skill applies only "
                "when explicitly told the agent is inside Islo chat"
            )
        for source in sorted((SKILLS / CHAT).rglob("*.md")):
            for target in LINK.findall(source.read_text()):
                if "://" in target or target.startswith(("#", "/")):
                    continue
                if not (source.parent / target.split("#", 1)[0]).is_file():
                    failures.append(
                        f"{source.relative_to(SKILLS)}: missing local reference {target}"
                    )

    for skill in sorted(path for path in SKILLS.iterdir() if path.is_dir()):
        if skill.name == CHAT:
            continue
        for path in sorted(skill.rglob("*.md")):
            for number in chat_only_lines(path.read_text()):
                failures.append(
                    f"{path.relative_to(SKILLS)}:{number}: chat-only card or embed "
                    f"link. Move it to the {CHAT} skill; other hosts cannot render it."
                )

    for name in ("factory-lines", "platform"):
        if f"`{CHAT}`" not in (SKILLS / name / "SKILL.md").read_text():
            failures.append(
                f"{name}/SKILL.md: must point to the {CHAT} skill for Islo chat"
            )

    if failures:
        print("\n".join(failures))
        return 1
    print("Chat-only behaviour is confined to the islo-chat skill.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
