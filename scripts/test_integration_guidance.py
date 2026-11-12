"""Keep the conflicting instructions from ISL-2448 out of skill entrypoints."""

import unittest

from validate_integration_guidance import validate_text


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


if __name__ == "__main__":
    unittest.main()
