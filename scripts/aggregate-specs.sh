#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SPECS_DIR="$REPO_ROOT/specs"

mkdir -p "$SPECS_DIR"

echo "Generating AsyncAPI specs from all services..."

# Each service is best-effort locally (strict in CI via AGGREGATE_STRICT=1).
STRICT="${AGGREGATE_STRICT:-0}"
warnings=0

fail_or_warn() {
  local label="$1"
  echo "WARNING: failed to generate spec for $label" >&2
  warnings=$((warnings + 1))
  if [ "$STRICT" = "1" ]; then
    return 1
  fi
  return 0
}

echo "  -> termodinamica"
if ! (cd "$REPO_ROOT/zero-termodinamica" && uv run python -m zero_termodinamica print-asyncapi) > "$SPECS_DIR/termodinamica.json"; then
  fail_or_warn "termodinamica" || exit 1
fi

echo "  -> power-tags"
if ! (cd "$REPO_ROOT/zero-power-tags" && uv run python -m zero_power_tags print-asyncapi) > "$SPECS_DIR/power-tags.json"; then
  fail_or_warn "power-tags" || exit 1
fi

echo "  -> power-tags metadata"
if ! (cd "$REPO_ROOT/zero-power-tags" && uv run python -m zero_power_tags print-metadata) > "$SPECS_DIR/power-tags-metadata.json"; then
  fail_or_warn "power-tags metadata" || exit 1
fi

echo "  -> hull-temperature"
if ! (cd "$REPO_ROOT/zero-hull-temperature" && uv run python -m zero_hull_temperature print-asyncapi) > "$SPECS_DIR/hull-temperature.json"; then
  fail_or_warn "hull-temperature" || exit 1
fi

if [ "$warnings" -gt 0 ]; then
  echo "Done with $warnings warning(s). Specs in $SPECS_DIR/" >&2
  ls -la "$SPECS_DIR/" >&2
  if [ "$STRICT" = "1" ]; then
    exit 1
  fi
else
  echo "Done! Specs written to $SPECS_DIR/"
  ls -la "$SPECS_DIR/"
fi
