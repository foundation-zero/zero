{{ config(materialized='materialized_view') }}

WITH bms_master_power_updates AS (
    SELECT * FROM {{ ref('bms_master_power_updates') }}
)

{{ join_electrical_metadata('bms_master_power_updates') }}
