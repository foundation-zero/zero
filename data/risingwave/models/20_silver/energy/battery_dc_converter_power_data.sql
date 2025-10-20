-- depends_on: {{ ref('battery_dc_converter_power_updates') }}

{{ config(materialized='materialized_view') }}

{{ join_electrical_metadata('battery_dc_converter_power_updates') }}
