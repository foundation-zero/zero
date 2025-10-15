{{ config(materialized='materialized_view') }}
{{ get_power_data_and_groups('battery_dc_converter_power_updates') }}
