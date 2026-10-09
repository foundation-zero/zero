#!/usr/bin/env bash
set -euo pipefail

TEST_CASE=$1

if ! [ -f tests/${TEST_CASE}-config.yaml ]; then
    echo "${TEST_CASE} is not a valid argument"
    exit 1
fi

# Vector doesn't guarantee output row order, so sort before comparing.
actual_output="$(docker run -q --rm -w /home/vector -v "$(pwd):/home/vector" timberio/vector:0.55.0-debian --config tests/${TEST_CASE}-config.yaml -q -q 2>&1)" && exit_status=$? || exit_status=$? 

actual_output_without_errors=$(printf '%s' "$actual_output" | grep -v ERROR  | sort)
actual_output_without_errors+=$'\n'

actual_output_errors=$(printf '%s' "$actual_output" | grep -o "ERROR.*$") || :
actual_output_errors+=$'\n'

if ! diff -u tests/${TEST_CASE}-expected-errors.txt <(printf '%s' "$actual_output_errors") >/dev/null; then
  echo "Vector errors do not match tests/${TEST_CASE}-expected-errors.txt, got:" >&2
  printf '%s' "$actual_output" >&2
  echo "" >&2
  echo "Diff:" >&2
  diff -u tests/${TEST_CASE}-expected-errors.txt <(printf '%s' "$actual_output_errors") || true
  exit 1
fi

if [ $exit_status -ne 0 ]; then
  echo "Vector did not exit cleanly but also gave no errors"
  exit 1
fi

if ! diff -u tests/${TEST_CASE}-expected.jsonl <(printf '%s' "$actual_output_without_errors") >/dev/null; then
  echo "Vector output does not match tests/${TEST_CASE}-expected.jsonl, got output:" >&2
  printf '%s\n' "$actual_output_without_errors" >&2
  echo "" >&2
  echo "Diff:" >&2
  diff -u tests/${TEST_CASE}-expected.jsonl <(printf '%s' "$actual_output_without_errors") || true
  exit 1
fi


echo "Vector output matches tests/${TEST_CASE}-expected.jsonl"
