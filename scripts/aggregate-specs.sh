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

# Drop write/command channels that zero-mqtt-graphql can't yet handle
# (it's read-only today, no GraphQL mutations):
#   - ":Handler" channels (action=receive) share their MQTT topic with a
#     sibling ":Publisher" channel -> "duplicate sanitized topic name".
#   - parametrized ".../Command" topic groups carry actuator setpoint
#     payloads (Valve/Pump/HeatPump/...) it can't resolve into fields ->
#     "no payload fields".
# Also strips any logging line(s) print-asyncapi may emit on stdout
# before the JSON body, by scanning for the first '{'.
# TODO: drop this filtering once zero-mqtt-graphql supports mutations.
filter_thrs_spec() {
  python3 -c '
import json
import sys

raw = sys.stdin.read()
idx = raw.find("{")
if idx == -1:
    sys.exit("no JSON object found in input")
doc = json.loads(raw[idx:])

channels = doc.get("channels", {})
operations = doc.get("operations", {})
messages = doc.get("components", {}).get("messages", {})


def topic_of(channel):
    return channel.get("bindings", {}).get("mqtt", {}).get("topic", "")


removed = {
    key
    for key, channel in channels.items()
    if ":Handler" in key or topic_of(channel).endswith("/Command")
}
for key in removed:
    del channels[key]
    messages.pop(f"{key}:Message", None)
    messages.pop(f"{key}:SubscribeMessage", None)

removed_refs = {f"#/channels/{key}" for key in removed}
for key in [
    k
    for k, op in operations.items()
    if op.get("channel", {}).get("$ref", "") in removed_refs
]:
    del operations[key]

json.dump(doc, sys.stdout, indent=2)
sys.stdout.write("\n")
'
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

echo "  -> thrs-control"
if ! (cd "$REPO_ROOT/zero-thrs-control" && uv run python -m thrs.cli print-asyncapi) | filter_thrs_spec > "$SPECS_DIR/thrs-control.json"; then
  fail_or_warn "thrs-control" || exit 1
fi

echo "  -> thrs-control module metadata"
# List each module's sensor (and, where present, computed) {field} topics so
# zero-mqtt-graphql can expose list queries for them (build_module_metadata).
# Same idea as power-tags' print-metadata, but per module: THRS has one {field}
# group per module, not a single flat namespace.
thrs_modules=$(cd "$REPO_ROOT/zero-thrs-control" && uv run python -c   'from thrs.spec.asyncapi import all_module_descriptions; print(" ".join(sorted(all_module_descriptions())))')
thrs_computed_modules=$(cd "$REPO_ROOT/zero-thrs-control" && uv run python -c   'from thrs.spec.asyncapi import modules_with_computed_fields; print(" ".join(modules_with_computed_fields()))')

for module in $thrs_modules; do
  echo "     - $module sensors"
  if ! (cd "$REPO_ROOT/zero-thrs-control" && uv run python -m thrs.cli print-module-metadata --module "$module" --kind sensors) > "$SPECS_DIR/thrs-$module-sensors-metadata.json"; then
    fail_or_warn "thrs-control $module sensors metadata" || exit 1
  fi
  if [[ " $thrs_computed_modules " == *" $module "* ]]; then
    echo "     - $module controller"
    if ! (cd "$REPO_ROOT/zero-thrs-control" && uv run python -m thrs.cli print-module-metadata --module "$module" --kind controller) > "$SPECS_DIR/thrs-$module-controller-metadata.json"; then
      fail_or_warn "thrs-control $module controller metadata" || exit 1
    fi
  fi
done

echo "  -> thrs-control module views"
# The nested view (modules.<module>.sensorValues) that lets the UI query
# zero-mqtt-graphql 1:1 with thrs-api (build_module_view, modules_view.rs).
for module in $thrs_modules; do
  echo "     - $module view"
  if ! (cd "$REPO_ROOT/zero-thrs-control" && uv run python -m thrs.cli print-module-view --module "$module") > "$SPECS_DIR/thrs-$module-module.json"; then
    fail_or_warn "thrs-control $module module view" || exit 1
  fi
done

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
