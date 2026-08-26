# zero-hull-temperature

Service that reads hull temperature sensor data from a Modbus TCP device and publishes it to an MQTT broker. Designed for use on a vessel where hull temperature measurement is controlled by an AMCS relay signal.

See also: 6.17 Hull temperature measurement in AMCS FDS, and 9445016 Hull temperature sensor positions.pdf.

## Overview

The application reads temperatures from a set of hull-mounted probes via Modbus TCP holding registers. Before reading, it sends an activation command to the AMCS over MQTT (using `KEB1_ACTIVATE_HULL_MEASUREMENT_ONOFF`) to switch on the measurement relay. After reading, it publishes the results as a JSON payload to a configurable MQTT topic.

## Requirements

- Python >= 3.13.1
- A Modbus TCP server exposing the hull temperature registers
- An MQTT broker

## Installation

With [uv](https://docs.astral.sh/uv/):

```bash
uv sync --locked
```

## Configuration

Settings are read from environment variables or a `.env` file. Base settings fields
(`mqtt_host`, `mqtt_port`, `mqtt_username`, `mqtt_password`, `modbus_host`, `modbus_port`)
map to unprefixed variables (`MQTT_HOST`, `MQTT_PORT`, `MODBUS_HOST`, ...). Fields declared
on a subcommand itself (e.g. `run`'s `activate_topic`) must be prefixed with the subcommand
name using `__` as a delimiter (`RUN__ACTIVATE_TOPIC`).

For a full list of options for each subcommand, use `--help`:

```bash
uv run python -m zero_hull_temperature <command> --help
```

## Usage

### Running

There is no installed CLI entry point, so run the application as a Python module:

```bash
uv run python -m zero_hull_temperature <command> [options]
```

### Commands

#### `run` — Periodic temperature publishing

Reads temperatures on a fixed interval and publishes them to an MQTT topic.

```bash
uv run python -m zero_hull_temperature run \
  --modbus-host <host> --modbus-port 502 \
  --mqtt-host <host> --mqtt-port 1883 \
  --activate-topic marpower/450000-amcs/Command \
  --activate-json-path '$.KEB1_ACTIVATE_HULL_MEASUREMENT_ONOFF'
```

| Option | Description | Default |
|---|---|---|
| `--activate-topic` | MQTT topic used to switch the relay | `marpower/450000-amcs/Command` |
| `--activate-json-path` | JSONPath within the activate topic payload | `$.KEB1_ACTIVATE_HULL_MEASUREMENT_ONOFF` |

#### `read` — Single one-shot read (with MQTT relay activation)

```bash
uv run python -m zero_hull_temperature read \
  --modbus-host <host> --modbus-port 502 \
  --mqtt-host <host> --mqtt-port 1883
```

#### `read-skip-mqtt` — Single one-shot read (no relay activation, no MQTT)

Reads the Modbus registers once, without toggling the relay or
connecting to MQTT, and prints the resulting temperature payload to stdout.
Useful as an offline diagnostic when no MQTT broker is available.

```bash
uv run python -m zero_hull_temperature read-skip-mqtt \
  --modbus-host <host> --modbus-port 502
```

#### `stub` — Run a local Modbus/MQTT stub for testing

Starts a Modbus TCP server pre-loaded with a fixed temperature value, and **subscribes** to MQTT for relay activation commands. The Modbus server only starts serving after it receives a truthy `KEB1_ACTIVATE_HULL_MEASUREMENT_ONOFF` message. Useful for integration testing without physical hardware.

```bash
uv run python -m zero_hull_temperature stub \
  --modbus-host localhost --modbus-port 502 \
  --mqtt-host <host> --mqtt-port 1883 \
  --temperature 21.5
```

| Option | Description | Default |
|---|---|---|
| `--temperature` | Temperature value served by the stub (°C) | `20.0` |
| `--seconds` | How long to run (`-1` = indefinitely) | `-1` |

#### `print-schema` — Print the MQTT output JSON schema

```bash
uv run python -m zero_hull_temperature print-schema
```

## MQTT Output Format

Temperatures are published as a JSON object:

```
{
  "temperatures": {
    "DV1": 12.3,
    "DV2": 11.8,
    "...": "..."
  }
}
```

## Development

```bash
uv sync --locked --group test       # test dependencies only
uv sync --locked --group dev --group test   # test + linting/type-checking
uv run pytest
uv run ruff check
uv run pyright
```

> Tests require a running MQTT broker on `localhost:1883`. The Modbus server is spun up in-process on port `11502`.