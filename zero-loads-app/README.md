# Zero Loads App

The Loads app does the processing as follows:
- Sensor equipment transmits sensor data via PCan UDP.
- The `adapter` module receives these messages, interprets them, and forwards the data to MQTT.
- RisingWave ingests relevant sensor data, constructs load conditions, and publishes them to MQTT.
- The `control` process consumes load conditions from MQTT, determines the load case by computing the sea state, and publishes the results to MQTT, where RisingWave sinks them into Postgres.
- When reference values are requested via the API, the current load case is retrieved from Postgres and the corresponding reference values are returned.


## Development Setup

This will setup everything needed to start any module within `zero-loads-app`.

 - Create a `.env` file using `.env.example` as a template

Install dependencies:
```bash
poetry install --with dev
```

Start the services in the root folder
```bash
cd ..
docker compose --profile zero up -d
```

Apply Hasura metadata:
```bash
cd hasura
hasura metadata apply --admin-secret myadminsecretkey
```

## Usage

### Adapter

The adapter receives PCan messages, interprets them, and forwards the data to MQTT.
```bash
poetry run loads adapter
```

The PCan stub simulates PCan messages over UDP for the adapter to ingest.
```bash
poetry run loads pcan-stub
```

### Control

The control module processes load conditions from MQTT, calculates sea state, and publishes results to MQTT.
```bash
poetry run loads control
```

The sensor stub simulates load conditions over MQTT for the control module.
```bash
poetry run loads conditions-stub
```

### API

Start the API service to expose a GraphQL API that returns reference values for a specified or current load case.
```bash
poetry run loads api
```

The sensor stub simulates load sesnors over MQTT.
```bash
poetry run loads sensor-stub
```

### Generate JWT Token

Generate a JWT token for a specific role (e.g., `captain`):
```bash
poetry run loads generate-jwt --roles captain
```

## Test Setup

Create a `.env` file using `.env.example` as a template in the root folder

```bash
docker compose --profile loads up -d
```
