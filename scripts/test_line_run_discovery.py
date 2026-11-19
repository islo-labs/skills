"""Validate the discovery instructions shipped to agents before lookup."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/islo/skills/factory-lines"


class LineRunDiscoveryTests(unittest.TestCase):
    def test_entrypoint_and_prerun_guidance_load_bounded_discovery(self):
        for path in (SKILL / "SKILL.md", SKILL / "references/wait-for-line-runs.md"):
            with self.subTest(path=path):
                self.assertIn("line-run-discovery.md", path.read_text())

    def test_discovery_contract_has_explicit_limits_and_identity_checks(self):
        text = (SKILL / "references/line-run-discovery.md").read_text()
        for required in (
            "at most three targeted page requests",
            "including continuation",
            '--line feature-delivery --q ISL-2416 --q "shared initialization"',
            "--paged --limit 20 --sort -created_at -o json",
            "--paged --limit 100 --sort -created_at -o json",
            "Do not continue the fallback page.",
            "--cursor CURSOR --limit 20",
            "same Factory, --line, --q terms, and --sort",
            "{items, cursor, total?}",
            "first page only",
            "--total",
            "started_at", "completed_at", "stopped_at", "asked_at",
            "known run ID or direct Islo run link",
            "Known JobRun IDs",
            "authoritative parent relation",
            "does not search arbitrary run params",
            "canonical identities",
            "same artifact",
            "Origin is association evidence, not ownership",
            "instead of choosing the newest run",
            "hydrate only the selected candidate",
            "failed and stopped runs",
            "substring match is only a candidate",
            "owner/repo and number",
            "Legacy offset flags and JSON arrays remain supported",
            "lookup incomplete",
            "rather than starting a replacement",
        ):
            with self.subTest(required=required):
                self.assertIn(required, text)

    def test_published_lookup_commands_are_native_and_bounded(self):
        for path in SKILL.rglob("*.md"):
            text = path.read_text()
            with self.subTest(path=path):
                self.assertNotIn("--offset", text)
                self.assertNotIn("until a page has fewer", text)
                self.assertNotIn("until null", text)
                for command in re.findall(r"islo[^\n`]*factory line-run list[^\n`]*", text):
                    self.assertIn("--paged", command)
                    self.assertRegex(command, r"--limit (20|100)\b")

    def test_scope_and_wait_recovery_rules_remain_available(self):
        discovery = (SKILL / "references/line-run-discovery.md").read_text()
        for required in ("authorized active Factories", "`factory_id`", "Never fan out"):
            self.assertIn(required, discovery)
        waiting = (SKILL / "references/wait-for-line-runs.md").read_text()
        for required in (
            "lost start response",
            "do not start another run",
            "15 seconds, 30 seconds, 60 seconds",
            "Stop waiting at 45 minutes",
            "Keep waiting through those attempts",
            "Waiting grants no run-control permission",
        ):
            self.assertIn(required, waiting)


if __name__ == "__main__":
    unittest.main()
