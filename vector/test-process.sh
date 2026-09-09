#!/usr/bin/env bash
set -euo pipefail

actual_output="$(docker run -q --rm -w /home/vector -v "$(pwd):/home/vector" timberio/vector:0.54.0-debian --config tests/config.yaml -q -q 2>&1)"
actual_output+=$'\n'

if ! diff -u tests/process-expected.json <(printf '%s' "$actual_output" | grep -v ERROR) >/dev/null; then
  echo "Vector output does not match tests/process-expected.json, got output:" >&2
  printf '%s\n' "$actual_output" >&2
  echo "" >&2
  echo "Diff:" >&2
  diff -u tests/process-expected.json <(printf '%s' "$actual_output" | grep -v ERROR) || true
  exit 1
fi

if ! printf '%s' "$actual_output" | grep ERROR | grep "count=1" > /dev/null; then
  echo "Expecting one parsing error, found none:"
  printf '%s' "$actual_output" | grep ERROR
  exit 1
fi

echo "Vector output matches tests/process-expected.json"
