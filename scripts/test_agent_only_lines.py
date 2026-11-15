"""Exercise the rejected fallback instructions from ISL-2567."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import validate_agent_only_lines as validator
from validate_agent_only_lines import violations


class AgentOnlyLinesTests(unittest.TestCase):
    def test_rejects_job_authoring_and_runtime_detours(self):
        for content in (
            "Scaffold and deploy with `islo job init`.",
            "Use an internal Job only when a required capability is unavailable.",
            "The runtime may compile an Agent stage into an internal Job.",
            '[[stages]]\nid = "release"\njob = "release-build"',
            "Internal Jobs support this behavior.",
            "Use an internal\nJob for the missing capability.",
            'job="release-build"',
        ):
            with self.subTest(content=content):
                self.assertTrue(violations(content))

    def test_allows_agent_stages_and_existing_job_maintenance_route(self):
        self.assertEqual(violations(
            '[[stages]]\nid = "release"\nagent = "release-build"\n'
            "If Agent schemas cannot express a capability, report it and stop.\n"
            "Maintain an existing Job or `job.toml` only when explicitly requested."
        ), [])

    def test_reports_source_lines(self):
        self.assertEqual(violations(
            "# Example\nUse an internal Job.\njob = 'build'\n"
        ), [2, 3])

    def test_gate_scans_every_new_line_file_and_excludes_maintenance(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in validator.NEW_LINE_FILES:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('agent = "build"\n')
            (root / "references/job-manifest.md").write_text("Existing internal Job\n")
            with patch.object(validator, "SKILL", root):
                with redirect_stdout(StringIO()):
                    self.assertEqual(validator.main(), 0)
                for name in validator.NEW_LINE_FILES:
                    with self.subTest(name=name):
                        path = root / name
                        path.write_text('job = "build"\n')
                        output = StringIO()
                        with redirect_stdout(output):
                            self.assertEqual(validator.main(), 1)
                        self.assertIn(f"{name}:1:", output.getvalue())
                        path.write_text('agent = "build"\n')


if __name__ == "__main__":
    unittest.main()
