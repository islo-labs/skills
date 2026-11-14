"""Guard the Machine Author's discovery and outside-sandbox credential handoff."""

from pathlib import Path
import unittest


MACHINES = (
    Path(__file__).resolve().parents[1]
    / "plugins/islo/skills/factory-lines/references/machines.md"
).read_text()


class MachineAuthorGuidanceTests(unittest.TestCase):
    def test_reuses_discovery_and_reads_the_named_component(self):
        for rule in (
            "Read CI workflows and repository docs once, on the first author turn",
            "On later turns, use that discovery",
            "Open a workflow again only when a repository was added",
            "earlier read missed the component named in this turn's instructions",
            "read that component's CI job and the docs it points at",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, MACHINES)
        self.assertNotIn("before you ask anything", MACHINES)

    def test_hands_credential_attachment_to_the_person(self):
        for rule in (
            "do not create, list, or attach a Machine environment or gateway profile",
            "Do not run `islo environment`, `islo gateway`, or `islo factory machine update`",
            "`islo factory machine get` stays allowed",
            "Name the host and the package",
            "Add a gateway allow rule for that host using the approved credential",
            "Attach that profile on the Machine",
            "gateway-profile edit on a ready Machine publishes a template version",
            "create the environment and attach it",
            "environment edit starts a new build that runs Author",
            "Start a new build after the attachment",
            "I attached the profile; rebuild",
            "empty `questions` only after that question POST succeeds",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, MACHINES)

    def test_links_the_machine_environment_and_gateway(self):
        for rule in (
            "islo factory current --output json",
            "factory.key",
            "[MACHINE_NAME](/factories/FACTORY_KEY/machines/MACHINE_NAME?view=card)",
            "[ENVIRONMENT_NAME](/settings/environments/ENVIRONMENT_ID?view=card)",
            "only when `islo factory machine get` returns an environment id",
            "https://app.islo.dev/settings/environments",
            "https://app.islo.dev/settings/gateway",
            "Gateway has no chat embed",
            "Put each embed in its own paragraph",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, MACHINES)


if __name__ == "__main__":
    unittest.main()
