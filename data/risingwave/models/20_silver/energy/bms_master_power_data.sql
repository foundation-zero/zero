{{ config(materialized='materialized_view') }}
{{ get_power_data_and_groups('bms_master_power_updates') }}