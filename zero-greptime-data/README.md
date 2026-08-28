# zero-greptime-data

dbt **views** over GreptimeDB's dynamically-generated raw telemetry tables, grounded in a
committed snapshot of prod's real schema.

## Why this exists

Telemetry flows MQTT → Vector (`greptimedb_logs` sink) → GreptimeDB `public`. Vector infers
each table name from the payload and Greptime infers the columns and types from the
flattened, snakecased JSON. The result is a large, growing set of raw tables whose schemas
nobody declared. Consumers (Grafana, downstream systems) need stable, typed, documented
surfaces to build on.

We build those surfaces as dbt views with **explicit columns**, materialized into a
dedicated `views` database (leaving `public` as raw-ingest only). The catch: dbt learns a
table's schema by introspecting the live target, but dev and CI have no live MQTT data. So a
**snapshot** of prod's schema (`SHOW CREATE TABLE` → committed `.sql`) is replayed into a
local Greptime, recreating prod's table shapes (empty) for fully offline development.

## Layout

```
zero-greptime-data/
├── docker-compose.yml            # local GreptimeDB v1.1.3 (PG wire on :4003)
├── snapshot/                     # committed DDL snapshot of the curated raw tables
│   ├── tables.txt                #   the curated table list that drives the snapshot
│   └── domestic__lighting_groups.sql
├── src/zero_greptime_data/       # snapshot + load tooling (CLI)
├── dbt/                          # the dbt project
│   ├── dbt_project.yml
│   ├── profiles.yml              # local + greptime-{zero,subzero,singel} tiers
│   ├── macros/greptime_view.sql  # the Greptime-specific overrides (see docs)
│   └── models/staging/           # the proof view + source/model tests
├── tests/                        # integration tests (real local Greptime, no mocking)
└── docs/viability-check.md       # why dbt-postgres can drive Greptime, and the gotchas
```

## Local development

Prerequisites: `uv`, Docker.

```bash
cd zero-greptime-data
uv sync
docker compose up -d --wait          # start local GreptimeDB

# Recreate prod's table shapes (empty) locally from the committed snapshot.
# Also creates the `greptime` and `views` databases that dbt needs.
uv run zero-greptime-data load

# Build the views and run the tests against local Greptime.
cd dbt
DBT_PROFILES_DIR="$PWD" uv run --project .. dbt build
```

`GREPTIME_HOST` / `GREPTIME_PG_PORT` / `GREPTIME_USER` / `GREPTIME_PASSWORD` configure both
the tooling and dbt; they default to the local compose instance (`127.0.0.1:4003`, `app`, no
password).

## Refreshing the snapshot

When you need to model a field that only exists because live data created it, refresh the
committed DDL from a live tier (over Tailscale), then review the diff:

```bash
# add the table to snapshot/tables.txt first, then:
uv run zero-greptime-data snapshot --host greptime-subzero.tail0b4840.ts.net
git diff snapshot/
```

Prod schema drift (new columns, shifted inferred types) then shows up as a reviewable diff
in `snapshot/`, and — because the views list columns explicitly and have source tests — as a
failing `dbt build` rather than a silent break.

## Testing

```bash
docker compose up -d --wait
uv run pytest        # exercises two seams against a real local Greptime, no DB mocking
```

- **Seam 1** (`tests/test_snapshot.py`): a known table → the snapshot script → replayable DDL.
- **Seam 2** (`tests/test_dbt_build.py`): local Greptime seeded from the committed snapshot →
  `dbt build` green → the proof view is queryable with its explicit columns across the
  `views` → `public` boundary.

CI (`.github/workflows/ci_zero_greptime_data.yaml`) runs lint, typecheck, and these tests
against a local Greptime — entirely offline, with no live MQTT data.

## How dbt drives Greptime

There is no maintained `dbt-greptimedb` adapter, so this project uses `dbt-postgres` against
Greptime's Postgres wire endpoint with a small, contained set of overrides (a
`CREATE OR REPLACE VIEW` materialization, and a connection that lands on a database named
`greptime`). The reasoning, the friction points, and the go/no-go spike that validated the
approach are written up in [`docs/viability-check.md`](docs/viability-check.md).

## Out of scope (follow-ups)

- Deploying views to real prod (`greptime-zero`) over Tailscale — gated on prod PG credentials.
- Additional views beyond the proof view — each repeats the proof-view pattern per curated table.
- Greptime Flows / continuous aggregation, and automated snapshot refresh / deploy pipelines.
