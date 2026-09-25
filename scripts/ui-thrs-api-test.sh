#!/bin/bash
# Run zero-ui's own THRS API integration test (the UI's queries and
# mutations, src/modules/thrsim/tests/api.integration.spec.ts) against a
# GraphQL endpoint: zero-mqtt-graphql by default, or any URL given as the
# first argument (e.g. http://localhost:5102/graphql for thrs-api).
# Needs the docker stack (broker + the API) and pnpm; run from WSL, where
# zero-ui/node_modules was installed.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

ENDPOINT="${1:-http://localhost:5103/graphql}"
shift || true

echo "Running zero-ui's THRS API test against $ENDPOINT"
cd "$REPO_ROOT/zero-ui"
VITE_THRS_API_SERVER="$ENDPOINT" \
  pnpm vitest run src/modules/thrsim/tests/api.integration.spec.ts "$@"
