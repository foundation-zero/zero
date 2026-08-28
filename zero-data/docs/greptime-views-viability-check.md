# Viability check: dbt-postgres against GreptimeDB — **GO**

The fail-fast spike from ticket 01 (and `PLAN.md` §Sequencing step 1). Verdict: **GO** —
`dbt-postgres` drives GreptimeDB v1.1.3 over the Postgres wire endpoint with a small,
contained set of macro overrides. No custom Python adapter is needed. The full path
(snapshot → local Greptime → dbt models → materialized views → tests) runs green offline.

All probes below were run against a standalone `greptime/greptimedb:v1.1.3` container over
its Postgres endpoint (`:4003`, user `app`, no password).

## What works out of the box

- **`dbt debug`** connects over the PG endpoint.
- **`SHOW CREATE TABLE`** returns replayable DDL (including `ENGINE=mito` / `WITH(...)`);
  loading it into a fresh Greptime recreates the table shape empty. Verified with a real
  prod table (`marpower__150000_propulsion__pcs_fwd` from `greptime-subzero`).
- **`information_schema.columns`** and `information_schema.tables` return usable schema info.
- **Cross-database views** work: a view in `views` can `SELECT` from a table in `public`.
- **`CREATE OR REPLACE VIEW`**, `information_schema.views`, `SHOW CREATE VIEW` all work.
- The Postgres-catalog compatibility views dbt's relation cache reads (`pg_tables`,
  `pg_namespace`, `pg_matviews`) are implemented.

## The friction points, and the contained fixes

Three friction points were predicted (`PLAN.md`); each has a small, reasonable fix.

### 1. Catalog rendering — dbt emits 3-part names; Greptime's only catalog is `greptime`

dbt-postgres always renders relations as `"<database>"."<schema>"."<identifier>"` and treats
the connection `dbname` as the leading catalog. Greptime's single catalog is `greptime`;
it rejects any other value there (`Failed to find schema`). It also refuses to accept
`greptime` as a *connection* database (`FATAL: Database not found: greptime`).

dbt-postgres additionally couples three things to one credential — the psycopg2 connection
`dbname`, dbt's relation `database`, and the leading catalog token are **all**
`credentials.database` — and enforces it with a **Python-level** guard
(`PostgresAdapter._link_cached_relations`, not macro-overridable) that rejects any relation
whose `database` differs from the connection `dbname`.

**Fix (no macro override, no Python):** create a Greptime database literally named
`greptime` and point the dbt connection at it (`dbname: greptime`). Now
`credentials.database == "greptime"`, so (a) the Python guard is satisfied — every relation's
database is `greptime` — and (b) all rendered names are `"greptime"."<db>"."<table>"`, which
Greptime accepts as `catalog.schema.table`. Fully-qualified names still target the intended
schema (`views`, `public`) regardless of which schema the session connected to. This removes
the need for any `generate_database_name` / `verify_database` overrides.

### 2. Relation caching — `pg_views` does not list views

Greptime implements `pg_tables` and `pg_namespace` but `pg_views` returns no rows, so dbt's
relation cache never sees existing views. This is harmless here because views are (re)built
with `CREATE OR REPLACE VIEW`, which is idempotent — dbt does not need the cache to decide to
drop-then-create. (`information_schema.tables` *does* report views, if ever needed.)

### 3. Transactions — unsupported, but tolerated

`BEGIN`/`COMMIT` emit `WARNING: transaction is not supported in GreptimeDB` and are otherwise
no-ops. dbt's transaction wrapping therefore needs no change.

### 4. View swap — Greptime cannot rename a view

dbt's stock `view` materialization builds a `__dbt_tmp` view then `ALTER ... RENAME`s it onto
the target. Greptime rejects renaming a view. **Fix:** one macro override
(`postgres__create_view_as` → `CREATE OR REPLACE VIEW`) plus a thin `view` materialization
that create-or-replaces the target directly, skipping the tmp+rename swap. This is the
`OR REPLACE` re-bind that `PLAN.md` anticipated.

## The complete override set (what ships in `dbt/macros/`)

- `postgres__create_view_as` → emits `CREATE OR REPLACE VIEW`.
- `materialization view, adapter='postgres'` → create-or-replace the target directly (no
  intermediate/backup/rename), keeping hooks, grants and docs behaviour.

Everything else is stock dbt-postgres. Connection config carries the rest: `dbname: greptime`
(the landing database), `schema: views` (models), sources declared with `database: greptime`,
`schema: public`.

## Proof

`dbt build` is green against a local Greptime seeded from the committed snapshot: source
tests pass, the proof view materializes into `views` via `CREATE OR REPLACE`, cross-database
resolution (`views` ← `public`) works, and the model test passes. Re-running is idempotent.
