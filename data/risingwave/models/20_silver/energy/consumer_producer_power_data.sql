{{ config(materialized='materialized_view') }}
{{ get_power_data_and_groups('consumer_producer_power_updates') }}
