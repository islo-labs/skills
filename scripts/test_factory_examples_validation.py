"""Check that expected missing resources do not hide other Line errors."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "plugins/islo/skills/factory-lines/scripts/validate_examples.sh"
REFERENCES = ROOT / "plugins/islo/skills/factory-lines/references"


def run_validator(mixed_errors: bool) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        scripts = root / "scripts"
        refs = root / "references"
        scripts.mkdir()
        refs.mkdir()
        shutil.copy2(SCRIPT, scripts / SCRIPT.name)
        shutil.copy2(REFERENCES / "line-manifest.md", refs / "line-manifest.md")
        shutil.copy2(REFERENCES / "create-a-line.md", refs / "create-a-line.md")
        stub = root / "islo"
        extra = 'echo "Error: malformed transition"' if mixed_errors else ":"
        stub.write_text(
            "#!/bin/sh\n"
            "if [ \"$1 $2 $3\" = \"factory line validate\" ]; then\n"
            "  if echo \"$4\" | grep -q 'create-a-line'; then\n"
            "    grep -q '{{unique_suffix}}' \"$4\" && exit 2\n"
            "    grep -q 'isolated-agent-check-validation' \"$4\" || exit 2\n"
            "    echo \"Error: Invalid request parameters\"\n"
            "    echo \"  Hint: stage 'check' references unknown Agent 'existing-agent'\"\n"
            f"    {extra}\n"
            "    exit 1\n"
            "  fi\n"
            "  echo \"Error: Invalid request parameters\"\n"
            "  echo \"  Hint: manager.agent references unknown Agent 'reviewer'\"\n"
            f"  {extra}\n"
            "  exit 1\n"
            "fi\n"
            "exit 0\n"
        )
        stub.chmod(0o755)
        env = {**os.environ, "PATH": f"{root}:{os.environ['PATH']}"}
        return subprocess.run(
            ["bash", str(scripts / SCRIPT.name)],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )


clean = run_validator(False)
assert clean.returncode == 0, clean.stdout
assert "create-a-line-1.toml (Agent schema valid" in clean.stdout
mixed = run_validator(True)
assert mixed.returncode != 0, mixed.stdout
assert "malformed transition" in mixed.stdout
print("Manager fixture diagnostics: OK")
