#!/usr/bin/env bash
# Validate every TOML example in the manifest references against the installed
# islo CLI, so the skill's examples cannot rot.
#
# Blocks tagged <!-- validate: line --> run through `islo factory line validate`.
# Blocks tagged <!-- validate: agent --> run through `islo agent validate`.
# Blocks tagged <!-- validate: manager-line --> exercise the Manager contract.
# Untagged ```toml blocks get a TOML parse check only (fragments).
#
# Line examples reference Agents that do not exist in the tenant; the
# server checks those references after schema validation, so that one error is
# accepted as proof the schema passed.
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
refs="$here/../references"
files=()
for candidate in \
  "$refs/agents-and-managers.md" \
  "$refs/line-manifest.md" \
  "$refs/create-a-line.md"; do
  [[ -f "$candidate" ]] && files+=("$candidate")
done
if [[ ${#files[@]} -eq 0 ]]; then
  echo "no manifest references to validate" >&2
  exit 1
fi

command -v islo >/dev/null || { echo "islo CLI not on PATH" >&2; exit 1; }

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

extract() {
  local md="$1" base
  base="$(basename "$md" .md)"
  awk -v out="$tmp/$base" '
    /<!-- validate: line -->/  { pending = "line"; next }
    /<!-- validate: agent -->/ { pending = "agent"; next }
    /<!-- validate: manager-line -->/ { pending = "manager-line"; next }
    /^```toml/ { inblock = 1; n += 1
                 kind = pending; if (kind == "") kind = "fragment"
                 pending = ""
                 kf = out "-" n ".kind"; tf = out "-" n ".toml"
                 print kind > kf; close(kf); printf "" > tf; next }
    /^```/     { if (inblock) { inblock = 0; close(tf) }; next }
    inblock    { print >> tf }
  ' "$md"
}

for f in "${files[@]}"; do
  [[ -f "$f" ]] || { echo "missing reference: $f" >&2; exit 1; }
  extract "$f"
done

only_missing_resource() {
  local output="$1" expected="$2"
  grep -Eq "^[[:space:]]+Hint: .*${expected}.*$" <<<"$output" &&
    ! grep -Ev "^(Error: Invalid request parameters|[[:space:]]+Hint: .*${expected}.*|[[:space:]]*)$" <<<"$output"
}

fail=0
agent_count=0
prompt_agent_count=0
script_agent_count=0
decision_agent_count=0
manager_count=0
shopt -s nullglob
for kindfile in "$tmp"/*.kind; do
  toml="${kindfile%.kind}.toml"
  kind="$(cat "$kindfile")"
  name="$(basename "$toml")"
  [[ -s "$toml" ]] || { echo "FAIL $name: empty block"; fail=1; continue; }

  if ! python3 -c "import tomllib,sys; tomllib.load(open(sys.argv[1],'rb'))" "$toml" 2>"$tmp/parse.err"; then
    echo "FAIL $name: not valid TOML"; sed 's/^/  /' "$tmp/parse.err"; fail=1; continue
  fi

  case "$kind" in
    fragment)
      echo "ok   $name (parse only)" ;;
    line|manager-line)
      [[ "$kind" == "manager-line" ]] && manager_count=$((manager_count + 1))
      validation_toml="$toml"
      if grep -q '{{unique_suffix}}' "$toml"; then
        validation_toml="${toml%.toml}-validation.toml"
        sed 's/{{unique_suffix}}/validation/g' "$toml" >"$validation_toml"
      fi
      out="$(islo factory line validate "$validation_toml" 2>&1)"; rc=$?
      if [[ $rc -eq 0 ]]; then
        echo "ok   $name (line validate)"
      elif [[ "$kind" == "manager-line" ]] && only_missing_resource "$out" "references unknown Agent"; then
        echo "ok   $name (Manager schema valid; example Agent not deployed in this tenant)"
      elif [[ "$kind" == "line" ]] && only_missing_resource "$out" "references unknown Agent"; then
        echo "ok   $name (Agent schema valid; example Agent not deployed in this tenant)"
      else
        echo "FAIL $name (line validate)"; sed 's/^/  /' <<<"$out"; fail=1
      fi ;;
    agent)
      agent_count=$((agent_count + 1))
      agent_type="$(python3 -c "import tomllib,sys; print(tomllib.load(open(sys.argv[1],'rb'))['type'])" "$toml")"
      case "$agent_type" in
        prompt) prompt_agent_count=$((prompt_agent_count + 1)) ;;
        script) script_agent_count=$((script_agent_count + 1)) ;;
        decision) decision_agent_count=$((decision_agent_count + 1)) ;;
      esac
      out="$(islo agent validate "$toml" 2>&1)"; rc=$?
      if [[ $rc -eq 0 ]]; then
        echo "ok   $name (Agent validate)"
      else
        echo "FAIL $name (Agent validate)"; sed 's/^/  /' <<<"$out"; fail=1
      fi ;;
  esac
done

if [[ $prompt_agent_count -eq 0 || $script_agent_count -eq 0 || $decision_agent_count -eq 0 ]]; then
  echo "FAIL: expected prompt, script, and decision Agent fixtures (found prompt=$prompt_agent_count script=$script_agent_count decision=$decision_agent_count)" >&2
  fail=1
fi
if [[ $agent_count -eq 0 || $manager_count -eq 0 ]]; then
  echo "FAIL: expected nonzero Agent and Manager Line fixtures (found $agent_count Agent, $manager_count Manager)" >&2
  fail=1
fi
exit $fail
