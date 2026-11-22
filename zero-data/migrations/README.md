# Migrating history to renamed topics

When a system moves to new MQTT topics, Vector (the data pipeline) writes its signals to new
Greptime tables, and everything recorded before stays in the old tables under the old names.
dbt and the dashboards read only the new tables, so they would lose that history.
`zero-data greptime migrate-history` copies it across, checks the copy, and drops the old
tables.

This guide walks through a rehearsal on a laptop and then the migration itself.

## How it works

- **The mapping** is a CSV with one row per signal: `old_topic,old_key,new_topic,new_key`. It
  is made where the new topics were designed (for system 450000: the topic review in the
  `zero-validation` repo) and committed here, as `<system>-mapping.csv`. A device that was
  published under an earlier topic as well gets extra rows for that topic. Signals that are
  deliberately not migrated are left out.
- **The spec** is generated from the mapping by running the repo's Vector on every topic and
  key, so table and column names are Vector's own. It is not committed.
- **A unit** is one old topic copied to one new topic. A unit is copied with all its columns
  or not at all: the new tables are append-only, so a row can't be completed or removed later.
- **The copy** runs day by day, newest first, across all units. A day of a wide table is
  copied in several inserts, because Greptime holds an insert in memory. Nothing is kept outside
  Greptime. Each insert leaves out the timestamps the new topic already has, so you can stop
  it and start it again, and a second run copies nothing.
- **One run at a time.** Two runs at once would both find a timestamp missing and both insert
  it, and a duplicate row can't be removed. A run therefore holds a lock, the table
  `migrate_history_running`, and a second run refuses to start while it exists. `drop
  --execute` holds the same lock, so it can't drop a table a run is reading.
- **Old and new topics never publish side by side**, so every row of an old topic is history
  of its new topic. No cut-over time is passed.

The four commands, all under `uv run zero-data greptime migrate-history`:

| Command | What it does |
|---|---|
| `build-spec <mapping.csv> --out <spec.json>` | Makes the spec. Needs Docker, not Greptime. |
| `run <spec.json> [--dry-run] [--until <date>] [--unlock]` | Copies. With `--dry-run` it only reads and prints a report. |
| `check <spec.json>` | Compares old and new. Prints the differences and exits 1 when there are any. |
| `drop <spec.json> [--execute] [--unlock]` | Drops the old tables whose history is checked. Without `--execute` it prints what it would do. |

