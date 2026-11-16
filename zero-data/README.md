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

### Migrating history to renamed topics

When a system moves to new topics and tables, `greptime migrate-history` copies its history
from the old tables into the new ones, under the new topic, `technical_name` and column
names. Its input is a spec (JSON) listing units: one old topic in one old table, copied to
one new topic in one new table, with a column map and a wave. The SQL that runs is a file
that has been reviewed, not SQL built during the run.

```bash
# Only reads. Per wave: wave-<n>.sql, wave-<n>.plan.json and the dry-run wave-<n>.report.md.
uv run zero-data greptime migrate-history plan spec.json --host <host> \
  --boundary 2026-11-17T10:00:00Z --out migration/ [--table <old table> ...]

# After review: runs the file as it is, journalling to wave-<n>.journal.jsonl; resumable.
uv run zero-data greptime migrate-history execute migration/wave-1.sql --host <host>

# Old against new rows per unit and day, and a sample of values: wave-<n>.check.md.
uv run zero-data greptime migrate-history check migration/wave-1.sql --host <host>
```

- Rows are copied only before a unit's bound: the new topic's first row at plan time, or
  `--boundary` for a topic that has none. `execute` and `check` read the bounds from the
  manifest, so plan once; after a copy, the new topic's first row is the copied history.
- `plan` adds missing columns (`ALTER TABLE … ADD COLUMN`, typed as the old column), casts
  where no value is lost, and refuses a unit that would need a lossy cast, whose new table
  holds rows before the boundary from topics outside the spec, or whose period overlaps
  another old topic of the same new topic. Refused units are listed in the report.
- `execute` refuses a SQL file whose sha256 or host isn't the plan's, or when a column it
  touches changed since the plan. It copies one window (a unit's day) at a time, skips a
  window whose rows are all there, and stops on one that holds only part of them.
- Resume a wave from the checkout that started it, or with its journal: without it,
  `execute` refuses the columns its earlier run added.

## Release Management

### Charts

The charts are deployed by their respective pipelines. Their versions are controlled by the `version` field in `Chart.yaml`. The version of `zero-data` they deploy is based on the `appVersion`.

## Firedetection metadata

The `metadata` folder contains an SQL file for creating and filling a metadata table in Greptime DB used for firedetection data. This table is now created by hand until a method is found to automate this process.
