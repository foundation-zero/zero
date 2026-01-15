{{ config(materialized='materialized_view') }}

{{ join_electrical_metadata(ref('bms_master_power_updates')) }}