`run`, `check` and `drop` take `--host <greptime host>` (default: `GREPTIME_HOST`, else the
local Greptime) and `--table <old table>`, repeatable, to work on the new topics those old
tables feed. A new topic's history is kept whole: when another old table feeds the same topic
(a device's earlier name), its rows come along.

## Rehearsal, before the cut-over

The rehearsal runs the whole migration on a laptop, on one real day of data. It needs no new
topics to exist yet: the new tables are created empty, and the run adds their columns.

1. **Start a local Greptime** from the repo root:
   ```bash
   docker compose --profile data-collection up -d greptimedb
   ```
2. **Restore the old tables from one daily backup** of the live Greptime. Copy the bucket
   credential into the container as in *Restore from the GCP bucket* in
   `apps/base/greptime-backup/README.md` of the `edge-flux` repo, with the cluster's own
   secret and bucket. A daily backup holds one day of **all** tables, which takes hours and
   more memory than a laptop has, so restore only the old tables of the mapping. For each one,
   create it from the live Greptime's `SHOW CREATE TABLE` and load its file:
   ```sql
   COPY "<old table>" FROM 'gcs://<bucket>/data/daily-backups/<date>/data/public/1/<old table>.parquet'
     WITH (FORMAT='parquet') CONNECTION (SCOPE='https://www.googleapis.com/auth/devstorage.read_only');
   ```
   Verify the backup first (`greptime cli data export-v2 verify`): a recent one may still be
   uploading. Give Docker at least 8 GB, and remove the credential afterwards.
3. **Build the spec:**
   ```bash
   uv run zero-data greptime migrate-history build-spec migrations/450000-mapping.csv --out spec.json
   ```
4. **Create the new tables, empty.** This helper is for rehearsals only; on the live Greptime
   the new tables come from Vector.
   ```bash
   uv run python -m tests.greptime.rehearsal_tables spec.json
   ```
5. **Dry run**, and read the report (see *Reading the dry run*):
   ```bash
   uv run zero-data greptime migrate-history run spec.json --dry-run
   ```
6. **Run, then check.** `check` should print nothing.
   ```bash
   uv run zero-data greptime migrate-history run spec.json
   uv run zero-data greptime migrate-history check spec.json
   ```
7. **Run again.** It should report 0 rows copied.
8. **Drop.** First without `--execute`, to see which tables would go and which are kept and
   why. The restored tables can be dropped for real: the local Greptime is a throwaway.

To rehearse again after a fix, remove the container and its data and start at step 1.

The rehearsal can't show a column whose type Vector picks differently from the old one,
since Vector hasn't written the new tables yet. The dry run on the live Greptime shows those.

## The migration, after the cut-over

Wait until the new topics have published for a few hours, so that Vector has created the new
tables and their columns.

1. **Build the spec** as in the rehearsal. Rebuild it if the mapping changed.
2. **Dry run against the live Greptime** and read the report:
   ```bash
   uv run zero-data greptime migrate-history run spec.json --host <host> --dry-run
   ```
3. **Fix what the report asks for** (types that differ, units left out), and dry-run again
   until it is clean or you accept what is left.
4. **Copy one day** and look at it: the newest day, across all tables.
   ```bash
   uv run zero-data greptime migrate-history run spec.json --host <host> --until <yesterday>
   ```
   Open the dashboards over that day. `check` will still list the older days as missing.
5. **Copy the rest.** It can take hours; stop it with Ctrl-C and start it again whenever.
   After each topic and day it waits 0.1 s to leave room for live data; `--pause` changes that.
   ```bash
   uv run zero-data greptime migrate-history run spec.json --host <host>
   ```
6. **Check.** Nothing printed means every unit's rows and values match.
   ```bash
   uv run zero-data greptime migrate-history check spec.json --host <host>
   ```
7. **Look at the dashboards** over a period before the cut-over.
8. **Take a Greptime backup, then drop the old tables:**
   ```bash
   uv run zero-data greptime migrate-history drop spec.json --host <host>            # what would happen
   uv run zero-data greptime migrate-history drop spec.json --host <host> --execute
   ```
   For each table that is kept because it holds data that isn't migrated, decide whether that
   data may go, and then drop it by name:
   ```bash
   uv run zero-data greptime migrate-history drop spec.json --host <host> \
     --table <old table> --accept-unmigrated --execute
   ```

## Reading the dry run

- **Per old table:** how many units and rows it has to copy, and how many are already there.
- **Units left out:** units the run would skip, with the reason. They stay in the old table
  and keep it from being dropped. Fix the cause and run again; the run then copies them.
- **Columns that differ in type:** the same signal has one type in the old table and another
  in the new one. The run doesn't convert values. Decide per column which side is wrong and
  alter that column:
  ```sql
  ALTER TABLE "<table>" MODIFY COLUMN "<column>" DOUBLE;
  ```
  - If the new column got its type by accident (a decimal signal whose first message was a
    whole number), alter the **new** table. Until then Greptime also rejects Vector's live
    values for it.
  - If the signal's type really changed, alter the **old** table.
- **Columns the run adds:** a new column exists only once a value has arrived for it. For
  signals that haven't published yet, the run adds the column with the old column's type. If
  Vector later sends such a signal with another type, Greptime rejects those inserts, which
  shows only in Greptime's frontend log. Check that log after the run.
- **Not migrated:** topics and columns with data in the old tables that the mapping doesn't
  cover. Add them to the mapping **before** the first run if they should be kept: a unit
  that has been copied can't get more columns afterwards.

## When something goes wrong

- **A run or drop refuses to start because another one holds the lock:** the message says
  from which machine and since when. Ctrl-C and errors release the lock. A run that lost its
  connection (a closed laptop, a restarted Greptime) can't, and leaves it behind. Make sure
  that run has ended, wait a minute so its last insert is finished in Greptime, and start
  again with `--unlock` (`run` and `drop` both take it).

- **The log says "Attempt N failed, trying again":** Greptime's frontend drops its connection to
  the datanode every few hours of copying, and the statement in flight fails with `Internal
  error: 1003`. The run waits a minute and sends it again, five times at most.
- **The run stops with an error** (a timeout, a restart of Greptime): start it again. If
  Greptime ran out of memory on an insert, lower `VALUES_PER_INSERT` in `migrate_history.py`
  first. Days
  that are complete are skipped, and a day that was copied in part gets its missing rows.
- **The run stops because a day "holds N rows after copying, M expected":** the new topic has
  rows on that day that didn't come from the old topic. Nothing wrong was written, but find
  out where they came from before going on.
- **`check` prints differences:** each line names the new table and topic, and the day or
  column that differs. Missing days mean the run hasn't finished. Anything else needs a look
  before any old table is dropped.
- **Wrong rows were copied:** they can't be deleted. The way back is to rebuild the new table
  without them (stop Vector, rename the table, create it again and copy the right rows back).
  The old tables are the source for that, which is why they are dropped last.

## What `drop` refuses

`drop` keeps an old table when:

- `check` finds a difference for a unit that reads from it, or a unit was left out;
- it received rows in the last day (some old tables keep publishing other signals);
- it holds topics or columns that aren't migrated, unless you name the table with `--table`
  and pass `--accept-unmigrated`.

It checks every table before it drops any. Old tables that feed the same new topic (a
device's earlier name in another table, or a new topic that gathers signals from two old
ones) can only be checked while all of them exist. So drop them in one run: once one of them
is gone, the others are kept, and removing those is a decision by hand.

It only looks at the old tables in the spec. `DROP TABLE` can't be undone.
