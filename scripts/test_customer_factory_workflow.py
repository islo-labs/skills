"""Guard the distributed Factory authoring path and its executable examples."""

import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "plugins/islo/skills"


def examples(path):
    return [
        tomllib.loads(block)
        for block in re.findall(r"```toml\n(.*?)```", path.read_text(), re.S)
    ]


class CustomerFactoryWorkflow(unittest.TestCase):
    def test_distributed_authoring_references_use_product_resources(self):
        for name in ("factory-lines", "platform", "line-manager-recovery"):
            for path in (SKILLS / name).rglob("*.md"):
                with self.subTest(path=path.relative_to(ROOT)):
                    self.assertNotRegex(
                        path.name + "\n" + path.read_text(), r"(?i)\bjobs?\b|job_"
                    )
                    for target in re.findall(
                        r"\]\(([^)#]+)(?:#[^)]*)?\)", path.read_text()
                    ):
                        if "://" not in target:
                            self.assertTrue((path.parent / target).exists(), target)

    def test_isolated_line_reuses_a_saved_agent(self):
        refs = SKILLS / "factory-lines/references"
        agents = [
            config
            for config in examples(refs / "agents-and-managers.md")
            if "type" in config
        ]
        self.assertEqual(
            {agent["type"] for agent in agents}, {"script", "decision", "prompt"}
        )
        script = next(agent for agent in agents if agent["type"] == "script")
        self.assertTrue(script["machine"])
        self.assertTrue(script["commands"])
        (line,) = examples(refs / "create-a-line.md")
        self.assertEqual(line["trigger"]["type"], "manual")
        (stage,) = line["stages"]
        self.assertEqual(stage["agent"], "existing-agent")
        stage["agent"] = script["name"]
        self.assertEqual(set(stage), {"id", "agent", "sandbox_name", "params"})
        self.assertEqual(
            [(t["from"], t["to"]) for t in line["transitions"]],
            [("trigger", stage["id"]), (stage["id"], "done")],
        )
        self.assertEqual(
            line["transitions"][0]["params"]["input"],
            {"type": "input", "name": "input"},
        )


if __name__ == "__main__":
    unittest.main()
