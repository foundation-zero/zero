# Plan: fast electrical energy dashboards (24 h and history)

Temporary: delete this file when the work is done. It records design sessions held on 2026-11-09, 2026-11-10 and 2026-11-12. Use it as the handoff for the sessions that write the design and build it.

**Status:** the requirements and most of the decisions are settled. **The architecture (path A, C, D or E below) is not chosen yet.** Read [Paths](#paths) and [Measurements](#measurements), make that choice first, then follow [Next steps](#next-steps).

The 2026-11-12 session tested three new ideas: thin dbt views without aggregation, aggregation in Grafana, and sampling instead of averaging. See [Thin views, Grafana aggregation and sampling](#thin-views-grafana-aggregation-and-sampling-tested-2026-11-12). It led to path E.

## Goal

There are two Grafana dashboards for Zero's electrical energy: consumption, production and storage.

- **Electrical energy:** the last 24 h, for the crew on board.
- **Historical energy:** 1–3 months back, for shore and engineering. Both run on the on-board GreptimeDB.

Both must stay quick, including over ranges of 1–2 months.

Files:
- Dashboards: `zero-dashboards/dashboards/Energy/electrical-energy-dashboard.json` (already Grafana v2) and `historical-energy-dashboard.json` (classic schema).
- dbt project: `zero-data/dbt` (`zero_data_greptime`).

## Why it is slow today

- **Every dbt model is a view.** staging → silver → gold are all views. Nothing is stored, and every refresh recomputes the whole chain from the raw tables.
- **The time filter can't reach the raw data.** Every gold view groups by a calculated time (`date_bin('1 minute', ts)`). Grafana filters on that calculated `time`, so the filter can't be moved down to the stored time index. Greptime reads and aggregates the whole table, then filters.
  - Measured locally: 393,120 rows from 28 files, against 4,323 rows from 1 file when the filter does reach the scan.
- **The metadata is joined before aggregating.** Silver joins each raw row to its metadata and gold aggregates afterwards.
  - Measured on Zero: `power_tags` over 7 days took **15.5 s** with join-then-aggregate and **0.36 s** with aggregate-then-join.
- **Result:** the old gold view `gld_power_tags_power_per_minute_per_main_group` takes **18.8 s for 24 h** on Zero.

**The general rule, whatever path is chosen:**
1. Filter on a *stored* time column.
2. Aggregate per topic.
3. Join context (metadata) afterwards, on the small result.
4. Never `GROUP BY` a calculated time (`date_bin`, `date_trunc`) inside a view.

`GROUP BY` on the stored time column, plus group columns, is fine. It was tested on a view over a silver table: 4,323 rows from 1 file.

## Facts about the environment

- **GreptimeDB 1.1.3** on Zero, Singel and Subzero. It runs standalone, and the local `docker-compose.yml` service `greptimedb` has the same version.
  - Raw tables are written by Vector over MQTT. They have `append_mode`, **no primary key**, **no TTL**, and time index `"timestamp"` `TIMESTAMP(9)`.
  - Every Marpower signal is stored as four columns: `__value`, `__is_valid`, `__has_value` and `__timestamp`.
- **No Flows existed on any ship** as of 2026-11-09, and there is **no `energy` schema** on any ship. The `energy.*` tables referenced in the history dashboard are stale.
- **dbt** runs dbt-postgres against Greptime's Postgres port (4003). Deploys are manual: `just dbt-deploy <tier>`. Nothing schedules dbt.
  - Metadata tables `power_tag_metadata` and `dc_24v_metadata` live in `public`. They are loaded by `on-run-start` macros.
  - `snapshot/*.sql` holds **schema only, no data**.
- **Data volume on Zero, rows per day:**

  | Table | Rows per day |
  |---|---|
  | `power_tags` | ~2.7 M |
  | battery (`marpower__450000_main_power_storage_errors`, ~1,100 columns) | ~1.8 M |
  | 24 V (`marpower__450000_24vdc_system`) | ~634 k |
  | PV converter, per table | ~83 k |
  | Aradex, per table | ~6 k |

- **Earliest raw data on Zero:**

  | Source | Earliest data |
  |---|---|
  | 24 V | 2026-04-07 |
  | Aradex FWD / AFT | 2026-05-21 / 2026-06-04 |
  | battery | 2026-08-19 |
  | busbar (solar until 2026-11-05 06:07 UTC) | 2026-09-04 |
  | `power_tags` | 2026-09-11 |
  | PV converter tables | 2026-11-05 |

- **Subzero is not usable as a test bed.** It only has battery data, and some tables are missing.
- **Units and signs:**
  - `power_tags.active_power_total` is in W.
  - 24 V power is `output_current × converter voltage / 1000`, in W.
  - **Aradex `power__value` is in 0.1 kW**, so `× 100` gives W. Positive is propulsion, negative is hydrogeneration. Source: "52422003 Modbus RTU interface PMS PCS R1.6 AFT/FWD", register `Ara1Power`: int16, 0.1 kW, "DC power, calculated with DC V and A x10". Zero's data peaks at 1904, which is 190 kW.
  - Solar is `-hvdc_power`, clipped at 0.
  - Energy is computed from power: the average per minute, summed, divided by 60.
- **The battery `energy_counter_{1,2,3}` fields aren't usable.** They are signed int32 values read as uint32 (for example 4294943118 = −24178), and they go up and down with charge and discharge. They're excluded.
- **Shore power** has no source yet. The dashboards have Shore slots that are always 0 or NULL. Shore is scheduled to be added soon.
- **The 7-day result showed production ≈ 0 kWh per day.** Solar and hydrogeneration were near zero, while consumption was 110–750 kWh per day. Check the solar sign and validity filters during the build.

### GreptimeDB 1.1.3 Flows: what works

Tested locally on 2026-11-09. Note that the online docs describe 1.3, which differs.

| Works | Doesn't work or watch out |
|---|---|
| A single-table aggregate (`date_bin` + `GROUP BY`) into a sink table | **A view as the source:** the Flow is created but never writes anything. |
| Conditional aggregates (`sum(CASE WHEN p>0 ...)`) | **JOIN or UNION in a Flow:** only works as a full recompute with `EVAL INTERVAL`, rereading all history every interval. Unusable. |
| WHERE filters on validity, NOT NULL and thresholds | **Existing data is not processed** by a new Flow. Backfill with `INSERT INTO sink SELECT ...`, which can run next to the Flow without problems. |
| Chaining: a 1 h Flow reading a 1 m sink table | **Unqualified source names** are looked up in the sink's database. Always write `public.x`. |
| Late data updates the row in place (sink primary key + time index) | **A sink in `append_mode` duplicates rows on every recompute.** Never use append mode for a sink. |
| `CREATE FLOW IF NOT EXISTS`, `CREATE OR REPLACE FLOW`, `DROP FLOW` | `OR REPLACE` doesn't reprocess history or change the sink's schema. |
| Latency of about 5 s with `EVAL INTERVAL '5 seconds'`. Without it, ~50–60 s for 1 m, up to 10 min for 1 h. | **Errors appear only in the server log.** `information_schema.flows` doesn't show failures, and there is no `flow_statistics` in 1.1.3. |
| | Several Flows writing into one sink table is **untested** (expected to work when topics don't overlap). |
| | `date_bin(...) AS ts` with `GROUP BY ts` is ambiguous when a source column is also `ts`. Use another alias. |

Recommended DDL pattern. The sink is pre-created, has a primary key and is not in append mode. It stores sum and count, so hourly values can be combined exactly:

```sql
CREATE TABLE rollups.slv_aradex_1m (
  topic STRING, time_window TIMESTAMP(9) NOT NULL,
  p_sum DOUBLE, p_min DOUBLE, p_max DOUBLE, n BIGINT,
  pos_sum DOUBLE, pos_min DOUBLE, pos_max DOUBLE, n_pos BIGINT,
  neg_sum DOUBLE, neg_min DOUBLE, neg_max DOUBLE, n_neg BIGINT,
  update_at TIMESTAMP(3),
  TIME INDEX (time_window), PRIMARY KEY (topic)
);
CREATE FLOW IF NOT EXISTS slv_aradex_1m__pcs_aft_ara1
SINK TO rollups.slv_aradex_1m
EVAL INTERVAL '15 seconds'
AS SELECT topic, date_bin('1 minute'::INTERVAL, "timestamp") AS time_window,
  sum(power__value), min(power__value), max(power__value), count(power__value),
  sum(CASE WHEN power__value > 0 THEN power__value END), min(CASE WHEN power__value > 0 THEN power__value END),
  max(CASE WHEN power__value > 0 THEN power__value END), count(CASE WHEN power__value > 0 THEN 1 END),
  sum(CASE WHEN power__value < 0 THEN power__value END), min(CASE WHEN power__value < 0 THEN power__value END),
  max(CASE WHEN power__value < 0 THEN power__value END), count(CASE WHEN power__value < 0 THEN 1 END)
FROM public.marpower__150000_propulsion__pcs_aft_ara1
WHERE power__is_valid AND power__has_value AND topic IS NOT NULL
GROUP BY topic, time_window;
-- The hourly Flow reads rollups.slv_aradex_1m: sum of sums, min of mins, max of maxes, sum of counts.
```

### GreptimeDB 1.1.3 Range Queries: not an alternative to rollups

Tested locally on 2026-11-11, to see whether Range Queries (`avg(x) RANGE '1m' ... ALIGN '1m' BY (topic)`) could replace Flows. Test bed: a `power_tags` copy with 14 days of synthetic data (1.2 M rows, 10 topics, one sample every 10 s, 5 files). Pushdown was read from the raw scan node in `EXPLAIN ANALYZE`. A full scan is 1.2 M rows and 5 files; 24 h with the filter pushed down is ~84 k rows and 1 file.

**Conclusion:** Range Queries are query syntax only. They read the same raw rows as `date_bin` + `GROUP BY`, so they don't change the 30–60 day numbers in [Measurements](#measurements). History still needs stored rollups.

| Works | Doesn't work or watch out |
|---|---|
| Time filter pushed down when the `WHERE` is **inside** the Range Query: `now() - interval`, and Grafana-style `BETWEEN` literals | **A view containing a Range Query:** `CREATE VIEW` fails ("Serialize logical plan for RangeSelect" not implemented). So no thin views with Range Queries. |
| A Range Query in a CTE with the filter inside, then joined to metadata (aggregate then join) | **A Range Query reading from a view**, even a plain one, fails ("Unknown table type, downcast failed"). |
| A Range Query reading from a subquery, or from a `UNION ALL` of raw tables, with the filter in each part | **The filter outside the Range Query** (a subquery or CTE filtered on its output time, or after a join) is **not** pushed down: a full scan, as with today's gold views. |
| A `UNION ALL` of several Range Queries, each with its own filter | Same rows read as `date_bin`; on 7 days hourly it was slightly slower locally (30 ms vs 15 ms). |
| `FILL LINEAR`, `ALIGN '1h' TO NOW`, any `ALIGN` size (`$__interval`-style) | |
| Conditional aggregates: `sum(CASE WHEN p > 0 ...) RANGE '1m'` | |
| Sliding windows: `avg(x) RANGE '5m' ALIGN '1m'` gives a 5-minute rolling average in one query | |

**Where they can help:** inline 24 h queries on raw data (paths C and D). For example the flow canvas's 5-minute rolling average, or gap-filled 1-minute buckets. Every panel then carries the full SQL with `$__timeFilter("timestamp")` inside each Range Query and each union part, because views can't hold them.

### Thin views, Grafana aggregation and sampling (tested 2026-11-12)

Three ideas were tested. Local tests used Greptime 1.1.3 with synthetic `power_tags` data: 10 topics, one sample every 4 s, 3–7 days in separate files. Pushdown was read from the raw scan node in `EXPLAIN ANALYZE`. The Zero measurements are read-only and inline (the SQL a thin view would expand to), one query at a time, with `/health` checked between runs.

**Publish rates on Zero (samples per topic per minute):** battery, PV converters and ESI 60; DC switches ~36; `power_tags` 15; 24 V 4; Aradex ~3. Aradex is published on change, but still has a sample in ~98 % of minutes.

#### 1. Thin dbt views without aggregation: the filter reaches the raw scan

Views that only rename, filter, derive columns and join metadata keep Grafana's time filter at the raw time index. The dbt structure (staging → silver → gold) can stay; only the `date_bin` + `GROUP BY` moves out of the views into the panel SQL. Greptime still does the aggregation.

| View shape (local, 24 h of 7 days selected) | Raw rows read |
|---|---|
| Today's gold view: `date_bin` + `GROUP BY` inside the view | 1,512,000 (all 7 days, 4 files) |
| Thin view; the panel aggregates | 216,000 (1 file) |
| Thin view with the metadata join inside it | 216,000 |
| `UNION ALL` of two sources with derived columns (`× 100`, `greatest(-x, 0)`) | 216,000 per source |
| A sampling view (`first_value` or `row_number()` per minute inside the view) | 1,512,000: blocked, like today's gold views |

Two conditions:
- **Aggregate per topic first, then join metadata, in the panel.** On Zero, `power_tags` 24 h took 0.66 s that way and 2.4 s with the row-level join from the view. Group power is the *sum* of per-topic averages anyway, so the panel needs the two-step query regardless.
- **Logic that needs a shared time bucket can't be row level.** 24 V current × voltage come from different samples and must be aligned per bucket in the panel query (or in a rollup).

Cost still grows with the selected range, because every query reads all raw rows in it (Zero, aggregate then join):

| Query | 24 h | 7 d | 30 d |
|---|---|---|---|
| `power_tags` per topic, then metadata | 0.58–0.66 s | 1.0–2.0 s | 2.6–3.6 s |
| Battery per topic per minute | 0.5–0.7 s | 3.6–4.1 s | ~25 s (2026-11-10) |

#### 2. Aggregation in Grafana: ruled out

- **Transfer:** raw `power_tags` over Greptime's HTTP API, which the Grafana plugin uses, took 2 s for 10 min (19,377 rows, 1.3 MB), 14 s for 1 h (116,488 rows, 8 MB) and 96 s for 6 h (688,835 rows, 48 MB). 24 h is ~2.7 M rows for `power_tags` alone.
- **Grafana 13 limits (docs):** SQL expressions run on the Grafana server and fail above `sql_expression_cell_limit` = 100,000 input cells (rows × columns) or after `sql_expression_timeout` = 10 s. SQL data sources are capped at `[dataproxy] row_limit` = 1,000,000 rows. Transformations have no documented limits or execution location.
- **Use Grafana only for the last step:** reshaping a few thousand rows that Greptime already aggregated, as the panels do now.

#### 3. Sampling (value at the start of each minute instead of the average): accurate, but no faster

- **Accuracy (Zero, 8 days, per day):** `power_tags` energy from the first sample per minute differs from the minute average by 0.05–1.5 %, mostly ~0.3 %. Battery charge and discharge differ by under 1 %.
- **Speed: no gain.** The database can't jump to the first sample of each minute: it reads every row in the range, then picks one. Locally `first_value`, `last_value`, `row_number() = 1`, a filter on the first 4 s of each minute, and a Range Query with `last_value` all read exactly as many rows as `avg()`. On Zero, 30 days took 3.1–3.6 s with `first_value` and 2.6–3.1 s with `avg`. (An earlier run that looked 2× faster was the file cache.)
- **In a view it is harmful:** the minute bucket has to be inside the view, which blocks the time filter (table above).
- Sampling only saves work if fewer rows are *stored*: at ingest (out of scope) or as rollup content, where it is no cheaper than an average.

#### 4. `INSERT INTO … SELECT` from a view works: rollups without Flows

Tested locally to see whether thin views can feed rollup tables (open decision 3). Flows can't read views; `INSERT … SELECT` can.

| Test | Result |
|---|---|
| Source: gold view on a silver view, with the metadata join | Works: 240 rows (10 topics × 24 h), exactly one day of samples |
| Time filter at the raw scan | Yes. The SELECT part reads only the window (1 file); runtime scales with it: 33 ms for 2 h, 50 ms for 1 day, 110 ms for 3 days. `EXPLAIN ANALYZE` of an INSERT isn't supported ("Insert into not implemented"), so this is checked via the SELECT and the timings. |
| Rerun the same INSERT | Upserts on primary key + time index: 240 rows after 3 runs, no duplicates |
| Late data | Picked up by the next run: the 10:00 hour went from 900 to 1,000 samples |
| Source: `UNION ALL` gold view (`power_tags` + Aradex split into Propulsion and Hydrogeneration) | Works; the filter reaches each part, old files are pruned |
| Filter relative to `now()`, as a scheduled job uses | Works |

Cost on Zero of the SELECT part of a run over the last 2 h (read-only): `power_tags` with metadata per hour or per minute 0.53 s; battery per minute 0.43 s.

Sink pattern used (as for Flows: primary key, not append mode):

```sql
CREATE TABLE rollups.electrical_1h (
  topic STRING, src STRING, main_group STRING,
  time_window TIMESTAMP(9) TIME INDEX,
  p_sum DOUBLE, n BIGINT, update_at TIMESTAMP(3),
  PRIMARY KEY (topic, src, main_group)
);
INSERT INTO rollups.electrical_1h (topic, src, main_group, time_window, p_sum, n, update_at)
SELECT topic, src, main_group, date_bin('1 hour'::INTERVAL, ts) AS tw, sum(power), count(power), now()
FROM views.gld_electrical
WHERE ts >= now() - INTERVAL '2 hours'
GROUP BY topic, src, main_group, tw;
```

Watch out: `source` is a reserved word in Greptime (quote it or use another name), and `Int64 * INTERVAL` isn't supported, so generate test timestamps outside SQL.

## Measurements

All times are server time (`execution_time_ms`). The Zero measurements were taken on 2026-11-10, while Zero was healthy.

| Query | Time |
|---|---|
| Old gold view, `power_tags`, 24 h | **18.8 s** |
| Raw `power_tags`, aggregate then join: 24 h / 7 d / 30 d | 0.08–0.46 s / 0.75 s / 2.1 s |
| Raw battery: 24 h per minute / 7 d / 30 d | 1.1 s / 5.7 s / **25 s** |
| **A full D-style panel** (daily production and consumption; `power_tags` + 24 V current×voltage + 4 Aradex + 3 PV + busbar), aggregate then join: 1 d / 7 d / 30 d / 60 d | **0.28 s / 2.2 s / 4.9 s / 16.9 s** |
| The same panel with join then aggregate: 1 d / 7 d / 30 d | 3.1 s / 24 s / >60 s |
| Rollup tables, locally, 24 h through gold views (3 months of synthetic 1 m data) | ~15 ms; 1 of 13+ files read |
| Raw `power_tags`, aggregate then join, Zero 2026-11-12: 24 h / 7 d / 30 d | 0.58–0.66 s / 1.0–2.0 s / 2.6–3.6 s |
| Raw `power_tags` 24 h, row-level metadata join then aggregate (as through a thin view with the join) | 2.4 s |
| Raw battery per minute, Zero 2026-11-12: 24 h / 7 d | 0.5–0.7 s / 3.6–4.1 s |
| Sampling (`first_value` per minute) instead of `avg`, `power_tags` 30 d | 3.1–3.6 s vs 2.6–3.1 s: no gain |
| Raw rows to Grafana over the HTTP API, `power_tags` 1 h / 6 h | 14 s / 96 s |
| SELECT part of a scheduled rollup run over 2 h: `power_tags` / battery | 0.53 s / 0.43 s |

Grafana's `$__interval` (bucket size calculated from the range) reduces the rows **returned**, not the rows **read**. Raw-query cost is driven by the range × the raw sample rate.

Range Queries have the same limit: with the filter pushed down they read exactly as many rows as `date_bin` (7 d locally: 602,000 rows and 3 files for both). See [Range Queries](#greptimedb-113-range-queries-not-an-alternative-to-rollups).

## Requirements and decisions

These hold whichever path is chosen, unless the path says otherwise.

### Users, freshness and resolution
- The 24 h dashboard is for the **crew**. The history dashboard is for **shore and engineering**.
- **Everything runs on the on-board GreptimeDB.** No shore replication.
- The history dashboard may lag by up to about an hour. The 24 h panels may lag **1–2 min**.
- The **flow canvas must be as real-time as possible** and keeps its **5-minute rolling average**. In path A it may read the `_1m` tables, about 15–30 s behind, which is accepted.
- **Resolution:**
  - 24 h: about 1 min for power and energy bars.
  - History: hourly and daily.
  - Stored time buckets: **1 minute and 1 hour only**.
- **Energy accuracy:** integrating power is fine, to a few percent. Counters aren't needed.
- **Data retention and storage are out of scope.** Raw tables, Vector and the ingest schema stay unchanged.

### dbt
- **dbt is not a hard requirement, but stays** as the deploy tool, the metadata loader and CI.
- **The staging layer is dropped.**
  - Flows can't read views, so staging would only duplicate logic.
  - Source column docs and tests move to `sources.yml`.
  - Renames, validity rules and the ≥ 18 V rule move to **macros** used by silver.
- **Silver** is per topic and per minute, with no metadata. It stays close to the source: **raw units, raw signs, no scaling, no sign flips.**
  - Stored per bucket: `sum`, `min`, `max`, `count`, and the same four columns for the **positive and negative parts, split per sample**: Aradex propulsion vs hydrogeneration, battery charge vs discharge.
  - Averages are presented in gold as `sum / count`.
- **Invalid records are dropped:**
  - `topic IS NULL`
  - `__is_valid` or `__has_value` false
  - 24 V voltage < 18 V
- **Battery fields:**
  - soc, soh, energy, num_connected_strings and charge_power
  - battery_power, split into charge and discharge
  - **Excluded:** the energy counters and the charging/discharging flags.
- **Gold adds context:**
  - metadata (main_group, sub_group, consumer)
  - Aradex `× 100`
  - the solar sign
  - 24 V current × voltage
  - labels
- Gold may use `GROUP BY` **only on the stored time column**. **No `ORDER BY`** in views.
- **Gold views** (path A):
  - per topic: `gld_electrical_1m` / `_1h`, all sources in one shape: `time, source, main_group, sub_group, consumer, production_kw, consumption_kw, samples`;
  - `gld_electrical_main_group_*` and `gld_electrical_sub_group_*`, grouped on the stored `time_window`;
  - `gld_battery_1m` / `_1h`;
  - the per-domain views stay for detail.
- New objects go in a **`rollups` database**. New gold names must not clash with the old `gld_*` during the overlap; use a `_1m` / `_1h` suffix.
- **Tests:**
  - On the fields used in each silver `WHERE` filter: topic not null, the validity flags, and 24 V ≥ 18 V.
  - On silver: not-null keys and freshness.
  - Source tests are limited to recent data with a `where:` config, so they don't scan months of raw rows.
- **The old `gld_*` views are dropped after the switch-over.** `slv_power_tags` is used by `zero-data/notebooks/energy_report.py`, so point that notebook at the new silver or gold first.

### Flows (paths A and C)
- **One Flow per source table.** Several Flows may write into one silver table:
  - Aradex: 4 Flows into one table.
  - PV: 3 Flows into one table.
  - Busbar: no Flow, only backfill for the period before 2026-11-05 06:07.
- `_1h` tables are filled by a Flow reading the `_1m` table.
- **`EVAL INTERVAL`:** 15 s for `_1m`, 5 min for `_1h`.
- **Deploy:** with the existing `just dbt-deploy <tier>`, using a new dbt **`flow` materialization** next to `greptime_view`.
  - It creates the sink table and runs `CREATE FLOW IF NOT EXISTS` / `OR REPLACE`.
  - A `sources=[...]` config creates one Flow per source table from the same model SQL.

### Backfill (paths A and C)
- A CLI command: `uv run zero-data rollups backfill --host <tier>`. It runs the same compiled SELECT as each Flow as `INSERT INTO … SELECT`.
- It takes **all available data**, not just 3 months, oldest first, **one source table × one day per chunk**.
- **Throttling:**
  - Pause at least 2 s, or the previous chunk's duration, whichever is longer.
  - Double the pause when a chunk takes more than 30 s.
  - Stop when a chunk takes more than 2 min.
  - Resumable with `--from <date>`. Optional `--window 22:00-06:00`.
- It can safely run again, because rows upsert on topic + time. It must be re-run after any silver logic change.

### Dashboards
- **Keep two separate dashboards.** Migrate both to the **Grafana v2 schema**. **Don't** apply the Trends/Live tab pattern from the commissioning migration.
- **Electrical energy** (default 24 h, refresh **30 s**). Keep the current design:
  - **Flow canvas:** 5-minute rolling average. Query A gives power per main group, query B the battery: energy, energy-weighted SoC, charge and discharge.
  - **Treemap:** average energy consumption over the selected range.
  - **Timeseries:** hourly bars, production above zero and consumption below, over the selected range.
  - **New: freshness stat** "x seconds ago" (Grafana unit "From Now"). In path A it's based on `max(update_at)` of the silver tables.
- **Historical energy** (refresh 5 min). Keep the current design:
  - **Main graph:** battery SoC with daily production and consumption bars over it.
  - **Treemap**, similar to the 24 h dashboard.
  - **Timeseries** of production and consumption per day.
  - **Freshness stat.**
  - **SoC details:**
    - The measured SoC shows the last **`$lookback_days`** days: a dashboard variable, default **20**.
    - **"SoC calculated":** the measured SoC trend over that look-back window, extended **7 days** into the future.
    - **"SoC prediction":** current SoC minus **`$daily_consumption`** × days, for 7 days. `$daily_consumption` is a **textbox, hotel load in kWh/day, default 20**, which the user can change.
    - SoC % uses **`$max_soc` = 300 kWh, the fixed theoretical capacity**. Keep it a constant.
    - The `$min_soc` threshold line stays.
    - The broken `$start_date` variable ("1 Jan 1970", wrong `date_format`) isn't needed any more.
  - **The "future" part moves to a separate visualization** that isn't affected by the time range:
    - a **Trend panel** with "days ahead" 0–7 on the x-axis, showing the prediction and calculated lines;
    - a **stat**: "Days until SoC < `$min_soc`".

    The SoC history panel then shows only measured data. Fallback, accepted for now: a dashboard range of `now-20d` → `now+7d`.
  - **The old `energy.*` queries stay hidden** (`hide: true`) as reference logic until they're rewritten onto the new tables:
    - SoC prediction and SoC calculated, which read `energy.electrical_soc_hourly`;
    - net daily, which reads `energy.electrical_hourly`;
    - the `daily_consumption` variable, which reads `energy.energy_metrics`.
- The Shore slots stay in the queries. Shore is a follow-up.

### Testing and rollout
- **Test locally first, as much as possible,** using the dbt snapshots (schema only), then **finally on Zero with real data**.
  - Copying ~2 days of real Zero data into the local Greptime is allowed: read-only, throttled, hourly chunks, only the needed columns, nothing committed.
- **Rollout:**
  1. **Local build:** compare minute by minute with the old views on the same data.
  2. **Local dashboards:** compare panel by panel.
  3. **PR 1 (zero-data):** new layers, materialization, backfill CLI and tests. The old models stay.
  4. **On Zero:** deploy, backfill, then check freshness and numbers.
  5. **PR 2 (zero-dashboards):** v2 dashboards next to the old ones with temporary uids and titles ("… (v2)"). Compare them for a few days.
  6. **PR 3:** the v2 dashboards take over the original uids and titles; the old dashboards are removed.
  7. **PR 4:** remove the old `stg_*` and `gld_*` models.

  Steps 6 and 7 need sign-off. The dashboard side may change with the chosen path.
- **When testing on Zero:** run heavy queries one at a time, check `/health` between runs, and stop above ~30–60 s.

## Paths

### A: rollups everywhere (Flows → silver tables → gold views)

**What it is:**
- Silver is filled by Flows from the raw tables, at 1 m and 1 h, per topic.
- Gold is thin views over silver.
- Both dashboards read gold. The flow canvas reads the `_1m` tables.
- Everything in the Flows, Backfill, dbt and Dashboards sections applies in full.

**Pros:**
- Constant cost whatever the range, history length or number of viewers: milliseconds.
- History can outlive raw retention.
- **One logic path** feeds both dashboards.
- Solves the battery history problem.

**Cons:**
- The most machinery: the `flow` materialization, about 9 + 9 Flows, about 12 sink tables, the backfill CLI and freshness monitoring.
- 1.1.3 Flows are young:
  - errors are silent;
  - no joins or unions;
  - changes don't reprocess history, so re-run the backfill;
  - behaviour depends on the Greptime version.
- A lag of about 15–30 s (1 m) and up to about 5 min (1 h).
- Continuous background load, though small.
- Rollup storage grows indefinitely (no TTL).
- `dbt-deploy` now changes data, not just definitions.
- Anything finer than 1 minute has to come from raw.

**Recommendation from the session:** A, because the measurements rule out D for history, and A has one logic path.

### C: hybrid (raw for 24 h, rollups for history)

**What it is:**
- The 24 h dashboard queries the raw tables through thin views, or inline SQL, with the rule *filter on raw time → aggregate per topic → join metadata*.
- The history dashboard reads `_1h` rollups: Flows straight from raw, plus backfill.

**Pros:**
- The 24 h data is **real time**, measured at 0.28 s for a full 24 h panel.
- Fewer rollup tables: hourly only.
- History stays fast.

**Cons:**
- **Two code paths compute the same energy numbers.** The 24 h and history dashboards can disagree, and fixes have to be made twice.
- It still needs the Flow machinery and backfill.
- The 24 h query cost grows with the number of viewers and refreshes on the ingesting box.

**When to choose it:** if real-time 24 h curves matter more to the crew than having one source of truth.

**Range Queries** fit the raw 24 h side, such as the canvas's 5-minute rolling average with `RANGE '5m' ALIGN '1m'`, but only as inline SQL in the panels. 1.1.3 views can't contain them.

### D: raw + thin views + `$__interval`, with a rollup only for the battery

**What it is:**
- All panels query the raw tables (aggregate per topic, then join).
- Grafana's `$__interval` sets the bucket size.
- One Flow plus backfill for the battery table only.

**Pros:**
- Real time.
- Almost no new machinery.
- One logic path.
- Fixing a formula fixes all history straight away.
- A small-scale way to learn Flows.

**Cons:**
- **Doesn't meet "smooth for 1–2 months":** a full energy panel takes 4.9 s for 30 days and **16.9 s for 60 days**, and cost rises faster than linearly as older sources come in.
- The battery panel without its rollup would take 25 s or more for 30 days.
- Cost grows with history length, refreshes, panels and viewers, on the box that ingests.
- The dashboard-level SQL is complex (the 24 V join, the split, the unions).

**When to choose it:** only if history is limited to about 30 days.

(B, raw only, is D without the battery rollup. It's ruled out by the battery numbers.)

Range Queries don't rescue D: they read the same raw rows, and they can't be put in views. See [Range Queries](#greptimedb-113-range-queries-not-an-alternative-to-rollups).

**D can keep the dbt structure:** thin views without aggregation keep the time filter at the raw scan, so the panels can query views instead of raw tables, and the SQL in the panels gets simpler. This doesn't change D's cost. See [Thin views](#thin-views-grafana-aggregation-and-sampling-tested-2026-11-12).

### E: thin dbt views for everything, rollups by scheduled `INSERT … SELECT`

Added 2026-11-12. Combines D's thin views with A's stored history, without Flows.

**What it is:**
- The dbt structure stays: staging → silver → gold, but **all views are thin**: rename, validity filters, derived columns (`× 100`, sign), metadata join, `UNION ALL` of sources. **No `date_bin` / `GROUP BY` in any view.**
- The **24 h dashboard** queries the gold views directly. The panel SQL aggregates per topic and bucket with `$__timeFilter`, then sums per group. Live, real time.
- The **history dashboard** reads `_1h` rollup tables (and `_1m` if needed), filled by a **scheduled `INSERT INTO rollup SELECT … FROM <gold view> WHERE ts >= now() - INTERVAL '2 hours' GROUP BY topic, …, bucket`**, for example every 5 min. The **backfill** is the same statement over older windows.
- Logic that needs a shared bucket (24 V current × voltage) is done in the panel query and in the rollup SELECT, from the same view.
- The staging layer can stay. The decision to drop it (see [dbt](#dbt)) was made because Flows can't read views, which doesn't apply here. The silver rules (raw units, validity filters, no metadata) still hold, but as row-level views instead of per-minute tables.

**Pros:**
- **One logic path:** the same views feed the live panels and the rollups. A fix in a view applies to both (history after re-running the backfill).
- History is fast and constant cost, as in A. Solves the battery history problem.
- **No Flows:** no silent errors, no `flow` materialization, no ~18 Flows, no Flow limits (views, joins and unions are all allowed as source).
- Late data and reruns are safe (upsert on primary key + time). Tested locally.
- The rollup cost per run is small (0.4–0.5 s per source for 2 h on Zero).
- The 24 h dashboard stays real time.

**Cons:**
- **Needs a scheduler**, which doesn't exist yet. Candidate: a Kubernetes CronJob running a `zero-data` CLI command (`rollups refresh`), next to the planned `rollups backfill`. Not tested.
- Freshness monitoring is needed (the `update_at` column; a freshness stat in the dashboards).
- History lags by one schedule interval plus the run time.
- The 24 h panels cost grows with viewers and refreshes, as in C and D (0.6 s per source for 24 h).
- The panel SQL carries the two-step aggregation (per topic, then per group).
- `dbt-deploy` only changes definitions; the rollup tables need their own creation (dbt `table` materialization with a pre-created sink, or the CLI).
- Not yet tested on Zero with writes; only locally and read-only.

**When to choose it:** if one logic path matters and the Flow machinery is unwanted. It meets "smooth for 1–2 months" through the rollups, and keeps the 24 h data live.

## Open decisions
1. **Path: A, C, D or E.** Not decided. See above.
2. Whether the hourly Flow should read the 1 m table for every silver table (assumed yes; paths A and C).
3. **Rollups without Flows** (raised 2026-11-11, **evaluated 2026-11-12**): `INSERT INTO … SELECT` from a view works, upserts safely and picks up late data. It is the core of path E. Still open: which scheduler (Kubernetes CronJob with a `zero-data` CLI command is the candidate), the schedule interval (e.g. 5 min over the last 2 h), and a first write test on Zero.
4. **Rollup bucket for path E:** `_1h` only, or also `_1m` (the 24 h dashboard can read raw through the views, so `_1m` may not be needed).
5. Retiring dbt entirely: a later, separate cleanup.

## Follow-ups (out of scope)
- **Shore power:** a new source, a silver Flow and table, and a series in the combined gold view. Can be added during or after this work.
- Grafana alert rules for Flow failures or stale data.
- Retention or TTL for raw data and rollups.

## Next steps
1. Choose the path. If E: first test a scheduled run on Zero (one source, `_1h`, a test database) and choose the scheduler.
2. Write the design plan for that path from this file: models, tables, Flows, views and dashboard queries.
3. Build it locally:
   - start the local Greptime with `docker compose --profile data-collection up -d --no-deps greptimedb`;
   - load the snapshot schema and ~2 days of Zero data;
   - build the layers and compare them with the old views.
4. Continue with the rollout steps above.

## Session artefacts (scratchpad, may be gone)
These are in `/tmp/claude-1000/-mnt-d-Repos-git-zero/b7934edd-d9e2-46d4-b336-53e30e81eee6/scratchpad/`:
- `d_history.sql`: the D panel written join-then-aggregate.
- `d_history_v2.sql`: the same panel written aggregate-then-join. It's copied below.
- `gen.py`: synthetic 3-month silver data generator.
- `q.sh`: local SQL helper.

## Appendix: the D-style history query (aggregate first, then join)

This is the query measured on Zero on 2026-11-10: 0.28 s for 1 d, 2.2 s for 7 d, 4.9 s for 30 d and 16.9 s for 60 d. It computes daily production and consumption in kWh from the raw tables, using hourly buckets. Replace `RANGE` with an interval such as `30 days`. In Grafana, use `$__timeFilter("timestamp")` for the filter and `'$__interval'` for the bucket size.

The pattern is what matters, for every path:
1. Filter on the raw `"timestamp"` in the innermost query.
2. Aggregate per topic.
3. Join the metadata afterwards.

The first version joined the metadata to raw rows before aggregating. It took 3.1 s for 1 d, 24 s for 7 d, and more than 60 s for 30 d.

It is a measurement query, not production SQL, and three shortcuts make it approximate:
- 24 V power is the hourly average current × the hourly average voltage, not per minute.
- The Aradex split is per sample, but averaged over the hour.
- It has not yet been checked against the old views. Production came out near 0, so check the solar sign.

```sql
-- D-style "Total electrical energy production/consumption per day", 30 days, $__interval = 1h
WITH
pt AS (
  SELECT a.b, m.main_group, a.w
  FROM (SELECT date_bin('1 hour'::interval, "timestamp") AS b, topic, avg(active_power_total) AS w
        FROM public.power_tags WHERE "timestamp" >= now() - interval 'RANGE' GROUP BY b, topic) a
  JOIN public.power_tag_metadata m ON a.topic = m.topic
  WHERE m.main_group IS NOT NULL
),
cur AS (
  SELECT a.b, m.converter, m.main_group, a.i
  FROM (SELECT date_bin('1 hour'::interval, "timestamp") AS b, topic, avg(output_current__value) AS i
        FROM public.marpower__450000_24vdc_system
        WHERE "timestamp" >= now() - interval 'RANGE' AND output_current__is_valid AND output_current__has_value
        GROUP BY b, topic) a
  JOIN public.dc_24v_metadata m ON a.topic = m.topic
  WHERE m.converter IS NOT NULL AND m.main_group IS NOT NULL
),
vol AS (
  SELECT b, converter, coalesce(avg(CASE WHEN subnr = 1 THEN v END), avg(CASE WHEN subnr = 2 THEN v END), avg(CASE WHEN subnr = 3 THEN v END), 24.0) AS v
  FROM (SELECT a.b, m.converter, m.converter_subnr AS subnr, a.v
        FROM (SELECT date_bin('1 hour'::interval, "timestamp") AS b, topic, avg(voltage__value) AS v
              FROM public.marpower__450000_24vdc_system
              WHERE "timestamp" >= now() - interval 'RANGE' AND voltage__is_valid AND voltage__value > 18
              GROUP BY b, topic) a
        JOIN public.dc_24v_metadata m ON a.topic = m.topic
        WHERE m.converter_subnr IS NOT NULL)
  GROUP BY b, converter
),
dc AS (SELECT cur.b, cur.main_group, cur.i * vol.v / 1000.0 AS w FROM cur JOIN vol ON cur.converter = vol.converter AND cur.b = vol.b),
ara AS (
  SELECT date_bin('1 hour'::interval, "timestamp") AS b, topic,
         avg(CASE WHEN power__value > 0 THEN power__value * 100 ELSE 0 END) AS prop,
         avg(CASE WHEN power__value < 0 THEN -power__value * 100 ELSE 0 END) AS hydro
  FROM (SELECT "timestamp", topic, power__value FROM public.marpower__150000_propulsion__pcs_aft_ara1 WHERE "timestamp" >= now() - interval 'RANGE' AND power__is_valid
        UNION ALL SELECT "timestamp", topic, power__value FROM public.marpower__150000_propulsion__pcs_aft_ara2 WHERE "timestamp" >= now() - interval 'RANGE' AND power__is_valid
        UNION ALL SELECT "timestamp", topic, power__value FROM public.marpower__150000_propulsion__pcs_fwd_ara1 WHERE "timestamp" >= now() - interval 'RANGE' AND power__is_valid
        UNION ALL SELECT "timestamp", topic, power__value FROM public.marpower__150000_propulsion__pcs_fwd_ara2 WHERE "timestamp" >= now() - interval 'RANGE' AND power__is_valid)
  GROUP BY b, topic
),
sol AS (
  SELECT date_bin('1 hour'::interval, "timestamp") AS b, topic, avg(greatest(-hvdc_power__value, 0)) AS w
  FROM (SELECT "timestamp", topic, hvdc_power__value FROM public.marpower__busbar
          WHERE "timestamp" >= now() - interval 'RANGE' AND "timestamp" < TIMESTAMP '2026-11-05 06:07:00' AND hvdc_power__is_valid
          AND topic IN ('marpower/busbar/epc-31-t101','marpower/busbar/epc-32-t101','marpower/busbar/epc-32-t102')
        UNION ALL SELECT "timestamp", topic, hvdc_power__value FROM public.marpower__450000_dc_distribution__pv_converter_main_1 WHERE "timestamp" >= now() - interval 'RANGE' AND hvdc_power__is_valid
        UNION ALL SELECT "timestamp", topic, hvdc_power__value FROM public.marpower__450000_dc_distribution__pv_converter_main_2 WHERE "timestamp" >= now() - interval 'RANGE' AND hvdc_power__is_valid
        UNION ALL SELECT "timestamp", topic, hvdc_power__value FROM public.marpower__450000_dc_distribution__pv_converter_owner WHERE "timestamp" >= now() - interval 'RANGE' AND hvdc_power__is_valid)
  GROUP BY b, topic
),
allw AS (
  SELECT b, main_group, w FROM pt
  UNION ALL SELECT b, main_group, w FROM dc
  UNION ALL SELECT b, 'Propulsion', prop FROM ara
  UNION ALL SELECT b, 'Hydrogeneration', hydro FROM ara
  UNION ALL SELECT b, 'Solar', w FROM sol
)
SELECT date_trunc('day', b) AS day,
  sum(CASE WHEN main_group IN ('Solar','Hydrogeneration') THEN w ELSE 0 END) / 1000 AS production_kwh,
  -sum(CASE WHEN main_group NOT IN ('Solar','Hydrogeneration') THEN w ELSE 0 END) / 1000 AS consumption_kwh
FROM allw GROUP BY day ORDER BY day
```
