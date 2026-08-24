#!/usr/bin/env bash
# Sync the canonical plugin manifest to the per-platform copies.
# Canonical: plugins/islo/.claude-plugin/plugin.json
# Copies:    plugins/islo/plugin.json
#            plugins/islo/.cursor-plugin/plugin.json
#            plugins/islo/.codex-plugin/plugin.json
# Usage: sync_plugin_manifests.sh [--check]
#   --check  exit 1 if any copy differs from canonical (CI mode); no writes.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
canonical="$repo_root/plugins/islo/.claude-plugin/plugin.json"
copies=(
  "$repo_root/plugins/islo/plugin.json"
  "$repo_root/plugins/islo/.cursor-plugin/plugin.json"
  "$repo_root/plugins/islo/.codex-plugin/plugin.json"
)

[[ -f "$canonical" ]] || { echo "missing canonical manifest: $canonical" >&2; exit 1; }

mode="${1:-sync}"
status=0
for copy in "${copies[@]}"; do
  if [[ "$mode" == "--check" ]]; then
    if ! cmp -s "$canonical" "$copy"; then
      echo "DRIFT: $copy differs from $canonical" >&2
      status=1
    fi
  else
    mkdir -p "$(dirname "$copy")"
    cp "$canonical" "$copy"
    echo "synced $copy"
  fi
done

if [[ "$mode" == "--check" && $status -eq 0 ]]; then
  echo "all plugin manifest copies match canonical"
fi
exit $status
