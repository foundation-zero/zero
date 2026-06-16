# zero-termodinamica

Service that reads termodinamica sensor data from a Modbus TCP device and publishes it to an MQTT broker. 

## Overview

The application reads modbus from a Modbus TCP adapter. After reading, it publishes the results as a JSON payload to a configurable MQTT topic.

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

For a full list of options for each subcommand, use `--help`:

```bash
poetry run python -m zero_termodinamica <command> --help
```

## Usage

### Running

There is no installed CLI entry point, so run the application as a Python module:

```bash
poetry run python -m zero_termodinamica <command> [options]
```

### Commands

#### `run` — Periodic temperature publishing

Reads temperatures on a fixed interval and publishes them to an MQTT topic.

```bash
poetry run python -m zero_termodinamica run \
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

#### `stub` — Run a local Modbus/MQTT stub for testing

Starts a Modbus TCP server pre-loaded with a fixed value. Useful for integration testing without physical hardware.

```bash
poetry run python -m zero_termodinamica stub \
  --modbus-host localhost --modbus-port 502 \
  --mqtt-host <host> --mqtt-port 1883 \
  --temperature 21.5
```

| Option | Description | Default |
|---|---|---|
| `--temperature` | Temperature value served by the stub (°C) | `20.0` |
| `--seconds` | How long to run (`-1` = indefinitely) | `-1` |


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
poetry install --with test       # test dependencies only
poetry install --with dev,test   # test + linting/type-checking
poetry run pytest
poetry run ruff check
poetry run pyright
```

> Tests require a running MQTT broker on `localhost:1883`. The Modbus server is spun up in-process on port `11502`.
