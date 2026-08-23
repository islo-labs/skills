#!/usr/bin/env python3
"""Validate the JSON shape of the plugin and marketplace manifests.

Plugin manifests (all 4 copies) must be plugin-shaped: name, version,
description, skills. Marketplace manifests must be marketplace-shaped:
name, plugins[] with name+source. A marketplace-shaped object in a
plugin.json path (the bug this guards against) fails loudly.
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

PLUGIN_MANIFESTS = [
    REPO / "plugins/islo/.claude-plugin/plugin.json",
    REPO / "plugins/islo/plugin.json",
    REPO / "plugins/islo/.cursor-plugin/plugin.json",
    REPO / "plugins/islo/.codex-plugin/plugin.json",
]

MARKETPLACE_MANIFESTS = [
    REPO / ".claude-plugin/marketplace.json",
    REPO / ".cursor-plugin/marketplace.json",
    REPO / ".agents/plugins/marketplace.json",
]

FORBIDDEN_PLUGIN_JSON = [
    REPO / ".claude-plugin/plugin.json",
]

errors: list[str] = []


def load(path: Path) -> dict | None:
    if not path.is_file():
        errors.append(f"missing: {path}")
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {path}: {exc}")
        return None


for path in FORBIDDEN_PLUGIN_JSON:
    if path.exists():
        errors.append(
            f"{path} must not exist: the repo root ships only marketplace.json; "
            "the plugin manifest lives at plugins/islo/.claude-plugin/plugin.json"
        )

for path in PLUGIN_MANIFESTS:
    data = load(path)
    if data is None:
        continue
    if "plugins" in data or "owner" in data:
        errors.append(f"{path} is marketplace-shaped; expected a plugin manifest")
        continue
    for field in ("name", "version", "description", "skills"):
        if field not in data:
            errors.append(f"{path} missing required field: {field}")

for path in MARKETPLACE_MANIFESTS:
    data = load(path)
    if data is None:
        continue
    if "name" not in data:
        errors.append(f"{path} missing required field: name")
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        errors.append(f"{path} missing non-empty plugins[]")
        continue
    for i, entry in enumerate(plugins):
        for field in ("name", "source"):
            if field not in entry:
                errors.append(f"{path} plugins[{i}] missing field: {field}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print(f"validated {len(PLUGIN_MANIFESTS)} plugin and {len(MARKETPLACE_MANIFESTS)} marketplace manifests")
