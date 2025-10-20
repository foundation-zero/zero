-- depends_on: {{ ref('consumer_producer_power_updates') }}

{{ config(materialized='materialized_view') }}

{{ join_electrical_metadata('consumer_producer_power_updates') }}
