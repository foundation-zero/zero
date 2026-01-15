{{ config(materialized='materialized_view') }}

{{ join_electrical_metadata(ref('battery_dc_converter_power_updates')) }}
