#!/usr/bin/env bash
set -euo pipefail

# --skip-healthchecks still builds every component, so a broken VRL reference
# fails, but needs no broker or Greptime (unlike plain validate).
for config in config-*.yaml; do
  docker run -q --rm --tmpfs /vector-data \
    -v "$(pwd)/$config:/config.yaml:ro" \
    -v "$(pwd)/processing:/etc/vector:ro" \
    -e MQTT_HOST=mqtt -e MQTT_PORT=1883 -e MQTT_USER=u -e MQTT_PASSWORD=p \
    -e ATPX_MQTT_HOST=atpx -e ATPX_MQTT_PORT=1883 \
    -e GREPTIMEDB_HOST=greptimedb -e GREPTIMEDB_PORT=4000 \
    timberio/vector:0.55.0-debian validate --skip-healthchecks /config.yaml
  echo "Vector config $config is valid"
done
