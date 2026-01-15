{{ config(materialized='materialized_view') }}

{{ join_electrical_metadata(ref('consumer_producer_power_updates')) }}
