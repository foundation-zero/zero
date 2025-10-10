# Setup

1. Create a `.env` file using `.env-example` as a template.
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
    hasura metadata apply --admin-secret adminsecretkey
    ```

## Loads

- Sensor equipment (e.g., A+T) transmits sensor data via PCan UDP.
- The adapter module receives these messages, interprets them, and forwards the data to MQTT.
- RisingWave ingests relevant sensor data, constructs load conditions, and publishes them to MQTT.
- The control process consumes load conditions from MQTT, determines the load case by computing the sea state, and publishes the results to MQTT, where RisingWave sinks them into Postgres.
- When reference values are requested via the API, the current load case is retrieved from Postgres and the corresponding reference values are returned.

### Adapter

The adapter receives PCan messages, interprets them, and forwards the data to MQTT.
```bash
poetry run loads adapter
```

The PCan stub simulates PCan messages over UDP for the adapter to ingest.
```bash
poetry run loads pcan_stub
```

### Control

The control module processes load conditions from MQTT, calculates load cases, and publishes results to MQTT.
```bash
poetry run loads control
```

The sensor stub simulates load conditions over MQTT for the control module.
```bash
poetry run loads sensor_stub
```

### API

Start the API service. This exposes a graphql API to return the reference values
```bash
poetry run loads api
```

### Generate JWT Token

Generate a JWT token for a specific role (in this case `captain`)
```bash
poetry run loads generate-jwt --roles captain
```
