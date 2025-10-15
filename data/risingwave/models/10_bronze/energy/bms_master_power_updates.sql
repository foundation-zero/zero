{{ config(materialized='materialized_view') }}
{{ get_power_updates('bms_master', ['Stored_Power', 'Stored_Energy']) }}
