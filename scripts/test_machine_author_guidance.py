"""Guard the Machine Author's discovery and blocked credential report."""

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

    def test_stops_for_credentials_and_lists_all_external_actions(self):
        for rule in (
            "Return author_state `blocked` with empty `questions` and end the turn",
            "Do not post a question or wait for an answer",
            "Do not try to attach credentials, gateway profiles, or environments from the sandbox",
            "report the work as blocked and list every action the user must take outside the sandbox",
            "Name each blocked component, failed command, required setting name, and registry host/package",
            "obtain an approved credential, add a gateway allow rule for the host, and attach that profile to the Machine",
            "create an environment if needed, add all required settings, and attach it to the Machine",
            "Start a new build after all attachments are complete so its sandbox receives the credentials",
            "Preserve completed work",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, MACHINES)

    def test_removes_the_attachment_section_and_rebuild_question(self):
        self.assertNotIn("## Credentials the sandbox cannot attach", MACHINES)
        self.assertNotIn("I attached the profile; rebuild", MACHINES)
        self.assertNotIn("Ask the user to create the environment", MACHINES)
        self.assertNotIn("missing-environment question rules", MACHINES)


if __name__ == "__main__":
    unittest.main()
