# Zero Loads App

The Loads app processes data as follows:
- Sensor equipment transmits sensor data via PCan UDP.
- The `adapter` module receives these messages, interprets them, and forwards the data to MQTT.
- The `control` process consumes load conditions from MQTT, determines the load case by computing the sea state, and publishes the results to MQTT, where RisingWave sinks them into Postgres.
- When reference values are requested via the API, the current load case is retrieved from Postgres, and the corresponding reference values are returned.


## Usage

1. Create a `.env` file based on `.env-example` in the root folder.

2. Start the services. Run in the root folder:
   ```bash
   docker compose --profile loads up -d
   ```

## Development Setup

1. Install dependencies:
   ```bash
   uv sync --locked
   ```

2. Create a `.env` file in the root folder based on `.env-example`.

3. Start the required services. Run in the root folder:
    ```bash
    docker compose --profile zero up -d
    ```

Apply Hasura metadata manually:
```bash
cd hasura
hasura metadata apply --admin-secret myadminsecretkey
```

### Running Components

#### Adapter

Run the adapter to receive PCan messages, interpret them, and forward the data to MQTT:
```bash
uv run loads adapter
```

Run the PCan stub to simulate PCan messages over UDP:
```bash
uv run loads pcan-stub
```

#### Control

Run the control module to process load conditions from MQTT, calculate sea state, and publish results:
```bash
uv run loads control
```

Run the sensor stub to simulate load conditions over MQTT:
```bash
uv run loads conditions-stub
```

#### API

Start the API service to expose a GraphQL API for retrieving reference values:
```bash
uv run loads api
```

Run the sails sensor stub to simulate sensor data over MQTT:
```bash
uv run loads sail-system-sensors-stub
```

Run the A+T sensor stub to simulate sensor data over MQTT:
```bash
uv run loads at-stub
```

#### Generate JWT Token

Generate a JWT token for a specific role (e.g., `captain`):
```bash
uv run loads generate-jwt --roles captain
```

#### Seeds

The Hasura seed files `hasura/seeds/zero/loads_reference_values.sql` and
`hasura/seeds/zero/loads_case_mappings.sql` are generated from the Sailpack
load cases in `src/sailpack/load_cases`:

```bash
just export_seed
```

To verify the committed seed files are still consistent with the Sailpack
export (also enforced in CI):
```bash
just check_seed
```

## Testing

1. Make sure the dependencies for testing are installed
```bash
uv sync --locked
```
2. Run unit tests
```bash
uv run pytest --run=unit
```
3. Run integration tests:

Start the required services. Run in the root folder:
```bash
docker compose --profile zero up -d
```

Run the integration tests:
```bash
uv run pytest . --run=integration
```
