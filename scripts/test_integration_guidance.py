"""Tests for the rule that chat-only behaviour lives only in islo-chat."""

import unittest

from validate_integration_guidance import chat_only_lines, skill_description


class IntegrationGuidanceTests(unittest.TestCase):
    def test_flags_chat_cards_and_embeds(self):
        for content in (
            "[GitHub](/integrations?connect=github&view=connect)",
            "[Run](/factories/ID/runs/lines/RUN?view=card)",
            "[Runs](/factory/runs?view=inbox)",
        ):
            with self.subTest(content=content):
                self.assertEqual(chat_only_lines(content), [1])

    def test_reports_the_line_number(self):
        self.assertEqual(
            chat_only_lines("text\n[Slack](/integrations?connect=slack&view=connect)"),
            [2],
        )

    def test_allows_cli_first_instructions(self):
        self.assertEqual(
            chat_only_lines(
                "Connect with `islo login --tool github`.\n"
                "Check `islo status`.\n"
                "Run `islo factory triggers list --with-status`.\n"
                "See [the docs](https://app.islo.dev/integrations)."
            ),
            [],
        )

    def test_reads_the_description(self):
        content = "---\nname: x\ndescription: Only when explicitly told.\n---\nbody"
        self.assertEqual(skill_description(content), "Only when explicitly told.")
        self.assertEqual(skill_description("no frontmatter"), "")


if __name__ == "__main__":
    unittest.main()
