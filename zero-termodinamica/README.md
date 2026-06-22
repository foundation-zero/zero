# zero-termodinamica

Service that reads termodinamica sensor data from a Modbus TCP device and publishes it to an MQTT broker. 

## Overview

The application reads modbus from a Modbus TCP adapter. After reading, it publishes the results as a JSON payload to a configurable MQTT topic.

## Requirements

- Just
- Python >= 3.13.1
- A Modbus TCP server exposing the termodinamica sensor data
- An MQTT broker

## Installation

With [Poetry](https://python-poetry.org/):

```bash
poetry install
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
