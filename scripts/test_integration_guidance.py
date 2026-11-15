"""Check integration command restrictions and documentation link resolution."""

import tempfile
import unittest
from pathlib import Path

from validate_integration_guidance import validate_links, validate_text


class IntegrationGuidanceTests(unittest.TestCase):
    def test_rejects_the_reviewed_instructions(self):
        for content in (
            "Connect integrations with `islo login --tool <provider>`.",
            "islo factory triggers list --with-status",
            "islo login --tool github   # required for private repos",
            "| Trigger fired but no run appeared | `islo factory triggers list --with-status` |",
        ):
            with self.subTest(content=content):
                self.assertEqual(validate_text(content), [1])

    def test_allows_browser_cards_and_the_unannotated_catalog(self):
        self.assertEqual(validate_text(
            "[GitHub](/integrations?connect=github&view=connect)\n"
            "islo factory triggers list\n"
            "islo factory line-run status <run-id>"
        ), [])

    def test_allows_explicit_prohibitions_and_outside_sandbox_commands(self):
        for content in (
            "Do not run `islo login --tool` or `islo status` inside a sandbox.",
            "Never run `islo factory triggers list --with-status` in a sandbox.",
            "From a local terminal outside a sandbox, run `islo status`.",
            "`islo status` uses endpoints that reject sandbox callers.",
        ):
            with self.subTest(content=content):
                self.assertEqual(validate_text(content), [])

    def test_scope_on_one_line_does_not_authorize_another_instruction(self):
        self.assertEqual(validate_text(
            "Do not run `islo status` inside a sandbox.\n"
            "Connect with `islo login --tool github`."
        ), [2])


class IntegrationLinkTests(unittest.TestCase):
    def test_relative_files_and_anchors_resolve(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "SKILL.md"
            reference = root / "using providers.md"
            source.write_text(
                "# Check connections\n"
                "[same file](#check-connections)\n"
                "[provider](using%20providers.md#github-and-linear)\n"
                "[duplicate](using%20providers.md#github-and-linear-1)\n"
                "[external](https://example.com/missing#anchor)\n"
                "[app](/integrations?connect=github&view=connect)\n"
            )
            reference.write_text("# GitHub and Linear\n## GitHub and Linear\n")
            self.assertEqual(validate_links(source), [])

    def test_rejects_missing_files_and_removed_anchors(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "SKILL.md"
            source.write_text(
                "# Connections\n"
                "[missing](references/removed.md)\n"
                "[removed](#old-connection-gate)\n"
            )
            errors = validate_links(source)
            self.assertEqual(len(errors), 2)
            self.assertIn("references/removed.md", errors[0])
            self.assertIn("#old-connection-gate", errors[1])

    def test_ignores_links_and_headings_in_code_examples(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "SKILL.md"
            source.write_text(
                "```markdown\n# Example heading\n[example](missing.md)\n```\n"
                "`[inline example](missing.md)`\n"
                "[bad anchor](#example-heading)\n"
            )
            errors = validate_links(source)
            self.assertEqual(len(errors), 1)
            self.assertIn("#example-heading", errors[0])


if __name__ == "__main__":
    unittest.main()
