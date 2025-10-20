-- depends_on: {{ ref('bms_master_power_updates') }}

{{ config(materialized='materialized_view') }}

{{ join_electrical_metadata('bms_master_power_updates') }}
