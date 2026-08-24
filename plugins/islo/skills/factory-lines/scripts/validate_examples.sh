#!/usr/bin/env bash
# Validate every TOML example in the manifest references against the installed
# islo CLI, so the skill's examples cannot rot.
#
# Blocks tagged <!-- validate: line --> run through `islo factory line validate`.
# Blocks tagged <!-- validate: job -->  run through `islo job deploy --dry-run`.
# Untagged ```toml blocks get a TOML parse check only (fragments).
#
# Line examples reference jobs that do not exist in the tenant; the server
# checks job references after schema validation, so that one error is accepted
# as proof the schema passed.
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
refs="$here/../references"
files=()
for candidate in "$refs/line-manifest.md" "$refs/job-manifest.md"; do
  [[ -f "$candidate" ]] && files+=("$candidate")
done
if [[ ${#files[@]} -eq 0 ]]; then
  echo "no manifest references to validate" >&2
  exit 0
fi

command -v islo >/dev/null || { echo "islo CLI not on PATH" >&2; exit 1; }

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# Split every ```toml block into $tmp/<file>-<n>.toml plus a .kind file
# holding line|job|fragment from the marker comment above the fence.
extract() {
  local md="$1" base
  base="$(basename "$md" .md)"
  awk -v out="$tmp/$base" '
    /<!-- validate: line -->/  { pending = "line"; next }
    /<!-- validate: job -->/   { pending = "job"; next }
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

fail=0
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
    line)
      out="$(islo factory line validate "$toml" 2>&1)"; rc=$?
      if [[ $rc -eq 0 ]]; then
        echo "ok   $name (line validate)"
      elif grep -q "references unknown job" <<<"$out" && ! grep -qv "references unknown job" <<<"$(grep "Error" <<<"$out")"; then
        echo "ok   $name (schema valid; example jobs not deployed in this tenant)"
      else
        echo "FAIL $name (line validate)"; sed 's/^/  /' <<<"$out"; fail=1
      fi ;;
    job)
      out="$(islo job deploy --path "$toml" --dry-run 2>&1)"; rc=$?
      if [[ $rc -eq 0 ]]; then
        echo "ok   $name (job dry-run)"
      else
        echo "FAIL $name (job dry-run)"; sed 's/^/  /' <<<"$out"; fail=1
      fi ;;
  esac
done

exit $fail
