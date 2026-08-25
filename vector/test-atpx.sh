#!/usr/bin/env bash
set -euo pipefail

# Vector doesn't guarantee output row order, so sort before comparing.
actual_output="$(docker run -q --rm -w /home/vector -v "$(pwd):/home/vector" timberio/vector:0.54.0-debian --config tests/atpx-config.yaml -q -q | sort)"

if ! diff -u tests/atpx-expected.json <(printf '%s' "$actual_output") >/dev/null; then
  echo "Vector output does not match tests/atpx-expected.json, got output:" >&2
  printf '%s\n' "$actual_output" >&2
  echo "" >&2
  echo "Diff:" >&2
  diff -u tests/atpx-expected.json <(printf '%s' "$actual_output") || true
  exit 1
fi

echo "Vector ATPX output matches tests/atpx-expected.json"
