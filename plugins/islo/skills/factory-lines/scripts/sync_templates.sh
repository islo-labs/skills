#!/usr/bin/env bash
# Sync templates/ from the canonical islo-agents repo at a pinned ref.
# templates/ is a synced snapshot; never hand-edit it.
#
# Usage: sync_templates.sh [--check]
#   --check  exit 1 if templates/ differs from the pinned ref (CI mode); no writes.
#
# Configuration:
#   ISLO_AGENTS_REPO  git URL or local path (default: https://github.com/islo-labs/islo-agents)
#   ISLO_AGENTS_REF   ref override; defaults to the contents of templates/.pinned-ref
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_root="$(cd "$here/.." && pwd)"
templates="$skill_root/templates"
repo="${ISLO_AGENTS_REPO:-https://github.com/islo-labs/islo-agents}"

# source path in islo-agents -> template name in this skill.
# templates/.sync-map (lines of "src:dst", # comments allowed) overrides this default.
mapping=(
  "lines/feature-delivery:feature-delivery"
  "lines/bug-repro:bug-repro"
  "lines/fullstack-qa-line:qa-line"
)
if [[ -f "$templates/.sync-map" ]]; then
  mapping=()
  while IFS= read -r entry; do
    [[ -z "$entry" || "$entry" == \#* ]] && continue
    mapping+=("$entry")
  done < "$templates/.sync-map"
fi

ref="${ISLO_AGENTS_REF:-}"
if [[ -z "$ref" ]]; then
  if [[ -f "$templates/.pinned-ref" ]]; then
    ref="$(tr -d '[:space:]' < "$templates/.pinned-ref")"
  else
    echo "no pinned ref: create templates/.pinned-ref or set ISLO_AGENTS_REF" >&2
    exit 2
  fi
fi

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

git clone --quiet --no-checkout "$repo" "$work/src"
commit="$(git -C "$work/src" rev-parse --verify --quiet "$ref^{commit}" \
  || git -C "$work/src" rev-parse --verify --quiet "origin/$ref^{commit}")" \
  || { echo "ref not found in $repo: $ref" >&2; exit 1; }
git -C "$work/src" checkout --quiet "$commit"

staged="$work/templates"
mkdir -p "$staged"
echo "$ref" > "$staged/.pinned-ref"
for keep in README.md .sync-map; do
  [[ -f "$templates/$keep" ]] && cp "$templates/$keep" "$staged/$keep"
done
for pair in "${mapping[@]}"; do
  src="${pair%%:*}"; dst="${pair##*:}"
  if [[ ! -d "$work/src/$src" ]]; then
    echo "missing in islo-agents@$ref: $src" >&2
    exit 1
  fi
  cp -R "$work/src/$src" "$staged/$dst"
done

if [[ "${1:-}" == "--check" ]]; then
  if diff -r "$staged" "$templates" >/dev/null 2>&1; then
    echo "templates/ matches islo-agents@$ref"
  else
    echo "DRIFT: templates/ differs from islo-agents@$ref" >&2
    diff -r "$staged" "$templates" >&2 || true
    exit 1
  fi
else
  rm -rf "$templates"
  mv "$staged" "$templates"
  echo "synced templates/ from islo-agents@$ref"
fi
