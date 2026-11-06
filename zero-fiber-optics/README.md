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
mqtt counters: connects=1 reconnects=0 enqueued=0 acked=0 publish_errors=0 publish_timeouts=0
```

`enqueued` counts packets handed to the MQTT client and `acked` counts PUBACKs
from the broker, the only counter that reflects actual delivery.

If a port stops receiving packets, the watchdog says so within 10 seconds. This
is the signal that the pipeline has stalled:

```
port 50000: no UDP packets received in the last 10s (total received 12345)
```

## Broker outages

Follows `docs/adr/0001-dependency-outages.md`; MQTT is a required dependency.

- Uses the MQTT 3.1.1 client with a clean session. rumqttc's MQTT 5 client
  flushes the socket without a timeout, so a broker that vanished without a
  TCP reset left it hung with nothing logged (bytebeamio/rumqtt#1078); the
  3.1.1 client gives up a flush after 5 s and reconnects.
- Reconnects with backoff 1 s doubling to 30 s; keepalive 15 s.
- Ready while connected, whether or not anything is being published:
  `/tmp/ready` holds one line such as
  `not ready: mqtt: Flush timeout since 13:02:05 UTC`, which the chart's exec
  readiness probe prints. A not-ready pod drops out of the UDP Service, so
  datagrams are not delivered to it during an outage.
- Exits, with the reason in `/dev/termination-log`, after 15 min not ready, or
  after 10 refusals in a row that retrying will not fix (bad credentials, not
  authorised, bad client id or protocol).

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
