# Fiber Processor Adapter

This application acts as a bridge between UDP binary streams (TProxyRxUdp protocol) and MQTT.
It reads an XML configuration file to understand the packet structure, listens on configured UDP ports, parses the incoming binary packets, and publishes the values to an MQTT broker.

## MQTT Publish Format

Each parsed UDP packet is published as a single JSON object on topic:

`<MQTT_PREFIX>/<channel>`

For example:

- topic: `fiber-optics/example-channel`
- payload: `{"packet-counter":5,"link-up":true}`

## Configuration

The application expects an XML configuration file. The default is `example/config.xml` in the current directory, or you can provide the path as the first argument.

## Environment Variables

- `MQTT_HOST`: Hostname of the MQTT broker (default: `localhost`)
- `MQTT_PORT`: Port of the MQTT broker (default: `1883`)
- `MQTT_PREFIX`: Topic prefix for all published messages (default: `telemetry`)
- `MQTT_USERNAME`: MQTT broker username (optional)
- `MQTT_PASSWORD`: MQTT broker password (optional)

Copy `.env.example` to `.env` and fill in values for local development. The application loads `.env` automatically if present.

## Logging

The log level comes from `RUST_LOG`; the Helm chart sets it from `logLevel`
(default `info`).

At startup the process logs the configuration it resolved, including the topic
each port publishes to. Check `topic=` and `expected_packet_len=` against what
consumers expect before looking anywhere else:

```
port 50000: channel 'values' mode=Receive frequency=10 variables=390 expected_packet_len=1560 topic='fiber-optics/values'
```

At `info` it also emits a counter summary every 60 seconds:

```
port 50000 counters: received=0 enqueued=0 parse_errors=0 length_mismatches=0 queue_dropped=0 publish_errors=0 publish_timeouts=0
mqtt counters: connects=1 reconnects=0 enqueued=0 acked=0 puback_denied=0 publish_errors=0 publish_timeouts=0 server_disconnects=0
```

`enqueued` counts packets handed to the MQTT client and `acked` counts PUBACKs
from the broker, the only counter that reflects actual delivery.

If a port stops receiving packets, the watchdog says so within 10 seconds. This
is the signal that the pipeline has stalled:

```
port 50000: no UDP packets received in the last 10s (total received 12345)
```

## Running

```bash
# Run with default config.xml
cargo run

# Run with specific config
cargo run -- path/to/config.xml
```

## Testing

```bash
cargo test
```
