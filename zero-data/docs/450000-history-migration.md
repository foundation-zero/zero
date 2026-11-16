# Plan: migrating the 450000 history to the per-kind tables

After the cut-over, Vector (the data pipeline) writes the 450000 signals to new per-kind Greptime tables (`marpower__<system>__<kind>`, with `technical_name`). History from before the cut-over stays in the 37 old tables (`marpower__450000_*` and a few others). dbt reads only the new tables, so the Energy dashboards, the shore power models and the four commissioning dashboards would lose that history. This plan copies it into the new tables, under the new `topic`, `technical_name` and column names, so they see one continuous history. It is the history step of the 450000 cut-over (ingest #1050; consumers #1051–#1058).

The plan was made with read-only queries. The copy is run by the data platform, which has write access, with a zero-data command (below) after review. Nothing here has been run against Greptime except read-only counts.

## What moves

Counted on 13 Nov 2026, from the migration spec (below):

- **455 copy units.** A unit is one old topic in one old table → one new topic in one new table, with a column map. 394 come from the 450000 mapping (old topic and key → new topic and key, per IO-list row); 61 are earlier names of the same devices (chains, below).
- **325M source rows** read from 38 old tables (the 37 of the mapping, plus `marpower__busbar`). They land in 44 of the 50 new tables. The six `45-pms` tables have no history: their rows are new.
- **Up to 650M target rows.** A catch-all topic splits into one row per device: `450000-amcs` gives 19 units, `450000-dc-distribution-general` 23. A unit copies only the old rows where at least one of its mapped columns has a value, so the real count is lower. The dry run gives it.
- **10,977 column maps.** Old and new column names come from running the real Vector (zero PR #1050 at `5f670080`) on every old and new topic and key, never from a reimplementation of snake case. Every old row of the mapping lands in the table the mapping names. No old column of a topic maps to two new columns.
- **Kept apart:** 3.9M rows on three topics, and the retired columns listed below.

The "merged columns" worry from the handoff doesn't apply. IO-list keys and node keys of one device were on different old topics (`dc-switch/keb6-0571` holds `CLOSED`, `dc-switch/0571` holds `Closed`). They share a column name in the old table, but not a row, so the old topic says which new column each row goes to.

## Per old table

Wave 1 is what dbt reads (Energy dashboards: 24 V, batteries, solar; shore power, #1057). Wave 2 is what the four commissioning dashboards read. Wave 3 is the rest. "Rows" are the old topics' rows over all time; chain rows are part of them.

| Wave | Old table (`marpower__…`) | Rows (chain) | Kept apart | Old topics → units | New tables (`marpower__…`) | Column maps |
|---|---|---|---|---|---|---|
| 1 | `450000_24vdc_system` | 53.7M (0.6M) | | 102 → 102 | `dc_24v__breaker`, `dc_24v__distribution_board`, `dc_24v__power_supply` | 1318 |
| 1 | `450000_main_power_storage_errors` | 81.7M | | 22 → 22 | `battery__pack` | 5984 |
| 1 | `450000_dc_distribution__pv_converter_main_1` | 0.7M | | 1 → 1 | `solar__dc_dc_converter` | 97 |
| 1 | `450000_dc_distribution__pv_converter_main_2` | 0.7M | | 1 → 1 | `solar__dc_dc_converter` | 97 |
| 1 | `450000_dc_distribution__pv_converter_owner` | 0.7M | | 1 → 1 | `solar__dc_dc_converter` | 97 |
| 1 | `busbar` | 17.9M (17.9M) | | 7 → 7 | `dc_350v__dc_dc_converter`, `solar__dc_dc_converter` | 679 |
| 1 | `450000_dc_distribution__conv` | 2.2M | | 7 → 7 | `dc_350v__dc_dc_converter`, `solar__dc_dc_converter` | 35 |
| 1 | `450000_dc_distribution_esi` | 14.9M (7.5M) | | 8 → 8 | `dc_700v__shore_converter` | 384 |
| 2 | `450000_fire_detection` | 35.5M (0.6M) | | 156 → 156 | `fire_detection__call_point`, `__detector`, `__sounder` | 780 |
| 2 | `450000_dc_distribution__dc_switch` | 39.3M | 0.2M | 15 → 15 | `dc_700v__dc_switch` | 220 |
| 2 | `450000_dynamic_conv_sb` | 13.1M | 2.9M | 3 → 3 | `ac_400v__breaker` | 42 |
| 2 | `450000_dynamic_conv_ps` | 13.0M | 0.8M | 3 → 3 | `ac_400v__breaker` | 42 |
| 2 | `450000_dynamic_conv_sb_ara__5_12_u101` | 4.7M | | 1 → 1 | `dc_ac__inverter` | 51 |
| 2 | `450000_dynamic_conv_ps_ara__5_11_u101` | 4.7M | | 1 → 1 | `dc_ac__inverter` | 51 |
| 2 | `450000_dynamic_conv_sb_general` | 4.3M | | 1 → 5 | 5 tables | 31 |
| 2 | `450000_dynamic_conv_ps_general` | 4.3M | | 1 → 5 | 5 tables | 31 |
| 2 | `450000_dc_distribution_general` | 4.5M | | 1 → 23 | 11 tables | 56 |
| 2 | `450000_dc_distribution__350v_conv` | 5.6M | | 2 → 8 | `dc_700v__dc_dc_converter`, `__isolation_monitor`, `__switchboard` | 18 |
| 2 | `450000_dc_distribution__350v_conv_aft_1`, `_aft_2`, `_fwd_1`, `_fwd_2` | 4 × 0.7M | | 4 → 4 | `dc_350v__dc_dc_converter` | 4 × 97 |
| 2 | `450000_amcs` | 4.6M | | 1 → 19 | 7 tables | 65 |
| 2 | `090000_doors_hatches` | 1.7M | | 1 → 1 | `dc_24v__distribution_board` | 3 |
| 2 | `450000_350vdc_system` | 1.2M | | 6 → 6 | `dc_350v__breaker` | 378 |
| 2 | `450000_dc_distribution__pwr` | 0.9M | | 4 → 4 | `amcs__plc` | 24 |
| 2 | `450000_fire_detection_general` | 0.6M | | 1 → 2 | `fire_detection__general`, `__main_panel` | 11 |
| 2 | `450000_ugrid` | 0.3M | | 2 → 2 | `dc_ac__inverter` | 4 |
| 2 | `450000_dynamic_conv` | 0.2M | | 1 → 1 | `ac_400v__bus_tie` | 2 |
| 3 | `450000_24vdc_system_general` | 4.5M | | 1 → 15 | 4 tables | 30 |
| 3 | `450000_gas_detection` | 2.0M | | 1 → 10 | `gas_detection__detector` | 11 |
| 3 | `97_spare_general` | 1.6M | | 1 → 2 | `amcs__general`, `dc_350v__bus_tie` | 3 |
| 3 | `450000_amcs__alarm_panel` | 0.9M | | 1 → 6 | `amcs__alarm_panel` | 14 |
| 3 | `450000_amcs__ums` | 0.7M | | 1 → 4 | `amcs__alarm_panel`, `amcs__ums_entrance_unit` | 17 |
| 3 | `450000_burglar` | 0.6M | | 1 → 7 | `burglar_detection__detector`, `__general` | 7 |
| 3 | `450000_main_power_storage_general` | 0.1M | | 1 → 1 | `amcs__cabinet` | 4 |
| 3 | `450000_amcs__plcpower__keb8` | 0.1M | | 1 → 1 | `amcs__plc` | 2 |
| 3 | `450000_dynamic_conv_general` | 0.1M | | 1 → 1 | `ac_400v__bus_tie` | 1 |

`090000_doors_hatches` and `97_spare_general` keep publishing after the cut-over. Only the five columns that move (the three SOS locker supply failures, two spare-list rows) are copied; the old tables stay as they are.

`main_power_storage_errors` is 41 GB of the 55 GB and has ~1,100 columns. It is copied per topic and per day (22 × ~90 windows).

## Chains: earlier names of the same devices (decided 13 Nov)

Each chain borrows the column map of the mapped old topic that took over from it; the keys are the same.

| Old topic | Rows, period | Copied as |
|---|---|---|
| `busbar/epc-31-t101`, `epc-32-t101`, `epc-32-t102` | 3 × 2.6M, 4 Sep – 5 Nov 06:07 UTC | `45-solar/dc-dc-converter/04-31-t101`, `04-32-t101`, `04-32-t102` (like `pv-converter-main-1`, `-main-2`, `-owner`) |
| `busbar/epc-71-t101` … `epc-72-t102` | 4 × 2.6M, same period | `45-dc-350v/dc-dc-converter/02-71-t101` … `02-72-t102` (like `350v-conv-aft-1` … `fwd-2`). The 350 V converters were on busbar too, not only the solar ones. |
| `450000-dc-distribution-esi/70-1x-tbc1x` | 4 × 1.9M, 19 Aug – 23 Oct | `45-dc-700v/shore-converter/07-1x-tbc1x` (like `07-1x-tbc1x`) |
| `450000-24vdc-system/14e1-33f01`, `14e1-45f01`, `14e2-24f24`, `14e2-77f01`, `14e3-12f01` | 5 × 0.11M, 7 Apr – 29 Jun | `45-dc-24v/breaker/<channel>`, named by the convention as zero PR #1053 does. They have no IO-list row. |
| `450000-fire-detection/201hNN/s`, `201hNN/1` (45 topics) | 45 × 14k, 6 – 14 Aug | the same device with `-` (`201h38-s`, `201h63-1`) |

`slv_solar_converters` and #996 bridge the busbar and shore converter chains in SQL today; that SQL can go once these are migrated.

**SB and PS uGrid: no copy needed.** The `ara-5/12/u101` topic in `dynamic_conv_sb` (7 Apr – 23 Oct) and `ara-5/11/u101` in `dynamic_conv_ps` (7 Apr – 12 Aug) duplicate the configured topics `450000-dynamic-conv-sb-ara/5-12-u101` and `…-ps-ara/5-11-u101`, which have been published since 7 Apr: the monthly row counts are identical to the row, April to September. The configured topics are in the mapping, so the uGrid history is migrated through them. Copying the chains as well would double it, so they are kept apart as duplicates. They hold three keys the configured topics don't (`AvailPo`, `MaxPo`, `ResPo`); those stay in the old tables.

Not part of this migration:
- The per-detector tables `marpower__450000_fire_detection__201h*` (110 tables, 19 Aug – 30 Sep) duplicate `marpower__450000_fire_detection` (one day of `201h1` checked: 2795 rows in both).
- `marpower__450000_hvac`, `_underwlights` and `_amcs__Command` aren't 450000 signals in the new IO lists.

## Kept apart

| What | Rows | Reason |
|---|---|---|
| `450000-dynamic-conv-sb/ara-5/12/u101` | 2.9M | Duplicate of the configured topic (above) |
| `450000-dynamic-conv-ps/ara-5/11/u101` | 0.8M | Duplicate of the configured topic (above) |
| `450000-dc-distribution/dc-switch/keb6-0574` | 0.2M | No DC switch 0574 in the IO lists; 7 Apr – 11 Jun |
| Retired columns: keys that stopped before the cut-over and have no row in the new IO lists | | No target. `24vdc_system_general` 13 (e.g. `gmdss_14_e_3_current`, until 29 Jun; `gen_service_14_e_1_03_v_0x_fault`, until 6 Nov), `dc_distribution_general` 8 (the uGrid `digin` inputs until 5 Nov, `keb_8_dc_switch_0576_*`), `main_power_storage_general` 8 (`main_batt_syst_{1,3,5,6}_estop_*`, until 20 Aug), `amcs__alarm_panel` 3 (until 1 Sep), `gas_detection` 2, `ugrid` 2, `dynamic_conv_ps_general` 1 |

Some retired keys may be earlier names of keys that exist now (`main_batt_syst_1_estop_act` until 20 Aug, `main_batt_syst_ps_aft_estop_act` after). Such a pair is a column chain like the topic chains above. It is folded in only when someone confirms which key took over, and until then it is kept apart.

**Live keys outside the IO lists.** Two sets of node keys are still published but have no IO-list row, so the mapping doesn't know them: the shore converters' `AmbientHighTemperature`, `ConverterOverload`, `IgbtHighTemperature`, `InputChokeHighTemperature`, `NeutralChokeHighTemperature`, `OuputChokeHighTemperature`, `TransformerHighTemperature` (since 6 Nov), and the battery packs' `SpVoltage` (since 19 Aug). Node keys keep their names (R6), so after the cut-over they should arrive under the same name on the new topic. A one-to-one unit (one old topic → one new topic) therefore also copies every old column whose name exists in the new table at migration time. The dry run lists these columns.

## How a unit is copied

For each unit, in daily windows, and only before the new topic's first row:

```sql
INSERT INTO "marpower__dc_700v__shore_converter"
  ("timestamp", "topic", "technical_name", "table", "source_type",
   "esi_ambient_temperature__value", "esi_ambient_temperature__timestamp", …)
SELECT "timestamp", 'marpower/45-dc-700v/shore-converter/07-11-tbc1a', '07-11-tbc1a',
       'marpower__dc_700v__shore_converter', "source_type",
       CAST("esi_ambient_temperature__value" AS DOUBLE), "esi_ambient_temperature__timestamp", …
FROM "marpower__450000_dc_distribution_esi"
WHERE "topic" = 'marpower/450000-dc-distribution-esi/70-11-tbc1a'
  AND "timestamp" >= '2026-08-19T00:00:00Z' AND "timestamp" < '2026-08-20T00:00:00Z'
  AND "timestamp" < <first row of the new topic>
  AND ("esi_ambient_temperature__value" IS NOT NULL OR …)
```

- **`topic` and `technical_name` take the new values**, not only `technical_name`: dbt and the metadata tables (`marpower__device_metadata`, `dc_24v_metadata`, fire detection) join on `topic`.
- **Every column of a key is copied:** `__value`, `__timestamp`, `__is_valid` and `__has_value`, where the old table has them. `table` is set to the new table name and `source_type` is copied, where the new table has those columns. `yard_tag` and `name` aren't written: they live in `marpower__device_metadata`.
- **Missing columns first.** A column exists only once Vector has written a non-null value, and its first write fixes its type. Before a unit runs, the command reads the new table's schema and adds each missing column with `ALTER TABLE … ADD COLUMN`, typed as the old column. Where both exist and the types differ, it casts the old value to the new type. A cast that would lose information, such as string to number, stops that unit and is reported.
- **The cut-over boundary is per unit:** the new topic's first row in the new table, read before the unit starts. A device that went quiet before the cut-over has no first row, and its bound is the cut-over time from the deploy.
- **Run once.** Tables are append-only, and a second run would duplicate rows. Before each window the command counts the new topic's rows in that window, and skips the window if any exist. Stopping and restarting is therefore safe, and a window is never half-copied twice.
- **One insert at a time.** Greptime is shared with the running boat. The command runs one window at a time, in the wave order above, with a pause between windows. It can be stopped and resumed.

## The command (decided 13 Nov: zero-data)

`zero-data greptime migrate-history`, next to `snapshot` and `load` in `zero-data/src/zero_data/greptime/`, with `--host` choosing the tier (`zero`, `subzero`). The spec (`migration450.json`) is built in zero-validation, next to the 450000 mapping. It is the only 450000-specific input, so the command can serve the next systems' cut-overs too.

### Reviewable and reproducible

What runs against Greptime is a SQL file that has been reviewed in a PR, not SQL put together during the run.

1. **Spec.** `build_migration450.py` (zero-validation) builds `migration450.json` from pinned inputs: the 450000 mapping (`data450.json`, from Marpower's IO lists at Plastic cs 4563), the zero commit of the Vector rule, the Vector image `0.55.0-debian`, and Greptime's schema. The spec records the commit and a sha256 of `data450.json`. Built again from the same inputs, it gives the same units and column maps; only the row counts move.
2. **Plan.** `migrate-history plan <spec> --host … --boundary <cut-over>` reads both tables' schemas and each new topic's first row. It writes one SQL file per wave: the `ALTER TABLE … ADD COLUMN` statements, then the `INSERT … SELECT` per unit and daily window, in a fixed order, each statement with a comment naming its unit. Alongside it writes the dry-run report: per unit, the old rows (all, and those with a mapped value), the target rows already there, the columns to add or cast, and live keys outside the mapping. The same spec and the same Greptime state give byte-identical files. This step only reads.
3. **Review.** The SQL files and the report go into a zero-validation PR, under `research/topic-structure-450000/migration/`. They are built from Marpower's IO lists, so they stay in that private repo. This repo is public, and only the generic command, with synthetic test fixtures, goes to zero-data. The reviewer reads the report and samples the SQL: a catch-all split, a chain, an `ALTER`, a cast.
4. **Execute.** `migrate-history execute <wave.sql> --host …` runs the reviewed file as it is. It refuses to run if the file's sha256 isn't the one recorded in the plan, or if the schema differs from what the plan read (a new column has appeared since, for example). Each statement it runs, with its row count and time, goes to a journal (`<wave>.journal.jsonl`). A restart skips what the journal shows as done, and also any window whose target already has rows. The journal is committed next to the SQL afterwards, as the record of what ran.
5. **Check.** `migrate-history check <spec> --host …` runs the checks below and writes a report next to the journal.

Tests run against the local greptimedb that zero-data's `greptimedb` tests use. They cover a catch-all split, a chain, a missing column, a type cast, a rerun that copies nothing, a window that already has rows, a changed SQL file that `execute` refuses, and a plan built twice that comes out byte-identical.

### Rehearse the cut-over on subzero first

Subzero (`greptime-subzero`, the same GreptimeDB 1.1.3) is fed by zero-data's simulator (`data_gen`). It publishes random values for every row of `zero-data/io_lists/ZERO mocked IO-List.xlsx` and `io-list ~ help ~ totals.xlsx`, on the old 450000 topics. On 16 Nov subzero had 165 `marpower__450000_*` tables, for example 75M battery rows and the shore converters on `70-1x`. None of the new per-kind tables exist there, and neither does `marpower__busbar`.

The rehearsal plays the whole cut-over on subzero, live writes included, before zero (decided 16 Nov):

1. **Fill in the old tables.** Copy one day per chain from zero into subzero's old tables (read from zero, write to subzero): `busbar/epc-*`, `dc-switch/keb6-0574` and the `201hNN/s` fire topics. The chains' real shapes are then covered too.
2. **Cut over subzero.** Deploy #1050's Vector to subzero, then switch the simulator to the new topics and keys by merging the PR that replaces its IO lists. The two files it reads today are an older copy of Marpower's lists (last updated 29 Sep in #647). They predate the October renames: the shore converters are still on `70-1x`, and the separate `pv-converter-*` and `350v-conv-*` topics are missing. The PR replaces them with the lists Marpower will deploy (AMCS R2.148, PMS R2.79, Internal R7.60, MPP R1.10, and the unchanged Typicals R1.41). Merging to main publishes the simulator image and chart, so that PR is merged only at this step. The zero-data reader doesn't accept those lists yet: AMCS and Typicals use target types it has no mapping for (`bool`, `Uint16`, `Uint32`, and lower-case `uint16`, `int32`, `double`, `float`; R2.147 has the same ones). The PR adds them. `vector_gen` and the AsyncAPI Spec read the same lists, so regenerating them after the merge drops the old `450000-…` grouped prefixes, as planned for after the cut-over. From then on, Vector creates the new tables from live messages and fixes their column types exactly as it will on zero, and the old tables stop. The time of the switch is subzero's boundary.
3. **Cover what the simulator doesn't publish.** The node keys from `project-configuration.json` and the live keys outside the IO lists (shore converter alarms, `SpVoltage`) are sent once through a local Vector with the #1050 rule, writing to subzero from a file of messages, not from the broker. A few keys are deliberately left unsent, so the plan has to add their columns.
4. **Deploy the consumers as on cut-over day:** #1053's dashboards against subzero's datasource, and #1054's dbt models (`just dbt-deploy subzero`).
5. **Plan → review → execute → check**, all waves, while the simulator keeps writing. Live rows after the boundary are never touched, and the per-unit boundary and the window check hold up against new rows arriving.
6. **Look at the result.** The four commissioning dashboards and the Energy dashboards show one continuous line through the boundary in every panel, and `dbt build` passes.
7. **Run it again.** A second `execute` must copy nothing, and `check` must give the same report.

This also rehearses cut-over day on the consumer PRs.

Only after this goes through without hand fixes do we plan against zero. On zero, try one small table first (`450000_ugrid`, 0.3M rows), check, then wave 1.

## Checks afterwards

- **Row counts per unit:** the old topic's rows with a mapped value before the boundary equal the new topic's rows before it. The count is per day, so a gap shows where it is.
- **Values:** for a sample of columns per unit, `count`, `min` and `max` before the boundary are the same in old and new.
- **Dashboards over a window before the cut-over:** the four commissioning dashboards and the Energy dashboards (24 V, batteries, solar) show the same curves as the old tables did, e.g. 1 – 7 Nov.
- **dbt:** `dbt build` passes, and the 24 V metadata test covers a window before the cut-over.
- **Keep the old tables** until the dashboards are checked. Dropping them is a separate decision.
- Record each old topic as migrated or `keep-apart`, with reason and who confirmed, in `knowledge/renames.yaml` (ticket 030). The format is decided there.

## Still open

- Who runs it, and when: after the cut-over, once the new tables exist.
- Whether any retired key is an earlier name of a current one (above). Without confirmation, those keys are kept apart.

## Rebuild the spec

In zero-validation (`research/topic-structure-450000/build_migration450.py`), with a checkout of this repo at the convention rule (#1050) and Docker. It runs `timberio/vector:0.55.0-debian` on every old and new topic and key, and reads the old tables' schema and per-topic row counts from Greptime (read-only, about 90 s). The chains and the kept-apart topics are constants at the top of the script.
