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
uv run loads at-sensors-stub
```

#### Generate JWT Token

Generate a JWT token for a specific role (e.g., `captain`):
```bash
uv run loads generate-jwt --roles captain
```

#### Seeds

The Hasura seed files `hasura/seeds/zero/loads_reference_values.sql` and
`hasura/seeds/zero/loads_case_mappings.sql` are generated from the Sailpack
load cases in `src/sailpack/load_cases` and the loads Google Sheet, which is the source of truth
for the SailPack mapping and the max loads. The SailPack targets go into `loads.reference_values`
and the lower and upper warning and alarm thresholds from the max loads tab into
`loads.thresholds`, one row per variable. The API takes each threshold from the reference
value of the matching load case, or from `loads.thresholds` where that is empty or no load
case matches, so a threshold set on a reference value overrides the variable threshold for those
conditions. Targets outside their thresholds are dropped and listed in
`src/sailpack/target_threshold_conflicts.csv`.

Regenerate the seeds, which downloads the sheet and first checks its technical names against the
registry, that every Vitters IO list row with a display name matches a registry variable on its
topic, and that the max loads are numeric and ordered:

```bash
just export_seed
```

To verify the committed seed files are still consistent with the sheet and the Sailpack
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
