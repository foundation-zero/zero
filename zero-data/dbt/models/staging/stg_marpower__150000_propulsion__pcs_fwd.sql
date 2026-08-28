{{ config(materialized='view') }}

-- Proof view. The raw table is ~320 columns: each measure lands as a clump of four inferred
-- fields (`__value`, `__is_valid`, `__has_value`, `__timestamp`). Here we pick a curated
-- set of `__value` measures with explicit columns, rename `timestamp` to `ts`, and drop the
-- validity/transport noise. Schema drift surfaces as a snapshot diff or failing test.
select
    "timestamp" as ts,
    device_state__value as device_state,
    drive_thermal_state__value as drive_thermal_state,
    command_register__value as command_register,
    azimuth_setpoint_not_reached__value as azimuth_setpoint_not_reached
from {{ source('raw', 'marpower__150000_propulsion__pcs_fwd') }}
