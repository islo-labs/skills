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

    def test_distinguishes_non_sensitive_configuration_from_secrets(self):
        for rule in (
            "Classify each setting by its value and use, not just its name.",
            "A local container database URL or a feature flag can be non-sensitive configuration.",
            "Real credentials embedded in a URL are still secrets.",
            "Public, disposable fixture values documented for local containers are non-sensitive; never reuse real service credentials as fixture defaults.",
            "If sensitivity is uncertain, treat the value as sensitive and never solicit it in a question.",
            "At build and verify, propose documented simple or default values for non-sensitive configuration needed to build, test, or start a component.",
            "When a decision is needed, ask the user to provide or confirm the non-sensitive value before running the dependent verb.",
            "Use the existing choice-question flow and return `needs_input`; the automatic Other option accepts a custom non-sensitive value.",
            "Inject the selected non-sensitive values into the relevant Machine verb scripts as safely quoted environment defaults before the repository command.",
            "Preserve environment overrides and treat values as data, never shell code; do not use eval.",
            "Put names supplied by script defaults in `[environment].optional`, even when absent from the sandbox environment, so preflight does not require them.",
            "A missing Machine environment alone does not block work that needs only non-sensitive configuration supplied by the scripts.",
            "Never solicit secret values in ordinary configuration questions or put them in scripts, summaries, logs, or commits.",
            "When required sensitive settings, credentials, tokens, API keys, or registry/package access cannot be supplied from this sandbox, stop work immediately.",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, MACHINES)
        for obsolete in (
            "At build, the only question before work is which newly discovered modules to build and test.",
            "Do not ask the person to add an environment variable at build.",
            "Do not ask for a missing value.",
            "When required registry/package credentials, settings, or a Machine environment cannot be supplied from this sandbox",
        ):
            with self.subTest(obsolete=obsolete):
                self.assertNotIn(obsolete, MACHINES)
        author_guidance = MACHINES.split("## How to discover configuration", 1)[
            1
        ].split("## Build lifecycle", 1)[0]
        self.assertNotIn("view=card", author_guidance)
        self.assertNotIn("/settings/environments", author_guidance)
        self.assertNotIn("/settings/gateway", author_guidance)

    def test_removes_the_attachment_section_and_rebuild_question(self):
        self.assertNotIn("## Credentials the sandbox cannot attach", MACHINES)
        self.assertNotIn("I attached the profile; rebuild", MACHINES)
        self.assertNotIn("Ask the user to create the environment", MACHINES)
        self.assertNotIn("missing-environment question rules", MACHINES)


if __name__ == "__main__":
    unittest.main()
