{{ config(materialized='materialized_view') }}

WITH battery_dc_converter_power_updates AS (
    SELECT * FROM {{ ref('battery_dc_converter_power_updates') }}
)

{{ join_electrical_metadata('battery_dc_converter_power_updates') }}
