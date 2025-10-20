{{ config(materialized='materialized_view') }}

WITH consumer_producer_power_updates AS (
    SELECT * FROM {{ ref('consumer_producer_power_updates') }}
)

{{ join_electrical_metadata('consumer_producer_power_updates') }}
