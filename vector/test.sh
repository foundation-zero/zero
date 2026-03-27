#!/usr/bin/env bash
set -euo pipefail

actual_output="$(podman run -q --rm -w /home/vector -v "$(pwd):/home/vector" timberio/vector:0.54.0-debian --config tests/config.yaml -q -q)"

if ! diff -u tests/expected.json <(printf '%s' "$actual_output") >/dev/null; then
  echo "Vector output does not match tests/expected.json, got output:" >&2
  printf '%s\n' "$actual_output" >&2
  echo "" >&2
  echo "Diff:" >&2
  diff -u tests/expected.json <(printf '%s' "$actual_output") || true
  exit 1
fi

echo "Vector output matches tests/expected.json"
