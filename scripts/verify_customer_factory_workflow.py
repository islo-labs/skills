"""Exercise the published skill examples through a local CLI and Factory API.

Requires a test Factory and Machine. Creates uniquely named Agent and Line
resources and removes them on exit. Does not start a run or invoke inference.
"""

import argparse
import json
import re
import subprocess
import tempfile
import tomllib
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFS = ROOT / "plugins/islo/skills/factory-lines/references"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", required=True)
    parser.add_argument("--factory", required=True)
    parser.add_argument("--machine", required=True)
    args = parser.parse_args()

    def cli(*words):
        result = subprocess.run(
            [args.cli, "--factory", args.factory, "--output", "json", *map(str, words)],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            raise RuntimeError(f"CLI {words}: {result.stderr or result.stdout}")
        return json.loads(result.stdout) if result.stdout.strip() else None

    def public(value):
        assert not re.search(r"(?i)\bjobs?\b|job_", json.dumps(value)), value

    for surface in ((), ("factory",), ("agent",), ("webhook",)):
        public(cli("schema", *surface))
    schema = cli("schema", "factory")["factory_line_toml"]
    assert schema["sections"]["stages[]"]["fields"]["agent"]["required"]
    agent = next(
        tomllib.loads(block)
        for block in re.findall(
            r"```toml\n(.*?)```", (REFS / "agents-and-managers.md").read_text(), re.S
        )
        if tomllib.loads(block).get("type") == "script"
    )
    line = tomllib.loads(
        re.findall(r"```toml\n(.*?)```", (REFS / "create-a-line.md").read_text(), re.S)[
            0
        ]
    )
    suffix = uuid.uuid4().hex[:12]
    agent["name"] = f"skill-agent-{suffix}"
    agent["machine"] = args.machine
    line["line"]["name"] = line["line"]["name"].replace("{{unique_suffix}}", suffix)
    line["stages"][0]["agent"] = agent["name"]
    public(agent)
    public(line)
    saved_agent = deployed_line = False
    try:
        with tempfile.TemporaryDirectory() as temporary:
            agent_file = Path(temporary) / "agent.json"
            agent_file.write_text(json.dumps(agent))
            line_file = Path(temporary) / "line.toml"
            source = (REFS / "create-a-line.md").read_text()
            source = re.findall(r"```toml\n(.*?)```", source, re.S)[0]
            line_file.write_text(
                source.replace("{{unique_suffix}}", suffix).replace(
                    'agent = "existing-agent"', f'agent = "{agent["name"]}"'
                )
            )
            cli("agent", "validate", agent_file)
            saved = cli("agent", "create", agent_file)
            saved_agent = True
            assert saved["name"] == agent["name"] and saved["type"] == "script"
            cli("factory", "line", "validate", line_file)
            cli("factory", "line", "deploy", line_file, "--dry-run")
            deployed = cli("factory", "line", "deploy", line_file)
            deployed_line = True
            public(deployed)
            observed = cli("factory", "line", "get", line["line"]["name"])
            public(observed)
            stages = observed["latest_version"]["manifest"]["stages"]
            assert len(stages) == 1 and stages[0]["agent"] == agent["name"], stages
            assert cli("agent", "get", agent["name"])["commands"] == agent["commands"]
            print(
                "PASS: skill Script Agent validated and saved; Agent-backed Line validated, deployed, and read without internal authoring concepts. No inference required."
            )
    finally:
        if deployed_line:
            cli("factory", "line", "rm", line["line"]["name"], "--force")
        if saved_agent:
            cli("agent", "delete", agent["name"], "--force")


if __name__ == "__main__":
    main()
