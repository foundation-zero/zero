{{ config(materialized='view') }}

-- Proof view. The raw Marpower table is ~320 columns: every measure arrives as a clump of
-- four inferred fields (`__value`, `__is_valid`, `__has_value`, `__timestamp`). This view
-- picks a curated set of `__value` measures with explicit columns (no SELECT *), renames
-- the ingest `timestamp` to `ts`, and drops the validity/transport noise — presenting a
-- stable, typed surface. An unexpected new column or a shifted inferred type surfaces as a
-- reviewable snapshot diff and/or a failing test rather than propagating downstream.
select
    "timestamp" as ts,
    device_state__value as device_state,
    drive_thermal_state__value as drive_thermal_state,
    command_register__value as command_register,
    azimuth_setpoint_not_reached__value as azimuth_setpoint_not_reached
from {{ source('raw', 'marpower__150000_propulsion__pcs_fwd') }}
