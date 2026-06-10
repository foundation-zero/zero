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

With [Poetry](https://python-poetry.org/):

```bash
poetry install
```

## Configuration

Settings are read from environment variables or a `.env` file. Because settings belong to CLI subcommands, variables must be prefixed with the subcommand name using `__` as a delimiter (e.g. `RUN__MODBUS_HOST`).

```dotenv
# run subcommand
RUN__MODBUS_HOST=
RUN__MODBUS_PORT=502
RUN__MQTT_HOST=
RUN__MQTT_PORT=1883
RUN__MQTT_USERNAME=
RUN__MQTT_PASSWORD=
RUN__SEND_TOPIC=hull-temperature/temperatures
RUN__SECONDS=300
RUN__N=-1

# stub subcommand
STUB__MODBUS_HOST=localhost
STUB__MODBUS_PORT=502
STUB__MQTT_HOST=
STUB__MQTT_PORT=1883
STUB__TEMPERATURE=20.0

# read / read-skip-mqtt follow the same pattern
```

## Usage

### Running

There is no installed CLI entry point, so run the application as a Python module:

```bash
poetry run python -m zero_hull_temperature <command> [options]
```

### Commands

#### `run` — Periodic temperature publishing

Reads temperatures on a fixed interval and publishes them to an MQTT topic.

```bash
poetry run python -m zero_hull_temperature run \
  --modbus-host <host> --modbus-port 502 \
  --mqtt-host <host> --mqtt-port 1883 \
  --send-topic hull-temperature/temperatures \
  --seconds 300
```

| Option | Description | Default |
|---|---|---|
| `--send-topic` | MQTT topic to publish readings to | — |
| `--seconds` | Interval between readings | — |
| `--n` | Number of readings to take (`-1` = unlimited) | `-1` |
| `--activate-topic` | MQTT topic used to switch the relay | `marpower/450000-amcs/Command` |
| `--activate-json-path` | JSONPath within the activate topic payload | `$.KEB1_ACTIVATE_HULL_MEASUREMENT_ONOFF` |

#### `read` — Single one-shot read (with MQTT relay activation)

```bash
poetry run python -m zero_hull_temperature read \
  --modbus-host <host> --modbus-port 502 \
  --mqtt-host <host> --mqtt-port 1883
```

#### `read-skip-mqtt` — Single one-shot read (no relay activation)

```bash
poetry run python -m zero_hull_temperature read-skip-mqtt \
  --modbus-host <host> --modbus-port 502
```

#### `stub` — Run a local Modbus/MQTT stub for testing

Starts a Modbus TCP server pre-loaded with a fixed temperature value, and **subscribes** to MQTT for relay activation commands. The Modbus server only starts serving after it receives a truthy `KEB1_ACTIVATE_HULL_MEASUREMENT_ONOFF` message. Useful for integration testing without physical hardware.

```bash
poetry run python -m zero_hull_temperature stub \
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
poetry run python -m zero_hull_temperature print-schema
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

## Kubernetes / Helm

A Helm chart is included in `charts/`. Key values:

```yaml
modbus:
  host: ""
  port: 502

mqtt:
  host: ""
  port: 1883
  username: hull-temperature
  existingSecret: ""
  existingSecretPasswordKey: password

hullTemperature:
  sendTopic: "hull-temperature/temperatures"
  intervalSeconds: 300
  n: -1
  activateTopic: marpower/450000-amcs/Command
  activateJsonPath: $.KEB1_ACTIVATE_HULL_MEASUREMENT_ONOFF
```

## Development

```bash
poetry install --with test       # test dependencies only
poetry install --with dev,test   # test + linting/type-checking
poetry run pytest
poetry run ruff check
poetry run pyright
```

> Tests require a running MQTT broker on `localhost:1883`. The Modbus server is spun up in-process on port `11502`.