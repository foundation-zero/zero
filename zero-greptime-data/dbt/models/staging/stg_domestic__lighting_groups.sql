{{ config(materialized='view') }}

-- Proof view. Explicit columns only (no SELECT *): an unexpected new column or a shifted
-- inferred type surfaces as a reviewable snapshot diff and/or a failing test rather than
-- propagating downstream. Renames the ingest `timestamp` to `ts` and drops Vector's
-- transport metadata (`source_type`, `table`, `topic`), presenting a stable, typed surface.
select
    "timestamp" as ts,
    id,
    level,
    room_id
from {{ source('raw', 'domestic__lighting_groups') }}
