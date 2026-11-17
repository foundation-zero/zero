# Zero Data

This repository contains the Zero data platform and scripts to process IO lists supplied by various parties into the SQL needed to process the values published by those parties.

## Usage

1. Create a `.env` file based on `.env-example` in the root folder.

2. Start the services. Run in the root folder:

```bash
docker compose --profile data up -d
```

## Development Setup

1. Install dependencies:

   ```bash
   uv sync --locked
   ```

2. Create a `.env` file in the root folder based on `.env.example`.

3. Set up the GSheet service account key file from Bitwarden.

4. Start the required services. Run in the root folder:

   ```bash
   docker compose --profile zero up -d
   ```

5. Create a `.env` file in this folder based on `.env.example`.

### Running Components

Generate DBT SQL files:

```bash
uv run zero-data generate-dbt
```

Start the data mocker:

```bash
uv run zero-data generate-data
```

## Testing

1. Make sure the dependencies for testing are installed

   ```bash
   uv sync --locked
   ```

1. Run the tests

   ```bash
   uv run pytest .
   ```

## Greptime views (dbt)

`dbt/` builds stable, typed **views** over GreptimeDB's dynamically-generated raw telemetry
tables (materialized into a dedicated `views` database, leaving `public` as raw-ingest
only). Because dev and CI have no live MQTT data, a committed **snapshot** of prod's real
schema (`SHOW CREATE TABLE` → `snapshot/*.sql`) is replayed into a local Greptime so the
models can be developed and tested fully offline.

```bash
# Local GreptimeDB, from the repo root (uses the repo-root docker-compose.yml):
docker compose --profile data-collection up -d greptimedb

# From this zero-data/ directory:
# Recreate prod's table shapes (empty) locally from the committed snapshot, and create the
# `views` database dbt materializes into.
uv run zero-data greptime load

# Build the views and run the tests.
cd dbt && DBT_PROFILES_DIR="$PWD" uv run --project .. dbt build
```

Refresh the committed schema from a live tier (over Tailscale), then review the diff:

```bash
# add the table to snapshot/tables.txt first, then:
uv run zero-data greptime snapshot --host greptime-zero.tail0b4840.ts.net
git diff snapshot/
```

`GREPTIME_HOST` / `GREPTIME_PG_PORT` / `GREPTIME_USER` / `GREPTIME_PASSWORD` configure both
the tooling and dbt (defaults target the local compose instance). The integration tests
(`tests/greptime/`) exercise both seams against a real local Greptime — no DB mocking.

### Deploying the views

Deploys are manual, from a developer machine on Tailscale. Per tier (`zero`, `singel`,
`subzero`):

```bash
just dbt-deploy zero
```

This creates the `views` database if needed and runs `dbt build` (models and tests) against
that tier. Rerunning is safe: views are `CREATE OR REPLACE`d. Each build also drops and
recreates `public.power_tag_metadata` from `macros/load_power_tag_metadata.sql`.

### Device metadata

`dbt/macros/marpower_device_metadata.csv` lists the devices on the Marpower topic convention
(`marpower/<NN>-<system>/<kind>[/<instance>]`), one row per topic, with their yard tag and
functional name (`ps-aft-1`, `owners-bimini`). The instance is left out when a device is the only
one of its kind, as in `marpower/21-fire-detection/main-panel`; its technical name is then the kind.
Such a kind cannot get a second device later without moving the first one to `<kind>/<instance>`,
which changes the table Vector writes it to. The CSV is the one place functional names are kept. Each `dbt build` recreates
`public.marpower__device_metadata` from it, through the generated
`macros/load_marpower_device_metadata.sql`.

The PMS, load balance and PCS testing dashboards join the table on `topic` to label each device
`name · technical name`, or the technical name alone where no name is set. A device without a row
still shows, under its technical name, except in the PMS status, command, alarm and transformer
temperature tables: they match on the names `aft` and `fwd` exactly, so their devices need a row
with one of those names.

To add or name a device, edit the CSV, then:

```bash
just generate-device-metadata
just dbt-deploy <tier>
```

`tests/test_device_metadata.py` checks that the macro matches the CSV, that each topic is built from
its system, kind and technical name and appears once, and that names are kebab-case and unique
within a system's kind. The dbt test `assert_device_metadata_follows_the_topic_convention` checks
that each topic follows the convention, that no system has two codes, and that each kind has one
topic shape.

## Release Management

### Charts

The charts are deployed by their respective pipelines. Their versions are controlled by the `version` field in `Chart.yaml`. The version of `zero-data` they deploy is based on the `appVersion`.

## Firedetection metadata

The `metadata` folder contains an SQL file for creating and filling a metadata table in Greptime DB used for firedetection data. This table is now created by hand until a method is found to automate this process.
