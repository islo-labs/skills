"""Regression checks for the Surfaces skill and its validator."""

import shutil
import tempfile
from pathlib import Path

import validate_surfaces_skill as validator


def test_router_defines_the_stage_capability_boundary() -> None:
    content = validator.SKILL.read_text()

    assert "stage agent" in content
    assert "line-run Surface environment" in content
    assert "Line Manager" in content


def test_web_guidance_verifies_service_locally() -> None:
    usage = (validator.SKILL.parent / "references/usage.md").read_text()

    assert "0.0.0.0" in usage
    assert "http://localhost:PORT" in usage
    assert "401" in usage
    assert "private" in usage
    assert "--public" in usage
    assert "returned Surface URL works" not in usage


def test_validator_rejects_malformed_yaml_frontmatter() -> None:
    with tempfile.TemporaryDirectory() as temporary_dir:
        skill_dir = Path(temporary_dir)
        skill = skill_dir / "SKILL.md"
        original = validator.SKILL.read_text()
        skill.write_text(original.replace("description: Publish", "description: [unfinished"))
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
    test_router_defines_the_stage_capability_boundary()
    test_web_guidance_verifies_service_locally()
    print("validated Surfaces router and malformed-frontmatter rejection")
