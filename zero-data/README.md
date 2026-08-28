# Zero Data

This repository contains the Zero data platform and scripts to process IO lists supplied by various parties into the SQL needed to process the values published by those parties.

## Usage

1. Create a `.env` file based on `.env-example` in the root folder.

3. Start the services. Run in the root folder:
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
# `greptime` and `views` databases dbt needs.
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
(`tests/greptime/`) exercise both seams against a real local Greptime — no DB mocking. How
dbt-postgres drives Greptime, and the friction points, are in
[`docs/greptime-views-viability-check.md`](docs/greptime-views-viability-check.md).

## Release Management

### Charts

The charts are deployed by their respective pipelines. Their versions are controlled by the `version` field in `Chart.yaml`. The version of `zero-data` they deploy is based on the `appVersion`.

## Firedetection metadata

The `metadata` folder contains an SQL file for creating and filling a metadata table in Greptime DB used for firedetection data. This table is now created by hand until a method is found to automate this process.
