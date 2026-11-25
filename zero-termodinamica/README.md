# zero-termodinamica

Service that reads termodinamica sensor data from a Modbus TCP device and publishes it to an MQTT broker. 

## Overview

The application reads modbus from a Modbus TCP adapter. After reading, it publishes the results as a JSON payload to a configurable MQTT topic. The ingest consists of two parts:
- Parsing IO list --> `scripts/io_list_to_json.py`
- Reading Modbus & publishing to mqtt --> the main application

The script produces a json file (`modbus_units.json`) that can be loaded in by the application to read specific modbus registers and bundle & publish them as json.

### Commands

The application also writes to the bridges. `termodinamica/heat-pump/set` takes
`{"power": bool, "setpoint_temperature": float}` (6..70 °C, whole degrees) and
switches the heat pump; `termodinamica/heat-pump` reads the result back. Whoever
sends it runs the external water pump, which may only stop once
`compressor_speed` reads zero.

## Requirements

- just
- Python >= 3.13.1
- uv
- An MQTT broker

## Installation

With [uv](https://docs.astral.sh/uv/):

```bash
uv sync --locked
```

## Configuration

Settings are read from environment variables or a `.env` file. 

For a full list of options for each subcommand, use `--help`:

```bash
just run --help
just run_stub --help
```

## Usage

### Running

Start MQTT Server, run the stub, and then the main application:

```bash
# Run message broker from root
docker compose --profile data-collection up -d vernemq
just run_stub
# Open new terminal
just run
```

## Development
To run all tests, linting, and type checking:
```bash
just check
```
