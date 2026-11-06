"""Guard against conflicting selection, goal, and verification instructions."""

from pathlib import Path
import unittest


REFERENCE = (
    Path(__file__).resolve().parents[1]
    / "plugins/islo/skills/factory-lines/references/machines.md"
)


class MachineAuthorGuidanceTests(unittest.TestCase):
    def test_existing_definitions_are_preserved_and_only_new_modules_are_offered(self):
        text = REFERENCE.read_text()
        for rule in (
            "Keep every module that already has a `component.toml` selected",
            "(already defined)",
            "(new)",
            "Pre-select a new CI module",
            "If nothing is new, continue without the inclusion question",
            "If exactly one module is discovered, skip the question",
            "unless a selected module requires it",
        ):
            with self.subTest(rule=rule):
                self.assertTrue(rule in text, f"Missing guidance: {rule}")
        self.assertFalse("Include none" in text)
        self.assertFalse("uses single_choice" in text)

    def test_optional_worker_does_not_expand_an_existing_api_machine(self):
        text = REFERENCE.read_text()
        for rule in (
            "When existing component definitions are present and only one new module remains",
            "include it only if CI builds or tests it or a selected module requires it",
            "Otherwise leave the optional docs-only module unselected and continue with the existing set",
            "with an already-defined API and one unrelated docs-only worker, keep the API selected and leave the worker unselected",
        ):
            with self.subTest(rule=rule):
                self.assertTrue(rule in text, f"Missing guidance: {rule}")
        self.assertFalse("Apply the same skip when only one new module remains" in text)

    def test_goals_precede_boot_but_do_not_add_a_verify_gate(self):
        text = REFERENCE.read_text()
        for rule in (
            "Ask once whether those goals are good enough, then stop",
            "Do not start services on that turn",
            "not a second pass gate",
            "`islo machine verify` starts every active driver in `depends_on` order",
            "runtime entrypoints for every driver in the active set",
            "Done means `islo machine verify` passes at the Machine level",
            "A test runs only when its entrypoint exists",
        ):
            with self.subTest(rule=rule):
                self.assertTrue(rule in text, f"Missing guidance: {rule}")
        for stale_rule in (
            "whose own command runs without another selected module",
            "for modules that can run alone",
            "cannot boot independently",
            "Passive modules still run install, build, and test",
            "solo boot",
        ):
            with self.subTest(stale_rule=stale_rule):
                self.assertFalse(stale_rule in text, f"Stale guidance: {stale_rule}")

    def test_settings_and_surfaces_keep_the_same_boundaries(self):
        text = REFERENCE.read_text()
        for rule in (
            "Ask only for a setting name that is missing",
            "It does not ask for the value",
            "Ask the user to create the environment and start a new Machine build",
            "Do not publish internal services or resource ports",
            "does not fail `islo machine verify`",
            "instructions.md",
            "actual address it bound in `url`",
        ):
            with self.subTest(rule=rule):
                self.assertTrue(rule in text, f"Missing guidance: {rule}")
        self.assertFalse(
            "Do not ask for an environment variable or a remote URL at either level"
            in text
        )


if __name__ == "__main__":
    unittest.main()
