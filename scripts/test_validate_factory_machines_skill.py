"""Regression checks for the Factory Machines skill and its validator."""

import shutil
import tempfile
from pathlib import Path

import validate_factory_machines_skill as validator


def test_router_includes_line_manager_delegation() -> None:
    content = validator.SKILL.read_text()

    assert "Line Manager" in content
    assert "stage agent" in content
    assert "do not invoke `islo surface`" in content


def test_validator_rejects_malformed_yaml_frontmatter() -> None:
    with tempfile.TemporaryDirectory() as temporary_dir:
        skill_dir = Path(temporary_dir)
        skill = skill_dir / "SKILL.md"
        original = validator.SKILL.read_text()
        skill.write_text(original.replace("description: Build,", "description: [unfinished"))
        shutil.copytree(validator.SKILL.parent / "references", skill_dir / "references")
        previous = validator.SKILL
        validator.SKILL = skill
        try:
            try:
                validator.validate()
            except AssertionError:
                pass
            else:
                raise AssertionError("malformed YAML frontmatter passed validation")
        finally:
            validator.SKILL = previous

if __name__ == "__main__":
    test_validator_rejects_malformed_yaml_frontmatter()
    test_router_includes_line_manager_delegation()
    print("validated Factory Machines router and malformed-frontmatter rejection")
