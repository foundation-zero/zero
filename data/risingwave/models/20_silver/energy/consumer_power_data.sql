{{ config(materialized='materialized_view') }}
{{ get_power_data_and_groups('consumer_power_updates') }}
