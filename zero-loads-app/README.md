# Zero Loads App

This repository contains the main components of the zero-loads-app:

- The adapter ingests sensor data from CANBus and forwards it to MQTT.
- The PCanStub simulates CANBus messages over UDP for testing.
- The Control module processes sensor data, determines sea state, and publishes results to MQTT.
- The SensorStub generates mock sensor data and sends it over MQTT.
- The API exposes load reference values via a GraphQL interface.


## Development Setup

1. Create a `.env` file using `.env.example` as a template.
2. Install dependencies:
    ```bash
    poetry install --with dev,test
    ```
3. Start the application:
    ```bash
    docker compose up
    ```
4. Apply Hasura metadata:
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
poetry run loads sensor-stub
```

### API

Start the API service to expose a GraphQL API that returns reference values for a specified or current load case.
```bash
poetry run loads api
```

### Generate JWT Token

Generate a JWT token for a specific role (e.g., `captain`):
```bash
poetry run loads generate-jwt --roles captain
```
