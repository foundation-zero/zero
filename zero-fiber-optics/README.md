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
